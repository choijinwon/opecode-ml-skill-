import argparse
import json
import re
import shutil
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
    data_model_file: str
    model_kind: str
    entrypoint_path: str
    created: bool
    skipped_reason: str | None = None


@dataclass
class RunTestReport:
    project_path: str
    generated: list[GeneratedRunTest] = field(default_factory=list)
    copied_to_aiu_studio: list[str] = field(default_factory=list)
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
    data_dir = project / "data"
    if not data_dir.is_dir():
        return []

    artifacts = [
        path
        for path in iter_files(data_dir)
        if path.suffix.lower() in ARTIFACT_SUFFIX_TO_KIND
    ]
    return sorted(artifacts, key=lambda item: str(item.relative_to(project)))


def run_test_filename(index: int) -> str:
    return "run_test.py" if index == 1 else f"run_test{index}.py"


def copy_data_files_to_aiu_studio(project: Path, force: bool = False) -> list[str]:
    data_dir = project / "data"
    target_root = project / "aiu_studio"
    copied: list[str] = []

    if not data_dir.is_dir():
        return copied

    target_root.mkdir(parents=True, exist_ok=True)
    for source in sorted(path for path in data_dir.rglob("*") if path.is_file()):
        relative_path = source.relative_to(data_dir)
        target = target_root / relative_path
        if target.exists() and not force:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append(str(target))
    return copied


def resolve_target_model(project: Path, target_model: str) -> Path:
    target = Path(target_model).expanduser()
    candidates = [target] if target.is_absolute() else [project / target, project / "data" / target]
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved.exists() and resolved.is_file():
            return resolved
    raise FileNotFoundError(f"target_data_model_file_not_found:{target_model}")


def validate_data_model_file(project: Path, model_file: Path) -> str:
    try:
        model_file.relative_to(project / "data")
    except ValueError as exc:
        raise ValueError(f"target_model_must_be_under_data:{model_file}") from exc

    suffix = model_file.suffix.lower()
    if suffix not in ARTIFACT_SUFFIX_TO_KIND:
        raise ValueError(f"unsupported_data_model_suffix:{suffix}")
    return ARTIFACT_SUFFIX_TO_KIND[suffix]


def render_run_test(project: Path, artifact: Path, model_kind: str) -> str:
    rel_artifact = artifact.relative_to(project).as_posix()
    rel_data_artifact = artifact.relative_to(project / "data").as_posix()
    model_var = safe_name(artifact)
    return f'''"""Auto-generated model smoke test entrypoint.

이 파일은 data/ 폴더에 모델 파일은 있지만 실행 파일이 없을 때 OpenCode MLflow skill이 생성합니다.
목적은 모델 형식에 맞게 로드 가능 여부를 빠르게 확인하는 것입니다.
필요한 dependency가 없으면 설치/환경 검증 단계에서 보완하세요.
"""

import argparse
import json
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
DATA_MODEL_PATH = PROJECT_DIR / {rel_artifact!r}
AIU_STUDIO_MODEL_PATH = PROJECT_DIR / "aiu_studio" / {rel_data_artifact!r}
MODEL_PATH = AIU_STUDIO_MODEL_PATH if AIU_STUDIO_MODEL_PATH.exists() else DATA_MODEL_PATH
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
    parser = argparse.ArgumentParser(description="Load and smoke-test a local data model file.")
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


def find_template_file(project: Path, template: str | None = None) -> Path | None:
    candidates = []
    if template:
        path = Path(template).expanduser()
        candidates.append(path if path.is_absolute() else project / path)
    candidates.extend([project / "runtest.py", project / "run_test.py"])
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate.resolve()
    return None


def replace_assignment(text: str, name: str, value: str) -> tuple[str, bool]:
    pattern = re.compile(rf"^{name}\s*=.*$", re.MULTILINE)
    replacement = f"{name} = {value}"
    updated, count = pattern.subn(replacement, text)
    return updated, count > 0


def render_selected_run_test(project: Path, artifact: Path, model_kind: str, template: Path | None) -> str:
    if template is None:
        return render_run_test(project, artifact, model_kind)

    rel_artifact = artifact.relative_to(project).as_posix()
    rel_data_artifact = artifact.relative_to(project / "data").as_posix()
    model_var = safe_name(artifact)
    text = template.read_text(encoding="utf-8")

    replacements = {
        "DATA_MODEL_PATH": f"PROJECT_DIR / {rel_artifact!r}",
        "AIU_STUDIO_MODEL_PATH": f'PROJECT_DIR / "aiu_studio" / {rel_data_artifact!r}',
        "MODEL_PATH": "AIU_STUDIO_MODEL_PATH if AIU_STUDIO_MODEL_PATH.exists() else DATA_MODEL_PATH",
        "MODEL_KIND": repr(model_kind),
        "MODEL_NAME": repr(model_var),
    }

    changed = False
    for name, value in replacements.items():
        text, did_change = replace_assignment(text, name, value)
        changed = changed or did_change

    if not changed:
        return render_run_test(project, artifact, model_kind)

    return text


def ensure_run_tests(project: Path, force: bool = False, execute: bool = True) -> RunTestReport:
    project = project.expanduser().resolve()
    report = RunTestReport(project_path=str(project))

    if not project.exists() or not project.is_dir():
        report.failures.append(f"project_not_found:{project}")
        return report

    artifacts = find_model_artifacts(project)
    if not artifacts:
        report.failures.append("data_model_file_not_found")
        return report

    for index, artifact in enumerate(artifacts, start=1):
        target = project / run_test_filename(index)
        model_kind = ARTIFACT_SUFFIX_TO_KIND[artifact.suffix.lower()]

        if target.exists() and not force:
            report.generated.append(
                GeneratedRunTest(
                    data_model_file=str(artifact),
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
                data_model_file=str(artifact),
                model_kind=model_kind,
                entrypoint_path=str(target),
                created=execute,
            )
        )

    return report


def ensure_selected_run_test(
    project: Path,
    target_model: str,
    output: str = "runtest_2.py",
    template: str | None = None,
    force: bool = False,
    execute: bool = True,
) -> RunTestReport:
    project = project.expanduser().resolve()
    report = RunTestReport(project_path=str(project))

    if not project.exists() or not project.is_dir():
        report.failures.append(f"project_not_found:{project}")
        return report

    try:
        artifact = resolve_target_model(project, target_model)
        model_kind = validate_data_model_file(project, artifact)
    except (FileNotFoundError, ValueError) as exc:
        report.failures.append(str(exc))
        return report

    target = project / output
    template_file = find_template_file(project, template)

    if execute:
        report.copied_to_aiu_studio = copy_data_files_to_aiu_studio(project, force=force)

    if target.exists() and not force:
        report.generated.append(
            GeneratedRunTest(
                data_model_file=str(artifact),
                model_kind=model_kind,
                entrypoint_path=str(target),
                created=False,
                skipped_reason="entrypoint_exists",
            )
        )
        return report

    if execute:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_selected_run_test(project, artifact, model_kind, template_file), encoding="utf-8")

    report.generated.append(
        GeneratedRunTest(
            data_model_file=str(artifact),
            model_kind=model_kind,
            entrypoint_path=str(target),
            created=execute,
        )
    )
    return report


def main():
    parser = argparse.ArgumentParser(description="Create run_test.py entrypoints for detected data model files.")
    parser.add_argument("--project", default=".", help="model project folder")
    parser.add_argument("--target-model", help="selected data model file path, relative to project or data/")
    parser.add_argument("--output", default="runtest_2.py", help="output run test filename for --target-model")
    parser.add_argument("--template", help="template run test file; defaults to runtest.py then run_test.py")
    parser.add_argument("--execute", action="store_true", help="write run_test files")
    parser.add_argument("--force", action="store_true", help="overwrite existing run_test files")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()

    if args.target_model:
        report = ensure_selected_run_test(
            Path(args.project),
            target_model=args.target_model,
            output=args.output,
            template=args.template,
            force=args.force,
            execute=args.execute,
        )
    else:
        report = ensure_run_tests(Path(args.project), force=args.force, execute=args.execute)

    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print(f"Project: {report.project_path}")
        for item in report.generated:
            status = "created" if item.created else f"skipped:{item.skipped_reason}"
            print(f"- {status} {item.entrypoint_path} for {item.model_kind}: {item.data_model_file}")
        if report.copied_to_aiu_studio:
            print("Copied to aiu_studio:")
            for copied in report.copied_to_aiu_studio:
                print(f"- {copied}")
        if report.failures:
            print("Failures:")
            for failure in report.failures:
                print(f"- {failure}")

    return 1 if report.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
