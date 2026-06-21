import os

import mlflow
import mlflow.genai
from mlflow.exceptions import MlflowException
from mlflow.genai.scorers import ResponseLength, ScorerSamplingConfig

from weather_agent import load_dotenv


def main() -> None:
    load_dotenv()
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5001"))
    mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT_NAME", "weather-agent"))

    experiment = mlflow.get_experiment_by_name(os.getenv("MLFLOW_EXPERIMENT_NAME", "weather-agent"))
    if experiment is None:
        raise RuntimeError("weather-agent experiment does not exist yet")

    scorer = ResponseLength(
        name="weather_response_length",
        min_length=20,
        max_length=500,
        unit="chars",
    )
    registered = scorer.register(experiment_id=experiment.experiment_id)
    print(f"registered scorer: {registered.name}")
    print(f"experiment_id: {experiment.experiment_id}")
    try:
        active = registered.start(
            experiment_id=experiment.experiment_id,
            sampling_config=ScorerSamplingConfig(sample_rate=1.0),
        )
        print(f"scorer status: {active.status}")
        print(f"sample rate: {active.sample_rate}")
    except MlflowException as exc:
        print(f"automatic scoring not started: {exc.message}")
        print("manual evaluation will still run below")

    traces = mlflow.search_traces(experiment_ids=[experiment.experiment_id], max_results=10)
    if len(traces) == 0:
        print("no traces found to evaluate")
        return

    result = mlflow.genai.evaluate(data=traces, scorers=[registered])
    print(f"evaluated traces: {len(traces)}")
    print(result.metrics)


if __name__ == "__main__":
    main()
