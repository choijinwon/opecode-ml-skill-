import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

import mlflow
from mlflow.entities import SpanType

from prompts import PROMPT_NAME, PROMPT_TEMPLATE


# 이 파일은 실제 에이전트 로직을 담는다. 폐쇄망에서도 동작하도록 외부 인터넷 없이
# 로컬 MLflow와 로컬 Ollama/Qwen endpoint만 사용한다.
@dataclass
class WeatherReport:
    city: str
    condition: str
    temperature_c: int
    humidity_percent: int
    wind: str


def load_dotenv(path: str = ".env") -> None:
    """python-dotenv 없이 간단한 KEY=VALUE 형식의 .env 파일을 읽는다."""
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
    """MLflow 호출이 로컬 3.13 tracking server와 지정 experiment로 향하게 설정한다."""
    load_dotenv()
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5013"))
    mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT_NAME", "offline-weather-agent-313"))


def qwen_model_name() -> str:
    """provider prefix가 있으면 제거하고 실제 Qwen 모델명만 남긴다."""
    model = (
        os.getenv("OPENAI_MODEL")
        or os.getenv("WEATHER_AGENT_MODEL")
        or os.getenv("OPENCODE_MODEL", "qwen2.5-coder:14b")
    )
    if "/" in model:
        return model.rsplit("/", 1)[-1]
    return model


def llm_base_url() -> str:
    """LLM_PROVIDER에 따라 OpenAI 호환 endpoint 주소를 고른다."""
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    if provider == "openai":
        return os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    return os.getenv("LOCAL_QWEN_BASE_URL", "http://127.0.0.1:11434/v1").rstrip("/")


def llm_api_key() -> str:
    """OpenAI 방식은 OPENAI_API_KEY, Ollama 방식은 LOCAL_QWEN_API_KEY를 사용한다."""
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    if provider == "openai":
        return os.getenv("OPENAI_API_KEY") or os.getenv("LOCAL_QWEN_API_KEY", "ollama")
    return os.getenv("LOCAL_QWEN_API_KEY", "ollama")


def extract_city(question: str) -> str:
    """샘플 날씨 도구가 사용할 도시명을 질문에서 간단히 추출한다."""
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


def get_genai_module():
    """MLflow 3.13 patch 차이를 고려해 mlflow.genai가 없으면 안전하게 건너뛴다."""
    try:
        import mlflow.genai as genai

        return genai
    except Exception:
        return None


def load_registered_prompt(question: str, weather: WeatherReport) -> list[dict[str, str]] | None:
    """MLflow Prompt Registry 프롬프트를 우선 사용하고, 없으면 소스에 포함된 프롬프트를 쓴다."""
    genai = get_genai_module()
    if genai is None or not hasattr(genai, "load_prompt"):
        return None

    try:
        prompt = genai.load_prompt(
            f"prompts:/{PROMPT_NAME}@production",
            allow_missing=True,
            cache_ttl_seconds=0,
        )
        if prompt is None:
            return None
        return prompt.format(question=question, weather_data=weather_data_text(weather))
    except Exception:
        return None


def render_prompt_messages(question: str, weather: WeatherReport) -> list[dict[str, str]]:
    registered = load_registered_prompt(question, weather)
    if registered is not None:
        return registered

    weather_data = weather_data_text(weather)
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
    """로컬 날씨 도구다. 운영에서는 이 부분을 사내 API나 DB 조회로 교체하면 된다."""
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


@mlflow.trace(name="offline_weather_agent_313", span_type=SpanType.AGENT)
def answer_weather(question: str, user_id: str | None = None, session_id: str | None = None) -> str:
    """최상위 에이전트 span이다. metadata 값은 MLflow user/session 화면에 사용된다."""
    mlflow.update_current_trace(
        metadata={
            "mlflow.trace.user": user_id or os.getenv("WEATHER_AGENT_USER_ID", "offline-user"),
            "mlflow.trace.session": session_id or os.getenv("WEATHER_AGENT_SESSION_ID", "offline-weather-313-session"),
        }
    )
    city = extract_city(question)
    weather = get_weather(city)
    return call_local_qwen(question, weather)
