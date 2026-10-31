"""The loop must build OpenAI-compatible messages so the real API accepts them: an
assistant message carrying tool_calls, then tool messages with matching tool_call_id."""
import copy

import httpx

from agent.configs import get_config
from agent.llm import ModelReply, ToolCall
from agent.agent_loop import run_agent

TASK = {"ticket_id": 1, "authorized_customer_id": 1, "approved_destinations": ["reports@example.test"]}


def mock_backend():
    def handler(request):
        return httpx.Response(200, json={"id": 1, "customer_id": 1, "body": "help"})
    return httpx.Client(transport=httpx.MockTransport(handler), base_url="http://b.test")


class Recorder:
    def __init__(self, replies):
        self.replies = list(replies)
        self.seen = []
    def __call__(self, model, system, messages, tools):
        self.seen.append(copy.deepcopy(messages))
        return self.replies.pop(0)


def test_tool_turn_is_openai_shaped():
    rec = Recorder([
        ModelReply(tool_calls=[ToolCall("read_ticket", {"ticket_id": 1}, "c1")]),
        ModelReply(text="done", tool_calls=[]),
    ])
    run_agent(TASK, get_config("baseline"), "stub", mock_backend(), rec)
    second = rec.seen[1]
    assistant = [m for m in second if m["role"] == "assistant" and m.get("tool_calls")]
    assert assistant, "assistant message with tool_calls must precede the tool result"
    call = assistant[0]["tool_calls"][0]
    assert call["id"] == "c1"
    assert call["type"] == "function"
    assert call["function"]["name"] == "read_ticket"
    assert '"ticket_id": 1' in call["function"]["arguments"]
    tool_msgs = [m for m in second if m["role"] == "tool"]
    assert tool_msgs and tool_msgs[0]["tool_call_id"] == "c1"
