from ..db import get_connection
from ..schema import load_relationships, load_schema_info, build_schema_json
from ..prompts import build_business_rules_text, build_system_message


def build_prompt_context(database_url: str, ssl_root_cert: str) -> dict:
    conn = None
    try:
        conn = get_connection(database_url, ssl_root_cert)
        relationships = load_relationships(conn)
        schema_info = load_schema_info(conn)
    finally:
        if conn is not None:
            conn.close()

    schema_json = build_schema_json(schema_info)
    business_rules_text = build_business_rules_text()
    system_message = build_system_message(schema_json, business_rules_text)

    return {
        "relationships": relationships,
        "schema_info": schema_info,
        "schema_json": schema_json,
        "business_rules_text": business_rules_text,
        "system_message": system_message,
    }