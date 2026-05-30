from flask import Flask
from .routes import bp
from .config import Config
from .llm import create_client

def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(Config)

    if not app.config.get("OPENAI_API_KEY"):
        raise RuntimeError("Missing OPENAI_API_KEY")
    if not app.config.get("DATABASE_URL"):
        raise RuntimeError("Missing DATABASE_URL")

    app.extensions["openai_client"] = create_client(app.config["OPENAI_API_KEY"])
    app.extensions["prompt_context"] = None

    app.register_blueprint(bp)
    return app