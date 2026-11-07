from app.core.llm_factory import get_llm

try:
    llm = get_llm()
    response = llm.invoke(
        "Explain what a Voice of Customer platform does in two sentences."
    )

    print("OpenAI connection successful!")
    print(response.content)

except Exception as error:
    print("OpenAI connection failed:")
    print(error)