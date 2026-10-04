import os
from flask import Flask
from dotenv import load_dotenv


def create_app(test_config=None):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    load_dotenv(os.path.join(base_dir, '..', '.env'))

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.Config')

    if test_config:
        app.config.update(test_config)

    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # register routes blueprint
    from . import routes
    app.register_blueprint(routes.bp)

    return app
