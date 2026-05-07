import os
import json
from typing import Annotated
import chainlit as cl
from autogen import ConversableAgent
from autogen.events.agent_events import ExecuteFunctionEvent, ExecutedFunctionEvent


def check_password_strength(
    password: Annotated[str, "The password string to evaluate"],
) -> dict:
    """Evaluate password strength and return a structured score."""
    length = len(password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(not c.isalnum() for c in password)

    score = sum([
        length >= 8,
        length >= 12,
        has_upper,
        has_lower,
        has_digit,
        has_symbol,
    ])

    if score >= 5:
        verdict = "strong"
    elif score >= 3:
        verdict = "medium"
    else:
        verdict = "weak"

    return {
        "length": length,
        "has_upper": has_upper,
        "has_lower": has_lower,
        "has_digit": has_digit,
        "has_symbol": has_symbol,
        "score": score,
        "max_score": 6,
        "verdict": verdict,
    }


api_key = os.getenv("API_KEY")
api_base_url = os.getenv("API_BASE_URL")
model = os.getenv("MODEL")

if not api_key:
    raise RuntimeError("API_KEY is not set. Add it to .env in the project root.")

llm_config = {
    "config_list": [
        {
            "model": model,
            "api_key": api_key,
            "base_url": api_base_url,
            "price": [0, 0],
        }
    ],
}


SYSTEM_PROMPT = """You are a password strength checker.

Your job: extract the password from the user's message and call
check_password_strength with it.

Rules for extracting the password:
- If the message is a single token with no spaces (e.g. "Daniel1234",
  "hello123!"), the entire message IS the password. Pass it as-is.
- If the message contains a phrase like "check this password: X",
  "the password is X", "test X", "evaluate X" — the password is X.
- Never ask the user to repeat the password. The password is in the
  message you just received.
- After the tool returns, summarize the score and verdict in plain
  English. If verdict is weak or medium, suggest one improvement.

Only ask for clarification if the message is clearly NOT a password
(e.g. greetings like "hi", or questions like "what can you do?")."""

WELCOME = """\
Hi. I am the password strength checker.

Send a password and I'll evaluate it across six criteria.
You'll see the tool call as an expandable Step below.
"""


def _format_content(content) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, (dict, list, tuple)):
        return json.dumps(content, ensure_ascii=True, indent=2)
    return str(content)


def _is_password_answer(msg: dict) -> bool:
    """Stop the AG2 loop after the agent's natural-language summary, not on
    the raw tool result. Tool results have role="tool" and their JSON content
    contains "score"/"verdict" too, so we must filter by role and shape."""
    if not isinstance(msg, dict):
        return False
    if msg.get("role") in ("tool", "function"):
        return False
    if msg.get("tool_calls"):
        return False
    content = msg.get("content")
    if not isinstance(content, str) or not content:
        return False
    stripped = content.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return False
    text = content.lower()
    return "score" in text or "verdict" in text or "/6" in text


@cl.on_chat_start
async def on_chat_start():
    agent = ConversableAgent(
        name="password_checker_agent",
        system_message=SYSTEM_PROMPT,
        llm_config=llm_config,
        human_input_mode="NEVER",
        is_termination_msg=_is_password_answer,
        functions=[check_password_strength],
    )
    cl.user_session.set("agent", agent)
    await cl.Message(content=WELCOME).send()


@cl.on_message
async def on_message(message: cl.Message):
    agent: ConversableAgent = cl.user_session.get("agent")

    response = await agent.a_run(
        message=message.content,
        clear_history=False,
        max_turns=4,
        summary_method="last_msg",
        user_input=False,
    )

    
    
    tool_inputs: dict = {}

    async for event in response.events:
        if isinstance(event, ExecuteFunctionEvent):
            ev = event.content
            key = getattr(ev, "call_id", None) or ev.func_name
            tool_inputs[key] = {
                "name": ev.func_name,
                "input": _format_content(ev.arguments) or "(no arguments)",
            }
            continue

        if not isinstance(event, ExecutedFunctionEvent):
            continue

        ev = event.content
        key = getattr(ev, "call_id", None) or ev.func_name
        step_data = tool_inputs.get(key, {"name": ev.func_name, "input": "(no arguments)"})
        async with cl.Step(name=step_data["name"], type="tool") as step:
            step.input = step_data["input"]
            step.output = _format_content(ev.content)

    summary = await response.summary
    await cl.Message(content=_format_content(summary)).send()