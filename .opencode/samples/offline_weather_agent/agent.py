import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

import mlflow
import mlflow.genai
from mlflow.entities import SpanType

from prompts import PROMPT_NAME, PROMPT_TEMPLATE


@dataclass
class WeatherReport:
    city: str
    condition: str
    temperature_c: int
    humidity_percent: int
    wind: str


def load_dotenv(path: str = ".env") -> None:
    if not os.path.exists(path):
        return

    with open(path, encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def configure_mlflow() -> None:
    load_dotenv()
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5001"))
    mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT_NAME", "offline-weather-agent"))


def qwen_model_name() -> str:
    model = os.getenv("WEATHER_AGENT_MODEL") or os.getenv("OPENCODE_MODEL", "qwen2.5-coder:14b")
    if "/" in model:
        return model.rsplit("/", 1)[-1]
    return model


def extract_city(question: str) -> str:
    for city in ("서울", "부산", "제주", "대구", "인천", "seoul", "busan", "jeju", "daegu", "incheon"):
        if city.lower() in question.lower():
            return city
    return "서울"


def weather_data_text(weather: WeatherReport) -> str:
    return (
        f"city={weather.city}, condition={weather.condition}, "
        f"temperature_c={weather.temperature_c}, humidity_percent={weather.humidity_percent}, "
        f"wind={weather.wind}"
    )


def render_prompt_messages(question: str, weather: WeatherReport) -> list[dict[str, str]]:
    weather_data = weather_data_text(weather)
    prompt = mlflow.genai.load_prompt(
        f"prompts:/{PROMPT_NAME}@production",
        allow_missing=True,
        cache_ttl_seconds=0,
    )
    if prompt is not None:
        return prompt.format(question=question, weather_data=weather_data)

    return [
        {
            "role": message["role"],
            "content": message["content"]
            .replace("{{question}}", question)
            .replace("{{weather_data}}", weather_data),
        }
        for message in PROMPT_TEMPLATE
    ]


@mlflow.trace(span_type=SpanType.TOOL)
def get_weather(city: str) -> WeatherReport:
    reports = {
        "seoul": WeatherReport("Seoul", "clear", 27, 48, "light breeze"),
        "서울": WeatherReport("Seoul", "clear", 27, 48, "light breeze"),
        "busan": WeatherReport("Busan", "cloudy", 24, 68, "coastal wind"),
        "부산": WeatherReport("Busan", "cloudy", 24, 68, "coastal wind"),
        "jeju": WeatherReport("Jeju", "rain showers", 23, 82, "moderate wind"),
        "제주": WeatherReport("Jeju", "rain showers", 23, 82, "moderate wind"),
        "daegu": WeatherReport("Daegu", "hot", 30, 42, "calm"),
        "대구": WeatherReport("Daegu", "hot", 30, 42, "calm"),
        "incheon": WeatherReport("Incheon", "misty", 22, 73, "sea breeze"),
        "인천": WeatherReport("Incheon", "misty", 22, 73, "sea breeze"),
    }
    return reports.get(city.lower(), WeatherReport(city, "partly cloudy", 25, 55, "calm"))


@mlflow.trace(span_type=SpanType.LLM)
def call_local_qwen(question: str, weather: WeatherReport) -> str:
    base_url = os.getenv("LOCAL_QWEN_BASE_URL", "http://127.0.0.1:11434/v1").rstrip("/")
    api_key = os.getenv("LOCAL_QWEN_API_KEY", "ollama")
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


@mlflow.trace(name="offline_weather_agent", span_type=SpanType.AGENT)
def answer_weather(question: str, user_id: str | None = None, session_id: str | None = None) -> str:
    mlflow.update_current_trace(
        metadata={
            "mlflow.trace.user": user_id or os.getenv("WEATHER_AGENT_USER_ID", "offline-user"),
            "mlflow.trace.session": session_id or os.getenv("WEATHER_AGENT_SESSION_ID", "offline-weather-session"),
        }
    )
    city = extract_city(question)
    weather = get_weather(city)
    return call_local_qwen(question, weather)
