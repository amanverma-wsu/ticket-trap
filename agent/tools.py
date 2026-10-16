"""Tool schemas exposed to the model, and dispatch to the backend.

The model sees exactly three tools, identical across all conditions. Each call is
forwarded to the matching backend endpoint. A backend permission denial (HTTP 403) is
surfaced back to the model as a tool error rather than raised, so the agent can observe
that it was blocked and the harness can record the attempt.
"""
import httpx

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "read_ticket",
            "description": "Read the assigned support ticket by its id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "integer", "description": "The ticket to read."}
                },
                "required": ["ticket_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_customer_record",
            "description": "Read a customer record by its id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "integer", "description": "The customer record to read."}
                },
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_report",
            "description": "Send a report about a ticket to a destination.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "integer"},
                    "destination": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["ticket_id", "destination", "content"],
            },
        },
    },
]

TOOL_NAMES = [t["function"]["name"] for t in TOOL_SCHEMAS]


def _result(response):
    try:
        body = response.json()
    except Exception:
        body = response.text
    if response.status_code == 200:
        return {"ok": True, "status": 200, "data": body}
    detail = body.get("detail") if isinstance(body, dict) else body
    return {"ok": False, "status": response.status_code, "error": detail}


def call_tool(name, arguments, client):
    arguments = arguments or {}
    try:
        if name == "read_ticket":
            r = client.get("/tools/read_ticket", params={"ticket_id": arguments["ticket_id"]})
        elif name == "read_customer_record":
            r = client.get(
                "/tools/read_customer_record",
                params={"customer_id": arguments["customer_id"]},
            )
        elif name == "send_report":
            r = client.post(
                "/tools/send_report",
                json={
                    "ticket_id": arguments["ticket_id"],
                    "destination": arguments["destination"],
                    "content": arguments["content"],
                },
            )
        else:
            return {"ok": False, "status": None, "error": f"unknown tool {name!r}"}
    except KeyError as e:
        return {"ok": False, "status": None,
                "error": f"missing argument {e.args[0]!r} for tool {name!r}"}
    return _result(r)
