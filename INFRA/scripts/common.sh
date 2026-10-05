#!/usr/bin/env bash
# Shared configuration; sourcing this file performs no cluster mutations.
INFRA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INFRA_PYTHON="$INFRA_DIR/.venv/bin/python"
CONTEXT=kind-local-platform
CLUSTER_NAME=local-platform
if [[ -f "$INFRA_DIR/.env" ]]; then
  set -a
  source "$INFRA_DIR/.env"
  set +a
fi

resolve_data_dir() {
  if [[ ! -x "$INFRA_PYTHON" ]]; then
    echo "INFRA Python environment is missing. Run 'make setup' from INFRA/." >&2
    return 1
  fi
  local path="${INFRA_DATA_DIR:-$INFRA_DIR/data}"
  if [[ "$path" =~ ^([A-Za-z]):/(.*)$ ]] && [[ -n "${WSL_DISTRO_NAME:-}" ]]; then
    path="/mnt/${BASH_REMATCH[1],,}/${BASH_REMATCH[2]}"
  fi
  if [[ "$path" != /* && "$path" != [A-Za-z]:/* ]]; then
    path="$INFRA_DIR/$path"
  fi
  if command -v cygpath >/dev/null 2>&1 && [[ -n "${MSYSTEM:-}" ]]; then
    path="$(cygpath -am "$path")"
  fi
  DATA_DIR="$("$INFRA_PYTHON" -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).resolve().as_posix())' "$path")"
  export DATA_DIR
}

load_deployment_flags() {
  local service name value default
  for service in citus cassandra qdrant timescale redis monitoring; do
    name="ENABLE_${service^^}"
    default=true
    [[ "$service" == monitoring ]] && default=false
    value="${!name:-$default}"
    if [[ "$value" != true && "$value" != false ]]; then
      echo "$name must be true or false in INFRA/.env." >&2
      return 1
    fi
    printf -v "$name" '%s' "$value"
    export "$name"
    export "TF_VAR_enable_${service}=$value"
  done
}

service_enabled() {
  local name="ENABLE_${1^^}"
  [[ "${!name:-false}" == true ]]
}

require_credentials() {
  load_deployment_flags || return 1
  local service name
  for service in citus cassandra qdrant timescale redis monitoring; do
    service_enabled "$service" || continue
    case "$service" in
      citus) name=POSTGRES_PASSWORD ;;
      cassandra) name=CASSANDRA_PASSWORD ;;
      qdrant) name=QDRANT_API_KEY ;;
      timescale) name=TIMESCALE_PASSWORD ;;
      redis) name=REDIS_PASSWORD ;;
      monitoring) name=GRAFANA_PASSWORD ;;
    esac
    if [[ -z "${!name:-}" || "${!name}" == replace-* ]]; then
      echo "$name must be configured in INFRA/.env when $service is enabled." >&2
      return 1
    fi
  done
  export TF_VAR_postgres_password="${POSTGRES_PASSWORD:-}"
  export TF_VAR_cassandra_password="${CASSANDRA_PASSWORD:-}"
  export TF_VAR_qdrant_api_key="${QDRANT_API_KEY:-}"
  export TF_VAR_timescale_password="${TIMESCALE_PASSWORD:-}"
  export TF_VAR_redis_password="${REDIS_PASSWORD:-}"
  export TF_VAR_grafana_password="${GRAFANA_PASSWORD:-}"
}
