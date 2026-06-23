from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    from design_agent_core.config import ARTIFACTS_DIR, configure_mlflow

    configure_mlflow()
    response_path = ARTIFACTS_DIR / "design_agent_last_response.json"
    if response_path.exists():
        response = json.loads(response_path.read_text(encoding="utf-8"))
        answer = str(response.get("answer", ""))
    else:
        answer = ""

    result = {
        "judge_name": "design-basic-quality-check",
        "criteria": [
            "목표/구조/스타일/접근성 포함",
            "실행 가능한 다음 작업 포함",
            "과장 표현 최소화",
        ],
        "scores": {
            "has_goal": "목표" in answer,
            "has_structure": "구조" in answer or "화면" in answer,
            "has_accessibility": "접근성" in answer or "대비" in answer,
            "has_next_step": "다음 작업" in answer,
        },
        "note": "운영 환경에서는 MLflow Judge 또는 AI Studio Judge API로 이 기준을 등록/실행한다.",
    }
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS_DIR / "design_judge_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
