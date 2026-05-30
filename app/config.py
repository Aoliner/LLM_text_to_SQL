import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
    SSL_ROOT_CERT = os.getenv("SSL_ROOT_CERT", "certs/prod-ca-2021.crt")
    DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"