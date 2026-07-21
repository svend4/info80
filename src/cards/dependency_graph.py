from typing import List, Dict, Set
from src.cards.base import DataCard


class CardDependencyGraph:
    def __init__(self):
        self.graph: Dict[str, List[str]] = {}   # card_id -> list of dependencies

    def add_card(self, card: DataCard):
        self.graph[card.id] = card.dependencies or []

    def get_dependencies(self, card_id: str) -> List[str]:
        """Возвращает все зависимости (рекурсивно)"""
        visited = set()
        result = []

        def dfs(cid: str):
            if cid in visited:
                return
            visited.add(cid)
            deps = self.graph.get(cid, [])
            for dep in deps:
                dfs(dep)
                if dep not in result:
                    result.append(dep)
            if cid not in result:
                result.append(cid)

        dfs(card_id)
        return result

    def resolve_execution_order(self, card_id: str) -> List[str]:
        """Возвращает порядок выполнения карточек (сначала зависимости)"""
        return self.get_dependencies(card_id)


# Глобальный граф зависимостей
card_graph = CardDependencyGraph()
