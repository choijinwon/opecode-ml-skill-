from __future__ import annotations

import argparse
import io
import json
import logging
import os
import sys
from pathlib import Path

import mlflow
import pandas as pd
from aiu_custom.predict import ModelWrapper


# 이 파일은 AI Studio 스타일 MLflow pyfunc 등록의 루트 실행 파일이다.
# `aiu_custom/`과 `offline_weather_agent_core/`를 code_paths로 함께 패키징한다.
ROOT = Path(__file__).resolve().parent
GENERATED_DIR = ROOT / "generated"
CONFIG_DIR = GENERATED_DIR / "config"
CONFIG_PATH = CONFIG_DIR / "config.json"
INPUT_EXAMPLE_PATH = GENERATED_DIR / "input_example.json"

# 폐쇄망/AI Studio 반입 시 환경별로 코드 상수를 채울 수 있게 비워둔다.
mlflow_tracking_url = ""
mlflow_tracking_username = ""
mlflow_tracking_password = ""
mlflow_experiment_name = ""
mlflow_register_model_name = ""


def configure_windows_utf8():
    """Windows 콘솔에서도 한글 로그가 깨지지 않도록 UTF-8을 설정한다."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name)
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
        elif hasattr(stream, "buffer"):
            setattr(sys, stream_name, io.TextIOWrapper(stream.buffer, encoding="utf-8"))


def configure_mlflow_from_code():
    """AI Studio 배포 환경에서 전달받은 MLflow 접속값을 적용한다."""
    os.environ.setdefault("MLFLOW_TRACKING_INSECURE_TLS", "TRUE")
    if mlflow_tracking_username:
        os.environ["MLFLOW_TRACKING_USERNAME"] = mlflow_tracking_username
    if mlflow_tracking_password:
        os.environ["MLFLOW_TRACKING_PASSWORD"] = mlflow_tracking_password
    if mlflow_tracking_url:
        mlflow.set_tracking_uri(mlflow_tracking_url)
    else:
        mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5001"))
    if mlflow_experiment_name:
        mlflow.set_experiment(mlflow_experiment_name)
    else:
        mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT_NAME", "offline-weather-agent"))


def build_config() -> dict:
    """pyfunc wrapper가 로드할 설정 파일을 만든다."""
    return {
        "question_column": "question",
        "user_id": "aiu-custom-user",
        "session_id": "aiu-custom-session",
        "env": {
            "LLM_PROVIDER": os.getenv("LLM_PROVIDER", "openai"),
            "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", "http://127.0.0.1:11434/v1"),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", "ollama"),
            "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "qwen2.5-coder:14b"),
            "MLFLOW_TRACKING_URI": os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5001"),
            "MLFLOW_EXPERIMENT_NAME": os.getenv("MLFLOW_EXPERIMENT_NAME", "offline-weather-agent"),
        },
    }


def input_example_df() -> pd.DataFrame:
    return pd.DataFrame({"question": ["서울 날씨 알려줘", "부산 날씨 알려줘"]})


def write_generated_files() -> dict:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    config = build_config()
    CONFIG_PATH.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    INPUT_EXAMPLE_PATH.write_text(
        json.dumps({"question": ["서울 날씨 알려줘", "부산 날씨 알려줘"]}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return config


def register_model():
    write_generated_files()
    registered_model_name = mlflow_register_model_name or "offline-weather-agent-aiu-custom"

    with mlflow.start_run(run_name="register-offline-weather-agent-aiu-custom"):
        mlflow.pyfunc.log_model(
            artifact_path="ai_studio",
            python_model=ModelWrapper(),
            code_paths=[
                (ROOT / "aiu_custom").as_posix(),
                (ROOT / "offline_weather_agent_core").as_posix(),
            ],
            artifacts={"config": CONFIG_PATH.as_posix()},
            input_example=input_example_df(),
            registered_model_name=registered_model_name,
            pip_requirements=(ROOT / "requirements.txt").as_posix(),
        )


def main():
    parser = argparse.ArgumentParser(description="AI Studio style MLflow weather agent sample")
    parser.add_argument("--prepare-only", action="store_true", help="create config/input example only")
    parser.add_argument("--register", action="store_true", help="log and register the pyfunc model with MLflow")
    args = parser.parse_args()

    configure_windows_utf8()
    logging.getLogger("mlflow").setLevel(logging.ERROR)

    if args.register:
        configure_mlflow_from_code()
        register_model()
        print("mlflow registration completed")
        return

    write_generated_files()
    print("prepare check passed")


if __name__ == "__main__":
    main()
