from __future__ import annotations

import argparse
import io
import json
import logging
import os
import sys
from pathlib import Path

import joblib
import mlflow
import pandas as pd
from aiu_custom.predict import ModelWrapper
from sklearn.datasets import load_diabetes
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import train_test_split


ROOT = Path(__file__).resolve().parent
GENERATED_DIR = ROOT / "generated"
CONFIG_DIR = GENERATED_DIR / "config"
MODEL_DIR = GENERATED_DIR / "saved_model"
CONFIG_PATH = CONFIG_DIR / "config.json"
MODEL_PATH = MODEL_DIR / "model.pkl"
INPUT_EXAMPLE_PATH = GENERATED_DIR / "input_example.json"

# MLflow settings are intentionally kept as code constants for closed-network
# deployments. Fill these with values assigned by the user's environment.
mlflow_tracking_url = ""
mlflow_tracking_username = ""
mlflow_tracking_password = ""
mlflow_experiment_name = ""
mlflow_register_model_name = ""


def configure_windows_utf8():
    # Windows terminals may default to a legacy code page. Keep stdout/stderr in
    # UTF-8 so Korean logs and MLflow messages do not break.
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name)
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
        elif hasattr(stream, "buffer"):
            setattr(sys, stream_name, io.TextIOWrapper(stream.buffer, encoding="utf-8"))


def configure_mlflow_from_code():
    # Every user has a different local or remote MLflow target. Do not assume a
    # fixed local URI; use only the code constants filled by the user.
    os.environ.setdefault("MLFLOW_TRACKING_INSECURE_TLS", "TRUE")
    if mlflow_tracking_username:
        os.environ["MLFLOW_TRACKING_USERNAME"] = mlflow_tracking_username
    if mlflow_tracking_password:
        os.environ["MLFLOW_TRACKING_PASSWORD"] = mlflow_tracking_password
    if mlflow_tracking_url:
        mlflow.set_tracking_uri(mlflow_tracking_url)
    if mlflow_experiment_name:
        mlflow.set_experiment(mlflow_experiment_name)


def prepare_dataset():
    diabetes = load_diabetes(as_frame=True)
    diabetes_df = diabetes.frame
    train_df, test_df = train_test_split(diabetes_df, test_size=0.2, random_state=42)

    train_x = train_df.drop(["target"], axis=1)
    train_y = train_df["target"]
    test_x = test_df.drop(["target"], axis=1)
    test_y = test_df["target"]
    return train_df, test_df, train_x, train_y, test_x, test_y


def write_input_example(test_x: pd.DataFrame) -> dict:
    sample_data = test_x.head(10).to_numpy()
    input_example = {
        "input": [
            {
                "name": "diabetes_example",
                "shape": list(sample_data.shape),
                "datatype": str(sample_data.dtype),
                "data": sample_data.tolist(),
            }
        ]
    }
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    INPUT_EXAMPLE_PATH.write_text(json.dumps(input_example, indent=2), encoding="utf-8")
    return input_example


def compute_metrics(actual, predicted) -> tuple[float, float, float]:
    rmse = root_mean_squared_error(actual, predicted)
    mae = mean_absolute_error(actual, predicted)
    r2 = r2_score(actual, predicted)
    return rmse, mae, r2


def prepare_model():
    train_df, test_df, train_x, train_y, test_x, test_y = prepare_dataset()
    input_example = write_input_example(test_x)

    params = {"alpha": 0.001, "l1_ratio": 0.5, "random_state": 42}
    model = ElasticNet(**params)
    model.fit(train_x, train_y)

    prediction = model.predict(test_x)
    rmse, mae, r2 = compute_metrics(test_y, prediction)

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(params, indent=2), encoding="utf-8")
    joblib.dump(model, MODEL_PATH)

    return {
        "model": model,
        "train_df": train_df,
        "test_df": test_df,
        "input_example": input_example,
        "mlflow_input_example": test_x.head(10),
        "params": params,
        "metrics": {"rmse": rmse, "mae": mae, "r2": r2},
    }


def register_model():
    payload = prepare_model()
    registered_model_name = mlflow_register_model_name or "sklearn-sample-ai-studio"

    train_ds = mlflow.data.from_pandas(payload["train_df"], name="Train", targets="target")
    test_ds = mlflow.data.from_pandas(payload["test_df"], name="Test", targets="target")

    with mlflow.start_run():
        mlflow.log_input(train_ds, context="training")
        mlflow.log_input(test_ds, context="test")
        mlflow.set_tag("data.name", "diabetes(sklearn)")
        mlflow.log_params(payload["params"])
        mlflow.log_metrics(payload["metrics"])
        mlflow.pyfunc.log_model(
            artifact_path="ai_studio",
            python_model=ModelWrapper(),
            code_paths=["aiu_custom"],
            artifacts={
                "model": MODEL_PATH.as_posix(),
                "config": CONFIG_PATH.as_posix(),
            },
            input_example=payload["mlflow_input_example"],
            registered_model_name=registered_model_name,
            pip_requirements="requirements.txt",
        )


def main():
    parser = argparse.ArgumentParser(description="AI Studio style sklearn MLflow sample")
    parser.add_argument("--prepare-only", action="store_true", help="create artifacts and validate inputs only")
    parser.add_argument("--register", action="store_true", help="log and register the model with MLflow")
    args = parser.parse_args()

    configure_windows_utf8()
    logging.getLogger("mlflow").setLevel(logging.ERROR)

    if args.register:
        configure_mlflow_from_code()
        register_model()
        print("mlflow registration completed")
        return

    prepare_model()
    print("prepare check passed")


if __name__ == "__main__":
    main()
