
from langgraph.graph import StateGraph, START, END

from app.workflows.state import VOCState

from app.agents.intent_router import intent_router
from app.agents.sql_generator import sql_generator
from app.agents.sql_executor_agent import sql_executor_agent
from app.agents.sql_repair import sql_repair_agent
from app.agents.verbatim_agent import verbatim_agent
from app.agents.source_distribution_agent import (
    source_distribution_agent
)
from app.agents.executive_synthesis_agent import (
    executive_synthesis_agent
)

def greeting_node(state: VOCState) -> dict:
    return {
        "final_answer": (
            "Hello! Welcome to VOC Intelligence 360. "
            "I can help you analyze customer feedback, "
            "sentiment, products and retailers."
        )
    }


def analysis_start_node(state: VOCState) -> dict:
    """Initialize values before parallel agent execution."""

    return {
        "query_results": [],
        "customer_quotes": [],
        "source_distribution": [],
        "executive_summary": "",
        "key_findings": [],
        "recommendations": [],
        "synthesis_error": None,
        "sql_error": None,
        "verbatim_error": None,
        "source_error": None,
        "retry_count": 0,
        "max_retries": state.get("max_retries", 2)
    }


def sql_complete_node(state: VOCState) -> dict:
    """Marks successful completion of the SQL branch."""
    print("SQL branch completed successfully.")
    return {}


def analysis_complete_node(state: VOCState) -> dict:
    """Build the final executive-ready response."""

    return {
        "final_answer": (
            "========== EXECUTIVE SUMMARY ==========\n"
            f"{state.get('executive_summary', '')}\n\n"

            "========== KEY FINDINGS ==========\n"
            + "\n".join(
                f"- {item}"
                for item in state.get("key_findings", [])
            )
            + "\n\n"

            "========== RECOMMENDATIONS ==========\n"
            + "\n".join(
                f"- {item}"
                for item in state.get("recommendations", [])
            )
            + "\n\n"

            "========== SQL ANALYSIS ==========\n"
            f"{state.get('query_results', [])}\n\n"

            "========== CUSTOMER VERBATIMS ==========\n"
            f"{state.get('customer_quotes', [])}\n\n"

            "========== SOURCE DISTRIBUTION ==========\n"
            f"{state.get('source_distribution', [])}\n\n"

            "========== AGENT STATUS ==========\n"
            f"SQL Error: {state.get('sql_error')}\n"
            f"Verbatim Error: {state.get('verbatim_error')}\n"
            f"Source Error: {state.get('source_error')}\n"
            f"Synthesis Error: {state.get('synthesis_error')}"
        )
    }


def error_node(state: VOCState) -> dict:
    return {
        "final_answer": state.get(
            "error",
            state.get(
                "sql_error",
                "An unexpected error occurred."
            )
        )
    }


def route_after_intent(state: VOCState) -> str:

    if state.get("error"):
        return "error"

    if state.get("intent") == "greeting":
        return "greeting"

    return "analysis_start"


def route_after_sql_generation(state: VOCState) -> str:

    if state.get("error"):
        return "error"

    return "execute"


def route_after_execution(state: VOCState) -> str:

    if state.get("sql_error"):

        if state.get("retry_count", 0) < state.get(
            "max_retries", 2
        ):
            return "repair"

        return "error"

    return "sql_complete"


def route_after_repair(state: VOCState) -> str:

    if state.get("error"):
        return "error"

    return "execute"


# Build workflow
workflow = StateGraph(VOCState)

# Register nodes
workflow.add_node("intent_router", intent_router)
workflow.add_node("greeting", greeting_node)
workflow.add_node("analysis_start", analysis_start_node)

workflow.add_node("sql_generator", sql_generator)
workflow.add_node("sql_executor", sql_executor_agent)
workflow.add_node("sql_repair", sql_repair_agent)
workflow.add_node("sql_complete", sql_complete_node)

workflow.add_node("verbatim_agent", verbatim_agent)
workflow.add_node("source_distribution_agent", source_distribution_agent)

# Register executive synthesis BEFORE connecting edges
workflow.add_node(
    "executive_synthesis",
    executive_synthesis_agent
)

workflow.add_node("complete", analysis_complete_node)
workflow.add_node("error", error_node)


# Entry point
workflow.add_edge(START, "intent_router")


# Intent routing
workflow.add_conditional_edges(
    "intent_router",
    route_after_intent,
    {
        "greeting": "greeting",
        "analysis_start": "analysis_start",
        "error": "error"
    }
)

workflow.add_edge("greeting", END)


# Parallel fan-out
workflow.add_edge("analysis_start", "sql_generator")
workflow.add_edge("analysis_start", "verbatim_agent")
workflow.add_edge("analysis_start", "source_distribution_agent")


# SQL branch with retry mechanism
workflow.add_conditional_edges(
    "sql_generator",
    route_after_sql_generation,
    {
        "execute": "sql_executor",
        "error": "error"
    }
)

workflow.add_conditional_edges(
    "sql_executor",
    route_after_execution,
    {
        "repair": "sql_repair",
        "sql_complete": "sql_complete",
        "error": "error"
    }
)

workflow.add_conditional_edges(
    "sql_repair",
    route_after_repair,
    {
        "execute": "sql_executor",
        "error": "error"
    }
)


# Join all three successful branches
# Wait for all three parallel branches
workflow.add_edge(
    [
        "sql_complete",
        "verbatim_agent",
        "source_distribution_agent"
    ],
    "executive_synthesis"
)

# Generate the final executive response
workflow.add_edge(
    "executive_synthesis",
    "complete"
)


# End nodes
workflow.add_edge("complete", END)
workflow.add_edge("error", END)


voc_graph = workflow.compile()
