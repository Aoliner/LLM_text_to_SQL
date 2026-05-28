from ..safety import validate_user_prompt, detect_prompt_injection, sanitize_user_prompt
from ..llm import parse_llm_response, generate_sql
from ..sql_validation import validate_read_only_sql


def generate_query_result(user_request: str, client, system_message: str) -> dict:
    is_ok, validation_error = validate_user_prompt(user_request)
    if not is_ok:
        return {
            "user_query": user_request,
            "has_error": True,
            "error": validation_error,
            "llm_comment": None,
            "generated_sql": None,
            "row_count": 0,
            "execution_time_ms": None,
            "rows": None,
            "columns": None,
        }

    if detect_prompt_injection(user_request):
        return {
            "user_query": user_request,
            "has_error": True,
            "error": "Request blocked due to suspected prompt injection.",
            "llm_comment": None,
            "generated_sql": None,
            "row_count": 0,
            "execution_time_ms": None,
            "rows": None,
            "columns": None,
        }

    safe_user_request = sanitize_user_prompt(user_request)
    full_response = generate_sql(client, system_message, safe_user_request)
    llm_comment, generated_sql = parse_llm_response(full_response)

    if llm_comment.startswith("-- UNSAFE_REQUEST"):
        return {
            "user_query": user_request,
            "sql": full_response,
            "llm_comment": llm_comment,
            "generated_sql": generated_sql,
            "has_error": True,
            "error": "Unsafe request blocked.",
            "row_count": 0,
            "execution_time_ms": None,
            "rows": None,
            "columns": None,
        }

    if not generated_sql.strip():
        return {
            "user_query": user_request,
            "sql": full_response,
            "llm_comment": llm_comment,
            "generated_sql": generated_sql,
            "has_error": True,
            "error": "No valid SQL generated.",
            "row_count": 0,
            "execution_time_ms": None,
            "rows": None,
            "columns": None,
        }

    is_valid, msg = validate_read_only_sql(generated_sql)
    if not is_valid:
        return {
            "user_query": user_request,
            "sql": full_response,
            "llm_comment": llm_comment,
            "generated_sql": generated_sql,
            "has_error": True,
            "error": msg,
            "row_count": 0,
            "execution_time_ms": None,
            "rows": None,
            "columns": None,
        }

    return {
        "user_query": user_request,
        "sql": full_response,
        "llm_comment": llm_comment,
        "generated_sql": generated_sql,
        "has_error": False,
        "error": None,
        "row_count": 0,
        "execution_time_ms": None,
        "rows": None,
        "columns": None,
    }