# История разработки проекта

## Основной план (завершён)

1. Multi-Agent
2. Data Cards
3. Dependency Graph
4. Реактивный слой
5. Streamlit UI
6. Персистентность
7. Улучшенный Supervisor
8. Безопасный subprocess sandbox
9. Human-in-the-loop
10. Версионирование карточек

## Дополнительные улучшения

### 11. **Строгий Docker-sandbox** ← текущий шаг

Добавлен `src/cards/docker_sandbox.py`:

- Если Docker доступен — код выполняется в изолированном контейнере:
  - `--network none` (без сети)
  - Ограничение памяти (128MB)
  - Ограничение CPU
  - Read-only файловая система
  - Временный tmpfs
- Если Docker недоступен — автоматический fallback на обычный subprocess sandbox
- `execute_card_safely()` теперь предпочитает Docker

---

## Возможные следующие направления

1. Observability / трейсинг
2. Интеграция с marimo
3. Card Marketplace
4. Автоматическое улучшение карточек
5. Более продвинутый Human-in-the-loop в Streamlit
