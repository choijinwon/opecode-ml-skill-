# Skill Analysis Report

## 1. 분석 개요

분석 대상은 OpenCode MLflow Local Model Skills의 7개 skill이다.

분석 목적:

- 현재 skill 구성이 요구사항에 맞는지 확인한다.
- skill-only 배포 원칙이 지켜지는지 확인한다.
- 단계 흐름, 네이밍, 안전 기준, 사용자 경험 측면의 적합성을 평가한다.
- 배포 전 보완하면 좋은 개선 항목을 정리한다.

참조 문서:

- `README.md`
- `SKILLS.md`
- `SKILL_REQUIREMENTS.md`
- `.opencode/skills/*/SKILL.md`

## 2. 현재 구성 요약

현재 저장소는 앱, CLI, TUI, 샘플 생성기, 자동 스캐너를 포함하지 않고 OpenCode skill 파일만 제공한다.

현재 skill 목록:

| Step | Skill | 역할 |
| --- | --- | --- |
| 1 | `agent-mlflow-skill-model-select` | 사용자가 가져온 로컬 모델 경로 선택 |
| 2 | `agent-mlflow-skill-project-check` | 프로젝트 구조와 필수 파일 확인 기준 안내 |
| 3 | `agent-mlflow-skill-mlflow-check` | MLflow 등록 준비 상태 확인 기준 안내 |
| 4 | `agent-mlflow-skill-gap-guide` | 부족한 파일과 설정의 보완 방향 분류 |
| 5 | `agent-mlflow-skill-run-model-guide` | `run_model.py` 옵션과 동작 기준 안내 |
| 6 | `agent-mlflow-skill-prepare-check` | `--prepare-only` 검증 기준 안내 |
| 7 | `agent-mlflow-skill-register-guide` | local/remote MLflow 등록 조건 안내 |

## 3. 요구사항 적합성 평가

| 항목 | 평가 | 근거 |
| --- | --- | --- |
| skill-only 배포 | 적합 | `.opencode/skills` 아래 7개 `SKILL.md`만 기능 자산으로 유지된다. |
| 샘플 생성 제외 | 적합 | 샘플 모델 생성 skill과 관련 문구가 제거되어 있다. |
| 자동 실행 제외 | 적합 | CLI, TUI, 자동 스캐너, 원격 등록 실행 기능을 포함하지 않는다. |
| 네이밍 규칙 | 적합 | 모든 skill이 `agent-mlflow-skill-` prefix와 lowercase kebab-case를 사용한다. |
| 폴더명/name 일치 | 적합 | 각 skill의 폴더명과 frontmatter `name`이 동일하다. |
| 단계 흐름 | 적합 | model select에서 register guide까지 1~7 단계가 연결된다. |
| 안전 기준 | 대체로 적합 | credential 출력 금지, 파일 수정 금지, 원격 등록 실행 제한이 명시되어 있다. |

## 4. 단계 흐름 분석

### 4.1 Model Select

장점:

- 사용자가 명시한 경로를 우선하도록 되어 있어 실제 사용 흐름과 잘 맞는다.
- 현재 프로젝트 루트와 `work/` 후보를 함께 고려해 초보자에게 친절하다.
- 파일 생성, 복사, 이동 금지가 명확하다.

주의점:

- `work/`는 특정 프로젝트 관습일 수 있으므로, 사용자 프로젝트에 `work/`가 없을 때 현재 루트 중심으로 안내해야 한다.

### 4.2 Project Check

장점:

- MLflow 등록 준비에 필요한 주요 파일을 명확히 나열한다.
- `pass/warn/block` 상태 구분을 요구해 다음 단계 판단이 쉽다.
- credential 값 출력 금지가 포함되어 있다.

주의점:

- framework 추정 기준은 TensorFlow/Keras, PyTorch, scikit-learn, ONNX, HuggingFace, XGBoost, LightGBM, custom pyfunc 기준으로 보강되어 있다.
- 다만 실제 프로젝트가 여러 framework를 혼합할 수 있으므로 primary model과 preprocessing dependency를 분리해서 해석해야 한다.

### 4.3 MLflow Check

장점:

- local tracking URI/remote 등록 준비를 분리한다.
- `MLFLOW_TRACKING_URI`, `MLFLOW_TRACKING_URL`, experiment, registered model name 확인 기준이 있다.
- secret 값 숨김과 원격 서버 미연결 원칙이 명확하다.

주의점:

- `MLFLOW_TRACKING_URI`와 `MLFLOW_TRACKING_URL`의 우선순위 또는 매핑 규칙은 더 자세히 정의할 수 있다.

### 4.4 Gap Guide

장점:

- 누락 항목을 `safe`, `review_required`, `blocked`로 분류해 안전한 안내가 가능하다.
- credential 삽입, artifact 삭제, 프로젝트 외부 수정이 blocked로 명시되어 있다.

주의점:

- `safe` 항목도 실제 파일 작성은 하지 않는다는 점을 계속 유지해야 한다.
- 사용자에게 "추가 안내"와 "자동 추가"가 혼동되지 않도록 표현을 관리해야 한다.

### 4.5 Run Model Guide

장점:

- `run_model.py`에 필요한 핵심 옵션이 단순하고 명확하다.
- Windows 경로와 공백 경로를 고려한다.
- 사용자 환경의 tracking URI 설정과 `mlflow.pyfunc.log_model(...)` 흐름을 안내한다.

주의점:

- 이 skill은 템플릿 구현이 아니라 안내용이라는 범위가 중요하다.
- framework별 wrapper 차이를 숨기되, 사용자가 어떤 wrapper가 필요한지 판단할 최소 기준이 필요할 수 있다.

### 4.6 Prepare Check

장점:

- 등록 전 점검 항목이 artifact, config, input example, output directory 중심으로 잘 정리되어 있다.
- 원격 등록을 수행하지 않는다는 안전 기준이 있다.

주의점:

- `wrapper can load or simulate model preparation`은 구현 방식에 따라 해석이 넓다. "실행 가능하면 load, 실행이 어렵다면 필요한 준비 조건만 확인"처럼 표현을 더 명확히 할 수 있다.

### 4.7 Register Guide

장점:

- 사용자 설정 tracking URI와 remote mode를 분리해 안내한다.
- 원격 등록은 명시적 승인 이후에만 안내하도록 되어 있다.
- credential 저장/생성을 금지한다.

주의점:

- 이 skill은 실행 조건 안내가 목적이므로, 실제 등록 실행으로 오해되지 않게 "명령 예시"와 "실행 승인"을 분리해 표현하는 것이 좋다.

## 5. 네이밍 분석

현재 네이밍은 이전 버전보다 훨씬 직관적이다.

좋은 점:

- `model-select`, `project-check`, `mlflow-check`, `gap-guide`, `run-model-guide`, `prepare-check`, `register-guide`는 단계별 목적이 바로 보인다.
- `agent-mlflow-skill-` prefix가 있어 배포 대상과 도메인이 분명하다.
- 모든 이름이 OpenCode skill 규칙에 맞는 lowercase kebab-case다.

남은 고려점:

- prefix가 길기 때문에 실제 대화에서 사용자가 직접 skill 이름을 부르기에는 다소 길다.
- 다만 배포/정렬/충돌 방지 목적이라면 현재 prefix는 유효하다.

## 6. 안전성 분석

현재 skill pack은 다음 안전 원칙을 유지한다.

- 파일 자동 생성 없음
- 기존 파일 자동 수정 없음
- 모델 artifact 이동/삭제/복사 없음
- secret 값 출력 금지
- 원격 MLflow 직접 연결 또는 등록 실행 없음
- 샘플 모델 다운로드 또는 생성 없음

이 방향은 "사용자에게 단순 skill만 제공"한다는 배포 목적에 잘 맞는다.

## 7. 사용자 경험 분석

사용자 흐름은 단순하다.

1. 사용자가 로컬 모델 경로를 제시한다.
2. OpenCode가 skill 지침에 따라 필요한 파일을 확인한다.
3. 부족한 항목을 안전하게 분류해 알려준다.
4. `run_model.py`와 `--prepare-only` 기준을 안내한다.
5. local/remote MLflow 등록 조건을 안내한다.

좋은 점:

- 단계가 7개로 짧고 이해하기 쉽다.
- 구현이 아니라 안내 중심이라 배포 부담이 낮다.
- 로컬 모델 프로젝트에 바로 복사해 사용할 수 있다.

아쉬운 점:

- skill만으로는 일관된 기계적 검사 결과가 보장되지는 않는다.
- 실제 파일 검사 품질은 OpenCode agent가 얼마나 정확히 로컬 파일을 읽고 해석하는지에 의존한다.

## 8. 리스크와 완화 방안

| 리스크 | 영향 | 완화 방안 |
| --- | --- | --- |
| 사용자가 skill을 자동 스캐너로 오해 | 기대치 불일치 | README와 요구사항 문서에 "안내용 skill"임을 유지한다. |
| secret 값 노출 | 보안 문제 | 모든 단계에서 값 대신 존재 여부만 표시하도록 유지한다. |
| `safe` 항목을 자동 생성으로 오해 | 파일 변경 혼동 | `safe`를 "추가 안내 가능"으로 계속 표현한다. |
| framework 혼합 프로젝트 해석 오류 | 안내 품질 저하 | primary model framework와 preprocessing framework를 분리해 표시한다. |
| 원격 등록 실행으로 오해 | 의도치 않은 외부 연결 | register-guide에서 "명시적 승인 전 실행 없음"을 유지한다. |

## 9. 개선 제안

우선순위 높은 개선:

- `agent-mlflow-skill-mlflow-check`에 local/remote 설정 우선순위를 추가한다.
- `agent-mlflow-skill-register-guide`에 "명령 예시와 실제 실행은 분리"한다는 문구를 강화한다.

우선순위 낮은 개선:

- 각 skill 제목을 새 짧은 이름에 맞춰 `Project Check`, `MLflow Check`, `Gap Guide`처럼 정리한다.
- 출력 형식을 더 일관되게 `Status`, `Evidence`, `Next`로 통일한다.
- README에 "추천 사용자 질문 예시"를 7단계에 맞춰 한 줄씩 추가한다.

## 10. 결론

현재 skill pack은 사용자가 요청한 "단순 skill 제공" 목적에 부합한다.

핵심 판단:

- skill-only 배포 원칙은 지켜지고 있다.
- 단계는 로컬 모델 선택부터 MLflow 등록 안내까지 자연스럽게 이어진다.
- 네이밍은 짧고 직관적으로 개선되었다.
- 안전 요구사항도 전반적으로 적절하다.

배포 가능 상태로 판단한다. 다만 local/remote 설정 우선순위와 framework 혼합 프로젝트 해석 기준을 조금 더 보강하면 실제 사용 품질이 더 좋아질 것이다.
