import logging.config
from pathlib import Path


def configure_logging() -> None:
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "standard",
                "stream": "ext://flask.logging.wsgi_errors_stream",
            },
            "audit_file": {
                "class": "logging.FileHandler",
                "level": "INFO",
                "formatter": "standard",
                "filename": "logs/audit.jsonl",
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "app.audit": {
                "level": "INFO",
                "handlers": ["audit_file"],
                "propagate": False,
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"],
        },
    })