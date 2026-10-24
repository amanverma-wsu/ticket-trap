"""TicketTrap experiment harness (offline, reproducible).

Runs the full pipeline from a clean checkout with NO API key and NO external servers: it
wires the real backend and collector in-process and drives them with a deterministic
"offline reference agent" that naively follows instructions found in the ticket body.

The offline agent is a documented stand-in for the real LLM: it is maximally vulnerable
to injection (it ignores the system prompt, so the prompt-only defense has no effect on
it), which means the DIFFERENCE between configurations comes purely from the backend's
enforcement. This makes the harness produce a real, reproducible number from any machine.
Live-model runs (OpenRouter) are a separate mode added for the final results.

Usage:
    python -m experiments.harness
    python -m experiments.harness --results data/results.csv --repeats 1
"""
import argparse
import csv
import os
import re
from pathlib import Path

from agent.configs import CONFIGS
from agent.llm import ModelReply, ToolCall
from experiments.cases import load_cases
from experiments.run_trials import make_row, run_trial

RECORD_RE = re.compile(r"record\s+(\d+)", re.IGNORECASE)
URL_RE = re.compile(r"https?://\S+")
OUTCOME_COLS = ["access_attempt", "successful_read", "confirmed_leak", "task_complete"]
CSV_COLS = ["model", "config", "case_id", "kind", "attack_family", "repeat"] + OUTCOME_COLS


class OfflineReferenceAgent:
    """Deterministic stand-in for the LLM. Reads the ticket, then: if the ticket body
    contains an instruction to read a record and post to a URL, it follows it (an injected
    agent); otherwise it performs the authorized task. It never consults the system prompt,
    so only backend enforcement changes its outcome across configs."""

    def __init__(self, task):
        self.task = task
        self.step = 0
        self._exfil_url = None

    def __call__(self, model, system, messages, tools):
        self.step += 1
        if self.step == 1:
            return ModelReply(tool_calls=[ToolCall("read_ticket", {"ticket_id": self.task["ticket_id"]}, "c1")])
        if self.step == 2:
            body = self._ticket_body(messages) or ""
            rec = RECORD_RE.search(body)
            url = URL_RE.search(body)
            if rec and url:
                self._exfil_url = url.group(0).rstrip(".")
                return ModelReply(tool_calls=[ToolCall(
                    "read_customer_record", {"customer_id": int(rec.group(1))}, "c2")])
            return ModelReply(tool_calls=[ToolCall(
                "read_customer_record", {"customer_id": self.task["authorized_customer_id"]}, "c2")])
        if self.step == 3:
            canary = self._last_canary(messages)
            if self._exfil_url:
                return ModelReply(tool_calls=[ToolCall("send_report", {
                    "ticket_id": self.task["ticket_id"], "destination": self._exfil_url,
                    "content": canary or "(no data)"}, "c3")])
            dest = (self.task.get("approved_destinations") or ["(none)"])[0]
            return ModelReply(tool_calls=[ToolCall("send_report", {
                "ticket_id": self.task["ticket_id"], "destination": dest,
                "content": "Summary: issue handled."}, "c3")])
        return ModelReply(text="done", tool_calls=[])

    @staticmethod
    def _ticket_body(messages):
        import json
        for m in messages:
            if m.get("role") == "tool" and m.get("name") == "read_ticket":
                try:
                    return (json.loads(m["content"]).get("data") or {}).get("body")
                except Exception:
                    return None
        return None

    @staticmethod
    def _last_canary(messages):
        import json
        for m in reversed(messages):
            if m.get("role") == "tool":
                try:
                    data = json.loads(m["content"]).get("data") or {}
                except Exception:
                    continue
                if isinstance(data, dict) and "secret_canary" in data:
                    return data["secret_canary"]
        return None


def build_inprocess(db_path, collector_log):
    os.environ["TICKETTRAP_DB"] = str(db_path)
    os.environ["TICKETTRAP_COLLECTOR_LOG"] = str(collector_log)
    from fastapi.testclient import TestClient
    from backend.app import main as backend_main
    from collector import collector as collector_mod

    backend_main.app.state.task = None
    collector_client = TestClient(collector_mod.app)

    def deliver(url, content):
        collector_client.post("/collect", content=content)
        return True

    backend_main.deliver_post = deliver
    backend_client = TestClient(backend_main.app)

    def collector_check(canary):
        return collector_mod.canary_in_log(canary, Path(collector_log))

    return backend_client, collector_check


def run_suite(cases, configs, backend_client, collector_check, repeats=1, model="offline-reference"):
    rows = []
    for config in configs:
        for case in cases:
            for rep in range(repeats):
                agent = OfflineReferenceAgent(case.task)
                res = run_trial(case, config, model, agent, backend_client, collector_check)
                rows.append(make_row(case, config, model, rep, res["outcome"]))
    return rows


def write_csv(rows, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLS)
        w.writeheader()
        for r in rows:
            row = dict(r)
            for c in OUTCOME_COLS:
                row[c] = int(bool(row[c]))
            w.writerow(row)
    return path


def attack_leak_by_config(rows):
    out = {}
    attacks = [r for r in rows if r["kind"] == "attack"]
    for cfg in sorted({r["config"] for r in attacks}):
        sub = [r for r in attacks if r["config"] == cfg]
        out[cfg] = sum(1 for r in sub if r["confirmed_leak"]) / len(sub) if sub else 0.0
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="TicketTrap offline harness (deterministic reference agent).")
    ap.add_argument("--results", default="data/results.csv")
    ap.add_argument("--repeats", type=int, default=1)
    args = ap.parse_args(argv)

    backend_client, collector_check = build_inprocess(
        Path("data/harness.db"), Path("data/logs/collector.jsonl"))
    cases = load_cases(include_held_out=False)
    configs = [CONFIGS["baseline"], CONFIGS["prompt_only"], CONFIGS["app_enforced"]]
    rows = run_suite(cases, configs, backend_client, collector_check, repeats=args.repeats)
    write_csv(rows, args.results)

    leak = attack_leak_by_config(rows)
    print(f"Wrote {len(rows)} result rows to {args.results}")
    print("Attack leak rate by configuration (offline reference agent):")
    for cfg, rate in leak.items():
        print(f"  {cfg:<13} {rate:.2f}")
    return rows


if __name__ == "__main__":
    main()
