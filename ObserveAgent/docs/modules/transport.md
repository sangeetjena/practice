# Queue delivery and publication

Source: `observe_agent/cloud/transport.py`.

## How the code works

verify_service_identity checks a Google-signed identity token's audience and exact service-account email. OutboxPublisher sends stable event IDs and marks published only after broker confirmation.

## Example

A publisher crashes after Pub/Sub accepted E1. E1 is published again later; the worker deduplicates by the database event ID.

## Debugging and limits

Wrong identities are rejected before processing. The queue envelope cannot select a tenant or checkpoint; those are loaded from the stored event.

See [the complete sequence](../CLOUD_RUNTIME.md) and [module map](../MODULE_GUIDE.md).

