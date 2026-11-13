
"""Record reproducibility context without logging API keys or secrets."""

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_commit():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def main():
    files = [
        "requirements.txt",
        "backend/requirements.txt",
        "collector/requirements.txt",
        "docker-compose.yml",
    ]

    cases = sorted((ROOT / "cases").rglob("*.json"))
    result = ROOT / "data/results.csv"

    metadata = {
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "git_commit": git_commit(),
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "mode": "offline-reference (default)",
        "repeats": 1,
        "case_count": len(cases),
        "case_sha256": {
            str(x.relative_to(ROOT)): sha256(x)
            for x in cases
        },
        "input_sha256": {
            f: sha256(ROOT / f)
            for f in files
        },
        "results_sha256": (
            sha256(result) if result.exists() else None
        ),
        "note": (
            "Metadata describes default offline run. "
            "Live evaluation must record actual models, "
            "temperature and API responses separately."
        ),
    }

    dest = ROOT / "data/run_metadata.json"
    dest.parent.mkdir(exist_ok=True)

    dest.write_text(
        json.dumps(metadata, indent=2) + "\n"
    )

    print(f"Wrote {dest}")


if __name__ == "__main__":
    main()
