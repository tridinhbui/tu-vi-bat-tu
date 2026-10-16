"""CalculationTrace: every computed value records how it was obtained."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TraceStep:
    id: str
    description: str
    inputs: dict[str, Any]
    result: Any
    rule: str | None = None  # rule/table id used, for provenance


@dataclass
class Trace:
    steps: list[TraceStep] = field(default_factory=list)

    def add(self, id: str, description: str, inputs: dict[str, Any], result: Any, rule: str | None = None):
        self.steps.append(TraceStep(id, description, inputs, result, rule))
        return result

    def get(self, id: str) -> TraceStep:
        return next(s for s in self.steps if s.id == id)
