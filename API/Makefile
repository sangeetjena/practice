.PHONY: install run test lint feed observe-agent docker-build docker-run

install:
	python -m pip install -e '.[dev]'

run:
	uvicorn api_interview_lab.server.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

lint:
	ruff check .

feed:
	python scripts/load_feed.py

observe-agent:
	PYTHONPATH=src:ObserveAgent python -m observe_agent.api

docker-build:
	docker build -t api-interview-lab:local .

docker-run:
	docker run --rm -p 8000:8000 api-interview-lab:local
