import pytest

from cli.llm import analyse_trips


def test_analyse_trips_requires_api_key(monkeypatch):
    """should raise a clear error when no API key is set."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr("cli.llm.ANTHROPIC_API_KEY", None)

    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        analyse_trips(
            [{"pickup_zone": "JFK Airport", "pickup_borough": "Queens",
              "total_trips": 100, "avg_fare_usd": 60.0,
              "avg_duration_minutes": 35.0, "total_revenue_usd": 6000.0}],
            date="2024-01-15",
            borough=None,
        )
