
import json
import re

from pydantic import BaseModel, Field

from app.core.llm_factory import get_llm
from app.services.sql_safety import validate_sql
from app.services.sql_executor import execute_readonly_query
from app.workflows.state import VOCState


class VerbatimSelection(BaseModel):
    selected_uuids: list[str] = Field(
        description="UUIDs of the most relevant customer reviews, maximum 4"
    )


def normalize_quote(quote: str) -> str:
    """Normalize whitespace and casing for duplicate detection."""
    return re.sub(r"\s+", " ", quote).strip().lower()




def generate_candidate_sql(user_query: str) -> str:
    """Generate SQL to retrieve relevant individual customer reviews."""
    llm = get_llm(temperature=0)

    prompt = f"""
You are a PostgreSQL query generator for a Voice of Customer platform.

Generate ONE SELECT query to retrieve individual customer reviews
relevant to this question:

USER QUESTION:
{user_query}

TABLE: enriched_unified_data

AVAILABLE COLUMNS:
uuid, data_source_type, engagement_date, customer_voice,
product_name, brand_name, retailer_name, sentiment,
maintheme, subtheme, explanation, customer_rating

RULES:
1. Use only enriched_unified_data.
2. Return individual rows, not aggregated results.
3. Include uuid, product_name, customer_voice, retailer_name,
   customer_rating, sentiment, maintheme, subtheme,
   data_source_type and engagement_date.
4. customer_voice must not be NULL or empty.
5. Prefer RATINGS_REVIEWS for direct customer reviews.
6. Select reviews directly relevant to the question.
7. For Microsoft Surface battery questions, include relevant
   battery, charging, sleep and power complaints.
8. For Copilot AI questions, prioritize feedback that explicitly
   discusses Copilot or AI capabilities.
9. Do not assume sentiment labels are always reliable.
10. Do not use GROUP BY or SELECT *.
11. Order by engagement_date DESC.
12. Limit results to 30.
13. Return only PostgreSQL SQL.
"""

    response = llm.invoke(prompt)
    content = response.content

    if isinstance(content, list):
        sql_query = "\n".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict)
        ).strip()
    elif isinstance(content, str):
        sql_query = content.strip()
    else:
        raise ValueError("LLM returned an unsupported response format.")

    # Remove Markdown fences, even if there is surrounding whitespace.
    sql_query = re.sub(
        r"^\s*```(?:sql)?\s*",
        "",
        sql_query,
        flags=re.IGNORECASE
    )
    sql_query = re.sub(r"\s*```\s*$", "", sql_query)

    if not sql_query:
        raise ValueError("LLM returned an empty SQL response.")

    print("\nCleaned Verbatim SQL:")
    print(sql_query)

    return validate_sql(sql_query)





def remove_duplicate_reviews(reviews: list[dict]) -> list[dict]:
    """Keep one record per unique customer interaction."""
    unique_reviews = []
    seen_uuids = set()

    for review in reviews:
        uuid = review.get("uuid")

        if not uuid or uuid in seen_uuids:
            continue

        quote = review.get("customer_voice") or ""
        if not quote.strip():
            continue

        seen_uuids.add(uuid)
        unique_reviews.append(review)

    return unique_reviews



def select_relevant_reviews(
    user_query: str,
    candidate_reviews: list[dict]
) -> list[dict]:
    """
    Ask the LLM to select up to four relevant reviews.
    Original customer quotes are never rewritten.
    """

    if not candidate_reviews:
        return []

    llm = get_llm(temperature=0)
    selector = llm.with_structured_output(VerbatimSelection)

    prompt = f"""
You are a Voice of Customer analyst.

Select the 2 to 4 most relevant customer reviews for this question:

USER QUESTION:
{user_query}

CANDIDATE REVIEWS:
{json.dumps(candidate_reviews, default=str, ensure_ascii=False)}

SELECTION RULES:
1. Select only reviews that directly address the user's question.
2. Prefer specific, authentic customer experiences.
3. Prefer distinct complaint patterns rather than repetitive reviews.
4. Avoid reviews that discuss unrelated issues.
5. Do not select a review merely because its theme label matches.
6. Do not invent UUIDs.
7. Return only UUIDs from the candidate reviews.
8. Select at most four reviews.
9. If fewer than two genuinely relevant reviews exist, return only
   the relevant ones.
10. Never rewrite or summarize the original customer voice.
11. Use customer_voice and customer_rating as primary evidence.
12. Do not reject or classify a review based solely on its sentiment label.
13. Prefer reviews with explicit descriptions of the issue being analyzed.

QUOTE DIVERSITY RULES:

1. Select quotes that represent the highest-count complaint
   categories from the SQL analysis.
2. Include at least one quote supporting the leading category.
3. Prefer coverage across different complaint categories.
4. Use authentic customer_voice text without rewriting it.
5. Include retailer, product, rating and source information.
6. Never select duplicate UUIDs.
7. Do not select a quote merely because its theme label
   matches the category; inspect the actual customer_voice.

"""

    response = selector.invoke(prompt)

    candidate_by_uuid = {
    review["uuid"]: review
    for review in candidate_reviews
}

    selected_reviews = []

    for selected_id in response.selected_uuids:
        review = candidate_by_uuid.get(selected_id)

        if review and review not in selected_reviews:
            selected_reviews.append(review)

    return selected_reviews[:4]


def verbatim_agent(state: VOCState) -> dict:
    """
    Retrieve and select authentic customer quotes relevant
    to the user's analytical question.
    """

    try:
        user_query = state["user_query"]

        print("Verbatim Agent: Generating candidate retrieval SQL...")

        candidate_sql = generate_candidate_sql(user_query)

        print("Verbatim Agent: Retrieving candidate reviews...")

        candidates = execute_readonly_query(candidate_sql)

        print(f"Verbatim Agent: Retrieved {len(candidates)} candidates.")

        # Remove exact duplicate customer voices.
        unique_candidates = remove_duplicate_reviews(candidates)

        print(
            f"Verbatim Agent: {len(unique_candidates)} unique reviews "
            "after deduplication."
        )

        # Select the most relevant reviews.
        selected_reviews = select_relevant_reviews(
            user_query,
            unique_candidates
        )

        print(
            f"Verbatim Agent: Selected {len(selected_reviews)} reviews."
        )

        return {
            "customer_quotes": selected_reviews,
            "verbatim_error": None
        }

    except Exception as error:
        print("Verbatim Agent Error:", error)

        return {
            "customer_quotes": [],
            "verbatim_error": str(error)
        }
