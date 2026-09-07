---
name: api-interview-guide
description: Explain, extend, debug, or quiz the user on the API Interview Lab project.
---

# API Interview Guide

Use this skill when working inside the `API` directory or when the user asks about this
project's REST, GraphQL, Pydantic, dataclass, pandas, asyncio, Docker, or Kubernetes examples.

## Required context

Read `PROJECT_KNOWLEDGE.md` before changing architecture or answering a project-specific
question. Read only the source files relevant to the question after that.

## Working rules

1. Keep the sales-order domain consistent across all examples so comparisons remain useful.
2. Maintain separation between transport models, domain models, and persistence.
3. Every new endpoint needs success, validation, and failure-path tests.
4. Prefer short runnable examples followed by interview trade-offs.
5. Do not present SQLite or pandas as production distributed-system choices.
6. Update `PROJECT_KNOWLEDGE.md` when architecture or public commands change.
7. Run `ruff check .` and `pytest` before considering a code change complete.

## Interview teaching format

For explanations, cover: problem, flow, key code, complexity/failure behavior, production
alternative, and one likely follow-up question. When quizzing, ask one question at a time and
wait for the user's answer before revealing the solution.

