# Tenant archive and vector retrieval

Source: `observe_agent/cloud/knowledge.py`.

## How the code works

TenantKnowledge exposes the graph's storage contract over PostgreSQL and remote Chroma. It forces a tenant scope, selects a tenant/profile collection and queries only active approved source IDs.

## Example

Acme ingests a reviewed memory fix; search('memory', tenant_id='acme', service='orders') retrieves it. Globex gets no such result even when the text query is identical.

## Debugging and limits

PostgreSQL and Chroma do not share a transaction. The archive is authoritative; reindex repairs a partially indexed source. Historical source versions are retained separately.

See [the complete sequence](../CLOUD_RUNTIME.md) and [module map](../MODULE_GUIDE.md).

