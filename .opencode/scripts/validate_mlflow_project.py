import argparse
import json
import os
import platform
import re
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = ROOT / "samples"

# When no project path is provided, selectable sample projects are inspected in
# this order. They match the bootstrap choices exposed to users.
SAMPLE_PRIORITY = ["sklearn_sample", "pytorch_sample", "tensorflow_sample"]

PROJECT_CHILD_PRIORITY = [
    "sklearn_sample",
    "pytorch_sample",
    "tensorflow_sample",
    "data",
    "model",
    "models",
]

# The skill pack does not require a fixed file name. These common names are
# used only as hints when detecting a registration or inference entrypoint.
ENTRYPOINT_NAMES = [
    "register_model.py",
    "serve.py",
    "inference.py",
    "predict.py",
    "main.py",
    "app.py",
    "train.py",
]

CONFIG_NAMES = [
    "config.json",
    "model_config.json",
    "mlflow_config.json",
    "config.yaml",
    "config.yml",
]

INPUT_EXAMPLE_NAMES = [
    "input_example.json",
    "sample_input.json",
    "example.json",
]

ARTIFACT_SUFFIXES = [
    ".pkl",
    ".pickle",
    ".sav",
    ".joblib",
    ".dill",
    ".cloudpickle",
    ".pt",
    ".pth",
    ".ckpt",
    ".bin",
    ".onnx",
    ".ort",
    ".h5",
    ".hdf5",
    ".keras",
    ".pb",
    ".tflite",
    ".bst",
    ".ubj",
    ".xgb",
    ".cbm",
    ".lgb",
    ".safetensors",
    ".pmml",
    ".mlmodel",
    ".gguf",
    ".ggml",
    ".mar",
    ".nemo",
    ".engine",
    ".plan",
    ".npz",
]

ARTIFACT_DIR_HINTS = [
    "save_model",
    "saved_model.pb",
    "variables",
    "tokenizer.json",
    "pytorch_model.bin",
    "model.safetensors",
]

REQUIRED_DIRS = [
    "aiu_custom",
    "local_serving",
    "save_model",
    "aiu_studio",
]

SKIP_DIR_NAMES = {
    ".git",
    ".opencode",
    ".agents",
    ".codex",
    "__pycache__",
    "node_modules",
    "outputs",
    "mlartifacts",
}


@dataclass
class Check:
    name: str
    status: str
    message: str
    evidence: list[str] = field(default_factory=list)


@dataclass
class ValidationReport:
    selected_project: str
    selection_reason: str
    model_found: bool
    data_dir_paths: list[str]
    data_file_count: int
    unsupported_data_files: list[str]
    data_model_files: list[str]
    model_artifact_paths: list[str]
    model_artifact_path: str | None
    os: str
    python: str
    checks: list[Check]
    next_steps: list[str]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def safe_relative(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def normalize_project_root(path: Path) -> Path:
    path = path.expanduser().resolve()
    if path.is_dir():
        for candidate in (path, *path.parents):
            if candidate.name == "data":
                return candidate.parent
    return path


def should_skip_dir(name: str) -> bool:
    lowered = name.lower()
    return (
        name in SKIP_DIR_NAMES
        or name.startswith(".")
        or lowered in {"venv", "env"}
        or lowered.startswith("venv-")
    )


def has_project_markers(path: Path) -> bool:
    # Treat the current directory as a model project only when it has clear
    # ML project markers. This prevents the repository root from being selected
    # just because it contains the skill pack itself.
    if not path.exists() or not path.is_dir():
        return False
    marker_names = {
        "requirements.txt",
        "pyproject.toml",
        "environment.yml",
        "environment.yaml",
        "config.json",
        "input_example.json",
        "register_model.py",
        "train.py",
    }
    if any((path / name).exists() for name in marker_names):
        return True
    return bool(find_artifacts(path, max_depth=6))


def score_project(path: Path) -> int:
    # The score is intentionally simple and transparent. It is a candidate
    # ranking aid, not a pass/fail quality score.
    score = 0
    if (path / "requirements.txt").exists():
        score += 5
    if any((path / name).exists() for name in ENTRYPOINT_NAMES):
        score += 4
    if find_artifacts(path, max_depth=3):
        score += 3
    if any((path / name).exists() for name in CONFIG_NAMES):
        score += 2
    if any((path / name).exists() for name in INPUT_EXAMPLE_NAMES):
        score += 2
    if all((path / name).is_dir() for name in REQUIRED_DIRS):
        score += 2
    return score


def iter_child_project_candidates(root: Path) -> list[Path]:
    if not root.exists() or not root.is_dir():
        return []
    candidates: list[Path] = []
    for child in root.iterdir():
        if not child.is_dir() or should_skip_dir(child.name):
            continue
        if has_project_markers(child) or score_project(child) > 0:
            candidates.append(child)
    return candidates


def select_best_child_project(root: Path) -> tuple[Path, str] | None:
    candidates = iter_child_project_candidates(root)
    if not candidates:
        return None

    def rank(path: Path) -> tuple[int, int, str]:
        priority = PROJECT_CHILD_PRIORITY.index(path.name) if path.name in PROJECT_CHILD_PRIORITY else len(PROJECT_CHILD_PRIORITY)
        return (-score_project(path), priority, path.name)

    selected_raw = sorted(candidates, key=rank)[0].resolve()
    selected = normalize_project_root(selected_raw)
    if selected_raw.name == "data" and selected_raw.is_dir():
        return selected, "child data folder under root; using parent project root"
    return selected, f"child model project under root: {selected_raw.name}"


def select_project(explicit: str | None) -> tuple[Path, str]:
    # Priority:
    # 1. explicit user path
    # 2. child project folder under the explicit/current root
    # 3. current directory when it looks like a model project
    # 4. bundled samples, using SAMPLE_PRIORITY as a tie breaker
    if explicit:
        raw_project = Path(explicit).expanduser().resolve()
        project = normalize_project_root(raw_project)
        if has_project_markers(project):
            if raw_project != project and raw_project.is_dir():
                return project, "explicit data folder or subfolder; using parent project root"
            return project, "explicit path"
        child = select_best_child_project(project)
        if child:
            return child
        return project, "explicit path without detected child project"

    cwd = Path.cwd().resolve()
    if has_project_markers(cwd):
        return cwd, "current directory has model project markers"

    child = select_best_child_project(cwd)
    if child:
        return child

    for name in SAMPLE_PRIORITY:
        candidate = SAMPLES_DIR / name
        if candidate.exists() and score_project(candidate) > 0:
            return candidate.resolve(), f"sample priority: {candidate.name}"

    raise FileNotFoundError("No model project candidate found. Provide --project.")


def iter_files(path: Path, max_depth: int = 8):
    # Limit traversal depth and skip heavy/generated directories so this script
    # remains safe to run in large Windows workspaces.
    base_depth = len(path.parts)
    for root, dirs, files in os.walk(path):
        root_path = Path(root)
        depth = len(root_path.parts) - base_depth
        if depth >= max_depth:
            dirs[:] = []
        dirs[:] = [d for d in dirs if not should_skip_dir(d)]
        for file_name in files:
            yield root_path / file_name


def find_data_dirs(path: Path, max_depth: int = 8) -> list[Path]:
    path = path.expanduser().resolve()
    if not path.exists() or not path.is_dir():
        return []
    if path.name == "data":
        return [path]

    direct = path / "data"
    found: list[Path] = []
    if direct.is_dir():
        found.append(direct)

    base_depth = len(path.parts)
    for root, dirs, _files in os.walk(path):
        root_path = Path(root)
        depth = len(root_path.parts) - base_depth
        if depth >= max_depth:
            dirs[:] = []
        dirs[:] = [d for d in dirs if not should_skip_dir(d)]
        for dirname in list(dirs):
            if dirname == "data":
                found.append(root_path / dirname)

    return sorted(set(found), key=lambda item: str(item))


def find_artifacts(path: Path, max_depth: int = 8) -> list[Path]:
    artifacts: list[Path] = []
    path = normalize_project_root(path)
    for data_dir in find_data_dirs(path, max_depth=max_depth):
        for file_path in iter_files(data_dir, max_depth=max_depth):
            if file_path.suffix.lower() in ARTIFACT_SUFFIXES:
                artifacts.append(file_path)
    return sorted(set(artifacts))


def find_data_files(path: Path, max_depth: int = 8) -> list[Path]:
    files: list[Path] = []
    path = normalize_project_root(path)
    for data_dir in find_data_dirs(path, max_depth=max_depth):
        files.extend(iter_files(data_dir, max_depth=max_depth))
    return sorted(set(files))


def detect_framework(project: Path, requirements_text: str, artifacts: list[Path]) -> tuple[str, list[str]]:
    # Framework detection is evidence-based and conservative. Unknown/custom is
    # valid when the project does not expose recognizable dependency or data model
    # hints.
    evidence: list[str] = []
    lowered = requirements_text.lower()
    artifact_names = " ".join(path.name.lower() for path in artifacts)

    rules = [
        ("tensorflow", ["tensorflow", "keras", ".keras", ".h5", ".hdf5", ".pb", ".tflite", "saved_model.pb"]),
        ("pytorch", ["torch", ".pt", ".pth", ".ckpt", ".bin", "pytorch_model.bin"]),
        ("sklearn", ["scikit-learn", "sklearn", ".pkl", ".pickle", ".sav", ".joblib"]),
        ("onnx", ["onnx", ".onnx", ".ort"]),
        ("huggingface", ["transformers", "tokenizer.json", "model.safetensors", ".safetensors"]),
        ("xgboost", ["xgboost", ".bst", ".ubj", ".xgb"]),
        ("catboost", ["catboost", ".cbm"]),
        ("lightgbm", ["lightgbm", ".lgb"]),
        ("llm-local", [".gguf", ".ggml"]),
        ("runtime-package", [".mar", ".nemo", ".engine", ".plan"]),
        ("portable-model", [".pmml", ".mlmodel"]),
    ]

    for framework, hints in rules:
        matched = [hint for hint in hints if hint in lowered or hint in artifact_names]
        if matched:
            evidence.extend(matched)
            return framework, evidence
    return "unknown/custom", evidence


def parse_requirements(project: Path) -> tuple[Path | None, str, list[str]]:
    req = project / "requirements.txt"
    if not req.exists():
        return None, "", []
    text = read_text(req)
    packages = []
    for line in text.splitlines():
        clean = line.strip()
        if clean and not clean.startswith("#"):
            packages.append(clean)
    return req, text, packages


def check_json_file(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, "missing"
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, f"invalid json: {exc}"
    except OSError as exc:
        return False, f"read error: {exc}"
    return True, "valid json"


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def check_optional_mlflow_config(project: Path) -> Check:
    path = project / "config" / "mlflow_config.json"
    if path.exists():
        return Check(
            "optional MLflow config",
            "pass",
            "optional config/mlflow_config.json is available",
            ["config/mlflow_config.json"],
        )
    return Check(
        "optional MLflow config",
        "warn",
        "optional MLflow config is not provided; environment variables or UI settings can be used",
        [],
    )


def find_first_existing(project: Path, names: list[str]) -> Path | None:
    for name in names:
        candidate = project / name
        if candidate.exists():
            return candidate
    return None


def find_entrypoints(project: Path) -> list[Path]:
    found = [project / name for name in ENTRYPOINT_NAMES if (project / name).exists()]
    recursive = [
        path
        for path in iter_files(project, max_depth=3)
        if path.suffix == ".py" and path.name in ENTRYPOINT_NAMES
    ]
    return sorted(set(found + recursive))


def check_aiu_custom(project: Path, entrypoints: list[Path]) -> Check:
    # AI Studio style pyfunc registration depends on aiu_custom being shipped
    # with the model project because mlflow.pyfunc.log_model uses it through
    # code_paths and ModelWrapper.
    entrypoint_text = "\n".join(read_text(path) for path in entrypoints)
    required = any(
        marker in entrypoint_text
        for marker in ["aiu_custom", "ModelWrapper", "code_paths", "PythonModel"]
    )
    aiu_dir = project / "aiu_custom"
    model_wrapper_file = aiu_dir / "model_wrapper.py"
    predict_file = model_wrapper_file if model_wrapper_file.exists() else aiu_dir / "predict.py"

    if not required and not aiu_dir.exists():
        return Check(
            "AI Studio custom wrapper",
            "pass",
            "aiu_custom is not required by detected entrypoints",
            [],
        )

    evidence = []
    if aiu_dir.exists():
        evidence.append("aiu_custom/")
    if model_wrapper_file.exists():
        evidence.append("aiu_custom/model_wrapper.py")
    elif predict_file.exists():
        evidence.append("aiu_custom/predict.py")
    predict_text = read_text(predict_file)
    if "ModelWrapper" in predict_text:
        evidence.append("ModelWrapper")
    if "mlflow.pyfunc.PythonModel" in predict_text or "PythonModel" in predict_text:
        evidence.append("PythonModel")

    missing = []
    if not aiu_dir.exists():
        missing.append("aiu_custom/")
    if not predict_file.exists():
        missing.append("aiu_custom/model_wrapper.py or aiu_custom/predict.py")
    if predict_file.exists() and "ModelWrapper" not in predict_text:
        missing.append("ModelWrapper class")

    if missing:
        return Check(
            "AI Studio custom wrapper",
            "block",
            "aiu_custom wrapper is required but incomplete",
            evidence + [f"missing: {item}" for item in missing],
        )
    return Check(
        "AI Studio custom wrapper",
        "pass",
        "aiu_custom wrapper is available",
        evidence,
    )


def check_required_dirs(project: Path) -> Check:
    evidence = []
    missing = []
    for name in REQUIRED_DIRS:
        if (project / name).is_dir():
            evidence.append(f"{name}/")
        else:
            missing.append(f"{name}/")
    if missing:
        return Check(
            "required project folders",
            "block",
            "required folders are missing",
            [f"missing: {', '.join(missing)}"] + evidence,
        )
    return Check(
        "required project folders",
        "pass",
        "required folders are available",
        evidence,
    )


def write_permission_check(project: Path) -> Check:
    try:
        with tempfile.NamedTemporaryFile(prefix=".mlflow_skill_check_", dir=project, delete=True) as handle:
            handle.write(b"ok")
        return Check(
            name="Windows/write permission check",
            status="pass",
            message="project directory is writable",
            evidence=[str(project)],
        )
    except OSError as exc:
        return Check(
            name="Windows/write permission check",
            status="block",
            message=f"project directory is not writable: {exc}",
            evidence=[str(project)],
        )


def windows_path_check(project: Path) -> Check:
    evidence = [str(project)]
    path_text = str(project)
    warnings = []
    if " " in path_text:
        warnings.append("path contains spaces; quote paths in shell commands")
    if len(path_text) > 240:
        warnings.append("path length is near the classic Windows MAX_PATH limit")
    if platform.system().lower() == "windows":
        evidence.append("running on Windows")
    else:
        evidence.append(f"running on {platform.system()}")

    if warnings:
        return Check("Windows/path compatibility", "warn", "; ".join(warnings), evidence)
    return Check("Windows/path compatibility", "pass", "path is compatible with common Windows constraints", evidence)


def has_prepare_only(entrypoints: list[Path]) -> tuple[bool, list[str]]:
    evidence = []
    # --prepare-only is only one possible implementation. "preflight" or a
    # prepare() function can provide the same registration-before-execution check.
    patterns = ["--prepare-only", "prepare_only", "preflight", "prepare("]
    for path in entrypoints:
        text = read_text(path)
        matched = [pattern for pattern in patterns if pattern in text]
        if matched:
            evidence.append(f"{path.name}: {', '.join(matched)}")
    return bool(evidence), evidence


def has_register_flow(entrypoints: list[Path]) -> tuple[bool, list[str]]:
    evidence = []
    patterns = ["mlflow.", "log_model", "start_run", "registered_model_name"]
    for path in entrypoints:
        text = read_text(path)
        matched = [pattern for pattern in patterns if pattern in text]
        if matched:
            evidence.append(f"{path.name}: {', '.join(matched)}")
    return bool(evidence), evidence


def find_mlflow_code_settings(entrypoints: list[Path]) -> list[str]:
    evidence = []
    setting_names = [
        "mlflow_tracking_url",
        "mlflow_tracking_username",
        "mlflow_tracking_password",
        "mlflow_experiment_name",
        "mlflow_register_model_name",
    ]
    for path in entrypoints:
        text = read_text(path)
        matched = [name for name in setting_names if name in text]
        if matched:
            evidence.append(f"{path.name}: {', '.join(matched)}")
    return evidence


def build_report(project: Path, reason: str, write_check: bool) -> ValidationReport:
    # Build the report in the same order as the 7 OpenCode skills:
    # model select -> project check -> mlflow check -> gap guide ->
    # run-model guide -> preflight check -> register guide.
    checks: list[Check] = []
    project = normalize_project_root(project)

    if not project.exists():
        checks.append(Check("local model path selection", "block", "selected project path does not exist", [str(project)]))
        return ValidationReport(str(project), reason, False, [], 0, [], [], [], None, platform.platform(), sys.version.split()[0], checks, ["Provide a valid --project path."])

    checks.append(Check("local model path selection", "pass", "project selected", [str(project), reason]))

    requirements_path, requirements_text, packages = parse_requirements(project)
    data_dirs = find_data_dirs(project)
    data_files = find_data_files(project)
    artifacts = find_artifacts(project)
    model_found = bool(artifacts)
    data_dir_paths = [safe_relative(path, project) for path in data_dirs]
    unsupported_data_files = [
        safe_relative(path, project)
        for path in data_files
        if path.suffix.lower() not in ARTIFACT_SUFFIXES
    ]
    data_model_files = [safe_relative(path, project) for path in artifacts]
    model_artifact_paths = data_model_files
    model_artifact_path = model_artifact_paths[0] if model_artifact_paths else None
    framework, framework_evidence = detect_framework(project, requirements_text, artifacts)
    entrypoints = find_entrypoints(project)
    config_file = find_first_existing(project, CONFIG_NAMES)
    input_example_file = find_first_existing(project, INPUT_EXAMPLE_NAMES)

    project_evidence = []
    if requirements_path:
        project_evidence.append(safe_relative(requirements_path, project))
    project_evidence.extend(safe_relative(path, project) for path in entrypoints[:5])
    project_evidence.extend(safe_relative(path, project) for path in artifacts[:5])
    checks.append(
        Check(
            "project scan",
            "pass" if entrypoints or artifacts or requirements_path else "warn",
            f"framework candidate: {framework}",
            project_evidence + framework_evidence,
        )
    )
    checks.append(check_required_dirs(project))
    checks.append(check_aiu_custom(project, entrypoints))

    mlflow_evidence = []
    has_mlflow_dep = any(re.match(r"(?i)^mlflow([=<>!~ ]|$)", pkg) for pkg in packages)
    if requirements_path:
        mlflow_evidence.append(f"requirements: {safe_relative(requirements_path, project)}")
    code_settings = find_mlflow_code_settings(entrypoints)
    mlflow_evidence.extend(code_settings)
    checks.append(
        Check(
            "MLflow readiness",
            "pass" if has_mlflow_dep else "warn",
            "mlflow dependency found" if has_mlflow_dep else "mlflow dependency is not confirmed",
            mlflow_evidence,
        )
    )

    # Code constants and project config files are the expected places to
    # confirm MLflow settings.
    config_ok = False
    if config_file:
        config_ok, config_message = check_json_file(config_file) if config_file.suffix == ".json" else (True, "config file exists")
    else:
        config_message = "config file not found"

    input_ok = False
    if input_example_file:
        input_ok, input_message = check_json_file(input_example_file)
    else:
        input_message = "input example not found"

    gap_status = "pass" if config_file and input_example_file and artifacts else "warn"
    checks.append(
        Check(
            "gap guidance",
            gap_status,
            "missing or review-required items are classified",
            [
                f"config: {config_message}",
                f"input_example: {input_message}",
                f"data_dir_count: {len(data_dirs)}",
                f"data_file_count: {len(data_files)}",
                f"data_model_file_count: {len(artifacts)}",
            ],
        )
    )
    checks.append(check_optional_mlflow_config(project))

    register_found, register_evidence = has_register_flow(entrypoints)
    checks.append(
        Check(
            "registration/entrypoint guidance",
            "pass" if register_found else "warn",
            "registration flow evidence found" if register_found else "registration entrypoint is not confirmed",
            register_evidence or [safe_relative(path, project) for path in entrypoints[:5]],
        )
    )

    prepare_found, prepare_evidence = has_prepare_only(entrypoints)
    checks.append(
        Check(
            "prepare-only/preflight check",
            "pass" if prepare_found else "warn",
            "prepare-only or preflight evidence found" if prepare_found else "prepare-only/preflight behavior is not confirmed",
            prepare_evidence,
        )
    )

    local_remote_evidence = []
    # Do not assume a fixed local tracking URI. Each user's local/remote MLflow
    # target should come from their config or environment.
    if config_file and config_file.suffix == ".json":
        try:
            payload = json.loads(config_file.read_text(encoding="utf-8"))
            for key in ["registered_model_name", "experiment_name", "tracking_uri", "tracking_url"]:
                if key in payload:
                    local_remote_evidence.append(f"{key}: present")
        except json.JSONDecodeError:
            pass
    local_remote_evidence.extend(code_settings)
    checks.append(
        Check(
            "local/remote MLflow registration readiness",
            "pass" if local_remote_evidence else "warn",
            "registration settings evidence found" if local_remote_evidence else "tracking/registration settings are not confirmed",
            local_remote_evidence,
        )
    )

    checks.append(windows_path_check(project))
    if write_check:
        checks.append(write_permission_check(project))

    next_steps = []
    if artifacts:
        next_steps.append("Select one model_artifact_path by number or path.")
        next_steps.append("Continue with agent-mlflow-skill-selected-run-test; copy data/ files to aiu_studio/ and create runtest_2.py for the selected model.")
        next_steps.append("After runtest_2.py is created, run environment check, inference test, and MLflow verify in order.")
    if any(check.status == "block" for check in checks):
        next_steps.append("Resolve blocked checks before MLflow registration.")
    if not has_mlflow_dep:
        next_steps.append("Add or confirm mlflow dependency in the project environment.")
    if not artifacts:
        if data_dirs:
            next_steps.append("data/ exists in the current analysis path, but no supported model artifact was found under data/**. If the model exists in a closed-network location, copy or mount it anywhere under this project's data/ tree and rerun analysis.")
        else:
            next_steps.append("No data/** model artifact was found in the current analysis path. If the model exists in a closed-network project, run analysis with that model project path or copy/mount the model under <model-project-folder>/data/**.")
    if not prepare_found:
        next_steps.append("Confirm a prepare-only or preflight behavior before registration.")
    if not local_remote_evidence:
        next_steps.append("Confirm local or remote MLflow tracking settings.")
    if not next_steps:
        next_steps.append("Proceed to local/remote MLflow registration guidance.")

    return ValidationReport(
        str(project),
        reason,
        model_found,
        data_dir_paths,
        len(data_files),
        unsupported_data_files,
        data_model_files,
        model_artifact_paths,
        model_artifact_path,
        platform.platform(),
        sys.version.split()[0],
        checks,
        next_steps,
    )


def print_text(report: ValidationReport):
    print(f"Selected project: {report.selected_project}")
    print(f"Selection reason: {report.selection_reason}")
    print(f"Model found: {report.model_found}")
    print(f"Data folders: {', '.join(report.data_dir_paths) if report.data_dir_paths else 'none'}")
    print(f"Data file count: {report.data_file_count}")
    print(f"Model artifact path: {report.model_artifact_path or 'none'}")
    if report.unsupported_data_files:
        print("Unsupported data files:")
        for item in report.unsupported_data_files[:20]:
            print(f"- {item}")
    print("Model artifact paths:")
    for index, model_artifact_path in enumerate(report.model_artifact_paths, start=1):
        print(f"{index}. {model_artifact_path}")
    print(f"OS: {report.os}")
    print(f"Python: {report.python}")
    print()
    for index, check in enumerate(report.checks, start=1):
        print(f"{index}. [{check.status}] {check.name}")
        print(f"   {check.message}")
        for evidence in check.evidence:
            print(f"   - {evidence}")
    print()
    print("Next steps:")
    for step in report.next_steps:
        print(f"- {step}")


def main():
    parser = argparse.ArgumentParser(description="Validate an MLflow model project using the skill pack checklist.")
    parser.add_argument("--project", help="model project path. If omitted, the script auto-selects a candidate.")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON output")
    parser.add_argument("--no-write-check", action="store_true", help="skip temporary write permission check")
    args = parser.parse_args()

    project, reason = select_project(args.project)
    report = build_report(project, reason, write_check=not args.no_write_check)
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print_text(report)

    if any(check.status == "block" for check in report.checks):
        return 2
    if any(check.status == "warn" for check in report.checks):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
