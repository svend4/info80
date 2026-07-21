# Agent Memory Project — Multi-Agent + Data Cards + Graphiti + Reactive

Полноценная агентная система с безопасным выполнением кода.

## Возможности

- Multi-Agent (Supervisor + Researcher + Coder + Reviewer)
- Data Cards с зависимостями и реактивностью
- **Персистентность** карточек
- **Умный Supervisor** с защитой от циклов
- **Безопасный sandbox** для выполнения сгенерированного кода
- Streamlit UI
- Graphiti + Docker

## Быстрый старт

```bash
git clone https://github.com/svend4/info80.git
cd info80
cp .env.example .env
# Заполните KAT_CODER_API_KEY

make ui
```

## Текущий статус

- [x] Multi-Agent + Supervisor
- [x] Data Cards + Dependency Graph
- [x] Реактивный слой
- [x] Персистентность
- [x] Улучшенный Supervisor
- [x] **Безопасный sandbox** ← сделано
- [ ] Human-in-the-loop
- [ ] Версионирование карточек

## Безопасность

Сгенерированный код выполняется в изолированном процессе с:
- Таймаутом
- Статической проверкой опасных конструкций
- Отдельным временным файлом

---
*Проект из длинной сессии с Grok (июль 2026)*
