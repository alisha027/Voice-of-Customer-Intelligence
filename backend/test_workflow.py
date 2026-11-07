from app.workflows.graph import voc_graph

print("\nLOADED GRAPH:")
print(voc_graph.get_graph().draw_mermaid())


def test_query(query):

    print("\n" + "=" * 70)
    print("USER QUESTION:", query)
    print("=" * 70)

    result = voc_graph.invoke({
        "user_query": query,
        "retry_count": 0,
        "max_retries": 2
    })

    print("\nINTENT:")
    print(result.get("intent"))

    print("\nGENERATED SQL:")
    print(result.get("sql_query"))

    print("\nSQL ANALYSIS RESULTS:")
    for row in result.get("query_results", []):
        print(row)

    print("\nCUSTOMER VERBATIMS:")
    for quote in result.get("customer_quotes", []):
        print("\nQuote:", quote.get("customer_voice"))
        print("Retailer:", quote.get("retailer_name"))
        print("Rating:", quote.get("customer_rating"))
        print("Source:", quote.get("data_source_type"))

    print("\nSOURCE DISTRIBUTION:")
    for source in result.get("source_distribution", []):
        print(source)

    print("\nAGENT ERRORS:")
    print("SQL:", result.get("sql_error"))
    print("Verbatim:", result.get("verbatim_error"))
    print("Source:", result.get("source_error"))

    print("\nFINAL RESPONSE:")
    print(result.get("final_answer"))


if __name__ == "__main__":

    test_query(
        "Why are customers complaining about Microsoft Surface battery life?"
    )
