#!/usr/bin/env bash

set -euo pipefail

# 이 스크립트는 샘플 루트에서 자주 쓰는 실행 명령을 짧게 묶는다.
# 예:
#   ./run.sh mlflow
#   ./run.sh web
#   ./run.sh register
#   ./run.sh prompt
#   ./run.sh judge

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$ROOT_DIR/.venv/bin/python"
VENV_UVICORN="$ROOT_DIR/.venv/bin/uvicorn"
VENV_MLFLOW="$ROOT_DIR/.venv/bin/mlflow"

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "Python 가상환경이 없습니다: $VENV_PYTHON"
  echo "먼저 .venv 환경을 준비해주세요."
  exit 1
fi

show_help() {
  cat <<'EOF'
사용법:
  ./run.sh help
  ./run.sh mlflow
  ./run.sh web
  ./run.sh register
  ./run.sh prompt
  ./run.sh judge
  ./run.sh langchain "서울 날씨 알려줘"
  ./run.sh langgraph "부산 날씨 알려줘"

명령 설명:
  mlflow     로컬 MLflow 서버를 127.0.0.1:5001 에 실행
  web        웹 챗봇 서버를 127.0.0.1:8081 에 실행
  register   모델 학습 + MLflow 등록 실행
  prompt     Prompt Registry 등록 실행
  judge      Judge 등록 및 평가 실행
  langchain  LangChain 샘플 실행
  langgraph  LangGraph 샘플 실행
EOF
}

run_mlflow() {
  cd "$ROOT_DIR"
  exec "$VENV_MLFLOW" server \
    --backend-store-uri "sqlite:///$ROOT_DIR/artifacts/mlflow.db" \
    --default-artifact-root "$ROOT_DIR/artifacts/ai_studio" \
    --host 127.0.0.1 \
    --port 5001
}

run_web() {
  cd "$ROOT_DIR"
  exec "$VENV_UVICORN" offline_weather_agent_core.web:app --host 127.0.0.1 --port 8081
}

run_register() {
  cd "$ROOT_DIR"
  exec "$VENV_PYTHON" run_model.py --register
}

run_prompt() {
  cd "$ROOT_DIR"
  exec "$VENV_PYTHON" registry/prompt.py
}

run_judge() {
  cd "$ROOT_DIR"
  exec "$VENV_PYTHON" registry/judge.py
}

run_langchain() {
  cd "$ROOT_DIR"
  exec "$VENV_PYTHON" offline_weather_agent_core/frameworks/langchain_agent.py "${1:-서울 날씨 알려줘}"
}

run_langgraph() {
  cd "$ROOT_DIR"
  exec "$VENV_PYTHON" offline_weather_agent_core/frameworks/langgraph_agent.py "${1:-부산 날씨 알려줘}"
}

COMMAND="${1:-help}"
ARG1="${2:-}"

case "$COMMAND" in
  help|-h|--help)
    show_help
    ;;
  mlflow)
    run_mlflow
    ;;
  web)
    run_web
    ;;
  register)
    run_register
    ;;
  prompt)
    run_prompt
    ;;
  judge)
    run_judge
    ;;
  langchain)
    run_langchain "$ARG1"
    ;;
  langgraph)
    run_langgraph "$ARG1"
    ;;
  *)
    echo "알 수 없는 명령입니다: $COMMAND"
    echo
    show_help
    exit 1
    ;;
esac
