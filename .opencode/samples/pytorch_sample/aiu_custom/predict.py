from __future__ import annotations

import json
from pathlib import Path

import mlflow.pyfunc
import pandas as pd
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


class ModelWrapper(mlflow.pyfunc.PythonModel):
    """PyTorch pyfunc wrapper used by the AI Studio style sample."""

    def load_context(self, context):
        config_path = Path(context.artifacts["config"])
        model_path = Path(context.artifacts["model"])
        self.config = json.loads(config_path.read_text(encoding="utf-8"))
        self.model = SimpleNet(input_size=self.config["input_size"])
        self.model.load_state_dict(torch.load(model_path, map_location="cpu"))
        self.model.eval()

    def predict(self, context, model_input: pd.DataFrame):
        if not isinstance(model_input, pd.DataFrame):
            model_input = pd.DataFrame(model_input)
        tensor = torch.tensor(model_input.to_numpy(), dtype=torch.float32)
        with torch.no_grad():
            return self.model(tensor).numpy()

