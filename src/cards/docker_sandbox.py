"""
Более строгий sandbox на основе Docker.

Если Docker доступен — код выполняется в изолированном контейнере:
- Без сети
- С ограничением по памяти и CPU
- С таймаутом
- Read-only файловая система (кроме /tmp)

Если Docker недоступен — используется обычный subprocess sandbox.
"""

import subprocess
import tempfile
import os
import shutil
from typing import Dict, Any, Optional
from src.cards.sandbox import run_in_sandbox, SandboxResult


def is_docker_available() -> bool:
    """Проверяет, доступен ли Docker"""
    if not shutil.which("docker"):
        return False
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def run_in_docker_sandbox(
    code: str,
    timeout: int = 15,
    memory_limit: str = "128m",
    cpus: str = "0.5"
) -> SandboxResult:
    """
    Выполняет код внутри временного Docker-контейнера.
    """
    if not is_docker_available():
        print("⚠️ Docker недоступен, используем обычный subprocess sandbox")
        return run_in_sandbox(code, timeout=timeout)

    with tempfile.TemporaryDirectory() as tmpdir:
        code_file = os.path.join(tmpdir, "code.py")
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(code)

        # Запускаем контейнер
        # --network none  — без сети
        # --memory        — лимит памяти
        # --cpus          — лимит CPU
        # --rm            — удалить после завершения
        # -v              — монтируем только код
        cmd = [
            "docker", "run",
            "--rm",
            "--network", "none",
            "--memory", memory_limit,
            "--cpus", cpus,
            "--read-only",
            "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
            "-v", f"{code_file}:/code.py:ro",
            "python:3.11-slim",
            "python", "/code.py"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode == 0:
                return SandboxResult(
                    success=True,
                    stdout=result.stdout.strip(),
                    stderr=result.stderr.strip()
                )
            else:
                return SandboxResult(
                    success=False,
                    stdout=result.stdout.strip(),
                    stderr=result.stderr.strip(),
                    error=f"Контейнер завершился с кодом {result.returncode}"
                )

        except subprocess.TimeoutExpired:
            return SandboxResult(
                success=False,
                error=f"Превышено время выполнения в Docker ({timeout} сек)"
            )
        except Exception as e:
            return SandboxResult(
                success=False,
                error=f"Ошибка Docker sandbox: {type(e).__name__}: {e}"
            )


def execute_card_in_docker(card, context: dict = None, timeout: int = 15) -> Dict[str, Any]:
    """Высокоуровневая функция выполнения карточки в Docker-sandbox"""
    code = getattr(card, "source_code", None)
    if not code:
        return {
            "success": False,
            "error": "У карточки отсутствует source_code"
        }

    result = run_in_docker_sandbox(code, timeout=timeout)

    return {
        "card_id": card.id,
        "card_name": card.name,
        "success": result.success,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "error": result.error,
        "sandbox": "docker" if is_docker_available() else "subprocess",
        "context": context or {}
    }
