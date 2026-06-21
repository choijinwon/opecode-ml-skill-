import os

import mlflow
import mlflow.genai

from agent import configure_mlflow
from prompts import PROMPT_NAME, PROMPT_TEMPLATE


def main() -> None:
    configure_mlflow()
    version = mlflow.genai.register_prompt(
        name=PROMPT_NAME,
        template=PROMPT_TEMPLATE,
        commit_message="Register closed-network weather agent prompt.",
        tags={
            "app": "offline-weather-agent",
            "network": "closed",
            "provider": "ollama",
            "model": os.getenv("WEATHER_AGENT_MODEL", "qwen2.5-coder:14b"),
        },
        model_config={
            "model": os.getenv("WEATHER_AGENT_MODEL", "qwen2.5-coder:14b"),
            "temperature": 0.2,
        },
    )
    mlflow.genai.set_prompt_alias(name=PROMPT_NAME, alias="production", version=version.version)
    print(f"registered prompt: {PROMPT_NAME}")
    print(f"version: {version.version}")
    print(f"uri: prompts:/{PROMPT_NAME}/{version.version}")
    print(f"alias uri: prompts:/{PROMPT_NAME}@production")


if __name__ == "__main__":
    main()
