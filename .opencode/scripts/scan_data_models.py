import argparse
import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path


MODEL_SUFFIX_TO_KIND = {
    ".pkl": "sklearn_pickle",
    ".pickle": "sklearn_pickle",
    ".sav": "sklearn_pickle",
    ".joblib": "sklearn_joblib",
    ".dill": "python_dill",
    ".cloudpickle": "python_cloudpickle",
    ".pt": "pytorch",
    ".pth": "pytorch",
    ".ckpt": "pytorch",
    ".bin": "pytorch_or_huggingface",
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

DEFAULT_SKIP_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
}


@dataclass
class DataFile:
    path: str
    suffix: str
    model_kind: str | None
    size_bytes: int


@dataclass
class DataDir:
    path: str
    file_count: int
    model_count: int
    model_files: list[DataFile] = field(default_factory=list)
    unsupported_files: list[DataFile] = field(default_factory=list)


@dataclass
class DataScanReport:
    project_path: str
    data_dir_count: int
    data_file_count: int
    model_found: bool
    model_count: int
    model_artifact_paths: list[str]
    data_dirs: list[DataDir]
    skipped_dirs: list[str]


def safe_relative(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def should_skip_dir(name: str, include_hidden: bool, include_opencode: bool) -> bool:
    lowered = name.lower()
    if name == ".opencode" and include_opencode:
        return False
    if name in DEFAULT_SKIP_DIRS:
        return True
    if lowered in {"venv", "env"} or lowered.startswith("venv-"):
        return True
    if not include_hidden and name.startswith("."):
        return True
    return False


def iter_data_dirs(project: Path, include_hidden: bool, include_opencode: bool) -> tuple[list[Path], list[Path]]:
    data_dirs: list[Path] = []
    skipped_dirs: list[Path] = []
    for root, dirs, _files in os.walk(project):
        root_path = Path(root)
        kept_dirs = []
        for dirname in dirs:
            if should_skip_dir(dirname, include_hidden=include_hidden, include_opencode=include_opencode):
                skipped_dirs.append(root_path / dirname)
                continue
            kept_dirs.append(dirname)
            if dirname == "data":
                data_dirs.append(root_path / dirname)
        dirs[:] = kept_dirs
    return sorted(set(data_dirs)), sorted(set(skipped_dirs))


def scan_data_dir(data_dir: Path, project: Path) -> DataDir:
    model_files: list[DataFile] = []
    unsupported_files: list[DataFile] = []
    file_count = 0

    for path in sorted(item for item in data_dir.rglob("*") if item.is_file()):
        file_count += 1
        suffix = path.suffix.lower()
        model_kind = MODEL_SUFFIX_TO_KIND.get(suffix)
        item = DataFile(
            path=safe_relative(path, project),
            suffix=suffix,
            model_kind=model_kind,
            size_bytes=path.stat().st_size,
        )
        if model_kind:
            model_files.append(item)
        else:
            unsupported_files.append(item)

    return DataDir(
        path=safe_relative(data_dir, project),
        file_count=file_count,
        model_count=len(model_files),
        model_files=model_files,
        unsupported_files=unsupported_files,
    )


def build_report(project: Path, include_hidden: bool = False, include_opencode: bool = False) -> DataScanReport:
    project = project.expanduser().resolve()
    if not project.exists() or not project.is_dir():
        raise FileNotFoundError(f"project folder not found: {project}")

    data_dir_paths, skipped_dir_paths = iter_data_dirs(
        project,
        include_hidden=include_hidden,
        include_opencode=include_opencode,
    )
    data_dirs = [scan_data_dir(path, project) for path in data_dir_paths]
    model_artifact_paths = [
        model.path
        for data_dir in data_dirs
        for model in data_dir.model_files
    ]
    data_file_count = sum(data_dir.file_count for data_dir in data_dirs)

    return DataScanReport(
        project_path=str(project),
        data_dir_count=len(data_dirs),
        data_file_count=data_file_count,
        model_found=bool(model_artifact_paths),
        model_count=len(model_artifact_paths),
        model_artifact_paths=model_artifact_paths,
        data_dirs=data_dirs,
        skipped_dirs=[safe_relative(path, project) for path in skipped_dir_paths],
    )


def print_text(report: DataScanReport):
    print(f"Project: {report.project_path}")
    print(f"Data folders: {report.data_dir_count}")
    print(f"Data files: {report.data_file_count}")
    print(f"Model found: {report.model_found}")
    print(f"Model count: {report.model_count}")
    print()

    if report.model_artifact_paths:
        print("Model artifact paths:")
        for index, path in enumerate(report.model_artifact_paths, start=1):
            print(f"{index}. {path}")
        print()

    if report.data_dirs:
        print("Data folder details:")
        for data_dir in report.data_dirs:
            print(f"- {data_dir.path}")
            print(f"  files: {data_dir.file_count}")
            print(f"  models: {data_dir.model_count}")
            for model in data_dir.model_files[:20]:
                print(f"  - [{model.model_kind}] {model.path} ({model.size_bytes} bytes)")
            if data_dir.unsupported_files:
                print(f"  unsupported: {len(data_dir.unsupported_files)}")
    else:
        print("No data folders found.")


def main():
    parser = argparse.ArgumentParser(description="Scan data/ folders and model artifacts only.")
    parser.add_argument("--project", default=".", help="workspace or model project folder")
    parser.add_argument("--include-hidden", action="store_true", help="include hidden folders except .git/.venv/node_modules")
    parser.add_argument("--include-opencode", action="store_true", help="include .opencode sample folders in the scan")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()

    report = build_report(
        Path(args.project),
        include_hidden=args.include_hidden,
        include_opencode=args.include_opencode,
    )
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print_text(report)


if __name__ == "__main__":
    main()
