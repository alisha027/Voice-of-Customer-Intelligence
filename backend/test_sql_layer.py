
from app.services.sql_safety import validate_sql, SQLValidationError

queries = {
    "simple_select": """
        SELECT uuid
        FROM enriched_unified_data
    """,

    "valid_cte": """
        WITH retailer_complaints AS (
            SELECT retailer_name, uuid
            FROM enriched_unified_data
        )
        SELECT retailer_name, COUNT(DISTINCT uuid) AS total
        FROM retailer_complaints
        GROUP BY retailer_name
    """,

    "unauthorized_table": """
        SELECT * FROM customer_database
    """,

    "delete_query": """
        DELETE FROM enriched_unified_data
    """,

    "multiple_statements": """
        SELECT uuid FROM enriched_unified_data;
        SELECT uuid FROM enriched_unified_data;
    """
}

for name, query in queries.items():
    try:
        result = validate_sql(query)
        print(f"PASS: {name}")
        print(result)
    except SQLValidationError as error:
        print(f"REJECTED: {name} -> {error}")
