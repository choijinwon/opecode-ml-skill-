import io
import inspect
import json
import logging
import os
import sys
from urllib.parse import quote

import joblib
import mlflow
from sklearn.datasets import load_iris, load_diabetes
from sklearn.linear_model import ElasticNet
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    root_mean_squared_error,
)
from sklearn.model_selection import train_test_split

from aiu_custom.predict import ModelWrapper


# ------------------------------------------------------------
# Windows 인코딩 문제 해결
# ------------------------------------------------------------
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

logging.getLogger("mlflow").setLevel(logging.ERROR)


def normalize_upload_uri(path):
    value = str(path).replace("＼", os.sep).replace("￦", os.sep).replace("₩", os.sep)
    return os.path.normpath(value)


def validate_mlflow_tracking_url(value):
    tracking_url = str(value).strip()
    lowered = tracking_url.lower()
    if not tracking_url:
        raise ValueError("mlflow_tracking_url_required: 원격 MLflow Tracking Server URL을 입력하세요.")
    if lowered.startswith(("sqlite:", "file:")):
        raise ValueError(
            "mlflow_tracking_url_invalid: sqlite/file 로컬 tracking은 사용하지 않습니다. "
            "원격 MLflow 서버 URL(http:// 또는 https://)을 입력하세요."
        )
    if not lowered.startswith(("http://", "https://")):
        raise ValueError("mlflow_tracking_url_invalid: http:// 또는 https:// URL만 사용할 수 있습니다.")
    if lowered.startswith(("http://127.0.0.1", "http://localhost", "https://127.0.0.1", "https://localhost")):
        print(
            "주의: localhost MLflow 서버를 사용 중입니다. "
            "서버 backend-store-uri가 sqlite/mlflow.db이면 disk I/O error가 날 수 있습니다. "
            "원격 MLflow 서버 URL 사용을 권장합니다."
        )
    return tracking_url


def handle_mlflow_connection_error(exc):
    message = str(exc)
    if "sqlite3.OperationalError" in message and "disk I/O error" in message:
        print("MLflow 서버 저장소 오류: SQLite disk I/O error가 발생했습니다.")
        print("원인 후보: MLflow 서버가 sqlite/mlflow.db backend로 떠 있고, 해당 경로 권한/잠금/드라이브 I/O 문제가 있습니다.")
        print("조치: mlflow_tracking_url을 원격 MLflow 서버 URL로 바꾸거나, 서버 backend-store-uri와 artifact-root 경로 권한을 확인하세요.")
        print("주의: runtest.py에서는 로컬 sqlite/file tracking을 사용하지 않습니다.")
        raise SystemExit(1)
    raise exc


# ------------------------------------------------------------
# MLflow 환경 설정
# ------------------------------------------------------------
# 할당받은 MLflow Tracking Server URL / 계정 정보 기재
mlflow_tracking_url = ""
mlflow_tracking_username = ""
mlflow_tracking_password = ""

mlflow_experiment_name = "diabetes_elasticnet_experiment"
mlflow_register_model_name = "diabetes_elasticnet_model"

os.environ["MLFLOW_TRACKING_INSECURE_TLS"] = "TRUE"
os.environ["MLFLOW_TRACKING_USERNAME"] = mlflow_tracking_username
os.environ["MLFLOW_TRACKING_PASSWORD"] = mlflow_tracking_password

missing_mlflow_settings = [
    name
    for name, value in {
        "mlflow_tracking_url": mlflow_tracking_url,
        "mlflow_tracking_username": mlflow_tracking_username,
        "mlflow_tracking_password": mlflow_tracking_password,
    }.items()
    if not str(value).strip()
]

if missing_mlflow_settings:
    print("학습 실행 및 원격 MLflow 등록을 위해 MLflow/AI Studio 설정을 runtest.py에 직접 입력하세요.")
    print("missing settings:")
    for name in missing_mlflow_settings:
        print(f"- {name}")
    print("비밀번호 값은 출력하지 않습니다.")
    raise SystemExit(0)

mlflow_tracking_url = validate_mlflow_tracking_url(mlflow_tracking_url)
try:
    mlflow.set_tracking_uri(mlflow_tracking_url)
    mlflow.set_experiment(mlflow_experiment_name)
except Exception as exc:
    handle_mlflow_connection_error(exc)


# ------------------------------------------------------------
# 데이터 준비
# ------------------------------------------------------------
diabetes = load_diabetes(as_frame=True)
diabetes_df = diabetes.frame

train_df, test_df = train_test_split(
    diabetes_df,
    test_size=0.2,
    random_state=42,
)

train_x = train_df.drop(["target"], axis=1)
train_y = train_df["target"]

test_x = test_df.drop(["target"], axis=1)
test_y = test_df["target"]


# ------------------------------------------------------------
# 모델 준비
# ------------------------------------------------------------
model = ElasticNet(
    alpha=0.001,
    l1_ratio=0.5,
    random_state=42,
)


def compute_metrics(actual, predicted):
    rmse = root_mean_squared_error(actual, predicted)
    mae = mean_absolute_error(actual, predicted)
    r2 = r2_score(actual, predicted)

    return rmse, mae, r2


# ------------------------------------------------------------
# Input example 정의
# ------------------------------------------------------------
batch_size = 10
sample_data = test_x.head(batch_size).to_numpy()

request_input_example = {
    "input": [
        {
            "name": "diabetes_example",
            "shape": list(sample_data.shape),
            "datatype": sample_data.dtype.name,
            "data": sample_data.tolist(),
        }
    ]
}

with open("input_example.json", "w", encoding="utf-8") as f:
    json.dump(request_input_example, f, indent=2, ensure_ascii=False)

# MLflow log_model에 넣을 input_example은 실제 모델 입력 형태로 사용
mlflow_input_example = test_x.head(batch_size)


# ------------------------------------------------------------
# Config 저장
# ------------------------------------------------------------
config_dir = "config"
os.makedirs(config_dir, exist_ok=True)

config_path = normalize_upload_uri(os.path.join(config_dir, "config.json"))

params = {
    "alpha": 0.001,
    "l1_ratio": 0.5,
    "feature_names": train_x.columns.tolist(),
}

with open(config_path, "w", encoding="utf-8") as f:
    json.dump(params, f, indent=4, ensure_ascii=False)


# ------------------------------------------------------------
# MLflow Dataset 정의
# ------------------------------------------------------------
mlflow_train_ds = mlflow.data.from_pandas(
    train_df,
    name="Train",
    targets="target",
)

mlflow_test_ds = mlflow.data.from_pandas(
    test_df,
    name="Test",
    targets="target",
)


def mlflow_ui_urls(experiment_id, run_id=None):
    base_url = str(mlflow_tracking_url).strip().rstrip("/")
    urls = {
        "tracking_url": base_url,
        "experiment_url": f"{base_url}/#/experiments/{experiment_id}",
        "experiment_models_url": f"{base_url}/#/experiments/{experiment_id}/models",
        "traces_url": f"{base_url}/#/experiments/{experiment_id}/traces?startTime=ALL",
    }
    if run_id:
        urls["run_url"] = f"{base_url}/#/experiments/{experiment_id}/runs/{run_id}"
    if mlflow_register_model_name:
        model_name = quote(mlflow_register_model_name, safe="")
        urls["registered_model_url"] = f"{base_url}/#/models/{model_name}"
    return urls


def print_mlflow_ui_urls(experiment_id, run_id=None):
    urls = mlflow_ui_urls(experiment_id, run_id)
    print("MLflow Tracking URL:", urls["tracking_url"])
    print("MLflow Experiment URL:", urls["experiment_url"])
    print("MLflow Experiment Models URL:", urls["experiment_models_url"])
    print("MLflow Traces URL:", urls["traces_url"])
    if "run_url" in urls:
        print("MLflow Run URL:", urls["run_url"])
    if "registered_model_url" in urls:
        print("MLflow Registered Model URL:", urls["registered_model_url"])


def ensure_registered_model(model_info):
    model_name = str(mlflow_register_model_name).strip()
    if not model_name:
        return "skipped: mlflow_register_model_name empty"
    try:
        client = mlflow.tracking.MlflowClient()
        client.get_registered_model(model_name)
        return f"exists: {model_name}"
    except Exception:
        pass
    model_uri = getattr(model_info, "model_uri", "")
    if not model_uri:
        return "failed: model_uri missing"
    try:
        registered = mlflow.register_model(model_uri=model_uri, name=model_name)
        version = getattr(registered, "version", "unknown")
        return f"registered: {model_name}, version={version}"
    except Exception as exc:
        return f"failed: {type(exc).__name__}: {exc}"


# ------------------------------------------------------------
# 모델 학습 / 평가 / 로깅
# ------------------------------------------------------------
with mlflow.start_run() as run:
    mlflow.log_input(mlflow_train_ds, context="training")
    mlflow.log_input(mlflow_test_ds, context="test")

    mlflow.set_tag("data.name", "diabetes_sklearn")
    mlflow.set_tag("model.type", "ElasticNet")
    mlflow.set_tag("framework", "scikit-learn")

    mlflow.log_params(
        {
            "alpha": params["alpha"],
            "l1_ratio": params["l1_ratio"],
        }
    )

    model.fit(train_x, train_y)

    prediction = model.predict(test_x)
    rmse, mae, r2 = compute_metrics(test_y, prediction)

    mlflow.log_metrics(
        {
            "rmse": rmse,
            "mae": mae,
            "r2": r2,
        }
    )

    # --------------------------------------------------------
    # 모델 파일 저장
    # --------------------------------------------------------
    model_dir = "saved_model"
    os.makedirs(model_dir, exist_ok=True)

    model_path = normalize_upload_uri(os.path.join(model_dir, "model.pkl"))
    joblib.dump(model, model_path)

    aiu_custom_path = "aiu_custom"

    # --------------------------------------------------------
    # MLflow PyFunc 모델 로깅
    # --------------------------------------------------------
    log_model_args = {
        "artifact_path": "ai_studio",
        "python_model": ModelWrapper(),
        "code_paths": [aiu_custom_path],
        "artifacts": {
            "model": model_path,
            "config": config_path,
        },
        "input_example": mlflow_input_example,
        "pip_requirements": "requirements.txt",
    }

    if mlflow_register_model_name:
        log_model_args["registered_model_name"] = mlflow_register_model_name

    if "name" in inspect.signature(mlflow.pyfunc.log_model).parameters:
        log_model_args["name"] = log_model_args.pop("artifact_path")

    model_info = mlflow.pyfunc.log_model(**log_model_args)
    registry_status = ensure_registered_model(model_info)

    print("MLflow Run ID:", run.info.run_id)
    print("Model URI:", model_info.model_uri)
    print("MLflow Registry:", registry_status)
    print("RMSE:", rmse)
    print("MAE:", mae)
    print("R2:", r2)
    print_mlflow_ui_urls(run.info.experiment_id, run.info.run_id)
