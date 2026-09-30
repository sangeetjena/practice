#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_credentials
kubectl --context "$CONTEXT" wait --for=condition=Ready nodes --all --timeout=5m
kubectl --context "$CONTEXT" -n postgres rollout status statefulset/citus-coordinator --timeout=30m
kubectl --context "$CONTEXT" -n postgres rollout status statefulset/citus-worker --timeout=30m
kubectl --context "$CONTEXT" -n cassandra rollout status statefulset/cassandra --timeout=30m
kubectl --context "$CONTEXT" -n qdrant rollout status statefulset/qdrant --timeout=20m
kubectl --context "$CONTEXT" -n timescale rollout status statefulset/timescale --timeout=20m
kubectl --context "$CONTEXT" -n redis rollout status statefulset/redis --timeout=10m

kubectl --context "$CONTEXT" -n timescale exec timescale-0 -- \
  psql -U postgres -d stock -tAc "SELECT default_version FROM pg_available_extensions WHERE name='timescaledb';" | \
  grep -Eq '^[0-9]'
echo "TimescaleDB: extension available PASS"
kubectl --context "$CONTEXT" -n redis exec redis-0 -- redis-cli ping | grep -qx PONG
echo "Redis: authenticated PING PASS"

active_workers="$(kubectl --context "$CONTEXT" -n postgres exec citus-coordinator-0 -- \
  psql -U postgres -d agentdb -tAc "SELECT count(*) FROM pg_dist_node WHERE isactive AND noderole='primary' AND groupid > 0;")"
[[ "$active_workers" == 3 ]] || { echo 'Expected three registered Citus workers.' >&2; exit 1; }
reachable_workers="$(kubectl --context "$CONTEXT" -n postgres exec citus-coordinator-0 -- \
  psql -U postgres -d agentdb -tAc "SELECT count(*) FROM run_command_on_workers('SELECT 1') WHERE success;")"
[[ "$reachable_workers" == 3 ]] || { echo 'Citus cannot query every worker.' >&2; exit 1; }
echo "Citus: three registered, reachable workers PASS"

for ordinal in 0 1 2; do
  ring="$(kubectl --context "$CONTEXT" -n cassandra exec "cassandra-$ordinal" -- nodetool status)"
  [[ "$(grep -c '^UN ' <<< "$ring")" == 3 ]] || { echo "$ring"; echo 'Cassandra ring is not healthy.' >&2; exit 1; }
  kubectl --context "$CONTEXT" -n cassandra exec "cassandra-$ordinal" -- \
    cqlsh -u cassandra -p "$CASSANDRA_PASSWORD" -e 'SELECT cluster_name FROM system.local;' >/dev/null
done
echo "Cassandra: three UN members and authenticated CQL on every replica PASS"

probe="infra-health-${RANDOM}"
trap 'kubectl --context "$CONTEXT" -n qdrant delete pod "$probe" --ignore-not-found --wait=false >/dev/null 2>&1 || true' EXIT
kubectl --context "$CONTEXT" -n qdrant run "$probe" --image=curlimages/curl:8.12.1 \
  --restart=Never --command -- sleep 600
kubectl --context "$CONTEXT" -n qdrant wait --for=condition=Ready "pod/$probe" --timeout=120s
for ordinal in 0 1 2; do
  kubectl --context "$CONTEXT" -n qdrant exec "$probe" -- \
    curl --fail --silent --show-error --max-time 15 -H "api-key: $QDRANT_API_KEY" \
    "http://qdrant-$ordinal.qdrant-headless.qdrant.svc.cluster.local:6333/cluster" | \
    "$INFRA_PYTHON" -c 'import json,sys; r=json.load(sys.stdin)["result"]; assert r["status"] == "enabled" and len(r["peers"]) == 3 and r["raft_info"]["leader"] is not None, r'
done
echo "Qdrant: three peers and an elected leader on every replica PASS"
if [[ "${ENABLE_MONITORING:-false}" == true ]]; then
  kubectl --context "$CONTEXT" -n monitoring rollout status deployment/monitoring-grafana --timeout=5m
  kubectl --context "$CONTEXT" -n monitoring rollout status statefulset/prometheus-monitoring-kube-prometheus-prometheus --timeout=5m
fi
kubectl --context "$CONTEXT" get nodes
kubectl --context "$CONTEXT" get pods -A
kubectl --context "$CONTEXT" get services -A
kubectl --context "$CONTEXT" get pv
kubectl --context "$CONTEXT" get pvc -A
