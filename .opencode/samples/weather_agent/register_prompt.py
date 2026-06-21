import os

import mlflow
import mlflow.genai

from prompts import WEATHER_AGENT_PROMPT_NAME, WEATHER_AGENT_PROMPT_TEMPLATE
from weather_agent import load_dotenv


def main() -> None:
    load_dotenv()
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5001"))
    mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT_NAME", "weather-agent"))

    prompt_version = mlflow.genai.register_prompt(
        name=WEATHER_AGENT_PROMPT_NAME,
        template=WEATHER_AGENT_PROMPT_TEMPLATE,
        commit_message="Add weather agent chat prompt for local Qwen tracing demo.",
        tags={
            "app": "weather-agent",
            "provider": "ollama",
            "model": os.getenv("WEATHER_AGENT_MODEL", "qwen2.5-coder:14b"),
        },
        model_config={
            "model": os.getenv("WEATHER_AGENT_MODEL", "qwen2.5-coder:14b"),
            "temperature": 0.2,
        },
    )
    mlflow.genai.set_prompt_alias(
        name=WEATHER_AGENT_PROMPT_NAME,
        alias="production",
        version=prompt_version.version,
    )

    print(f"registered prompt: {WEATHER_AGENT_PROMPT_NAME}")
    print(f"version: {prompt_version.version}")
    print(f"uri: prompts:/{WEATHER_AGENT_PROMPT_NAME}/{prompt_version.version}")
    print(f"alias uri: prompts:/{WEATHER_AGENT_PROMPT_NAME}@production")


if __name__ == "__main__":
    main()
