
from typing import TypedDict, Optional, Any


class VOCState(TypedDict, total=False):
    user_query: str
    intent: str

    # SQL analysis branch
    sql_query: str
    query_results: list[dict[str, Any]]
    sql_error: Optional[str]
    retry_count: int
    max_retries: int

    # Verbatim branch
    customer_quotes: list[dict[str, Any]]
    verbatim_error: Optional[str]

    # Source distribution branch
    source_distribution: list[dict[str, Any]]
    source_error: Optional[str]

    # Shared workflow output
    final_answer: str
    error: Optional[str]

    # Executive synthesis output
    executive_summary: str
    key_findings: list[str]
    recommendations: list[str]

    executive_summary: str
    key_findings: list[str]
    recommendations: list[str]
    synthesis_error: Optional[str]
