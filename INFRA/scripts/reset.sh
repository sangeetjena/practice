#!/usr/bin/env bash
set -euo pipefail

INFRA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
bash "$INFRA_DIR/scripts/check-prerequisites.sh"
if [[ ! -f "$INFRA_DIR/.env" ]]; then
  echo "Missing $INFRA_DIR/.env. Configure local credentials before resetting." >&2
  exit 1
fi
set -a
source "$INFRA_DIR/.env"
set +a
for variable_name in POSTGRES_PASSWORD CASSANDRA_PASSWORD QDRANT_API_KEY; do
  if [[ -z "${!variable_name:-}" || "${!variable_name}" == replace-* ]]; then
    echo "$variable_name must be set in .env before resetting." >&2
    exit 1
  fi
done

echo "This destroys the cluster and permanently deletes all database data."
read -r -p "Type RESET DATABASE DATA AND CLUSTER to continue: " confirmation
if [[ "$confirmation" != "RESET DATABASE DATA AND CLUSTER" ]]; then
  echo "Cancelled; nothing was changed."
  exit 1
fi
bash "$INFRA_DIR/scripts/destroy-cluster.sh"
printf 'DELETE DATABASE DATA\n' | bash "$INFRA_DIR/scripts/clean-data.sh"
bash "$INFRA_DIR/scripts/create-cluster.sh"
bash "$INFRA_DIR/scripts/deploy-infra.sh"
bash "$INFRA_DIR/scripts/verify.sh"