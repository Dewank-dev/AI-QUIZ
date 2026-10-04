# AI Quiz Generator and Performance Analyzer

This is a beginner-friendly Flask application for generating quizzes and analyzing performance.

Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Initialize and run

```bash
python seed_database.py
python run.py
# open http://127.0.0.1:5000
```

Tests

```bash
pytest
```

Environment

Copy `.env.example` to `.env` and set `SECRET_KEY` and optional AI variables.

Notes

- To generate AI-like questions without an API, use the API endpoint `POST /api/generate-questions` with JSON payload.
- The application uses server-side evaluation; client cannot tamper with scores.
