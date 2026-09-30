CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE TABLE IF NOT EXISTS market_bars (
    symbol text NOT NULL,
    interval text NOT NULL,
    bar_time timestamptz NOT NULL,
    observed_at timestamptz NOT NULL,
    source text NOT NULL,
    source_id text NOT NULL,
    open double precision NOT NULL,
    high double precision NOT NULL,
    low double precision NOT NULL,
    close double precision NOT NULL,
    volume bigint NOT NULL CHECK (volume >= 0),
    adjusted boolean NOT NULL,
    PRIMARY KEY (symbol, interval, bar_time, source, source_id)
);
SELECT create_hypertable('market_bars', by_range('bar_time'), if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS market_bars_symbol_time_idx
    ON market_bars (symbol, interval, bar_time DESC);
