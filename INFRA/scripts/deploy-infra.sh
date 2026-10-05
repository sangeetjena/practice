#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_credentials
if ! kind get clusters | grep -qx local-platform; then
  echo "kind cluster local-platform does not exist. Run 'make create' first." >&2
  exit 1
fi

mkdir -p "$INFRA_DIR/.state"

kubectl --context kind-local-platform apply -f "$INFRA_DIR/kubernetes/namespaces/namespaces.yaml"
kubectl --context kind-local-platform apply -f "$INFRA_DIR/kubernetes/storage/storage-classes.yaml"
kubectl --context kind-local-platform apply -f "$INFRA_DIR/kubernetes/storage/persistent-volumes.yaml"
kubectl --context kind-local-platform apply -f "$INFRA_DIR/kubernetes/networking/policies/database-policies.yaml"

echo "Initializing Terraform providers"
terraform -chdir="$INFRA_DIR/terraform" init -input=false
PLAN_FILE="$INFRA_DIR/.state/infra.tfplan"
terraform -chdir="$INFRA_DIR/terraform" plan -input=false -out="$PLAN_FILE"
terraform -chdir="$INFRA_DIR/terraform" apply -input=false -auto-approve "$PLAN_FILE"

if service_enabled citus; then
  kubectl --context kind-local-platform -n postgres rollout status statefulset/citus-coordinator --timeout=30m
  kubectl --context kind-local-platform -n postgres rollout status statefulset/citus-worker --timeout=30m
fi
if service_enabled cassandra; then
  kubectl --context kind-local-platform -n cassandra rollout status statefulset/cassandra --timeout=30m
fi
if service_enabled qdrant; then
  kubectl --context kind-local-platform -n qdrant rollout status statefulset/qdrant --timeout=20m
fi
if service_enabled timescale; then
  kubectl --context kind-local-platform -n timescale rollout status statefulset/timescale --timeout=20m
fi
if service_enabled redis; then
  kubectl --context kind-local-platform -n redis rollout status statefulset/redis --timeout=10m
fi
echo "Database infrastructure is ready."
