# Agent Memory Project

Multi-Agent система с Data Cards, реактивностью, версионированием, Human-in-the-loop, sandbox, Observability, marimo и **Card Marketplace**.

## Возможности

- Multi-Agent (Supervisor + Researcher + Coder + Reviewer)
- Data Cards + Reactive + Versioning
- Human-in-the-loop
- Docker + subprocess sandbox
- Observability (трассы)
- Экспорт в marimo
- **Card Marketplace** (обмен карточками)

## Card Marketplace

1. На любой карточке нажмите **Publish**
2. Карточка появится во вкладке **Marketplace**
3. Другой пользователь (или другой проект) может нажать **Установить**

Пакеты хранятся в `data/marketplace/`.

## Быстрый старт

```bash
git clone https://github.com/svend4/info80.git
cd info80
cp .env.example .env
make ui
```

---
*Проект из длинной сессии с Grok (июль 2026)*
