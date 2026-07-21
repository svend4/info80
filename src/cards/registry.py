from typing import Dict, List, Optional
from src.cards.base import DataCard
from src.cards.dependency_graph import card_graph
import json
import os
from pathlib import Path

CARDS_DIR = Path("data/cards")


class CardRegistry:
    def __init__(self, auto_load: bool = True):
        self._cards: Dict[str, DataCard] = {}
        CARDS_DIR.mkdir(parents=True, exist_ok=True)
        
        if auto_load:
            self.load_all()

    def register(self, card: DataCard, persist: bool = True):
        """Регистрирует карточку и сохраняет на диск"""
        self._cards[card.id] = card
        card_graph.add_card(card)
        
        if persist:
            self._save_card(card)

    def get(self, card_id: str) -> Optional[DataCard]:
        return self._cards.get(card_id)

    def list_all(self) -> List[DataCard]:
        return list(self._cards.values())

    def get_by_tag(self, tag: str) -> List[DataCard]:
        return [c for c in self._cards.values() if tag in c.tags]

    def delete(self, card_id: str):
        if card_id in self._cards:
            del self._cards[card_id]
            file_path = CARDS_DIR / f"{card_id}.json"
            if file_path.exists():
                file_path.unlink()

    def _save_card(self, card: DataCard):
        """Сохраняет одну карточку в JSON"""
        file_path = CARDS_DIR / f"{card.id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(card.to_dict(), f, ensure_ascii=False, indent=2)

    def load_all(self):
        """Загружает все карточки с диска при старте"""
        if not CARDS_DIR.exists():
            return
        
        loaded = 0
        for file_path in CARDS_DIR.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                card = DataCard.from_dict(data)
                self._cards[card.id] = card
                card_graph.add_card(card)
                loaded += 1
            except Exception as e:
                print(f"⚠️ Не удалось загрузить карточку {file_path.name}: {e}")
        
        if loaded > 0:
            print(f"✅ Загружено {loaded} Data Cards из диска")

    def save_all(self):
        """Принудительно сохраняет все карточки"""
        for card in self._cards.values():
            self._save_card(card)


# Глобальный реестр (автоматически загружает карточки при импорте)
card_registry = CardRegistry(auto_load=True)
