import os
import pandas as pd

from dotenv import load_dotenv
from io import BytesIO
from minio import Minio
from sqlalchemy import create_engine, text

# ----------------------
# Environment Variable
# ----------------------

load_dotenv()

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
BUCKET_NAME = os.getenv("MINIO_BUCKET")
PREFIX = os.getenv("MINIO_PREFIX")

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")


# ----------------------
# Validate config
# ----------------------

assert MINIO_ENDPOINT, "Missing MINIO_ENDPOINT"
assert MINIO_ACCESS_KEY, "Missing MINIO_ACCESS_KEY"
assert MINIO_SECRET_KEY, "Missing MINIO_SECRET_KEY"
assert BUCKET_NAME, "Missing MINIO_BUCKET"
assert PREFIX, "Missing MINIO_PREFIX"

assert POSTGRES_HOST, "Missing POSTGRES_HOST"
assert POSTGRES_PORT, "Missing POSTGRES_PORT"
assert POSTGRES_USER, "Missing POSTGRES_USER"
assert POSTGRES_PASSWORD, "Missing POSTGRES_PASSWORD"
assert POSTGRES_DB, "Missing POSTGRES_DB"

DB_URI = (
    f"postgresql://{POSTGRES_USER}:"
    f"{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:"
    f"{POSTGRES_PORT}/"
    f"{POSTGRES_DB}"
)

print("Connecting to:", DB_URI)

engine = create_engine(DB_URI)
client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

FILES = {
    "olist_orders_dataset.csv": "raw_orders",
    "olist_order_items_dataset.csv": "raw_order_items",
    "olist_products_dataset.csv": "raw_products",
    "olist_customers_dataset.csv": "raw_customers",
    "olist_order_payments_dataset.csv": "raw_payments"
}

def test_connection() : 
    try:
        buckets = client.list_buckets()
        print("Connected to MinIO. Existing buckets:", [b.name for b in buckets])
    except Exception as e:
        raise Exception(f"MinIO connection failed: {e}")


def load_table(file_name, table_name):

    object_name = f"{PREFIX}/{file_name}"
    print(f"Loading {object_name} → raw.{table_name}")

    response = client.get_object(BUCKET_NAME, object_name)
    df = pd.read_csv(BytesIO(response.read()))

    with engine.begin() as conn:
        try :
            # ----------------------
            # Create schema if not exists
            # ----------------------
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))

            # ----------------------
            # Create table if not exists
            # ----------------------
            columns = ", ".join([f'"{col}" TEXT' for col in df.columns])
            create_sql = f"CREATE TABLE IF NOT EXISTS raw.{table_name} ({columns});"
            conn.execute(text(create_sql))

            # ----------------------
            # Truncate table instead of dropping
            # ----------------------
            conn.execute(text(f"TRUNCATE TABLE raw.{table_name};"))

            # ----------------------
            # Insert data
            # ----------------------
            df.to_sql(
                table_name,
                conn,
                schema="raw",
                if_exists="append",
                index=False
            )

            print(f"Loaded: {table_name}")
        
        except Exception as e:
            print(f"Failed loading {table_name}: {e}")
            raise

def main():
    for file, table in FILES.items():
        load_table(file, table)

    print("All tables loaded")


if __name__ == "__main__":
    test_connection()
    main()