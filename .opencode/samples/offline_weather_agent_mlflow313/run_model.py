from __future__ import annotations

import argparse
import io
import json
import logging
import os
import shutil
import sys
from pathlib import Path

import joblib
import mlflow
import pandas as pd
from aiu_custom.predict import ModelWrapper
from mlflow.models.signature import infer_signature
from sklearn.datasets import load_diabetes
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


ROOT = Path(__file__).resolve().parent
CONFIG_DIR = ROOT / "config"
CONFIG_PATH = CONFIG_DIR / "config.json"
MODEL_CONFIG_PATH = CONFIG_DIR / "model_config.json"
TRAIN_CONFIG_PATH = CONFIG_DIR / "train_config.json"
MLFLOW_CONFIG_PATH = CONFIG_DIR / "mlflow_config.json"
SAVED_MODEL_DIR = ROOT / "saved_model"
MODEL_PACKAGE_DIR = ROOT / "model"
ARTIFACTS_DIR = ROOT / "artifacts"
MLFLOW_ARTIFACTS_DIR = ARTIFACTS_DIR / "ai_studio"
LOCAL_SERVING_DIR = ROOT / "local_serving"
INPUT_EXAMPLE_PATH = ROOT / "input_example.json"
MODEL_SUMMARY_PATH = ROOT / "model_summary.txt"
SOURCE_MODEL_PATH = SAVED_MODEL_DIR / "model.pkl"
LOCAL_PREDICTION_PATH = LOCAL_SERVING_DIR / "local_prediction.json"
SERVING_RESULT_PATH = LOCAL_SERVING_DIR / "serving_result.json"
MLFLOW_RECORDS_PATH = ARTIFACTS_DIR / "mlflow_records.json"

# 폐쇄망/AI Studio 반입 시 할당받은 값을 코드 상수에 입력한다.
mlflow_tracking_url = ""
mlflow_tracking_username = ""
mlflow_tracking_password = ""
mlflow_experiment_name = ""
mlflow_register_model_name = ""


def configure_windows_utf8():
    # Windows 콘솔에서 한글 로그/JSON이 깨지지 않도록 stdout/stderr를 UTF-8로 고정한다.
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name)
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
        elif hasattr(stream, "buffer"):
            setattr(sys, stream_name, io.TextIOWrapper(stream.buffer, encoding="utf-8"))


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def mlflow_settings() -> dict:
    # 코드 상수와 config 파일을 함께 읽되, 코드 상수 값을 우선한다.
    payload = read_json(MLFLOW_CONFIG_PATH)
    return {
        "tracking_url": mlflow_tracking_url or payload.get("mlflow_tracking_url", ""),
        "username": mlflow_tracking_username or payload.get("mlflow_tracking_username", ""),
        "password": mlflow_tracking_password or payload.get("mlflow_tracking_password", ""),
        "experiment_id": payload.get("mlflow_experiment_id", ""),
        "experiment_name": mlflow_experiment_name or payload.get("mlflow_experiment_name", ""),
        "register_model_name": mlflow_register_model_name or payload.get("mlflow_register_model_name", ""),
    }


def configure_mlflow():
    # tracking uri, 인증, experiment를 한 군데서 정리해서 이후 단계가 같은 설정을 쓰게 한다.
    settings = mlflow_settings()
    os.environ.setdefault("MLFLOW_TRACKING_INSECURE_TLS", "TRUE")
    if settings["username"]:
        os.environ["MLFLOW_TRACKING_USERNAME"] = settings["username"]
    if settings["password"]:
        os.environ["MLFLOW_TRACKING_PASSWORD"] = settings["password"]

    tracking_uri = settings["tracking_url"] or f"sqlite:///{(ARTIFACTS_DIR / 'mlflow.db').as_posix()}"
    experiment_id = settings["experiment_id"]
    experiment_name = settings["experiment_name"] or "offline_weather_agent_local"
    mlflow.set_tracking_uri(tracking_uri)

    client = mlflow.tracking.MlflowClient()
    if experiment_id:
        experiment = client.get_experiment(experiment_id)
        if experiment is None:
            raise RuntimeError(f"MLflow experiment id {experiment_id} does not exist")
        mlflow.set_experiment(experiment_id=experiment_id)
        return settings, tracking_uri, experiment.name, experiment.experiment_id

    # experiment id를 고정하지 않으면 이름 기준으로 찾고, 없으면 로컬 artifact 경로로 새로 만든다.
    experiment = client.get_experiment_by_name(experiment_name)
    if experiment is None:
        experiment_id = client.create_experiment(
            name=experiment_name,
            artifact_location=MLFLOW_ARTIFACTS_DIR.as_uri(),
        )
        experiment = client.get_experiment(experiment_id)
    mlflow.set_experiment(experiment_id=experiment.experiment_id)
    return settings, tracking_uri, experiment.name, experiment.experiment_id


def ensure_dirs():
    # 샘플 배포 시 필요한 기본 폴더를 먼저 만든다.
    for path in [CONFIG_DIR, SAVED_MODEL_DIR, MODEL_PACKAGE_DIR, ARTIFACTS_DIR, MLFLOW_ARTIFACTS_DIR, LOCAL_SERVING_DIR]:
        path.mkdir(parents=True, exist_ok=True)
        (path / ".gitkeep").touch(exist_ok=True)


def compute_metrics(actual, predicted):
    rmse = mean_squared_error(actual, predicted) ** 0.5
    mae = mean_absolute_error(actual, predicted)
    r2 = r2_score(actual, predicted)
    return rmse, mae, r2


def prepare_training_data():
    # 외부 다운로드 없이 sklearn 내장 diabetes 데이터셋으로 학습 데이터를 준비한다.
    diabetes = load_diabetes(as_frame=True)
    diabetes_df = diabetes.frame
    train_df, test_df = train_test_split(diabetes_df, test_size=0.2, random_state=42)
    train_x = train_df.drop(["target"], axis=1)
    train_y = train_df["target"]
    test_x = test_df.drop(["target"], axis=1)
    test_y = test_df["target"]
    return train_df, test_df, train_x, train_y, test_x, test_y


def build_input_example(test_x: pd.DataFrame) -> dict:
    # MLflow model serving/input example 확인용 샘플 요청 payload를 만든다.
    sample_data = test_x.head(10)
    input_example = {
        "input": [
            {
                "name": "diabetes_example",
                "shape": list(sample_data.shape),
                "datatype": "FP64",
                "data": sample_data.to_numpy().tolist(),
            }
        ]
    }
    write_json(INPUT_EXAMPLE_PATH, input_example)
    return input_example


def train_and_save_model():
    # 이 단계는 "원본 모델 + 설정 파일 + 입력 예시"를 로컬 프로젝트 구조에 떨어뜨리는 역할이다.
    ensure_dirs()
    train_df, test_df, train_x, train_y, test_x, test_y = prepare_training_data()

    params = {"alpha": 0.001, "l1_ratio": 0.5, "random_state": 42}
    model = ElasticNet(**params)
    model.fit(train_x, train_y.values.ravel())

    predictions = model.predict(test_x)
    rmse, mae, r2 = compute_metrics(test_y, predictions)
    metrics = {"rmse": rmse, "mae": mae, "r2": r2}

    joblib.dump(model, SOURCE_MODEL_PATH)
    build_input_example(test_x)

    # 이후 pyfunc packaging과 MLflow 등록이 같은 설정을 재사용할 수 있게 config를 저장한다.
    config = {
        "framework": "sklearn",
        "task": "diabetes_regression",
        "model_file": "saved_model/model.pkl",
        "feature_names": train_x.columns.tolist(),
        "target_name": "target",
        "params": params,
        "metrics": metrics,
        "registered_model_name": mlflow_settings().get("register_model_name") or "offline-weather-agent-mlflow313",
    }
    write_json(CONFIG_PATH, config)
    write_json(MODEL_CONFIG_PATH, {"model_type": "ElasticNet", "framework": "sklearn", "artifact": "saved_model/model.pkl"})
    write_json(TRAIN_CONFIG_PATH, {"dataset": "sklearn.load_diabetes", "test_size": 0.2, "random_state": 42})
    if not MLFLOW_CONFIG_PATH.exists():
        write_json(MLFLOW_CONFIG_PATH, {
            "mlflow_tracking_url": "",
            "mlflow_tracking_username": "",
            "mlflow_tracking_password": "",
            "mlflow_experiment_id": "",
            "mlflow_experiment_name": "",
            "mlflow_register_model_name": "",
        })

    MODEL_SUMMARY_PATH.write_text(
        "model_type: ElasticNet\n"
        "dataset: sklearn diabetes\n"
        f"source_model: {SOURCE_MODEL_PATH.relative_to(ROOT).as_posix()}\n"
        f"rmse: {rmse:.6f}\n"
        f"mae: {mae:.6f}\n"
        f"r2: {r2:.6f}\n",
        encoding="utf-8",
    )
    return train_df, test_df, train_x, train_y, test_x, test_y, model, config, metrics


def save_pyfunc_package(test_x: pd.DataFrame):
    # model/ 폴더는 MLflow pyfunc 패키지 결과물 전용이므로 매 실행마다 새로 만든다.
    if MODEL_PACKAGE_DIR.exists():
        for child in MODEL_PACKAGE_DIR.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()

    MODEL_PACKAGE_DIR.mkdir(parents=True, exist_ok=True)

    loaded_model = joblib.load(SOURCE_MODEL_PATH)
    signature = infer_signature(test_x.head(10), loaded_model.predict(test_x.head(10)))
    # AI Studio 형태와 맞추기 위해 wrapper + artifacts 조합으로 pyfunc 패키지를 저장한다.
    mlflow.pyfunc.save_model(
        path=MODEL_PACKAGE_DIR.as_posix(),
        python_model=ModelWrapper(),
        code_paths=["aiu_custom"],
        artifacts={
            "model": SOURCE_MODEL_PATH.as_posix(),
            "config": CONFIG_PATH.as_posix(),
        },
        input_example=test_x.head(10),
        signature=signature,
        pip_requirements="requirements.txt",
    )


def local_serving_test(test_x: pd.DataFrame):
    # 배포 전에도 wrapper 예측이 로컬에서 동작하는지 확인하는 sanity check 단계다.
    wrapper = ModelWrapper()
    class Context:
        artifacts = {"model": SOURCE_MODEL_PATH.as_posix(), "config": CONFIG_PATH.as_posix()}
    wrapper.load_context(Context())
    sample = test_x.head(3)
    predictions = wrapper.predict(None, sample)
    result = {
        "mode": "local-serving-test",
        "input_rows": sample.to_dict(orient="records"),
        "predictions": predictions,
        "deployment_executed": False,
    }
    write_json(LOCAL_PREDICTION_PATH, result)
    write_json(SERVING_RESULT_PATH, {
        "status": "success",
        "result_file": "local_serving/local_prediction.json",
        "deployment_executed": False,
    })
    return result


def register_model(train_df: pd.DataFrame, test_df: pd.DataFrame, test_x: pd.DataFrame, config: dict, metrics: dict):
    # register 단계에서만 실제 MLflow run/model registry 기록을 남긴다.
    settings, tracking_uri, experiment_name, experiment_id = configure_mlflow()
    registered_model_name = settings["register_model_name"] or config.get("registered_model_name", "offline-weather-agent-mlflow313")
    loaded_model = joblib.load(SOURCE_MODEL_PATH)
    signature = infer_signature(test_x.head(10), loaded_model.predict(test_x.head(10)))

    train_ds = mlflow.data.from_pandas(train_df, name="Train", targets="target")
    test_ds = mlflow.data.from_pandas(test_df, name="Test", targets="target")

    with mlflow.start_run(run_name="register-sklearn-diabetes-model") as run:
        # training/test dataset, params, metrics를 함께 남겨야 UI에서 모델 맥락을 같이 볼 수 있다.
        mlflow.log_input(train_ds, context="training")
        mlflow.log_input(test_ds, context="test")
        mlflow.set_tag("data.name", "diabetes(sklearn)")
        mlflow.log_params(config["params"])
        mlflow.log_metrics(metrics)
        model_info = mlflow.pyfunc.log_model(
            artifact_path="ai_studio",
            python_model=ModelWrapper(),
            code_paths=["aiu_custom"],
            artifacts={
                "model": SOURCE_MODEL_PATH.as_posix(),
                "config": CONFIG_PATH.as_posix(),
            },
            input_example=test_x.head(10),
            signature=signature,
            registered_model_name=registered_model_name,
            pip_requirements="requirements.txt",
        )

    client = mlflow.tracking.MlflowClient()
    # 등록 직후 최신 model version과 run 정보를 별도 JSON으로 남겨 운영/검증에 재사용한다.
    versions = client.search_model_versions(f"name='{registered_model_name}'")
    latest = max(versions, key=lambda item: int(item.version))
    records = {
        "artifact_type": "mlflow_tracking_records",
        "tracking_backend": "sqlite" if tracking_uri.startswith("sqlite:///") else "remote",
        "tracking_uri": tracking_uri,
        "artifact_location": "artifacts/ai_studio",
        "experiment_id": experiment_id,
        "experiment_name": experiment_name,
        "registered_model_name": registered_model_name,
        "model_version": latest.version,
        "run_id": run.info.run_id,
        "source": latest.source,
        "model_uri": model_info.model_uri,
        "metrics": metrics,
        "deployment_executed": False,
        "mlflow_registration_executed": True,
    }
    write_json(MLFLOW_RECORDS_PATH, records)
    return records


def run_pipeline(register: bool):
    # prepare-only와 register가 같은 준비 단계를 공유하고, 마지막 등록 단계만 선택적으로 탄다.
    train_df, test_df, train_x, train_y, test_x, test_y, model, config, metrics = train_and_save_model()
    save_pyfunc_package(test_x)
    serving_result = local_serving_test(test_x)
    records = register_model(train_df, test_df, test_x, config, metrics) if register else None
    return {"config": config, "metrics": metrics, "serving_result": serving_result, "mlflow_records": records}


def main():
    parser = argparse.ArgumentParser(description="Train local sklearn model and register it with MLflow")
    parser.add_argument("--prepare-only", action="store_true", help="train and prepare local files without MLflow registration")
    parser.add_argument("--register", action="store_true", help="train, package, and register with MLflow")
    args = parser.parse_args()

    configure_windows_utf8()
    logging.getLogger("mlflow").setLevel(logging.ERROR)

    # 기본 실행은 prepare 성격이고, --register를 붙였을 때만 MLflow 등록까지 진행한다.
    result = run_pipeline(register=args.register)
    if args.register:
        print("mlflow registration completed")
    else:
        print("prepare check passed")
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
