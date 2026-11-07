
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env", override=True)


def get_llm(temperature=0, model=None):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing from .env")

    selected_model = model or os.getenv(
        "OPENAI_MODEL",
        "gpt-4o-mini"
    )

    return ChatOpenAI(
        model=selected_model,
        temperature=temperature,
        api_key=api_key,
        timeout=60,
        max_retries=2
    )
