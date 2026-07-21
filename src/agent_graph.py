from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
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


class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    task: str
    context: str
    next: str
    created_card_id: str


async def researcher(state: AgentState):
    context = await get_project_context(state["task"])
    return {"context": context, "next": "coder"}


async def coder(state: AgentState):
    prompt = f"""
Ты — KAT-Coder-Pro V2.5.

=== Память проекта ===
{state.get('context', '')}

=== Задача ===
{state['task']}

После генерации кода в конце обязательно добавь:
CARD_NAME: <короткое название карточки>
CARD_DESCRIPTION: <краткое описание что делает код>
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
        "next": "reviewer",
        "created_card_id": new_card.id
    }


async def reviewer(state: AgentState):
    last_code = state["messages"][-1] if state.get("messages") else ""
    prompt = f"Проверь этот код на качество, безопасность и best practices:\n\n{last_code}\n\nЕсли всё хорошо — напиши APPROVED. Если есть замечания — укажи их."
    
    response = kat_client.chat.completions.create(
        model=KAT_CODER_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    review = response.choices[0].message.content
    return {"messages": [review], "next": "end"}


async def supervisor(state: AgentState):
    system_prompt = """Ты — Supervisor. Реши, кого вызвать следующим:
- researcher (если нет контекста)
- coder (если нужно написать код)
- reviewer (если нужно проверить код)
- end (если задача выполнена)

Отвечай только одним словом: researcher, coder, reviewer или end."""

    response = kat_client.chat.completions.create(
        model=KAT_CODER_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Текущая задача: {state['task']}\nКонтекст: {state.get('context', 'нет')}\nСообщения: {len(state.get('messages', []))}"}
        ],
        temperature=0.1,
        max_tokens=10
    )
    decision = response.choices[0].message.content.strip().lower()
    if decision not in ["researcher", "coder", "reviewer", "end"]:
        decision = "coder"
    return {"next": decision}


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

workflow.add_edge("researcher", "supervisor")
workflow.add_edge("coder", "supervisor")
workflow.add_edge("reviewer", "supervisor")

app = workflow.compile()
