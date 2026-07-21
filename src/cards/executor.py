from src.cards.reactive import reactive_executor


def execute_card_with_dependencies(card_id: str, context: dict = None):
    """Выполняет карточку вместе со всеми её зависимостями (реактивно)"""
    return reactive_executor.execute_chain(card_id, context)
