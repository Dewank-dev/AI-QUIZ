from app import create_app

app = create_app()

if __name__ == '__main__':
    # Disable the Werkzeug reloader when running inside environments
    # (e.g., Streamlit runner) that do not allow signal handlers.
    app.run(debug=True, use_reloader=False)
