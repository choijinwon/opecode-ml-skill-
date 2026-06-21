import os

import mlflow

from offline_weather_agent_313.config import configure_mlflow, get_genai_module, llm_api_key, llm_base_url, qwen_model_name


def judge_base_url() -> str:
    """MLflow 3.13 judge는 chat completions 전체 endpoint가 필요하다."""
    base_url = llm_base_url()
    if base_url.endswith("/chat/completions"):
        return base_url
    return f"{base_url}/chat/completions"


def main() -> None:
    # MLflow 3.13에는 이후 버전의 ResponseLength scorer가 없다.
    # 그래서 이 샘플은 make_judge()로 로컬 Qwen을 LLM 평가자로 사용한다.
    configure_mlflow()
    experiment = mlflow.get_experiment_by_name(os.getenv("MLFLOW_EXPERIMENT_NAME", "offline-weather-agent-313"))
    if experiment is None:
        raise RuntimeError("offline-weather-agent-313 experiment does not exist")

    genai = get_genai_module()
    if genai is None:
        print("mlflow.genai is not available; skipping judge setup")
        return

    os.environ.setdefault("OPENAI_API_KEY", llm_api_key())

    judge = genai.make_judge(
        name="offline_weather_313_quality",
        instructions=(
            "Evaluate whether the assistant output is a useful Korean weather answer. "
            "Return true only when the output answers the user's weather question using the provided trace. "
            "Inputs: {{ inputs }}\nOutputs: {{ outputs }}\nTrace: {{ trace }}"
        ),
        model=f"openai:/{qwen_model_name()}",
        base_url=judge_base_url(),
        extra_headers={"Authorization": f"Bearer {llm_api_key()}"},
        feedback_value_type=bool,
        inference_params={"temperature": 0},
    )

    try:
        registered = judge.register(experiment_id=experiment.experiment_id)
        print(f"registered judge: {registered.name}")
    except Exception as exc:
        print(f"judge registration skipped: {exc}")
        registered = judge

    try:
        traces = mlflow.search_traces(experiment_ids=[experiment.experiment_id], max_results=20)
    except TypeError:
        traces = mlflow.search_traces(locations=[experiment.experiment_id], max_results=20)

    if len(traces) == 0:
        print("no traces found")
        return

    try:
        result = genai.evaluate(data=traces, scorers=[registered])
        print(f"evaluated traces: {len(traces)}")
        print(result.metrics)
    except Exception as exc:
        print(f"manual evaluation skipped: {exc}")


if __name__ == "__main__":
    main()
