# Fail-closed cloud settings

Source: `observe_agent/cloud/config.py`.

## How the code works

CloudSettings.from_env requires a PostgreSQL connection and a nonempty tenant/service/metrics mapping. It also loads remote Chroma and Google push identity settings.

## Example

DATABASE_URL uses postgresql+psycopg:// for SQLAlchemy; checkpoint_url changes only the driver prefix for psycopg. OBSERVE_TENANTS fixes each tenant's Prometheus URL and service ownership.

## Debugging and limits

Cloud SQLite is rejected. Tests inject a SQLite Database explicitly; that exception is not enabled by deployment environment.

See [the complete sequence](../CLOUD_RUNTIME.md) and [module map](../MODULE_GUIDE.md).

