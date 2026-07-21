"""
Безопасный sandbox для выполнения кода из Data Cards.

Подходы:
1. Запуск в отдельном процессе через subprocess
2. Таймаут выполнения
3. Захват stdout / stderr
4. Ограничение по времени и базовые проверки безопасности
"""

import subprocess
import tempfile
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import textwrap


class SandboxResult:
    def __init__(self, success: bool, stdout: str = "", stderr: str = "", error: str = None):
        self.success = success
        self.stdout = stdout
        self.stderr = stderr
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "error": self.error
        }


def _is_code_dangerous(code: str) -> Optional[str]:
    """Простая статическая проверка на явно опасные конструкции"""
    dangerous_patterns = [
        "os.system",
        "subprocess",
        "__import__",
        "eval(",
        "exec(",
        "open(",
        "pathlib",
        "shutil",
        "socket",
        "requests",
        "urllib",
        "pickle",
        "marshal",
        "ctypes",
        "sys.exit",
        "while True",
    ]
    
    code_lower = code.lower()
    for pattern in dangerous_patterns:
        if pattern.lower() in code_lower:
            return f"Обнаружена потенциально опасная конструкция: {pattern}"
    return None


def run_in_sandbox(
    code: str,
    timeout: int = 10,
    allow_dangerous: bool = False
) -> SandboxResult:
    """
    Безопасно выполняет Python-код в отдельном процессе.
    
    Args:
        code: исходный код
        timeout: максимальное время выполнения в секундах
        allow_dangerous: разрешить потенциально опасный код (не рекомендуется)
    """
    
    # 1. Статическая проверка
    if not allow_dangerous:
        danger = _is_code_dangerous(code)
        if danger:
            return SandboxResult(
                success=False,
                error=f"Код отклонён системой безопасности: {danger}"
            )
    
    # 2. Создаём временный файл
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False,
        encoding="utf-8"
    ) as tmp:
        # Оборачиваем код, чтобы можно было перехватывать вывод
        wrapped_code = textwrap.dedent(f"""
            import sys
            from io import StringIO
            
            # Перехватываем stdout
            old_stdout = sys.stdout
            sys.stdout = mystdout = StringIO()
            
            try:
            {textwrap.indent(code, '    ')}
            except Exception as e:
                print(f"RUNTIME_ERROR: {{type(e).__name__}}: {{e}}")
            finally:
                sys.stdout = old_stdout
                print(mystdout.getvalue())
        """)
        tmp.write(wrapped_code)
        tmp_path = tmp.name
    
    try:
        # 3. Запускаем в отдельном процессе
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=tempfile.gettempdir()  # Запускаем не в проекте
        )
        
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        
        if result.returncode == 0:
            return SandboxResult(
                success=True,
                stdout=stdout,
                stderr=stderr
            )
        else:
            return SandboxResult(
                success=False,
                stdout=stdout,
                stderr=stderr,
                error=f"Процесс завершился с кодом {result.returncode}"
            )
            
    except subprocess.TimeoutExpired:
        return SandboxResult(
            success=False,
            error=f"Превышено время выполнения ({timeout} сек)"
        )
    except Exception as e:
        return SandboxResult(
            success=False,
            error=f"Ошибка sandbox: {type(e).__name__}: {e}"
        )
    finally:
        # 4. Удаляем временный файл
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def execute_card_code(card, context: dict = None, timeout: int = 10) -> Dict[str, Any]:
    """
    Высокоуровневая функция для выполнения кода карточки.
    """
    code = getattr(card, "source_code", None)
    if not code:
        return {
            "success": False,
            "error": "У карточки отсутствует source_code"
        }
    
    result = run_in_sandbox(code, timeout=timeout)
    
    return {
        "card_id": card.id,
        "card_name": card.name,
        "success": result.success,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "error": result.error,
        "context": context or {}
    }
