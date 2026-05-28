import os

class Config:
    OPENAI_API_KEY = os.getenv("openai_api_key")
    DATABASE_URL = os.getenv("database_url")
    SSL_ROOT_CERT = os.getenv("ssl_root_cert", "certs/prod-ca-2021.crt")
    DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"