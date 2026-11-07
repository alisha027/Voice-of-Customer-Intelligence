
import re

from app.core.llm_factory import get_llm
from app.services.sql_safety import validate_sql
from app.services.sql_executor import execute_readonly_query
from app.workflows.state import VOCState


def generate_source_sql(user_query: str) -> str:
    llm = get_llm(temperature=0)

    
    prompt = f"""
    You are a PostgreSQL analytics query generator.

    Generate ONE SELECT query to calculate source distribution
    for this Voice of Customer question:

    USER QUESTION:
    {user_query}

    TABLE: enriched_unified_data

    AVAILABLE COLUMNS:
    uuid, data_source_type, engagement_date, customer_voice,
    product_name, brand_name, retailer_name, sentiment,
    maintheme, subtheme, explanation, customer_rating

    RULES:

    1. Use only enriched_unified_data.
    2. Return:
    data_source_type,
    COUNT(DISTINCT uuid) AS unique_interactions.
    3. Group by data_source_type.
    4. Use ILIKE for product and text matching.
    5. NEVER use exact equality for product_name when the
    user mentions a product family or partial product name.
    6. For Microsoft Surface, use:
    product_name ILIKE '%Surface%'
    7. For battery-related questions, consider:
    maintheme ILIKE '%Battery%'
    OR subtheme ILIKE '%Battery%'
    OR subtheme ILIKE '%Charging%'
    OR subtheme ILIKE '%Sleep%'
    OR subtheme ILIKE '%Power%'
    8. If the question asks about negative complaints, use:
    LOWER(sentiment) = 'negative'.
    9. Use only filters supported by the user's question.
    10. Do not invent exact product names, themes, or values.
    11. Do not use SELECT *.
    12. Do not use multiple statements.
    13. Do not use unnecessary restrictive filters.
    14. Order by unique_interactions DESC.
    15. Return ONLY PostgreSQL SQL without Markdown.
    """


    response = llm.invoke(prompt)
    sql_query = response.content.strip()

    sql_query = re.sub(
        r"^```(?:sql)?\s*",
        "",
        sql_query,
        flags=re.IGNORECASE
    )
    sql_query = re.sub(r"\s*```$", "", sql_query)

    results = execute_readonly_query(sql_query)

    print("Source distribution SQL results:", results)
    print("Number of source categories:", len(results))

    if not results:
        print("Source Agent: Query returned zero rows.")

        return {
            "source_distribution": [],
            "source_error": "No matching source records were found."
        }

    return validate_sql(sql_query)


def source_distribution_agent(state: VOCState) -> dict:
    try:
        user_query = state["user_query"]

        print("Source Agent: Generating source distribution SQL...")

        sql_query = generate_source_sql(user_query)
        print("\nGenerated Source Distribution SQL:")
        print(sql_query)

        print("Source Agent: Executing source distribution query...")

        results = execute_readonly_query(sql_query)

        total = sum(
            int(row["unique_interactions"])
            for row in results
        )

        distribution = []

        for row in results:
            count = int(row["unique_interactions"])

            distribution.append({
                "source": row["data_source_type"],
                "unique_interactions": count,
                "percentage": round(
                    (count / total) * 100, 2
                ) if total else 0
            })

        print(
            f"Source Agent: Retrieved {len(distribution)} source categories."
        )

        return {
            "source_distribution": distribution,
            "source_error": None
        }

    except Exception as error:
        print("Source Agent Error:", error)

        return {
            "source_distribution": [],
            "source_error": str(error)
        }
