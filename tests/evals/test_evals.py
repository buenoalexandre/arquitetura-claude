"""Avaliação de qualidade das respostas.

Dois modos:
- offline (padrão, roda no CI de todo PR): valida os datasets e os corretores contra as
  ``reference_output`` — garante que o harness funciona e que as referências estão corretas;
- live (``pytest -m live tests/evals``): chama o modelo real, exige taxa de aprovação mínima
  e grava um relatório em ``tests/evals/reports/``. Roda no workflow ``evals.yml``.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.container import build_container
from app.core.config import LLMSettings, Settings
from app.domain.models import Message
from app.llm.anthropic_provider import AnthropicProvider
from app.llm.provider import LLMRequest
from tests.evals.graders import EvalCase, grade

pytestmark = pytest.mark.evals

DATASETS = Path(__file__).parent / "datasets"
REPORTS = Path(__file__).parent / "reports"
MIN_PASS_RATE = float(os.environ.get("EVAL_MIN_PASS_RATE", "0.9"))


def load_cases() -> list[EvalCase]:
    cases = []
    for file in sorted(DATASETS.glob("*.jsonl")):
        for line in file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                cases.append(EvalCase(**json.loads(line)))
    return cases


CASES = load_cases()


def test_dataset_ids_are_unique() -> None:
    ids = [case.id for case in CASES]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.id)
def test_reference_outputs_pass_their_own_criteria(case: EvalCase) -> None:
    result = grade(case, case.reference_output)
    assert result.passed, result.failures


@pytest.mark.live
@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), reason="sem ANTHROPIC_API_KEY")
async def test_live_pass_rate() -> None:
    settings = Settings(env="test", llm=LLMSettings(provider="anthropic"))
    container = build_container(settings, AnthropicProvider(settings.llm.timeout_seconds))
    registry = container.chat_service.prompts

    results = []
    for case in CASES:
        prompt = registry.render(case.prompt, settings.prompts.default_variables)
        response = await container.llm.complete(
            LLMRequest(
                system=prompt.text,
                messages=[Message(role="user", content=case.input)],
                model=settings.llm.model,
                max_tokens=2000,
                effort="low",
            )
        )
        result = grade(case, response.text)
        results.append(
            {
                "id": case.id,
                "passed": result.passed,
                "failures": result.failures,
                "prompt_version": prompt.version,
                "output": response.text,
            }
        )

    pass_rate = sum(r["passed"] for r in results) / len(results)
    REPORTS.mkdir(exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    (REPORTS / f"eval-{stamp}.json").write_text(
        json.dumps(
            {"model": settings.llm.model, "pass_rate": pass_rate, "results": results},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    assert pass_rate >= MIN_PASS_RATE, f"taxa de aprovação {pass_rate:.0%} < {MIN_PASS_RATE:.0%}"
