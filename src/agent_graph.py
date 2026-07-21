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
MAX_ITERATIONS = 10


class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    task: str
    context: str
    next: str
    created_card_id: str
    iteration: int
    history: List[str]
    last_agent: Optional[str]
    review_result: Optional[str]
    # Human-in-the-loop
    waiting_for_human: bool
    human_feedback: Optional[str]
    human_decision: Optional[str]   # "approve" | "reject" | "modify" | None


# === Специалисты ===

async def researcher(state: AgentState):
    print("🔍 Researcher: ищу контекст...")
    context = await get_project_context(state["task"])
    return {
        "context": context or "Контекст не найден",
        "next": "supervisor",
        "last_agent": "researcher",
        "iteration": state.get("iteration", 0) + 1,
        "waiting_for_human": False
    }


async def coder(state: AgentState):
    print("💻 Coder (KAT-Coder): генерирую код...")
    
    extra = ""
    if state.get("human_feedback"):
        extra = f"\n\n=== Обратная связь от человека ===\n{state['human_feedback']}\nУчти эти замечания при генерации."

    prompt = f"""
Ты — KAT-Coder-Pro V2.5.

=== Контекст проекта ===
{state.get('context', 'Контекст отсутствует')}

=== Задача ===
{state['task']}
{extra}

Требования:
1. Напиши качественный и безопасный код.
2. В конце обязательно добавь:
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
        "iteration": state.get("iteration", 0) + 1,
        "waiting_for_human": False,
        "human_feedback": None
    }


async def reviewer(state: AgentState):
    print("🔎 Reviewer: проверяю код...")
    last_code = state["messages"][-1] if state.get("messages") else ""
    
    prompt = f"""Ты — строгий code reviewer.

Проверь код на корректность, безопасность и best practices.

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
        "iteration": state.get("iteration", 0) + 1,
        "waiting_for_human": False
    }


async def human_approval(state: AgentState):
    """
    Узел Human-in-the-loop.
    Система останавливается и ждёт решения человека.
    """
    print("👤 Ожидание решения человека (Human-in-the-loop)...")
    print("   Доступные действия: approve / reject / modify + комментарий")
    
    # В реальном использовании состояние будет обновлено извне
    # (через API или Streamlit), а граф продолжит работу.
    return {
        "waiting_for_human": True,
        "next": "supervisor",          # После получения feedback вернёмся к supervisor
        "last_agent": "human_approval",
        "iteration": state.get("iteration", 0) + 1
    }


# === Supervisor ===

async def supervisor(state: AgentState):
    iteration = state.get("iteration", 0)
    history = state.get("history", [])
    last_agent = state.get("last_agent")
    has_context = bool(state.get("context"))
    has_code = bool(state.get("messages"))
    review = state.get("review_result", "") or ""
    human_decision = state.get("human_decision")

    # Защита от бесконечных циклов
    if iteration >= MAX_ITERATIONS:
        print(f"⚠️ Достигнут лимит итераций ({MAX_ITERATIONS}). Завершаем.")
        return {"next": "end", "history": history + ["end (max iterations)"]}

    # === Обработка решения человека ===
    if human_decision:
        if human_decision == "approve":
            print("✅ Человек одобрил результат. Завершаем.")
            return {"next": "end", "history": history + ["end (human approved)"]}
        elif human_decision == "reject":
            print("❌ Человек отклонил. Завершаем без сохранения.")
            return {"next": "end", "history": history + ["end (human rejected)"]}
        elif human_decision == "modify":
            print("✏️ Человек запросил доработку. Отправляем на coder.")
            return {
                "next": "coder",
                "history": history + ["coder (human modify)"],
                "human_decision": None
            }

    # === Обычная логика ===
    if not has_context and last_agent != "researcher":
        decision = "researcher"
    elif not has_code and last_agent != "coder":
        decision = "coder"
    elif has_code and last_agent == "coder":
        decision = "reviewer"
    elif "APPROVED" in review.upper() and last_agent == "reviewer":
        # После успешного ревью спрашиваем человека
        decision = "human_approval"
    elif "NEEDS_WORK" in review.upper() and last_agent == "reviewer":
        # При проблемах тоже можем спросить человека
        decision = "human_approval"
    else:
        decision = await _llm_decide(state)

    # Защита от циклов
    if len(history) >= 2 and history[-1] == decision and history[-2] == decision:
        print(f"⚠️ Обнаружен цикл на '{decision}'. Завершаем.")
        decision = "end"

    print(f"🧠 Supervisor → {decision} (iteration {iteration})")
    
    return {
        "next": decision,
        "history": history + [decision],
        "iteration": iteration
    }


async def _llm_decide(state: AgentState) -> str:
    system_prompt = """Ты — Supervisor multi-agent системы.
Доступные действия: researcher, coder, reviewer, human_approval, end.
Отвечай только одним словом."""

    user_content = f"""
Задача: {state['task']}
Есть контекст: {bool(state.get('context'))}
Есть код: {bool(state.get('messages'))}
Последний агент: {state.get('last_agent')}
Ревью: {(state.get('review_result') or '')[:150]}
История: {state.get('history', [])}
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
        if decision in ["researcher", "coder", "reviewer", "human_approval", "end"]:
            return decision
    except Exception as e:
        print(f"Ошибка LLM Supervisor: {e}")
    
    return "end"


# === Сборка графа ===

workflow = StateGraph(AgentState)

workflow.add_node("supervisor", supervisor)
workflow.add_node("researcher", researcher)
workflow.add_node("coder", coder)
workflow.add_node("reviewer", reviewer)
workflow.add_node("human_approval", human_approval)

workflow.set_entry_point("supervisor")

workflow.add_conditional_edges(
    "supervisor",
    lambda state: state["next"],
    {
        "researcher": "researcher",
        "coder": "coder",
        "reviewer": "reviewer",
        "human_approval": "human_approval",
        "end": END
    }
)

workflow.add_edge("researcher", "supervisor")
workflow.add_edge("coder", "supervisor")
workflow.add_edge("reviewer", "supervisor")
workflow.add_edge("human_approval", "supervisor")

app = workflow.compile()
