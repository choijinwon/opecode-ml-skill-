from __future__ import annotations

import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
ARTIFACTS_DIR = ROOT / "artifacts"
SAVE_MODEL_DIR = ROOT / "save_model"
AI_STUDIO_ENV_PATH = CONFIG_DIR / "ai_studio.env"
AGENT_CONFIG_PATH = CONFIG_DIR / "agent_config.json"


def load_env_file(path: Path = AI_STUDIO_ENV_PATH) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
            os.environ.setdefault(key, value)
    return values


def read_agent_config() -> dict:
    if not AGENT_CONFIG_PATH.exists():
        return {}
    return json.loads(AGENT_CONFIG_PATH.read_text(encoding="utf-8"))


def ai_studio_settings() -> dict:
    load_env_file()
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
    import mlflow

    load_env_file()
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    SAVE_MODEL_DIR.mkdir(parents=True, exist_ok=True)

    tracking_uri = os.getenv(
        "MLFLOW_TRACKING_URI",
        f"sqlite:///{(ARTIFACTS_DIR / 'mlflow.db').as_posix()}",
    )
    experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME", "design-agent-ai-studio")
    registered_model_name = os.getenv(
        "MLFLOW_REGISTER_MODEL_NAME",
        "design-agent-ai-studio",
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
