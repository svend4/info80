from typing import Dict, List, Optional
from src.cards.base import DataCard
from src.cards.dependency_graph import card_graph


class CardRegistry:
    def __init__(self):
        self._cards: Dict[str, DataCard] = {}

    def register(self, card: DataCard):
        self._cards[card.id] = card
        card_graph.add_card(card)   # обновляем граф зависимостей

    def get(self, card_id: str) -> Optional[DataCard]:
        return self._cards.get(card_id)

    def list_all(self) -> List[DataCard]:
        return list(self._cards.values())

    def get_by_tag(self, tag: str) -> List[DataCard]:
        return [c for c in self._cards.values() if tag in c.tags]


# Глобальный реестр
card_registry = CardRegistry()
