from __future__ import annotations

import mlflow
from mlflow.entities import SpanType

from offline_weather_agent_core.llm import call_qwen
from offline_weather_agent_core.retrieval import retrieve_context
from offline_weather_agent_core.weather import extract_city, get_weather


@mlflow.trace(name="offline_weather_core_agent", span_type=SpanType.AGENT)
def answer_weather(
    question: str,
    user_id: str | None = None,
    session_id: str | None = None,
) -> str:
    """기본 core 경로를 단계형 agent trace로 실행한다."""
    mlflow.update_current_trace(
        user=user_id or "offline-core-user",
        session_id=session_id or "offline-core-session",
        tags={
            "user_id": user_id or "offline-core-user",
            "session_id": session_id or "offline-core-session",
        },
        metadata={
            "framework": "core",
        },
    )
    city = extract_city(question)
    weather = get_weather(city)
    contexts = retrieve_context(question)
    return call_qwen(question, weather, contexts)
