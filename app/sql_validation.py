from sqlglot import exp
from sqlglot.errors import ParseError
import sqlglot

def validate_read_only_sql(query: str) -> tuple[bool, str]:
    try:
        statements = sqlglot.parse(query, read="postgres")
    except ParseError as e:
        return False, f"Invalid SQL syntax: {e}"

    if not statements:
        return False, "Empty SQL query"

    if len(statements) != 1:
        return False, "Only one SQL statement is allowed"

    stmt = statements[0]

    allowed_roots = (
        exp.Select,
        exp.With,
        exp.Union,
        exp.Intersect,
        exp.Except,
    )

    if not isinstance(stmt, allowed_roots):
        return False, f"Only SELECT queries are allowed, got: {stmt.key}"

    forbidden = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Create,
        exp.Drop,
        exp.Alter,
        exp.Merge,
        exp.Copy,
        exp.Command,
        exp.Lock,
        exp.Grant,
        exp.Revoke
    )

    bad_node = next(stmt.find_all(*forbidden), None)
    if bad_node:
        return False, f"Forbidden SQL operation detected: {bad_node.key}"

    return True, "OK"