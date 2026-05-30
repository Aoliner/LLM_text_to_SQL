from flask import Blueprint, render_template, request

from .dependencies import client, database_url, ssl_root_cert, prompt_context
from .services.query_service import generate_query_result
from .services.execution_service import execute_query

bp = Blueprint("main", __name__)


@bp.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template(
            "index.html",
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

    user_request = request.form["query"]
    action = request.form.get("action")

    if action == "generate":
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
            "has_error": False,
            "error": None,
            "row_count": 0,
            "execution_time_ms": None,
            "rows": None,
            "columns": None,
        }

        if not generated_sql.strip():
            result["has_error"] = True
            result["error"] = "No SQL query to execute."
            return render_template("index.html", **result)

        execution_result = execute_query(
            generated_sql=generated_sql,
            database_url=database_url,
            ssl_root_cert=ssl_root_cert,
        )

        result.update(execution_result)
        result["has_error"] = bool(execution_result["error"])

    else:
        result = {
            "user_query": user_request,
            "sql": None,
            "generated_sql": "",
            "llm_comment": None,
            "has_error": True,
            "error": "Invalid action.",
            "row_count": 0,
            "execution_time_ms": None,
            "rows": None,
            "columns": None,
        }

    return render_template("index.html", **result)