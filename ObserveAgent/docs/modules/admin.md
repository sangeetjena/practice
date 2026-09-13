# Operator commands

Source: `observe_agent/cloud/admin.py`.

## How the code works

migrate initializes SQL and LangGraph schemas. publish relays pending events. drain processes pending events locally. reindex rebuilds one explicit tenant's active documents.

## Example

python -m observe_agent.cloud.admin reindex --tenant acme rebuilds Acme's vectors after a model change.

## Debugging and limits

Schema initialization is idempotent but does not migrate historical SQLite files. Administrative commands are not public REST routes.

See [the complete sequence](../CLOUD_RUNTIME.md) and [module map](../MODULE_GUIDE.md).

