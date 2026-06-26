import argparse
import json
import os
import re
import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path


ARTIFACT_SUFFIX_TO_KIND = {
    ".pkl": "sklearn_pickle",
    ".pickle": "sklearn_pickle",
    ".sav": "sklearn_pickle",
    ".joblib": "sklearn_joblib",
    ".dill": "python_dill",
    ".cloudpickle": "python_cloudpickle",
    ".pt": "pytorch",
    ".pth": "pytorch",
    ".ckpt": "pytorch",
    ".bin": "pytorch",
    ".onnx": "onnx",
    ".ort": "onnx",
    ".h5": "tensorflow",
    ".hdf5": "tensorflow",
    ".keras": "tensorflow",
    ".pb": "tensorflow_pb",
    ".tflite": "tensorflow_lite",
    ".bst": "xgboost",
    ".ubj": "xgboost",
    ".xgb": "xgboost",
    ".cbm": "catboost",
    ".lgb": "lightgbm",
    ".safetensors": "safetensors",
    ".pmml": "pmml",
    ".mlmodel": "coreml",
    ".gguf": "gguf",
    ".ggml": "gguf",
    ".mar": "torchserve_mar",
    ".nemo": "nemo",
    ".engine": "tensorrt",
    ".plan": "tensorrt",
    ".npz": "numpy_weights",
}

SKIP_DIR_NAMES = {
    ".git",
    ".opencode",
    ".agents",
    ".codex",
    "__pycache__",
    "node_modules",
    "outputs",
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


def normalize_project_root(project: Path) -> Path:
    project = project.expanduser().resolve()
    if project.is_dir():
        for candidate in (project, *project.parents):
            if candidate.name == "data":
                return candidate.parent
    return project


def should_skip_dir(name: str) -> bool:
    lowered = name.lower()
    return (
        name in SKIP_DIR_NAMES
        or name.startswith(".")
        or lowered in {"venv", "env"}
        or lowered.startswith("venv-")
    )


def iter_files(project: Path):
    for path in project.rglob("*"):
        if any(should_skip_dir(part) for part in path.relative_to(project).parts):
            continue
        if path.is_file():
            yield path


def find_data_dirs(project: Path) -> list[Path]:
    project = normalize_project_root(project)
    if not project.exists() or not project.is_dir():
        return []
    if project.name == "data":
        return [project]

    found: list[Path] = []
    direct = project / "data"
    if direct.is_dir():
        found.append(direct)

    base_depth = len(project.parts)
    for root, dirs, _files in os.walk(project):
        root_path = Path(root)
        depth = len(root_path.parts) - base_depth
        if depth >= 8:
            dirs[:] = []
        dirs[:] = [d for d in dirs if not should_skip_dir(d)]
        for dirname in list(dirs):
            if dirname == "data":
                found.append(root_path / dirname)

    return sorted(set(found), key=lambda item: str(item))


def find_model_artifacts(project: Path) -> list[Path]:
    project = normalize_project_root(project)
    artifacts = [
        path
        for data_dir in find_data_dirs(project)
        for path in iter_files(data_dir)
        if path.suffix.lower() in ARTIFACT_SUFFIX_TO_KIND
    ]
    return sorted(artifacts, key=lambda item: str(item.relative_to(project)))


def run_test_filename(index: int) -> str:
    return "run_test.py" if index == 1 else f"run_test{index}.py"


def nearest_data_dir(project: Path, artifact: Path) -> Path:
    project = normalize_project_root(project)
    for candidate in [artifact.parent, *artifact.parents]:
        if candidate.name == "data":
            try:
                candidate.relative_to(project)
            except ValueError:
                continue
            return candidate
    raise ValueError(f"target_model_must_be_under_data:{artifact}")


def copy_data_files_to_aiu_studio(project: Path, data_dir: Path, force: bool = False) -> list[str]:
    project = normalize_project_root(project)
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
    project = normalize_project_root(project)
    target = Path(target_model).expanduser()
    candidates = [target] if target.is_absolute() else [project / target, project / "data" / target]
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved.exists() and resolved.is_file():
            return resolved
    raise FileNotFoundError(f"target_data_model_file_not_found:{target_model}")


def validate_data_model_file(project: Path, model_file: Path) -> str:
    project = normalize_project_root(project)
    nearest_data_dir(project, model_file)

    suffix = model_file.suffix.lower()
    if suffix not in ARTIFACT_SUFFIX_TO_KIND:
        raise ValueError(f"unsupported_data_model_suffix:{suffix}")
    return ARTIFACT_SUFFIX_TO_KIND[suffix]


def render_run_test(project: Path, artifact: Path, model_kind: str) -> str:
    rel_artifact = artifact.relative_to(project).as_posix()
    rel_data_artifact = artifact.relative_to(nearest_data_dir(project, artifact)).as_posix()
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

    if MODEL_KIND == "python_dill":
        import dill

        with MODEL_PATH.open("rb") as handle:
            return dill.load(handle)

    if MODEL_KIND == "python_cloudpickle":
        import cloudpickle

        with MODEL_PATH.open("rb") as handle:
            return cloudpickle.load(handle)

    if MODEL_KIND == "pytorch":
        try:
            import torch
        except ModuleNotFoundError:
            return {{
                "model_path": str(MODEL_PATH),
                "model_kind": MODEL_KIND,
                "dependency_required": "torch",
                "message": "torch is not installed in this Python environment; install/activate a PyTorch runtime before real inference",
            }}

        try:
            return torch.load(MODEL_PATH, map_location="cpu")
        except Exception as exc:
            return {{
                "model_path": str(MODEL_PATH),
                "model_kind": MODEL_KIND,
                "load_error": f"{{type(exc).__name__}}: {{exc}}",
                "message": "torch was imported but the model file could not be loaded; verify that the selected file is a valid PyTorch artifact",
            }}

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
        try:
            from safetensors.torch import load_file
        except ModuleNotFoundError:
            return {{
                "model_path": str(MODEL_PATH),
                "model_kind": MODEL_KIND,
                "dependency_required": "safetensors, torch",
                "message": "safetensors/torch is not installed in this Python environment; install/activate the runtime before real inference",
            }}

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


def has_assignment(text: str, name: str) -> bool:
    return bool(re.search(rf"^{name}\s*=", text, flags=re.MULTILINE))


def insert_support_block(text: str, support_block: str) -> str:
    if not support_block:
        return text
    pattern = re.compile(r"^(PROJECT_DIR\s*=.*)$", re.MULTILINE)
    updated, count = pattern.subn(rf"\1\n{support_block}", text, count=1)
    if count:
        return updated
    return "from pathlib import Path\n\nPROJECT_DIR = Path(__file__).resolve().parent\n" + support_block + text


def replace_first_available_assignment(text: str, names: list[str], value: str) -> tuple[str, bool]:
    changed = False
    for name in names:
        text, did_change = replace_assignment(text, name, value)
        changed = changed or did_change
    return text, changed


def render_selected_run_test(project: Path, artifact: Path, model_kind: str, template: Path | None) -> str:
    if template is None:
        return render_run_test(project, artifact, model_kind)

    rel_artifact = artifact.relative_to(project).as_posix()
    rel_data_artifact = artifact.relative_to(nearest_data_dir(project, artifact)).as_posix()
    model_var = safe_name(artifact)
    text = template.read_text(encoding="utf-8")

    path_value = "AIU_STUDIO_MODEL_PATH if AIU_STUDIO_MODEL_PATH.exists() else DATA_MODEL_PATH"
    replacement_groups = [
        (["DATA_MODEL_PATH", "SOURCE_MODEL_PATH"], f"PROJECT_DIR / {rel_artifact!r}"),
        (["AIU_STUDIO_MODEL_PATH", "AI_STUDIO_MODEL_PATH"], f'PROJECT_DIR / "aiu_studio" / {rel_data_artifact!r}'),
        (
            [
                "MODEL_PATH",
                "MODEL_FILE",
                "MODEL_FILE_PATH",
                "MODEL_ARTIFACT_PATH",
                "ARTIFACT_PATH",
                "TARGET_MODEL_PATH",
                "SELECTED_MODEL_PATH",
            ],
            path_value,
        ),
        (["MODEL_KIND", "MODEL_TYPE", "MODEL_FORMAT", "FRAMEWORK"], repr(model_kind)),
        (["MODEL_NAME", "MODEL_ID"], repr(model_var)),
    ]

    changed = False
    for names, value in replacement_groups:
        text, did_change = replace_first_available_assignment(text, names, value)
        changed = changed or did_change

    if not changed:
        return render_run_test(project, artifact, model_kind)

    header = f'''# Converted by OpenCode MLflow skill.
# Selected data model: {rel_artifact}
# Selected model kind: {model_kind}

'''
    support_lines = []
    if not has_assignment(text, "DATA_MODEL_PATH"):
        support_lines.append(f"DATA_MODEL_PATH = PROJECT_DIR / {rel_artifact!r}")
    if not has_assignment(text, "AIU_STUDIO_MODEL_PATH"):
        support_lines.append(f'AIU_STUDIO_MODEL_PATH = PROJECT_DIR / "aiu_studio" / {rel_data_artifact!r}')
    support_block = "\n".join(support_lines)
    if support_block:
        support_block = support_block + "\n"
        text = insert_support_block(text, support_block)

    if not text.startswith("# Converted by OpenCode MLflow skill."):
        text = header + text

    return text


def ensure_run_tests(project: Path, force: bool = False, execute: bool = True) -> RunTestReport:
    project = normalize_project_root(project)
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
    project = normalize_project_root(project)
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
        report.copied_to_aiu_studio = copy_data_files_to_aiu_studio(project, nearest_data_dir(project, artifact), force=force)

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
