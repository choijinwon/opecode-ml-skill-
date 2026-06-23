from __future__ import annotations

from typing import Any

import mlflow.pyfunc
import pandas as pd

from legal_agent_core.config import configure_mlflow
from legal_agent_core.core import answer_legal_question


class ModelWrapper(mlflow.pyfunc.PythonModel):
    """AI Studio/MLflow pyfunc용 wrapper다.

    입력 DataFrame 컬럼:
    - question 또는 message: 사용자 질문
    - user_id: MLflow session 사용자 식별자
    - session_id: MLflow chat session 식별자
    """

    def load_context(self, context: Any) -> None:
        self.context = context

    def predict(self, context: Any, model_input: pd.DataFrame) -> list[dict[str, object]]:
        configure_mlflow()
        records = model_input.to_dict(orient="records")
        outputs = []
        for row in records:
            question = row.get("question") or row.get("message") or ""
            result = answer_legal_question(
                question=str(question),
                user_id=str(row.get("user_id") or "pyfunc-user"),
                session_id=str(row.get("session_id") or "pyfunc-session"),
            )
            outputs.append(result)
        return outputs
