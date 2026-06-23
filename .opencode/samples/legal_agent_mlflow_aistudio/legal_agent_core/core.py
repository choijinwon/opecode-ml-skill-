from __future__ import annotations

import mlflow
from mlflow.entities import SpanType

from legal_agent_core.config import ai_studio_settings
from legal_agent_core.llm import call_ai_studio_llm
from legal_agent_core.prompts import render_prompt
from legal_agent_core.retrieval import retrieve_legal_context


@mlflow.trace(name="classify_legal_topic", span_type=SpanType.TOOL)
def classify_legal_topic(question: str) -> str:
    """질문을 단순 분류한다. 운영에서는 분류 모델/룰/API로 교체 가능하다."""
    if any(word in question for word in ["해고", "근로", "임금", "연차", "징계"]):
        return "근로/인사"
    if any(word in question for word in ["개인정보", "동의", "파기", "위탁"]):
        return "개인정보"
    if any(word in question for word in ["저작권", "상표", "특허", "라이선스"]):
        return "지식재산권"
    if any(word in question for word in ["계약", "해지", "위약", "통보"]):
        return "계약"
    return "일반 법률 문의"


@mlflow.trace(name="legal_agent", span_type=SpanType.AGENT)
def answer_legal_question(
    question: str,
    user_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, object]:
    """법률 에이전트 실행 진입점이다.

    MLflow Traces:
    - root span: legal_agent
    - child span: classify_legal_topic, retrieve_legal_context, call_ai_studio_llm

    MLflow Chat Sessions:
    - mlflow.trace.user와 mlflow.trace.session metadata로 사용자/세션을 묶는다.
    """
    settings = ai_studio_settings()
    trace_user = user_id or "legal-demo-user"
    trace_session = session_id or "legal-demo-session"
    mlflow.update_current_trace(
        user=trace_user,
        session_id=trace_session,
        tags={
            "app": "legal-agent-ai-studio",
            "domain": "legal",
            "user_id": trace_user,
            "session_id": trace_session,
        },
        metadata={
            "mlflow.trace.user": trace_user,
            "mlflow.trace.session": trace_session,
            "app": "legal-agent-ai-studio",
            "domain": "legal",
            "ai_studio_model": settings["model"],
        },
    )

    topic = classify_legal_topic(question)
    contexts = retrieve_legal_context(question)
    messages = render_prompt(question, topic, contexts)
    answer = call_ai_studio_llm(question, topic, messages, contexts)

    return {
        "answer": answer,
        "topic": topic,
        "contexts": contexts,
        "user_id": trace_user,
        "session_id": trace_session,
        "model": settings["model"],
    }
