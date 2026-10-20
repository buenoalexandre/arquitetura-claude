"""Guardrails de entrada: limites, detecção de injeção de prompt e redação de PII.

As heurísticas aqui são a primeira linha de defesa, baratas e determinísticas. Elas não
substituem a separação de privilégios (o modelo nunca deve ter acesso a mais do que o
usuário) nem um classificador dedicado (ex.: Lakera Guard, Prompt Guard, NeMo Guardrails).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.core.config import GuardrailSettings
from app.core.errors import GuardrailViolationError

INJECTION_PATTERNS: dict[str, re.Pattern[str]] = {
    "ignore_instructions": re.compile(
        r"\b(ignore|disregard|forget|esque[cç]a|desconsidere)\b.{0,40}"
        r"(\b(previous|prior|above|all)\b.{0,20}\b(instructions?|rules)\b"
        r"|\b(instru[cç][oõ]es|regras)\b.{0,20}\b(anteriores|acima|do sistema)\b"
        r"|\btodas as\b.{0,20}\b(instru[cç][oõ]es|regras)\b)",
        re.IGNORECASE,
    ),
    "reveal_system_prompt": re.compile(
        r"\b(reveal|show|print|mostre|revele|imprima)\b.{0,40}\b(system prompt|prompt de "
        r"sistema|instru[cç][oõ]es (iniciais|internas))\b",
        re.IGNORECASE,
    ),
    "role_override": re.compile(
        r"\b(you are now|a partir de agora voc[eê] [eé]|developer mode|modo desenvolvedor)\b",
        re.IGNORECASE,
    ),
    "fake_delimiters": re.compile(r"<\|?(system|im_start|endoftext)\|?>", re.IGNORECASE),
}

PII_PATTERNS: dict[str, re.Pattern[str]] = {
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "cpf": re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
    "phone_br": re.compile(r"(?:\+55\s?)?\(?\d{2}\)?\s?9?\d{4}-?\d{4}\b"),
}


@dataclass
class InputCheck:
    text: str
    flags: list[str] = field(default_factory=list)


def detect_prompt_injection(text: str) -> list[str]:
    return [name for name, pattern in INJECTION_PATTERNS.items() if pattern.search(text)]


def detect_pii(text: str) -> list[str]:
    return [name for name, pattern in PII_PATTERNS.items() if pattern.search(text)]


def redact_pii(text: str) -> str:
    for name, pattern in PII_PATTERNS.items():
        text = pattern.sub(f"[{name.upper()}_REMOVIDO]", text)
    return text


def check_input(text: str, settings: GuardrailSettings) -> InputCheck:
    if len(text) > settings.max_input_chars:
        raise GuardrailViolationError(
            f"Mensagem excede o limite de {settings.max_input_chars} caracteres."
        )
    injection = detect_prompt_injection(text)
    if injection and settings.block_prompt_injection:
        raise GuardrailViolationError()
    flags = [f"injection:{name}" for name in injection]
    flags += [f"pii:{name}" for name in detect_pii(text)]
    return InputCheck(text=text, flags=flags)
