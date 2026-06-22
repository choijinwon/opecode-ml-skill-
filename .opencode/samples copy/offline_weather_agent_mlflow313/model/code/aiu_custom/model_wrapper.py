from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import mlflow.pyfunc
import pandas as pd


class ModelWrapper(mlflow.pyfunc.PythonModel):
    """AI Studio/MLflow pyfunc wrapper for the local sklearn model."""

    def load_context(self, context):
        self.model = joblib.load(context.artifacts["model"])
        config_path = Path(context.artifacts["config"])
        self.config = json.loads(config_path.read_text(encoding="utf-8"))

    def predict(self, context, model_input: Any):
        feature_names = self.config.get("feature_names", [])
        if isinstance(model_input, pd.DataFrame):
            input_df = model_input.copy()
        elif isinstance(model_input, dict):
            input_df = pd.DataFrame(model_input)
        else:
            input_df = pd.DataFrame(model_input, columns=feature_names or None)

        if feature_names:
            input_df = input_df[feature_names]
        return self.model.predict(input_df).tolist()
