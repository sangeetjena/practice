#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
resolve_data_dir
docker info >/dev/null
nodes="$(docker ps -aq --filter "label=io.x-k8s.kind.cluster=$CLUSTER_NAME")"
if [[ -n "$nodes" ]]; then
  echo "Destroy all lab node containers before cleaning database data." >&2
  exit 1
fi
"$INFRA_PYTHON" "$INFRA_DIR/scripts/data-path.py" validate
echo "Permanently delete database files under $DATA_DIR."
read -r -p "Type DELETE DATABASE DATA to continue: " confirmation
[[ "$confirmation" == 'DELETE DATABASE DATA' ]] || { echo 'Cancelled.'; exit 1; }
"$INFRA_PYTHON" "$INFRA_DIR/scripts/data-path.py" clean
echo "Database data removed."
