import argparse
import importlib.metadata
import json
import os
import platform
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path


ENV_KEYS = [
    "MLFLOW_TRACKING_URI",
    "MLFLOW_EXPERIMENT_NAME",
    "MLFLOW_EXPERIMENT_ID",
]

CORE_PACKAGES = [
    "mlflow",
    "scikit-learn",
    "torch",
    "tensorflow",
    "transformers",
]


@dataclass
class PackageStatus:
    name: str
    status: str
    version: str | None = None


@dataclass
class EnvVarStatus:
    name: str
    status: str


@dataclass
class EnvFileStatus:
    path: str
    key_status: list[EnvVarStatus] = field(default_factory=list)


@dataclass
class EnvironmentReport:
    project_path: str
    os: str
    python_executable: str
    python_version: str
    virtual_env: str
    dependency_files: list[str]
    packages: list[PackageStatus] = field(default_factory=list)
    env_vars: list[EnvVarStatus] = field(default_factory=list)
    optional_config: EnvFileStatus | None = None
    failures: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)


def package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def env_status(name: str) -> str:
    value = os.environ.get(name)
    if value is None:
        return "missing"
    if value == "":
        return "empty"
    return "set"


def dependency_files(project: Path) -> list[str]:
    names = ["requirements.txt", "pyproject.toml", "environment.yml", "environment.yaml"]
    return [name for name in names if (project / name).exists()]


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


def optional_config_status(project: Path) -> EnvFileStatus:
    path = project / "config" / "mlflow_config.json"
    if path.exists():
        return EnvFileStatus(str(path), [EnvVarStatus("config/mlflow_config.json", "set")])
    return EnvFileStatus(str(path), [EnvVarStatus("config/mlflow_config.json", "missing")])


def build_report(project: Path) -> EnvironmentReport:
    deps = dependency_files(project)
    packages = []
    for package in CORE_PACKAGES:
        version = package_version(package)
        packages.append(PackageStatus(package, "set" if version else "missing", version))

    env_vars = [EnvVarStatus(key, env_status(key)) for key in ENV_KEYS]
    optional_config = optional_config_status(project)
    failures: list[str] = []
    next_steps: list[str] = []

    if not deps:
        failures.append("missing_dependency_file")
        next_steps.append("Add or confirm requirements.txt, pyproject.toml, or environment.yml.")
    if package_version("mlflow") is None:
        failures.append("missing_dependency:mlflow")
        next_steps.append("Install or activate an environment that includes mlflow.")
    if env_status("MLFLOW_TRACKING_URI") == "missing":
        next_steps.append("Confirm local or remote MLFLOW_TRACKING_URI before MLflow verification.")

    virtual_env = os.environ.get("VIRTUAL_ENV") or os.environ.get("CONDA_PREFIX") or "not detected"
    return EnvironmentReport(
        project_path=str(project),
        os=f"{platform.system()} {platform.release()}",
        python_executable=sys.executable,
        python_version=platform.python_version(),
        virtual_env=virtual_env,
        dependency_files=deps,
        packages=packages,
        env_vars=env_vars,
        optional_config=optional_config,
        failures=failures,
        next_steps=next_steps,
    )


def print_text(report: EnvironmentReport):
    print(f"Project: {report.project_path}")
    print(f"OS: {report.os}")
    print(f"Python: {report.python_version} ({report.python_executable})")
    print(f"Virtual env: {report.virtual_env}")
    print(f"Dependency files: {', '.join(report.dependency_files) if report.dependency_files else 'missing'}")
    print("\nPackages:")
    for package in report.packages:
        suffix = f" {package.version}" if package.version else ""
        print(f"- {package.name}: {package.status}{suffix}")
    print("\nEnvironment variables:")
    for item in report.env_vars:
        print(f"- {item.name}: {item.status}")
    if report.optional_config:
        print(f"\nOptional MLflow config: {report.optional_config.path}")
        for item in report.optional_config.key_status:
            print(f"- {item.name}: {item.status}")
    if report.failures:
        print("\nFailures:")
        for failure in report.failures:
            print(f"- {failure}")
    if report.next_steps:
        print("\nNext steps:")
        for step in report.next_steps:
            print(f"- {step}")


def main():
    parser = argparse.ArgumentParser(description="Check local ML project execution environment and optional MLflow settings.")
    parser.add_argument("--project", default=".", help="model project folder")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()

    project = Path(args.project).expanduser().resolve()
    if not project.exists():
        raise FileNotFoundError(f"project folder not found: {project}")

    report = build_report(project)
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print_text(report)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[error] {exc}", file=sys.stderr)
        sys.exit(1)
