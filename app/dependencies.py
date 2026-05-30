from flask import current_app

from .llm import create_client
from .services.schema_service import build_prompt_context


def get_client():
    client = current_app.extensions.get("openai_client")
    if client is None:
        client = create_client(current_app.config["OPENAI_API_KEY"])
        current_app.extensions["openai_client"] = client
    return client


def get_prompt_context():
    prompt_context = current_app.extensions.get("prompt_context")
    if prompt_context is None:
        prompt_context = build_prompt_context(
            current_app.config["DATABASE_URL"],
            current_app.config["SSL_ROOT_CERT"],
        )
        current_app.extensions["prompt_context"] = prompt_context
    return prompt_context