-- Proposed PostgreSQL HLD schema; the runnable library still uses SQLite.
-- This is a target design, not a migration or a PostgreSQL repository adapter.

CREATE TABLE tags (
  tenant_id UUID NOT NULL,
  tag_id UUID NOT NULL,
  display_name TEXT NOT NULL,
  normalized_name TEXT NOT NULL,
  state TEXT NOT NULL DEFAULT 'active'
    CHECK (state IN ('active', 'deleted')),
  version BIGINT NOT NULL DEFAULT 1 CHECK (version > 0),
  PRIMARY KEY (tenant_id, tag_id),
  UNIQUE (tenant_id, normalized_name)
);

CREATE TABLE resource_refs (
  tenant_id UUID NOT NULL,
  resource_id UUID NOT NULL,
  product TEXT NOT NULL,
  resource_type TEXT NOT NULL,
  external_id TEXT NOT NULL,
  state TEXT NOT NULL DEFAULT 'active'
    CHECK (state IN ('active', 'deleted')),
  tagset_version BIGINT NOT NULL DEFAULT 0
    CHECK (tagset_version >= 0),
  PRIMARY KEY (tenant_id, resource_id),
  UNIQUE (tenant_id, product, resource_type, external_id)
);

CREATE TABLE resource_tags (
  tenant_id UUID NOT NULL,
  resource_id UUID NOT NULL,
  tag_id UUID NOT NULL,
  association_id UUID NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by UUID NOT NULL,
  PRIMARY KEY (tenant_id, resource_id, tag_id),
  UNIQUE (tenant_id, association_id),
  FOREIGN KEY (tenant_id, resource_id)
    REFERENCES resource_refs (tenant_id, resource_id),
  FOREIGN KEY (tenant_id, tag_id)
    REFERENCES tags (tenant_id, tag_id)
);
CREATE INDEX resource_tags_by_tag ON resource_tags (
  tenant_id, tag_id, created_at DESC, association_id DESC
) INCLUDE (resource_id);

CREATE TABLE outbox (
  event_id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  aggregate_type TEXT NOT NULL,
  aggregate_id UUID NOT NULL,
  version BIGINT NOT NULL CHECK (version > 0),
  event_type TEXT NOT NULL,
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  published_at TIMESTAMPTZ,
  UNIQUE (tenant_id, aggregate_type, aggregate_id, version)
);
CREATE INDEX outbox_pending ON outbox (created_at, event_id)
  WHERE published_at IS NULL;

CREATE TABLE idempotency_records (
  tenant_id UUID NOT NULL,
  caller_id UUID NOT NULL,
  operation TEXT NOT NULL,
  request_key TEXT NOT NULL,
  request_hash TEXT NOT NULL,
  status_code INTEGER NOT NULL,
  response_body JSONB NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (tenant_id, caller_id, operation, request_key)
);

