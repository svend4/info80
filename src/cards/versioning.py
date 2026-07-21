"""
Система версионирования Data Cards.

При каждом обновлении карточки предыдущая версия сохраняется в историю.
Можно просматривать историю и делать rollback.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
import json
import shutil
from datetime import datetime
from src.cards.base import DataCard
from src.cards.registry import card_registry, CARDS_DIR

HISTORY_DIR = Path("data/cards/history")


def _ensure_history_dir(card_id: str) -> Path:
    path = HISTORY_DIR / card_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_version(card: DataCard):
    """
    Сохраняет текущую версию карточки в историю перед обновлением.
    """
    history_path = _ensure_history_dir(card.id)
    version_file = history_path / f"v{card.version}.json"
    
    with open(version_file, "w", encoding="utf-8") as f:
        json.dump(card.to_dict(), f, ensure_ascii=False, indent=2)
    
    print(f"📦 Сохранена версия {card.version} карточки {card.id}")


def get_versions(card_id: str) -> List[Dict[str, Any]]:
    """Возвращает список всех сохранённых версий карточки"""
    history_path = HISTORY_DIR / card_id
    if not history_path.exists():
        return []
    
    versions = []
    for file in sorted(history_path.glob("v*.json")):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
            versions.append({
                "version": data.get("version"),
                "created_at": data.get("created_at"),
                "name": data.get("name"),
                "description": data.get("description"),
                "file": str(file)
            })
        except Exception as e:
            print(f"Ошибка чтения версии {file}: {e}")
    
    return versions


def get_version(card_id: str, version: str) -> Optional[DataCard]:
    """Загружает конкретную версию карточки"""
    history_path = HISTORY_DIR / card_id
    version_file = history_path / f"v{version}.json"
    
    if not version_file.exists():
        return None
    
    with open(version_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return DataCard.from_dict(data)


def rollback(card_id: str, version: str) -> Optional[DataCard]:
    """
    Откатывает карточку к указанной версии.
    Текущая версия предварительно сохраняется в историю.
    """
    current = card_registry.get(card_id)
    if current:
        # Сохраняем текущую версию перед откатом
        save_version(current)
    
    old_card = get_version(card_id, version)
    if not old_card:
        print(f"❌ Версия {version} карточки {card_id} не найдена")
        return None
    
    # Создаём новую версию на основе старой
    new_version = _bump_version(old_card.version)
    old_card.version = new_version
    old_card.metadata["rolled_back_from"] = version
    old_card.metadata["rollback_at"] = datetime.utcnow().isoformat()
    
    card_registry.register(old_card, persist=True)
    print(f"✅ Откат карточки {card_id} к версии {version} → новая версия {new_version}")
    return old_card


def _bump_version(version: str) -> str:
    """Увеличивает минорную версию (1.0.0 → 1.0.1)"""
    try:
        parts = version.split(".")
        parts[-1] = str(int(parts[-1]) + 1)
        return ".".join(parts)
    except Exception:
        return version + ".1"


def create_new_version(card: DataCard, new_source_code: str = None) -> DataCard:
    """
    Создаёт новую версию существующей карточки.
    Старая версия сохраняется в историю.
    """
    # Сохраняем текущую версию в историю
    save_version(card)
    
    # Увеличиваем версию
    card.version = _bump_version(card.version)
    card.created_at = datetime.utcnow()
    
    if new_source_code:
        card.source_code = new_source_code
        def execute_func(context: dict = None):
            return {
                "card_id": card.id,
                "code": new_source_code,
                "name": card.name,
                "context": context or {}
            }
        card.execute = execute_func
    
    card.metadata["updated_at"] = datetime.utcnow().isoformat()
    
    card_registry.register(card, persist=True)
    print(f"🆕 Создана новая версия карточки {card.id}: {card.version}")
    return card
