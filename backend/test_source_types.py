
from app.services.sql_executor import execute_readonly_query

query = """
SELECT
    data_source_type,
    customer_voice
FROM enriched_unified_data
WHERE maintheme = 'Battery & Power Management'
  AND sentiment = 'Negative'
LIMIT 15;
"""

results = execute_readonly_query(query)

print("\nDATA SOURCE BREAKDOWN")
print("=" * 60)

for row in results:
    print(row)
