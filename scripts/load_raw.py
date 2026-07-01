import duckdb
import os

DB_PATH = os.environ.get(
    "DBT_DB_PATH",
    os.path.expanduser("~/development/capstone-data-tool/data/capstone.duckdb")
)

DATA_DIR = os.path.expanduser("~/development/capstone-data-tool/data")

def load_raw():
    conn = duckdb.connect(DB_PATH)

    conn.execute("CREATE SCHEMA IF NOT EXISTS nyc_tlc")

    print("Loading yellow trips parquet...")
    conn.execute(f"""
        CREATE OR REPLACE TABLE nyc_tlc.yellow_trips AS
        SELECT * FROM read_parquet('{DATA_DIR}/yellow_tripdata_2024-01.parquet')
    """)

    print("Loading taxi zones CSV...")
    conn.execute(f"""
        CREATE OR REPLACE TABLE nyc_tlc.taxi_zones AS
        SELECT * FROM read_csv_auto('{DATA_DIR}/taxi_zone_lookup.csv')
    """)

    print("Done. Row counts:")
    print(conn.execute("SELECT COUNT(*) FROM nyc_tlc.yellow_trips").fetchone())
    print(conn.execute("SELECT COUNT(*) FROM nyc_tlc.taxi_zones").fetchone())

    conn.close()

if __name__ == "__main__":
    load_raw()
