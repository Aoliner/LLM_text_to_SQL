import time
from ..db import get_connection


def execute_query(generated_sql: str, database_url: str, ssl_root_cert: str) -> dict:
    conn = None  
    try:
        conn = get_connection(database_url, ssl_root_cert)
        with conn.cursor() as cur:
            start = time.perf_counter()
            cur.execute("SET statement_timeout = 6000;")
            cur.execute(generated_sql)
            rows = cur.fetchall()
            end = time.perf_counter()
            return {
                "rows": rows,
                "columns": [desc[0] for desc in cur.description] if cur.description else [],
                "row_count": len(rows),
                "execution_time_ms": round((end - start) * 1000, 2),
                "error": None,
            }
    except Exception as e:
        return {
            "rows": None, "columns": None, "row_count": 0,
            "execution_time_ms": None,
            "error": f"Execution error: {e}",
        }
    finally:
        if conn is not None:  
            conn.close()