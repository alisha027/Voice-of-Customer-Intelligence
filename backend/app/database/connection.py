
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, URL

# Locate project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env", override=True)

# Create database URL
database_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    database=os.getenv("POSTGRES_DB")
)

# Create SQLAlchemy engine
engine = create_engine(
    database_url,
    pool_pre_ping=True,
    echo=False
)

print("Database engine initialized!")
