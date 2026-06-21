from offline_weather_agent_core.config import get_genai_module
from offline_weather_agent_core.prompts import PROMPT_NAME, PROMPT_TEMPLATE
from offline_weather_agent_core.retrieval import context_text
from offline_weather_agent_core.weather import WeatherReport, weather_data_text


def load_registered_prompt(
    question: str,
    weather: WeatherReport,
    contexts: list[dict[str, str]] | None = None,
) -> list[dict[str, str]] | None:
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
        return prompt.format(
            question=question,
            weather_data=weather_data_text(weather),
            rag_context=context_text(contexts or []),
        )
    except Exception:
        return None


def render_prompt_messages(
    question: str,
    weather: WeatherReport,
    contexts: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    registered = load_registered_prompt(question, weather, contexts)
    if registered is not None:
        return registered

    weather_data = weather_data_text(weather)
    rag_context = context_text(contexts or [])
    return [
        {
            "role": message["role"],
            "content": message["content"]
            .replace("{{question}}", question)
            .replace("{{weather_data}}", weather_data)
            .replace("{{rag_context}}", rag_context),
        }
        for message in PROMPT_TEMPLATE
    ]


def to_langchain_messages(messages: list[dict[str, str]]):
    """Prompt registry/소스 프롬프트 메시지를 LangChain 메시지 객체로 바꾼다."""
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

    converted = []
    for message in messages:
        role = message.get("role", "user")
        content = message.get("content", "")
        if role == "system":
            converted.append(SystemMessage(content=content))
        elif role == "assistant":
            converted.append(AIMessage(content=content))
        else:
            converted.append(HumanMessage(content=content))
    return converted
