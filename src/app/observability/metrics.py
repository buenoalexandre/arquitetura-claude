"""Métricas em processo (contadores e histogramas) para componentes de IA.

Implementação mínima e sem dependências, exposta em ``GET /v1/metrics``. Em produção,
substitua por OpenTelemetry Metrics ou Prometheus mantendo os mesmos nomes de métrica.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from dataclasses import dataclass, field

LabelKey = tuple[tuple[str, str], ...]


def _key(labels: dict[str, str]) -> LabelKey:
    return tuple(sorted(labels.items()))


@dataclass
class _Histogram:
    count: int = 0
    total: float = 0.0
    maximum: float = 0.0
    values: list[float] = field(default_factory=list)

    def observe(self, value: float) -> None:
        self.count += 1
        self.total += value
        self.maximum = max(self.maximum, value)
        self.values.append(value)
        if len(self.values) > 1000:  # janela deslizante para percentis
            self.values = self.values[-1000:]

    def percentile(self, p: float) -> float:
        if not self.values:
            return 0.0
        ordered = sorted(self.values)
        index = min(len(ordered) - 1, round(p / 100 * (len(ordered) - 1)))
        return ordered[index]


class Metrics:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counters: dict[str, dict[LabelKey, float]] = defaultdict(lambda: defaultdict(float))
        self._histograms: dict[str, dict[LabelKey, _Histogram]] = defaultdict(
            lambda: defaultdict(_Histogram)
        )

    def increment(self, name: str, value: float = 1.0, **labels: str) -> None:
        with self._lock:
            self._counters[name][_key(labels)] += value

    def observe(self, name: str, value: float, **labels: str) -> None:
        with self._lock:
            self._histograms[name][_key(labels)].observe(value)

    def counter_value(self, name: str, **labels: str) -> float:
        return self._counters.get(name, {}).get(_key(labels), 0.0)

    def snapshot(self) -> dict[str, list[dict[str, object]]]:
        with self._lock:
            result: dict[str, list[dict[str, object]]] = {}
            for name, series in self._counters.items():
                result[name] = [{"labels": dict(k), "value": v} for k, v in series.items()]
            for name, hseries in self._histograms.items():
                result[name] = [
                    {
                        "labels": dict(k),
                        "count": h.count,
                        "avg": h.total / h.count if h.count else 0.0,
                        "p50": h.percentile(50),
                        "p95": h.percentile(95),
                        "max": h.maximum,
                    }
                    for k, h in hseries.items()
                ]
            return result
