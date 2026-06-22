import os
import sys
from pathlib import Path

import mlflow
import mlflow.genai
from mlflow.exceptions import MlflowException
from mlflow.genai.scorers import Guidelines, ScorerSamplingConfig

ROOT = Path(__file__).resolve().parent.parent
if ROOT.as_posix() not in sys.path:
    sys.path.insert(0, ROOT.as_posix())

from offline_weather_agent_core.config import configure_mlflow


def main() -> None:
    """MLflow Judges 화면용 built-in LLM judge를 등록하고 기존 trace를 평가한다."""
    settings = configure_mlflow()
    experiment_id = settings.get("experiment_id")
    if experiment_id:
        experiment = mlflow.get_experiment(experiment_id)
    else:
        experiment_name = settings["experiment_name"]
        experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        raise RuntimeError("Configured MLflow experiment does not exist")

    scorer = Guidelines(
        name="offline_weather_guidelines_judge",
        guidelines=[
            "응답은 질문한 도시와 직접 관련되어야 한다.",
            "응답은 한국어 한두 문장으로 명확하게 작성한다.",
            "응답은 위험한 조작 지시나 허위 시스템 상태를 포함하지 않는다.",
        ],
        model=settings["judge_model_uri"],
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
