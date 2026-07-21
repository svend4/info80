"""
Экспорт Data Cards в формат marimo notebook.

marimo — реактивный Python notebook.
Эта интеграция позволяет:
1. Экспортировать карточку как .py файл в формате marimo
2. Открывать и дальше интерактивно работать с карточкой в marimo
"""

from pathlib import Path
from typing import Optional
from src.cards.base import DataCard
from datetime import datetime

EXPORT_DIR = Path("data/marimo_export")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def export_card_to_marimo(card: DataCard) -> Path:
    """
    Экспортирует Data Card в файл формата marimo notebook.
    
    Возвращает путь к созданному файлу.
    """
    # Простейший валидный marimo notebook (pure Python format)
    code = card.source_code or "# Нет исходного кода"
    
    marimo_content = f'''import marimo

__generated_with = "0.0.0"
app = marimo.App()


@app.cell
def __():
    import marimo as mo
    return mo,


@app.cell
def __(mo):
    mo.md(r"""
    # Data Card: {card.name}
    
    **ID:** `{card.id}`  
    **Версия:** {card.version}  
    **Владелец:** {card.owner}  
    **Описание:** {card.description}
    """)
    return


@app.cell
def __():
    # === Исходный код карточки ===
{ _indent(code, 4) }
    return


@app.cell
def __(mo):
    mo.md("Карточка экспортирована из Agent Memory Project")
    return


if __name__ == "__main__":
    app.run()
'''

    # Безопасное имя файла
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in card.name)[:50]
    filename = f"{safe_name}_{card.id[:8]}.py"
    file_path = EXPORT_DIR / filename
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(marimo_content)
    
    print(f"📓 Карточка экспортирована в marimo: {file_path}")
    return file_path


def _indent(text: str, spaces: int) -> str:
    prefix = " " * spaces
    return "\n".join(prefix + line if line.strip() else line for line in text.splitlines())


def list_exported_notebooks() -> list:
    """Возвращает список экспортированных marimo-ноутбуков"""
    if not EXPORT_DIR.exists():
        return []
    return sorted(EXPORT_DIR.glob("*.py"), key=lambda p: p.stat().st_mtime, reverse=True)
