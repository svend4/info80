# История разработки проекта (из сессии с Grok)

## Хронология (по порядку)

### 1. Начало — KAT-Coder-Pro V2.5
- Обсуждение модели Kuaishou KwaiKAT KAT-Coder-Pro V2.5
- Анализ AutoBuilder, KwaiClawEnv, агентного RL, MOPD

### 2. Entire — Git-платформа для AI-агентов
- Запуск Entire (Томас Домке)
- Checkpoints, зеркалирование репозиториев, CLI

### 3. Zep AI / Graphiti
- Долгосрочная память через temporal knowledge graph
- Интеграция с Entire и KAT-Coder

### 4. Построение Multi-Agent системы
- Supervisor + Researcher + Coder + Reviewer
- LLM Supervisor
- Прямой вызов KAT-Coder-Pro V2.5

### 5. Data Cards (по мотивам DataCards.app + marimo)
- Создание отдельного модуля Card System
- Базовый класс DataCard
- Registry + Dependency Graph
- Автоматическое создание карточек

### 6. Реактивный слой
- ReactiveExecutor (по мотивам marimo)
- Помечание stale-карточек
- Автоматический пересчёт цепочек

### 7. Streamlit UI
- Просмотр карточек + статус (актуальна / устарела)

### 8. Финальная сборка репозитория
- Docker + Makefile + документация

### 9. **Персистентность Data Cards** (текущий шаг)
- Карточки сохраняются в `data/cards/*.json`
- Автоматическая загрузка при старте
- `source_code` хранится для восстановления `execute`
- Двойное сохранение: диск + Graphiti

---

## Следующие шаги (по приоритету)

1. Улучшение Supervisor (защита от зацикливания + лучший промпт)
2. Безопасное выполнение сгенерированного кода (sandbox)
3. Human-in-the-loop
4. Версионирование карточек
5. Более глубокая интеграция с marimo
