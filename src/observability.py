"""
Простой слой observability для Multi-Agent системы.

- Логирует каждый шаг агентов
- Считает базовые метрики
- Сохраняет трассы в data/traces/
- Позволяет просматривать историю запусков
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import uuid
from collections import defaultdict

TRACES_DIR = Path("data/traces")
TRACES_DIR.mkdir(parents=True, exist_ok=True)


class Tracer:
    def __init__(self):
        self.current_trace_id: Optional[str] = None
        self.events: List[Dict[str, Any]] = []
        self.metrics = defaultdict(int)

    def start_trace(self, task: str) -> str:
        """Начинает новую трассу выполнения"""
        self.current_trace_id = str(uuid.uuid4())[:8]
        self.events = []
        self.metrics = defaultdict(int)
        
        self.log("trace_started", {
            "task": task,
            "trace_id": self.current_trace_id
        })
        return self.current_trace_id

    def log(self, event_type: str, data: Dict[str, Any] = None):
        """Добавляет событие в текущую трассу"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "data": data or {}
        }
        self.events.append(event)
        
        # Простые метрики
        self.metrics[event_type] += 1
        if event_type in ("researcher", "coder", "reviewer", "human_approval", "supervisor"):
            self.metrics["agent_calls"] += 1

    def end_trace(self, status: str = "completed"):
        """Завершает трассу и сохраняет на диск"""
        if not self.current_trace_id:
            return
        
        trace = {
            "trace_id": self.current_trace_id,
            "status": status,
            "started_at": self.events[0]["timestamp"] if self.events else None,
            "ended_at": datetime.utcnow().isoformat(),
            "metrics": dict(self.metrics),
            "events": self.events
        }
        
        file_path = TRACES_DIR / f"{self.current_trace_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(trace, f, ensure_ascii=False, indent=2)
        
        print(f"📊 Трасса сохранена: {file_path}")
        self.current_trace_id = None
        return trace

    def get_metrics(self) -> Dict[str, int]:
        return dict(self.metrics)


# Глобальный трейсер
tracer = Tracer()


def list_traces(limit: int = 20) -> List[Dict[str, Any]]:
    """Возвращает список последних трасс"""
    files = sorted(TRACES_DIR.glob("*.json"), reverse=True)[:limit]
    traces = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            traces.append({
                "trace_id": data.get("trace_id"),
                "status": data.get("status"),
                "started_at": data.get("started_at"),
                "metrics": data.get("metrics", {}),
                "events_count": len(data.get("events", []))
            })
        except Exception:
            pass
    return traces


def get_trace(trace_id: str) -> Optional[Dict[str, Any]]:
    """Загружает полную трассу по ID"""
    file_path = TRACES_DIR / f"{trace_id}.json"
    if not file_path.exists():
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
