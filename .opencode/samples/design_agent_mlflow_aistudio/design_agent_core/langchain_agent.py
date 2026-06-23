from __future__ import annotations

import mlflow
from mlflow.entities import SpanType

from design_agent_core.core import classify_design_task
from design_agent_core.llm import call_ai_studio_llm
from design_agent_core.prompts import render_prompt
from design_agent_core.retrieval import retrieve_design_guidelines


@mlflow.trace(name="langchain_design_agent", span_type=SpanType.AGENT)
def answer_with_langchain(
    request: str,
    user_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, object]:
    trace_user = user_id or "design-langchain-user"
    trace_session = session_id or "design-langchain-session"
    mlflow.update_current_trace(
        user=trace_user,
        session_id=trace_session,
        tags={"framework": "langchain", "app": "design-agent-ai-studio", "domain": "design"},
        metadata={
            "mlflow.trace.user": trace_user,
            "mlflow.trace.session": trace_session,
            "framework": "langchain",
        },
    )
    task_type = classify_design_task(request)
    guidelines = retrieve_design_guidelines(request)
    messages = render_prompt(request, task_type, guidelines)
    answer = call_ai_studio_llm(request, task_type, messages, guidelines)
    return {
        "framework": "langchain",
        "langchain_core_available": _langchain_available(),
        "answer": answer,
        "task_type": task_type,
        "guidelines": guidelines,
        "user_id": trace_user,
        "session_id": trace_session,
    }


def _langchain_available() -> bool:
    try:
        from langchain_core.runnables import RunnableLambda  # noqa: F401
    except Exception:
        return False
    return True
