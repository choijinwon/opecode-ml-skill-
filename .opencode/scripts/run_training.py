import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = ROOT / "samples"
SAMPLE_PRIORITY = ["sklearn_sample", "pytorch_sample", "tensorflow_sample"]
ENTRYPOINTS = ["train.py", "run_model.py", "scripts/train.py"]
REQUIRED_DIRS = ["aiu_custom", "local_serving", "save_model"]
ARTIFACT_DIRS = ["save_model", "model", "artifacts", "saved_model"]
ARTIFACT_SUFFIXES = {".pkl", ".joblib", ".pt", ".pth", ".h5", ".keras", ".onnx", ".safetensors"}
AI_STUDIO_ENV_KEYS = [
    "mlflow_tracking_url",
    "mlflow_tracking_username",
    "mlflow_tracking_password",
    "mlflow_experiment_name",
    "mlflow_register_model_name",
]


@dataclass
class TrainingReport:
    project_path: str
    model_found: bool
    selected_sample: str | None
    work_path: str
    entrypoint: str | None
    command: list[str]
    executed: bool
    return_code: int | None
    artifacts: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)


def has_model_project(project: Path) -> bool:
    markers = ["train.py", "run_model.py", "predict.py", "input_example.json", "MLmodel"]
    if any((project / name).exists() for name in markers):
        return True
    if any((project / name).exists() for name in ARTIFACT_DIRS):
        return True
    return any(path.suffix in ARTIFACT_SUFFIXES for path in project.glob("*") if path.is_file())


def select_sample() -> Path:
    for name in SAMPLE_PRIORITY:
        candidate = SAMPLES_DIR / name
        if candidate.exists():
            return candidate
    raise FileNotFoundError("sample_not_found: sklearn_sample, pytorch_sample, tensorflow_sample are missing")


def prepare_sample(project: Path, force: bool) -> tuple[Path, str]:
    sample = select_sample()
    work_path = project / "work" / sample.name
    if work_path.exists():
        if not force:
            raise FileExistsError(f"sample_prepare_error: work path already exists: {work_path}")
        shutil.rmtree(work_path)
    work_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(sample, work_path)
    return work_path, sample.name


def find_entrypoint(project: Path) -> Path | None:
    for name in ENTRYPOINTS:
        candidate = project / name
        if candidate.exists():
            return candidate
    return None


def build_command(python_bin: str, entrypoint: Path, prepare_only: bool) -> list[str]:
    cmd = [python_bin, str(entrypoint)]
    if prepare_only and entrypoint.name in {"run_model.py", "register_model.py"}:
        cmd.append("--prepare-only")
    return cmd


def find_artifacts(project: Path) -> list[str]:
    found: list[str] = []
    for name in ARTIFACT_DIRS:
        path = project / name
        if path.exists():
            found.append(str(path))
    for path in project.rglob("*"):
        if path.is_file() and (path.suffix in ARTIFACT_SUFFIXES or path.name in {"MLmodel", "python_model.pkl"}):
            found.append(str(path))
    return sorted(set(found))


def missing_required_dirs(project: Path) -> list[str]:
    return [name for name in REQUIRED_DIRS if not (project / name).is_dir()]


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


def missing_ai_studio_env(project: Path) -> list[str]:
    path = project / "ai_studio.env"
    values = parse_env_file(path)
    missing = []
    if not path.exists():
        missing.append("ai_studio.env")
    for key in AI_STUDIO_ENV_KEYS:
        if key not in values or values[key] == "":
            missing.append(key)
    return missing


def run_command(cmd: list[str], cwd: Path) -> int:
    result = subprocess.run(cmd, cwd=cwd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run local training or prepare a standard sample model after ai_studio.env checks.")
    parser.add_argument("--project", default=".", help="user-specified model project folder")
    parser.add_argument("--python", default=sys.executable, help="Python interpreter to use")
    parser.add_argument("--execute", action="store_true", help="actually run the selected command")
    parser.add_argument("--force-sample", action="store_true", help="overwrite existing sample work path")
    parser.add_argument("--prepare-only", action="store_true", help="prefer prepare-only mode when supported")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()

    project = Path(args.project).expanduser().resolve()
    if not project.exists():
        raise FileNotFoundError(f"project folder not found: {project}")

    failures: list[str] = []
    next_steps: list[str] = []
    selected_sample = None
    model_found = has_model_project(project)
    work_path = project

    if not model_found:
        try:
            work_path, selected_sample = prepare_sample(project, force=args.force_sample)
        except Exception as exc:
            failures.append(str(exc))
            entrypoint = None
            cmd: list[str] = []
            report = TrainingReport(str(project), False, None, str(project), None, cmd, False, None, [], failures, [])
            print(json.dumps(asdict(report), ensure_ascii=False, indent=2) if args.json else f"[error] {exc}")
            sys.exit(1)

    entrypoint = find_entrypoint(work_path)
    if entrypoint is None:
        failures.append("missing_train_entrypoint")
        cmd = []
    else:
        cmd = build_command(args.python, entrypoint, args.prepare_only)

    return_code = None
    if args.execute and cmd:
        return_code = run_command(cmd, cwd=work_path)
        if return_code != 0:
            failures.append("runtime_error")
    elif cmd:
        next_steps.append("Run again with --execute to start training or model export.")

    artifacts = find_artifacts(work_path)
    missing_dirs = missing_required_dirs(work_path)
    if missing_dirs:
        failures.extend(f"missing_required_dir:{name}" for name in missing_dirs)
    missing_env = missing_ai_studio_env(work_path)
    if missing_env:
        failures.extend(f"missing_env:{name}" for name in missing_env)
    if args.execute and not artifacts:
        failures.append("artifact_not_created")

    report = TrainingReport(
        project_path=str(project),
        model_found=model_found,
        selected_sample=selected_sample,
        work_path=str(work_path),
        entrypoint=str(entrypoint) if entrypoint else None,
        command=cmd,
        executed=args.execute,
        return_code=return_code,
        artifacts=artifacts,
        failures=failures,
        next_steps=next_steps,
    )

    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print(f"Project: {report.project_path}")
        print(f"Work path: {report.work_path}")
        print(f"Model found: {report.model_found}")
        print(f"Selected sample: {report.selected_sample or 'none'}")
        print(f"Entrypoint: {report.entrypoint or 'missing'}")
        print(f"Command: {' '.join(report.command) if report.command else 'none'}")
        print(f"Executed: {report.executed}")
        print(f"Return code: {report.return_code}")
        print("Artifacts:")
        for artifact in report.artifacts:
            print(f"- {artifact}")
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
