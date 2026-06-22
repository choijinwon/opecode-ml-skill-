import os

import mlflow
import pandas as pd

from offline_weather_agent_core.config import configure_mlflow
from offline_weather_agent_core.core import answer_weather


class OfflineWeatherAgentModel(mlflow.pyfunc.PythonModel):
    """MLflow Model Registry에 올릴 pyfunc 모델 래퍼다."""

    def predict(self, context, model_input, params=None):
        """DataFrame/list/string 입력을 받아 날씨 에이전트 답변 리스트로 변환한다."""
        if isinstance(model_input, pd.DataFrame):
            questions = model_input["question"].fillna("서울 날씨 알려줘").tolist()
        elif isinstance(model_input, list):
            questions = model_input
        else:
            questions = [str(model_input)]

        return [answer_weather(str(question)) for question in questions]


def main() -> None:
    """기본 pyfunc 형태로 오프라인 날씨 에이전트를 MLflow에 등록한다."""
    configure_mlflow()
    input_example = pd.DataFrame({"question": ["서울 날씨 알려줘"]})
    model_name = "offline-weather-agent-qwen"

    with mlflow.start_run(run_name="register-offline-weather-agent"):
        info = mlflow.pyfunc.log_model(
            artifact_path="offline_weather_agent",
            python_model=OfflineWeatherAgentModel(),
            input_example=input_example,
            registered_model_name=model_name,
            pip_requirements=[
                f"mlflow=={mlflow.__version__}",
                "fastapi",
                "langchain",
                "langchain-openai",
                "langgraph",
                "pandas",
                "pydantic",
            ],
            metadata={
                "base_model": os.getenv("OPENAI_MODEL") or os.getenv("WEATHER_AGENT_MODEL", "qwen2.5-coder:14b"),
                "provider": os.getenv("LLM_PROVIDER", "ollama"),
                "network": "closed",
            },
        )

    print(f"registered model: {model_name}")
    print(f"model uri: {info.model_uri}")


if __name__ == "__main__":
    main()
