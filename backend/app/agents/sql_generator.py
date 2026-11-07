
from app.core.llm_factory import get_llm
from app.workflows.state import VOCState
from app.prompts.sql_generation_prompt import SQL_GENERATION_PROMPT
from app.services.sql_safety import validate_sql, SQLValidationError


def sql_generator(state: VOCState) -> dict:

    try:
        llm = get_llm(temperature=0)

        prompt = SQL_GENERATION_PROMPT.format(
            user_query=state["user_query"]
        )

        response = llm.invoke(prompt)
        generated_sql = response.content.strip()

        if generated_sql.startswith("```"):
            generated_sql = generated_sql.split("\n", 1)[1]
            generated_sql = generated_sql.rsplit("```", 1)[0].strip()

        safe_sql = validate_sql(generated_sql)

        print("Generated SQL:", safe_sql)

        return {
            "sql_query": safe_sql,
            "sql_error": None,
            "error": None
        }

    except SQLValidationError as error:
        return {
            "sql_query": "",
            "error": f"SQL validation failed: {error}"
        }

    except Exception as error:
        return {
            "sql_query": "",
            "error": f"SQL generation failed: {error}"
        }
