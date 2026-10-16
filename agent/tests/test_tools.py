"""Tests for the tool schemas and backend dispatch. Uses httpx.MockTransport, so no
real backend and no network are needed."""
import json

import httpx

from agent.tools import TOOL_NAMES, TOOL_SCHEMAS, call_tool


def make_client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler), base_url="http://backend.test")


def test_exactly_three_tools():
    assert TOOL_NAMES == ["read_ticket", "read_customer_record", "send_report"]
    for t in TOOL_SCHEMAS:
        assert t["type"] == "function"
        assert "name" in t["function"]
        assert "parameters" in t["function"]


def test_read_ticket_dispatch():
    seen = {}

    def handler(request):
        seen["path"] = request.url.path
        seen["ticket_id"] = request.url.params.get("ticket_id")
        return httpx.Response(200, json={"id": 1, "customer_id": 1, "body": "hello"})

    out = call_tool("read_ticket", {"ticket_id": 1}, make_client(handler))
    assert seen["path"] == "/tools/read_ticket"
    assert seen["ticket_id"] == "1"
    assert out["ok"] is True
    assert out["data"]["body"] == "hello"


def test_unauthorized_record_surfaces_403():
    def handler(request):
        return httpx.Response(403, json={"detail": "not authorized"})

    out = call_tool("read_customer_record", {"customer_id": 2}, make_client(handler))
    assert out["ok"] is False
    assert out["status"] == 403
    assert "not authorized" in out["error"]


def test_send_report_posts_body():
    seen = {}

    def handler(request):
        seen["path"] = request.url.path
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"status": "sent", "destination": "r@example.test"})

    out = call_tool(
        "send_report",
        {"ticket_id": 1, "destination": "r@example.test", "content": "done"},
        make_client(handler),
    )
    assert seen["path"] == "/tools/send_report"
    assert seen["body"]["destination"] == "r@example.test"
    assert out["ok"] is True


def test_unknown_tool():
    out = call_tool("delete_everything", {}, make_client(lambda r: httpx.Response(200)))
    assert out["ok"] is False
    assert "unknown tool" in out["error"]


def test_missing_argument():
    out = call_tool("read_ticket", {}, make_client(lambda r: httpx.Response(200)))
    assert out["ok"] is False
    assert "missing argument" in out["error"]
