import os

import mlflow
import pandas as pd

from weather_agent import load_dotenv, weather_agent


class WeatherAgentModel(mlflow.pyfunc.PythonModel):
    def predict(self, context, model_input, params=None):
        if isinstance(model_input, pd.DataFrame):
            questions = model_input["question"].fillna("서울 날씨 알려줘").tolist()
        elif isinstance(model_input, list):
            questions = model_input
        else:
            questions = [str(model_input)]

        return [weather_agent(str(question)) for question in questions]


def main():
    load_dotenv()
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5001"))
    mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT_NAME", "weather-agent"))

    input_example = pd.DataFrame({"question": ["서울 날씨 알려줘"]})
    with mlflow.start_run(run_name="register-weather-agent-qwen"):
        model_info = mlflow.pyfunc.log_model(
            artifact_path="weather_agent_qwen",
            python_model=WeatherAgentModel(),
            input_example=input_example,
            registered_model_name="weather-agent-qwen",
            pip_requirements=[
                f"mlflow=={mlflow.__version__}",
                "pandas",
            ],
            metadata={
                "base_model": os.getenv("WEATHER_AGENT_MODEL", "qwen2.5-coder:14b"),
                "provider": "ollama",
                "tracking_purpose": "weather-agent-demo",
            },
        )

    print(f"registered model: weather-agent-qwen")
    print(f"model uri: {model_info.model_uri}")


if __name__ == "__main__":
    main()
