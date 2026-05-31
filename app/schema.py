import json
import psycopg2
RELATIONSHIPS_SQL = """
SELECT
    tc.constraint_name,
    tc.table_name AS child_table,
    kcu.column_name AS child_column,
    ccu.table_name AS parent_table,
    ccu.column_name AS parent_column
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
   AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
   AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name, kcu.ordinal_position;
"""

COLUMNS_SQL = """
SELECT
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
"""

def load_relationships(conn):
    relationships = []
    try:
        with conn.cursor() as cur:
            cur.execute(RELATIONSHIPS_SQL)
            rows = cur.fetchall()
    except psycopg2.Error as e:
        raise RuntimeError(f"Failed to load relationships: {e}") from e

    for constraint_name, child_table, child_column, parent_table, parent_column in rows:
        relationships.append({
            "constraint_name": constraint_name,
            "child_table": child_table,
            "child_column": child_column,
            "parent_table": parent_table,
            "parent_column": parent_column
        })
    return relationships

def load_schema_info(conn):
    schema_info = {}
    try:
        with conn.cursor() as cur:
            cur.execute("SET statement_timeout = 5000;")
            cur.execute(COLUMNS_SQL)
            rows = cur.fetchall()
    except psycopg2.Error as e:
        raise RuntimeError(f"Failed to load schema info: {e}") from e

    for table_name, column_name, data_type, is_nullable in rows:
        schema_info.setdefault(table_name, []).append({
            "column_name": column_name,
            "data_type": data_type,
            "is_nullable": is_nullable
        })
    return schema_info

def build_schema_json(schema_info):
    return json.dumps(schema_info, indent=2)