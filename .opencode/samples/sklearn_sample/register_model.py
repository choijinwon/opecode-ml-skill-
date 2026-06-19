import argparse
import json
from pathlib import Path

import joblib
import mlflow


def prepare(root: Path):
    config = json.loads((root / "config.json").read_text(encoding="utf-8"))
    artifact_path = root / config["artifact_path"]
    if not artifact_path.exists():
        raise FileNotFoundError(f"missing artifact: {artifact_path}")
    _ = json.loads((root / "input_example.json").read_text(encoding="utf-8"))
    return config, artifact_path


def register(root: Path):
    config, artifact_path = prepare(root)
    model = joblib.load(artifact_path)
    with mlflow.start_run():
        mlflow.log_dict(config, "config.json")
        mlflow.sklearn.log_model(model, artifact_path="model")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    if args.prepare_only:
        prepare(root)
        print("prepare check passed")
        return
    register(root)
    print("registration flow completed")


if __name__ == "__main__":
    main()
