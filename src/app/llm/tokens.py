"""Estimativa local de tokens.

Heurística (~4 caracteres por token) usada para orçamentos de contexto sem chamada de rede.
Para contagem exata, use o endpoint de contagem de tokens do provedor.
"""

from __future__ import annotations


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)
