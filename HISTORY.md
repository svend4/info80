# История разработки проекта (из сессии с Grok)

## Хронология (по порядку)

### 1–8. Базовая система
- KAT-Coder, Entire, Graphiti, Multi-Agent, Data Cards, Reactive, Streamlit, Persistence, Improved Supervisor

### 9. **Безопасное выполнение кода (Sandbox)** ← текущий шаг

Добавлен модуль `src/cards/sandbox.py`:

- Запуск кода в **отдельном процессе** (subprocess)
- Таймаут выполнения (по умолчанию 10 сек)
- Статическая проверка на опасные конструкции (`os.system`, `eval`, `exec`, `subprocess`, `socket` и др.)
- Захват stdout / stderr
- Временные файлы удаляются после выполнения
- Интеграция в Streamlit UI (кнопка «Безопасно выполнить»)

---

## Следующие шаги (по приоритету)

1. Human-in-the-loop
2. Версионирование карточек
3. Более строгий sandbox (Docker / RestrictedPython)
4. Observability
