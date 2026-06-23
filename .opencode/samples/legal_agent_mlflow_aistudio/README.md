# Legal Agent MLflow AI Studio Sample

이 샘플은 **GenAI + MLflow + AI Studio endpoint** 연결 구조를 쉽게 확인하기 위한 법률 에이전트 예제입니다.

목표는 아래 기능을 한 폴더에서 이해하고 실행하는 것입니다.

```text
Prompt   -> 법률 상담 스타일 프롬프트 관리
Tracking -> MLflow trace/span 기록
Session  -> 사용자별 대화 session_id 기록
Judge    -> 답변 길이/면책 문구 등 품질 평가 기준
Model    -> save_model/에 로컬 모델 정보 저장
AI Studio -> endpoint URL / API key / model 값으로 LLM 연결
```

주의: 이 샘플은 법률 정보 안내용 구조 예제입니다. 실제 법률 자문, 소송 전략, 계약 판단을 대체하지 않습니다.

## 필수 폴더

```text
aiu_custom/      AI Studio pyfunc wrapper
legal_agent_core/ 에이전트 핵심 로직
save_model/      로컬 모델 또는 모델 메타데이터 저장
local_serving/   로컬 API 테스트
registry/        prompt / judge 등록 스크립트
artifacts/       실행 결과와 MLflow 기록 요약
config/          AI Studio / MLflow / Agent 설정
```

## 파일 구조

```text
legal_agent_mlflow_aistudio/
  aiu_custom/
    predict.py              MLflow pyfunc wrapper. AI Studio 모델 등록 시 진입점
  legal_agent_core/
    config.py               env, MLflow tracking, endpoint 설정
    core.py                 법률 에이전트 실행 흐름과 trace/session 기록
    langchain_agent.py      LangChain 스타일 Prompt + Tool + LLM 조립
    langgraph_agent.py      LangGraph StateGraph 노드 실행 흐름
    llm.py                  AI Studio OpenAI 호환 endpoint 호출
    prompts.py              Prompt 템플릿과 면책 문구
    retrieval.py            샘플 법률 문서 검색. 운영 시 RAG/API로 교체
  registry/
    prompt.py               MLflow Prompt 등록 예시
    judge.py                Judge 기준 실행/기록 예시
  local_serving/
    serving_app.py          FastAPI 로컬 endpoint
  save_model/
    .gitkeep                실행 시 legal_agent_model.json 생성
  artifacts/
    .gitkeep                실행 결과 JSON, 로컬 MLflow DB 생성
  run_model.py              저장/채팅/등록 실행 진입점
```

## AI Studio endpoint 설정

`config/ai_studio.env.example`을 복사해 실제 값만 채웁니다.

```bash
cp config/ai_studio.env.example config/ai_studio.env
```

```env
OPENAI_API_KEY="your-internal-key"
OPENAI_BASE_URL="http://ai-studio-endpoint:port/v1"
OPENAI_MODEL="qwen3.6"
OPENAI_MODELS="qwen3.6,gpt20,gamma"

MLFLOW_TRACKING_URI="http://127.0.0.1:5001"
MLFLOW_EXPERIMENT_NAME="legal-agent-ai-studio"
MLFLOW_REGISTER_MODEL_NAME="legal-agent-ai-studio"

LAW_API_OC="your-law-api-oc"
LAW_API_BASE_URL="http://www.law.go.kr/DRF/lawSearch.do"
LAW_API_TARGET="eflaw"
```

실제 API key, password, token 값은 Git에 올리지 않습니다.

## 실행 순서

샘플 폴더에서 실행합니다.

```bash
python run_model.py --save
python run_model.py --chat "임대차 계약 해지 통보는 어떻게 정리해야 하나요?"
python run_model.py --langchain "임대차 계약 해지 통보는 어떻게 정리해야 하나요?"
python run_model.py --langgraph "임대차 계약 해지 통보는 어떻게 정리해야 하나요?"
python registry/prompt.py
python registry/judge.py
```

각 명령의 의미:

- `python run_model.py --save`: `save_model/legal_agent_model.json`을 생성합니다. AI Studio에 올릴 모델 메타데이터와 prompt/model 정보를 확인하는 단계입니다.
- `python run_model.py --chat "...질문..."`: 법률 에이전트를 실행하고 MLflow Trace, Session metadata를 남깁니다.
- `python run_model.py --langchain "...질문..."`: LangChain 스타일로 Prompt, Tool, LLM을 조립해 실행합니다.
- `python run_model.py --langgraph "...질문..."`: LangGraph StateGraph 스타일로 classify, retrieve, prompt, llm 노드를 실행합니다.
- `python registry/prompt.py`: MLflow GenAI Prompt Registry가 지원되는 환경에서 Prompt를 등록합니다.
- `python registry/judge.py`: 마지막 답변을 기준으로 면책 문구, 응답 길이, 체크리스트 포함 여부를 평가해 `artifacts/legal_judge_result.json`에 남깁니다.
- `python run_model.py --register`: MLflow pyfunc 모델로 등록합니다. MLflow tracking server와 registry가 준비된 환경에서 사용합니다.

로컬 API:

```bash
uvicorn local_serving.serving_app:app --host 127.0.0.1 --port 8090
```

요청 예시:

```bash
curl -X POST http://127.0.0.1:8090/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"계약서 검토 전에 확인할 항목 알려줘","user_id":"demo-user","session_id":"legal-session-001"}'
```

## MLflow에 남는 구조

```text
Trace
  legal_agent
    classify_legal_topic     TOOL
    retrieve_legal_context   RETRIEVER
    call_ai_studio_llm       LLM

  langchain_legal_agent
    classify_legal_topic     TOOL
    retrieve_legal_context   RETRIEVER
    call_ai_studio_llm       LLM

  langgraph_legal_agent
    langgraph_node_classify   TOOL
    langgraph_node_retrieve   RETRIEVER
    langgraph_node_prompt     TOOL
    langgraph_node_llm        LLM

Metadata
  mlflow.trace.user
  mlflow.trace.session
  app
  domain
  ai_studio_model
```

Session은 별도 테이블을 직접 만들지 않아도 `mlflow.trace.session` 값으로 묶입니다. AI Studio에서 Chat Session 화면을 만들 때는 이 값을 기준으로 대화 묶음을 조회하면 됩니다.

## Core / LangChain / LangGraph 차이

```text
core.py
  - 가장 단순한 기본 실행 흐름
  - dependency 최소
  - 디버깅과 smoke test에 적합

langchain_agent.py
  - Prompt + Tool + LLM 조립 관점을 보여줌
  - Agent Builder 화면 설계와 매핑하기 쉬움

langgraph_agent.py
  - classify -> retrieve -> prompt -> llm 노드 흐름을 명시
  - Agent Viewer, Trace Viewer, 단계별 실패 분석에 적합
```

## AI Studio 화면 연결 아이디어

```text
Prompt
  - 법률 에이전트 기본 프롬프트
  - 버전/alias 관리

Tracking
  - 질문별 trace
  - LLM 호출/검색/context span 확인

Session
  - 사용자별 상담 흐름 확인
  - session_id 기준 대화 묶음

Judge
  - 면책 문구 포함 여부
  - 응답 길이
  - 출처/근거 안내 여부

Dataset
  - 자주 묻는 법률 질문
  - 기대 답변/금지 답변
  - 회귀 테스트용 질의 세트
```

## 운영 적용 포인트

- `legal_agent_core/retrieval.py`는 샘플 검색입니다. 실제 적용 시 사내 법률 문서 검색 API, RAG API, vector DB endpoint로 교체합니다.
- `LAW_API_OC`가 있으면 `http://www.law.go.kr/DRF/lawSearch.do` 목록조회 API를 먼저 조회합니다. 인증값이 없거나 실패하면 로컬 샘플 법률 가이드로 fallback합니다.
- `legal_agent_core/llm.py`는 `OPENAI_BASE_URL/chat/completions`를 호출합니다. AI Studio endpoint가 OpenAI 호환이면 그대로 연결됩니다.
- API key, token, password는 `config/ai_studio.env` 또는 서버 Secret으로 주입합니다. 코드와 Git에는 실제 값을 넣지 않습니다.
- `aiu_custom/predict.py`는 AI Studio/MLflow pyfunc 등록용 wrapper입니다. 입력 컬럼은 `question`, `user_id`, `session_id`입니다.
- 법률 도메인은 오답 리스크가 크므로 Judge는 최소한 면책 문구, 근거/출처, 금지 표현, 응답 일관성 기준을 포함해야 합니다.

## 국가법령정보 공동활용 조회 흐름

국가법령정보 공동활용 OPEN API는 크게 두 단계로 사용합니다.

```text
1. 목록조회 API
   - 법령명으로 검색
   - 법령일련번호, 기본정보, 법령상세링크를 받음

2. 본문조회 API
   - 목록조회 결과의 법령일련번호 또는 법령상세링크로 본문 조회
   - 기본정보, 소관부처, 조문, 부칙, 별표, 별표 파일 링크 확인
```

이 샘플은 에이전트의 RAG 검색 단계에서 먼저 목록조회 API를 호출합니다. 목록조회 결과의 `법령상세링크`는 본문조회로 이어지는 링크로 보관합니다.

## 목록조회 요청 변수

기본 endpoint:

```text
http://www.law.go.kr/DRF/lawSearch.do
```

샘플에서 사용하는 기본 요청 변수:

```text
OC       OpenAPI 사용자 인증값
target   목록조회 대상. 활용가이드 예시는 현행법령 기준 eflaw
type     XML 또는 JSON
query    검색어
display  조회 건수
page     페이지 번호
```

예시:

```text
https://www.law.go.kr/DRF/lawSearch.do?OC=test&target=eflaw&query=자동차관리법
```

샘플 호출 예시:

```text
http://www.law.go.kr/DRF/lawSearch.do?OC=인증값&target=eflaw&type=XML&query=개인정보&display=5&page=1
```

## 본문조회와 별표 파일

목록조회 결과에는 `법령상세링크`가 포함됩니다. 이 링크를 사용하면 본문조회 결과에서 조문, 부칙, 별표 정보를 확인할 수 있습니다.

본문조회 결과의 별표 파일은 아래 값 뒤에 `https://www.law.go.kr`를 붙여 다운로드합니다.

```text
별표서식파일링크
별표서식PDF파일링크
```

예시:

```text
https://www.law.go.kr/LSW/flDownload.do?flSeq=162492787
```

구현 위치:

```text
legal_agent_core/law_api.py
legal_agent_core/retrieval.py
```
