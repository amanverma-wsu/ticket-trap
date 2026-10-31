"""Tests for the live-model wiring. No network: the OpenAI client and call_model are
patched, so we verify the adapter and the suite factory without any paid call."""
import httpx

import agent.llm as llm
from agent.configs import CONFIGS
from agent.llm import ModelReply, ToolCall
from experiments.cases import load_cases
from experiments.harness import build_inprocess, make_live_model_fn, run_live, run_suite


def wired(tmp_path):
    return build_inprocess(tmp_path / "h.db", tmp_path / "collector.jsonl")


def test_make_live_model_fn_adapts_to_call_model(monkeypatch):
    seen = {}

    monkeypatch.setattr(llm, "make_client", lambda *a, **k: "FAKECLIENT")

    def fake_call_model(client, model, system, messages, tools=None, temperature=0.0):
        seen.update(client=client, model=model, system=system, temperature=temperature)
        return ModelReply(text="ok")

    monkeypatch.setattr(llm, "call_model", fake_call_model)

    fn = make_live_model_fn(temperature=0.0)
    reply = fn("deepseek/deepseek-v4.1-flash", "SYS", [{"role": "user", "content": "hi"}], [])
    assert reply.text == "ok"
    assert seen["client"] == "FAKECLIENT"
    assert seen["model"] == "deepseek/deepseek-v4.1-flash"
    assert seen["system"] == "SYS"


def test_run_suite_accepts_custom_factory(tmp_path):
    bc, cc = wired(tmp_path)

    def factory(task):
        def fn(model, system, messages, tools):
            return ModelReply(text="I will not act on the ticket.", tool_calls=[])
        return fn

    cases = load_cases(include_held_out=False)
    rows = run_suite(cases, [CONFIGS["baseline"]], bc, cc, model="custom", agent_factory=factory)
    assert len(rows) == len(cases)
    assert all(not r["confirmed_leak"] for r in rows)
    assert all(r["model"] == "custom" for r in rows)


def test_run_live_aborts_without_confirmation(tmp_path, monkeypatch):
    bc, cc = wired(tmp_path)
    monkeypatch.setattr("builtins.input", lambda *a: "no")
    rows = run_live(load_cases(), [CONFIGS["baseline"]], bc, cc,
                    ["deepseek/deepseek-v4.1-flash"], repeats=1, confirm=False)
    assert rows == []
