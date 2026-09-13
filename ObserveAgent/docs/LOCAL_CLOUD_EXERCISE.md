# Local asynchronous exercise (PowerShell)

This runs the cloud code locally with real PostgreSQL and a separate Chroma server. Pub/Sub is
replaced by the operator `drain` command, which consumes the same durable event table. It is a
local exercise, not a claim that a background publisher is running.

## Start

```powershell
cd practice/ObserveAgent
python scripts/bootstrap_cloud.py
docker compose --env-file .env.cloud -f compose.cloud.yml up -d --build
$key = (Get-Content local-api-key.txt -Raw).Trim()
$headers = @{"X-API-Key"=$key; "Idempotency-Key"="demo-submit-1"}
$body = @{id="inc-1"; title="Orders became slow"; service="orders"} | ConvertTo-Json
$created = Invoke-RestMethod -Method Post -Uri http://localhost:8091/v1/incidents -Headers $headers -ContentType application/json -Body $body
$created
```

The response is queued. The default Acme metrics URL expects the API lab's Prometheus exposed on
host port 9090. If that lab is not running, the agent records missing metrics instead of fabricating
evidence. Configure each real tenant's metrics endpoint in OBSERVE_TENANTS.

## Process and inspect

```powershell
docker compose --env-file .env.cloud -f compose.cloud.yml exec api python -m observe_agent.cloud.admin drain
$result = Invoke-RestMethod http://localhost:8091/v1/incidents/inc-1 -Headers $headers
$result | ConvertTo-Json -Depth 15
```

The run used PostgreSQL checkpoints and Chroma even though the model defaults are offline.
Re-submit the identical request/key: it returns the same incident without enqueuing a second event.
Changing its body with the same idempotency key returns 409.

## Add evidence and retrieve customer memory

```powershell
$message = @{id="msg-1"; content="Customer dependency configuration changed yesterday."} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://localhost:8091/v1/incidents/inc-1/messages -Headers $headers -ContentType application/json -Body $message
docker compose --env-file .env.cloud -f compose.cloud.yml exec api python -m observe_agent.cloud.admin drain
Invoke-RestMethod http://localhost:8091/v1/incidents/inc-1/messages -Headers $headers
```

The session ID stays the same; revision and run ID change. The new graph receives recent messages
and the prior report summary. Older messages remain in SQL. Requests during queued/running state
return 409; wait for the current event before adding new evidence.

## Approval and feedback

For actions, configure a tenant allowlist and supply an action_context target at incident creation.
When status is awaiting_approval, use the returned proposal_version and action IDs:

```powershell
$decision = @{id="approval-1"; approved=$true; proposal_version=$result.proposal_version; action_ids=@($result.result.proposed_actions[0].id)} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://localhost:8091/v1/incidents/inc-1/actions/decision -Headers $headers -ContentType application/json -Body $decision
```

Run drain again. Do not use an old `$result` after adding evidence; GET the latest proposal first.
Reviewer identity comes from the key registry. Feedback uses decision, resolved, cause and resolution
fields plus a client-generated id; it does not accept a reviewer or tenant field in the body.

## Debug

- `docker compose ... logs api migrate postgres chroma`: locate the failing component.
- GET status stuck queued: drain locally or inspect Scheduler/outbox delivery in Google Cloud.
- 401: verify the client key matches the stored SHA-256 hash.
- 403: verify role and server-managed service ownership.
- 404 with another customer's key: expected isolation, not missing global memory.
- 409 on approval: fetch the newest proposal version; new evidence invalidates previous approval.
- Failed incident: inspect cloud_events.error (exception class) and attempt count in PostgreSQL.
- After changing embedding model: run `cloud.admin reindex --tenant acme` in the configured container.

Keep volumes to preserve state. `docker compose down -v` deliberately deletes the local databases.
