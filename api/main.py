from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.agent_graph import app as agent_app

app = FastAPI(title="KAT-Coder Multi-Agent API", version="1.1.0")

class TaskRequest(BaseModel):
    task: str

class HumanFeedbackRequest(BaseModel):
    decision: str          # "approve" | "reject" | "modify"
    feedback: Optional[str] = None
    current_state: dict    # состояние, возвращённое предыдущим /run

@app.get("/")
async def root():
    return {
        "message": "KAT-Coder Multi-Agent + Data Cards + Human-in-the-loop API",
        "endpoints": ["/run", "/human-feedback"]
    }

@app.post("/run")
async def run_agent(request: TaskRequest):
    result = await agent_app.ainvoke({
        "task": request.task,
        "messages": [],
        "iteration": 0,
        "history": [],
        "waiting_for_human": False
    })
    
    return {
        "result": result.get("messages", [""])[-1] if result.get("messages") else None,
        "created_card_id": result.get("created_card_id"),
        "waiting_for_human": result.get("waiting_for_human", False),
        "review_result": result.get("review_result"),
        "history": result.get("history"),
        "full_state": result
    }

@app.post("/human-feedback")
async def human_feedback(request: HumanFeedbackRequest):
    """
    Продолжить выполнение после решения человека.
    """
    if request.decision not in ["approve", "reject", "modify"]:
        raise HTTPException(400, "decision must be approve | reject | modify")
    
    state = request.current_state.copy()
    state["human_decision"] = request.decision
    state["human_feedback"] = request.feedback
    state["waiting_for_human"] = False
    
    result = await agent_app.ainvoke(state)
    
    return {
        "result": result.get("messages", [""])[-1] if result.get("messages") else None,
        "waiting_for_human": result.get("waiting_for_human", False),
        "history": result.get("history"),
        "full_state": result
    }
