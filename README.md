# AI Quiz Generator and Performance Analyzer

This is a beginner-friendly quiz application for generating quizzes and analyzing performance.
It can run as either a Streamlit app or the original Flask app.

Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run with Streamlit

```bash
streamlit run streamlit_app.py
# open the local URL shown in the terminal
```

Deploy to Streamlit Community Cloud

1. Push this project to GitHub.
2. Open Streamlit Community Cloud and create a new app.
3. Select the repository, branch, and set the main file path to `streamlit_app.py`.
4. Deploy. Streamlit will install dependencies from `requirements.txt`.

Optional environment variables for AI generation can be added in the app settings:

```bash
HF_API_KEY=your_hugging_face_token
HF_MODEL=google/flan-t5-small
```

Run the original Flask app

```bash
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
- Streamlit Community Cloud storage is ephemeral, so saved attempt history may reset when the app restarts.
