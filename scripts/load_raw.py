import duckdb
import os
import sys

DB_PATH = os.environ.get(
    "DBT_DB_PATH",
    os.path.expanduser("~/development/capstone-data-tool/data/capstone.duckdb")
)

def load_raw(data_dir: str, trips_file: str):
    conn = duckdb.connect(DB_PATH)

    conn.execute("CREATE SCHEMA IF NOT EXISTS nyc_tlc")

    print(f"Loading trips from {data_dir}/{trips_file}...")
    conn.execute(f"""
        CREATE OR REPLACE TABLE nyc_tlc.yellow_trips AS
        SELECT * FROM read_parquet('{data_dir}/{trips_file}')
    """)

    print("Loading taxi zones CSV...")
    conn.execute(f"""
        CREATE OR REPLACE TABLE nyc_tlc.taxi_zones AS
        SELECT * FROM read_csv_auto('{data_dir}/taxi_zone_lookup.csv')
    """)

    print("Done. Row counts:")
    print(conn.execute("SELECT COUNT(*) FROM nyc_tlc.yellow_trips").fetchone())
    print(conn.execute("SELECT COUNT(*) FROM nyc_tlc.taxi_zones").fetchone())

    conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--ci":
        load_raw("tests/fixtures", "sample_trips.parquet")
    else:
        data_dir = os.path.expanduser("~/development/capstone-data-tool/data")
        load_raw(data_dir, "yellow_tripdata_2024-01.parquet")
