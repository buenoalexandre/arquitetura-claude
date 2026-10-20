"""Hook PreToolUse (Edit/Write): impede gravar segredos no código ou editar arquivos .env.

Sair com código 2 bloqueia a edição e devolve o motivo ao Claude.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import PurePath

SECRET_PATTERNS: dict[str, str] = {
    "chave Anthropic": r"sk-ant-[A-Za-z0-9_\-]{20,}",
    "chave OpenAI": r"sk-(proj-)?[A-Za-z0-9]{32,}",
    "chave AWS": r"AKIA[0-9A-Z]{16}",
    "token GitHub": r"gh[pousr]_[A-Za-z0-9]{36,}",
    "chave privada": r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "token Slack": r"xox[baprs]-[A-Za-z0-9-]{10,}",
}

PROTECTED_FILES = re.compile(r"(^|[\\/])\.env(\.(?!example$)[\w.-]+)?$")


def main() -> int:
    payload = json.load(sys.stdin)
    tool_input = payload.get("tool_input", {})
    path = str(tool_input.get("file_path", ""))
    if path and PROTECTED_FILES.search(path):
        print(
            f"Bloqueado: {PurePath(path).name} guarda segredos e não é editado pelo agente. "
            "Edite .env.example e peça ao usuário para atualizar o .env.",
            file=sys.stderr,
        )
        return 2

    edits = tool_input.get("edits") or []
    texts = [str(tool_input.get(k, "")) for k in ("content", "new_string")]
    texts += [str(e.get("new_string", "")) for e in edits if isinstance(e, dict)]
    for label, pattern in SECRET_PATTERNS.items():
        if any(re.search(pattern, text) for text in texts):
            print(
                f"Bloqueado: o conteúdo parece conter uma {label}. Use variáveis de ambiente "
                "ou o cofre de segredos.",
                file=sys.stderr,
            )
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
