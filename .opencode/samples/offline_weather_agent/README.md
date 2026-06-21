# Offline Weather Agent Sample

폐쇄망에서 실행하는 로컬 챗봇 샘플이다. 외부 API, CDN, 이미지, 폰트 리소스를 사용하지 않는다.

구성:

- Chat UI: FastAPI가 HTML/CSS/JS를 직접 서빙
- LLM: 로컬 Ollama OpenAI-compatible API
- Observability: 로컬 MLflow Tracking/Tracing
- LangChain: `langchain_agent.py`
- LangGraph: `langgraph_agent.py`
- AI Studio pyfunc: `aiu_custom/`, `run_model.py`
- Prompt Registry: `offline-weather-agent-chat`
- Model Registry: `offline-weather-agent-qwen`
- Judge/Scorer: `offline_weather_response_length`

## Module Layout

유지보수를 쉽게 하기 위해 실행 파일은 `entrypoints/`, 실제 로직은 `offline_weather_agent_core/`, MLflow 등록 로직은 `registry/` 패키지로 나뉘어 있다.
루트의 `app.py`, `agent.py`, `langchain_agent.py`, `langgraph_agent.py`, `register_*.py`는 기존 실행 명령을 유지하기 위한 얇은 호환 wrapper다.
`aiu_custom/`은 AI Studio 스타일 MLflow pyfunc 등록에서 사용하는 필수 custom code package다.

```text
agent.py                    # 기존 import 호환 wrapper -> entrypoints/agent.py
app.py                      # 기존 uvicorn app:app 호환 wrapper -> entrypoints/app.py
prompts.py                  # 기존 prompt import 호환 wrapper -> entrypoints/prompts.py
langchain_agent.py          # 기존 실행 호환 wrapper -> entrypoints/langchain_agent.py
langgraph_agent.py          # 기존 실행 호환 wrapper -> entrypoints/langgraph_agent.py
register_prompt.py          # 기존 실행 호환 wrapper -> entrypoints/register_prompt.py
register_model.py           # 기존 실행 호환 wrapper -> entrypoints/register_model.py
register_judge.py           # 기존 실행 호환 wrapper -> entrypoints/register_judge.py
run_model.py                # AI Studio 스타일 pyfunc 등록 entrypoint
entrypoints/
├── agent.py                # agent 공개 API 관리
├── app.py                  # FastAPI app 객체 생성
├── prompts.py              # prompt 공개 API 관리
├── langchain_agent.py      # LangChain 실행 entrypoint
├── langgraph_agent.py      # LangGraph 실행 entrypoint
├── register_prompt.py      # Prompt Registry 실행 entrypoint
├── register_model.py       # 기본 Model Registry 실행 entrypoint
└── register_judge.py       # Judge/Scorer 실행 entrypoint
aiu_custom/
└── predict.py                # AI Studio 스타일 MLflow pyfunc ModelWrapper
registry/
├── prompt.py                 # Prompt Registry 등록
├── model.py                  # 기본 pyfunc Model Registry 등록
└── judge.py                  # Judges/Scorers 등록 및 평가
offline_weather_agent_core/
├── config.py                 # .env, MLflow, OpenAI-compatible LLM 설정
├── weather.py                # 도시 추출, 로컬 날씨 도구
├── prompts.py                # 기본 프롬프트 템플릿
├── prompting.py              # MLflow Prompt Registry 로딩 및 fallback
├── llm.py                    # OpenAI-compatible Qwen 호출
├── core.py                   # 기본 weather agent
├── web.py                    # FastAPI 챗봇 앱
└── frameworks/
    ├── langchain_agent.py    # LangChain 체인 샘플
    └── langgraph_agent.py    # LangGraph workflow 샘플
```

## Prerequisites

로컬에서 다음 두 서버가 떠 있어야 한다.

```bash
ollama serve
.venv/bin/mlflow ui --host 127.0.0.1 --port 5001
```

설치된 Qwen 모델 확인:

```bash
ollama list
```

이 샘플의 기본 모델은 `qwen2.5-coder:14b`이다.

## Configure

필요하면 샘플 env를 복사해서 수정한다.

```bash
cp .opencode/samples/offline_weather_agent/.env.example .env
```

주요 값:

```bash
MLFLOW_TRACKING_URI=http://127.0.0.1:5001
MLFLOW_EXPERIMENT_NAME=offline-weather-agent
LLM_PROVIDER=ollama
LOCAL_QWEN_BASE_URL=http://127.0.0.1:11434/v1
LOCAL_QWEN_API_KEY=ollama
WEATHER_AGENT_MODEL=qwen2.5-coder:14b
```

OpenAI 호환 endpoint로 Qwen을 사용할 수도 있다.

```bash
LLM_PROVIDER=openai
OPENAI_BASE_URL=http://127.0.0.1:11434/v1
OPENAI_API_KEY=ollama
OPENAI_MODEL=qwen2.5-coder:14b
```

## Run Chatbot

```bash
.venv/bin/uvicorn app:app --app-dir .opencode/samples/offline_weather_agent --host 127.0.0.1 --port 8010
```

브라우저:

```text
http://127.0.0.1:8010
```

API 테스트:

```bash
curl -s -X POST http://127.0.0.1:8010/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"서울 날씨 알려줘","session_id":"offline-test","user_id":"offline-user"}'
```

## Run LangChain/LangGraph Samples

LangChain 샘플:

```bash
MLFLOW_TRACKING_URI=http://127.0.0.1:5001 \
.venv/bin/python .opencode/samples/offline_weather_agent/langchain_agent.py "서울 날씨 알려줘"
```

LangGraph 샘플:

```bash
MLFLOW_TRACKING_URI=http://127.0.0.1:5001 \
.venv/bin/python .opencode/samples/offline_weather_agent/langgraph_agent.py "부산 날씨 알려줘"
```

## AI Studio Style pyfunc

`aiu_custom` 폴더는 AI Studio 스타일 등록에서 필수로 사용하는 custom code package다.
`run_model.py`는 `mlflow.pyfunc.log_model()` 호출 시 다음 값을 사용한다.

```python
code_paths=["aiu_custom", "offline_weather_agent_core"]
python_model=ModelWrapper()
artifacts={"config": "generated/config/config.json"}
```

사전 준비 검증:

```bash
.venv/bin/python .opencode/samples/offline_weather_agent/run_model.py --prepare-only
```

MLflow 등록:

```bash
MLFLOW_TRACKING_URI=http://127.0.0.1:5001 \
.venv/bin/python .opencode/samples/offline_weather_agent/run_model.py --register
```

## MLflow Setup

프롬프트 등록:

```bash
.venv/bin/python .opencode/samples/offline_weather_agent/register_prompt.py
```

모델 등록:

```bash
.venv/bin/python .opencode/samples/offline_weather_agent/register_model.py
```

Judge/Scorer 등록 및 수동 평가:

```bash
.venv/bin/python .opencode/samples/offline_weather_agent/register_judge.py
```

## MLflow Screens

기본 experiment는 `offline-weather-agent`이다. 생성된 experiment ID는 환경마다 다를 수 있다.

- Traces: `http://127.0.0.1:5001/#/experiments/<ID>/traces`
- Chat sessions: `http://127.0.0.1:5001/#/experiments/<ID>/chat-sessions`
- Prompts: `http://127.0.0.1:5001/#/experiments/<ID>/prompts`
- Judges: `http://127.0.0.1:5001/#/experiments/<ID>/judges`
- Models: MLflow UI 왼쪽의 Models 또는 Registered Models

## Closed Network Notes

- 인터넷 날씨 API를 호출하지 않는다.
- Qwen 호출은 `LOCAL_QWEN_BASE_URL`만 사용한다.
- UI는 외부 CDN 없이 단일 HTML 문자열로 동작한다.
- Python 패키지는 폐쇄망 반입 전에 wheelhouse 또는 사내 PyPI에 준비해야 한다.
