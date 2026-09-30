SHELL := bash
.SHELLFLAGS := -euo pipefail -c

.PHONY: prerequisites create start infra deploy status network-status verify test-network test-persistence expose-postgres expose-cassandra expose-qdrant expose-timescale expose-redis expose-all stop destroy clean-data reset

prerequisites:
	bash ./scripts/check-prerequisites.sh

create: prerequisites
	bash ./scripts/create-cluster.sh

start: prerequisites
	bash ./scripts/start-cluster.sh

infra:
	bash ./scripts/deploy-infra.sh

deploy:
	$(MAKE) create
	$(MAKE) infra
	$(MAKE) verify

status:
	kubectl --context kind-local-platform get nodes
	kubectl --context kind-local-platform get pods -A
	kubectl --context kind-local-platform get services -A
	kubectl --context kind-local-platform get statefulsets -A
	kubectl --context kind-local-platform get pv
	kubectl --context kind-local-platform get pvc -A
	kubectl --context kind-local-platform get networkpolicy -A
	helm --kube-context kind-local-platform list -A

network-status:
	kubectl --context kind-local-platform get services -A
	kubectl --context kind-local-platform get endpoints -A
	kubectl --context kind-local-platform get networkpolicy -A

verify:
	bash ./scripts/verify.sh

test-network:
	bash ./scripts/test-network.sh

test-persistence:
	bash ./scripts/test-persistence.sh

expose-postgres:
	bash ./scripts/expose-services.sh postgres

expose-cassandra:
	bash ./scripts/expose-services.sh cassandra

expose-qdrant:
	bash ./scripts/expose-services.sh qdrant

expose-timescale:
	bash ./scripts/expose-services.sh timescale

expose-redis:
	bash ./scripts/expose-services.sh redis

.PHONY: expose-monitoring test-static
expose-monitoring:
	bash ./scripts/expose-services.sh monitoring

test-static:
	python3 -m unittest discover -s tests -v

expose-all:
	bash ./scripts/expose-services.sh all

stop:
	bash ./scripts/stop-cluster.sh

destroy:
	bash ./scripts/destroy-cluster.sh

clean-data:
	bash ./scripts/clean-data.sh

reset:
	bash ./scripts/reset.sh
