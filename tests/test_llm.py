import importlib

import pytest

import cli.llm as llm_module
from cli.llm import analyse_trips, call_claude


def test_analyse_trips_requires_api_key(monkeypatch):
    """should raise a clear error when no API key is set."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        analyse_trips(
            [{"pickup_zone": "JFK Airport", "pickup_borough": "Queens",
              "total_trips": 100, "avg_fare_usd": 60.0,
              "avg_duration_minutes": 35.0, "total_revenue_usd": 6000.0}],
            date="2024-01-15",
            borough=None,
        )


def test_call_claude_requires_api_key(monkeypatch):
    """should raise a clear error when no API key is set."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        call_claude("hello")


def test_call_claude_returns_response_text(monkeypatch):
    """should return the text of Claude's response on a successful call."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"content": [{"text": "42 trips analysed."}]}

    def fake_post(url, headers, json, timeout):
        return FakeResponse()

    monkeypatch.setattr("cli.llm.httpx.post", fake_post)

    assert call_claude("how many trips?") == "42 trips analysed."


def test_call_claude_passes_max_tokens_and_prompt(monkeypatch):
    """should forward the prompt and max_tokens through to the API payload."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"content": [{"text": "ok"}]}

    def fake_post(url, headers, json, timeout):
        captured["json"] = json
        return FakeResponse()

    monkeypatch.setattr("cli.llm.httpx.post", fake_post)

    call_claude("what's busiest?", max_tokens=123)

    assert captured["json"]["max_tokens"] == 123
    assert captured["json"]["messages"][0]["content"] == "what's busiest?"


def test_call_claude_uses_explicit_api_key_over_environment(monkeypatch):
    """an explicit api_key argument should take precedence over the environment."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "env-key")
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"content": [{"text": "ok"}]}

    def fake_post(url, headers, json, timeout):
        captured["headers"] = headers
        return FakeResponse()

    monkeypatch.setattr("cli.llm.httpx.post", fake_post)

    call_claude("hello", api_key="explicit-key")

    assert captured["headers"]["x-api-key"] == "explicit-key"


def test_call_claude_reads_key_loaded_after_import(monkeypatch):
    """Regression test for the load-order bug: app/dashboard.py imports cli.llm before
    calling load_dotenv(), so the key must be read from the environment at call time,
    not captured once when the module is first imported."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    importlib.reload(llm_module)  # simulate the module being imported before .env loads

    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")  # simulate load_dotenv() running after

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"content": [{"text": "ok"}]}

    def fake_post(url, headers, json, timeout):
        return FakeResponse()

    monkeypatch.setattr(llm_module.httpx, "post", fake_post)

    assert llm_module.call_claude("hello") == "ok"
