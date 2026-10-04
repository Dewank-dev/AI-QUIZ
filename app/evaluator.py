def evaluate_quiz(questions, submitted_answers):
    total = len(questions)
    correct = 0
    incorrect = 0
    unanswered = 0
    details = []

    for q in questions:
        qid = str(q.get('id'))
        correct_answer = q.get('answer')
        given = submitted_answers.get(qid)
        status = 'Unanswered'
        if given is None:
            unanswered += 1
        else:
            if given == correct_answer:
                correct += 1
                status = 'Correct'
            else:
                incorrect += 1
                status = 'Incorrect'

        details.append({'id': qid, 'correct_answer': correct_answer, 'given': given, 'status': status, 'topic': q.get('topic', 'General')})

    score = correct
    percentage = (correct / total * 100) if total else 0
    accuracy = (correct / (correct + incorrect) * 100) if (correct + incorrect) else 0

    return {
        'total': total,
        'correct': correct,
        'incorrect': incorrect,
        'unanswered': unanswered,
        'score': f"{score}/{total}",
        'percentage': round(percentage,2),
        'accuracy': round(accuracy,2),
        'details': details
    }
