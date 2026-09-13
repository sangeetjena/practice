# Validated public inputs

Source: `observe_agent/cloud/contracts.py`.

## How the code works

Strict Pydantic models forbid extra fields and bound public strings. They exclude tenant_id and reviewer: authentication supplies those values.

## Example

IncidentInput(id='inc-1', title='Slow orders', service='orders') is valid. Adding tenant_id='globex' yields an API 422 response.

## Debugging and limits

ApprovalInput requires an exact proposal_version and explicit action IDs; the database checks that the version is current.

See [the complete sequence](../CLOUD_RUNTIME.md) and [module map](../MODULE_GUIDE.md).

