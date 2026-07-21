# История разработки проекта (из сессии с Grok)

## Хронология (по порядку)

### 1. Начало — KAT-Coder-Pro V2.5
- Обсуждение модели Kuaishou KwaiKAT KAT-Coder-Pro V2.5

### 2. Entire — Git-платформа для AI-агентов
- Запуск Entire (Томас Домке)

### 3. Zep AI / Graphiti
- Долгосрочная память через temporal knowledge graph

### 4. Построение Multi-Agent системы
- Supervisor + Researcher + Coder + Reviewer

### 5. Data Cards (по мотивам DataCards.app + marimo)
- Модуль Card System + Dependency Graph

### 6. Реактивный слой
- ReactiveExecutor (stale + auto-recompute)

### 7. Streamlit UI

### 8. Финальная сборка репозитория

### 9. Персистентность Data Cards
- Сохранение в `data/cards/*.json` + Graphiti
- Автозагрузка при старте

### 10. **Улучшение Supervisor** (текущий шаг)
- Защита от бесконечных циклов (`MAX_ITERATIONS = 8`)
- История решений (`history`)
- Умные эвристики + LLM fallback
- Отслеживание `last_agent`, `review_result`, `iteration`
- Защита от повторных вызовов одного агента подряд
- Более качественные промпты для Coder и Reviewer

---

## Следующие шаги (по приоритету)

1. Безопасное выполнение сгенерированного кода (sandbox)
2. Human-in-the-loop
3. Версионирование карточек
4. Более глубокая интеграция с marimo
5. Observability (логирование, трейсинг)
