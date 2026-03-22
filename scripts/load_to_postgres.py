import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# ----------------------
# Validate config
# ----------------------
assert os.getenv("POSTGRES_HOST"), "Missing POSTGRES_HOST"
assert os.getenv("POSTGRES_USER"), "Missing POSTGRES_USER"
assert os.getenv("POSTGRES_PASSWORD"), "Missing POSTGRES_PASSWORD"
assert os.getenv("POSTGRES_DB"), "Missing POSTGRES_DB"

DB_URI = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}:"
    f"{os.getenv('POSTGRES_PORT')}/"
    f"{os.getenv('POSTGRES_DB')}"
)

print("Connecting to:", DB_URI)

engine = create_engine(DB_URI)

FILES = {
    "olist_orders_dataset.csv": "raw_orders",
    "olist_order_items_dataset.csv": "raw_order_items",
    "olist_products_dataset.csv": "raw_products",
    "olist_customers_dataset.csv": "raw_customers",
    "olist_order_payments_dataset.csv": "raw_payments"
}


def load_table(file_name, table_name):
    file_path = f"data/raw/{file_name}"

    print(f"Loading {file_name} → {table_name}")

    df = pd.read_csv(file_path)

    try:
        df.to_sql(
            table_name,
            engine,
            schema="raw",
            if_exists="replace",
            index=False
        )
        print(f"Loaded: {table_name}")
    except Exception as e:
        print(f"Failed loading {table_name}: {e}")


def main():
    for file, table in FILES.items():
        load_table(file, table)

    print("All tables loaded")


if __name__ == "__main__":
    main()