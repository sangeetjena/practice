# Keep Beam versions aligned with requirements/beam.lock and pyproject.toml.
ARG LAUNCHER_IMAGE=gcr.io/dataflow-templates-base/python311-template-launcher-base:20250923_RC00
FROM ${LAUNCHER_IMAGE} AS template_launcher
FROM apache/beam_python3.11_sdk:2.69.0 AS dependencies
WORKDIR /opt/platform
COPY requirements/beam.lock /opt/platform/requirements.lock
RUN pip install --no-cache-dir -r requirements.lock
COPY shared /opt/platform/shared
COPY jobs /opt/platform/jobs
ENV PYTHONPATH=/opt/platform

FROM dependencies AS worker
ENTRYPOINT ["/opt/apache/beam/boot"]

FROM dependencies AS launcher
COPY --from=template_launcher /opt/google/dataflow/python_template_launcher /opt/google/dataflow/python_template_launcher
ENV FLEX_TEMPLATE_PYTHON_PY_FILE=/opt/platform/jobs/dataflow/main.py
ENTRYPOINT ["/opt/google/dataflow/python_template_launcher"]
