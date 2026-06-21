# MLflow 메뉴 상세 가이드

이 문서는 `offline_weather_agent_mlflow313` 샘플과 OpenCode 기반 MLflow 테스트 흐름을 기준으로,
MLflow 좌측 메뉴가 각각 어떤 의미를 가지는지 설명한다.

특히 아래처럼 헷갈리기 쉬운 구분을 명확히 하는 것이 목적이다.

```text
Training runs = 모델 학습/등록 같은 작업 실행 이력
Traces        = 질문 1건의 내부 실행 흐름
Sessions      = 여러 trace를 대화 세션으로 묶은 화면
Judges        = 응답 평가 규칙과 결과
Prompts       = 등록된 프롬프트 자산
```

## 메뉴 한눈에 보기

| 메뉴 | 한 줄 설명 | 주 사용자 |
| --- | --- | --- |
| `Overview` | experiment 전체 상태 요약 | 운영자, 개발자 |
| `Training runs` | 학습/등록/배치 실행 기록 | 모델 개발자 |
| `Traces` | 요청 1건의 내부 실행 상세 | 에이전트 개발자 |
| `Sessions` | 대화 세션 단위 묶음 | 챗봇 운영자 |
| `Judges` | 자동 평가 규칙과 결과 | 평가 담당자 |
| `Review` | 사람이 응답을 직접 검토 | 품질 검수자 |
| `Datasets` | 평가용 질문/정답 세트 | 평가 담당자 |
| `Evaluation runs` | 평가 실행 이력 | 평가 담당자, 운영자 |
| `Playground` | 프롬프트/모델 즉석 테스트 | 프롬프트 개발자 |
| `Prompts` | Prompt Registry 자산 관리 | 프롬프트 개발자 |
| `Agent versions` | 에이전트 버전 관리 | 운영자, 개발자 |

## 1. Overview

### 목적

Experiment 전체의 최근 활동을 한 번에 훑는 요약 화면이다.

### 여기서 보는 것

- 최근 실행 활동이 있는지
- runs, traces, prompts, judges가 비어 있지 않은지
- 최근 오류나 평가 결과가 있는지

### 샘플에서 확인하는 것

`offline_weather_agent_local` experiment가 실제로 사용되고 있는지 먼저 확인한다.

### 언제 쓰는가

- 처음 experiment에 들어왔을 때
- 전체 흐름이 살아 있는지 빠르게 보고 싶을 때

## 2. Training runs

### 목적

전통적인 MLflow run 기록을 보는 화면이다.  
모델 학습, metric 기록, artifact 저장, 모델 등록 같은 “작업 실행 이력”이 여기에 남는다.

### 여기서 보는 것

- run name
- 시작 시간 / 종료 시간
- parameters
- metrics
- artifacts
- model logging 이력

### 샘플에서 확인하는 것

주로 아래 작업 결과가 여기 남는다.

- `run_model.py --register`
- `registry/judge.py` 실행 시 생성되는 평가 run
- 일부 prompt/judge 관련 실행 기록

샘플에서 특히 확인하는 항목:

- `rmse`
- `mae`
- `r2`
- registered model과 연결된 run
- artifact 저장 여부

### 쉽게 이해하면

```text
Training runs = 모델 작업 실행 이력 표
```

### 이 메뉴가 중요한 이유

모델이 실제로 학습되었는지, 등록됐는지, 어떤 파라미터와 metric으로 남았는지를 가장 먼저 확인할 수 있다.

## 3. Traces

### 목적

질문 1건이 내부에서 어떤 단계로 처리되었는지 보는 화면이다.

### 여기서 보는 것

- trace input / output
- span graph
- tags / metadata
- latency
- 오류 정보
- linked prompts
- tool, retriever, llm 단계

### 샘플에서 확인하는 것

웹에서 `서울 날씨 알려줘` 같은 질문을 보내면 trace 1건이 생성된다.

core 경로에서는 보통 아래 단계가 graph에 보인다.

```text
offline_weather_web_chat
└── offline_weather_core_agent
    ├── get_weather
    ├── retrieve_local_context
    └── call_qwen
```

### 샘플에서 특히 보는 포인트

- trace가 `experiment 4`에 붙는지
- `framework=core/langchain/langgraph`가 metadata에 남는지
- `Click a graph node to navigate spans`가 의미 있게 보일 정도로 span이 분리됐는지
- `Linked prompts`가 함께 붙는지

### 쉽게 이해하면

```text
Traces = 질문 1건의 내부 처리 디버깅 화면
```

## 4. Sessions

### 목적

여러 trace를 같은 대화 세션으로 묶어 보는 화면이다.

### 여기서 보는 것

- 같은 `session_id`를 가진 여러 요청
- 사용자별 대화 흐름
- 한 대화 안에서 turn이 어떻게 이어졌는지

### 샘플에서 확인하는 것

웹 API에서 `session_id`를 유지한 채 여러 번 질문하면, 이 메뉴에서 하나의 대화처럼 묶여 보여야 한다.

예:

```text
1. 서울 날씨 알려줘
2. 부산은?
3. 그럼 제주는?
```

### 쉽게 이해하면

```text
Sessions = 챗봇 대화방 단위 기록
```

### 이 메뉴가 중요한 이유

trace는 1건 단위라 흐름이 끊겨 보일 수 있다.  
챗봇 운영 관점에서는 session 화면이 실제 사용자 경험에 더 가깝다.

## 5. Judges

### 목적

응답 품질을 자동으로 평가하는 규칙과 결과를 보는 메뉴다.

### 여기서 보는 것

- judge 이름
- scorer 종류
- 평가 결과
- 평가 상태
- 실패/오류 정보

### 샘플에서 확인하는 것

- `offline_weather_guidelines_judge`
- `offline_weather_length_score`

예를 들어 아래 기준을 평가할 수 있다.

- 질문한 도시와 관련된 응답인가
- 한국어로 짧고 명확하게 답했는가
- 위험한 조작 지시나 허위 시스템 상태가 없는가

### 주의할 점

trace가 있다고 judge 결과가 자동으로 항상 생기지는 않는다.

구분:

```text
trace 생성 != judge 평가 저장
```

그래서 UI에 `null`이 보이면 보통 아래 둘 중 하나다.

- 평가가 아직 안 붙음
- 평가가 실패했음

### 쉽게 이해하면

```text
Judges = 응답 자동 채점 규칙
```

## 6. Review

### 목적

자동 평가 외에 사람이 직접 결과를 검토하는 메뉴다.

### 여기서 보는 것

- 응답 내용
- 비교 대상
- 수동 검토 포인트

### 샘플에서 확인하는 것

이 샘플에서는 필수 메뉴는 아니지만, 아래 같은 점검에 유용하다.

- 응답이 실제로 자연스러운지
- judge 결과와 사람이 느끼는 품질이 맞는지
- 잘못된 답변 사례를 골라서 다시 개선할지

### 쉽게 이해하면

```text
Review = 사람이 직접 보는 품질 검토 화면
```

## 7. Datasets

### 목적

평가용 질문/정답/라벨 세트를 관리하는 메뉴다.

### 여기서 보는 것

- input question
- expected answer
- labels / tags
- 평가용 샘플 묶음

### 샘플에서 확인하는 것

지금 샘플은 dataset 중심보다는 trace/demo 중심이지만, 나중에 아래 같은 QA 세트를 만들면 이 메뉴가 중요해진다.

예:

```text
질문: 서울 날씨 알려줘
기대: 서울 관련 응답이어야 함

질문: 부산 날씨 알려줘
기대: 부산 관련 응답이어야 함
```

### 쉽게 이해하면

```text
Datasets = 평가 문제집 저장소
```

## 8. Evaluation runs

### 목적

judge나 dataset을 실제로 실행한 평가 이력을 보는 메뉴다.

### 여기서 보는 것

- 어떤 dataset으로 평가했는지
- 어떤 judge를 사용했는지
- 평가 실행 시간
- 평가 결과 요약

### 샘플에서 확인하는 것

- judge 평가 실행 기록
- trace 기반 평가 기록
- dataset 기반 평가 기록

### 쉽게 이해하면

```text
Evaluation runs = 평가를 실제로 돌린 작업 기록
```

## 9. Playground

### 목적

프롬프트나 모델 응답을 UI에서 즉석으로 시험하는 메뉴다.

### 여기서 보는 것

- 테스트 입력
- 테스트 응답
- prompt/model 조합 실험

### 샘플에서 확인하는 것

- prompt registry에 등록된 프롬프트가 어떤 응답을 내는지
- 모델 호출이 되는지
- trace 전에 간단히 실험해볼 수 있는지

### 쉽게 이해하면

```text
Playground = 즉석 실험 창
```

## 10. Prompts

### 목적

등록된 프롬프트 자산을 관리하는 메뉴다.

### 여기서 보는 것

- prompt 이름
- version
- latest / production alias
- template 내용

### 샘플에서 확인하는 것

- `offline-weather-agent-mlflow313-chat-prompt`
- 버전이 몇 번인지
- production/latest가 어느 버전을 가리키는지

### trace와의 관계

trace 안에서 `mlflow.genai.load_prompt(...)`가 호출되면 `Linked prompts`로 연결된다.

즉:

```text
Prompts = 프롬프트 자산 저장소
Linked prompts = 어떤 trace가 어떤 프롬프트를 썼는지 연결된 흔적
```

## 11. Agent versions

### 목적

에이전트 구성 자체를 버전 단위로 관리하는 메뉴다.

### 여기서 보는 것

- agent 버전
- 연결된 prompt
- 도구 구성
- 설정 버전

### 샘플에서 확인하는 것

이 샘플에서는 가장 핵심 메뉴는 아니지만, 아래처럼 확장할 때 중요해진다.

- core / langchain / langgraph 실행 경로 관리
- prompt 변경 이력 관리
- agent 구성을 버전별로 비교

### 쉽게 이해하면

```text
Agent versions = 에이전트 설계 버전 관리
```

## 샘플 기준으로 가장 자주 보는 메뉴

| 우선순위 | 메뉴 | 이유 |
| --- | --- | --- |
| 1 | `Training runs` | 모델 학습/등록 성공 여부 확인 |
| 2 | `Traces` | 웹 요청이 trace로 남는지 확인 |
| 3 | `Sessions` | 대화처럼 묶이는지 확인 |
| 4 | `Prompts` | linked prompt 확인 |
| 5 | `Judges` | 자동 평가 결과 확인 |

## 상황별로 어디를 보면 되는가

| 하고 싶은 일 | 먼저 볼 메뉴 | 같이 볼 메뉴 |
| --- | --- | --- |
| 모델 등록이 성공했는지 확인 | `Training runs` | `Models` |
| 웹 질문이 남는지 확인 | `Traces` | `Sessions` |
| 대화 세션으로 묶이는지 확인 | `Sessions` | `Traces` |
| 프롬프트 연결 여부 확인 | `Traces` | `Prompts` |
| 응답 품질 자동 평가 확인 | `Judges` | `Evaluation runs` |
| 평가용 문제집 관리 | `Datasets` | `Evaluation runs` |

## 이 샘플에서 추천 확인 순서

### 1. 모델 등록 확인

- `Training runs`
- `Models`

### 2. 웹 요청 trace 확인

- `Traces`

### 3. 대화 묶음 확인

- `Sessions`

### 4. prompt 연결 확인

- trace 상세의 `Linked prompts`
- `Prompts`

### 5. 자동 평가 확인

- `Judges`
- `Evaluation runs`

## 한 줄 요약

| 메뉴 | 핵심 의미 |
| --- | --- |
| `Training runs` | 모델 작업 실행 기록 |
| `Traces` | 질문 1건 처리 흐름 |
| `Sessions` | 대화 묶음 |
| `Judges` | 응답 평가 |
| `Review` | 수동 검토 |
| `Datasets` | 평가 문제집 |
| `Evaluation runs` | 평가 실행 기록 |
| `Playground` | 즉석 테스트 |
| `Prompts` | 프롬프트 자산 |
| `Agent versions` | 에이전트 버전 |
