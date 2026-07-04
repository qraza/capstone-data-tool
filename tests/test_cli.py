import os

import duckdb
import pytest
from click.testing import CliRunner

# Point the CLI at the CI test database before importing it
TEST_DB = os.path.join(os.path.dirname(__file__), "..", "data", "ci_test.duckdb")
os.environ.setdefault("DBT_DB_PATH", os.path.abspath(TEST_DB))

from cli.main import cli  # noqa: E402


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


def test_summary_returns_table(runner):
    """summary should render a table for a date present in the sample data."""
    result = runner.invoke(cli, ["summary", "--date", "2024-01-15", "--top", "3"])
    assert result.exit_code == 0
    assert "NYC Taxi Summary" in result.output


def test_summary_no_data_message(runner):
    """summary should handle dates with no data gracefully."""
    result = runner.invoke(cli, ["summary", "--date", "1999-01-01"])
    assert result.exit_code == 0
    assert "No data found" in result.output


def test_summary_rejects_bad_order_by(runner):
    """click should reject invalid --order-by choices."""
    result = runner.invoke(cli, ["summary", "--order-by", "not_a_column"])
    assert result.exit_code != 0


def test_mart_table_exists():
    """the mart table should exist and have rows."""
    conn = duckdb.connect(os.environ["DBT_DB_PATH"], read_only=True)
    count = conn.execute("SELECT COUNT(*) FROM main.mart_trip_summary").fetchone()[0]
    conn.close()
    assert count > 0
