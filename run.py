from app import create_app

app = create_app()

if __name__ == '__main__':
    # Only start the Flask dev server when explicitly requested via
    # the FLASK_RUN environment variable. This prevents the Flask
    # dev server from being started automatically inside multi-process
    # runners (Streamlit/Uvicorn) which would cause port conflicts.
    import os

    if os.environ.get('FLASK_RUN', '0') == '1':
        # Keep the reloader disabled to avoid multiple startups.
        app.run(debug=True, use_reloader=False)
    else:
        print('Flask app created but not started. Set FLASK_RUN=1 to run locally.')
