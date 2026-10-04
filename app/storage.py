import os
import json
from datetime import datetime

QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'questions.json')
ATTEMPTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'instance', 'attempts.json')


def load_questions():
    with open(QUESTIONS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # ensure ids
    for i, q in enumerate(data, start=1):
        if 'id' not in q:
            q['id'] = i
    return data


def load_attempts():
    if not os.path.exists(ATTEMPTS_PATH):
        return []
    with open(ATTEMPTS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_attempt(attempt: dict):
    attempts = load_attempts()
    new_id = max([a.get('id',0) for a in attempts], default=0) + 1
    attempt['id'] = new_id
    attempt['created_at'] = datetime.utcnow().isoformat()
    attempts.append(attempt)
    os.makedirs(os.path.dirname(ATTEMPTS_PATH), exist_ok=True)
    with open(ATTEMPTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(attempts, f, indent=2)
    return attempt


def clear_attempts():
    """Clear all saved attempts (write an empty list)."""
    os.makedirs(os.path.dirname(ATTEMPTS_PATH), exist_ok=True)
    with open(ATTEMPTS_PATH, 'w', encoding='utf-8') as f:
        json.dump([], f, indent=2)
    return True
