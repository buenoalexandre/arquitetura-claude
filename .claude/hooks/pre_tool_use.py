"""Hook PreToolUse: guarda-corpos que rodam antes de cada ferramenta.

Instruções no CLAUDE.md orientam; hooks garantem. Tudo o que NUNCA pode acontecer fica aqui:
- Bash: bloqueia comandos destrutivos ou que exfiltram segredos;
- Edit/Write/MultiEdit: impede gravar segredos no código e editar arquivos .env.

Protocolo: recebe JSON no stdin; sair com código 2 bloqueia a chamada e envia o stderr ao Claude.
Teste manual:
    echo '{"tool_name": "Bash", "tool_input": {"command": "rm -rf /"}}' | python pre_tool_use.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import PurePath
from typing import Any

BLOCKED_COMMANDS: list[tuple[str, str]] = [
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

SECRET_PATTERNS: dict[str, str] = {
    "chave Anthropic": r"sk-ant-[A-Za-z0-9_\-]{20,}",
    "chave OpenAI": r"sk-(proj-)?[A-Za-z0-9]{32,}",
    "chave AWS": r"AKIA[0-9A-Z]{16}",
    "token GitHub": r"gh[pousr]_[A-Za-z0-9]{36,}",
    "chave privada": r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "token Slack": r"xox[baprs]-[A-Za-z0-9-]{10,}",
}

PROTECTED_FILES = re.compile(r"(^|[\\/])\.env(\.(?!example$)[\w.-]+)?$")
EDIT_TOOLS = {"Edit", "Write", "MultiEdit"}


def check_command(command: str) -> str | None:
    for pattern, reason in BLOCKED_COMMANDS:
        if re.search(pattern, command, re.IGNORECASE):
            return f"{reason}. Comando: {command}"
    return None


def check_edit(tool_input: dict[str, Any]) -> str | None:
    path = str(tool_input.get("file_path", ""))
    if path and PROTECTED_FILES.search(path):
        return (
            f"{PurePath(path).name} guarda segredos e não é editado pelo agente. "
            "Edite .env.example e peça ao usuário para atualizar o .env."
        )
    edits = tool_input.get("edits") or []
    texts = [str(tool_input.get(k, "")) for k in ("content", "new_string")]
    texts += [str(e.get("new_string", "")) for e in edits if isinstance(e, dict)]
    for label, pattern in SECRET_PATTERNS.items():
        if any(re.search(pattern, text) for text in texts):
            return f"o conteúdo parece conter uma {label}. Use variáveis de ambiente ou o cofre."
    return None


def main() -> int:
    payload = json.load(sys.stdin)
    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})
    reason = None
    if tool_name == "Bash":
        reason = check_command(str(tool_input.get("command", "")))
    elif tool_name in EDIT_TOOLS:
        reason = check_edit(tool_input)
    if reason:
        print(f"Bloqueado pelo hook pre_tool_use: {reason}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
