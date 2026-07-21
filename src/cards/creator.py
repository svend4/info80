from src.cards.base import DataCard
from src.cards.registry import card_registry
from src.cards.graphiti_integration import add_card_to_graphiti
from datetime import datetime
import uuid
from typing import Optional


async def create_data_card_from_generation(
    generated_code: str,
    task: str,
    owner: str = "auto-kat-coder",
    tags: Optional[list] = None
) -> DataCard:
    """
    Автоматически создаёт DataCard из кода, сгенерированного KAT-Coder.
    """
    card_name = "Auto Generated Solution"
    card_description = f"Автоматически созданная карточка для задачи: {task}"

    if "CARD_NAME:" in generated_code:
        card_name = generated_code.split("CARD_NAME:")[1].split("\n")[0].strip()
    if "CARD_DESCRIPTION:" in generated_code:
        card_description = generated_code.split("CARD_DESCRIPTION:")[1].split("\n")[0].strip()

    card_id = f"auto.{card_name.lower().replace(' ', '_')}.{uuid.uuid4().hex[:8]}"

    def execute_card(context: dict = None):
        return {
            "card_id": card_id,
            "code": generated_code,
            "task": task,
            "context": context or {}
        }

    new_card = DataCard(
        id=card_id,
        name=card_name,
        description=card_description,
        version="1.0.0",
        owner=owner,
        tags=tags or ["auto-generated", "kat-coder"],
        dependencies=[],
        execute=execute_card,
        metadata={
            "created_by": "KAT-Coder-Pro V2.5",
            "created_at": datetime.utcnow().isoformat(),
            "raw_code_length": len(generated_code)
        }
    )

    card_registry.register(new_card)
    
    # Сохраняем в Graphiti
    try:
        await add_card_to_graphiti(new_card)
    except Exception as e:
        print(f"Failed to save card to Graphiti: {e}")
    
    return new_card
