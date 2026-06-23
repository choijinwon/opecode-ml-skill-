from __future__ import annotations

import mlflow
from mlflow.entities import SpanType

from design_agent_core.config import ai_studio_settings
from design_agent_core.llm import call_ai_studio_llm
from design_agent_core.prompts import render_prompt
from design_agent_core.retrieval import retrieve_design_guidelines


@mlflow.trace(name="classify_design_task", span_type=SpanType.TOOL)
def classify_design_task(request: str) -> str:
    if any(word in request.lower() for word in ["대시보드", "admin", "관리자", "saas"]):
        return "운영형 UI/대시보드"
    if any(word in request.lower() for word in ["온보딩", "가입", "시작"]):
        return "온보딩 UX"
    if any(word in request.lower() for word in ["랜딩", "홈페이지", "마케팅"]):
        return "랜딩/마케팅 페이지"
    if any(word in request.lower() for word in ["브랜드", "로고", "톤", "카피"]):
        return "브랜드/콘텐츠 디자인"
    return "일반 UX/UI 디자인"


@mlflow.trace(name="design_agent", span_type=SpanType.AGENT)
def answer_design_request(
    request: str,
    user_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, object]:
    settings = ai_studio_settings()
    trace_user = user_id or "design-demo-user"
    trace_session = session_id or "design-demo-session"
    mlflow.update_current_trace(
        user=trace_user,
        session_id=trace_session,
        tags={
            "app": "design-agent-ai-studio",
            "domain": "design",
            "user_id": trace_user,
            "session_id": trace_session,
        },
        metadata={
            "mlflow.trace.user": trace_user,
            "mlflow.trace.session": trace_session,
            "app": "design-agent-ai-studio",
            "domain": "design",
            "ai_studio_model": settings["model"],
        },
    )
    task_type = classify_design_task(request)
    guidelines = retrieve_design_guidelines(request)
    messages = render_prompt(request, task_type, guidelines)
    answer = call_ai_studio_llm(request, task_type, messages, guidelines)
    return {
        "answer": answer,
        "task_type": task_type,
        "guidelines": guidelines,
        "user_id": trace_user,
        "session_id": trace_session,
        "model": settings["model"],
    }
