"""
Card Marketplace — обмен и публикация Data Cards.

Возможности:
- Экспорт карточки в переносимый пакет (.card.json)
- Импорт карточки из пакета
- Локальный каталог shared-карточек
- Простая "публикация" и установка
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import shutil
from datetime import datetime
from src.cards.base import DataCard
from src.cards.registry import card_registry

MARKETPLACE_DIR = Path("data/marketplace")
MARKETPLACE_DIR.mkdir(parents=True, exist_ok=True)

SHARED_DIR = MARKETPLACE_DIR / "shared"
SHARED_DIR.mkdir(parents=True, exist_ok=True)

PACKAGES_DIR = MARKETPLACE_DIR / "packages"
PACKAGES_DIR.mkdir(parents=True, exist_ok=True)


def export_card_package(card_id: str) -> Optional[Path]:
    """
    Экспортирует карточку в переносимый пакет .card.json
    """
    card = card_registry.get(card_id)
    if not card:
        print(f"Карточка {card_id} не найдена")
        return None

    package = {
        "format": "datacard-package-v1",
        "exported_at": datetime.utcnow().isoformat(),
        "card": card.to_dict()
    }

    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in card.name)[:40]
    filename = f"{safe_name}_{card.id[:8]}.card.json"
    path = PACKAGES_DIR / filename

    with open(path, "w", encoding="utf-8") as f:
        json.dump(package, f, ensure_ascii=False, indent=2)

    print(f"📦 Пакет создан: {path}")
    return path


def import_card_package(package_path: str | Path, overwrite: bool = False) -> Optional[DataCard]:
    """
    Импортирует карточку из пакета .card.json
    """
    path = Path(package_path)
    if not path.exists():
        print(f"Файл не найден: {path}")
        return None

    with open(path, "r", encoding="utf-8") as f:
        package = json.load(f)

    if package.get("format") != "datacard-package-v1":
        print("Неизвестный формат пакета")
        return None

    data = package["card"]
    card = DataCard.from_dict(data)

    existing = card_registry.get(card.id)
    if existing and not overwrite:
        # Создаём карточку с новым ID, чтобы не затирать
        import uuid
        card.id = f"imported.{card.id}.{uuid.uuid4().hex[:6]}"
        print(f"Карточка уже существует, импортирована как {card.id}")

    card_registry.register(card, persist=True)
    print(f"✅ Карточка импортирована: {card.name} ({card.id})")
    return card


def publish_card(card_id: str) -> Optional[Path]:
    """
    "Публикует" карточку в локальный shared-каталог marketplace.
    """
    package_path = export_card_package(card_id)
    if not package_path:
        return None

    dest = SHARED_DIR / package_path.name
    shutil.copy2(package_path, dest)
    print(f"📢 Карточка опубликована в marketplace: {dest}")
    return dest


def list_shared_cards() -> List[Dict[str, Any]]:
    """Список карточек, доступных в локальном marketplace"""
    cards = []
    for f in sorted(SHARED_DIR.glob("*.card.json"), reverse=True):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                package = json.load(fp)
            card_data = package.get("card", {})
            cards.append({
                "file": str(f),
                "name": card_data.get("name"),
                "id": card_data.get("id"),
                "version": card_data.get("version"),
                "description": card_data.get("description", "")[:120],
                "owner": card_data.get("owner"),
                "exported_at": package.get("exported_at")
            })
        except Exception as e:
            print(f"Ошибка чтения {f}: {e}")
    return cards


def install_shared_card(filename: str, overwrite: bool = False) -> Optional[DataCard]:
    """Устанавливает карточку из shared-каталога в локальный реестр"""
    path = SHARED_DIR / filename
    if not path.exists():
        # Попробуем найти по части имени
        matches = list(SHARED_DIR.glob(f"*{filename}*"))
        if matches:
            path = matches[0]
        else:
            print(f"Пакет не найден: {filename}")
            return None
    return import_card_package(path, overwrite=overwrite)


def list_local_packages() -> List[Path]:
    """Список локально экспортированных пакетов"""
    return sorted(PACKAGES_DIR.glob("*.card.json"), reverse=True)
