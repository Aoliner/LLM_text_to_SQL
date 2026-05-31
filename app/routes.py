from flask import Blueprint, render_template, request, current_app
from .dependencies import get_client, get_prompt_context
from .logging.audit_logger import log_execute_request, log_execute_response
from .services.execution_service import execute_query
from .services.query_service import generate_query_result
from .sql_validation import validate_read_only_sql

bp = Blueprint("main", __name__)


def _initial_view_model() -> dict:
    return {
        "status": "idle",
        "execution_time_ms": None,
        "row_count": 0,
        "rows": None,
        "columns": None,
        "raw_llm_response": "",
        "generated_sql": "",
        "llm_comment": None,
        "user_query": "",
        "has_error": False,
        "error": None,
    }


def _error_result(user_request: str, error: str) -> dict:
    result = _initial_view_model()
    result.update(
        {
            "user_query": user_request,
            "status": "error",
            "has_error": True,
            "error": error,
        }
    )
    return result


def _build_execute_base_result(user_request: str, generated_sql: str, llm_comment: str) -> dict:
    return {
        "user_query": user_request,
        "raw_llm_response": "",
        "generated_sql": generated_sql,
        "llm_comment": llm_comment,
        "status": "ready",
        "has_error": False,
        "error": None,
        "row_count": 0,
        "execution_time_ms": None,
        "rows": None,
        "columns": None,
    }


def _handle_generate(user_request: str) -> dict:
    try:
        client = get_client()
        prompt_context = get_prompt_context()
    except Exception as e:
        return _error_result(user_request, f"Initialization error: {e}")

    return generate_query_result(
        user_request=user_request,
        client=client,
        system_message=prompt_context["system_message"],
    )


def _handle_execute(user_request: str) -> dict:
    generated_sql = request.form.get("generated_sql", "")
    llm_comment = request.form.get("llm_comment", "")
    result = _build_execute_base_result(user_request, generated_sql, llm_comment)

    log_execute_request(
        user_query=user_request,
        generated_sql=generated_sql,
        llm_comment=llm_comment,
    )

    if not generated_sql.strip():
        result.update(
            {
                "status": "error",
                "has_error": True,
                "error": "No SQL query to execute.",
            }
        )
        _log_execute_result(result)
        return result

    is_valid, validation_message = validate_read_only_sql(generated_sql)
    if not is_valid:
        result.update(
            {
                "status": "error",
                "has_error": True,
                "error": validation_message,
            }
        )
        _log_execute_result(result)
        return result

    execution_result = execute_query(
        generated_sql=generated_sql,
        database_url=current_app.config["DATABASE_URL"],
        ssl_root_cert=current_app.config["SSL_ROOT_CERT"],
    )

    result.update(execution_result)
    result["has_error"] = bool(result["error"])
    if result["has_error"]:
        result["status"] = "error"

    _log_execute_result(result)
    return result


def _log_execute_result(result: dict) -> None:
    log_execute_response(
        user_query=result["user_query"],
        generated_sql=result["generated_sql"],
        row_count=result["row_count"],
        execution_time_ms=result["execution_time_ms"],
        error=result["error"],
    )


def _handle_post() -> dict:
    user_request = request.form.get("query", "")
    action = request.form.get("action")

    handlers = {
        "generate": _handle_generate,
        "execute": _handle_execute,
    }

    handler = handlers.get(action)
    if handler is None:
        return _error_result(user_request, "Invalid action.")

    return handler(user_request)


@bp.get("/")
def home_get():
    return render_template("index.html", **_initial_view_model())


@bp.post("/")
def home_post():
    result = _handle_post()
    return render_template("index.html", **result)