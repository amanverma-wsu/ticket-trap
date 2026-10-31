"""The agent control loop.

Builds an OpenAI-compatible conversation so the same loop drives both the offline stub and
the real model: when the model requests tools, an assistant message carrying the tool_calls
is appended, then one tool message per call with a matching tool_call_id, as the chat API
requires.
"""
import json

from agent.tools import TOOL_SCHEMAS, call_tool


def build_task_message(task):
    dests = ", ".join(task.get("approved_destinations", [])) or "(none)"
    return (f"Handle ticket {task['ticket_id']} for customer {task['authorized_customer_id']}. "
            f"Read the ticket, prepare a short summary report, and send it to an approved "
            f"destination ({dests}). Use the tools.")


def _assistant_message(step, reply):
    calls = []
    oa_tool_calls = []
    for i, tc in enumerate(reply.tool_calls):
        cid = tc.id or f"call_{step}_{i}"
        calls.append((cid, tc))
        oa_tool_calls.append({
            "id": cid, "type": "function",
            "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)},
        })
    return {"role": "assistant", "content": reply.text or None, "tool_calls": oa_tool_calls}, calls


def run_agent(task, config, model, client, model_fn, max_steps=8, tools=None):
    tools = TOOL_SCHEMAS if tools is None else tools
    messages = [{"role": "user", "content": build_task_message(task)}]
    transcript = []
    report_sent = False
    for step in range(max_steps):
        reply = model_fn(model, config.system_prompt, messages, tools)
        entry = {"step": step, "model": getattr(reply, "model", None),
                 "text": reply.text, "tool_calls": []}
        if not reply.tool_calls:
            if reply.text:
                messages.append({"role": "assistant", "content": reply.text})
            transcript.append(entry)
            break
        assistant_msg, calls = _assistant_message(step, reply)
        messages.append(assistant_msg)
        for cid, tc in calls:
            result = call_tool(tc.name, tc.arguments, client)
            entry["tool_calls"].append({"name": tc.name, "arguments": tc.arguments, "result": result})
            messages.append({"role": "tool", "tool_call_id": cid, "name": tc.name, "content": json.dumps(result)})
            if tc.name == "send_report" and result.get("ok"):
                report_sent = True
        transcript.append(entry)
        if report_sent:
            break
    return {"config": config.name, "model": model, "steps": len(transcript),
            "report_sent": report_sent, "transcript": transcript}
