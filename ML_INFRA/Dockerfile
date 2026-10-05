FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .
COPY artifacts/candidate.json /models/model.json
ENV ML_ARTIFACT_PATH=/models/model.json
EXPOSE 8000
CMD ["uvicorn", "ml_infra.serve:app", "--host", "0.0.0.0", "--port", "8000"]
