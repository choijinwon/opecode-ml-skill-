import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DIRS = ["aiu_custom", "local_serving", "save_model", "aiu_studio"]
ENTRYPOINTS = ["train.py", "scripts/train.py", "run_test.py"]
SKIP_DIR_NAMES = {".git", ".opencode", ".agents", ".codex", "__pycache__", "node_modules", "outputs", "mlartifacts"}
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


@dataclass
class TrainingReport:
    project_path: str
    model_found: bool
    work_path: str
    entrypoint: str | None
    command: list[str]
    executed: bool
    return_code: int | None
    data_model_files: list[str] = field(default_factory=list)
    selected_model_file: str | None = None
    selected_model_kind: str | None = None
    generated_entrypoints: list[str] = field(default_factory=list)
    generated_required_files: list[str] = field(default_factory=list)
    copied_aiu_studio_template_files: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)


def normalize_project_root(project: Path) -> Path:
    project = project.expanduser().resolve()
    if project.is_dir():
        for candidate in (project, *project.parents):
            if candidate.name == "data":
                return candidate.parent
    return project


def should_skip_dir(name: str) -> bool:
    lowered = name.lower()
    return name in SKIP_DIR_NAMES or name.startswith(".") or lowered in {"venv", "env"} or lowered.startswith("venv-")


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
        if len(root_path.parts) - base_depth >= 8:
            dirs[:] = []
        dirs[:] = [dirname for dirname in dirs if not should_skip_dir(dirname)]
        for dirname in dirs:
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


def safe_name(path: Path) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "_", path.stem).strip("_") or "model"


def find_entrypoint(project: Path) -> Path | None:
    for name in ENTRYPOINTS:
        candidate = project / name
        if candidate.exists():
            return candidate
    for candidate in sorted(project.glob("run_test*.py")):
        if candidate.is_file():
            return candidate
    return None


def build_command(python_bin: str, entrypoint: Path, prepare_only: bool) -> list[str]:
    cmd = [python_bin, str(entrypoint)]
    if prepare_only and entrypoint.name == "register_model.py":
        cmd.append("--prepare-only")
    if prepare_only and entrypoint.name.startswith("run_test"):
        cmd.append("--load-only")
    return cmd


def find_artifacts(project: Path) -> list[str]:
    found = [str(path) for path in find_model_artifacts(project)]
    for path in project.rglob("*"):
        if path.is_file() and path.name in {"MLmodel", "python_model.pkl"}:
            found.append(str(path))
    return sorted(set(found))


def missing_required_dirs(project: Path) -> list[str]:
    return [name for name in REQUIRED_DIRS if not (project / name).is_dir()]


def resolve_target_model(project: Path, target_model: str) -> Path:
    target = Path(target_model).expanduser()
    candidates = [target] if target.is_absolute() else [project / target, project / "data" / target]
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved.exists() and resolved.is_file():
            return resolved
    raise FileNotFoundError(f"target_data_model_file_not_found:{target_model}")


def resolve_target_model_by_index(project: Path, target_index: int) -> Path:
    artifacts = find_model_artifacts(project)
    if target_index < 1:
        raise ValueError(f"target_index_must_be_1_or_greater:{target_index}")
    if not artifacts:
        raise FileNotFoundError("data_model_file_not_found")
    if target_index > len(artifacts):
        raise ValueError(f"target_index_out_of_range:{target_index};available:{len(artifacts)}")
    return artifacts[target_index - 1]


def default_aiu_studio_template_source(model_kind: str) -> Path | None:
    preferred = ROOT / "sample" / "aiu_studio"
    if preferred.is_dir():
        return preferred

    if model_kind in {"pytorch", "safetensors", "torchserve_mar", "nemo"}:
        sample_name = "pytorch_sample"
    elif model_kind in {"tensorflow", "tensorflow_pb", "tensorflow_lite"}:
        sample_name = "tensorflow_sample"
    else:
        sample_name = "sklearn_sample"

    fallback = ROOT / "samples" / sample_name / "aiu_studio"
    return fallback if fallback.is_dir() else None


def copy_aiu_studio_template(project: Path, model_kind: str, force: bool = False) -> tuple[list[str], str | None, list[str]]:
    source_dir = default_aiu_studio_template_source(model_kind)
    if source_dir is None:
        return [], None, ["aiu_studio_template_not_found:.opencode/sample/aiu_studio or .opencode/samples/*_sample/aiu_studio"]

    target_root = project / "aiu_studio"
    copied: list[str] = []
    target_root.mkdir(parents=True, exist_ok=True)
    for source in sorted(path for path in source_dir.rglob("*") if path.is_file()):
        if source.suffix.lower() in ARTIFACT_SUFFIX_TO_KIND:
            continue
        target = target_root / source.relative_to(source_dir)
        if target.exists() and not force:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append(str(target))
    return copied, str(source_dir), []


def render_requirements(model_kind: str) -> str:
    packages = {
        "sklearn_pickle": ["mlflow", "scikit-learn"],
        "sklearn_joblib": ["mlflow", "joblib", "scikit-learn"],
        "pytorch": ["mlflow", "torch"],
        "onnx": ["mlflow", "onnxruntime"],
        "tensorflow": ["mlflow", "tensorflow"],
        "tensorflow_lite": ["mlflow", "tensorflow"],
        "xgboost": ["mlflow", "xgboost"],
        "catboost": ["mlflow", "catboost"],
        "lightgbm": ["mlflow", "lightgbm"],
        "safetensors": ["mlflow", "torch", "safetensors"],
        "numpy_weights": ["mlflow", "numpy"],
    }.get(model_kind, ["mlflow"])
    return "\n".join(packages) + "\n"


def render_input_example(model_kind: str) -> str:
    payload = {"input": [[0.0]]} if model_kind == "onnx" else {"inputs": [[0.0]]}
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def render_run_test(project: Path, artifact: Path, model_kind: str) -> str:
    rel_artifact = artifact.relative_to(project).as_posix()
    return f'''"""Auto-generated model smoke test entrypoint."""

import argparse
import json
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
DATA_MODEL_PATH = PROJECT_DIR / {rel_artifact!r}
AIU_STUDIO_DIR = PROJECT_DIR / "aiu_studio"
MODEL_PATH = DATA_MODEL_PATH
MODEL_KIND = {model_kind!r}
MODEL_NAME = {safe_name(artifact)!r}


def load_json(path: str | None):
    if not path:
        return None
    target = Path(path)
    if not target.is_absolute():
        target = PROJECT_DIR / target
    return json.loads(target.read_text(encoding="utf-8")) if target.exists() else None


def load_model():
    if MODEL_KIND == "sklearn_pickle":
        import pickle
        with MODEL_PATH.open("rb") as handle:
            return pickle.load(handle)
    if MODEL_KIND == "sklearn_joblib":
        import joblib
        return joblib.load(MODEL_PATH)
    if MODEL_KIND == "pytorch":
        try:
            import torch
            return torch.load(MODEL_PATH, map_location="cpu")
        except ModuleNotFoundError:
            return {{"model_path": str(MODEL_PATH), "model_kind": MODEL_KIND, "dependency_required": "torch"}}
        except Exception as exc:
            return {{"model_path": str(MODEL_PATH), "model_kind": MODEL_KIND, "load_error": f"{{type(exc).__name__}}: {{exc}}"}}
    if MODEL_KIND == "onnx":
        import onnxruntime as ort
        return ort.InferenceSession(str(MODEL_PATH), providers=["CPUExecutionProvider"])
    if MODEL_KIND in {{"tensorflow", "tensorflow_lite", "tensorflow_pb"}}:
        from tensorflow import keras
        return keras.models.load_model(MODEL_PATH)
    return {{"model_path": str(MODEL_PATH), "model_kind": MODEL_KIND, "message": "custom runtime loader is required"}}


def main():
    parser = argparse.ArgumentParser(description="Load and smoke-test a local data model file.")
    parser.add_argument("--input", default="input_example.json")
    parser.add_argument("--load-only", action="store_true")
    args = parser.parse_args()

    model = load_model()
    print(f"model_path={{MODEL_PATH}}")
    print(f"model_kind={{MODEL_KIND}}")
    print(f"model_name={{MODEL_NAME}}")
    print(f"loaded_type={{type(model).__name__}}")
    if args.load_only:
        print("predict=skipped")
        return
    payload = load_json(args.input)
    if payload is not None and hasattr(model, "predict"):
        print(f"predict={{model.predict(payload)}}")
    else:
        print("predict=not_available_or_no_input")


if __name__ == "__main__":
    main()
'''


def render_predict(project: Path, artifact: Path, model_kind: str) -> str:
    rel_artifact = artifact.relative_to(project).as_posix()
    return f'''"""AI Studio compatible MLflow pyfunc wrapper."""

from pathlib import Path

import mlflow.pyfunc


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_MODEL_PATH = PROJECT_DIR / {rel_artifact!r}
AIU_STUDIO_DIR = PROJECT_DIR / "aiu_studio"
MODEL_PATH = DATA_MODEL_PATH
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
    if MODEL_KIND == "pytorch":
        try:
            import torch
            return torch.load(MODEL_PATH, map_location="cpu")
        except ModuleNotFoundError:
            return {{"model_path": str(MODEL_PATH), "model_kind": MODEL_KIND, "dependency_required": "torch"}}
        except Exception as exc:
            return {{"model_path": str(MODEL_PATH), "model_kind": MODEL_KIND, "load_error": f"{{type(exc).__name__}}: {{exc}}"}}
    if MODEL_KIND == "onnx":
        import onnxruntime as ort
        return ort.InferenceSession(str(MODEL_PATH), providers=["CPUExecutionProvider"])
    if MODEL_KIND in {{"tensorflow", "tensorflow_lite", "tensorflow_pb"}}:
        from tensorflow import keras
        return keras.models.load_model(MODEL_PATH)
    return {{"model_path": str(MODEL_PATH), "model_kind": MODEL_KIND, "message": "custom runtime loader is required"}}
'''


def write_if_missing(path: Path, content: str, force: bool, generated: list[str]):
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    generated.append(str(path))


def ensure_required_files(project: Path, artifact: Path, model_kind: str, force: bool) -> tuple[list[str], list[str], list[str]]:
    generated: list[str] = []
    failures: list[str] = []
    copied, _source, copy_failures = copy_aiu_studio_template(project, model_kind, force=force)
    failures.extend(copy_failures)

    for name in REQUIRED_DIRS:
        target_dir = project / name
        target_dir.mkdir(parents=True, exist_ok=True)
        gitkeep = target_dir / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("", encoding="utf-8")
        generated.append(str(target_dir))

    write_if_missing(project / "requirements.txt", render_requirements(model_kind), force, generated)
    write_if_missing(project / "input_example.json", render_input_example(model_kind), force, generated)
    write_if_missing(project / "aiu_custom" / "__init__.py", "", force, generated)
    write_if_missing(project / "aiu_custom" / "predict.py", render_predict(project, artifact, model_kind), force, generated)
    write_if_missing(project / "local_serving" / "serving_app.py", "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/health')\ndef health():\n    return {'status': 'ok'}\n", force, generated)
    return generated, copied, failures


def find_template_file(project: Path, template: str | None = None) -> Path | None:
    candidates: list[Path] = []
    if template:
        path = Path(template).expanduser()
        candidates.append(path if path.is_absolute() else project / path)
    candidates.extend([project / "runtest.py", project / "run_test.py"])
    return next((candidate.resolve() for candidate in candidates if candidate.exists() and candidate.is_file()), None)


def replace_assignment(text: str, name: str, value: str) -> tuple[str, bool]:
    updated, count = re.subn(rf"^{name}\s*=.*$", f"{name} = {value}", text, flags=re.MULTILINE)
    return updated, count > 0


def has_assignment(text: str, name: str) -> bool:
    return bool(re.search(rf"^{name}\s*=", text, flags=re.MULTILINE))


def render_selected_run_test(project: Path, artifact: Path, model_kind: str, template: Path | None) -> str:
    if template is None:
        return render_run_test(project, artifact, model_kind)

    rel_artifact = artifact.relative_to(project).as_posix()
    text = template.read_text(encoding="utf-8")
    changed = False
    replacements = {
        "DATA_MODEL_PATH": f"PROJECT_DIR / {rel_artifact!r}",
        "SOURCE_MODEL_PATH": f"PROJECT_DIR / {rel_artifact!r}",
        "MODEL_PATH": "DATA_MODEL_PATH",
        "MODEL_KIND": repr(model_kind),
        "MODEL_TYPE": repr(model_kind),
        "MODEL_FORMAT": repr(model_kind),
        "FRAMEWORK": repr(model_kind),
        "MODEL_NAME": repr(safe_name(artifact)),
        "MODEL_ID": repr(safe_name(artifact)),
        "AIU_STUDIO_DIR": 'PROJECT_DIR / "aiu_studio"',
    }
    for name, value in replacements.items():
        text, did_change = replace_assignment(text, name, value)
        changed = changed or did_change
    if not changed:
        return render_run_test(project, artifact, model_kind)

    support_lines = []
    for name, value in {
        "DATA_MODEL_PATH": f"PROJECT_DIR / {rel_artifact!r}",
        "AIU_STUDIO_DIR": 'PROJECT_DIR / "aiu_studio"',
        "MODEL_PATH": "DATA_MODEL_PATH",
        "MODEL_KIND": repr(model_kind),
        "MODEL_NAME": repr(safe_name(artifact)),
    }.items():
        if not has_assignment(text, name):
            support_lines.append(f"{name} = {value}")
    if support_lines:
        support_block = "\n".join(support_lines) + "\n"
        text = re.sub(r"^(PROJECT_DIR\s*=.*)$", rf"\1\n{support_block}", text, count=1, flags=re.MULTILINE)

    header = f"# Converted by OpenCode MLflow skill.\n# Selected data model: {rel_artifact}\n# Selected model kind: {model_kind}\n\n"
    return text if text.startswith("# Converted by OpenCode MLflow skill.") else header + text


def ensure_run_tests(project: Path, force: bool = False) -> tuple[list[str], list[str]]:
    generated: list[str] = []
    failures: list[str] = []
    artifacts = find_model_artifacts(project)
    if not artifacts:
        return generated, ["data_model_file_not_found"]
    for index, artifact in enumerate(artifacts, start=1):
        target = project / ("run_test.py" if index == 1 else f"run_test{index}.py")
        if target.exists() and not force:
            continue
        target.write_text(render_run_test(project, artifact, ARTIFACT_SUFFIX_TO_KIND[artifact.suffix.lower()]), encoding="utf-8")
        generated.append(str(target))
    return generated, failures


def ensure_selected_run_test(project: Path, artifact: Path, output: str, template: str | None, force: bool, copy_template: bool = True) -> tuple[list[str], list[str], list[str], str]:
    model_kind = ARTIFACT_SUFFIX_TO_KIND[artifact.suffix.lower()]
    copied, source, failures = copy_aiu_studio_template(project, model_kind, force=force) if copy_template else ([], None, [])
    target = project / output
    if target.exists() and not force:
        return [], copied, failures, source or ""
    target.write_text(render_selected_run_test(project, artifact, model_kind, find_template_file(project, template)), encoding="utf-8")
    return [str(target)], copied, failures, source or ""


def run_command(cmd: list[str], cwd: Path) -> int:
    return subprocess.run(cmd, cwd=cwd).returncode


def main():
    parser = argparse.ArgumentParser(description="Prepare and run a local ML model project.")
    parser.add_argument("--project", default=".", help="user-specified model project folder")
    parser.add_argument("--python", default=sys.executable, help="Python interpreter to use")
    parser.add_argument("--target-model", help="selected data model file path, relative to project or data/")
    parser.add_argument("--target-index", type=int, help="1-based selected model number from model_artifact_paths")
    parser.add_argument("--output", default="runtest_2.py", help="output run test filename for selected model mode")
    parser.add_argument("--template", help="template run test file; defaults to runtest.py then run_test.py")
    parser.add_argument("--execute", action="store_true", help="actually run the selected command after preparation")
    parser.add_argument("--force", action="store_true", help="overwrite generated files")
    parser.add_argument("--no-create-run-test", action="store_true", help="do not create run_test.py when data model files are found")
    parser.add_argument("--no-ensure-required-files", action="store_true", help="do not create required project files when data model files are found")
    parser.add_argument("--prepare-only", action="store_true", help="prefer prepare-only mode when supported")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()

    if args.target_model and args.target_index:
        parser.error("use only one of --target-model or --target-index")

    project = normalize_project_root(Path(args.project))
    if not project.exists():
        raise FileNotFoundError(f"project folder not found: {project}")

    failures: list[str] = []
    next_steps: list[str] = []
    generated_entrypoints: list[str] = []
    generated_required_files: list[str] = []
    copied_template_files: list[str] = []
    selected_model: Path | None = None
    selected_kind: str | None = None

    data_model_files = find_model_artifacts(project)
    model_found = bool(data_model_files) or any((project / name).exists() for name in ["train.py", "predict.py", "input_example.json", "MLmodel"])

    if args.target_index or args.target_model:
        selected_model = resolve_target_model_by_index(project, args.target_index) if args.target_index else resolve_target_model(project, args.target_model or "")
        selected_kind = ARTIFACT_SUFFIX_TO_KIND[selected_model.suffix.lower()]
        if not args.no_ensure_required_files:
            generated, copied, required_failures = ensure_required_files(project, selected_model, selected_kind, args.force)
            generated_required_files.extend(generated)
            copied_template_files.extend(copied)
            failures.extend(required_failures)
        generated, copied, selected_failures, _source = ensure_selected_run_test(
            project,
            selected_model,
            args.output,
            args.template,
            args.force,
            copy_template=args.no_ensure_required_files,
        )
        generated_entrypoints.extend(generated)
        copied_template_files.extend(copied)
        failures.extend(selected_failures)
        entrypoint = project / args.output
    else:
        entrypoint = find_entrypoint(project)
        if model_found and data_model_files and not args.no_ensure_required_files:
            generated, copied, required_failures = ensure_required_files(project, data_model_files[0], ARTIFACT_SUFFIX_TO_KIND[data_model_files[0].suffix.lower()], args.force)
            generated_required_files.extend(generated)
            copied_template_files.extend(copied)
            failures.extend(required_failures)
        if entrypoint is None and model_found and data_model_files and not args.no_create_run_test:
            generated, run_test_failures = ensure_run_tests(project, force=args.force)
            generated_entrypoints.extend(generated)
            failures.extend(run_test_failures)
            entrypoint = find_entrypoint(project)

    if not model_found:
        failures.append("model_not_found")
        next_steps.append("Copy or mount the closed-network model under <model-project-folder>/data/** and rerun analysis.")
        next_steps.append("If no closed-network model can be mounted, choose a sample: python .opencode/scripts/bootstrap_sample_project.py --project <model-project-folder> --sample sklearn --execute")

    if entrypoint is None or not entrypoint.exists():
        failures.append("missing_train_entrypoint")
        if model_found and data_model_files:
            next_steps.append("Create run_test.py with .opencode/scripts/run_training.py --project <model-project-folder>")
        cmd = []
    else:
        cmd = build_command(args.python, entrypoint, args.prepare_only)

    return_code = None
    if args.execute and cmd:
        return_code = run_command(cmd, cwd=project)
        if return_code != 0:
            failures.append("runtime_error")
    elif cmd:
        next_steps.append("Run again with --execute to start training or model export.")

    missing_dirs = missing_required_dirs(project)
    if missing_dirs:
        failures.extend(f"missing_required_dir:{name}" for name in missing_dirs)

    report = TrainingReport(
        project_path=str(project),
        model_found=model_found,
        work_path=str(project),
        entrypoint=str(entrypoint) if entrypoint else None,
        command=cmd,
        executed=args.execute,
        return_code=return_code,
        data_model_files=[str(path) for path in data_model_files],
        selected_model_file=str(selected_model) if selected_model else None,
        selected_model_kind=selected_kind,
        generated_entrypoints=generated_entrypoints,
        generated_required_files=generated_required_files,
        copied_aiu_studio_template_files=copied_template_files,
        failures=failures,
        next_steps=next_steps,
    )

    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print(f"Project: {report.project_path}")
        print(f"Work path: {report.work_path}")
        print(f"Model found: {report.model_found}")
        print(f"Entrypoint: {report.entrypoint or 'missing'}")
        print(f"Command: {' '.join(report.command) if report.command else 'none'}")
        print(f"Executed: {report.executed}")
        print(f"Return code: {report.return_code}")
        if report.selected_model_file:
            print(f"Selected model: {report.selected_model_file} ({report.selected_model_kind})")
        print("Data model files:")
        for data_model_file in report.data_model_files:
            print(f"- {data_model_file}")
        print("Generated entrypoints:")
        for generated in report.generated_entrypoints:
            print(f"- {generated}")
        print("Generated required files:")
        for generated in report.generated_required_files:
            print(f"- {generated}")
        print("Copied aiu_studio template files:")
        for copied in report.copied_aiu_studio_template_files:
            print(f"- {copied}")
        if report.failures:
            print("Failures:")
            for failure in report.failures:
                print(f"- {failure}")
        if report.next_steps:
            print("Next steps:")
            for step in report.next_steps:
                print(f"- {step}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[error] {exc}", file=sys.stderr)
        sys.exit(1)
