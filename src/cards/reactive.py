from typing import Set, Dict
from src.cards.registry import card_registry
from src.cards.dependency_graph import card_graph
import asyncio


class ReactiveExecutor:
    def __init__(self):
        self.stale_cards: Set[str] = set()
        self.last_results: Dict[str, any] = {}

    def mark_stale(self, card_id: str):
        """Помечает карточку и все зависимые от неё как устаревшие"""
        dependents = self._find_dependents(card_id)
        self.stale_cards.update(dependents)
        self.stale_cards.add(card_id)

    def _find_dependents(self, card_id: str) -> Set[str]:
        """Находит все карточки, которые зависят от данной"""
        dependents = set()
        for cid, deps in card_graph.graph.items():
            if card_id in deps:
                dependents.add(cid)
                dependents.update(self._find_dependents(cid))
        return dependents

    async def execute_if_needed(self, card_id: str, context: dict = None):
        """Выполняет карточку только если она устарела или ещё не выполнялась"""
        if card_id in self.stale_cards or card_id not in self.last_results:
            card = card_registry.get(card_id)
            if card and card.execute:
                print(f"🔄 Реактивное выполнение: {card.name}")
                result = card.execute(context or {})
                self.last_results[card_id] = result
                self.stale_cards.discard(card_id)
                return result
        return self.last_results.get(card_id)

    async def execute_chain(self, card_id: str, context: dict = None):
        """Выполняет всю цепочку зависимостей реактивно"""
        order = card_graph.resolve_execution_order(card_id)
        results = {}

        for cid in order:
            result = await self.execute_if_needed(cid, context)
            results[cid] = result

        return results


# Глобальный реактивный исполнитель
reactive_executor = ReactiveExecutor()
