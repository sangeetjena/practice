# Symptom

An API has p95 latency above 500 milliseconds or shows a sudden increase from its baseline.

# Diagnostic steps

1. Confirm the metric has current samples and uses a normalized route.
2. Compare request rate, error ratio, and p95 latency by service and deployed version.
3. Open representative traces and identify the child span contributing most additional time.
4. Correlate trace IDs with error logs without copying credentials or payloads.
5. Check pod readiness, restarts, database pool wait, queue lag, and dependency saturation.
6. Compare deployments, configuration, and feature-flag changes near the first bad time.

# Resolution choices

If one new version is affected and rollback is compatible, request an approved canary rollback.
If a dependency is saturated, reduce incoming pressure or increase safe capacity according to the
dependency runbook. Do not retry indiscriminately because retry amplification can worsen overload.

# Verification

Watch p95 latency, error rate, saturation, and request volume for the affected service. Recovery
requires the original SLO signal to improve for a sustained window; one healthy pod is insufficient.

# Rollback

If the action does not improve the original signal or creates a new regression, stop the rollout,
restore the previous reviewed configuration, and escalate to the service owner.
