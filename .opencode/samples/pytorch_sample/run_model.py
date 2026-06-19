from __future__ import annotations

import argparse
import io
import json
import logging
import os
import sys
from pathlib import Path

import mlflow
import pandas as pd
from aiu_custom.predict import ModelWrapper


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
INPUT_EXAMPLE_PATH = ROOT / "input_example.json"

# MLflow settings are intentionally kept as code constants for closed-network
# deployments. Fill these with values assigned by the user's environment.
mlflow_tracking_url = ""
mlflow_tracking_username = ""
mlflow_tracking_password = ""
mlflow_experiment_name = ""
mlflow_register_model_name = ""


def configure_windows_utf8():
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name)
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
        elif hasattr(stream, "buffer"):
            setattr(sys, stream_name, io.TextIOWrapper(stream.buffer, encoding="utf-8"))


def configure_mlflow_from_code():
    os.environ.setdefault("MLFLOW_TRACKING_INSECURE_TLS", "TRUE")
    if mlflow_tracking_username:
        os.environ["MLFLOW_TRACKING_USERNAME"] = mlflow_tracking_username
    if mlflow_tracking_password:
        os.environ["MLFLOW_TRACKING_PASSWORD"] = mlflow_tracking_password
    if mlflow_tracking_url:
        mlflow.set_tracking_uri(mlflow_tracking_url)
    if mlflow_experiment_name:
        mlflow.set_experiment(mlflow_experiment_name)


def prepare():
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    artifact_path = ROOT / config["artifact_path"]
    if not artifact_path.exists():
        raise FileNotFoundError(f"missing artifact: {artifact_path}")
    input_payload = json.loads(INPUT_EXAMPLE_PATH.read_text(encoding="utf-8"))
    input_example = pd.DataFrame(input_payload["inputs"])
    return config, artifact_path, input_example


def register_model():
    config, artifact_path, input_example = prepare()
    registered_model_name = mlflow_register_model_name or config.get("registered_model_name", "pytorch-sample-model")

    with mlflow.start_run():
        mlflow.log_dict(config, "config.json")
        mlflow.pyfunc.log_model(
            artifact_path="ai_studio",
            python_model=ModelWrapper(),
            code_paths=["aiu_custom"],
            artifacts={
                "model": artifact_path.as_posix(),
                "config": CONFIG_PATH.as_posix(),
            },
            input_example=input_example,
            registered_model_name=registered_model_name,
            pip_requirements="requirements.txt",
        )


def main():
    parser = argparse.ArgumentParser(description="AI Studio style PyTorch MLflow sample")
    parser.add_argument("--prepare-only", action="store_true", help="validate local artifacts only")
    parser.add_argument("--register", action="store_true", help="log and register the model with MLflow")
    args = parser.parse_args()

    configure_windows_utf8()
    logging.getLogger("mlflow").setLevel(logging.ERROR)

    if args.register:
        configure_mlflow_from_code()
        register_model()
        print("mlflow registration completed")
        return

    prepare()
    print("prepare check passed")


if __name__ == "__main__":
    main()
