from __future__ import annotations

import json
from pathlib import Path

import joblib
import mlflow.pyfunc
import pandas as pd


class ModelWrapper(mlflow.pyfunc.PythonModel):
    """Small pyfunc wrapper used by the AI Studio style sample."""

    def load_context(self, context):
        model_path = Path(context.artifacts["model"])
        config_path = Path(context.artifacts["config"])
        self.model = joblib.load(model_path)
        self.config = json.loads(config_path.read_text(encoding="utf-8"))

    def predict(self, context, model_input: pd.DataFrame):
        if not isinstance(model_input, pd.DataFrame):
            model_input = pd.DataFrame(model_input)
        return self.model.predict(model_input)
