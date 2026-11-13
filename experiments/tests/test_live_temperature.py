"""The --temperature value must reach the real model call. No network: make_client and
call_model are patched, so run_live is exercised without any paid request."""
import agent.llm as llm
from agent.configs import CONFIGS
from agent.llm import ModelReply
from experiments.cases import load_cases
from experiments.harness import build_inprocess, run_live


def test_temperature_reaches_call_model(tmp_path, monkeypatch):
    seen = {}
    monkeypatch.setattr(llm, "make_client", lambda *a, **k: "FAKECLIENT")

    def fake_call_model(client, model, system, messages, tools=None, temperature=0.0):
        seen["temperature"] = temperature
        return ModelReply(text="declining", tool_calls=[])

    monkeypatch.setattr(llm, "call_model", fake_call_model)

    bc, cc = build_inprocess(tmp_path / "h.db", tmp_path / "collector.jsonl")
    cases = [c for c in load_cases() if c.case_id == "benign_summary_01"]
    rows = run_live(cases, [CONFIGS["baseline"]], bc, cc, ["deepseek/deepseek-v4.1-flash"],
                    repeats=1, confirm=True, temperature=0.7)
    assert rows
    assert seen["temperature"] == 0.7
