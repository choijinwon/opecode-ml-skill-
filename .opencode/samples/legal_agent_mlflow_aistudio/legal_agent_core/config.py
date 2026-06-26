from __future__ import annotations

import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
ARTIFACTS_DIR = ROOT / "artifacts"
SAVE_MODEL_DIR = ROOT / "save_model"
AGENT_CONFIG_PATH = CONFIG_DIR / "agent_config.json"


def read_agent_config() -> dict:
    if not AGENT_CONFIG_PATH.exists():
        return {}
    return json.loads(AGENT_CONFIG_PATH.read_text(encoding="utf-8"))


def ai_studio_settings() -> dict:
    return {
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "base_url": os.getenv("OPENAI_BASE_URL", "").rstrip("/"),
        "model": os.getenv("OPENAI_MODEL", "qwen3.6"),
        "models": [
            model.strip()
            for model in os.getenv("OPENAI_MODELS", "qwen3.6").split(",")
            if model.strip()
        ],
    }


def configure_mlflow() -> dict:
    """MLflow tracking/experiment를 설정한다.

    MLFLOW_TRACKING_URI가 없으면 샘플 내부 artifacts/mlflow.db를 사용한다.
    서버 배포 시에는 환경변수 또는 Secret로 값을 주입한다.
    """
    import mlflow

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    SAVE_MODEL_DIR.mkdir(parents=True, exist_ok=True)

    tracking_uri = os.getenv(
        "MLFLOW_TRACKING_URI",
        f"sqlite:///{(ARTIFACTS_DIR / 'mlflow.db').as_posix()}",
    )
    experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME", "legal-agent-ai-studio")
    registered_model_name = os.getenv(
        "MLFLOW_REGISTER_MODEL_NAME",
        "legal-agent-ai-studio",
    )

    if os.getenv("MLFLOW_TRACKING_USERNAME"):
        os.environ["MLFLOW_TRACKING_USERNAME"] = os.environ["MLFLOW_TRACKING_USERNAME"]
    if os.getenv("MLFLOW_TRACKING_PASSWORD"):
        os.environ["MLFLOW_TRACKING_PASSWORD"] = os.environ["MLFLOW_TRACKING_PASSWORD"]

    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)
    return {
        "tracking_uri": tracking_uri,
        "experiment_name": experiment_name,
        "registered_model_name": registered_model_name,
    }


def secret_status() -> dict[str, str]:
    settings = ai_studio_settings()
    return {
        "OPENAI_API_KEY": "set" if settings["api_key"] else "missing",
        "OPENAI_BASE_URL": "set" if settings["base_url"] else "missing",
        "OPENAI_MODEL": settings["model"] or "missing",
        "MLFLOW_TRACKING_URI": "set" if os.getenv("MLFLOW_TRACKING_URI") else "local-default",
    }
