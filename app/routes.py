from flask import Blueprint, render_template, request, current_app

from .dependencies import get_client, get_prompt_context
from .services.query_service import generate_query_result
from .services.execution_service import execute_query
from .sql_validation import validate_read_only_sql

bp = Blueprint("main", __name__)


@bp.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template(
            "index.html",
            status="idle",
            execution_time_ms=None,
            row_count=0,
            rows=None,
            columns=None,
            generated_sql="",
            llm_comment=None,
            user_query="",
            has_error=False,
            error=None,
        )

    user_request = request.form.get("query", "")
    action = request.form.get("action")

    if action == "generate":
        client = get_client()
        prompt_context = get_prompt_context()

        result = generate_query_result(
            user_request=user_request,
            client=client,
            system_message=prompt_context["system_message"],
        )

    elif action == "execute":
        generated_sql = request.form.get("generated_sql", "")
        llm_comment = request.form.get("llm_comment", "")

        result = {
            "user_query": user_request,
            "sql": generated_sql,
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

        if not generated_sql.strip():
            result["has_error"] = True
            result["status"] = "error"
            result["error"] = "No SQL query to execute."
            return render_template("index.html", **result)

        is_valid, validation_message = validate_read_only_sql(generated_sql)
        if not is_valid:
            result["has_error"] = True
            result["status"] = "error"
            result["error"] = validation_message
            return render_template("index.html", **result)

        execution_result = execute_query(
            generated_sql=generated_sql,
            database_url=current_app.config["DATABASE_URL"],
            ssl_root_cert=current_app.config["SSL_ROOT_CERT"],
        )

        result.update(execution_result)
        result["has_error"] = bool(execution_result["error"])

        if result["has_error"]:
            result["status"] = "error"

    else:
        result = {
            "user_query": user_request,
            "sql": None,
            "generated_sql": "",
            "llm_comment": None,
            "status": "error",
            "has_error": True,
            "error": "Invalid action.",
            "row_count": 0,
            "execution_time_ms": None,
            "rows": None,
            "columns": None,
        }

    return render_template("index.html", **result)