from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List, Optional
import operator
from openai import OpenAI
from src.memory import get_project_context
from src.cards.creator import create_data_card_from_generation
from src.cards.reactive import reactive_executor
import os
from dotenv import load_dotenv

load_dotenv()

kat_client = OpenAI(
    base_url=os.getenv("KAT_CODER_BASE_URL", "https://api.streamlake.ai/v1"),
    api_key=os.getenv("KAT_CODER_API_KEY")
)

KAT_CODER_MODEL = os.getenv("KAT_CODER_MODEL", "kat-coder-pro-v2.5")
MAX_ITERATIONS = 8  # Защита от бесконечных циклов


class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    task: str
    context: str
    next: str
    created_card_id: str
    iteration: int
    history: List[str]          # История решений Supervisor
    last_agent: Optional[str]
    review_result: Optional[str]


# === Специалисты ===

async def researcher(state: AgentState):
    print(f"🔍 Researcher: ищу контекст по задаче...")
    context = await get_project_context(state["task"])
    return {
        "context": context or "Контекст не найден",
        "next": "supervisor",
        "last_agent": "researcher",
        "iteration": state.get("iteration", 0) + 1
    }


async def coder(state: AgentState):
    print(f"💻 Coder (KAT-Coder): генерирую код...")
    prompt = f"""
Ты — KAT-Coder-Pro V2.5 — мощный агентный coding-модель.

=== Память / Контекст проекта ===
{state.get('context', 'Контекст отсутствует')}

=== Текущая задача ===
{state['task']}

Требования:
1. Напиши качественный, безопасный и рабочий код.
2. В конце ответа обязательно добавь:
CARD_NAME: <короткое название>
CARD_DESCRIPTION: <краткое описание>
"""

    response = kat_client.chat.completions.create(
        model=KAT_CODER_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=6000
    )
    
    result = response.choices[0].message.content

    new_card = await create_data_card_from_generation(
        generated_code=result,
        task=state['task']
    )

    reactive_executor.mark_stale(new_card.id)

    return {
        "messages": [result],
        "created_card_id": new_card.id,
        "next": "supervisor",
        "last_agent": "coder",
        "iteration": state.get("iteration", 0) + 1
    }


async def reviewer(state: AgentState):
    print(f"🔎 Reviewer: проверяю код...")
    last_code = state["messages"][-1] if state.get("messages") else ""
    
    prompt = f"""Ты — строгий code reviewer.

Проверь следующий код на:
- Корректность
- Безопасность
- Best practices
- Потенциальные баги

Код:
{last_code}

В конце ответа напиши одно из двух:
APPROVED — если код хороший
NEEDS_WORK — если есть серьёзные замечания
"""
    
    response = kat_client.chat.completions.create(
        model=KAT_CODER_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    review = response.choices[0].message.content
    
    return {
        "messages": [review],
        "review_result": review,
        "next": "supervisor",
        "last_agent": "reviewer",
        "iteration": state.get("iteration", 0) + 1
    }


# === Улучшенный Supervisor ===

async def supervisor(state: AgentState):
    iteration = state.get("iteration", 0)
    history = state.get("history", [])
    last_agent = state.get("last_agent")
    has_context = bool(state.get("context"))
    has_code = bool(state.get("messages"))
    review = state.get("review_result", "")

    # === Защита от бесконечных циклов ===
    if iteration >= MAX_ITERATIONS:
        print(f"⚠️ Достигнут лимит итераций ({MAX_ITERATIONS}). Завершаем.")
        return {"next": "end", "history": history + ["end (max iterations)"]}

    # === Простые правила (быстрые эвристики) ===
    if not has_context and last_agent != "researcher":
        decision = "researcher"
    elif not has_code and last_agent != "coder":
        decision = "coder"
    elif has_code and last_agent == "coder":
        decision = "reviewer"
    elif "APPROVED" in (review or "").upper():
        decision = "end"
    elif "NEEDS_WORK" in (review or "").upper() and last_agent == "reviewer":
        # Можно отправить обратно на доработку
        decision = "coder"
    else:
        # Если правила не сработали — спрашиваем LLM
        decision = await _llm_decide(state)

    # Защита от повторного вызова одного и того же агента подряд слишком часто
    if len(history) >= 2 and history[-1] == decision and history[-2] == decision:
        print(f"⚠️ Обнаружен возможный цикл на '{decision}'. Принудительно завершаем.")
        decision = "end"

    print(f"🧠 Supervisor → {decision} (iteration {iteration})")
    
    return {
        "next": decision,
        "history": history + [decision],
        "iteration": iteration
    }


async def _llm_decide(state: AgentState) -> str:
    """Более умное решение через LLM, когда эвристики не хватает"""
    system_prompt = """Ты — опытный Supervisor multi-agent системы разработки.

Доступные агенты:
- researcher — ищет контекст и знания
- coder — пишет код (KAT-Coder)
- reviewer — проверяет код
- end — завершить задачу

Правила:
1. Сначала всегда желательно получить контекст (researcher).
2. После получения контекста — писать код (coder).
3. После написания кода — проверять (reviewer).
4. Если reviewer сказал APPROVED — завершай (end).
5. Если reviewer сказал NEEDS_WORK — можно вернуть на coder.
6. Не вызывай одного и того же агента много раз подряд.

Отвечай ТОЛЬКО одним словом: researcher, coder, reviewer или end."""

    user_content = f"""
Задача: {state['task']}

Текущее состояние:
- Есть контекст: {bool(state.get('context'))}
- Есть код: {bool(state.get('messages'))}
- Последний агент: {state.get('last_agent')}
- Результат ревью: {state.get('review_result', 'ещё не было')[:200] if state.get('review_result') else 'ещё не было'}
- История решений: {state.get('history', [])}
- Итерация: {state.get('iteration', 0)}
"""

    try:
        response = kat_client.chat.completions.create(
            model=KAT_CODER_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.1,
            max_tokens=10
        )
        decision = response.choices[0].message.content.strip().lower()
        if decision in ["researcher", "coder", "reviewer", "end"]:
            return decision
    except Exception as e:
        print(f"Ошибка LLM Supervisor: {e}")
    
    return "end"  # fallback


# === Сборка графа ===

workflow = StateGraph(AgentState)

workflow.add_node("supervisor", supervisor)
workflow.add_node("researcher", researcher)
workflow.add_node("coder", coder)
workflow.add_node("reviewer", reviewer)

workflow.set_entry_point("supervisor")

workflow.add_conditional_edges(
    "supervisor",
    lambda state: state["next"],
    {
        "researcher": "researcher",
        "coder": "coder",
        "reviewer": "reviewer",
        "end": END
    }
)

# Все специалисты возвращаются к Supervisor
workflow.add_edge("researcher", "supervisor")
workflow.add_edge("coder", "supervisor")
workflow.add_edge("reviewer", "supervisor")

app = workflow.compile()
