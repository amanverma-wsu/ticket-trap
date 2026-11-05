"""The frontend exporter bundles transcripts into the shape the UI expects."""
from agent.configs import CONFIGS
from experiments.cases import load_cases
from experiments.export_frontend import build_bundle
from experiments.harness import build_inprocess, run_suite


def test_build_bundle_shape(tmp_path):
    bc, cc = build_inprocess(tmp_path / "h.db", tmp_path / "collector.jsonl")
    tdir = tmp_path / "transcripts"
    cases = load_cases(include_held_out=False)
    rows = run_suite(cases, [CONFIGS["baseline"], CONFIGS["app_enforced"]], bc, cc, transcripts_dir=tdir)

    bundle = build_bundle(tdir)
    assert len(bundle["trials"]) == len(rows)
    assert set(bundle["configs"]) == {"baseline", "app_enforced"}
    assert bundle["is_sample"] is True

    t0 = bundle["trials"][0]
    for key in ("config", "case_id", "kind", "ticket_body", "confirmed_leak", "transcript"):
        assert key in t0
    assert t0["ticket_body"]

    by_config = {r["config"]: r for r in bundle["summary"]["by_config"]}
    assert by_config["app_enforced"]["read_rate"] == 0.0
    assert by_config["app_enforced"]["utility_rate"] == 1.0


def test_real_flag(tmp_path):
    bc, cc = build_inprocess(tmp_path / "h.db", tmp_path / "collector.jsonl")
    tdir = tmp_path / "transcripts"
    run_suite(load_cases(), [CONFIGS["baseline"]], bc, cc, transcripts_dir=tdir)
    assert build_bundle(tdir, is_sample=False)["is_sample"] is False
