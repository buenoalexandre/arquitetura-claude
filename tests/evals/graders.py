"""Corretores (graders) determinísticos para avaliação de respostas do modelo.

Corretores determinísticos são baratos, reprodutíveis e devem ser a primeira escolha. Use
LLM-como-juiz apenas para critérios subjetivos (tom, completude), sempre com rubrica
explícita e calibrado contra notas humanas (ver docs/ai/evaluation.md).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvalCase:
    id: str
    prompt: str
    input: str
    criteria: dict[str, Any]
    reference_output: str
    tags: list[str] = field(default_factory=list)


@dataclass
class GradeResult:
    case_id: str
    passed: bool
    failures: list[str]


def grade(case: EvalCase, output: str) -> GradeResult:
    failures: list[str] = []
    criteria = case.criteria
    lowered = output.lower()

    for term in criteria.get("must_contain", []):
        if term.lower() not in lowered:
            failures.append(f"deveria conter '{term}'")
    for term in criteria.get("must_not_contain", []):
        if term.lower() in lowered:
            failures.append(f"não deveria conter '{term}'")
    if (pattern := criteria.get("regex")) and not re.search(pattern, output):
        failures.append(f"não casa com /{pattern}/")
    if (max_chars := criteria.get("max_chars")) and len(output) > max_chars:
        failures.append(f"excede {max_chars} caracteres ({len(output)})")
    if (max_sentences := criteria.get("max_sentences")) is not None:
        sentences = [s for s in re.split(r"[.!?]+\s", output.strip()) if s]
        if len(sentences) > max_sentences:
            failures.append(f"excede {max_sentences} frases ({len(sentences)})")

    return GradeResult(case_id=case.id, passed=not failures, failures=failures)
