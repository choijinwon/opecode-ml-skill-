# Offline Weather Agent Sample for MLflow 3.13.0

폐쇄망에서 `MLflow 3.13.0`으로 실행하는 로컬 챗봇 샘플이다. 외부 API, CDN, 이미지, 폰트 리소스를 사용하지 않는다.

구성:

- Chat UI: FastAPI가 HTML/CSS/JS를 직접 서빙
- LLM: 로컬 Ollama OpenAI-compatible API
- Observability: 로컬 MLflow Tracking/Tracing
- LangChain: `langchain_agent.py`
- LangGraph: `langgraph_agent.py`
- AI Studio pyfunc: `aiu_custom/`, `run_model.py`
- Prompt Registry: `offline-weather-agent-313-chat`
- Model Registry: `offline-weather-agent-313-qwen`
- Judge/Scorer: 가능하면 `offline_weather_313_response_length` 등록

## Module Layout

유지보수를 쉽게 하기 위해 실제 로직은 `offline_weather_agent_313/` 패키지로 나뉘어 있다.
루트의 `app.py`, `agent.py`, `langchain_agent.py`, `langgraph_agent.py`는 기존 실행 명령을 유지하기 위한 얇은 entrypoint/wrapper다.
`aiu_custom/`은 AI Studio 스타일 MLflow pyfunc 등록에서 사용하는 필수 custom code package다.

```text
aiu_custom/
└── predict.py                # AI Studio 스타일 MLflow pyfunc ModelWrapper
run_model.py                  # AI Studio 스타일 pyfunc 등록 entrypoint
offline_weather_agent_313/
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

## Create Environment

Python 3.12 예시:

```bash
python3.12 -m venv .venv-mlflow313
.venv-mlflow313/bin/pip install -r .opencode/samples/offline_weather_agent_mlflow313/requirements.txt
```

폐쇄망에서는 위 패키지 wheel을 사내 PyPI나 wheelhouse에 먼저 반입해야 한다.

## Start Local Services

Ollama:

```bash
ollama serve
ollama list
```

MLflow 3.13.0 UI:

```bash
.venv-mlflow313/bin/mlflow ui \
  --backend-store-uri sqlite:///mlflow313.db \
  --default-artifact-root ./mlartifacts313 \
  --host 127.0.0.1 \
  --port 5013
```

기존 `mlflow.db`가 MLflow 3.14 이상에서 생성된 경우 3.13 서버가 열지 못할 수 있으므로,
3.13 샘플은 `mlflow313.db`를 별도로 사용한다.

## Configure

필요하면 샘플 env를 복사한다.

```bash
cp .opencode/samples/offline_weather_agent_mlflow313/.env.example .env
```

기본값:

```bash
MLFLOW_TRACKING_URI=http://127.0.0.1:5013
MLFLOW_EXPERIMENT_NAME=offline-weather-agent-313
LLM_PROVIDER=ollama
LOCAL_QWEN_BASE_URL=http://127.0.0.1:11434/v1
LOCAL_QWEN_API_KEY=ollama
WEATHER_AGENT_MODEL=qwen2.5-coder:14b
```

OpenAI 호환 endpoint로 Qwen을 사용할 수도 있다. 이 경우 `LLM_PROVIDER=openai`로 두고
`OPENAI_BASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL`을 설정한다.

```bash
LLM_PROVIDER=openai
OPENAI_BASE_URL=http://127.0.0.1:11434/v1
OPENAI_API_KEY=ollama
OPENAI_MODEL=qwen2.5-coder:14b
```

실제 OpenAI API를 쓰려면:

```bash
LLM_PROVIDER=openai
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

폐쇄망에서 Qwen을 쓸 경우에는 `OPENAI_BASE_URL`에 사내 OpenAI-compatible gateway 주소를 넣고,
`OPENAI_MODEL`에 gateway가 노출하는 Qwen 모델명을 넣는다.

로컬 Qwen을 MLflow judge 모델로 사용할 때 3.13의 OpenAI provider가 API key 환경변수를 요구한다.
샘플 스크립트는 `OPENAI_API_KEY`가 없으면 현재 provider의 API key 값으로 자동 설정한다.
또한 3.13 judge의 `base_url`은 chat completions endpoint로 맞춰야 해서,
스크립트가 base URL 뒤에 `/chat/completions`를 자동으로 붙인다.

## Run Chatbot

```bash
.venv-mlflow313/bin/uvicorn app:app --app-dir .opencode/samples/offline_weather_agent_mlflow313 --host 127.0.0.1 --port 8013
```

브라우저:

```text
http://127.0.0.1:8013
```

API 테스트:

```bash
curl -s -X POST http://127.0.0.1:8013/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"서울 날씨 알려줘","session_id":"offline-313-test","user_id":"offline-user"}'
```

## Run LangChain/LangGraph Samples

LangChain 샘플:

```bash
MLFLOW_TRACKING_URI=http://127.0.0.1:5013 \
.venv-mlflow313/bin/python .opencode/samples/offline_weather_agent_mlflow313/langchain_agent.py "서울 날씨 알려줘"
```

LangGraph 샘플:

```bash
MLFLOW_TRACKING_URI=http://127.0.0.1:5013 \
.venv-mlflow313/bin/python .opencode/samples/offline_weather_agent_mlflow313/langgraph_agent.py "부산 날씨 알려줘"
```

두 샘플 모두 `mlflow.langchain.autolog()`를 사용한다. LangGraph도 LangChain runnable/callback
기반으로 동작하므로 같은 autolog 설정으로 trace를 남긴다. 추가로 각 스크립트의 최상위 함수에
`@mlflow.trace(..., span_type=SpanType.AGENT)`를 붙여 chat session metadata도 남긴다.

## AI Studio Style pyfunc

`aiu_custom` 폴더는 AI Studio 스타일 등록에서 필수로 사용하는 custom code package다.
`run_model.py`는 `mlflow.pyfunc.log_model()` 호출 시 다음 값을 사용한다.

```python
code_paths=["aiu_custom", "offline_weather_agent_313"]
python_model=ModelWrapper()
artifacts={"config": "generated/config/config.json"}
```

사전 준비 검증:

```bash
.venv-mlflow313/bin/python .opencode/samples/offline_weather_agent_mlflow313/run_model.py --prepare-only
```

MLflow 등록:

```bash
MLFLOW_TRACKING_URI=http://127.0.0.1:5013 \
.venv-mlflow313/bin/python .opencode/samples/offline_weather_agent_mlflow313/run_model.py --register
```

## MLflow Setup

프롬프트 등록:

```bash
.venv-mlflow313/bin/python .opencode/samples/offline_weather_agent_mlflow313/register_prompt.py
```

모델 등록:

```bash
.venv-mlflow313/bin/python .opencode/samples/offline_weather_agent_mlflow313/register_model.py
```

Judge/Scorer 등록 및 수동 평가:

```bash
.venv-mlflow313/bin/python .opencode/samples/offline_weather_agent_mlflow313/register_judge.py
```

## MLflow Screens

생성된 experiment ID는 환경마다 다를 수 있다.

- Traces: `http://127.0.0.1:5013/#/experiments/<ID>/traces`
- Chat sessions: `http://127.0.0.1:5013/#/experiments/<ID>/chat-sessions`
- Prompts: `http://127.0.0.1:5013/#/experiments/<ID>/prompts`
- Judges: `http://127.0.0.1:5013/#/experiments/<ID>/judges`
- Models: MLflow UI 왼쪽의 Models 또는 Registered Models

## Compatibility Notes

- 샘플의 핵심 경로는 `mlflow.trace`, `mlflow.set_experiment`, `mlflow.pyfunc.log_model`을 사용한다.
- Prompt/Judge API는 MLflow 설치 상태에 따라 없을 수 있으므로, 없으면 스크립트가 안내 메시지를 출력하고 종료한다.
- 로컬 OSS MLflow에서는 일부 자동 judge 실행이 제한될 수 있다. 이 경우 수동 evaluation run 방식으로 사용한다.
