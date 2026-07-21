from fastapi import FastAPI
from pydantic import BaseModel
from src.agent_graph import app as agent_app

app = FastAPI(title="KAT-Coder Multi-Agent API", version="1.0.0")

class TaskRequest(BaseModel):
    task: str

@app.get("/")
async def root():
    return {"message": "KAT-Coder Multi-Agent + Data Cards API is running"}

@app.post("/run")
async def run_agent(request: TaskRequest):
    result = await agent_app.ainvoke({
        "task": request.task,
        "messages": []
    })
    return {
        "result": result.get("messages", [""])[-1] if result.get("messages") else None,
        "created_card_id": result.get("created_card_id"),
        "full_state": result
    }
