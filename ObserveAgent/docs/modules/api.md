# REST gateway and private worker surface

Source: `observe_agent/cloud/api.py`.

## How the code works

create_app(role='api') installs customer routes; role='worker' installs only private delivery/relay routes. Bodies are bounded, authentication is mandatory, and 202 means durable acceptance.

## Example

POST /v1/incidents returns queued. GET /v1/incidents/inc-1 later returns completed or awaiting_approval. Posting new evidence saves a message and schedules the next revision.

## Debugging and limits

Do not confuse this entrypoint with observe_agent.api, the old unauthenticated local lab. Internal worker endpoints additionally require verified Google service identity.

See [the complete sequence](../CLOUD_RUNTIME.md) and [module map](../MODULE_GUIDE.md).

