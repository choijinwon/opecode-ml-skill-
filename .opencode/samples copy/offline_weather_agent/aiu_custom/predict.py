from __future__ import annotations

import json
import os
from pathlib import Path

import mlflow.pyfunc
import pandas as pd


class ModelWrapper(mlflow.pyfunc.PythonModel):
    """AI Studio에서 로드할 수 있는 날씨 에이전트 pyfunc wrapper다."""

    def load_context(self, context):
        config_path = Path(context.artifacts["config"])
        self.config = json.loads(config_path.read_text(encoding="utf-8"))

        for key, value in self.config.get("env", {}).items():
            os.environ.setdefault(key, str(value))

    def predict(self, context, model_input: pd.DataFrame):
        from offline_weather_agent_core.config import configure_mlflow
        from offline_weather_agent_core.core import answer_weather

        configure_mlflow()
        if not isinstance(model_input, pd.DataFrame):
            model_input = pd.DataFrame(model_input)

        question_column = self.config.get("question_column", "question")
        user_id = self.config.get("user_id", "aiu-custom-user")
        session_id = self.config.get("session_id", "aiu-custom-session")

        questions = model_input[question_column].fillna("서울 날씨 알려줘").astype(str).tolist()
        return [answer_weather(question, user_id=user_id, session_id=session_id) for question in questions]

