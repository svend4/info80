# Agent Memory Project — Multi-Agent + Data Cards + Graphiti + Reactive

Полноценная агентная система, разработанная в длинной сессии с Grok.

## Что это за проект

Это open-source реализация идей, близких к **DataCards.app** и **marimo**, но с сильным акцентом на:

- **Multi-Agent** оркестрацию (LangGraph)
- **Долгосрочную память** (Graphiti)
- **Переиспользуемые Data Cards** с зависимостями
- **Реактивное выполнение** (по мотивам marimo)
- **Персистентность карточек** (диск + Graphiti)
- Интеграцию с **KAT-Coder-Pro V2.5**
- Версионирование сессий через **Entire**
- Удобный Streamlit UI

## Основные возможности

- LLM Supervisor + Researcher / Coder / Reviewer
- Автоматическое создание Data Cards из кода KAT-Coder
- **Персистентность**: карточки сохраняются на диск (`data/cards/`) и переживают перезапуски
- Dependency Graph между карточками
- Реактивный слой (stale cards + auto-recompute)
- Сохранение карточек в Graphiti как знания
- Streamlit-интерфейс с отображением статуса карточек
- Docker + one-command запуск

## Быстрый старт

```bash
git clone https://github.com/svend4/info80.git
cd info80

cp .env.example .env
# Заполните KAT_CODER_API_KEY и другие переменные

make up          # Docker + Neo4j
# или
make ui          # Только Streamlit UI
```

## Структура проекта

```
info80/
├── data/cards/                 # ← Персистентные Data Cards (JSON)
├── src/
│   ├── agent_graph.py          # Multi-Agent + Supervisor + KAT-Coder
│   ├── memory.py               # Graphiti
│   └── cards/
│       ├── base.py             # DataCard (с сериализацией)
│       ├── registry.py         # Persistent CardRegistry
│       ├── creator.py
│       ├── dependency_graph.py
│       ├── executor.py
│       ├── reactive.py
│       └── graphiti_integration.py
├── streamlit_app.py
├── api/main.py
├── main.py
├── docker-compose.yml
├── Dockerfile
├── Makefile
└── HISTORY.md
```

## Архитектура (кратко)

1. **Supervisor** (LLM) решает, кого вызвать
2. **Researcher** достаёт контекст из Graphiti
3. **Coder** (KAT-Coder) генерирует код + автоматически создаёт Data Card
4. Карточка **сразу сохраняется** на диск + в Graphiti
5. **Reviewer** проверяет результат
6. Data Cards имеют зависимости и реактивно пересчитываются

## Текущий статус (по порядку разработки)

- [x] Multi-Agent + LLM Supervisor
- [x] Data Cards система
- [x] Dependency Graph
- [x] Реактивный слой
- [x] **Персистентность карточек** ← только что сделано
- [ ] Улучшение Supervisor (следующий шаг)
- [ ] Безопасное выполнение сгенерированного кода
- [ ] Human-in-the-loop
- [ ] Версионирование карточек

## Связь с DataCards.app и marimo

- **DataCards.app** — enterprise-версия похожей идеи
- **marimo** — ближайший открытый аналог реактивных ноутбуков
- Этот проект берёт лучшее из обеих философий

---

*Проект полностью собран на основе длинной сессии диалога с Grok (июль 2026).*
