from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    from legal_agent_core.config import ARTIFACTS_DIR, configure_mlflow
    from legal_agent_core.prompts import SAFETY_NOTICE

    configure_mlflow()
    response_path = ARTIFACTS_DIR / "legal_agent_last_response.json"
    if response_path.exists():
        response = json.loads(response_path.read_text(encoding="utf-8"))
        answer = str(response.get("answer", ""))
    else:
        answer = ""

    result = {
        "judge_name": "legal-basic-quality-check",
        "criteria": [
            "면책 문구 포함",
            "응답 길이 80자 이상",
            "확인 항목 또는 bullet 포함",
        ],
        "scores": {
            "has_safety_notice": SAFETY_NOTICE in answer,
            "length_ok": len(answer) >= 80,
            "has_checklist": "-" in answer or "확인" in answer,
        },
        "note": "운영 환경에서는 MLflow Judge 또는 AI Studio Judge API로 이 기준을 등록/실행한다.",
    }
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS_DIR / "legal_judge_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
