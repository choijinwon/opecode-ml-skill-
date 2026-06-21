# Offline Weather Agent Sample

폐쇄망에서 실행하는 로컬 챗봇 샘플이다. 외부 API, CDN, 이미지, 폰트 리소스를 사용하지 않는다.

구성:

- Chat UI: FastAPI가 HTML/CSS/JS를 직접 서빙
- LLM: 로컬 Ollama OpenAI-compatible API
- Observability: 로컬 MLflow Tracking/Tracing
- Prompt Registry: `offline-weather-agent-chat`
- Model Registry: `offline-weather-agent-qwen`
- Judge/Scorer: `offline_weather_response_length`

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
LOCAL_QWEN_BASE_URL=http://127.0.0.1:11434/v1
LOCAL_QWEN_API_KEY=ollama
WEATHER_AGENT_MODEL=qwen2.5-coder:14b
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
