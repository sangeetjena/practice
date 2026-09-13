# External-action reservations

Source: `observe_agent/cloud/effects.py`.

## How the code works

DurableActionExecutor writes a unique tenant/action reservation before calling the shared executor. Completed results can be replayed without repeating the effect.

## Example

SMTP succeeds but the process dies before recording success. On redelivery, the reservation exists and the result is marked uncertain; it is not sent again automatically.

## Debugging and limits

This sacrifices automatic retry for ambiguous writes. An operator must reconcile the provider, then create a newly reviewed proposal if needed. It is not an exactly-once delivery claim.

See [the complete sequence](../CLOUD_RUNTIME.md) and [module map](../MODULE_GUIDE.md).

