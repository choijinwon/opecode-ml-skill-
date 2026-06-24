import argparse
import json
import shutil
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = ROOT / "samples"

SAMPLES = {
    "sklearn": {
        "path": "sklearn_sample",
        "label": "sklearn 모델",
        "description": "폐쇄망에서 사용자가 sklearn 모델 코드와 데이터를 넣는 기본 샘플",
    },
    "pytorch": {
        "path": "pytorch_sample",
        "label": "PyTorch 모델",
        "description": "폐쇄망에서 사용자가 PyTorch 모델 코드와 데이터를 넣는 기본 샘플",
    },
    "tensorflow": {
        "path": "tensorflow_sample",
        "label": "TensorFlow/Keras 모델",
        "description": "폐쇄망에서 사용자가 TensorFlow/Keras 모델 코드와 데이터를 넣는 기본 샘플",
    },
}

IGNORED_NAMES = {
    ".DS_Store",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "mlruns",
    "mlartifacts",
    "mlflow.db",
}

GENERATED_ROOT_DIRS = {
    "model",
    "saved_model",
}

GENERATED_PATH_PREFIXES = {
    ("artifacts", "ai_studio"),
}

REQUIRED_PROJECT_DIRS = [
    "aiu_custom",
    "local_serving",
    "save_model",
]

IGNORABLE_PROJECT_ROOT_NAMES = {
    ".git",
    ".gitignore",
    ".opencode",
    ".DS_Store",
}


@dataclass
class BootstrapReport:
    project_path: str
    selected_sample: str | None
    sample_source_path: str | None
    execute: bool
    project_empty: bool
    copied: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)


def list_samples() -> list[dict[str, str]]:
    rows = []
    for key, meta in SAMPLES.items():
        source = SAMPLES_DIR / meta["path"]
        rows.append(
            {
                "key": key,
                "label": meta["label"],
                "description": meta["description"],
                "source_path": str(source),
                "available": str(source.exists()).lower(),
                "required_dirs": str(has_required_dirs(source)).lower(),
            }
        )
    return rows


def has_required_dirs(sample: Path) -> bool:
    return all((sample / name).is_dir() for name in REQUIRED_PROJECT_DIRS)


def is_project_empty(project: Path) -> bool:
    if not project.exists():
        return True
    for child in project.iterdir():
        if child.name not in IGNORABLE_PROJECT_ROOT_NAMES:
            return False
    return True


def should_ignore(path: Path) -> bool:
    parts = path.parts
    if any(part in IGNORED_NAMES for part in parts):
        return True
    if parts and parts[0] in GENERATED_ROOT_DIRS:
        return True
    return any(parts[: len(prefix)] == prefix for prefix in GENERATED_PATH_PREFIXES)


def iter_sample_files(sample: Path):
    for path in sample.rglob("*"):
        if should_ignore(path.relative_to(sample)):
            continue
        yield path


def copy_sample(sample: Path, project: Path, force: bool, execute: bool) -> tuple[list[str], list[str]]:
    copied: list[str] = []
    skipped: list[str] = []

    for source in iter_sample_files(sample):
        relative = source.relative_to(sample)
        target = project / relative

        if source.is_dir():
            if execute:
                target.mkdir(parents=True, exist_ok=True)
            copied.append(str(relative) + "/")
            continue

        if target.exists() and not force:
            skipped.append(str(relative))
            continue

        if execute:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        copied.append(str(relative))

    for name in REQUIRED_PROJECT_DIRS:
        target = project / name
        if execute:
            target.mkdir(parents=True, exist_ok=True)
        entry = f"{name}/"
        if entry not in copied:
            copied.append(entry)

    return copied, skipped


def build_next_steps(sample_key: str) -> list[str]:
    return [
        "선택한 샘플 루트에 사용자 모델 코드, 데이터, requirements.txt, run_model.py를 추가한다.",
        "ai_studio.env 또는 config/ai_studio.env.example을 기준으로 MLflow/AI Studio 접속값을 설정한다.",
        "run_model.py를 추가한 뒤 python run_model.py --prepare-only 로 모델 저장 구조를 확인한다.",
        "python run_model.py 로 save_model/ 또는 MLflow artifact 생성 여부를 확인한다.",
        "local_serving/ 또는 aiu_custom/predict.py 기준으로 추론 테스트를 수행한다.",
        "MLflow UI에서 traces, chat-sessions, prompts, judges, datasets 기록을 확인한다.",
        f"선택 샘플: {sample_key}",
    ]


def main():
    parser = argparse.ArgumentParser(description="Bootstrap one bundled offline model sample into an empty project root.")
    parser.add_argument("--project", default=".", help="target project root")
    parser.add_argument("--sample", choices=sorted(SAMPLES), help="sample key: sklearn, pytorch, tensorflow")
    parser.add_argument("--list", action="store_true", help="list selectable samples")
    parser.add_argument("--execute", action="store_true", help="copy files into the project root")
    parser.add_argument("--force", action="store_true", help="allow overwriting existing files")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()

    if args.list:
        rows = list_samples()
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            for row in rows:
                print(f"{row['key']}: {row['label']} - {row['description']}")
                print(f"  source: {row['source_path']}")
                print(f"  available: {row['available']}")
        return

    if not args.sample:
        raise ValueError("--sample is required unless --list is used")

    project = Path(args.project).expanduser().resolve()
    sample_meta = SAMPLES[args.sample]
    sample_source = SAMPLES_DIR / sample_meta["path"]
    failures: list[str] = []
    copied: list[str] = []
    skipped: list[str] = []

    if not sample_source.exists():
        failures.append(f"sample_not_found:{sample_source}")
    elif not has_required_dirs(sample_source):
        failures.append(f"sample_missing_required_dirs:{','.join(REQUIRED_PROJECT_DIRS)}")

    project_empty = is_project_empty(project)
    if project.exists() and not project.is_dir():
        failures.append(f"project_is_not_directory:{project}")
    if not project_empty and not args.force:
        failures.append("project_not_empty")

    if not failures:
        if args.execute:
            project.mkdir(parents=True, exist_ok=True)
        copied, skipped = copy_sample(sample_source, project, force=args.force, execute=args.execute)

    report = BootstrapReport(
        project_path=str(project),
        selected_sample=args.sample,
        sample_source_path=str(sample_source),
        execute=args.execute,
        project_empty=project_empty,
        copied=copied,
        skipped=skipped,
        failures=failures,
        next_steps=build_next_steps(args.sample) if not failures else [],
    )

    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print(f"Project: {report.project_path}")
        print(f"Selected sample: {report.selected_sample}")
        print(f"Sample source: {report.sample_source_path}")
        print(f"Project empty: {report.project_empty}")
        print(f"Execute: {report.execute}")
        print(f"Copied entries: {len(report.copied)}")
        if report.skipped:
            print("Skipped existing files:")
            for item in report.skipped:
                print(f"- {item}")
        if report.failures:
            print("Failures:")
            for failure in report.failures:
                print(f"- {failure}")
        if report.next_steps:
            print("Next steps:")
            for step in report.next_steps:
                print(f"- {step}")

    if failures:
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[error] {exc}", file=sys.stderr)
        sys.exit(1)
