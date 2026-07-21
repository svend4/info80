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
    Карточка сразу сохраняется на диск и в Graphiti.
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
        source_code=generated_code,          # Важно для персистентности
        execute=execute_func,
        metadata={
            "created_by": "KAT-Coder-Pro V2.5",
            "created_at": datetime.utcnow().isoformat(),
            "raw_code_length": len(generated_code),
            "original_task": task
        }
    )

    # Регистрируем + сохраняем на диск
    card_registry.register(new_card, persist=True)
    
    # Сохраняем в Graphiti
    try:
        await add_card_to_graphiti(new_card)
    except Exception as e:
        print(f"⚠️ Не удалось сохранить карточку в Graphiti: {e}")
    
    print(f"✅ Создана и сохранена DataCard: {new_card.name} ({new_card.id})")
    return new_card
