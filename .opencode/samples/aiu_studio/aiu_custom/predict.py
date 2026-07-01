from __future__ import annotations

import json
import os

import joblib
import mlflow.pyfunc


def _normalize_path(path):
    value = str(path).replace("\\", "/").replace("＼", "/").replace("￦", "/").replace("₩", "/")
    while "//" in value and not value.startswith("//"):
        value = value.replace("//", "/")
    return os.path.normpath(value)


def _load_json(path):
    if not path or not os.path.isfile(path):
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _extract_model_input(payload):
    if isinstance(payload, dict):
        for key in ("inputs", "input"):
            values = payload.get(key)
            if isinstance(values, list) and values:
                first_input = values[0]
                if isinstance(first_input, dict) and "data" in first_input:
                    return first_input["data"]
                return values
        for key in ("data", "instances", "features", "x"):
            value = payload.get(key)
            if value is not None:
                return value
    return payload


def _to_model_frame(model_input, feature_names):
    try:
        import pandas as pd
    except Exception:
        return model_input

    if isinstance(model_input, pd.DataFrame):
        if feature_names:
            return model_input[feature_names]
        return model_input

    if feature_names:
        return pd.DataFrame(model_input, columns=feature_names)
    return model_input


class ModelWrapper(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        model_path = _normalize_path(context.artifacts["model"])
        config_path = _normalize_path(context.artifacts.get("config", ""))

        self.config = _load_json(config_path)
        self.feature_names = self.config.get("feature_names", [])
        self.model = joblib.load(model_path)

    def predict(self, context, model_input, params=None):
        if not hasattr(self, "model"):
            return {
                "status": "model_not_loaded",
                "detail": "MLflow calls load_context() before predict().",
                "input": model_input,
            }

        prepared_input = _to_model_frame(
            _extract_model_input(model_input),
            self.feature_names,
        )
        prediction = self.model.predict(prepared_input)

        if hasattr(prediction, "tolist"):
            prediction = prediction.tolist()

        return {"predictions": prediction}


def predict(payload):
    wrapper = ModelWrapper()
    model_path = payload.get("model_path") if isinstance(payload, dict) else None
    if not model_path:
        return {
            "status": "model_path_required",
            "detail": "MLflow serving calls load_context(); direct predict() needs model_path in payload.",
            "input": payload,
        }

    class _Context:
        artifacts = {
            "model": model_path,
            "config": payload.get("config_path", "") if isinstance(payload, dict) else "",
        }

    wrapper.load_context(_Context())
    return wrapper.predict(None, payload)
