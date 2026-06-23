from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from legal_agent_core.config import configure_mlflow
from legal_agent_core.core import answer_legal_question


class ChatRequest(BaseModel):
    message: str
    user_id: str = "legal-api-user"
    session_id: str = "legal-api-session"


app = FastAPI(title="Legal Agent MLflow AI Studio Sample")


@app.post("/chat")
def chat(request: ChatRequest):
    configure_mlflow()
    return answer_legal_question(
        question=request.message,
        user_id=request.user_id,
        session_id=request.session_id,
    )
