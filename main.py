from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from dotenv import load_dotenv

load_dotenv()

from agent import run_agent
from tools import get_all_leads

app = FastAPI(title="AutoStream Lead Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class AgentStateIn(BaseModel):
    collecting_lead: bool = False
    lead_data: dict = {}
    lead_captured: bool = False

class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []
    agent_state: Optional[AgentStateIn] = None

class ChatResponse(BaseModel):
    response: str
    intent: str
    collecting_lead: bool
    lead_captured: bool
    lead_data: dict

@app.get("/")
def root():
    return {"status": "AutoStream Lead Agent is running"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        # Build clean history (plain role/content dicts only)
        history = [{"role": m.role, "content": m.content} for m in request.history]

        # Inject agent state via _state message so agent.py can pick it up
        if request.agent_state and (
            request.agent_state.collecting_lead
            or request.agent_state.lead_data
            or request.agent_state.lead_captured
        ):
            history.append({
                "role": "_state",
                "content": "",
                "collecting_lead": request.agent_state.collecting_lead,
                "lead_data": request.agent_state.lead_data,
                "lead_captured": request.agent_state.lead_captured,
            })

        result = run_agent(request.message, history)
        return ChatResponse(
            response=result["response"],
            intent=result["intent"],
            collecting_lead=result["collecting_lead"],
            lead_captured=result["lead_captured"],
            lead_data=result["lead_data"],
        )
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print("BACKEND ERROR:", error_detail)
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/leads")
def get_leads():
    leads = get_all_leads()
    return {"count": len(leads), "leads": leads}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
