import os

import click
import duckdb
from dotenv import load_dotenv

load_dotenv()

def get_db_path() -> str:
    return os.environ.get(
        "DBT_DB_PATH",
        os.path.expanduser("~/development/capstone-data-tool/data/capstone.duckdb"),
    )

LOCAL_DATA_DIR = os.path.expanduser("~/development/capstone-data-tool/data")
CI_DATA_DIR = "tests/fixtures"
TRIPS_FILE = "yellow_tripdata_2024-01.parquet"
CI_TRIPS_FILE = "sample_trips.parquet"
ZONES_FILE = "taxi_zone_lookup.csv"


def resolve_local_source(source: str) -> tuple[str, str]:
    """Map a local/ci --source to (data_dir, trips_file)."""
    if source == "ci":
        return CI_DATA_DIR, CI_TRIPS_FILE
    return LOCAL_DATA_DIR, TRIPS_FILE


def require_azure_config() -> tuple[str, str]:
    """Read Azure config from the environment, or raise a friendly error."""
    connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    container = os.environ.get("CAPSTONE_AZURE_CONTAINER")
    missing = [
        name
        for name, value in [
            ("AZURE_STORAGE_CONNECTION_STRING", connection_string),
            ("CAPSTONE_AZURE_CONTAINER", container),
        ]
        if not value
    ]
    if missing:
        raise click.UsageError(
            "--source azure requires " + " and ".join(missing) + " to be set "
            "(in the environment or a .env file — see .env.example)."
        )
    return connection_string, container


def load_local(conn, data_dir: str, trips_file: str):
    print(f"Loading trips from {data_dir}/{trips_file}...")
    conn.execute(f"""
        CREATE OR REPLACE TABLE nyc_tlc.yellow_trips AS
        SELECT * FROM read_parquet('{data_dir}/{trips_file}')
    """)

    print(f"Loading taxi zones CSV from {data_dir}/{ZONES_FILE}...")
    conn.execute(f"""
        CREATE OR REPLACE TABLE nyc_tlc.taxi_zones AS
        SELECT * FROM read_csv_auto('{data_dir}/{ZONES_FILE}')
    """)


def load_azure(conn):
    connection_string, container = require_azure_config()

    conn.execute("INSTALL azure")
    conn.execute("LOAD azure")
    # The default transport fails TLS verification on some Linux setups (can't find the
    # system CA bundle); curl transport uses the system's own TLS stack instead.
    conn.execute("SET azure_transport_option_type='curl'")
    conn.execute(
        "CREATE OR REPLACE SECRET azure_capstone (TYPE AZURE, CONNECTION_STRING ?)",
        [connection_string],
    )

    print(f"Loading trips from azure://{container}/{TRIPS_FILE}...")
    conn.execute(f"""
        CREATE OR REPLACE TABLE nyc_tlc.yellow_trips AS
        SELECT * FROM read_parquet('azure://{container}/{TRIPS_FILE}')
    """)

    print(f"Loading taxi zones CSV from azure://{container}/{ZONES_FILE}...")
    conn.execute(f"""
        CREATE OR REPLACE TABLE nyc_tlc.taxi_zones AS
        SELECT * FROM read_csv_auto('azure://{container}/{ZONES_FILE}')
    """)


@click.command()
@click.option(
    "--source",
    type=click.Choice(["local", "azure", "ci"]),
    default="local",
    show_default=True,
    help="Where to load raw data from.",
)
def main(source: str):
    """Load raw NYC TLC trip data + zone lookup into DuckDB."""
    conn = duckdb.connect(get_db_path())
    conn.execute("CREATE SCHEMA IF NOT EXISTS nyc_tlc")

    if source == "azure":
        load_azure(conn)
    else:
        data_dir, trips_file = resolve_local_source(source)
        load_local(conn, data_dir, trips_file)

    print("Done. Row counts:")
    print(conn.execute("SELECT COUNT(*) FROM nyc_tlc.yellow_trips").fetchone())
    print(conn.execute("SELECT COUNT(*) FROM nyc_tlc.taxi_zones").fetchone())

    conn.close()


if __name__ == "__main__":
    main()
