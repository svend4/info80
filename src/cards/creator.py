from src.cards.base import DataCard
from src.cards.registry import card_registry
from src.cards.graphiti_integration import add_card_to_graphiti
from src.cards.versioning import create_new_version, save_version
from datetime import datetime
import uuid
from typing import Optional


async def create_data_card_from_generation(
    generated_code: str,
    task: str,
    owner: str = "auto-kat-coder",
    tags: Optional[list] = None,
    existing_card_id: Optional[str] = None
) -> DataCard:
    """
    Создаёт новую DataCard или новую версию существующей.
    """
    card_name = "Auto Generated Solution"
    card_description = f"Автоматически созданная карточка для задачи: {task}"

    if "CARD_NAME:" in generated_code:
        try:
            card_name = generated_code.split("CARD_NAME:")[1].split("\n")[0].strip()
        except Exception:
            pass
    if "CARD_DESCRIPTION:" in generated_code:
        try:
            card_description = generated_code.split("CARD_DESCRIPTION:")[1].split("\n")[0].strip()
        except Exception:
            pass

    # Если передали existing_card_id — создаём новую версию
    if existing_card_id:
        existing = card_registry.get(existing_card_id)
        if existing:
            existing.name = card_name
            existing.description = card_description
            return create_new_version(existing, new_source_code=generated_code)

    card_id = f"auto.{card_name.lower().replace(' ', '_').replace('/', '_')[:40]}.{uuid.uuid4().hex[:8]}"

    def execute_func(context: dict = None):
        return {
            "card_id": card_id,
            "code": generated_code,
            "name": card_name,
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
        source_code=generated_code,
        execute=execute_func,
        metadata={
            "created_by": "KAT-Coder-Pro V2.5",
            "created_at": datetime.utcnow().isoformat(),
            "raw_code_length": len(generated_code),
            "original_task": task
        }
    )

    card_registry.register(new_card, persist=True)
    
    try:
        await add_card_to_graphiti(new_card)
    except Exception as e:
        print(f"⚠️ Не удалось сохранить в Graphiti: {e}")
    
    print(f"✅ Создана DataCard: {new_card.name} v{new_card.version} ({new_card.id})")
    return new_card
