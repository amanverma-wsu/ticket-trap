"""Custom agent loop: call model, parse tool calls, invoke backend tools, log everything.

Provider dispatch is intentionally thin so both pinned models run through one loop.
"""
import os

from configs import CONFIGS
from tools import TOOL_SCHEMAS


def run_agent(task: dict, config_name: str, model: str, max_steps: int = 8) -> dict:
    config = CONFIGS[config_name]
    transcript = []  # full log: every model message and tool call

    # TODO:
    #  1. Build the initial messages from config.system_prompt + the trusted task.
    #  2. Loop up to max_steps:
    #       - call the model (OpenAI or Anthropic, chosen by `model`)
    #       - if it requests a tool, call the backend endpoint and append the result
    #       - record each step in `transcript`
    #  3. Stop when the agent sends a report or hits the step limit.
    #  Permissions are enforced by the backend (config.enforce_permissions is set
    #  server-side per trial); the agent never sees or controls them.

    return {"config": config_name, "model": model, "transcript": transcript}


if __name__ == "__main__":
    print("Models:", os.getenv("OPENAI_MODEL"), os.getenv("ANTHROPIC_MODEL"))
    print("Configs:", list(CONFIGS))
    print("Tools:", [t["name"] for t in TOOL_SCHEMAS])
