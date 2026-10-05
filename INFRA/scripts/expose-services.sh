#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
load_deployment_flags

forward() {
  local selected="$1"
  [[ "$selected" == postgres ]] && selected=citus
  [[ "$selected" == grafana || "$selected" == prometheus ]] && selected=monitoring
  if ! service_enabled "$selected"; then
    echo "$1 is disabled in INFRA/.env." >&2
    return 1
  fi
  case "$1" in
    postgres)
      kubectl --context "$CONTEXT" -n postgres port-forward --address 127.0.0.1 \
        svc/citus-coordinator "${POSTGRES_LOCAL_PORT:-5432}:5432"
      ;;
    cassandra)
      kubectl --context "$CONTEXT" -n cassandra port-forward --address 127.0.0.1 \
        svc/cassandra "${CASSANDRA_LOCAL_PORT:-9042}:9042"
      ;;
    qdrant)
      kubectl --context "$CONTEXT" -n qdrant port-forward --address 127.0.0.1 \
        svc/qdrant "${QDRANT_HTTP_LOCAL_PORT:-6333}:6333" \
        "${QDRANT_GRPC_LOCAL_PORT:-6334}:6334"
      ;;
    timescale)
      kubectl --context "$CONTEXT" -n timescale port-forward --address 127.0.0.1 \
        svc/timescale "${TIMESCALE_LOCAL_PORT:-5433}:5432"
      ;;
    redis)
      kubectl --context "$CONTEXT" -n redis port-forward --address 127.0.0.1 \
        svc/redis "${REDIS_LOCAL_PORT:-6379}:6379"
      ;;
    grafana)
      kubectl --context "$CONTEXT" -n monitoring port-forward --address 127.0.0.1 \
        svc/monitoring-grafana "${GRAFANA_LOCAL_PORT:-3000}:80"
      ;;
    prometheus)
      kubectl --context "$CONTEXT" -n monitoring port-forward --address 127.0.0.1 \
        svc/monitoring-kube-prometheus-prometheus "${PROMETHEUS_LOCAL_PORT:-9090}:9090"
      ;;
    *)
      echo "Usage: $0 {postgres|cassandra|qdrant|timescale|redis|grafana|prometheus|monitoring|all}" >&2
      return 2
      ;;
  esac
}

if [[ "${1:-}" != all && "${1:-}" != monitoring ]]; then
  forward "${1:-}"
  exit
fi

mkdir -p "$INFRA_DIR/.state"
pids=()
services=()
if [[ "${1:-}" == monitoring ]]; then
  services=(grafana prometheus)
else
  for service in postgres cassandra qdrant timescale redis; do
    selected="$service"
    [[ "$selected" == postgres ]] && selected=citus
    if service_enabled "$selected"; then
      services+=("$service")
    fi
  done
  if service_enabled monitoring; then
    services+=(grafana prometheus)
  fi
fi
if [[ "${#services[@]}" == 0 ]]; then
  echo "No services are enabled in INFRA/.env." >&2
  exit 1
fi
for service in "${services[@]}"; do
  bash "$0" "$service" >"$INFRA_DIR/.state/port-forward-$service.log" 2>&1 &
  pids+=("$!")
done
stop_forwards() {
  for pid in "${pids[@]}"; do
    kill "$pid" 2>/dev/null || true
  done
}
trap stop_forwards INT TERM EXIT
sleep 2
for index in "${!pids[@]}"; do
  if ! kill -0 "${pids[$index]}" 2>/dev/null; then
    echo "A port-forward failed to start; inspect .state/port-forward-*.log" >&2
    exit 1
  fi
done
echo "Port-forwards active for: ${services[*]}. Press Ctrl-C to stop."
while true; do
  for pid in "${pids[@]}"; do
    if ! kill -0 "$pid" 2>/dev/null; then
      echo "A port-forward exited; inspect .state/port-forward-*.log" >&2
      exit 1
    fi
  done
  sleep 1
done
