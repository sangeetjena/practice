---
name: stock-csv-research
description: Maintain this CrewAI stock prediction project, its YAML agent groups, typed contracts, reusable tools and CSV memory. Use for changes inside stock; infrastructure and ML training live elsewhere.
---

# Stock CSV research

This brief supersedes the older mixed DB/API workflow. Read README.md for layout
and docs/RUNBOOK.md for exact commands, memory schema and review semantics.

- Package is stock_research. Initialized by official CrewAI classic Flow generator;
  pyproject type=flow, kickoff=stock_research.main:kickoff.
- Modules are agents (grouped crews/YAML), models (all Pydantic contracts), flow
  (group and master orchestration), tools (reusable APIs/storage/calculations).
- Groups: data_ingestion (discovery, technical, fundamental, earnings, news),
  analytical (volume/candlestick/Bollinger), master, learner, critique.
- Use standard CrewBase/agent/task/crew/tool/llm decorators. YAML owns prompts/tasks.
  Parallel tasks use async_execution then a synchronous context barrier. Do not
  execute discovery with ingestion tasks or remove the barrier.
- No active database/vector-store writes. CSV is durable memory; CrewAI vector
  memory is disabled. Reusable connectors remain in tools/db for future use.
- Source numbers are validated against the bound tool results. Code calculates
  indicators, fundamental expiry, next-session verdicts and historical accuracy.
  LLM agents summarize/interpret and propose bounded research directions.
- Fundamentals expire after one calendar month, read only eligible past snapshots.
  Current APIs do not provide historical replay; live cutoffs must be current.
- CSV records preserve original prediction/evidence. Critique only adds fields.
  Evaluate the first later completed session, never a favorable later bar.
  Keep original/later evidence separate and avoid hindsight attribution.
- Learner passes evaluated CSV outcomes and suggestions to master; no automatic
  retraining or rule changes. Local knowledge Markdown is reference guidance.
- Offline fixtures are synthetic, isolated under data/offline, and abstain.
- Existing .env is untracked and must be preserved. Credentials never enter logs.
- Unit tests run without external systems. Use real Crew/task construction and
  simulated task execution to validate concurrency/contracts before live tests.
