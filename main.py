import asyncio
from src.agent_graph import app

async def main():
    result = await app.ainvoke({
        "task": "Добавь в проект аутентификацию через Google OAuth с защитой от CSRF",
        "messages": []
    })
    
    print("=== Результат ===")
    print(result.get("messages", ["Нет результата"])[-1])

if __name__ == "__main__":
    asyncio.run(main())
