from graphiti import Graphiti
from dotenv import load_dotenv
import os

load_dotenv()

# Подключаемся к Neo4j (из docker-compose)
graph = Graphiti(
    uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    user=os.getenv("NEO4J_USER", "neo4j"),
    password=os.getenv("NEO4J_PASSWORD", "password123")
)

PROJECT_ID = os.getenv("PROJECT_ID", "default-project")


async def get_project_context(task: str) -> str:
    """Получаем релевантный контекст из Graphiti"""
    try:
        results = await graph.search(
            query=task,
            num_results=5
        )
        return "\n".join([str(r) for r in results]) if results else ""
    except Exception as e:
        print(f"Graphiti search error: {e}")
        return ""


async def find_relevant_cards(task: str):
    results = await graph.search(query=task, num_results=5)
    return [r for r in results if "DataCard" in str(r)]
