import json
from pathlib import Path

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


def main():
    root = Path(__file__).resolve().parent
    config = json.loads((root / "config.json").read_text(encoding="utf-8"))
    artifact_path = root / config["artifact_path"]
    artifact_path.parent.mkdir(parents=True, exist_ok=True)

    model = SimpleNet(input_size=config["input_size"])
    torch.save(model.state_dict(), artifact_path)
    print(f"saved artifact: {artifact_path}")


if __name__ == "__main__":
    main()
