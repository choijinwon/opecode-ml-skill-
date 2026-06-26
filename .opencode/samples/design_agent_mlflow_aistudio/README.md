# Design Agent MLflow AI Studio Sample

이 샘플은 **GenAI + MLflow + AI Studio endpoint**에 연결되는 디자인 에이전트 예제입니다.

목표:

```text
Prompt   -> 디자인 브리프/가이드 프롬프트 관리
Tracking -> MLflow trace/span 기록
Session  -> 사용자별 디자인 작업 session_id 기록
Judge    -> 브랜드 일관성/실행 가능성/금지 표현 평가
Model    -> save_model/에 디자인 에이전트 메타데이터 저장
AI Studio -> endpoint URL / API key / model 값으로 LLM 연결
```

## 필수 폴더

```text
aiu_custom/       AI Studio pyfunc wrapper
design_agent_core/ 디자인 에이전트 핵심 로직
save_model/       로컬 모델 메타데이터 저장
local_serving/    로컬 API 테스트
registry/         prompt / judge 등록 스크립트
artifacts/        실행 결과와 MLflow 기록 요약
config/           AI Studio / MLflow / Agent 설정
```

## 파일 구조

```text
design_agent_mlflow_aistudio/
  aiu_custom/
    predict.py              MLflow pyfunc wrapper
  design_agent_core/
    config.py               env, MLflow tracking, endpoint 설정
    core.py                 디자인 에이전트 실행 흐름과 trace/session 기록
    langchain_agent.py      LangChain 스타일 Prompt + Tool + LLM 조립
    langgraph_agent.py      LangGraph StateGraph 노드 실행 흐름
    llm.py                  AI Studio OpenAI 호환 endpoint 호출
    prompts.py              디자인 프롬프트
    retrieval.py            샘플 디자인 가이드 검색
    source_analyzer.py      소스 분석 기반 디자인 가이드 생성
  registry/
    prompt.py               MLflow Prompt 등록 예시
    judge.py                Judge 기준 실행/기록 예시
  local_serving/
    serving_app.py          FastAPI 로컬 endpoint
  save_model/
    .gitkeep                실행 시 design_agent_model.json 생성
  artifacts/
    .gitkeep                실행 결과 JSON, 로컬 MLflow DB 생성
  프로젝트 진입점              저장/채팅/등록 실행 진입점
```

## Endpoint 설정

```bash
cp config/ai_studio.env.example config/ai_studio.env
```

```env
OPENAI_API_KEY="your-internal-key"
OPENAI_BASE_URL="http://ai-studio-endpoint:port/v1"
OPENAI_MODEL="qwen3.6"
OPENAI_MODELS="qwen3.6,gpt20,gamma"

MLFLOW_TRACKING_URI="http://127.0.0.1:5001"
MLFLOW_EXPERIMENT_NAME="design-agent-ai-studio"
MLFLOW_REGISTER_MODEL_NAME="design-agent-ai-studio"
```

실제 API key, password, token 값은 Git에 올리지 않습니다.

## 실행 순서

```bash
OpenCode 빌드모드에서 해당 기능을 선택해 실행
OpenCode 빌드모드에서 해당 기능을 선택해 실행
OpenCode 빌드모드에서 해당 기능을 선택해 실행
OpenCode 빌드모드에서 해당 기능을 선택해 실행
OpenCode 빌드모드에서 해당 기능을 선택해 실행
python registry/prompt.py
python registry/judge.py
OpenCode 빌드모드에서 해당 기능을 선택해 실행
```

각 명령의 의미:

- `--save`: `save_model/design_agent_model.json` 생성
- `--chat`: 기본 core 에이전트 실행 및 MLflow Trace/Session 기록
- `--langchain`: Prompt + Tool + LLM 조립 관점 실행
- `--langgraph`: classify -> retrieve -> prompt -> llm 노드 흐름 실행
- `--analyze-source`: 사용자가 지정한 프로젝트 소스를 분석해 디자인 토큰/컴포넌트/가이드 초안 생성
- `registry/prompt.py`: Prompt Registry 등록
- `registry/judge.py`: 마지막 답변 기준 Judge 결과 생성
- `--register`: MLflow pyfunc 모델 등록

## MLflow Trace 구조

```text
Trace
  design_agent
    classify_design_task       TOOL
    retrieve_design_guidelines RETRIEVER
    call_ai_studio_llm         LLM

  langgraph_design_agent
    langgraph_node_classify    TOOL
    langgraph_node_retrieve    RETRIEVER
    langgraph_node_prompt      TOOL
    langgraph_node_llm         LLM

  analyze_source_project
    collect_source_files       TOOL
    detect_frontend_framework  TOOL
    extract_design_tokens      TOOL
    build_component_catalog    TOOL
    write_design_guide         TOOL

Metadata
  mlflow.trace.user
  mlflow.trace.session
  app
  domain
  ai_studio_model
```

## AI Studio 화면 연결 아이디어

```text
Prompt
  - 디자인 브리프 생성 프롬프트
  - 디자인 리뷰 프롬프트
  - 카피/톤앤매너 프롬프트

Tracking
  - 요청별 trace
  - LLM 호출/가이드 검색/context span 확인

Session
  - 프로젝트별 디자인 대화 흐름
  - session_id 기준 브리프 변경 이력 확인

Judge
  - 브랜드 일관성
  - 실행 가능성
  - 금지 표현/과장 표현 여부
  - UI 접근성 언급 여부

Dataset
  - 디자인 요청
  - 기대 브리프
  - 금지 산출물
  - 회귀 테스트 질의 세트
```

## 소스 분석 기반 디자인 가이드

frontend/source 프로젝트 경로를 지정하면 정적 분석으로 디자인 가이드 초안을 생성합니다.

```bash
OpenCode 빌드모드에서 해당 기능을 선택해 실행
```

생성 파일:

```text
artifacts/design_source_analysis.json
artifacts/design_component_catalog.json
artifacts/design_guide.md
```

분석 대상:

```text
framework 후보
컴포넌트 파일
색상
CSS 변수
font-size
border-radius
spacing
className/class 사용 패턴
button/form/table/modal 사용 여부
```

제외 폴더:

```text
node_modules
.git
dist
build
.next
coverage
__pycache__
```

## 운영 적용 포인트

- `retrieval.py`는 샘플 디자인 가이드입니다. 운영에서는 디자인 시스템 문서 API, 브랜드 가이드 API, Figma/Drive 검색 API로 교체합니다.
- `llm.py`는 `OPENAI_BASE_URL/chat/completions`를 호출합니다.
- `aiu_custom/predict.py` 입력 컬럼은 `request`, `user_id`, `session_id`입니다.
- 디자인 도메인은 결과물이 주관적이므로 Judge 기준을 명확히 정의해야 합니다.
