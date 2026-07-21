from pydantic import BaseModel, Field
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime


class DataCard(BaseModel):
    id: str
    name: str
    description: str
    version: str = "1.0.0"
    owner: str
    tags: List[str] = []
    dependencies: List[str] = []          # ID зависимых карточек
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    execute: Optional[Callable] = None    # Функция, которую можно вызвать
    metadata: Dict[str, Any] = {}

    class Config:
        arbitrary_types_allowed = True
