# История разработки проекта

## Хронология (по порядку)

### 1–8. Базовая система + Sandbox
- Multi-Agent, Data Cards, Reactive, Persistence, Improved Supervisor, Safe Sandbox

### 9. **Human-in-the-loop** ← текущий шаг

Добавлено:

- Новое поле состояния: `waiting_for_human`, `human_feedback`, `human_decision`
- Новый узел графа: `human_approval`
- Supervisor теперь после Reviewer может отправлять результат человеку
- Человек может ответить:
  - `approve` — принять и завершить
  - `reject` — отклонить
  - `modify` + комментарий — отправить на доработку Coder’у
- API endpoint `/human-feedback` для продолжения работы после решения человека

---

## Следующие шаги

1. Версионирование карточек
2. Более строгий sandbox (Docker)
3. Observability / трейсинг
4. Интеграция с marimo как execution backend
