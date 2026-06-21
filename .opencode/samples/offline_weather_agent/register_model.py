import os

import mlflow
import pandas as pd

from agent import answer_weather, configure_mlflow


class OfflineWeatherAgentModel(mlflow.pyfunc.PythonModel):
    def predict(self, context, model_input, params=None):
        if isinstance(model_input, pd.DataFrame):
            questions = model_input["question"].fillna("서울 날씨 알려줘").tolist()
        elif isinstance(model_input, list):
            questions = model_input
        else:
            questions = [str(model_input)]

        return [answer_weather(str(question)) for question in questions]


def main() -> None:
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
                "pandas",
                "pydantic",
            ],
            metadata={
                "base_model": os.getenv("WEATHER_AGENT_MODEL", "qwen2.5-coder:14b"),
                "provider": "ollama",
                "network": "closed",
            },
        )

    print(f"registered model: {model_name}")
    print(f"model uri: {info.model_uri}")


if __name__ == "__main__":
    main()
