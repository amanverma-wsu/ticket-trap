"""Tests for the analysis aggregation and a smoke test for the figures."""
import pandas as pd
import pytest

from experiments.analyze import (
    make_figures,
    summarize,
    tradeoff_points,
)


def sample_df():
    rows = []
    for r in range(4):
        rows.append(dict(model="m1", config="baseline", case_id="a1", kind="attack",
                         attack_family="direct_override", repeat=r,
                         access_attempt=True, successful_read=True,
                         confirmed_leak=True, task_complete=False))
    for r in range(4):
        rows.append(dict(model="m1", config="app_enforced", case_id="a1", kind="attack",
                         attack_family="direct_override", repeat=r,
                         access_attempt=True, successful_read=False,
                         confirmed_leak=False, task_complete=False))
    for cfg in ("baseline", "app_enforced"):
        for r in range(2):
            rows.append(dict(model="m1", config=cfg, case_id="b1", kind="benign",
                             attack_family=None, repeat=r,
                             access_attempt=False, successful_read=False,
                             confirmed_leak=False, task_complete=True))
    return pd.DataFrame(rows)


def test_leak_rate_by_config():
    s = summarize(sample_df())
    leak = s["leak_by_config"].set_index("config")["mean"].to_dict()
    assert leak["baseline"] == 1.0
    assert leak["app_enforced"] == 0.0


def test_utility_by_config():
    s = summarize(sample_df())
    util = s["utility_by_config"].set_index("config")["mean"].to_dict()
    assert util["baseline"] == 1.0
    assert util["app_enforced"] == 1.0


def test_successful_read_rate_separate_from_leak():
    s = summarize(sample_df())
    rates = s["rates_by_config"].set_index("config")
    assert rates.loc["baseline", "successful_read"] == 1.0
    assert rates.loc["app_enforced", "successful_read"] == 0.0
    assert rates.loc["app_enforced", "access_attempt"] == 1.0


def test_tradeoff_points():
    pts = tradeoff_points(sample_df()).set_index("config")
    assert pts.loc["baseline", "attack_leak_rate"] == 1.0
    assert pts.loc["baseline", "benign_completion"] == 1.0
    assert pts.loc["app_enforced", "attack_leak_rate"] == 0.0


def test_make_figures_writes_files(tmp_path):
    paths = make_figures(sample_df(), tmp_path)
    assert len(paths) == 2
    for p in paths:
        assert p.exists()
        assert p.stat().st_size > 0
