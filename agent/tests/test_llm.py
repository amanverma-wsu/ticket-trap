"""Unit tests for the model-call layer. No network, no API spend: we build fake
OpenAI-compatible response objects and check the pure normalization, and we check
make_client wiring without issuing a request."""
from types import SimpleNamespace

import pytest

from agent.llm import make_client, normalize_response


def _resp(content, tool_calls=None, model="deepseek/deepseek-v4.1-flash"):
    message = SimpleNamespace(content=content, tool_calls=tool_calls)
    choice = SimpleNamespace(message=message)
    return SimpleNamespace(choices=[choice], model=model)


def _tool_call(name, arguments, id="call_1"):
    return SimpleNamespace(id=id, function=SimpleNamespace(name=name, arguments=arguments))


def test_normalize_plain_text():
    reply = normalize_response(_resp("hello there"))
    assert reply.text == "hello there"
    assert reply.tool_calls == []
    assert reply.model == "deepseek/deepseek-v4.1-flash"


def test_normalize_tool_call_parses_json_arguments():
    tc = _tool_call("read_ticket", '{"ticket_id": 1}')
    reply = normalize_response(_resp(None, tool_calls=[tc]))
    assert reply.text == ""
    assert len(reply.tool_calls) == 1
    assert reply.tool_calls[0].name == "read_ticket"
    assert reply.tool_calls[0].arguments == {"ticket_id": 1}
    assert reply.tool_calls[0].id == "call_1"


def test_normalize_bad_arguments_become_empty_dict():
    tc = _tool_call("send_report", "{not valid json")
    reply = normalize_response(_resp(None, tool_calls=[tc]))
    assert reply.tool_calls[0].arguments == {}


def test_normalize_no_choices_is_safe():
    reply = normalize_response(SimpleNamespace(choices=[], model="deepseek/deepseek-v4.1-flash"))
    assert reply.text == ""
    assert reply.tool_calls == []


def test_make_client_requires_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        make_client()


def test_make_client_uses_openrouter_base_url(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test-not-real")
    client = make_client()
    assert "openrouter.ai" in str(client.base_url)
