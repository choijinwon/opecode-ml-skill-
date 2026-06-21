import os

import mlflow
from mlflow.entities import SpanType

from offline_weather_agent_core.llm import call_qwen
from offline_weather_agent_core.weather import extract_city, get_weather


@mlflow.trace(name="offline_weather_agent_core", span_type=SpanType.AGENT)
def answer_weather(question: str, user_id: str | None = None, session_id: str | None = None) -> str:
    """최상위 에이전트 span이다. metadata 값은 MLflow user/session 화면에 사용된다."""
    mlflow.update_current_trace(
        metadata={
            "mlflow.trace.user": user_id or os.getenv("WEATHER_AGENT_USER_ID", "offline-user"),
            "mlflow.trace.session": session_id or os.getenv("WEATHER_AGENT_SESSION_ID", "offline-weather-session"),
        }
    )
    city = extract_city(question)
    weather = get_weather(city)
    return call_qwen(question, weather)

