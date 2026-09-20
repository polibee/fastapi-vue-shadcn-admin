from collections import defaultdict
from threading import Lock
from typing import Any


class MetricsRegistry:
    def __init__(self) -> None:
        self._lock = Lock()
        self._counters: dict[str, int] = defaultdict(int)
        self._histograms: dict[str, list[float]] = defaultdict(list)

    @staticmethod
    def _key(name: str, tags: dict[str, str] | None) -> str:
        suffix = "|" + ",".join(f"{key}={value}" for key, value in sorted((tags or {}).items())) if tags else ""
        return name + suffix

    def increment(self, name: str, *, tags: dict[str, str] | None = None, value: int = 1) -> None:
        with self._lock:
            self._counters[self._key(name, tags)] += value

    def observe(self, name: str, value: float, *, tags: dict[str, str] | None = None) -> None:
        with self._lock:
            self._histograms[self._key(name, tags)].append(float(value))

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "counters": dict(self._counters),
                "histograms": {
                    key: {
                        "count": len(values),
                        "sum": sum(values),
                        "min": min(values) if values else None,
                        "max": max(values) if values else None,
                    }
                    for key, values in self._histograms.items()
                },
            }

    def reset(self) -> None:
        with self._lock:
            self._counters.clear()
            self._histograms.clear()


metrics = MetricsRegistry()
