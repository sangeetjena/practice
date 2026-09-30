#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
resolve_data_dir
"$INFRA_PYTHON" "$INFRA_DIR/scripts/data-path.py" prepare
mkdir -p "$INFRA_DIR/.state"
RENDERED_CONFIG="$INFRA_DIR/.state/kind-config.yaml"
"$INFRA_PYTHON" "$INFRA_DIR/scripts/data-path.py" render > "$RENDERED_CONFIG"
if kind get clusters | grep -qx local-platform; then
  echo "kind cluster local-platform already exists"
  for node in local-platform-control-plane local-platform-worker local-platform-worker2 local-platform-worker3; do
    status="$(docker inspect -f '{{.State.Status}}' "$node" 2>/dev/null || true)"
    if [[ "$status" == exited || "$status" == created ]]; then
      docker start "$node" >/dev/null
    fi
  done
else
  echo "Creating kind cluster local-platform"
  kind create cluster --name local-platform --config "$RENDERED_CONFIG"
fi

echo "Installing Calico v3.30.3 so Kubernetes NetworkPolicies are enforced"
kubectl --context "$CONTEXT" apply -f \
  https://raw.githubusercontent.com/projectcalico/calico/v3.30.3/manifests/calico.yaml
kubectl --context "$CONTEXT" wait --for=condition=Ready nodes --all --timeout=5m
kubectl --context "$CONTEXT" cluster-info
kubectl --context "$CONTEXT" -n kube-system rollout status daemonset/calico-node --timeout=5m
echo "Cluster is ready; host database data is under $DATA_DIR"