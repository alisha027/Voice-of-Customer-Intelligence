
from app.workflows.state import VOCState
from app.core.llm_factory import get_llm
from app.services.sql_safety import validate_sql


def sql_repair_agent(state: VOCState) -> dict:

    retry_count = state.get("retry_count", 0)

    try:
        llm = get_llm(temperature=0)

        prompt = f"""
        You are a PostgreSQL SQL debugging expert.

        The following SQL query failed during execution.

        Original user question:
        {state["user_query"]}

        Failed SQL:
        {state["sql_query"]}

        Database error:
        {state["sql_error"]}

        Available table:
        enriched_unified_data

        Important columns:
        uuid, customer_voice, product_name, product_family,
        brand_name, retailer_name, sentiment, maintheme,
        subtheme, customer_rating, engagement_date,
        data_source_type.

        Rules:
        1. Return only one SELECT statement.
        2. Only use enriched_unified_data.
        3. Never invent column names.
        4. Use PostgreSQL syntax.
        5. Preserve the original analytical intent.
        6. Do not return markdown or explanations.
        """

        response = llm.invoke(prompt)

        repaired_sql = response.content.strip()

        if repaired_sql.startswith("```"):
            repaired_sql = repaired_sql.split("\n", 1)[1]
            repaired_sql = repaired_sql.rsplit("```", 1)[0].strip()

        safe_sql = validate_sql(repaired_sql)

        return {
            "sql_query": safe_sql,
            "retry_count": retry_count + 1,
            "sql_error": None,
            "error": None
        }

    except Exception as error:

        return {
            "retry_count": retry_count + 1,
            "error": f"SQL repair failed: {error}"
        }
