from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from design_agent_core.config import configure_mlflow
from design_agent_core.core import answer_design_request


class DesignRequest(BaseModel):
    message: str
    user_id: str = "design-api-user"
    session_id: str = "design-api-session"


app = FastAPI(title="Design Agent MLflow AI Studio Sample")


@app.post("/chat")
def chat(request: DesignRequest):
    configure_mlflow()
    return answer_design_request(
        request=request.message,
        user_id=request.user_id,
        session_id=request.session_id,
    )
