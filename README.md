# Agent Memory Project — Multi-Agent + Data Cards + Graphiti + Reactive

Полноценная агентная система, разработанная в длинной сессии с Grok.

## Что это за проект

Open-source реализация идей, близких к **DataCards.app** и **marimo**, с акцентом на:

- Multi-Agent оркестрацию (LangGraph)
- Долгосрочную память (Graphiti)
- Переиспользуемые Data Cards с зависимостями
- Реактивное выполнение
- **Персистентность карточек**
- **Умный Supervisor** с защитой от циклов
- Интеграцию с KAT-Coder-Pro V2.5

## Основные возможности

- LLM Supervisor + Researcher / Coder / Reviewer
- Автоматическое создание Data Cards
- Персистентность (диск + Graphiti)
- Dependency Graph + реактивный слой
- Защита от зацикливания агентов
- Streamlit UI
- Docker

## Быстрый старт

```bash
git clone https://github.com/svend4/info80.git
cd info80

cp .env.example .env
# Заполните KAT_CODER_API_KEY

make up          # Docker + Neo4j
make ui          # Streamlit UI
```

## Текущий статус разработки (по порядку)

- [x] Multi-Agent + LLM Supervisor
- [x] Data Cards система
- [x] Dependency Graph
- [x] Реактивный слой
- [x] Streamlit UI
- [x] Персистентность карточек
- [x] **Улучшенный Supervisor** ← только что сделано
- [ ] Безопасное выполнение сгенерированного кода
- [ ] Human-in-the-loop
- [ ] Версионирование карточек

## Архитектура

1. **Supervisor** (умный) решает, кого вызвать, с защитой от циклов
2. **Researcher** → Graphiti
3. **Coder** (KAT-Coder) → генерирует код + создаёт Data Card
4. **Reviewer** → проверяет (APPROVED / NEEDS_WORK)
5. Карточки сохраняются и могут реактивно пересчитываться

---

*Проект собран на основе длинной сессии с Grok (июль 2026).*
