"""Rastreamento distribuído com OpenTelemetry (vendor-neutral).

Por padrão os spans ficam em memória/no-op. Para exportar, instale
``opentelemetry-exporter-otlp`` e defina ``OTEL_EXPORTER_OTLP_ENDPOINT`` (Langfuse, Jaeger,
Grafana Tempo, Datadog e outros aceitam OTLP).
"""

from __future__ import annotations

import os
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

_configured = False


def configure_tracing(service_name: str, enabled: bool) -> None:
    global _configured  # noqa: PLW0603 - configuração única por processo
    if _configured or not enabled:
        return
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import (  # noqa: PLC0415
                OTLPSpanExporter,
            )

            provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
        except ImportError:  # exportador opcional
            pass
    trace.set_tracer_provider(provider)
    _configured = True


def get_tracer(name: str = "app") -> Any:
    return trace.get_tracer(name)
