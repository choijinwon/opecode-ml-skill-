import os

import mlflow
import pandas as pd

from offline_weather_agent_313.config import configure_mlflow
from offline_weather_agent_313.core import answer_weather


class OfflineWeatherAgent313Model(mlflow.pyfunc.PythonModel):
    """채팅 에이전트를 MLflow pyfunc 모델처럼 호출하기 위한 wrapper다."""

    def predict(self, context, model_input, params=None):
        """DataFrame/list/string 입력을 질문 리스트로 바꿔 에이전트 답변을 반환한다."""
        if isinstance(model_input, pd.DataFrame):
            questions = model_input["question"].fillna("서울 날씨 알려줘").tolist()
        elif isinstance(model_input, list):
            questions = model_input
        else:
            questions = [str(model_input)]

        return [answer_weather(str(question)) for question in questions]


def main() -> None:
    """MLflow 3.13 Model Registry에 날씨 에이전트 wrapper를 등록한다."""
    configure_mlflow()
    input_example = pd.DataFrame({"question": ["서울 날씨 알려줘"]})
    model_name = "offline-weather-agent-313-qwen"

    with mlflow.start_run(run_name="register-offline-weather-agent-313"):
        info = mlflow.pyfunc.log_model(
            artifact_path="offline_weather_agent_313",
            python_model=OfflineWeatherAgent313Model(),
            input_example=input_example,
            registered_model_name=model_name,
            pip_requirements=[
                "mlflow==3.13.0",
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
                "mlflow_target_version": "3.13.0",
            },
        )

    print(f"registered model: {model_name}")
    print(f"model uri: {info.model_uri}")


if __name__ == "__main__":
    main()
