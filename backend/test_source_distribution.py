
from app.agents.source_distribution_agent import source_distribution_agent

test_state = {
    "user_query": (
        "Why are customers complaining about "
        "Microsoft Surface battery life?"
    )
}

result = source_distribution_agent(test_state)

print("\n" + "=" * 55)
print("SOURCE DISTRIBUTION RESULTS")
print("=" * 55)

if result.get("source_error"):
    print("Error:", result["source_error"])
else:
    for item in result["source_distribution"]:
        print(
            f"{item['source']}: "
            f"{item['unique_interactions']} interactions "
            f"({item['percentage']}%)"
        )
