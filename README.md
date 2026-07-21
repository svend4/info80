# Agent Memory Project — Multi-Agent + Data Cards + Graphiti + Reactive

Полноценная агентная система, разработанная в длинной сессии с Grok.

## Что это за проект

Это open-source реализация идей, близких к **DataCards.app** и **marimo**, но с сильным акцентом на:

- **Multi-Agent** оркестрацию (LangGraph)
- **Долгосрочную память** (Graphiti)
- **Переиспользуемые Data Cards** с зависимостями
- **Реактивное выполнение** (по мотивам marimo)
- Интеграцию с **KAT-Coder-Pro V2.5**
- Версионирование сессий через **Entire**
- Удобный Streamlit UI

Проект был построен **пошагово** в длинном диалоге с Grok (июль 2026).

## Основные возможности

- LLM Supervisor + Researcher / Coder / Reviewer
- Автоматическое создание Data Cards из кода, сгенерированного KAT-Coder
- Dependency Graph между карточками
- Реактивный слой (stale cards + auto-recompute)
- Сохранение карточек в Graphiti как знания
- Streamlit-интерфейс с отображением статуса карточек
- Docker + one-command запуск

## Быстрый старт

```bash
git clone https://github.com/svend4/info80.git
cd info80

# Включаем Entire (если используете)
entire enable

cp .env.example .env
# Заполните KAT_CODER_API_KEY и другие переменные

make up          # Docker + Neo4j
# или
make ui          # Только Streamlit UI
```

## Структура проекта

```
agent-memory-project/
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── requirements.txt
├── .env.example
├── main.py
├── streamlit_app.py
├── api/
│   └── main.py
├── src/
│   ├── agent_graph.py          # Multi-Agent + Supervisor + KAT-Coder
│   ├── memory.py               # Graphiti
│   └── cards/
│       ├── base.py
│       ├── registry.py
│       ├── creator.py
│       ├── dependency_graph.py
│       ├── executor.py
│       ├── reactive.py
│       └── graphiti_integration.py
└── HISTORY.md                  # История развития проекта из сессии
```

## Архитектура (кратко)

1. **Supervisor** (LLM) решает, кого вызвать
2. **Researcher** достаёт контекст из Graphiti
3. **Coder** (KAT-Coder) генерирует код + автоматически создаёт Data Card
4. **Reviewer** проверяет результат
5. Data Cards имеют зависимости и реактивно пересчитываются
6. Всё сохраняется в Graphiti и может версионироваться через Entire

## Связь с DataCards.app и marimo

- **DataCards.app** — enterprise-версия похожей идеи (реактивные executable nodes + dependency graph + compliance)
- **marimo** — ближайший открытый аналог реактивных ноутбуков
- Этот проект берёт лучшее из обеих философий и упаковывает в Multi-Agent + Graphiti систему

## Лицензия

См. LICENSE

---

*Проект полностью собран на основе длинной сессии диалога с Grok (июль 2026).*
