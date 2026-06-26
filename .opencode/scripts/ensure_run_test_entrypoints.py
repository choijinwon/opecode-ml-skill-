import argparse
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path


ARTIFACT_SUFFIX_TO_KIND = {
    ".pkl": "sklearn_pickle",
    ".joblib": "sklearn_joblib",
    ".pt": "pytorch",
    ".pth": "pytorch",
    ".onnx": "onnx",
    ".h5": "tensorflow",
    ".keras": "tensorflow",
    ".bst": "xgboost",
    ".ubj": "xgboost",
    ".safetensors": "safetensors",
}

SKIP_DIR_NAMES = {
    ".git",
    ".opencode",
    ".agents",
    ".codex",
    ".venv",
    "__pycache__",
    "node_modules",
    "outputs",
    "mlruns",
    "mlartifacts",
}


@dataclass
class GeneratedRunTest:
    artifact_path: str
    model_kind: str
    entrypoint_path: str
    created: bool
    skipped_reason: str | None = None


@dataclass
class RunTestReport:
    project_path: str
    generated: list[GeneratedRunTest] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)


def safe_name(path: Path) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "_", path.stem).strip("_") or "model"


def iter_files(project: Path):
    for path in project.rglob("*"):
        if any(part in SKIP_DIR_NAMES for part in path.relative_to(project).parts):
            continue
        if path.is_file():
            yield path


def find_model_artifacts(project: Path) -> list[Path]:
    artifacts = [
        path
        for path in iter_files(project)
        if path.suffix.lower() in ARTIFACT_SUFFIX_TO_KIND
    ]
    return sorted(artifacts, key=lambda item: str(item.relative_to(project)))


def run_test_filename(index: int) -> str:
    return "run_test.py" if index == 1 else f"run_test{index}.py"


def render_run_test(project: Path, artifact: Path, model_kind: str) -> str:
    rel_artifact = artifact.relative_to(project).as_posix()
    model_var = safe_name(artifact)
    return f'''"""Auto-generated model smoke test entrypoint.

이 파일은 모델 artifact는 있지만 실행 파일이 없을 때 OpenCode MLflow skill이 생성합니다.
목적은 모델 형식에 맞게 로드 가능 여부를 빠르게 확인하는 것입니다.
필요한 dependency가 없으면 설치/환경 검증 단계에서 보완하세요.
"""

import argparse
import json
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_DIR / {rel_artifact!r}
MODEL_KIND = {model_kind!r}
MODEL_NAME = {model_var!r}


def load_json(path: str | None):
    if not path:
        return None
    target = Path(path)
    if not target.is_absolute():
        target = PROJECT_DIR / target
    if not target.exists():
        raise FileNotFoundError(f"input file not found: {{target}}")
    return json.loads(target.read_text(encoding="utf-8"))


def load_model():
    if MODEL_KIND == "sklearn_pickle":
        import pickle

        with MODEL_PATH.open("rb") as handle:
            return pickle.load(handle)

    if MODEL_KIND == "sklearn_joblib":
        import joblib

        return joblib.load(MODEL_PATH)

    if MODEL_KIND == "pytorch":
        import torch

        return torch.load(MODEL_PATH, map_location="cpu")

    if MODEL_KIND == "onnx":
        import onnxruntime as ort

        return ort.InferenceSession(str(MODEL_PATH), providers=["CPUExecutionProvider"])

    if MODEL_KIND == "tensorflow":
        from tensorflow import keras

        return keras.models.load_model(MODEL_PATH)

    if MODEL_KIND == "xgboost":
        import xgboost as xgb

        booster = xgb.Booster()
        booster.load_model(str(MODEL_PATH))
        return booster

    if MODEL_KIND == "safetensors":
        from safetensors.torch import load_file

        return load_file(str(MODEL_PATH))

    raise ValueError(f"unsupported model kind: {{MODEL_KIND}}")


def maybe_predict(model, payload):
    if payload is None:
        return None

    if hasattr(model, "predict"):
        return model.predict(payload)

    if MODEL_KIND == "onnx" and isinstance(payload, dict):
        return model.run(None, payload)

    return None


def main():
    parser = argparse.ArgumentParser(description="Load and smoke-test a local model artifact.")
    parser.add_argument("--input", default="input_example.json", help="optional JSON input file")
    parser.add_argument("--load-only", action="store_true", help="only load the model, skip predict")
    args = parser.parse_args()

    model = load_model()
    print(f"model_path={{MODEL_PATH}}")
    print(f"model_kind={{MODEL_KIND}}")
    print(f"model_name={{MODEL_NAME}}")
    print(f"loaded_type={{type(model).__name__}}")

    if args.load_only:
        print("predict=skipped")
        return

    payload = load_json(args.input) if (PROJECT_DIR / args.input).exists() else None
    result = maybe_predict(model, payload)
    if result is None:
        print("predict=not_available_or_no_input")
    else:
        print(f"predict_type={{type(result).__name__}}")
        print(f"predict={{result}}")


if __name__ == "__main__":
    main()
'''


def ensure_run_tests(project: Path, force: bool = False, execute: bool = True) -> RunTestReport:
    project = project.expanduser().resolve()
    report = RunTestReport(project_path=str(project))

    if not project.exists() or not project.is_dir():
        report.failures.append(f"project_not_found:{project}")
        return report

    artifacts = find_model_artifacts(project)
    if not artifacts:
        report.failures.append("model_artifact_not_found")
        return report

    for index, artifact in enumerate(artifacts, start=1):
        target = project / run_test_filename(index)
        model_kind = ARTIFACT_SUFFIX_TO_KIND[artifact.suffix.lower()]

        if target.exists() and not force:
            report.generated.append(
                GeneratedRunTest(
                    artifact_path=str(artifact),
                    model_kind=model_kind,
                    entrypoint_path=str(target),
                    created=False,
                    skipped_reason="entrypoint_exists",
                )
            )
            continue

        if execute:
            target.write_text(render_run_test(project, artifact, model_kind), encoding="utf-8")

        report.generated.append(
            GeneratedRunTest(
                artifact_path=str(artifact),
                model_kind=model_kind,
                entrypoint_path=str(target),
                created=execute,
            )
        )

    return report


def main():
    parser = argparse.ArgumentParser(description="Create run_test.py entrypoints for detected model artifacts.")
    parser.add_argument("--project", default=".", help="model project folder")
    parser.add_argument("--execute", action="store_true", help="write run_test files")
    parser.add_argument("--force", action="store_true", help="overwrite existing run_test files")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()

    report = ensure_run_tests(Path(args.project), force=args.force, execute=args.execute)

    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print(f"Project: {report.project_path}")
        for item in report.generated:
            status = "created" if item.created else f"skipped:{item.skipped_reason}"
            print(f"- {status} {item.entrypoint_path} for {item.model_kind}: {item.artifact_path}")
        if report.failures:
            print("Failures:")
            for failure in report.failures:
                print(f"- {failure}")

    return 1 if report.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
