# Agent Memory Project

Multi-Agent система с Data Cards, реактивностью, версионированием, Human-in-the-loop и **двумя уровнями sandbox**.

## Возможности

- Multi-Agent (Supervisor + Researcher + Coder + Reviewer)
- Data Cards + Dependency Graph + Reactive + Versioning
- Human-in-the-loop
- **Два sandbox**:
  - Subprocess (базовый)
  - **Docker** (строгая изоляция, если доступен)
- Streamlit UI + FastAPI

## Безопасность выполнения кода

```text
execute_card_safely()
       │
       ├─ Docker доступен? ──► Docker sandbox
       │                         (network=none, memory limit, read-only)
       │
       └─ Нет ───────────────► Subprocess sandbox
                                 (timeout + static checks)
```

## Быстрый старт

```bash
git clone https://github.com/svend4/info80.git
cd info80
cp .env.example .env
make ui
```

## Статус

Основной план полностью выполнен + добавлен строгий Docker-sandbox.

---
*Проект из длинной сессии с Grok (июль 2026)*
