from __future__ import annotations

from typing import Any

import mlflow.pyfunc
import pandas as pd

from design_agent_core.config import configure_mlflow
from design_agent_core.core import answer_design_request


class ModelWrapper(mlflow.pyfunc.PythonModel):
    """AI Studio/MLflow pyfunc용 디자인 에이전트 wrapper다.

    입력 DataFrame 컬럼:
    - request 또는 message: 디자인 요청
    - user_id: 사용자 식별자
    - session_id: 디자인 작업 세션 식별자
    """

    def load_context(self, context: Any) -> None:
        self.context = context

    def predict(self, context: Any, model_input: pd.DataFrame) -> list[dict[str, object]]:
        configure_mlflow()
        outputs = []
        for row in model_input.to_dict(orient="records"):
            request = row.get("request") or row.get("message") or ""
            outputs.append(
                answer_design_request(
                    request=str(request),
                    user_id=str(row.get("user_id") or "pyfunc-user"),
                    session_id=str(row.get("session_id") or "pyfunc-session"),
                )
            )
        return outputs
