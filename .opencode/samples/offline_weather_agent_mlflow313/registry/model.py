import os
import sys
from pathlib import Path

import mlflow
import pandas as pd
from mlflow.exceptions import MlflowException

ROOT = Path(__file__).resolve().parent.parent
if ROOT.as_posix() not in sys.path:
    sys.path.insert(0, ROOT.as_posix())

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
    settings = configure_mlflow()
    input_example = pd.DataFrame({"question": ["서울 날씨 알려줘"]})
    model_name = settings["registered_model_name"]

    with mlflow.start_run(run_name="register-offline-weather-agent") as run:
        info = mlflow.pyfunc.log_model(
            name="ai_studio",
            python_model=OfflineWeatherAgentModel(),
            input_example=input_example,
            code_paths=[(ROOT / "offline_weather_agent_core").as_posix()],
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
                "base_model": settings["base_model"],
                "provider": settings["provider"],
                "network": "closed",
            },
        )

    client = mlflow.MlflowClient()
    try:
        client.create_registered_model(model_name)
    except MlflowException as exc:
        if "already exists" not in str(exc):
            raise

    version = client.create_model_version(
        name=model_name,
        source=info.model_uri,
        run_id=run.info.run_id,
        model_id=getattr(info, "model_id", None),
    )

    print(f"registered model: {model_name}")
    print(f"model uri: {info.model_uri}")
    print(f"model version: {version.version}")


if __name__ == "__main__":
    main()
