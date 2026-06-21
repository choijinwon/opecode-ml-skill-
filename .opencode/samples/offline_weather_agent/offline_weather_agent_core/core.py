import os

import mlflow
from mlflow.entities import SpanType

from offline_weather_agent_core.llm import call_qwen
from offline_weather_agent_core.retrieval import retrieve_context
from offline_weather_agent_core.weather import extract_city, get_weather


@mlflow.trace(name="offline_weather_agent_core", span_type=SpanType.AGENT)
def answer_weather(question: str, user_id: str | None = None, session_id: str | None = None) -> str:
    """최상위 에이전트 span이다. metadata 값은 MLflow user/session 화면에 사용된다."""
    resolved_user_id = user_id or os.getenv("WEATHER_AGENT_USER_ID", "offline-user")
    resolved_session_id = session_id or os.getenv("WEATHER_AGENT_SESSION_ID", "offline-weather-session")
    mlflow.update_current_trace(
        user=resolved_user_id,
        session_id=resolved_session_id,
        tags={
            "user_id": resolved_user_id,
            "session_id": resolved_session_id,
        },
        metadata={
            "app": "offline-weather-agent",
            "entrypoint": "web-or-pyfunc",
        }
    )
    city = extract_city(question)
    weather = get_weather(city)
    contexts = retrieve_context(question)
    return call_qwen(question, weather, contexts)
