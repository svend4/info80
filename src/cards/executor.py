from src.cards.reactive import reactive_executor
from src.cards.sandbox import execute_card_code
from src.cards.registry import card_registry
from typing import Dict, Any


def execute_card_with_dependencies(card_id: str, context: dict = None):
    """Выполняет карточку вместе со всеми её зависимостями (реактивно)"""
    return reactive_executor.execute_chain(card_id, context)


def execute_card_safely(card_id: str, context: dict = None, timeout: int = 10) -> Dict[str, Any]:
    """
    Безопасно выполняет код конкретной карточки через sandbox.
    """
    card = card_registry.get(card_id)
    if not card:
        return {
            "success": False,
            "error": f"Карточка {card_id} не найдена"
        }
    
    return execute_card_code(card, context=context, timeout=timeout)
