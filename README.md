# Agent Memory Project

Multi-Agent система с Data Cards, реактивностью, версионированием, Human-in-the-loop, Docker-sandbox и **Observability**.

## Возможности

- Multi-Agent (Supervisor + Researcher + Coder + Reviewer)
- Data Cards + Reactive + Versioning
- Human-in-the-loop
- Два уровня sandbox (subprocess + Docker)
- **Observability** — полные трассы выполнения агентов
- Streamlit UI + FastAPI

## Observability

Каждый запуск задачи создаёт трассу в `data/traces/`.

В Streamlit есть вкладка **«Трассы»**, где можно посмотреть:
- Какие агенты вызывались
- Решения Supervisor
- Созданные карточки
- Метрики

## Быстрый старт

```bash
git clone https://github.com/svend4/info80.git
cd info80
cp .env.example .env
make ui
```

---
*Проект из длинной сессии с Grok (июль 2026)*
