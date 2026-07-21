from src.cards.base import DataCard
from src.memory import graph
from datetime import datetime


async def add_card_to_graphiti(card: DataCard):
    """Сохраняет DataCard в Graphiti как эпизод/узел знаний"""
    
    episode_body = f"""
DataCard: {card.name}
Описание: {card.description}
Версия: {card.version}
Владелец: {card.owner}
Теги: {', '.join(card.tags)}
Зависимости: {card.dependencies}
Метаданные: {card.metadata}
"""

    await graph.add_episode(
        name=f"DataCard_{card.id}",
        episode_body=episode_body,
        source="Auto DataCard Creation",
        reference_time=card.created_at.isoformat() if hasattr(card, 'created_at') else None
    )
    
    print(f"✅ DataCard сохранена в Graphiti: {card.name} ({card.id})")


async def search_cards_in_graphiti(query: str, num_results: int = 5):
    """Ищет подходящие Data Cards в Graphiti"""
    results = await graph.search(
        query=query,
        num_results=num_results
    )
    return results
