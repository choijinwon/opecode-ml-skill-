from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    import mlflow
    from legal_agent_core.config import ARTIFACTS_DIR, configure_mlflow
    from legal_agent_core.prompts import PROMPT_NAME, SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

    configure_mlflow()
    genai = getattr(mlflow, "genai", None)
    if genai is None or not hasattr(genai, "register_prompt"):
        print("현재 MLflow 환경에서 genai.register_prompt API를 찾을 수 없습니다.")
        return

    prompt = genai.register_prompt(
        name=PROMPT_NAME,
        template=f"{SYSTEM_PROMPT}\n\n{USER_PROMPT_TEMPLATE}",
        commit_message="법률 에이전트 기본 프롬프트 등록",
    )
    try:
        prompt.set_alias("production")
    except Exception:
        pass

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS_DIR / "legal_prompt_registered.txt").write_text(
        f"prompt_name={PROMPT_NAME}\nversion={getattr(prompt, 'version', '')}\n",
        encoding="utf-8",
    )
    print(f"registered prompt: {PROMPT_NAME}")


if __name__ == "__main__":
    main()
