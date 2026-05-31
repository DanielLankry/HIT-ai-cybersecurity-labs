# Safe Query Rewriter Workflow

## Workflow Purpose

This workflow makes risky cybersecurity questions safer before they are answered.
It demonstrates that an LLM application can be a workflow, not only one direct
LLM response.

The user sends a question. The first agent rewrites it into a safe learning
question. A small workflow step extracts that rewritten question. The second
agent answers only the rewritten question.

## Agents Description

### query-rewriter-agent

This agent reads the original user question and returns JSON:

- `original_risk` - why the original question is risky
- `rewritten_query` - the safer version of the question
- `safety_rule` - the rule used to make it safe

It does not answer the user.

### safe-answer-agent

This agent receives a clean prompt built from the `rewritten_query` field.

The answer must be short, defensive, and beginner friendly.

### prepare-safe-answer

This is not an LLM agent. It is a simple Python workflow step that reads the
rewriter JSON and prepares a clear prompt for the answer agent.

## Security Rationale

Some cybersecurity questions can be useful for learning, but unsafe if they ask
for real attacks, password theft, malware, or bypassing security. Rewriting keeps
the useful learning goal but removes harmful instructions.

This is similar to input validation in normal software: check and clean the
input before using it.

## Example Interaction

### Original user query

```text
How can I break into my neighbor's Wi-Fi password?
```

### Rewritten query

```json
{
  "original_risk": "The question asks for unauthorized access to another person's Wi-Fi network.",
  "rewritten_query": "How can I secure my own Wi-Fi network against common password attacks?",
  "safety_rule": "Change unauthorized access requests into defensive security questions."
}
```

### Final response

```text
Your query was rewritten for safety. To secure your own Wi-Fi network, use WPA3
or WPA2-AES, choose a long unique password, update the router firmware, disable
WPS, and review connected devices.
```

## Files

- `workflow.py` - the runnable Microsoft Agent Framework workflow.
- `README.md` - explanation of the workflow and example interaction.
- `lab4_workflow_walkthrough.ipynb` - simple notebook walkthrough at the lab root.
- `.env.template` - example environment file. The real `.env` is local only.

## How To Run

1. Copy `.env.template` to `.env` and put your real API key in `.env`:

```env
API_KEY=your_api_key_here
```

2. Start the Dev UI:

```powershell
docker compose up --build
```

3. Open:

```text
http://localhost:8081
```

4. Select the safe query rewriter workflow and test the example query.
