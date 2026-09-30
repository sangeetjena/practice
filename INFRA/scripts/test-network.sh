#!/usr/bin/env bash
set -euo pipefail

CONTEXT=kind-local-platform
AUTHORIZED_POD=infra-network-check-${RANDOM}
UNAUTHORIZED_NAMESPACE=infra-network-denied-${RANDOM}
UNAUTHORIZED_POD=infra-network-check-${RANDOM}

cleanup() {
  kubectl --context "$CONTEXT" -n workloads delete pod "$AUTHORIZED_POD" --ignore-not-found >/dev/null 2>&1 || true
  kubectl --context "$CONTEXT" delete namespace "$UNAUTHORIZED_NAMESPACE" --ignore-not-found >/dev/null 2>&1 || true
}
trap cleanup EXIT

kubectl --context "$CONTEXT" -n workloads run "$AUTHORIZED_POD" \
  --image=busybox:1.36.1 --restart=Never --command -- sleep 1800
kubectl --context "$CONTEXT" -n workloads wait --for=condition=Ready \
  "pod/$AUTHORIZED_POD" --timeout=90s

for endpoint in \
  "citus-coordinator.postgres.svc.cluster.local 5432" \
  "cassandra.cassandra.svc.cluster.local 9042" \
  "qdrant.qdrant.svc.cluster.local 6333" \
  "qdrant.qdrant.svc.cluster.local 6334" \
  "timescale.timescale.svc.cluster.local 5432" \
  "redis.redis.svc.cluster.local 6379"; do
  read -r host port <<< "$endpoint"
  kubectl --context "$CONTEXT" -n workloads exec "$AUTHORIZED_POD" -- \
    nslookup "$host" >/dev/null
  kubectl --context "$CONTEXT" -n workloads exec "$AUTHORIZED_POD" -- \
    nc -z -w 3 "$host" "$port"
  printf 'workloads -> %s:%s PASS\n' "$host" "$port"
done

kubectl --context "$CONTEXT" create namespace "$UNAUTHORIZED_NAMESPACE"
kubectl --context "$CONTEXT" -n "$UNAUTHORIZED_NAMESPACE" run "$UNAUTHORIZED_POD" \
  --image=busybox:1.36.1 --restart=Never --command -- sleep 1800
kubectl --context "$CONTEXT" -n "$UNAUTHORIZED_NAMESPACE" wait \
  --for=condition=Ready "pod/$UNAUTHORIZED_POD" --timeout=90s

for endpoint in \
  "citus-coordinator.postgres.svc.cluster.local 5432" \
  "cassandra.cassandra.svc.cluster.local 9042" \
  "qdrant.qdrant.svc.cluster.local 6333" \
  "qdrant.qdrant.svc.cluster.local 6334" \
  "timescale.timescale.svc.cluster.local 5432" \
  "redis.redis.svc.cluster.local 6379"; do
  read -r host port <<< "$endpoint"
  kubectl --context "$CONTEXT" -n "$UNAUTHORIZED_NAMESPACE" exec "$UNAUTHORIZED_POD" -- nslookup "$host" >/dev/null
  # A remote marker distinguishes a failed connection from a failed kubectl exec.
  result="$(kubectl --context "$CONTEXT" -n "$UNAUTHORIZED_NAMESPACE" exec "$UNAUTHORIZED_POD" -- \
    sh -c 'command -v nc >/dev/null || exit 2; if nc -z -w 3 "$1" "$2"; then echo ALLOWED; else echo DENIED; fi' -- "$host" "$port")"
  [[ "$result" == DENIED ]] || { echo "Unauthorized access succeeded: $host:$port" >&2; exit 1; }
  printf 'unauthorized -> %s:%s BLOCKED\n' "$host" "$port"
done
