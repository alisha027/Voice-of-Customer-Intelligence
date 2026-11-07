
from app.workflows.state import VOCState
from app.services.sql_executor import execute_readonly_query


def sql_executor_agent(state: VOCState) -> dict:

    try:
        results = execute_readonly_query(
            state["sql_query"]
        )

        print(f"SQL executed successfully: {len(results)} rows")

        return {
            "query_results": results,
            "sql_error": None,
            "error": None
        }

    except Exception as error:

        print("SQL execution error:", error)

        return {
            "query_results": [],
            "sql_error": str(error),
            "error": None
        }
