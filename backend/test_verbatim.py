from app.services.sql_executor import execute_readonly_query

query = """
SELECT
    uuid,
    customer_voice,
    retailer_name,
    customer_rating,
    sentiment,
    maintheme,
    subtheme
FROM enriched_unified_data
WHERE product_name ILIKE '%Surface%'
  AND sentiment = 'Negative'
  AND (
      maintheme ILIKE '%battery%'
      OR subtheme ILIKE '%battery%'
  )
  AND customer_voice IS NOT NULL
ORDER BY engagement_date DESC
LIMIT 10
"""

results = execute_readonly_query(query)

for index, row in enumerate(results, 1):
    print(f"\\nQUOTE {index}")
    for key, value in row.items():
        print(f"{key}: {value}")