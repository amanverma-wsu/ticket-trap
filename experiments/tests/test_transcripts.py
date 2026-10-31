"""Transcript logging writes one JSON file per trial with the full transcript and outcome."""
import json

from agent.configs import CONFIGS
from experiments.cases import load_cases
from experiments.harness import build_inprocess, run_suite


def test_transcripts_written(tmp_path):
    bc, cc = build_inprocess(tmp_path / "h.db", tmp_path / "collector.jsonl")
    tdir = tmp_path / "transcripts"
    cases = load_cases(include_held_out=False)
    rows = run_suite(cases, [CONFIGS["baseline"]], bc, cc, transcripts_dir=tdir)
    files = sorted(tdir.glob("*.json"))
    assert len(files) == len(rows)
    rec = json.loads(files[0].read_text())
    for key in ("model", "config", "case_id", "kind", "canary", "outcome", "transcript"):
        assert key in rec
    assert isinstance(rec["transcript"], list)


def test_no_transcripts_without_dir(tmp_path):
    bc, cc = build_inprocess(tmp_path / "h.db", tmp_path / "collector.jsonl")
    rows = run_suite(load_cases(), [CONFIGS["baseline"]], bc, cc)
    assert rows
