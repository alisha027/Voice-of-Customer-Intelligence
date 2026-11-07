
from sqlalchemy import text

from app.database.connection import engine
from app.services.sql_safety import validate_sql


def execute_readonly_query(query: str) -> list[dict]:

    # Validate before execution
    safe_query = validate_sql(query)

    try:
        with engine.connect() as connection:

            result = connection.execute(text(safe_query))

            rows = [
                dict(row)
                for row in result.mappings().all()
            ]

            return rows

    except Exception as error:
        raise RuntimeError(
            f"SQL execution failed: {str(error)}"
        ) from error
