import json
import urllib.error
import urllib.request

import mlflow
from mlflow.entities import SpanType

from offline_weather_agent_313.config import llm_api_key, llm_base_url, qwen_model_name
from offline_weather_agent_313.prompting import render_prompt_messages
from offline_weather_agent_313.weather import WeatherReport


@mlflow.trace(span_type=SpanType.LLM)
def call_qwen(question: str, weather: WeatherReport) -> str:
    """OpenAI 호환 chat completions endpoint로 Qwen 모델을 호출한다."""
    base_url = llm_base_url()
    api_key = llm_api_key()
    payload = {
        "model": qwen_model_name(),
        "messages": render_prompt_messages(question, weather),
        "temperature": 0.2,
        "stream": False,
    }
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"].strip()
    except (KeyError, TimeoutError, urllib.error.URLError, urllib.error.HTTPError) as exc:
        return (
            f"{weather.city}은 현재 {weather.condition}, {weather.temperature_c}도입니다. "
            f"습도는 {weather.humidity_percent}%이고 바람은 {weather.wind} 수준이에요. "
            f"(local fallback: {exc.__class__.__name__})"
        )

