# Lab 4 - MAF LLM Agent Workflow

## Lab Purpose

This lab demonstrates that an LLM application can be a workflow, not only one
direct chatbot response. The workflow makes risky cybersecurity questions safer
before they are answered.

The user sends a question. The first agent rewrites it into a safe learning
question. A small Python workflow step extracts that rewritten question. The
second agent answers only the safe version.

## Workflow

```text
User Query
   ↓
query-rewriter-agent
   ↓
prepare-safe-answer
   ↓
safe-answer-agent
```

## Agents / Steps

### query-rewriter-agent

Reads the original user question and returns JSON with:

- `original_risk`
- `rewritten_query`
- `safety_rule`

### prepare-safe-answer

A simple Python workflow step. It extracts `rewritten_query` from the JSON and
builds a clean prompt for the answer agent.

### safe-answer-agent

Answers only the rewritten safe question. The answer should stay short,
defensive, and beginner friendly.

## Files

- `README.md` - this GitHub folder summary.
- `app/safe_query_rewriter/workflow.py` - the runnable Microsoft Agent Framework workflow.
- `app/safe_query_rewriter/README.md` - detailed workflow explanation and example interaction.
- `lab4_workflow_walkthrough.ipynb` - simple notebook walkthrough of the workflow idea.
- `compose.yml` - Docker Compose file for the Dev UI.
- `Dockerfile`, `pyproject.toml`, `uv.lock` - Python runtime files.
- `.env.template` - example environment file. The real `.env` is local only.

## Example

Original unsafe query:

```text
How can I break into my neighbor's Wi-Fi password?
```

Safe rewritten query:

```text
How can I secure my own Wi-Fi network against common password attacks?
```

Final answer gives defensive Wi-Fi security advice instead of attack steps.

## How To Run

1. Copy `.env.template` to `.env`.
2. Put your API key in `.env`.
3. Start the Dev UI:

```powershell
docker compose up --build
```

4. Open:

```text
http://localhost:8081
```

5. Select the safe query rewriter workflow and test the example query.
