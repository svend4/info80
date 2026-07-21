# Agent Memory Project

Multi-Agent система с Data Cards, реактивностью, безопасным выполнением кода и **Human-in-the-loop**.

## Возможности

- Multi-Agent (Supervisor + Researcher + Coder + Reviewer)
- Data Cards + Dependency Graph + Reactive
- Персистентность карточек
- Безопасный sandbox
- **Human-in-the-loop** (approve / reject / modify)
- Streamlit UI + FastAPI

## Быстрый старт

```bash
git clone https://github.com/svend4/info80.git
cd info80
cp .env.example .env
make ui
```

## Human-in-the-loop

После того как Reviewer проверил код, система может остановиться и ждать решения человека.

Через API:

```bash
# 1. Запустить задачу
curl -X POST http://localhost:8000/run -d '{"task": "..."}'

# 2. Если waiting_for_human == true, отправить решение
curl -X POST http://localhost:8000/human-feedback \
  -d '{"decision": "approve", "current_state": {...}}'
```

Возможные решения: `approve` | `reject` | `modify`

## Статус

- [x] Multi-Agent + Supervisor
- [x] Data Cards + Reactive + Persistence
- [x] Safe Sandbox
- [x] **Human-in-the-loop**
- [ ] Версионирование карточек

---
*Проект из длинной сессии с Grok (июль 2026)*
