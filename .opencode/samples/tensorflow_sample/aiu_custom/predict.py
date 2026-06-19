from __future__ import annotations

import json
from pathlib import Path

import mlflow.pyfunc
import pandas as pd
import tensorflow as tf


class ModelWrapper(mlflow.pyfunc.PythonModel):
    """TensorFlow pyfunc wrapper used by the AI Studio style sample."""

    def load_context(self, context):
        config_path = Path(context.artifacts["config"])
        model_path = Path(context.artifacts["model"])
        self.config = json.loads(config_path.read_text(encoding="utf-8"))
        self.model = tf.keras.models.load_model(model_path)

    def predict(self, context, model_input: pd.DataFrame):
        if not isinstance(model_input, pd.DataFrame):
            model_input = pd.DataFrame(model_input)
        return self.model.predict(model_input.to_numpy(), verbose=0)

