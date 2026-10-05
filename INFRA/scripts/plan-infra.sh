#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_credentials
if ! kind get clusters | grep -qx local-platform; then
  echo "kind cluster local-platform does not exist. Run 'make create' first." >&2
  exit 1
fi
terraform -chdir="$INFRA_DIR/terraform" init -input=false
terraform -chdir="$INFRA_DIR/terraform" plan -input=false
