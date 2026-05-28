import os
from dotenv import load_dotenv

from .llm import create_client
from .services.schema_service import build_prompt_context


load_dotenv()

client = create_client()
database_url = os.getenv("database_url")
ssl_root_cert = os.getenv("ssl_root_cert", "certs/prod-ca-2021.crt")
prompt_context = build_prompt_context(database_url, ssl_root_cert)