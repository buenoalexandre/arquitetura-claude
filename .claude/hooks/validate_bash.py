"""Hook PreToolUse (Bash): bloqueia comandos destrutivos ou que exfiltram segredos.

Instruções no CLAUDE.md orientam; hooks garantem. Tudo o que NUNCA pode acontecer fica aqui.
Protocolo: recebe JSON no stdin; sair com código 2 bloqueia a chamada e envia o stderr ao Claude.
Teste manual: echo '{"tool_input": {"command": "rm -rf /"}}' | python validate_bash.py
"""

from __future__ import annotations

import json
import re
import sys

BLOCKED: list[tuple[str, str]] = [
    (r"\brm\s+-[a-z]*r[a-z]*f?\s+(/|~|\*|\.)(\s|$)", "remoção recursiva de diretório raiz/home"),
    (r"\bgit\s+push\b.*(--force|-f\b)", "push forçado reescreve o histórico remoto"),
    (r"\bgit\s+reset\s+--hard\b", "descarta alterações locais sem volta"),
    (r"\bgit\s+clean\s+-[a-z]*f", "apaga arquivos não rastreados"),
    (
        r"\b(cat|less|more|type|head|tail)\b[^|;&]*\.env(\s|$|\.(?!example))",
        "leitura de arquivo .env",
    ),
    (r"\b(printenv|env)\b\s*($|\|)", "despejo de variáveis de ambiente"),
    (r"(curl|wget)[^|]*\|\s*(ba|z)?sh\b", "execução de script remoto via pipe"),
    (r"\bchmod\s+(-R\s+)?777\b", "permissão 777"),
    (r"\b(mkfs|dd\s+if=|shutdown|reboot)\b", "comando de sistema destrutivo"),
    (r"--no-verify\b", "pular hooks de verificação do git"),
]


def check(command: str) -> str | None:
    for pattern, reason in BLOCKED:
        if re.search(pattern, command, re.IGNORECASE):
            return reason
    return None


def main() -> int:
    payload = json.load(sys.stdin)
    command = payload.get("tool_input", {}).get("command", "")
    reason = check(command)
    if reason:
        print(f"Bloqueado pelo hook validate_bash: {reason}. Comando: {command}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
