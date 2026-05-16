from fastapi import FastAPI
from pydantic import BaseModel
from agent import WorkAgent

app = FastAPI(title="Work Agent API")

agent = WorkAgent()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    reply = agent.chat(req.message)
    return ChatResponse(reply=reply)


@app.post("/reset")
def reset():
    agent.reset()
    return {"status": "ok", "message": "会话已重置"}


@app.get("/health")
def health():
    return {"status": "ok"}
