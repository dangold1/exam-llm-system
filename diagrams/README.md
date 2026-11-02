# Exam System — Architecture Diagrams

Senior-architect documentation for the **Python stack** (`python/server` Flask backend + `python/client` React frontend).
Scope is intentionally limited per `CLAUDE.md`: `nodejs/` is ignored.

## Index

| # | File | Subject |
|---|------|---------|
| 1 | [01-system-overview.md](./01-system-overview.md) | High-level architecture, layering, runtime topology |
| 2 | [02-user-flow.md](./02-user-flow.md) | Student journey: load questions → answer → submit → see grades |
| 3 | [03-llm-orchestration.md](./03-llm-orchestration.md) | Azure OpenAI grading: classes, functions, retries, fallback |
| 4 | [04-data-model.md](./04-data-model.md) | API contracts, MongoDB schemas, Pydantic models |

All diagrams use **Mermaid** so they render natively on GitHub and most Markdown viewers.

## Reading order for an interview walk-through

1. Open `01-system-overview.md` first — sets the layered architecture context.
2. Walk through `02-user-flow.md` — narrates the happy path the interviewer can click through.
3. Drill into `03-llm-orchestration.md` — shows the LLM is *isolated, validated, and bounded*.
4. Reference `04-data-model.md` when the interviewer asks "what's stored / what's the contract?"

## Design intent (one paragraph)

A thin Flask route accepts a submission, persists it ungraded, then hands off to a `GradingService`
orchestrator that fans out per-question grading through an `AzureOpenAIGrader` adapter.
The adapter encapsulates **all** Azure transport, retries, and JSON repair; `GradingService` knows
nothing about HTTP or OpenAI. Grader output is **schema-validated by Pydantic** before persistence —
no malformed grade ever reaches MongoDB. A single grading failure degrades to a per-question fallback
(`grading_status: "failed"`, score 0, explanatory feedback) so one bad LLM call cannot poison the batch.
The React client renders results from the same JSON contract; failed grades are visually distinct.
