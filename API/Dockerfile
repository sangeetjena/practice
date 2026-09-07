FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build
COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip wheel --wheel-dir /wheels .

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=container \
    DATABASE_PATH=/app/data/orders.db

RUN groupadd --system app && useradd --system --gid app --home /app app
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN python -m pip install --no-cache-dir /wheels/* && rm -rf /wheels
COPY --chown=app:app feeds ./feeds
COPY --chown=app:app scripts ./scripts
RUN mkdir -p /app/data && chown app:app /app/data && \
    python scripts/load_feed.py --database /app/data/orders.db

USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/live')"

CMD ["uvicorn", "api_interview_lab.server.main:app", "--host", "0.0.0.0", "--port", "8000"]

