#!/usr/bin/env bash
set -euo pipefail

nodes=(
  local-platform-control-plane
  local-platform-worker
  local-platform-worker2
  local-platform-worker3
)
stopped=0
for node in "${nodes[@]}"; do
  status="$(docker inspect -f '{{.State.Status}}' "$node" 2>/dev/null || true)"
  if [[ "$status" == running ]]; then
    docker stop "$node" >/dev/null
    stopped=$((stopped + 1))
  fi
done
if ((stopped)); then
  echo "Paused $stopped kind node containers. Use 'make start' to resume them."
else
  echo "No running local-platform kind nodes found."
fi