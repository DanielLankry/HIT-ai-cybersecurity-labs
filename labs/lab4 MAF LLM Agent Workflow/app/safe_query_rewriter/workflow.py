import os

from agent_framework import AgentExecutorResponse, WorkflowBuilder, WorkflowContext, executor
from agent_framework.openai import OpenAIChatClient
from pydantic import BaseModel, Field


base_url = os.getenv("API_BASE_URL")
api_key = os.getenv("API_KEY")
model_id = os.getenv("MODEL", "deepseek/deepseek-chat-v3.1")

if not api_key:
    raise RuntimeError("API_KEY is not set. Add it to .env in the lab4 folder.")

client = OpenAIChatClient(
    base_url=base_url,
    api_key=api_key,
    model_id=model_id,
)


class RewriteResult(BaseModel):
    """Structured output from the first agent.

    This makes the rewritten query visible in the Dev UI workflow steps.
    """

    original_risk: str = Field(description="Why the original query is risky")
    rewritten_query: str = Field(description="Safe version of the query")
    safety_rule: str = Field(description="Rule used to rewrite the query")


query_rewriter_agent = client.create_agent(
    name="query-rewriter-agent",
    description="Rewrites unsafe cybersecurity questions into safe learning questions.",
    instructions="""
You are a defensive query rewriting agent.

Your task:
Read the user's cybersecurity question and rewrite it so it is safe for learning.

Rules:
- Do not answer the user.
- Keep the main learning goal.
- Remove requests to attack real systems, steal passwords, bypass security,
  write malware, or hide from detection.
- Make the rewritten query defensive and educational.
- Return only valid JSON.

Return this JSON format:
{
  "original_risk": "short reason why the original query is risky",
  "rewritten_query": "safe educational version of the query",
  "safety_rule": "short safety rule used"
}
""",
    output_model=RewriteResult,
)


safe_answer_agent = client.create_agent(
    name="safe-answer-agent",
    description="Answers only the safe rewritten question.",
    instructions="""
You are a beginner-friendly cybersecurity assistant.

You receive a safe rewritten cybersecurity question. Write an answer to it.

Rules:
- Say that the query was rewritten for safety.
- Keep the answer short, simple, and defensive.
- Do not only repeat the question.
- Do not give attack steps, exploit commands, malware code, password theft help,
  or instructions for attacking real systems.
""",
)


@executor(id="prepare-safe-answer")
async def prepare_safe_answer(
    response: AgentExecutorResponse,
    ctx: WorkflowContext[str],
):
    """Build a clean prompt for the answer agent.

    The rewriter returns JSON. This step extracts the safe query so the second
    agent answers the rewritten question instead of the full previous chat.
    """

    result = RewriteResult.model_validate_json(response.agent_run_response.text)

    safe_prompt = f"""
The original query was rewritten for safety.

Original risk:
{result.original_risk}

Safe rewritten query:
{result.rewritten_query}

Safety rule:
{result.safety_rule}

Write an answer to the safe rewritten query.
Do not repeat the question.
Keep the answer short, simple, and defensive.
"""

    await ctx.send_message(safe_prompt)


# Sequential workflow: rewrite first, prepare a clean prompt, then answer.
workflow = (
    WorkflowBuilder()
    .set_start_executor(query_rewriter_agent)
    .add_edge(query_rewriter_agent, prepare_safe_answer)
    .add_edge(prepare_safe_answer, safe_answer_agent)
    .build()
)


class WorkflowWrapper:
    """Small wrapper used by the course example to work cleanly in Dev UI."""

    def __init__(self, wf):
        self._workflow = wf

    async def run_stream(
        self,
        input_data=None,
        checkpoint_id=None,
        checkpoint_storage=None,
        **kwargs,
    ):
        if checkpoint_id is not None:
            raise NotImplementedError("Checkpoint resume is not supported for this lab.")

        async for event in self._workflow.run_stream(input_data, **kwargs):
            yield event

    def __getattr__(self, name):
        return getattr(self._workflow, name)


workflow = WorkflowWrapper(workflow)
