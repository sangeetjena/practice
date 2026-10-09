-- Apply on the INFRA Citus coordinator's agentdb. This is the durable source of truth.
CREATE TABLE IF NOT EXISTS market_events (
    event_id uuid PRIMARY KEY,
    symbol text NOT NULL,
    event_type text NOT NULL,
    occurred_at timestamptz NOT NULL,
    observed_at timestamptz NOT NULL,
    source text NOT NULL,
    source_id text NOT NULL,
    payload jsonb NOT NULL,
    UNIQUE (source, source_id)
);
CREATE INDEX IF NOT EXISTS market_events_symbol_time_idx ON market_events (symbol, occurred_at);
CREATE INDEX IF NOT EXISTS market_events_observed_idx ON market_events (observed_at);

CREATE TABLE IF NOT EXISTS stock_context (
    symbol text PRIMARY KEY,
    version integer NOT NULL CHECK (version > 0),
    as_of timestamptz NOT NULL,
    context jsonb NOT NULL
);

CREATE TABLE IF NOT EXISTS decisions (
    decision_id uuid PRIMARY KEY,
    symbol text NOT NULL,
    decided_at timestamptz NOT NULL,
    cutoff_at timestamptz NOT NULL,
    action text NOT NULL,
    snapshot jsonb NOT NULL,
    CHECK (cutoff_at <= decided_at)
);
CREATE INDEX IF NOT EXISTS decisions_symbol_time_idx ON decisions (symbol, decided_at DESC);

CREATE TABLE IF NOT EXISTS critiques (
    critique_id uuid PRIMARY KEY,
    decision_id uuid NOT NULL REFERENCES decisions (decision_id),
    evaluated_at timestamptz NOT NULL,
    outcome text NOT NULL,
    critique jsonb NOT NULL
);

CREATE TABLE IF NOT EXISTS model_predictions (
    prediction_id uuid PRIMARY KEY,
    symbol text NOT NULL,
    cutoff_at timestamptz NOT NULL,
    model_name text NOT NULL,
    model_version text NOT NULL,
    feature_version text NOT NULL,
    features jsonb NOT NULL,
    target text NOT NULL,
    probability_up double precision NOT NULL CHECK (probability_up BETWEEN 0 AND 1),
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (symbol, cutoff_at, model_name, model_version)
);
CREATE TABLE IF NOT EXISTS stock_summary_daily (
    symbol text NOT NULL,
    cutoff_at timestamptz NOT NULL,
    summary jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (symbol, cutoff_at)
);

-- Additive CrewAI research tables; legacy ML predictions/daily summaries are retained.
CREATE TABLE IF NOT EXISTS research_runs (
    run_id uuid PRIMARY KEY, status text NOT NULL, record jsonb NOT NULL
);
CREATE TABLE IF NOT EXISTS research_audit (
    audit_id bigserial PRIMARY KEY, run_id uuid NOT NULL REFERENCES research_runs(run_id),
    kind text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(), record jsonb NOT NULL
);
CREATE TABLE IF NOT EXISTS stock_research_summary (
    decision_id uuid PRIMARY KEY REFERENCES decisions(decision_id),
    run_id uuid NOT NULL REFERENCES research_runs(run_id), symbol text NOT NULL,
    cutoff_at timestamptz NOT NULL, packet jsonb NOT NULL, recommendation jsonb NOT NULL
);
CREATE INDEX IF NOT EXISTS research_summary_symbol_cutoff ON stock_research_summary(symbol,cutoff_at DESC);
CREATE TABLE IF NOT EXISTS stock_research_criticism (
    criticism_id bigserial PRIMARY KEY, run_id uuid NOT NULL REFERENCES research_runs(run_id),
    decision_id uuid NOT NULL REFERENCES stock_research_summary(decision_id),
    evaluated_at timestamptz NOT NULL DEFAULT now(), report jsonb NOT NULL, terminal boolean NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS research_terminal_critique ON stock_research_criticism(decision_id) WHERE terminal;
-- Read recommendations together with criticism without modifying original snapshots.
CREATE OR REPLACE VIEW stock_research_summary_with_criticism AS
SELECT s.*, COALESCE((SELECT jsonb_agg(c.report ORDER BY c.evaluated_at)
    FROM stock_research_criticism c WHERE c.decision_id=s.decision_id), '[]'::jsonb) AS criticisms
FROM stock_research_summary s;
