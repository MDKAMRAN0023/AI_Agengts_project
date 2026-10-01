from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.agents.graph import graph


app = FastAPI(
    title="Agentic RAG Copilot",
    description="Agentic RAG Question Answering API",
    version="1.0.0"
)


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# REQUEST MODEL
# =========================

class QuestionRequest(BaseModel):

    question: str
    session_id: str = "default-session"


# =========================
# RESPONSE MODEL
# =========================

class QuestionResponse(BaseModel):

    question: str
    route: str
    answer: str


# =========================
# ROOT
# =========================

@app.get("/")
def root():

    return {
        "message": "Agentic RAG Copilot API is running"
    }


# =========================
# ASK
# =========================

@app.post("/ask", response_model=QuestionResponse)
def ask(request: QuestionRequest):

    result = graph.invoke({
        "question": request.question,
        "session_id": request.session_id
    })

    return {
        "question": result["question"],
        "route": result["route"],
        "answer": result.get(
            "answer",
            "I don't know."
        )
    }