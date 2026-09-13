# Customer identity and roles

Source: `observe_agent/cloud/security.py`.

## How the code works

Authenticator hashes the supplied X-API-Key and compares it with server-managed hashes. Principal.require enforces read, submit and review roles.

## Example

A registry maps a key hash to tenant acme, subject alice and roles read/submit. Alice can submit an incident but cannot approve an action without review.

## Debugging and limits

The registry stores hashes, not raw keys. Duplicate hashes are rejected. Cloud Run IAM is a separate invocation layer. Tenant membership currently grants role-based access to all tenant incidents.

See [the complete sequence](../CLOUD_RUNTIME.md) and [module map](../MODULE_GUIDE.md).

