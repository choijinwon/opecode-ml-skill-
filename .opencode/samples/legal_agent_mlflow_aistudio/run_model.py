from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SAVE_MODEL_DIR = ROOT / "save_model"
ARTIFACTS_DIR = ROOT / "artifacts"
MODEL_META_PATH = SAVE_MODEL_DIR / "legal_agent_model.json"
LAST_RESPONSE_PATH = ARTIFACTS_DIR / "legal_agent_last_response.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def save_local_model() -> dict:
    from legal_agent_core.config import ai_studio_settings, read_agent_config, secret_status
    from legal_agent_core.prompts import PROMPT_NAME, SAFETY_NOTICE

    SAVE_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    settings = ai_studio_settings()
    metadata = {
        "agent_name": "legal-agent-ai-studio",
        "model_type": "genai-legal-agent",
        "ai_studio_model": settings["model"],
        "available_models": settings["models"],
        "prompt_name": PROMPT_NAME,
        "agent_config": read_agent_config(),
        "safety_notice": SAFETY_NOTICE,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "secret_status": secret_status(),
    }
    write_json(MODEL_META_PATH, metadata)
    write_json(
        ARTIFACTS_DIR / "legal_agent_save_result.json",
        {
            "saved_model": MODEL_META_PATH.as_posix(),
            "message": "save_model 폴더에 법률 에이전트 모델 메타데이터를 생성했습니다.",
        },
    )
    return metadata


def chat(question: str, user_id: str, session_id: str) -> dict:
    from legal_agent_core.config import configure_mlflow
    from legal_agent_core.core import answer_legal_question

    configure_mlflow()
    result = answer_legal_question(question=question, user_id=user_id, session_id=session_id)
    write_json(LAST_RESPONSE_PATH, result)
    return result


def chat_langchain(question: str, user_id: str, session_id: str) -> dict:
    from legal_agent_core.config import configure_mlflow
    from legal_agent_core.langchain_agent import answer_with_langchain

    configure_mlflow()
    result = answer_with_langchain(question=question, user_id=user_id, session_id=session_id)
    write_json(LAST_RESPONSE_PATH, result)
    return result


def chat_langgraph(question: str, user_id: str, session_id: str) -> dict:
    from legal_agent_core.config import configure_mlflow
    from legal_agent_core.langgraph_agent import answer_with_langgraph

    configure_mlflow()
    result = answer_with_langgraph(question=question, user_id=user_id, session_id=session_id)
    write_json(LAST_RESPONSE_PATH, result)
    return result


def register_pyfunc_model() -> dict:
    import mlflow
    import pandas as pd
    from aiu_custom.predict import ModelWrapper
    from legal_agent_core.config import configure_mlflow

    settings = configure_mlflow()
    if not MODEL_META_PATH.exists():
        save_local_model()

    input_example = pd.DataFrame(
        [
            {
                "question": "계약 해지 통보 전에 무엇을 확인해야 하나요?",
                "user_id": "register-user",
                "session_id": "legal-register-session",
            }
        ]
    )
    with mlflow.start_run(run_name="legal-agent-register"):
        mlflow.log_artifact(MODEL_META_PATH.as_posix(), artifact_path="save_model")
        model_info = mlflow.pyfunc.log_model(
            artifact_path="legal_agent_model",
            python_model=ModelWrapper(),
            input_example=input_example,
            registered_model_name=settings["registered_model_name"],
        )
    payload = {
        "model_uri": model_info.model_uri,
        "registered_model_name": settings["registered_model_name"],
    }
    write_json(ARTIFACTS_DIR / "legal_agent_register_result.json", payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Legal Agent MLflow AI Studio sample")
    parser.add_argument("--save", action="store_true", help="save_model 폴더에 모델 메타데이터를 저장한다.")
    parser.add_argument("--chat", help="질문을 실행하고 MLflow trace/session을 남긴다.")
    parser.add_argument("--langchain", help="LangChain 스타일 에이전트로 질문을 실행한다.")
    parser.add_argument("--langgraph", help="LangGraph StateGraph 스타일 에이전트로 질문을 실행한다.")
    parser.add_argument("--user-id", default="legal-demo-user")
    parser.add_argument("--session-id", default="legal-demo-session")
    parser.add_argument("--register", action="store_true", help="MLflow pyfunc model로 등록한다.")
    args = parser.parse_args()

    if args.save:
        result = save_local_model()
    elif args.chat:
        result = chat(args.chat, args.user_id, args.session_id)
    elif args.langchain:
        result = chat_langchain(args.langchain, args.user_id, args.session_id)
    elif args.langgraph:
        result = chat_langgraph(args.langgraph, args.user_id, args.session_id)
    elif args.register:
        result = register_pyfunc_model()
    else:
        parser.print_help()
        return

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
