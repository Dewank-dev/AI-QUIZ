from flask import Blueprint, render_template, request, session, redirect, url_for, current_app, flash
from .quiz_engine import QuizEngine
from .evaluator import evaluate_quiz
from .analyzer import analyze_performance
from .ai_generator import generate_ai_questions
from .storage import save_attempt, load_attempts, load_questions
from .storage import clear_attempts
from flask import jsonify
from datetime import datetime

bp = Blueprint('main', __name__)


# DB init is handled in app factory; keep routes simple


@bp.route('/')
def index():
    subjects = ['Python', 'C Programming', 'HTML/CSS', 'Artificial Intelligence', 'Machine Learning']
    return render_template('index.html', subjects=subjects)


@bp.route('/about')
def about():
    return render_template('about.html')


@bp.route('/quiz/setup')
def quiz_setup():
    subjects = ['Python', 'C Programming', 'HTML/CSS', 'Artificial Intelligence', 'Machine Learning']
    # derive topics dynamically from question bank
    from .storage import load_questions
    all_q = load_questions()
    topics_map = {}
    for s in subjects:
        tset = sorted(list({q.get('topic') for q in all_q if q.get('subject') == s}))
        topics_map[s] = ['All'] + tset if tset else ['All']
    return render_template('quiz_setup.html', subjects=subjects, topics_map=topics_map)


@bp.route('/quiz/start', methods=['POST'])
def quiz_start():
    subject = request.form.get('subject')
    topic = request.form.get('topic')
    difficulty = request.form.get('difficulty')
    num = int(request.form.get('num', 10))

    # Validate available questions via file storage
    from .storage import load_questions
    all_q = load_questions()
    filtered = [q for q in all_q if q.get('subject') == subject]
    if topic and topic != 'All':
        filtered = [q for q in filtered if q.get('topic') == topic]
    if difficulty and difficulty != 'Mixed':
        filtered = [q for q in filtered if q.get('difficulty') == difficulty]

    available = len(filtered)
    if available == 0:
        flash('No questions available for selected criteria.', 'warning')
        return redirect(url_for('main.quiz_setup'))
    # Do not reduce num here: QuizEngine will generate variations if needed

    engine = QuizEngine()
    qs = engine.fetch_questions(subject=subject, topic=topic, difficulty=difficulty, num=num)

    # Store quiz in session (without correct answers) but include question ids and shuffled options
    session['quiz_questions'] = [{'id': q['id'], 'question': q['question'], 'options': q['options'], 'topic': q['topic']} for q in qs]
    session['quiz_meta'] = {'subject': subject, 'topic': topic, 'difficulty': difficulty, 'num': len(qs)}
    return redirect(url_for('main.quiz'))


@bp.route('/quiz')
def quiz():
    quiz_qs = session.get('quiz_questions')
    meta = session.get('quiz_meta')
    if not quiz_qs or not meta:
        flash('No active quiz. Please setup a quiz first.', 'info')
        return redirect(url_for('main.quiz_setup'))
    return render_template('quiz.html', questions=quiz_qs, meta=meta)


@bp.route('/quiz/submit', methods=['POST'])
def quiz_submit():
    quiz_qs = session.get('quiz_questions')
    meta = session.get('quiz_meta')
    if not quiz_qs or not meta:
        flash('Quiz session expired or invalid.', 'danger')
        return redirect(url_for('main.quiz_setup'))

    submitted = {}
    for q in quiz_qs:
        key = f"q_{q['id']}"
        val = request.form.get(key)
        if val:
            submitted[str(q['id'])] = val

    result = evaluate_quiz(quiz_qs, submitted)
    analysis = analyze_performance(result['details'])

    # Persist attempt
    attempt = {
        'id': None,
        'subject': meta.get('subject'),
        'topic': meta.get('topic'),
        'difficulty': meta.get('difficulty'),
        'questions': [q['id'] for q in quiz_qs],
        'answers': submitted,
        'score': result['correct'],
        'percent': result['percentage']
    }
    saved = save_attempt(attempt)


    # clear session quiz
    session.pop('quiz_questions', None)
    session.pop('quiz_meta', None)

    return redirect(url_for('main.result', attempt_id=saved.get('id')))





@bp.route('/result/<int:attempt_id>')
def result(attempt_id):
    attempt = load_attempts()
    attempt = next((a for a in attempt if a.get('id')==attempt_id), None)
    if not attempt:
        return render_template('error.html', message='Attempt not found'), 404

    qs_all = load_questions()
    qs = [q for q in qs_all if q.get('id') in attempt.get('questions', [])]
    result = evaluate_quiz(qs, attempt.get('answers', {}))
    analysis = analyze_performance(result['details'])
    return render_template('result.html', result=result, analysis=analysis, attempt=attempt)


@bp.route('/history')
def history():
    attempts = load_attempts()
    attempts = sorted(attempts, key=lambda x: x.get('created_at',''), reverse=True)
    # Format created_at into a friendly human-readable form
    for a in attempts:
        ca = a.get('created_at')
        if isinstance(ca, str):
            try:
                # handle ISO format timestamps saved by file-based storage
                dt = datetime.fromisoformat(ca)
                a['created_at'] = dt.strftime('%d %B %Y %H:%M')
            except Exception:
                # leave original string if parsing fails
                a['created_at'] = ca
    return render_template('history.html', attempts=attempts)


@bp.route('/history/clear', methods=['POST'])
def history_clear():
    # clear attempts via storage helper
    try:
        clear_attempts()
        flash('All history cleared.', 'success')
    except Exception as e:
        flash('Failed to clear history: ' + str(e), 'danger')
    return redirect(url_for('main.history'))


@bp.route('/api/generate-questions', methods=['POST'])
def api_generate_questions():
    data = request.get_json() or {}
    subject = data.get('subject')
    topic = data.get('topic')
    difficulty = data.get('difficulty')
    num = int(data.get('num', 5))

    # Try AI generator (will fallback internally)
    try:
        generated = generate_ai_questions(subject=subject, topic=topic, difficulty=difficulty, num=num)
        return jsonify({'ok': True, 'questions': generated})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


