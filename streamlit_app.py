from datetime import datetime

import streamlit as st
import plotly.express as px

from app.analyzer import analyze_performance
from app.evaluator import evaluate_quiz
from app.quiz_engine import QuizEngine
from app.storage import clear_attempts, load_attempts, load_questions, save_attempt


PAGES = ["HOME", "Quiz", "Results", "History"]


st.set_page_config(
    page_title="AI Quiz Generator",
    page_icon="Q",
    layout="wide",
)


def inject_global_styles():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"], [data-testid="collapsedControl"] {
            display: none;
        }

        .stApp {
            background:
                linear-gradient(180deg, #f7fbff 0%, #ffffff 44%, #f7fbf7 100%);
            color: #1f2430;
        }

        .block-container {
            max-width: 1180px;
            padding: 2rem 2rem 4rem;
        }

        .app-hero {
            background: linear-gradient(135deg, #ffffff 0%, #eef8f6 48%, #fff6ed 100%);
            border: 1px solid #e2ebe8;
            border-radius: 20px;
            box-shadow: 0 24px 70px rgba(22, 45, 61, 0.10);
            margin-bottom: 1.2rem;
            padding: 2rem;
        }

        .app-hero h1 {
            color: #1f2430;
            font-size: clamp(2.2rem, 5vw, 4.4rem);
            line-height: 1.02;
            margin: 0.1rem 0 0.8rem;
            letter-spacing: 0;
        }

        .app-hero p {
            color: #52606d;
            font-size: 1.08rem;
            line-height: 1.6;
            margin: 0;
            max-width: 720px;
        }

        .eyebrow {
            color: #008b7a !important;
            font-size: 0.78rem !important;
            font-weight: 800;
            letter-spacing: 0 !important;
            margin-bottom: 0.6rem !important;
            text-transform: uppercase;
        }

        .nav-wrap {
            align-items: center;
            display: flex;
            justify-content: center;
            margin: 0.6rem 0 2rem;
        }

        div[data-testid="stSegmentedControl"] {
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid #dfe8ed;
            border-radius: 999px;
            box-shadow: 0 18px 44px rgba(31, 36, 48, 0.12);
            padding: 0.38rem;
        }

        div[data-testid="stSegmentedControl"] button {
            border-radius: 999px;
            color: #485463;
            font-weight: 800;
            min-height: 2.7rem;
            padding: 0.35rem 1.05rem;
        }

        div[data-testid="stSegmentedControl"] button[aria-pressed="true"] {
            background: #1f2430;
            color: #ffffff;
            box-shadow: 0 10px 22px rgba(31, 36, 48, 0.24);
        }

        div[data-testid="stRadio"] {
            margin-top: 0.7rem;
        }

        div[data-testid="stRadio"] [role="radiogroup"] {
            gap: 0.55rem;
        }

        div[data-testid="stRadio"] label[data-baseweb="radio"] {
            background: #f8fafc;
            border: 1px solid #e3e9ef;
            border-radius: 12px;
            margin-bottom: 0.45rem;
            padding: 0.68rem 0.8rem;
            transition: border-color 160ms ease, box-shadow 160ms ease, background 160ms ease;
        }

        div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
            background: #eef8f6;
            border-color: #00a08d;
            box-shadow: 0 8px 20px rgba(0, 139, 122, 0.12);
        }

        h2, h3 {
            color: #1f2430;
            letter-spacing: 0;
        }

        div[data-testid="stSelectbox"] div[data-baseweb="select"],
        div[data-testid="stNumberInput"] input,
        div[data-testid="stTextInput"] input {
            background: #ffffff;
            border-color: #dce4ea;
            border-radius: 12px;
            box-shadow: 0 10px 26px rgba(31, 36, 48, 0.05);
        }

        .stButton > button,
        .stFormSubmitButton > button {
            border-radius: 12px;
            font-weight: 800;
            min-height: 3rem;
            padding: 0.55rem 1.1rem;
        }

        .stButton > button[kind="primary"],
        .stFormSubmitButton > button[kind="primary"] {
            background: linear-gradient(135deg, #ff4d4f 0%, #ff7b3f 100%);
            border: 0;
            box-shadow: 0 14px 26px rgba(255, 77, 79, 0.22);
        }

        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e4e9ee;
            border-radius: 16px;
            box-shadow: 0 16px 36px rgba(31, 36, 48, 0.07);
            padding: 1rem 1.1rem;
        }

        div[data-testid="stExpander"] details {
            background: #ffffff;
            border: 1px solid #e4e9ee;
            border-radius: 14px;
            box-shadow: 0 12px 28px rgba(31, 36, 48, 0.05);
        }

        div[data-testid="stAlert"] {
            border-radius: 14px;
        }

        hr {
            border-color: #e8edf1;
            margin: 1.2rem 0 1.6rem;
        }

        @media (max-width: 640px) {
            .block-container {
                padding: 1rem 1rem 3rem;
            }

            .app-hero {
                border-radius: 16px;
                padding: 1.2rem;
            }

            div[data-testid="stSegmentedControl"] {
                width: 100%;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_subjects():
    questions = load_questions()
    return sorted({q.get("subject") for q in questions if q.get("subject")})


def get_topics(subject):
    questions = load_questions()
    topics = sorted(
        {
            q.get("topic")
            for q in questions
            if q.get("subject") == subject and q.get("topic")
        }
    )
    return ["All"] + topics


def reset_quiz():
    keys_to_clear = [
        key
        for key in st.session_state
        if key.startswith("answer_")
        or key in ("quiz_questions", "quiz_meta", "quiz_result", "submitted_answers")
    ]
    for key in keys_to_clear:
        st.session_state.pop(key, None)


def start_quiz(subject, topic, difficulty, num_questions):
    engine = QuizEngine()
    questions = engine.fetch_questions(
        subject=subject,
        topic=topic,
        difficulty=difficulty,
        num=num_questions,
    )
    st.session_state.quiz_questions = questions
    st.session_state.quiz_meta = {
        "subject": subject,
        "topic": topic,
        "difficulty": difficulty,
        "num": len(questions),
    }
    st.session_state.pop("quiz_result", None)
    st.session_state.pop("submitted_answers", None)


def render_setup():
    st.header("Create a quiz")

    subjects = get_subjects()
    if not subjects:
        st.error("No questions found in data/questions.json.")
        return

    with st.container(border=True):
        col_subject, col_topic = st.columns(2)
        with col_subject:
            subject = st.selectbox("Subject", subjects)
        with col_topic:
            topic = st.selectbox("Topic", get_topics(subject))

        col_difficulty, col_count = st.columns(2)
        with col_difficulty:
            difficulty = st.selectbox("Difficulty", ["Mixed", "Easy", "Medium", "Hard"])
        with col_count:
            num_questions = st.number_input(
                "Number of questions",
                min_value=1,
                max_value=30,
                value=10,
                step=1,
            )

        if st.button("Start quiz", type="primary"):
            start_quiz(subject, topic, difficulty, int(num_questions))
            if st.session_state.quiz_questions:
                st.session_state.pending_page = "Quiz"
                st.rerun()
            else:
                st.warning("No questions are available for the selected criteria.")


def render_quiz():
    questions = st.session_state.get("quiz_questions", [])
    meta = st.session_state.get("quiz_meta")

    if not questions or not meta:
        st.info("Create a quiz first.")
        return

    st.header(f"{meta['subject']} Quiz")
    st.caption(
        f"Topic: {meta['topic']} | Difficulty: {meta['difficulty']} | "
        f"Questions: {meta['num']}"
    )

    with st.form("active_quiz"):
        answers = {}
        for index, question in enumerate(questions, start=1):
            with st.container(border=True):
                st.subheader(f"Question {index}")
                st.write(question.get("question"))
                selected = st.radio(
                    "Choose one answer",
                    question.get("options", []),
                    key=f"answer_{question.get('id')}_{index}",
                    index=None,
                )
            if selected:
                answers[str(question.get("id"))] = selected

        submitted = st.form_submit_button("Submit quiz", type="primary")

    if submitted:
        result = evaluate_quiz(questions, answers)
        analysis = analyze_performance(result["details"])
        saved = save_attempt(
            {
                "subject": meta.get("subject"),
                "topic": meta.get("topic"),
                "difficulty": meta.get("difficulty"),
                "questions": [q.get("id") for q in questions],
                "answers": answers,
                "score": result["correct"],
                "percent": result["percentage"],
            }
        )
        st.session_state.quiz_result = {
            "result": result,
            "analysis": analysis,
            "attempt": saved,
            "questions": questions,
        }
        st.session_state.submitted_answers = answers
        st.session_state.pending_page = "Results"
        st.rerun()


def render_results():
    payload = st.session_state.get("quiz_result")
    if not payload:
        st.info("Submit a quiz to see your result.")
        return

    result = payload["result"]
    analysis = payload["analysis"]
    questions_by_id = {str(q.get("id")): q for q in payload["questions"]}

    st.header("Results")
    col_score, col_percent, col_accuracy, col_unanswered = st.columns(4)
    col_score.metric("Score", result["score"])
    col_percent.metric("Percentage", f"{result['percentage']}%")
    col_accuracy.metric("Accuracy", f"{result['accuracy']}%")
    col_unanswered.metric("Unanswered", result["unanswered"])

    topic_percentages = analysis.get("topic_percentages", {})
    if topic_percentages:
        chart_data = [
            {"Topic": topic, "Score": score}
            for topic, score in topic_percentages.items()
        ]
        fig = px.bar(
            chart_data,
            x="Topic",
            y="Score",
            range_y=[0, 100],
            text="Score",
            color="Score",
            color_continuous_scale="Teal",
        )
        fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig, width="stretch")

    st.subheader("Feedback")
    for item in analysis.get("feedback", []):
        st.write(f"- {item}")

    st.subheader("Question review")
    for item in result["details"]:
        question = questions_by_id.get(str(item["id"]), {})
        with st.expander(f"{item['status']}: {question.get('question', 'Question')}"):
            st.write(f"Your answer: {item.get('given') or 'Unanswered'}")
            st.write(f"Correct answer: {item.get('correct_answer')}")
            explanation = question.get("explanation")
            if explanation:
                st.write(f"Explanation: {explanation}")


def render_history():
    st.header("Attempt history")
    attempts = sorted(load_attempts(), key=lambda item: item.get("created_at", ""), reverse=True)

    if not attempts:
        st.info("No saved attempts yet.")
        return

    col_clear, _ = st.columns([1, 4])
    with col_clear:
        if st.button("Clear history"):
            clear_attempts()
            st.rerun()

    rows = []
    for attempt in attempts:
        created_at = attempt.get("created_at", "")
        try:
            created_at = datetime.fromisoformat(created_at).strftime("%d %b %Y %H:%M")
        except ValueError:
            pass
        rows.append(
            {
                "Date": created_at,
                "Subject": attempt.get("subject"),
                "Topic": attempt.get("topic"),
                "Difficulty": attempt.get("difficulty"),
                "Score": attempt.get("score"),
                "Percent": attempt.get("percent"),
            }
        )

    st.dataframe(rows, width="stretch", hide_index=True)


inject_global_styles()

if "active_page" not in st.session_state:
    st.session_state.active_page = "HOME"
elif st.session_state.active_page not in PAGES:
    st.session_state.active_page = "HOME"

pending_page = st.session_state.pop("pending_page", None)
if pending_page in PAGES:
    st.session_state.active_page = pending_page
    st.session_state.nav_page = pending_page
elif "nav_page" not in st.session_state or st.session_state.nav_page not in PAGES:
    st.session_state.nav_page = st.session_state.active_page

st.markdown(
    """
    <section class="app-hero">
        <p class="eyebrow">Interactive Practice Lab</p>
        <h1>AI Quiz Generator</h1>
        <p>Build focused quizzes, answer at your pace, and review topic-wise performance in one clean workspace.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="nav-wrap">', unsafe_allow_html=True)
selected_page = st.segmented_control(
    "Navigation",
    PAGES,
    key="nav_page",
    label_visibility="collapsed",
    width="content",
)
st.markdown("</div>", unsafe_allow_html=True)
if selected_page is None:
    selected_page = st.session_state.active_page
st.session_state.active_page = selected_page

if selected_page == "HOME":
    render_setup()
elif selected_page == "Quiz":
    render_quiz()
elif selected_page == "Results":
    render_results()
else:
    render_history()
