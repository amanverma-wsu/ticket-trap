"""Model-call layer for the TicketTrap agent.

DeepSeek exposes an OpenAI-compatible API, so we use the `openai` SDK pointed at
DeepSeek's base URL. Both models under test (deepseek-flash, deepseek-v4-pro) go through
this one path.

The network call (`call_model`) is kept thin and separate from the pure response-parsing
(`normalize_response`) so the parsing can be unit-tested without hitting the API or
spending anything.
"""
import json
import os
from dataclasses import dataclass, field


@dataclass
class ToolCall:
    name: str
    arguments: dict
    id: str | None = None


@dataclass
class ModelReply:
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    model: str | None = None  # exact model ID the API reported, for reproducibility


def make_client(api_key: str | None = None, base_url: str | None = None):
    """Build an OpenAI-SDK client pointed at DeepSeek. Reads DEEPSEEK_API_KEY and
    DEEPSEEK_BASE_URL from the environment when not passed explicitly."""
    from openai import OpenAI

    key = api_key or os.environ.get("DEEPSEEK_API_KEY")
    url = base_url or os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    if not key:
        raise RuntimeError(
            "DEEPSEEK_API_KEY is not set; put it in .env (never commit it)."
        )
    return OpenAI(api_key=key, base_url=url)


def normalize_response(response) -> ModelReply:
    """Turn a raw OpenAI-compatible chat completion into a ModelReply.

    Pure function over the response object — no network — so it is unit-testable with a
    stub. Tool-call arguments come back as a JSON string from the API and are parsed to a
    dict here; unparseable arguments become an empty dict rather than raising.
    """
    reply = ModelReply(model=getattr(response, "model", None))
    choices = getattr(response, "choices", None) or []
    if not choices:
        return reply

    message = choices[0].message
    reply.text = getattr(message, "content", None) or ""

    for tc in getattr(message, "tool_calls", None) or []:
        fn = tc.function
        try:
            args = json.loads(fn.arguments) if fn.arguments else {}
        except (json.JSONDecodeError, TypeError):
            args = {}
        reply.tool_calls.append(
            ToolCall(name=fn.name, arguments=args, id=getattr(tc, "id", None))
        )
    return reply


def call_model(client, model, system, messages, tools=None, temperature=0.0) -> ModelReply:
    """Make one chat-completion call and normalize the result. `messages` is a list of
    {role, content} dicts; `system` is prepended as a system message."""
    full_messages = [{"role": "system", "content": system}, *messages]
    kwargs = {"model": model, "messages": full_messages, "temperature": temperature}
    if tools:
        kwargs["tools"] = tools
    response = client.chat.completions.create(**kwargs)
    return normalize_response(response)
