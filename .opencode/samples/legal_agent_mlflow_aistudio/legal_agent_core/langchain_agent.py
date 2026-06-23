from __future__ import annotations

import mlflow
from mlflow.entities import SpanType

from legal_agent_core.core import classify_legal_topic
from legal_agent_core.llm import call_ai_studio_llm
from legal_agent_core.prompts import render_prompt
from legal_agent_core.retrieval import retrieve_legal_context


@mlflow.trace(name="langchain_legal_agent", span_type=SpanType.AGENT)
def answer_with_langchain(
    question: str,
    user_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, object]:
    """LangChain 스타일의 Prompt + Tool + LLM 조립 예시다.

    운영에서는 Runnable, Tool, ChatModel을 더 세분화할 수 있다.
    샘플은 유지보수를 쉽게 하기 위해 core 함수들을 재사용한다.
    """
    trace_user = user_id or "legal-langchain-user"
    trace_session = session_id or "legal-langchain-session"
    mlflow.update_current_trace(
        user=trace_user,
        session_id=trace_session,
        tags={
            "framework": "langchain",
            "app": "legal-agent-ai-studio",
            "domain": "legal",
        },
        metadata={
            "mlflow.trace.user": trace_user,
            "mlflow.trace.session": trace_session,
            "framework": "langchain",
        },
    )

    runnable_available = _langchain_available()
    topic = classify_legal_topic(question)
    contexts = retrieve_legal_context(question)
    messages = render_prompt(question, topic, contexts)
    answer = call_ai_studio_llm(question, topic, messages, contexts)
    return {
        "framework": "langchain",
        "langchain_core_available": runnable_available,
        "answer": answer,
        "topic": topic,
        "contexts": contexts,
        "user_id": trace_user,
        "session_id": trace_session,
    }


def _langchain_available() -> bool:
    try:
        from langchain_core.runnables import RunnableLambda  # noqa: F401
    except Exception:
        return False
    return True
