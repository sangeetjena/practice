#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
docker info >/dev/null
kind delete cluster --name "$CLUSTER_NAME"
echo 'Cluster deleted. Host database data and Terraform state are preserved.'
