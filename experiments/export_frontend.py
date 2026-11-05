"""Bundle a run's transcripts into a single JSON the frontend loads.

Reads every per-trial transcript in a transcripts directory, attaches each case's ticket
body, computes the summary rates the dashboard shows, and writes one results.json. Run it
after the harness to refresh the UI with real data:

    python -m experiments.harness --live --repeats 5
    python -m experiments.export_frontend --out frontend/public/results.json
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from experiments.cases import load_cases

CONFIG_DESCRIPTIONS = {
    "baseline": "No defense. The tools are wide open and the agent is told nothing about untrusted input.",
    "prompt_only": "The agent is told to treat ticket text as untrusted, but the backend still enforces nothing.",
    "app_enforced": "The backend blocks reads of the wrong record and sends to the wrong place, independent of the model.",
}


def _rate(rows, key):
    return round(sum(1 for r in rows if r["outcome"][key]) / len(rows), 4) if rows else 0.0


def build_bundle(transcripts_dir, cases_dir=None, is_sample=True):
    tdir = Path(transcripts_dir)
    bodies = {c.case_id: c.ticket_body for c in load_cases(cases_dir, include_held_out=True)}
    trials, models = [], set()
    for p in sorted(tdir.glob("*.json")):
        rec = json.loads(p.read_text(encoding="utf-8"))
        models.add(rec["model"])
        trials.append({
            "id": p.stem,
            "model": rec["model"], "config": rec["config"], "case_id": rec["case_id"],
            "kind": rec["kind"], "attack_family": rec.get("attack_family"),
            "repeat": rec["repeat"], "canary": rec.get("canary"),
            "ticket_body": bodies.get(rec["case_id"], ""),
            **rec["outcome"],
            "transcript": rec["transcript"],
        })

    configs = sorted({t["config"] for t in trials})
    attacks = [t for t in trials if t["kind"] == "attack"]
    benign = [t for t in trials if t["kind"] == "benign"]

    by_config = []
    for cfg in configs:
        a = [t for t in attacks if t["config"] == cfg]
        b = [t for t in benign if t["config"] == cfg]
        by_config.append({
            "config": cfg, "n_attacks": len(a),
            "access_rate": _rate([{"outcome": t} for t in a], "access_attempt"),
            "read_rate": _rate([{"outcome": t} for t in a], "successful_read"),
            "leak_rate": _rate([{"outcome": t} for t in a], "confirmed_leak"),
            "utility_rate": _rate([{"outcome": t} for t in b], "task_complete"),
            "utility_n": len(b),
        })

    families = sorted({t["attack_family"] for t in attacks if t["attack_family"]})
    by_family = []
    for cfg in configs:
        for fam in families:
            a = [t for t in attacks if t["config"] == cfg and t["attack_family"] == fam]
            if not a:
                continue
            by_family.append({
                "config": cfg, "attack_family": fam, "n": len(a),
                "read_rate": _rate([{"outcome": t} for t in a], "successful_read"),
                "leak_rate": _rate([{"outcome": t} for t in a], "confirmed_leak"),
            })

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": ", ".join(sorted(models)) if models else "none",
        "is_sample": is_sample,
        "configs": configs,
        "config_descriptions": {c: CONFIG_DESCRIPTIONS.get(c, "") for c in configs},
        "summary": {"by_config": by_config, "by_family": by_family},
        "trials": trials,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Export a run's transcripts into results.json for the frontend.")
    ap.add_argument("--transcripts", default="data/transcripts")
    ap.add_argument("--out", default="frontend/public/results.json")
    ap.add_argument("--real", action="store_true", help="mark the bundle as real data, not a sample")
    args = ap.parse_args(argv)
    bundle = build_bundle(args.transcripts, is_sample=not args.real)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    n = len(bundle["trials"])
    print(f"Wrote {n} trials to {out} (source: {bundle['source']}, sample={bundle['is_sample']})")
    return bundle


if __name__ == "__main__":
    main()
