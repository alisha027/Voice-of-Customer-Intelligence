
from pydantic import BaseModel, Field

from app.core.llm_factory import get_llm
from app.workflows.state import VOCState


class ExecutiveInsights(BaseModel):
    executive_summary: str = Field(
        description=(
            "A concise executive summary based strictly on "
            "the available SQL results and supporting evidence."
        )
    )

    key_findings: list[str] = Field(
        description=(
            "Three to five specific findings supported by "
            "the supplied evidence. Avoid unsupported claims."
        )
    )

    recommendations: list[str] = Field(
        description=(
            "Three practical, evidence-based business "
            "recommendations linked to identified findings."
        )
    )


def executive_synthesis_agent(state: VOCState) -> dict:
    """
    Combines SQL analysis, customer verbatims and source
    distribution into evidence-based executive insights.
    """

    print("Executive Synthesis Agent: Generating insights...")

    query_results = state.get("query_results") or []
    customer_quotes = state.get("customer_quotes") or []
    source_distribution = state.get("source_distribution") or []

    sql_error = state.get("sql_error")
    verbatim_error = state.get("verbatim_error")
    source_error = state.get("source_error")

    # Handle the situation where no analytical evidence exists.
    if sql_error or not query_results:
        reason = (
            "SQL execution failed."
            if sql_error
            else "The SQL query returned no matching records."
        )

        print(f"Executive Synthesis: {reason}")

        return {
            "executive_summary": (
                f"The requested analysis could not be completed. "
                f"{reason} Please refine the question or verify "
                f"the available dataset."
            ),
            "key_findings": [],
            "recommendations": [
                "Review the query filters and verify that "
                "matching records exist in the dataset."
            ],
            "synthesis_error": None
        }

    try:
        llm = get_llm()

        structured_llm = llm.with_structured_output(
            ExecutiveInsights
        )

        prompt = f"""
You are a senior Voice of Customer (VOC) business analyst.

Your responsibility is to transform the supplied analytical
evidence into accurate, concise and actionable business insights.

You must prioritize factual correctness over persuasive language.

==================================================
USER QUESTION
==================================================

{state.get("user_query", "")}

==================================================
1. SQL ANALYSIS RESULTS — PRIMARY NUMERICAL EVIDENCE
==================================================

{query_results}

SQL ERROR:
{sql_error}

RULES:

1. SQL results are the source of truth for numerical claims.
2. Never invent, modify or estimate counts.
3. Do not introduce retailers, products or categories
   that are absent from the SQL results.
4. If SQL results are empty, do not invent findings.
5. Distinguish complaint volume from complaint rate.
6. A higher complaint count does NOT establish a higher
   dissatisfaction rate or worse retailer performance.
7. Only discuss dissatisfaction rates if both the complaint
   count and total review denominator are provided.
8. Do not assume zero complaints unless the SQL query
   explicitly establishes zero matching records.
9. Do not assume that counts from different groups represent
   globally unique reviews if UUIDs may overlap.

==================================================
2. CUSTOMER VERBATIMS — QUALITATIVE EVIDENCE
==================================================

{customer_quotes}

VERBATIM ERROR:
{verbatim_error}

RULES:

1. Use quotes only as qualitative supporting evidence.
2. Never use a few selected quotes to establish the
   frequency of a complaint.
3. Do not rewrite or fabricate customer statements.
4. Identify the retailer and product accurately.
5. Distinguish product complaints from retailer complaints.
6. A display issue is a product complaint.
7. Aggressive sales tactics or poor replacement handling
   are retailer experience complaints.
8. Do not claim that every retailer has the same problem
   based on a quote from only one retailer.
9. If quotes are unrelated to the user's question,
   do not use them as supporting evidence.
10. If no relevant quotes exist, acknowledge the limitation.

==================================================
3. SOURCE DISTRIBUTION — CHANNEL EVIDENCE
==================================================

{source_distribution}

SOURCE DISTRIBUTION ERROR:
{source_error}

Interpretation:

- RATINGS_REVIEWS = Direct customer product reviews.
- HML = Customer support conversations.
- WOTS = Retail observations, field notes or promoter reports.

RULES:

1. Describe each source accurately.
2. Do not present WOTS observations as direct customer quotes.
3. Do not confuse source distribution with retailer
   complaint distribution.
4. Do not use source percentages to claim product quality
   or retailer performance.
5. If source distribution is unavailable, acknowledge it
   only when relevant to the requested analysis.

==================================================
4. EXECUTIVE SUMMARY
==================================================

Write a concise summary that:

1. Directly answers the user's question.
2. Highlights the most important SQL findings.
3. Uses relevant customer quotes as supporting evidence.
4. Identifies important limitations in the available data.
5. Avoids unsupported comparisons or conclusions.

==================================================
5. KEY FINDINGS
==================================================

Provide three to five findings.

Each finding must:

- Be supported by SQL results or relevant verbatims.
- Use exact counts when available.
- Distinguish numerical findings from qualitative observations.
- Avoid unsupported causal explanations.
- Avoid claiming that a retailer performs better
  based only on lower complaint volume.

==================================================
6. BUSINESS RECOMMENDATIONS
==================================================

Provide three actionable recommendations.

Each recommendation must:

- Be connected to an identified finding.
- Address a specific product, service or customer issue.
- Be practical and relevant to the business.
- Avoid generic suggestions unsupported by evidence.

Do not recommend fixing a problem that is not supported
by the supplied evidence.

==================================================
7. FINAL CONSISTENCY CHECK
==================================================

Before returning the structured response, verify:

- Do all numerical claims match SQL results?
- Are retailer names and counts correct?
- Are complaint counts distinguished from complaint rates?
- Are product complaints distinguished from retail complaints?
- Are customer quotes relevant to the question?
- Are source categories described accurately?
- Are recommendations supported by the findings?
- Are missing or conflicting results acknowledged?

If evidence is insufficient, explicitly state the limitation
instead of making an unsupported conclusion.

Return structured output matching the requested schema.
"""

        insights = structured_llm.invoke(prompt)

        print("Executive Synthesis Agent: Completed.")

        return {
            "executive_summary": insights.executive_summary,
            "key_findings": insights.key_findings,
            "recommendations": insights.recommendations,
            "synthesis_error": None
        }

    except Exception as error:
        print("Executive Synthesis Error:", error)

        return {
            "executive_summary": (
                "Executive synthesis could not be generated."
            ),
            "key_findings": [],
            "recommendations": [],
            "synthesis_error": str(error)
        }
