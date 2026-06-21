import argparse
import json
from pathlib import Path

import mlflow
import torch
from torch import nn


class SimpleNet(nn.Module):
    def __init__(self, input_size: int = 4):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_size, 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.layers(x)


def load_inputs(path: Path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    return torch.tensor(payload["inputs"], dtype=torch.float32)


def prepare(root: Path):
    config = json.loads((root / "config.json").read_text(encoding="utf-8"))
    artifact_path = root / config["artifact_path"]
    if not artifact_path.exists():
        raise FileNotFoundError(f"missing artifact: {artifact_path}")
    example = load_inputs(root / "input_example.json")
    return config, artifact_path, example


def register(root: Path):
    config, artifact_path, example = prepare(root)
    model = SimpleNet(input_size=config["input_size"])
    model.load_state_dict(torch.load(artifact_path, map_location="cpu"))
    model.eval()
    with mlflow.start_run():
        mlflow.log_dict(config, "config.json")
        mlflow.pytorch.log_model(model, artifact_path="model", input_example=example, serialization_format="pickle")


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
