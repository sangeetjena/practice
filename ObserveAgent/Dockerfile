FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/ObserveAgent

WORKDIR /app
RUN useradd --create-home --uid 10001 observer
COPY pyproject.toml /app/pyproject.toml
RUN pip install --no-cache-dir "fastapi>=0.115,<1" "httpx>=0.27,<1" \
    "chromadb>=1,<2" "langgraph-checkpoint-sqlite>=3,<4" "langgraph>=1.1,<2" "openai>=2,<3" "pydantic>=2.9,<3" "uvicorn[standard]>=0.30,<1"
COPY . /app/ObserveAgent
RUN mkdir -p /data && chown -R observer:observer /data /app
USER observer
EXPOSE 8090
CMD ["python", "-m", "observe_agent.api"]
