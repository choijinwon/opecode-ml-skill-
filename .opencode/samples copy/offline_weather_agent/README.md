# Offline Weather Agent Sample

폐쇄망에서 실행하는 로컬 챗봇 샘플이다. 외부 API, CDN, 이미지, 폰트 리소스를 사용하지 않는다.

구성:

- Chat UI: FastAPI가 HTML/CSS/JS를 직접 서빙
- LLM: 로컬 Ollama OpenAI-compatible API
- Observability: 로컬 MLflow Tracking/Tracing
- RAG: `offline_weather_agent_core/retrieval.py`가 로컬 문서를 검색해 프롬프트에 추가
- LangChain: `offline_weather_agent_core/frameworks/langchain_agent.py`
- LangGraph: `offline_weather_agent_core/frameworks/langgraph_agent.py`
- AI Studio pyfunc: `aiu_custom/`, `run_model.py`
- Prompt Registry: `offline-weather-agent-chat`
- Model Registry: `offline-weather-agent-qwen`
- Judge/Scorer: `offline_weather_response_length`

## Module Layout

유지보수를 쉽게 하기 위해 루트에는 설명/설정/실행 보조 파일만 두고, 실제 실행 파일은 `offline_weather_agent_core/`와 `registry/` 패키지로 나뉘어 있다.
`aiu_custom/`은 AI Studio 스타일 MLflow pyfunc 등록에서 사용하는 필수 custom code package다.

```text
README.md                  # 샘플 설명
.env.example               # 로컬/폐쇄망 환경 변수 예시
requirements.txt           # 샘플 의존성
run_model.py               # AI Studio 스타일 pyfunc 등록 entrypoint
artifacts/                 # 로컬 산출물 보관 폴더(.gitkeep만 Git 추적)
aiu_custom/
└── predict.py              # AI Studio 스타일 MLflow pyfunc ModelWrapper
registry/
├── prompt.py               # Prompt Registry 등록
├── model.py                # 기본 pyfunc Model Registry 등록
└── judge.py                # Judges/Scorers 등록 및 평가
offline_weather_agent_core/
├── config.py               # .env, MLflow, OpenAI-compatible LLM 설정
├── weather.py              # 도시 추출, 로컬 날씨 도구
├── documents.py            # 폐쇄망 RAG용 로컬 문서
├── retrieval.py            # 의존성 없는 keyword retrieval
├── prompts.py              # 기본 프롬프트 템플릿
├── prompting.py            # MLflow Prompt Registry 로딩 및 fallback
├── llm.py                  # OpenAI-compatible Qwen 호출
├── core.py                 # 기본 weather agent
├── web.py                  # FastAPI 챗봇 앱
└── frameworks/
    ├── langchain_agent.py  # LangChain 체인 샘플
    └── langgraph_agent.py  # LangGraph workflow 샘플
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
OPENAI_API_KEY=your-internal-qwen-key
OPENAI_BASE_URL=http://xxx.xxx.xxx.xxx:포트/v1
OPENAI_MODEL=qwen3.6
OPENAI_MODELS=qwen3.6,gpt20,gamma
```

`OPENAI_MODEL`은 실제 호출할 기본 모델이다.
`OPENAI_MODELS`는 AI Studio 화면에서 선택 가능한 모델 목록으로 사용할 수 있다.
`OPENAI_MODEL`이 비어 있으면 `OPENAI_MODELS`의 첫 번째 모델을 fallback으로 사용한다.

## Run Chatbot

```bash
.venv/bin/uvicorn offline_weather_agent_core.web:app \
  --app-dir .opencode/samples/offline_weather_agent \
  --host 127.0.0.1 \
  --port 8010
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
PYTHONPATH=.opencode/samples/offline_weather_agent \
.venv/bin/python -m offline_weather_agent_core.frameworks.langchain_agent "서울 날씨 알려줘"
```

## Local RAG

이 샘플의 RAG는 검색 API와 로컬 fallback을 모두 지원한다.
`RAG_SEARCH_API_URL`이 설정되어 있으면 `offline_weather_agent_core/retrieval.py`가 검색 API를 호출하고,
API가 없거나 실패하면 `offline_weather_agent_core/documents.py`의 로컬 문서를 검색한다.

현재 구조:

```text
사용자 질문
-> get_weather() 로컬 날씨 도구
-> retrieve_context() 로컬 문서 검색
-> call_qwen() 프롬프트에 weather_data + rag_context 전달
-> MLflow trace에 RETRIEVER/LLM/AGENT span 기록
```

검색 API 요청 형식:

```json
{
  "query": "MLflow 세션값은 어디에 남아?",
  "top_k": 2
}
```

검색 API 응답 형식:

```json
{
  "results": [
    {
      "id": "doc-1",
      "title": "MLflow Chat Sessions",
      "text": "MLflow Chat Sessions는 mlflow.trace.session metadata로 대화를 묶는다."
    }
  ]
}
```

환경변수:

```bash
RAG_SEARCH_API_URL=http://127.0.0.1:8020/search
RAG_SEARCH_API_KEY=
RAG_SEARCH_TIMEOUT_SECONDS=5
```

FAISS나 Chroma를 붙일 때는 별도 검색 API를 만들고 `RAG_SEARCH_API_URL`만 연결하면 된다.

LangGraph 샘플:

```bash
MLFLOW_TRACKING_URI=http://127.0.0.1:5001 \
PYTHONPATH=.opencode/samples/offline_weather_agent \
.venv/bin/python -m offline_weather_agent_core.frameworks.langgraph_agent "부산 날씨 알려줘"
```

## AI Studio Style pyfunc

`aiu_custom` 폴더는 AI Studio 스타일 등록에서 필수로 사용하는 custom code package다.
`artifacts/` 폴더는 로컬 산출물이나 반입 파일을 둘 수 있는 자리이며, 실제 파일은 Git에 올리지 않고 `.gitkeep`만 추적한다.
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
PYTHONPATH=.opencode/samples/offline_weather_agent \
.venv/bin/python -m registry.prompt
```

모델 등록:

```bash
PYTHONPATH=.opencode/samples/offline_weather_agent \
.venv/bin/python -m registry.model
```

Judge/Scorer 등록 및 수동 평가:

```bash
PYTHONPATH=.opencode/samples/offline_weather_agent \
.venv/bin/python -m registry.judge
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
