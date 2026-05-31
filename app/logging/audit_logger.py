import json
import logging
from datetime import datetime, timezone
from hashlib import sha256



LOGGER_NAME = "app.audit"


def get_audit_logger() -> logging.Logger:
    return logging.getLogger(LOGGER_NAME)


def _write_jsonl(event: dict) -> None:
    logger = get_audit_logger()
    logger.info(json.dumps(event, ensure_ascii=False))


def _query_hash(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def log_generate_request(user_query: str, sanitized_query: str) -> None:
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": "generate_request",
        "user_query": user_query,
        "sanitized_query": sanitized_query,
        "sanitized_query_sha256": _query_hash(sanitized_query),
    }
    _write_jsonl(event)


def log_generate_response(
    user_query: str,
    llm_comment: str,
    raw_llm_response: str,
    generated_sql: str,
    status: str,
    error: str | None = None,
) -> None:
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": "generate_response",
        "user_query": user_query,
        "llm_comment": llm_comment,
        "raw_llm_response": raw_llm_response,
        "generated_sql": generated_sql,
        "status": status,
        "error": error,
    }
    _write_jsonl(event)


def log_execute_request(user_query: str, generated_sql: str, llm_comment: str | None = None) -> None:
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": "execute_request",
        "user_query": user_query,
        "llm_comment": llm_comment,
        "generated_sql": generated_sql,
    }
    _write_jsonl(event)


def log_execute_response(
    user_query: str,
    generated_sql: str,
    row_count: int,
    execution_time_ms: float | None,
    error: str | None,
) -> None:
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": "execute_response",
        "user_query": user_query,
        "generated_sql": generated_sql,
        "row_count": row_count,
        "execution_time_ms": execution_time_ms,
        "error": error,
    }
    _write_jsonl(event)