from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SAVE_MODEL_DIR = ROOT / "save_model"
ARTIFACTS_DIR = ROOT / "artifacts"
MODEL_META_PATH = SAVE_MODEL_DIR / "design_agent_model.json"
LAST_RESPONSE_PATH = ARTIFACTS_DIR / "design_agent_last_response.json"
SOURCE_ANALYSIS_PATH = ARTIFACTS_DIR / "design_source_analysis.json"
COMPONENT_CATALOG_PATH = ARTIFACTS_DIR / "design_component_catalog.json"
DESIGN_GUIDE_PATH = ARTIFACTS_DIR / "design_guide.md"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def save_local_model() -> dict:
    from design_agent_core.config import ai_studio_settings, read_agent_config, secret_status
    from design_agent_core.prompts import PROMPT_NAME

    settings = ai_studio_settings()
    metadata = {
        "agent_name": "design-agent-ai-studio",
        "model_type": "genai-design-agent",
        "ai_studio_model": settings["model"],
        "available_models": settings["models"],
        "prompt_name": PROMPT_NAME,
        "agent_config": read_agent_config(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "secret_status": secret_status(),
    }
    write_json(MODEL_META_PATH, metadata)
    write_json(
        ARTIFACTS_DIR / "design_agent_save_result.json",
        {
            "saved_model": MODEL_META_PATH.as_posix(),
            "message": "save_model 폴더에 디자인 에이전트 모델 메타데이터를 생성했습니다.",
        },
    )
    return metadata


def chat(request: str, user_id: str, session_id: str) -> dict:
    from design_agent_core.config import configure_mlflow
    from design_agent_core.core import answer_design_request

    configure_mlflow()
    result = answer_design_request(request=request, user_id=user_id, session_id=session_id)
    write_json(LAST_RESPONSE_PATH, result)
    return result


def chat_langchain(request: str, user_id: str, session_id: str) -> dict:
    from design_agent_core.config import configure_mlflow
    from design_agent_core.langchain_agent import answer_with_langchain

    configure_mlflow()
    result = answer_with_langchain(request=request, user_id=user_id, session_id=session_id)
    write_json(LAST_RESPONSE_PATH, result)
    return result


def chat_langgraph(request: str, user_id: str, session_id: str) -> dict:
    from design_agent_core.config import configure_mlflow
    from design_agent_core.langgraph_agent import answer_with_langgraph

    configure_mlflow()
    result = answer_with_langgraph(request=request, user_id=user_id, session_id=session_id)
    write_json(LAST_RESPONSE_PATH, result)
    return result


def register_pyfunc_model() -> dict:
    import mlflow
    import pandas as pd
    from aiu_custom.predict import ModelWrapper
    from design_agent_core.config import configure_mlflow

    settings = configure_mlflow()
    if not MODEL_META_PATH.exists():
        save_local_model()
    input_example = pd.DataFrame(
        [
            {
                "request": "B2B SaaS 대시보드 디자인 방향을 잡아줘",
                "user_id": "register-user",
                "session_id": "design-register-session",
            }
        ]
    )
    with mlflow.start_run(run_name="design-agent-register"):
        mlflow.log_artifact(MODEL_META_PATH.as_posix(), artifact_path="save_model")
        model_info = mlflow.pyfunc.log_model(
            artifact_path="design_agent_model",
            python_model=ModelWrapper(),
            input_example=input_example,
            registered_model_name=settings["registered_model_name"],
        )
    payload = {
        "model_uri": model_info.model_uri,
        "registered_model_name": settings["registered_model_name"],
    }
    write_json(ARTIFACTS_DIR / "design_agent_register_result.json", payload)
    return payload


def analyze_source(project_path: str, user_id: str, session_id: str) -> dict:
    from design_agent_core.config import configure_mlflow
    from design_agent_core.source_analyzer import analyze_source_project

    configure_mlflow()
    result = analyze_source_project(
        project_path=project_path,
        user_id=user_id,
        session_id=session_id,
    )
    write_json(SOURCE_ANALYSIS_PATH, result)
    write_json(COMPONENT_CATALOG_PATH, result["catalog"])
    DESIGN_GUIDE_PATH.parent.mkdir(parents=True, exist_ok=True)
    DESIGN_GUIDE_PATH.write_text(str(result["guide_markdown"]), encoding="utf-8")
    return {
        "project_path": result["project_path"],
        "framework": result["framework"],
        "file_count": result["file_count"],
        "component_count": result["component_count"],
        "analysis_json": SOURCE_ANALYSIS_PATH.as_posix(),
        "component_catalog_json": COMPONENT_CATALOG_PATH.as_posix(),
        "design_guide_md": DESIGN_GUIDE_PATH.as_posix(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Design Agent MLflow AI Studio sample")
    parser.add_argument("--save", action="store_true", help="save_model 폴더에 모델 메타데이터를 저장한다.")
    parser.add_argument("--chat", help="기본 디자인 에이전트로 요청을 실행한다.")
    parser.add_argument("--langchain", help="LangChain 스타일 에이전트로 요청을 실행한다.")
    parser.add_argument("--langgraph", help="LangGraph 스타일 에이전트로 요청을 실행한다.")
    parser.add_argument("--analyze-source", help="지정한 소스 프로젝트를 분석해 디자인 가이드 초안을 생성한다.")
    parser.add_argument("--user-id", default="design-demo-user")
    parser.add_argument("--session-id", default="design-demo-session")
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
    elif args.analyze_source:
        result = analyze_source(args.analyze_source, args.user_id, args.session_id)
    elif args.register:
        result = register_pyfunc_model()
    else:
        parser.print_help()
        return

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
