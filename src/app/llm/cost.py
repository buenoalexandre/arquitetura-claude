"""Estimativa de custo por chamada.

Preços de referência em USD por 1 milhão de tokens (tabela de 2026-09). Revise a cada
atualização de modelo — a fonte oficial é a página de preços do provedor.
"""

from __future__ import annotations

PRICING_PER_MTOK: dict[str, tuple[float, float]] = {
    # modelo: (entrada, saída)
    "claude-fable-5-1": (10.00, 50.00),
    "claude-opus-5-5": (4.00, 20.00),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-haiku-4-5": (1.00, 5.00),
}


def estimate_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    input_price, output_price = PRICING_PER_MTOK.get(model, (0.0, 0.0))
    cost = (input_tokens * input_price + output_tokens * output_price) / 1_000_000
    return round(cost, 6)
