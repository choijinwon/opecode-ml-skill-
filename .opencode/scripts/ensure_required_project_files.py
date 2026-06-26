import argparse
import json
import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path

from ensure_run_test_entrypoints import ARTIFACT_SUFFIX_TO_KIND
from ensure_run_test_entrypoints import find_model_artifacts
from ensure_run_test_entrypoints import normalize_project_root


REQUIRED_DIRS = ["aiu_custom", "local_serving", "save_model", "aiu_studio"]
KIND_REQUIREMENTS = {
    "sklearn_pickle": ["mlflow", "scikit-learn"],
    "sklearn_joblib": ["mlflow", "joblib", "scikit-learn"],
    "python_dill": ["mlflow", "dill"],
    "python_cloudpickle": ["mlflow", "cloudpickle"],
    "pytorch": ["mlflow", "torch"],
    "onnx": ["mlflow", "onnxruntime"],
    "tensorflow": ["mlflow", "tensorflow"],
    "tensorflow_lite": ["mlflow", "tensorflow"],
    "tensorflow_pb": ["mlflow", "tensorflow"],
    "xgboost": ["mlflow", "xgboost"],
    "catboost": ["mlflow", "catboost"],
    "lightgbm": ["mlflow", "lightgbm"],
    "safetensors": ["mlflow", "torch", "safetensors"],
    "numpy_weights": ["mlflow", "numpy"],
}


@dataclass
class EnsuredFile:
    path: str
    created: bool
    skipped_reason: str | None = None


@dataclass
class RequiredFilesReport:
    project_path: str
    data_model_file: str | None
    model_kind: str | None
    ensured: list[EnsuredFile] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)


def write_if_missing(path: Path, content: str, report: RequiredFilesReport, force: bool = False):
    if path.exists() and not force:
        report.ensured.append(EnsuredFile(str(path), created=False, skipped_reason="exists"))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    report.ensured.append(EnsuredFile(str(path), created=True))


def touch_dir(path: Path, report: RequiredFilesReport):
    path.mkdir(parents=True, exist_ok=True)
    report.ensured.append(EnsuredFile(str(path), created=True if not any(path.iterdir()) else False, skipped_reason=None if not any(path.iterdir()) else "exists"))


def render_requirements(model_kind: str) -> str:
    packages = KIND_REQUIREMENTS.get(model_kind, ["mlflow"])
    return "\n".join(packages) + "\n"


def render_input_example(model_kind: str) -> str:
    if model_kind == "onnx":
        payload = {"input": [[0.0]]}
    elif model_kind in {"pytorch", "safetensors"}:
        payload = {"inputs": [[0.0]]}
    else:
        payload = {"inputs": [[0.0]]}
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def render_predict(project: Path, artifact: Path, model_kind: str) -> str:
    rel_artifact = artifact.relative_to(project).as_posix()
    rel_data_artifact = artifact.relative_to(project / "data").as_posix()
    return f'''"""AI Studio compatible MLflow pyfunc wrapper.

이 파일은 data/ 폴더에 모델 파일은 있지만 필수 실행 파일이 없을 때 자동 생성됩니다.
모델 형식별 로더는 {model_kind!r} 기준입니다.
"""

from pathlib import Path

import mlflow.pyfunc


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_MODEL_PATH = PROJECT_DIR / {rel_artifact!r}
AIU_STUDIO_MODEL_PATH = PROJECT_DIR / "aiu_studio" / {rel_data_artifact!r}
MODEL_PATH = AIU_STUDIO_MODEL_PATH if AIU_STUDIO_MODEL_PATH.exists() else DATA_MODEL_PATH
MODEL_KIND = {model_kind!r}


class ModelWrapper(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        self.model = load_model()

    def predict(self, context, model_input, params=None):
        if hasattr(self.model, "predict"):
            return self.model.predict(model_input)
        if MODEL_KIND == "onnx" and isinstance(model_input, dict):
            return self.model.run(None, model_input)
        return {{
            "model_path": str(MODEL_PATH),
            "model_kind": MODEL_KIND,
            "message": "model loaded; custom predict logic is required for this model type",
        }}


def load_model():
    if MODEL_KIND == "sklearn_pickle":
        import pickle

        with MODEL_PATH.open("rb") as handle:
            return pickle.load(handle)

    if MODEL_KIND == "sklearn_joblib":
        import joblib

        return joblib.load(MODEL_PATH)

    if MODEL_KIND == "python_dill":
        import dill

        with MODEL_PATH.open("rb") as handle:
            return dill.load(handle)

    if MODEL_KIND == "python_cloudpickle":
        import cloudpickle

        with MODEL_PATH.open("rb") as handle:
            return cloudpickle.load(handle)

    if MODEL_KIND == "pytorch":
        import torch

        return torch.load(MODEL_PATH, map_location="cpu")

    if MODEL_KIND == "onnx":
        import onnxruntime as ort

        return ort.InferenceSession(str(MODEL_PATH), providers=["CPUExecutionProvider"])

    if MODEL_KIND == "tensorflow":
        from tensorflow import keras

        return keras.models.load_model(MODEL_PATH)

    if MODEL_KIND == "tensorflow_lite":
        import tensorflow as tf

        interpreter = tf.lite.Interpreter(model_path=str(MODEL_PATH))
        interpreter.allocate_tensors()
        return interpreter

    if MODEL_KIND == "xgboost":
        import xgboost as xgb

        booster = xgb.Booster()
        booster.load_model(str(MODEL_PATH))
        return booster

    if MODEL_KIND == "catboost":
        from catboost import CatBoost

        model = CatBoost()
        model.load_model(str(MODEL_PATH))
        return model

    if MODEL_KIND == "lightgbm":
        import lightgbm as lgb

        return lgb.Booster(model_file=str(MODEL_PATH))

    if MODEL_KIND == "safetensors":
        from safetensors.torch import load_file

        return load_file(str(MODEL_PATH))

    if MODEL_KIND == "numpy_weights":
        import numpy as np

        return np.load(MODEL_PATH)

    if MODEL_KIND in {{
        "tensorflow_pb",
        "pmml",
        "coreml",
        "gguf",
        "torchserve_mar",
        "nemo",
        "tensorrt",
    }}:
        return {{
            "model_path": str(MODEL_PATH),
            "model_kind": MODEL_KIND,
            "message": "file format detected; custom runtime loader is required",
        }}

    raise ValueError(f"unsupported model kind: {{MODEL_KIND}}")
'''


def render_serving_app() -> str:
    return '''"""Minimal local serving app for generated model projects."""

from pathlib import Path
import sys

from fastapi import FastAPI
from pydantic import BaseModel


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from aiu_custom.predict import ModelWrapper


class PredictRequest(BaseModel):
    inputs: object | None = None


app = FastAPI(title="local-model-serving")
wrapper = ModelWrapper()
wrapper.load_context(None)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(request: PredictRequest):
    payload = request.inputs if request.inputs is not None else {}
    result = wrapper.predict(None, payload)
    return {"result": result}
'''


def copy_data_files_to_aiu_studio(project: Path, report: RequiredFilesReport, force: bool = False, execute: bool = True):
    data_dir = project / "data"
    target_root = project / "aiu_studio"
    if not data_dir.is_dir():
        report.failures.append("data_folder_not_found")
        return

    for source in sorted(path for path in data_dir.rglob("*") if path.is_file()):
        relative_path = source.relative_to(data_dir)
        target = target_root / relative_path

        if not execute:
            report.ensured.append(EnsuredFile(str(target), created=False, skipped_reason="dry_run"))
            continue

        if target.exists() and not force:
            report.ensured.append(EnsuredFile(str(target), created=False, skipped_reason="exists"))
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        report.ensured.append(EnsuredFile(str(target), created=True))


def ensure_required_files(project: Path, force: bool = False, execute: bool = True) -> RequiredFilesReport:
    project = normalize_project_root(project)
    report = RequiredFilesReport(project_path=str(project), data_model_file=None, model_kind=None)

    if not project.exists() or not project.is_dir():
        report.failures.append(f"project_not_found:{project}")
        return report

    artifacts = find_model_artifacts(project)
    if not artifacts:
        report.failures.append("data_model_file_not_found")
        return report

    artifact = artifacts[0]
    model_kind = ARTIFACT_SUFFIX_TO_KIND[artifact.suffix.lower()]
    report.data_model_file = str(artifact)
    report.model_kind = model_kind

    if execute:
        for name in REQUIRED_DIRS:
            target_dir = project / name
            target_dir.mkdir(parents=True, exist_ok=True)
            gitkeep = target_dir / ".gitkeep"
            if not gitkeep.exists():
                gitkeep.write_text("", encoding="utf-8")
            report.ensured.append(EnsuredFile(str(target_dir), created=True))

        copy_data_files_to_aiu_studio(project, report, force=force, execute=True)
        write_if_missing(project / "requirements.txt", render_requirements(model_kind), report, force=force)
        write_if_missing(project / "input_example.json", render_input_example(model_kind), report, force=force)
        write_if_missing(project / "aiu_custom" / "__init__.py", "", report, force=force)
        write_if_missing(project / "aiu_custom" / "predict.py", render_predict(project, artifact, model_kind), report, force=force)
        write_if_missing(project / "local_serving" / "serving_app.py", render_serving_app(), report, force=force)
    else:
        for target in [
            project / "requirements.txt",
            project / "input_example.json",
            project / "aiu_custom" / "__init__.py",
            project / "aiu_custom" / "predict.py",
            project / "local_serving" / "serving_app.py",
        ]:
            report.ensured.append(EnsuredFile(str(target), created=False, skipped_reason="dry_run"))
        copy_data_files_to_aiu_studio(project, report, force=force, execute=False)

    return report


def main():
    parser = argparse.ArgumentParser(description="Ensure required project files for a detected data model file.")
    parser.add_argument("--project", default=".", help="model project folder")
    parser.add_argument("--execute", action="store_true", help="write required files")
    parser.add_argument("--force", action="store_true", help="overwrite generated files")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()

    report = ensure_required_files(Path(args.project), force=args.force, execute=args.execute)

    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print(f"Project: {report.project_path}")
        print(f"Data model file: {report.data_model_file or 'not found'}")
        print(f"Model kind: {report.model_kind or 'unknown'}")
        for item in report.ensured:
            status = "created" if item.created else f"skipped:{item.skipped_reason}"
            print(f"- {status} {item.path}")
        if report.failures:
            print("Failures:")
            for failure in report.failures:
                print(f"- {failure}")

    return 1 if report.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
