# Agent Memory Project

Multi-Agent система с Data Cards, реактивностью, версионированием, Human-in-the-loop, Docker-sandbox, Observability и **экспортом в marimo**.

## Возможности

- Multi-Agent (Supervisor + Researcher + Coder + Reviewer)
- Data Cards + Reactive + Versioning
- Human-in-the-loop
- Docker + subprocess sandbox
- Observability (трассы)
- **Экспорт Data Cards в marimo notebooks**

## Работа с marimo

1. В Streamlit нажмите **«Export to marimo»** на любой карточке
2. Откройте файл:
   ```bash
   marimo edit data/marimo_export/имя_файла.py
   ```

## Быстрый старт

```bash
git clone https://github.com/svend4/info80.git
cd info80
cp .env.example .env
make ui
```

---
*Проект из длинной сессии с Grok (июль 2026)*
