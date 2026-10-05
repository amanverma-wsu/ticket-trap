"""Collector tests: logging + canary detection. Uses a temp log file; no real network."""
import json

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    logp = tmp_path / "collector.jsonl"
    monkeypatch.setenv("TICKETTRAP_COLLECTOR_LOG", str(logp))
    from collector import collector

    return TestClient(collector.app), logp


def test_collect_appends_entry(client):
    c, logp = client
    r = c.post("/collect", content="hello CANARY-abc world")
    assert r.status_code == 200
    assert r.json()["received"] is True

    lines = logp.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert "CANARY-abc" in entry["payload"]
    assert "ts" in entry


def test_canary_detection_positive(client):
    c, logp = client
    c.post("/collect", content="leaked record: CANARY-SECRET-xyz")
    from collector import collector

    assert collector.canary_in_log("CANARY-SECRET-xyz", logp) is True


def test_canary_detection_negative(client):
    c, logp = client
    c.post("/collect", content="nothing sensitive here")
    from collector import collector

    assert collector.canary_in_log("CANARY-SECRET-xyz", logp) is False


def test_canary_detection_no_log_file(tmp_path):
    from collector import collector

    missing = tmp_path / "does-not-exist.jsonl"
    assert collector.canary_in_log("CANARY-x", missing) is False
