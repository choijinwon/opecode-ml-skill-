from __future__ import annotations

import json
import os
from pathlib import Path

import mlflow
from mlflow.entities.trace_location import MlflowExperimentLocation


ROOT = Path(__file__).resolve().parent.parent
MLFLOW_CONFIG_PATH = ROOT / "config" / "mlflow_config.json"


def _read_config() -> dict:
    if not MLFLOW_CONFIG_PATH.exists():
        return {}
    return json.loads(MLFLOW_CONFIG_PATH.read_text(encoding="utf-8"))


def get_settings() -> dict:
    config = _read_config()
    return {
        "tracking_url": os.getenv("MLFLOW_TRACKING_URL") or config.get("mlflow_tracking_url", ""),
        "tracking_username": os.getenv("MLFLOW_TRACKING_USERNAME")
        or config.get("mlflow_tracking_username", ""),
        "tracking_password": os.getenv("MLFLOW_TRACKING_PASSWORD")
        or config.get("mlflow_tracking_password", ""),
        "experiment_id": os.getenv("MLFLOW_EXPERIMENT_ID") or config.get("mlflow_experiment_id", ""),
        "experiment_name": os.getenv("MLFLOW_EXPERIMENT_NAME")
        or config.get("mlflow_experiment_name", "offline_weather_agent_local"),
        "registered_model_name": os.getenv("MLFLOW_REGISTER_MODEL_NAME")
        or config.get("mlflow_register_model_name")
        or "offline-weather-agent-mlflow313",
        "judge_model_uri": os.getenv("JUDGE_MODEL_URI")
        or config.get("judge_model_uri", "ollama:/qwen2.5-coder:14b"),
        "judge_api_base": os.getenv("JUDGE_API_BASE")
        or config.get("judge_api_base", "http://127.0.0.1:11434/v1"),
        "judge_api_key": os.getenv("JUDGE_API_KEY") or config.get("judge_api_key", "ollama"),
        "provider": os.getenv("LLM_PROVIDER", "ollama"),
        "base_model": os.getenv("OPENAI_MODEL")
        or os.getenv("WEATHER_AGENT_MODEL")
        or "qwen2.5-coder:14b",
    }


def configure_mlflow() -> dict:
    settings = get_settings()

    os.environ.setdefault("MLFLOW_TRACKING_INSECURE_TLS", "TRUE")
    if settings["tracking_username"]:
        os.environ["MLFLOW_TRACKING_USERNAME"] = settings["tracking_username"]
    if settings["tracking_password"]:
        os.environ["MLFLOW_TRACKING_PASSWORD"] = settings["tracking_password"]
    if settings["tracking_url"]:
        mlflow.set_tracking_uri(settings["tracking_url"])
    if settings["experiment_id"]:
        os.environ["MLFLOW_EXPERIMENT_ID"] = settings["experiment_id"]
        mlflow.set_experiment(experiment_id=settings["experiment_id"])
    else:
        mlflow.set_experiment(settings["experiment_name"])

    os.environ["OPENAI_API_KEY"] = settings["judge_api_key"]
    os.environ["OPENAI_API_BASE"] = settings["judge_api_base"]
    os.environ["OPENAI_BASE_URL"] = settings["judge_api_base"]
    os.environ["OLLAMA_API_BASE"] = settings["judge_api_base"]

    return settings


def configure_tracing_destination() -> dict:
    settings = configure_mlflow()
    if settings["experiment_id"]:
        mlflow.tracing.set_destination(
            MlflowExperimentLocation(experiment_id=settings["experiment_id"])
        )
    return settings


def llm_base_url() -> str:
    """LangChain/LangGraph/OpenAI-compatible 호출에 공통으로 쓰는 로컬 endpoint다."""
    settings = get_settings()
    return settings["judge_api_base"].rstrip("/")


def llm_api_key() -> str:
    """폐쇄망 로컬 endpoint용 기본 API key를 반환한다."""
    settings = get_settings()
    return settings["judge_api_key"]


def qwen_model_name() -> str:
    """로컬 Qwen 계열 기본 모델 이름을 반환한다."""
    settings = get_settings()
    return settings["base_model"]


def get_genai_module():
    """MLflow genai 모듈이 있으면 반환하고, 없으면 None을 반환한다."""
    return getattr(mlflow, "genai", None)
