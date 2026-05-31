from ..safety import validate_user_prompt, detect_prompt_injection, sanitize_user_prompt
from ..llm import parse_llm_response, generate_sql
from ..sql_validation import validate_read_only_sql
from ..logging.audit_logger import log_generate_request, log_generate_response


def _base_result(user_request: str) -> dict:
    return {
        "user_query": user_request,
        "raw_llm_response": "",
        "llm_comment": None,
        "generated_sql": "",
        "status": "error",
        "has_error": False,
        "error": None,
        "row_count": 0,
        "execution_time_ms": None,
        "rows": None,
        "columns": None,
    }


def _log_response(result: dict) -> dict:
    log_generate_response(
        user_query=result["user_query"],
        llm_comment=result["llm_comment"] or "",
        raw_llm_response=result["raw_llm_response"],
        generated_sql=result["generated_sql"],
        status=result["status"],
        error=result["error"],
    )
    return result


def _set_error(result: dict, error: str, status: str = "error") -> dict:
    result["has_error"] = True
    result["status"] = status
    result["error"] = error
    return result


def _validate_user_request(result: dict, user_request: str) -> tuple[dict, str | None]:
    is_ok, validation_error = validate_user_prompt(user_request)
    if not is_ok:
        return _set_error(result, validation_error), None

    if detect_prompt_injection(user_request):
        return _set_error(
            result,
            "Request blocked due to suspected prompt injection.",
            status="unsafe",
        ), None

    return result, sanitize_user_prompt(user_request)


def _handle_control_response(
    result: dict,
    llm_comment: str,
    generated_sql: str,
) -> dict:
    has_sql_body = bool(generated_sql.strip())

    control_types = {
        "-- UNSAFE_REQUEST:": ("unsafe", "Unsafe request blocked."),
        "-- CLARIFY:": ("clarify", None),
        "-- CANNOT_ANSWER:": ("cannot_answer", None),
    }

    for prefix, (status, error_message) in control_types.items():
        if llm_comment.startswith(prefix):
            if has_sql_body:
                result["generated_sql"] = ""
                return _set_error(
                    result,
                    f"Malformed model response: {prefix[3:-1]} must not include SQL.",
                )

            result["status"] = status
            result["has_error"] = error_message is not None
            result["error"] = error_message
            return result

    return result


def _handle_comment_response(result: dict, generated_sql: str) -> dict:
    if not generated_sql.strip():
        return _set_error(result, "No valid SQL generated.")

    is_valid, validation_message = validate_read_only_sql(generated_sql)
    if not is_valid:
        return _set_error(result, validation_message)

    result["status"] = "ready"
    return result


def generate_query_result(user_request: str, client, system_message: str) -> dict:
    result = _base_result(user_request)

    result, safe_user_request = _validate_user_request(result, user_request)
    if safe_user_request is None:
        return result

    log_generate_request(
        user_query=user_request,
        sanitized_query=safe_user_request,
    )

    try:
        raw_llm_response = generate_sql(client, system_message, safe_user_request)
    except Exception as e:
        _set_error(result, f"Model error: {e}")
        return _log_response(result)

    llm_comment, generated_sql = parse_llm_response(raw_llm_response)

    result["raw_llm_response"] = raw_llm_response
    result["llm_comment"] = llm_comment
    result["generated_sql"] = generated_sql

    if llm_comment.startswith(("-- UNSAFE_REQUEST:", "-- CLARIFY:", "-- CANNOT_ANSWER:")):
        return _log_response(_handle_control_response(result, llm_comment, generated_sql))

    if llm_comment.startswith("-- COMMENT:"):
        return _log_response(_handle_comment_response(result, generated_sql))

    _set_error(result, "Unexpected model response type.")
    return _log_response(result)