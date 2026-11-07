
from sqlalchemy import inspect
from app.database.connection import engine

inspector = inspect(engine)

table_name = "enriched_unified_data"

print(f"\nTABLE: {table_name}")
print("-" * 60)

columns = inspector.get_columns(table_name)

for column in columns:
    print(
        f"Column: {column['name']:<30} "
        f"Type: {column['type']}"
    )

print("\nAVAILABLE TABLES:")
print(inspector.get_table_names())
