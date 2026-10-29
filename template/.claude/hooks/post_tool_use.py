"""Hook PostToolUse (Edit/Write/MultiEdit): formata arquivos Python editados com ruff.

Nunca bloqueia: se o ruff não estiver instalado, apenas segue em frente.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys


def main() -> int:
    payload = json.load(sys.stdin)
    path = str(payload.get("tool_input", {}).get("file_path", ""))
    ruff = shutil.which("ruff")
    if path.endswith(".py") and ruff:
        subprocess.run([ruff, "format", "--quiet", path], check=False)  # noqa: S603
        subprocess.run([ruff, "check", "--fix", "--quiet", path], check=False)  # noqa: S603
    return 0


if __name__ == "__main__":
    sys.exit(main())
