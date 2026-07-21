# Agent Memory Project

Полноценная Multi-Agent система с Data Cards, реактивностью, безопасным выполнением, Human-in-the-loop и **версионированием**.

## Возможности

- Multi-Agent (Supervisor + Researcher + Coder + Reviewer)
- Data Cards + Dependency Graph + Reactive
- Персистентность + **Версионирование** (история + rollback)
- Безопасный sandbox
- Human-in-the-loop
- Streamlit UI + FastAPI

## Быстрый старт

```bash
git clone https://github.com/svend4/info80.git
cd info80
cp .env.example .env
make ui
```

## Версионирование

Каждая Data Card хранит историю изменений.

В Streamlit можно:
- Посмотреть все версии
- Сделать Rollback к любой предыдущей версии

## Статус разработки

- [x] Multi-Agent + Supervisor
- [x] Data Cards + Reactive + Persistence
- [x] Safe Sandbox
- [x] Human-in-the-loop
- [x] **Версионирование карточек**

---
*Проект из длинной сессии с Grok (июль 2026)*
