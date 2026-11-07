
from app.agents.verbatim_agent import verbatim_agent

test_state = {
    "user_query": (
        "Why are customers complaining about "
        "Microsoft Surface battery life?"
    )
}

result = verbatim_agent(test_state)

print("\n" + "=" * 60)
print("VERBATIM AGENT RESULTS")
print("=" * 60)

if result.get("verbatim_error"):
    print("Error:", result["verbatim_error"])
else:
    for index, review in enumerate(
        result["customer_quotes"], start=1
    ):
        print(f"\nREVIEW {index}")
        print("Quote:", review["customer_voice"])
        print("Product:", review["product_name"])
        print("Retailer:", review["retailer_name"])
        print("Rating:", review["customer_rating"])
        print("Sentiment:", review["sentiment"])
        print("Source:", review["data_source_type"])
        print("UUID:", review["uuid"])
