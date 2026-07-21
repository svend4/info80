import asyncio
from src.agent_graph import app
from src.observability import tracer

async def main():
    task = "Добавь в проект аутентификацию через Google OAuth с защитой от CSRF"
    
    # Начинаем трассу
    trace_id = tracer.start_trace(task)
    print(f"📊 Запущена трасса: {trace_id}")
    
    result = await app.ainvoke({
        "task": task,
        "messages": [],
        "iteration": 0,
        "history": [],
        "waiting_for_human": False,
        "trace_id": trace_id
    })
    
    # Завершаем трассу, если ещё не завершена
    if tracer.current_trace_id:
        tracer.end_trace("completed")
    
    print("\n=== Результат ===")
    print(result.get("messages", ["Нет результата"])[-1])
    print("\n=== Метрики ===")
    print(tracer.get_metrics())

if __name__ == "__main__":
    asyncio.run(main())
