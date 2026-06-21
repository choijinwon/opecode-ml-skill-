import os

import mlflow

from offline_weather_agent_313.config import configure_mlflow, get_genai_module
from offline_weather_agent_313.prompts import PROMPT_NAME, PROMPT_TEMPLATE


def main() -> None:
    """MLflow Prompts 화면에서 볼 수 있게 프롬프트를 등록한다."""
    configure_mlflow()
    genai = get_genai_module()
    register_prompt = getattr(genai, "register_prompt", None) if genai else getattr(mlflow, "register_prompt", None)
    set_prompt_alias = getattr(genai, "set_prompt_alias", None) if genai else getattr(mlflow, "set_prompt_alias", None)

    if register_prompt is None or set_prompt_alias is None:
        print("prompt registry API is not available in this MLflow installation")
        return

    model_name = os.getenv("OPENAI_MODEL") or os.getenv("WEATHER_AGENT_MODEL", "qwen2.5-coder:14b")
    version = register_prompt(
        name=PROMPT_NAME,
        template=PROMPT_TEMPLATE,
        commit_message="MLflow 3.13 폐쇄망 날씨 에이전트 프롬프트 등록",
        tags={
            "app": "offline-weather-agent-313",
            "network": "closed",
            "provider": os.getenv("LLM_PROVIDER", "ollama"),
            "model": model_name,
        },
        model_config={
            "model": model_name,
            "temperature": 0.2,
        },
    )
    set_prompt_alias(name=PROMPT_NAME, alias="production", version=version.version)
    print(f"registered prompt: {PROMPT_NAME}")
    print(f"version: {version.version}")
    print(f"uri: prompts:/{PROMPT_NAME}/{version.version}")
    print(f"alias uri: prompts:/{PROMPT_NAME}@production")


if __name__ == "__main__":
    main()
