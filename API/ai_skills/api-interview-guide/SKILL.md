---
name: api-interview-guide
description: Explain, extend, debug, or quiz the user on the API Interview Lab's API, security, data, observability, discovery, governance, and deployment components.
---

# API Interview Guide

Use this skill when working inside the `API` directory or when the user asks about this
project's REST, GraphQL, Pydantic, dataclass, pandas, asyncio, Docker, or Kubernetes examples.

## Required context

Read `PROJECT_KNOWLEDGE.md` before changing architecture or answering a project-specific
question. For an end-to-end explanation or interview preparation, also read
`../../docs/PROJECT_WALKTHROUGH.md`. Then read only the source files relevant to the question.

## Working rules

1. Keep the sales-order domain consistent across all examples so comparisons remain useful.
2. Maintain separation between transport models, domain models, and persistence.
3. Every new endpoint needs success, validation, and failure-path tests.
4. Prefer short runnable examples followed by interview trade-offs.
5. Do not present SQLite or pandas as production distributed-system choices.
6. Update `PROJECT_KNOWLEDGE.md` when architecture or public commands change.
7. Run `ruff check .` and `pytest` before considering a code change complete.

## Modes

- Explain a component: use the walkthrough, then verify the named source file.
- Trace a request: follow gateway → app → auth → store/dependency → telemetry.
- Change code: update behavior tests, commands, knowledge base and walkthrough when affected.
- Debug the running stack: start at the HTTP symptom, then metrics → trace → correlated logs →
  dependency/platform state. Do not treat correlation as proof of causation.
- Quiz: ask one question at a time and wait for the answer before revealing the solution.

## Interview teaching format

For explanations, cover: problem, flow, key code, complexity/failure behavior, production
alternative, and one likely follow-up question. Clearly distinguish implemented behavior from a
production extension. For system design, use: functional questions, non-functional requirements,
back-of-the-envelope estimates, HLD, component trade-offs, and conclusion.
