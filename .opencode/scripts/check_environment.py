import argparse
import importlib.metadata
import json
import os
import platform
import re
import subprocess
import sys
import urllib.error
import urllib.request
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
class ErrorGuide:
    category: str
    evidence: str
    guide: str
    next_action: str


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
    install_command: list[str] = field(default_factory=list)
    install_executed: bool = False
    install_return_code: int | None = None
    error_log_path: str | None = None
    error_guides: list[ErrorGuide] = field(default_factory=list)
    qwen_diagnosis_status: str = "not_requested"
    qwen_diagnosis: str | None = None
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


def parse_requirements(path: Path) -> list[str]:
    packages: list[str] = []
    if not path.exists():
        return packages
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        package = re.split(r"[<>=!~;\\[]", line, maxsplit=1)[0].strip()
        if package:
            packages.append(package)
    return packages


ERROR_GUIDE_PATTERNS = [
    (
        r"ModuleNotFoundError|No module named",
        "missing_python_package",
        "필요한 Python 패키지가 현재 환경에 설치되어 있지 않습니다.",
        "requirements.txt를 확인한 뒤 check_environment.py --install-requirements를 실행하거나 올바른 venv/conda 환경을 활성화하세요.",
    ),
    (
        r"requirements_install_failed|Could not find a version|No matching distribution",
        "requirements_install_failed",
        "requirements.txt 설치 중 패키지 버전 또는 패키지 저장소 문제가 발생했습니다.",
        "폐쇄망 내부 PyPI/mirror 설정, Python 버전, 패키지 버전 제약을 확인하세요.",
    ),
    (
        r"MLFLOW_ALLOW_FILE_STORE|filesystem tracking backend|maintenance mode",
        "mlflow_file_store_policy",
        "MLflow 3.x에서 filesystem tracking backend 정책 제한이 발생했습니다.",
        "sqlite:///mlflow.db 같은 DB backend를 쓰거나, 필요한 경우 MLFLOW_ALLOW_FILE_STORE=true를 명시하세요.",
    ),
    (
        r"Connection refused|Max retries exceeded|Name or service not known|Temporary failure in name resolution",
        "network_or_tracking_unreachable",
        "MLflow server, AI Studio endpoint, 또는 LLM endpoint에 접근하지 못했습니다.",
        "URL, 포트, 방화벽, 프록시, 폐쇄망 DNS, 서비스 기동 상태를 확인하세요.",
    ),
    (
        r"401|403|Unauthorized|Forbidden|authentication|permission denied|Access denied",
        "auth_or_permission_error",
        "인증 정보 또는 권한 문제로 요청이 거부되었습니다.",
        "API key, token, username/password, Secret 주입 상태를 값 노출 없이 set/empty/missing 기준으로 확인하세요.",
    ),
    (
        r"Address already in use|port .* already in use",
        "port_in_use",
        "배포 또는 로컬 서버 포트가 이미 사용 중입니다.",
        "사용 중인 프로세스를 종료하거나 다른 포트를 지정하세요.",
    ),
    (
        r"CUDA out of memory|OutOfMemory|Killed",
        "resource_exhausted",
        "메모리 또는 GPU 리소스가 부족합니다.",
        "batch size, 모델 크기, worker 수를 줄이고 CPU/GPU 메모리 상태를 확인하세요.",
    ),
    (
        r"target_data_model_file_not_found|FileNotFoundError|No such file or directory",
        "file_not_found",
        "필요한 모델 파일 또는 설정 파일 경로를 찾지 못했습니다.",
        "선택한 모델이 <model-project-folder>/data/** 아래에 있는지, 경로가 런타임 기준으로 맞는지 확인하세요.",
    ),
    (
        r"unsupported_data_model_suffix|unsupported model kind",
        "unsupported_model_format",
        "지원하지 않는 모델 확장자 또는 로더 형식입니다.",
        "지원 확장자로 모델을 저장하거나 aiu_custom/predict.py에 커스텀 로더를 추가하세요.",
    ),
]


def read_error_text(error_log: str | None, error_text: str | None, max_chars: int = 12000) -> tuple[str | None, str]:
    if error_text:
        return None, error_text[-max_chars:]
    if not error_log:
        return None, ""
    path = Path(error_log).expanduser().resolve()
    if not path.exists():
        return str(path), f"error_log_file_not_found:{path}"
    return str(path), path.read_text(encoding="utf-8", errors="ignore")[-max_chars:]


def build_error_guides(error_text: str) -> list[ErrorGuide]:
    if not error_text:
        return []
    guides: list[ErrorGuide] = []
    for pattern, category, guide, next_action in ERROR_GUIDE_PATTERNS:
        match = re.search(pattern, error_text, flags=re.IGNORECASE)
        if match:
            guides.append(ErrorGuide(category, match.group(0), guide, next_action))
    if not guides:
        guides.append(
            ErrorGuide(
                "unknown_error",
                error_text.strip().splitlines()[-1][:300] if error_text.strip() else "empty_error_text",
                "등록된 규칙으로 분류되지 않은 오류입니다.",
                "전체 로그의 최초 에러, 마지막 에러, 배포 시점 변경사항을 함께 확인하고 Qwen 진단을 사용하세요.",
            )
        )
    return guides


def qwen_diagnose(error_text: str, guides: list[ErrorGuide]) -> tuple[str, str | None]:
    base_url = os.environ.get("OPENAI_BASE_URL", "").rstrip("/")
    api_key = os.environ.get("OPENAI_API_KEY", "")
    model = os.environ.get("OPENAI_MODEL") or os.environ.get("OPENAI_MODELS", "").split(",", 1)[0].strip()
    if not error_text:
        return "skipped:no_error_text", None
    if not base_url or not model:
        return "skipped:missing_OPENAI_BASE_URL_or_OPENAI_MODEL", None

    prompt = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are an offline Korean MLOps deployment error analyst. Do not expose secrets. Return concise root cause, checks, and fix steps.",
            },
            {
                "role": "user",
                "content": (
                    "다음 배포 오류를 분석해줘. 한국어로 원인, 확인 방법, 조치 순서만 간결하게 작성해.\n\n"
                    f"Rule guides: {[asdict(item) for item in guides]}\n\n"
                    f"Error log:\n{error_text[-8000:]}"
                ),
            },
        ],
        "temperature": 0.1,
    }
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(prompt).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            **({"Authorization": f"Bearer {api_key}"} if api_key else {}),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        content = payload.get("choices", [{}])[0].get("message", {}).get("content")
        return "ok", content
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError, KeyError) as exc:
        return f"failed:{type(exc).__name__}", None


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


def build_report(
    project: Path,
    install_requirements: bool = False,
    python_bin: str | None = None,
    error_log: str | None = None,
    error_text: str | None = None,
    qwen: bool = False,
) -> EnvironmentReport:
    deps = dependency_files(project)
    requirements_path = project / "requirements.txt"
    requirements_packages = parse_requirements(requirements_path)
    package_names = sorted(set(CORE_PACKAGES + requirements_packages))
    packages = []
    for package in package_names:
        version = package_version(package)
        packages.append(PackageStatus(package, "set" if version else "missing", version))

    env_vars = [EnvVarStatus(key, env_status(key)) for key in ENV_KEYS]
    optional_config = optional_config_status(project)
    failures: list[str] = []
    next_steps: list[str] = []
    install_command: list[str] = []
    install_return_code: int | None = None
    error_log_path, deployment_error_text = read_error_text(error_log, error_text)
    error_guides = build_error_guides(deployment_error_text)
    qwen_status = "not_requested"
    qwen_result = None

    if not deps:
        failures.append("missing_dependency_file")
        next_steps.append("Add or confirm requirements.txt, pyproject.toml, or environment.yml.")
    if requirements_path.exists():
        install_command = [python_bin or sys.executable, "-m", "pip", "install", "-r", str(requirements_path)]
        if install_requirements:
            result = subprocess.run(install_command, cwd=project)
            install_return_code = result.returncode
            if install_return_code != 0:
                failures.append(f"requirements_install_failed:{install_return_code}")
        else:
            next_steps.append("Run with --install-requirements to install packages from requirements.txt.")
    if package_version("mlflow") is None:
        failures.append("missing_dependency:mlflow")
        next_steps.append("Install or activate an environment that includes mlflow.")
    if env_status("MLFLOW_TRACKING_URI") == "missing":
        next_steps.append("Confirm local or remote MLFLOW_TRACKING_URI before MLflow verification.")
    if error_guides:
        next_steps.append("Review deployment error guides and apply the suggested fix steps.")
    if qwen:
        qwen_status, qwen_result = qwen_diagnose(deployment_error_text, error_guides)

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
        install_command=install_command,
        install_executed=install_requirements,
        install_return_code=install_return_code,
        error_log_path=error_log_path,
        error_guides=error_guides,
        qwen_diagnosis_status=qwen_status,
        qwen_diagnosis=qwen_result,
        failures=failures,
        next_steps=next_steps,
    )


def print_text(report: EnvironmentReport):
    print(f"Project: {report.project_path}")
    print(f"OS: {report.os}")
    print(f"Python: {report.python_version} ({report.python_executable})")
    print(f"Virtual env: {report.virtual_env}")
    print(f"Dependency files: {', '.join(report.dependency_files) if report.dependency_files else 'missing'}")
    if report.install_command:
        print(f"Requirements install command: {' '.join(report.install_command)}")
        print(f"Requirements install executed: {report.install_executed}")
        print(f"Requirements install return code: {report.install_return_code}")
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
    if report.error_guides:
        print("\nDeployment Error Guides:")
        if report.error_log_path:
            print(f"Error log: {report.error_log_path}")
        for item in report.error_guides:
            print(f"- {item.category}: {item.guide}")
            print(f"  evidence: {item.evidence}")
            print(f"  next: {item.next_action}")
        print(f"Qwen diagnosis status: {report.qwen_diagnosis_status}")
        if report.qwen_diagnosis:
            print(f"Qwen diagnosis:\n{report.qwen_diagnosis}")
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
    parser.add_argument("--python", default=sys.executable, help="Python interpreter to use for requirements installation")
    parser.add_argument("--install-requirements", action="store_true", help="install packages from requirements.txt with python -m pip install -r")
    parser.add_argument("--error-log", help="deployment error log file to analyze")
    parser.add_argument("--error-text", help="deployment error text to analyze")
    parser.add_argument("--qwen-diagnose", action="store_true", help="ask local Qwen through OPENAI_BASE_URL/OPENAI_MODEL for additional diagnosis")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()

    project = Path(args.project).expanduser().resolve()
    if not project.exists():
        raise FileNotFoundError(f"project folder not found: {project}")

    report = build_report(
        project,
        install_requirements=args.install_requirements,
        python_bin=args.python,
        error_log=args.error_log,
        error_text=args.error_text,
        qwen=args.qwen_diagnose,
    )
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
