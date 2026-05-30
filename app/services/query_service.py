from ..safety import validate_user_prompt, detect_prompt_injection, sanitize_user_prompt
from ..llm import parse_llm_response, generate_sql
from ..sql_validation import validate_read_only_sql


def generate_query_result(user_request: str, client, system_message: str) -> dict:
    base_result = {
        "user_query": user_request,
        "sql": None,
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

    is_ok, validation_error = validate_user_prompt(user_request)
    if not is_ok:
        base_result["has_error"] = True
        base_result["status"] = "error"
        base_result["error"] = validation_error
        return base_result

    if detect_prompt_injection(user_request):
        base_result["has_error"] = True
        base_result["status"] = "unsafe"
        base_result["error"] = "Request blocked due to suspected prompt injection."
        return base_result

    safe_user_request = sanitize_user_prompt(user_request)

    try:
        full_response = generate_sql(client, system_message, safe_user_request)
    except Exception as e:
        base_result["has_error"] = True
        base_result["status"] = "error"
        base_result["error"] = f"Model error: {str(e)}"
        return base_result

    llm_comment, generated_sql = parse_llm_response(full_response)

    base_result["sql"] = full_response
    base_result["llm_comment"] = llm_comment
    base_result["generated_sql"] = generated_sql

    has_sql_body = bool(generated_sql and generated_sql.strip())

    if llm_comment.startswith("-- UNSAFE_REQUEST:"):
        if has_sql_body:
            base_result["has_error"] = True
            base_result["status"] = "error"
            base_result["error"] = "Malformed model response: UNSAFE_REQUEST must not include SQL."
            base_result["generated_sql"] = ""
            return base_result

        base_result["has_error"] = True
        base_result["status"] = "unsafe"
        base_result["error"] = "Unsafe request blocked."
        return base_result

    if llm_comment.startswith("-- CLARIFY:"):
        if has_sql_body:
            base_result["has_error"] = True
            base_result["status"] = "error"
            base_result["error"] = "Malformed model response: CLARIFY must not include SQL."
            base_result["generated_sql"] = ""
            return base_result

        base_result["status"] = "clarify"
        return base_result

    if llm_comment.startswith("-- CANNOT_ANSWER:"):
        if has_sql_body:
            base_result["has_error"] = True
            base_result["status"] = "error"
            base_result["error"] = "Malformed model response: CANNOT_ANSWER must not include SQL."
            base_result["generated_sql"] = ""
            return base_result

        base_result["status"] = "cannot_answer"
        return base_result

    if llm_comment.startswith("-- COMMENT:"):
        if not has_sql_body:
            base_result["has_error"] = True
            base_result["status"] = "error"
            base_result["error"] = "No valid SQL generated."
            return base_result

        is_valid, validation_message = validate_read_only_sql(generated_sql)
        if not is_valid:
            base_result["has_error"] = True
            base_result["status"] = "error"
            base_result["error"] = validation_message
            return base_result

        base_result["status"] = "ready"
        return base_result

    base_result["has_error"] = True
    base_result["status"] = "error"
    base_result["error"] = "Unexpected model response type."
    return base_result