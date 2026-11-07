
import sqlglot
from sqlglot import exp


ALLOWED_TABLE = "enriched_unified_data"
MAX_ROWS = 100


class SQLValidationError(Exception):
    """Raised when a SQL query fails safety validation."""
    pass


def validate_sql(query: str) -> str:
    """
    Validate SQL before execution.

    Rules:
    1. Only one SQL statement is allowed.
    2. Only SELECT queries are allowed.
    3. Only enriched_unified_data can be accessed.
    4. CTE references are permitted.
    5. Schema-qualified and catalog-qualified tables are rejected.
    6. Results are limited to MAX_ROWS.
    """

    if not query or not query.strip():
        raise SQLValidationError("SQL query cannot be empty.")

    try:
        statements = sqlglot.parse(query, read="postgres")
    except Exception as error:
        raise SQLValidationError(
            f"Invalid SQL syntax: {error}"
        ) from error

    # Reject multiple statements
    if len(statements) != 1 or statements[0] is None:
        raise SQLValidationError(
            "Only one SQL statement is permitted."
        )

    parsed = statements[0]

    # Only SELECT queries are permitted
    if not isinstance(parsed, exp.Select):
        raise SQLValidationError(
            "Only SELECT queries are permitted."
        )

    # Collect CTE names defined in the query
    cte_names = {
        cte.alias_or_name.lower()
        for cte in parsed.find_all(exp.CTE)
    }

    # Validate every referenced table
    tables = list(parsed.find_all(exp.Table))

    if not tables:
        raise SQLValidationError(
            "Query must reference the approved feedback table."
        )

    physical_tables = []

    for table in tables:
        table_name = table.name.lower()

        # Permit references to CTEs
        if table_name in cte_names:
            continue

        # Reject schema-qualified or catalog-qualified references
        if table.db or table.catalog:
            raise SQLValidationError(
                "Schema-qualified table references are not permitted."
            )

        # Only permit the approved physical table
        if table_name != ALLOWED_TABLE.lower():
            raise SQLValidationError(
                f"Access to table '{table.name}' is not permitted."
            )

        physical_tables.append(table)

    if not physical_tables:
        raise SQLValidationError(
            "Query must reference the approved feedback table."
        )

    # Add a row limit if one is not already present.
    # This applies to the outermost SELECT.
    if parsed.args.get("limit") is None:
        parsed = parsed.limit(MAX_ROWS)

    return parsed.sql(dialect="postgres")
