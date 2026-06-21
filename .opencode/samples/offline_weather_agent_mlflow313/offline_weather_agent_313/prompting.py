from offline_weather_agent_313.config import get_genai_module
from offline_weather_agent_313.prompts import PROMPT_NAME, PROMPT_TEMPLATE
from offline_weather_agent_313.weather import WeatherReport, weather_data_text


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

