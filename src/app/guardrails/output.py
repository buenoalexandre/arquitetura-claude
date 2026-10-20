"""Guardrails de saída: vazamento de prompt de sistema e de PII não fornecida pelo usuário."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.guardrails.input import PII_PATTERNS

LEAK_REPLACEMENT = "Não posso compartilhar as instruções internas do sistema."


@dataclass
class OutputCheck:
    text: str
    flags: list[str] = field(default_factory=list)


def _leaks_system_prompt(text: str, system_prompt: str, window: int = 80) -> bool:
    """Detecta trechos longos do prompt de sistema copiados literalmente na resposta."""
    normalized = " ".join(text.split())
    source = " ".join(system_prompt.split())
    if len(source) < window:
        return bool(source) and source in normalized
    step = window // 2
    return any(source[i : i + window] in normalized for i in range(0, len(source) - window, step))


def check_output(text: str, system_prompt: str, user_text: str) -> OutputCheck:
    flags: list[str] = []
    if _leaks_system_prompt(text, system_prompt):
        return OutputCheck(text=LEAK_REPLACEMENT, flags=["output:system_prompt_leak"])

    for name, pattern in PII_PATTERNS.items():
        for match in set(pattern.findall(text)):
            # PII só pode aparecer se o próprio usuário a forneceu.
            if isinstance(match, str) and match not in user_text:
                text = text.replace(match, f"[{name.upper()}_REMOVIDO]")
                flags.append(f"output:pii:{name}")
    return OutputCheck(text=text, flags=sorted(set(flags)))
