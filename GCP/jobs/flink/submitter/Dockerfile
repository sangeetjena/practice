FROM python:3.11.13-slim-bookworm
WORKDIR /app
COPY jobs/flink/submitter/submit.py /app/submit.py
USER 10001:10001
ENTRYPOINT ["python", "/app/submit.py"]
