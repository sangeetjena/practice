FROM python:3.11.13-slim-bookworm
# Dataproc mounts Spark and the JRE. Do not install pyspark or a JRE in this image.
RUN apt-get update && apt-get install -y --no-install-recommends procps tini libjemalloc2 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -g 1099 spark && useradd -u 1099 -g 1099 -m -d /home/spark spark
COPY requirements/cloud.lock /tmp/requirements.lock
RUN pip install --no-cache-dir -r /tmp/requirements.lock
COPY shared /opt/platform/shared
COPY jobs /opt/platform/jobs
ENV PYTHONPATH=/opt/platform
ENV PYSPARK_PYTHON=/usr/local/bin/python
USER spark
