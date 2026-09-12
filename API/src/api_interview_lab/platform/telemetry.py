"""OpenTelemetry traces/metrics plus trace-correlated, credential-free request logs."""
import json
import logging
import time
import uuid

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

log = logging.getLogger("platform.requests")


def instrument(app, service, enabled):
    resource = Resource.create({"service.name": service, "service.namespace": "commerce"})
    meter_provider = MeterProvider(resource=resource)
    if enabled:
        metric_reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(timeout=2), export_interval_millis=5_000
        )
        meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
        provider = TracerProvider(resource=resource)
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(timeout=2)))
        app.state.tracer_provider = provider
        app.state.meter_provider = meter_provider
        FastAPIInstrumentor.instrument_app(app, tracer_provider=provider,
                                           excluded_urls="health/live,health/ready,metrics")
    meter = metrics.get_meter("api_interview_lab.platform", meter_provider=meter_provider)
    count = meter.create_counter(
        "api_requests", unit="{request}", description="Completed API requests"
    )
    latency = meter.create_histogram(
        "api_request_duration", unit="s", description="API request latency"
    )
    app.state.request_counter = count
    app.state.request_latency = latency

    @app.middleware("http")
    async def observe(request, call_next):
        started = time.perf_counter()
        request_id = uuid.uuid4().hex  # never log caller-controlled identifiers verbatim
        request.state.request_id = request_id
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Content-Type-Options"] = "nosniff"
            return response
        finally:
            route = getattr(request.scope.get("route"), "path", "unmatched")
            if route not in {"/metrics", "/health/live", "/health/ready"}:
                method = request.method if request.method in {
                    "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"} else "OTHER"
                elapsed = time.perf_counter() - started
                attributes = {
                    "service": service,
                    "route": route,
                    "method": method,
                    "status": str(status),
                }
                count.add(1, attributes)
                latency.record(elapsed, attributes)
                context = trace.get_current_span().get_span_context()
                log.info(json.dumps({"service": service, "route": route, "status": status,
                                     "duration_ms": round(elapsed * 1000, 2),
                                     "request_id": request_id,
                                     "trace_id": format(context.trace_id, "032x")}))
