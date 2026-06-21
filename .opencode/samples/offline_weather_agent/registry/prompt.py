import os

import mlflow.genai

from offline_weather_agent_core.config import configure_mlflow
from offline_weather_agent_core.prompts import PROMPT_NAME, PROMPT_TEMPLATE


def main() -> None:
    """MLflow Prompt Registry에 날씨 에이전트 프롬프트를 등록한다."""
    configure_mlflow()
    model_name = os.getenv("OPENAI_MODEL") or os.getenv("WEATHER_AGENT_MODEL", "qwen2.5-coder:14b")

    version = mlflow.genai.register_prompt(
        name=PROMPT_NAME,
        template=PROMPT_TEMPLATE,
        commit_message="Register closed-network weather agent prompt.",
        tags={
            "app": "offline-weather-agent",
            "network": "closed",
            "provider": os.getenv("LLM_PROVIDER", "ollama"),
            "model": model_name,
        },
        model_config={
            "model": model_name,
            "temperature": 0.2,
        },
    )
    mlflow.genai.set_prompt_alias(name=PROMPT_NAME, alias="production", version=version.version)
    print(f"registered prompt: {PROMPT_NAME}")
    print(f"version: {version.version}")
    print(f"uri: prompts:/{PROMPT_NAME}/{version.version}")
    print(f"alias uri: prompts:/{PROMPT_NAME}@production")
