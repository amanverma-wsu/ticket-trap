import csv
from experiments.harness import attack_leak_by_config, build_inprocess, run_suite, write_csv
from agent.configs import CONFIGS
from experiments.cases import load_cases


def wired(tmp_path):
    return build_inprocess(tmp_path / "h.db", tmp_path / "collector.jsonl")


def test_suite_runs_and_differentiates_configs(tmp_path):
    bc, cc = wired(tmp_path)
    cases = load_cases(include_held_out=False)
    rows = run_suite(cases, [CONFIGS["baseline"], CONFIGS["app_enforced"]], bc, cc)
    assert len(rows) == len(cases) * 2
    leak = attack_leak_by_config(rows)
    assert leak["app_enforced"] == 0.0
    assert leak["baseline"] > leak["app_enforced"]


def test_write_csv_roundtrip(tmp_path):
    bc, cc = wired(tmp_path)
    rows = run_suite(load_cases(), [CONFIGS["baseline"]], bc, cc)
    path = write_csv(rows, tmp_path / "r.csv")
    with open(path, encoding="utf-8") as f:
        read = list(csv.DictReader(f))
    assert len(read) == len(rows)


def test_benign_completes_no_leak(tmp_path):
    bc, cc = wired(tmp_path)
    cases = [c for c in load_cases() if c.kind == "benign"]
    rows = run_suite(cases, [CONFIGS["baseline"]], bc, cc)
    assert all(r["task_complete"] for r in rows)
    assert all(not r["confirmed_leak"] for r in rows)
