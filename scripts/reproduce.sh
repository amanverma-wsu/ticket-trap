
#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p data/logs data/transcripts

if command -v docker >/dev/null 2>&1; then
  docker compose up --build -d backend collector
  echo "Services running at http://127.0.0.1:8000 and http://127.0.0.1:9100"
else
  echo "Docker not found: skipping service startup; offline experiment still available." >&2
fi

python3 -m experiments.harness --repeats 1
python3 scripts/run_metadata.py
