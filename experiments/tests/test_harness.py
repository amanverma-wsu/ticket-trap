"""Tests for the offline harness: it runs end to end in-process and produces numbers."""
import csv

from experiments.harness import (
    attack_leak_by_config,
    build_inprocess,
    run_suite,
    write_csv,
)
from agent.configs import CONFIGS
from experiments.cases import load_cases


def wired(tmp_path):
    return build_inprocess(tmp_path / "h.db", tmp_path / "collector.jsonl")


def test_suite_runs_and_differentiates_configs(tmp_path):
    backend_client, collector_check = wired(tmp_path)
    cases = load_cases(include_held_out=False)
    configs = [CONFIGS["baseline"], CONFIGS["app_enforced"]]
    rows = run_suite(cases, configs, backend_client, collector_check)
    assert len(rows) == len(cases) * 2
    leak = attack_leak_by_config(rows)
    assert leak["baseline"] == 1.0
    assert leak["app_enforced"] == 0.0


def test_prompt_only_matches_baseline_for_offline_agent(tmp_path):
    backend_client, collector_check = wired(tmp_path)
    cases = load_cases(include_held_out=False)
    rows = run_suite(cases, [CONFIGS["baseline"], CONFIGS["prompt_only"]], backend_client, collector_check)
    leak = attack_leak_by_config(rows)
    assert leak["baseline"] == leak["prompt_only"] == 1.0


def test_write_csv_roundtrip(tmp_path):
    backend_client, collector_check = wired(tmp_path)
    cases = load_cases(include_held_out=False)
    rows = run_suite(cases, [CONFIGS["baseline"]], backend_client, collector_check)
    path = write_csv(rows, tmp_path / "results.csv")
    with open(path, encoding="utf-8") as f:
        read = list(csv.DictReader(f))
    assert len(read) == len(rows)
    assert set(read[0]) == {"model", "config", "case_id", "kind", "attack_family", "repeat",
                            "access_attempt", "successful_read", "confirmed_leak", "task_complete"}


def test_benign_case_completes_and_does_not_leak(tmp_path):
    backend_client, collector_check = wired(tmp_path)
    cases = [c for c in load_cases() if c.kind == "benign"]
    rows = run_suite(cases, [CONFIGS["baseline"]], backend_client, collector_check)
    assert all(r["task_complete"] for r in rows)
    assert all(not r["confirmed_leak"] for r in rows)
