SHELL := bash
.SHELLFLAGS := -euo pipefail -c
.ONESHELL:

PYTHON ?= python3
VENV_PYTHON := .venv/bin/python
SYMBOL ?= GOOGL
EPOCHS ?= 300
TEST_FILE ?= tests/predict.json
MODEL_URL ?= http://127.0.0.1:8000
KUBE_CONTEXT ?= kind-local-platform
KIND_CLUSTER ?= local-platform
NAMESPACE := logistic-regression

.PHONY: prerequisites train predict deploy diagnose expose status test

prerequisites:
	if [ ! -x "$(VENV_PYTHON)" ]; then $(PYTHON) -m venv .venv; fi
	if "$(VENV_PYTHON)" scripts/environment_ready.py; then
	  echo 'ML_INFRA virtual environment and packages are already ready.'
	else
	  "$(VENV_PYTHON)" -m pip install -e ".[serve,dev]"
	  "$(VENV_PYTHON)" scripts/environment_ready.py
	fi

train: prerequisites
	source .venv/bin/activate
	set -a
	if [ -f .env ]; then source .env; fi
	set +a
	: "$${ML_DATABASE_URL:?Set ML_DATABASE_URL in ML_INFRA/.env or environment}"
	: "$${ML_TIMESCALE_URL:?Set ML_TIMESCALE_URL in ML_INFRA/.env or environment}"
	python -m ml_infra.train --symbol "$(SYMBOL)" --epochs "$(EPOCHS)" --require-gpu --output artifacts/candidate.json

predict: prerequisites
	source .venv/bin/activate
	set -a
	if [ -f .env ]; then source .env; fi
	set +a
	: "$${ML_MODEL_TOKEN:?Set ML_MODEL_TOKEN in ML_INFRA/.env or environment}"
	python -m ml_infra.predict --file "$(TEST_FILE)" --url "$(MODEL_URL)"

deploy: prerequisites
	source .venv/bin/activate
	test -f artifacts/candidate.json || { echo 'Run make train first.' >&2; exit 1; }
	image_tag=$$(python -c 'import json; print(json.load(open("artifacts/candidate.json", encoding="utf-8"))["model_version"])')
	set -a
	if [ -f .env ]; then source .env; fi
	set +a
	: "$${ML_DATABASE_URL_IN_CLUSTER:?Set ML_DATABASE_URL_IN_CLUSTER}"
	: "$${ML_TIMESCALE_URL_IN_CLUSTER:?Set ML_TIMESCALE_URL_IN_CLUSTER}"
	: "$${ML_MODEL_TOKEN:?Set ML_MODEL_TOKEN}"
	kubectl --context "$(KUBE_CONTEXT)" apply -f ../INFRA/kubernetes/namespaces/namespaces.yaml
	kubectl --context "$(KUBE_CONTEXT)" apply -f ../INFRA/kubernetes/networking/policies/database-policies.yaml
	docker build -t "stock-model:$$image_tag" .
	kind load docker-image "stock-model:$$image_tag" --name "$(KIND_CLUSTER)"
	kubectl --context "$(KUBE_CONTEXT)" -n "$(NAMESPACE)" create secret generic stock-model-db-urls \
	  --from-literal=postgres_url="$$ML_DATABASE_URL_IN_CLUSTER" \
	  --from-literal=timescale_url="$$ML_TIMESCALE_URL_IN_CLUSTER" \
	  --from-literal=model_token="$$ML_MODEL_TOKEN" \
	  --dry-run=client -o yaml | kubectl --context "$(KUBE_CONTEXT)" apply -f - >/dev/null
	if ! helm upgrade --install stock-model ./helm/stock-model \
	  --kube-context "$(KUBE_CONTEXT)" --namespace "$(NAMESPACE)" \
	  --values ./helm/stock-model/values.yaml --set-string "image.tag=$$image_tag" \
	  --wait --timeout 10m; then
	  $(MAKE) diagnose
	  exit 1
	fi
	kubectl --context "$(KUBE_CONTEXT)" -n "$(NAMESPACE)" rollout status deployment/stock-model --timeout=10m
	$(MAKE) expose

diagnose:
	kubectl --context "$(KUBE_CONTEXT)" -n "$(NAMESPACE)" get deployment,pods,svc -o wide || true
	kubectl --context "$(KUBE_CONTEXT)" -n "$(NAMESPACE)" describe pods -l app=stock-model || true
	kubectl --context "$(KUBE_CONTEXT)" -n "$(NAMESPACE)" logs deployment/stock-model --all-containers=true --tail=80 || true
	kubectl --context "$(KUBE_CONTEXT)" -n "$(NAMESPACE)" get events --sort-by=.lastTimestamp || true

expose:
	@mkdir -p .state
	if [ -f .state/port-forward.pid ] && kill -0 "$$(cat .state/port-forward.pid)" 2>/dev/null; then
	  echo "Port forward already running on $(MODEL_URL)"
	else
	  nohup kubectl --context "$(KUBE_CONTEXT)" -n "$(NAMESPACE)" \
	    port-forward --address 127.0.0.1 svc/stock-model 8000:8000 \
	    >.state/port-forward.log 2>&1 </dev/null &
	  echo $$! >.state/port-forward.pid
	fi
	for attempt in 1 2 3 4 5 6 7 8 9 10; do
	  if curl -fsS "$(MODEL_URL)/health" 2>/dev/null; then echo; echo "Endpoint: $(MODEL_URL)/predict"; exit 0; fi
	  sleep 2
	done
	echo 'Port forward failed; inspect .state/port-forward.log' >&2
	exit 1

status:
	kubectl --context "$(KUBE_CONTEXT)" -n "$(NAMESPACE)" get deployment,pods,svc,endpoint

test: prerequisites
	source .venv/bin/activate
	python -m pytest -q
