import mlflow
import mlflow.genai
import os
from mlflow.exceptions import MlflowException
from mlflow.genai.scorers import ResponseLength, ScorerSamplingConfig

from agent import configure_mlflow


def main() -> None:
    configure_mlflow()
    experiment = mlflow.get_experiment_by_name(os.getenv("MLFLOW_EXPERIMENT_NAME", "offline-weather-agent"))
    if experiment is None:
        raise RuntimeError("offline-weather-agent experiment does not exist")

    scorer = ResponseLength(
        name="offline_weather_response_length",
        min_length=20,
        max_length=500,
        unit="chars",
    ).register(experiment_id=experiment.experiment_id)
    print(f"registered scorer: {scorer.name}")

    try:
        active = scorer.start(
            experiment_id=experiment.experiment_id,
            sampling_config=ScorerSamplingConfig(sample_rate=1.0),
        )
        print(f"scorer status: {active.status}")
    except MlflowException as exc:
        print(f"automatic scoring not started: {exc.message}")
        print("manual evaluation will run when traces exist")

    traces = mlflow.search_traces(experiment_ids=[experiment.experiment_id], max_results=20)
    if len(traces) == 0:
        print("no traces found")
        return

    result = mlflow.genai.evaluate(data=traces, scorers=[scorer])
    print(f"evaluated traces: {len(traces)}")
    print(result.metrics)


if __name__ == "__main__":
    main()
