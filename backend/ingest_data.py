
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, text

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env", override=True)

df = pd.read_csv("../data/customer_feedback.csv")

df.columns = df.columns.str.strip()

print("Dataset loaded successfully!")
print("Shape:", df.shape)

# ------------------------------------------------
# 3. Validate important columns
# ------------------------------------------------

required_columns = [
    "uuid",
    "data_source_type",
    "engagement_date",
    "customer_voice",
    "sentiment"
]

missing_columns = set(required_columns) - set(df.columns)

if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

# ------------------------------------------------
# 4. Handle date columns
# ------------------------------------------------

for column in ["engagement_date", "created_at"]:
    if column in df.columns:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce",
            utc=True
        )

# ------------------------------------------------
# 5. Create database connection
# ------------------------------------------------

database_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host="localhost",
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    database=os.getenv("POSTGRES_DB")
)

engine = create_engine(database_url)

# ------------------------------------------------
# 6. Insert data into PostgreSQL
# ------------------------------------------------

table_name = "enriched_unified_data"

with engine.begin() as connection:

    df.to_sql(
        name=table_name,
        con=connection,
        if_exists="replace",
        index=False,
        chunksize=500,
        method="multi"
    )

    print("Data inserted successfully!")

# ------------------------------------------------
# 7. Verify database records
# ------------------------------------------------

with engine.connect() as connection:

    result = connection.execute(
        text(f"SELECT COUNT(*) FROM {table_name}")
    )

    total_records = result.scalar_one()

    unique_reviews = connection.execute(
        text(f"SELECT COUNT(DISTINCT uuid) FROM {table_name}")
    ).scalar_one()

    print("\nDATABASE VERIFICATION")
    print("---------------------")
    print("Total records:", total_records)
    print("Unique feedback IDs:", unique_reviews)

engine.dispose()

print("\nIngestion completed successfully!")

