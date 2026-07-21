from pydantic import BaseModel, Field
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
import json


class DataCard(BaseModel):
    id: str
    name: str
    description: str
    version: str = "1.0.0"
    owner: str
    tags: List[str] = []
    dependencies: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Для персистентности храним исходный код, а не Callable
    source_code: Optional[str] = None
    metadata: Dict[str, Any] = {}

    # execute будет восстанавливаться динамически
    execute: Optional[Callable] = None

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        """Сериализация без Callable"""
        data = self.dict(exclude={"execute"})
        data["created_at"] = self.created_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "DataCard":
        """Десериализация + восстановление execute"""
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        
        card = cls(**{k: v for k, v in data.items() if k != "execute"})
        
        # Восстанавливаем execute из source_code
        if card.source_code:
            def execute_func(context: dict = None):
                return {
                    "card_id": card.id,
                    "code": card.source_code,
                    "name": card.name,
                    "context": context or {}
                }
            card.execute = execute_func
        
        return card
