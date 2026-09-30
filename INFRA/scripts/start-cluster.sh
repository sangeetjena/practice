#!/usr/bin/env bash
set -euo pipefail

INFRA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
for node in local-platform-control-plane local-platform-worker local-platform-worker2 local-platform-worker3; do
  status="$(docker inspect -f '{{.State.Status}}' "$node" 2>/dev/null || true)"
  if [[ "$status" == exited || "$status" == created ]]; then
    docker start "$node" >/dev/null
  fi
done
bash "$INFRA_DIR/scripts/create-cluster.sh"