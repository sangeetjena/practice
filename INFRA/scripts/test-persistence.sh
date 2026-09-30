#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_credentials
resolve_data_dir
"$INFRA_PYTHON" "$INFRA_DIR/scripts/data-path.py" validate
bash "$INFRA_DIR/scripts/verify.sh"
CONTEXT=kind-local-platform
TEST_ID="infra-$(date +%s)-${RANDOM}${RANDOM}"
COLLECTION="infra_test_$(printf '%s' "$TEST_ID" | tr -cd '[:alnum:]' | tr '[:upper:]' '[:lower:]')"
STATE_FILE="$INFRA_DIR/.state/persistence-test-id"
mkdir -p "$INFRA_DIR/.state"
printf '%s\n' "$TEST_ID" > "$STATE_FILE"
cleanup() {
  kubectl --context "$CONTEXT" -n qdrant delete pod infra-qdrant-persistence-check \
    --ignore-not-found >/dev/null 2>&1 || true
}
trap cleanup EXIT

postgres_query() {
  kubectl --context "$CONTEXT" -n postgres exec citus-coordinator-0 -- \
    env PGPASSWORD="$POSTGRES_PASSWORD" psql -U postgres -d agentdb -tAc "$1"
}

timescale_query() {
  kubectl --context "$CONTEXT" -n timescale exec timescale-0 -- \
    env PGPASSWORD="$TIMESCALE_PASSWORD" psql -U postgres -d stock -tAc "$1"
}

redis_query() {
  kubectl --context "$CONTEXT" -n redis exec redis-0 -- redis-cli "$@"
}

cassandra_query() {
  kubectl --context "$CONTEXT" -n cassandra exec cassandra-0 -- \
    cqlsh -u cassandra --password "$CASSANDRA_PASSWORD" -k infra_lab -e "$1"
}

qdrant_request() {
  kubectl --context "$CONTEXT" -n qdrant exec infra-qdrant-persistence-check -- \
    curl --fail --silent --show-error -H "api-key: $QDRANT_API_KEY" "$@"
}

echo "Writing persistence marker $TEST_ID"
postgres_query "CREATE TABLE IF NOT EXISTS infra_persistence (id text PRIMARY KEY, value text NOT NULL);"
postgres_query "SELECT create_distributed_table('infra_persistence', 'id') WHERE NOT EXISTS (SELECT 1 FROM pg_dist_partition WHERE logicalrelid = 'infra_persistence'::regclass);"
postgres_query "INSERT INTO infra_persistence VALUES ('$TEST_ID', 'survives-cluster-recreation') ON CONFLICT (id) DO UPDATE SET value = EXCLUDED.value;"
POSTGRES_VALUE="$(postgres_query "SELECT value FROM infra_persistence WHERE id = '$TEST_ID'")"
[[ "$POSTGRES_VALUE" == survives-cluster-recreation ]]

timescale_query "CREATE TABLE IF NOT EXISTS infra_persistence (id text PRIMARY KEY, value text NOT NULL);"
timescale_query "INSERT INTO infra_persistence VALUES ('$TEST_ID', 'survives-cluster-recreation') ON CONFLICT (id) DO UPDATE SET value = EXCLUDED.value;"
TIMESCALE_VALUE="$(timescale_query "SELECT value FROM infra_persistence WHERE id = '$TEST_ID'")"
[[ "$TIMESCALE_VALUE" == survives-cluster-recreation ]]
redis_query SET "infra:persistence:$TEST_ID" survives-cluster-recreation >/dev/null
[[ "$(redis_query GET "infra:persistence:$TEST_ID")" == survives-cluster-recreation ]]
sleep 2  # AOF appendfsync everysec must flush before the cluster is destroyed.

kubectl --context "$CONTEXT" -n cassandra exec cassandra-0 -- \
  cqlsh -u cassandra --password "$CASSANDRA_PASSWORD" -e \
  "CREATE KEYSPACE IF NOT EXISTS infra_lab WITH replication = {'class':'SimpleStrategy','replication_factor':3};"
kubectl --context "$CONTEXT" -n cassandra exec cassandra-0 -- \
  cqlsh -u cassandra --password "$CASSANDRA_PASSWORD" -e \
  "CREATE TABLE IF NOT EXISTS infra_lab.persistence_check (id text PRIMARY KEY, value text);"
kubectl --context "$CONTEXT" -n cassandra exec cassandra-0 -- \
  cqlsh -u cassandra --password "$CASSANDRA_PASSWORD" -k infra_lab -e \
  "INSERT INTO persistence_check (id, value) VALUES ('$TEST_ID', 'survives-cluster-recreation');"
CASSANDRA_RESULT="$(cassandra_query "SELECT value FROM persistence_check WHERE id = '$TEST_ID';")"
grep -Fq survives-cluster-recreation <<< "$CASSANDRA_RESULT"

kubectl --context "$CONTEXT" -n qdrant run infra-qdrant-persistence-check \
  --image=curlimages/curl:8.12.1 --restart=Never --command -- sleep 1800
kubectl --context "$CONTEXT" -n qdrant wait --for=condition=Ready \
  pod/infra-qdrant-persistence-check --timeout=90s
qdrant_request -X PUT \
  "http://qdrant.qdrant.svc.cluster.local:6333/collections/$COLLECTION" \
  -H 'Content-Type: application/json' -d '{"vectors":{"size":2,"distance":"Cosine"},"shard_number":3,"replication_factor":2,"write_consistency_factor":2}' >/dev/null
qdrant_request "http://qdrant.qdrant.svc.cluster.local:6333/collections/$COLLECTION" | "$INFRA_PYTHON" -c 'import json,sys; p=json.load(sys.stdin)["result"]["config"]["params"]; assert p["shard_number"] == 3 and p["replication_factor"] == 2'
qdrant_request -X PUT \
  "http://qdrant.qdrant.svc.cluster.local:6333/collections/$COLLECTION/points?wait=true" \
  -H 'Content-Type: application/json' \
  -d "{\"points\":[{\"id\":1,\"vector\":[0.1,0.2],\"payload\":{\"test_id\":\"$TEST_ID\"}}]}" >/dev/null
QDRANT_RESULT="$(qdrant_request \
  "http://qdrant.qdrant.svc.cluster.local:6333/collections/$COLLECTION/points/1")"
grep -Fq "$TEST_ID" <<< "$QDRANT_RESULT"
kubectl --context "$CONTEXT" -n qdrant delete pod infra-qdrant-persistence-check --wait=true

echo "Destroying and recreating the kind cluster to verify host-backed data."
bash "$INFRA_DIR/scripts/destroy-cluster.sh"
for directory in \
  postgres/coordinator postgres/worker-0 postgres/worker-1 postgres/worker-2 \
  cassandra/node-0 cassandra/node-1 cassandra/node-2 \
  qdrant/node-0 qdrant/node-1 qdrant/node-2 \
  timescale redis; do
  [[ -d "$DATA_DIR/$directory" ]]
done
bash "$INFRA_DIR/scripts/create-cluster.sh"
bash "$INFRA_DIR/scripts/deploy-infra.sh"
bash "$INFRA_DIR/scripts/verify.sh"

POSTGRES_VALUE="$(postgres_query "SELECT value FROM infra_persistence WHERE id = '$TEST_ID'")"
[[ "$POSTGRES_VALUE" == survives-cluster-recreation ]]
TIMESCALE_VALUE="$(timescale_query "SELECT value FROM infra_persistence WHERE id = '$TEST_ID'")"
[[ "$TIMESCALE_VALUE" == survives-cluster-recreation ]]
[[ "$(redis_query GET "infra:persistence:$TEST_ID")" == survives-cluster-recreation ]]
CASSANDRA_RESULT="$(cassandra_query "SELECT value FROM persistence_check WHERE id = '$TEST_ID';")"
grep -Fq survives-cluster-recreation <<< "$CASSANDRA_RESULT"
QDRANT_RESULT="$(kubectl --context "$CONTEXT" -n qdrant run infra-qdrant-persistence-check \
  --image=curlimages/curl:8.12.1 --restart=Never --rm -i --quiet --command -- \
  curl --fail --silent --show-error -H "api-key: $QDRANT_API_KEY" \
  "http://qdrant.qdrant.svc.cluster.local:6333/collections/$COLLECTION/points/1")"
grep -Fq "$TEST_ID" <<< "$QDRANT_RESULT"

echo "PostgreSQL persistence: PASS"
echo "Cassandra persistence: PASS"
echo "Qdrant persistence: PASS"
echo "TimescaleDB persistence: PASS"
echo "Redis AOF persistence: PASS"
rm -f "$STATE_FILE"
