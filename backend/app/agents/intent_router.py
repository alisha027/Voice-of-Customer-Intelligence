
from pydantic import BaseModel, Field
from typing import Literal

from app.workflows.state import VOCState
from app.core.llm_factory import get_llm


class IntentClassification(BaseModel):

    intent: Literal["greeting", "analysis"] = Field(
        description="Classify the user query as greeting or analysis"
    )


def intent_router(state: VOCState) -> dict:

    try:
        # Use Groq through our centralized LLM factory
        llm = get_llm(temperature=0)

        classifier = llm.with_structured_output(
            IntentClassification
        )

        response = classifier.invoke([
            (
                "system",
                """
                You are the intent classification agent
                for VOC Intelligence 360.

                Classify the user message into:

                greeting:
                Greetings and casual conversation.

                analysis:
                Questions about customer feedback, sentiment,
                products, brands, retailers, complaints,
                trends or comparisons.
                """
            ),
            ("human", state["user_query"])
        ])

        print("Detected intent:", response.intent)

        return {
            "intent": response.intent,
            "error": None
        }

    except Exception as error:

        print("Intent router error:", error)

        return {
            "error": f"Intent classification failed: {str(error)}"
        }
