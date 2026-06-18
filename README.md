# OpenCode MLflow Skill Pack

OpenCode에서 MLflow 기반 ML/GenAI 프로젝트 온보딩, 실험 추적, 모델 등록, tracing, evaluation, 운영 점검을 빠르게 수행하기 위한 skill pack입니다.

이 저장소는 `choijinwon/agent-onboarding-ml`의 MLflow 온보딩 POC 구조를 OpenCode skill 형식에 맞게 정리한 버전입니다.

## 구성

```text
.opencode/
├── agents/
│   └── mlflow.md
└── skills/
    ├── mlflow-onboarding/
    ├── mlflow-experiment-tracking/
    ├── mlflow-registration-check/
    ├── mlflow-model-registry-deployment/
    ├── instrumenting-with-mlflow-tracing/
    ├── analyze-mlflow-trace/
    ├── agent-evaluation/
    └── ...
```

OpenCode는 프로젝트 루트에서 `.opencode/skills/<name>/SKILL.md`를 자동 발견합니다. 각 skill의 `name`은 폴더명과 일치합니다.

## 사용 방법

이 저장소를 ML 프로젝트 루트에 복사합니다.

```bash
cp -R .opencode /path/to/your-ml-project/
```

그다음 해당 ML 프로젝트에서 OpenCode를 실행하고 다음처럼 요청합니다.

```text
@mlflow 이 프로젝트 MLflow 등록 준비 상태 점검해줘
@mlflow train.py에 experiment tracking 누락된 부분 찾아줘
@mlflow LangChain agent에 MLflow tracing 붙이는 계획 만들어줘
@mlflow 모델 registry 배포 체크리스트 만들어줘
```

프로젝트에 이미 `.opencode`가 있다면 `skills/`와 `agents/mlflow.md`만 병합하세요.

## 포함된 주요 skill

### 모델 테스트 시나리오 단계 skill

- `model-scenario-orchestrator`: 전체 Step 1~10 흐름 조율
- `sample-model-matrix-generation`: 10개 폐쇄망 샘플 모델 matrix 정의
- `model-sample-selection-flow`: `.aiu/sample_projects/`와 `work/` 모델 선택 흐름
- `model-project-scan-validation`: requirements, entrypoint, artifact, config, input example 스캔
- `mlflow-readiness-validation`: local/remote MLflow 등록 준비 상태 점검
- `registration-gap-fill-planning`: Step 6 승인 전 누락 파일 보완 계획
- `run-model-template-planning`: `run_model.py` 옵션과 책임 정의
- `prepare-only-validation`: `run_model.py --prepare-only` 검증 흐름
- `mlflow-registration-execution`: local file store 또는 원격 MLflow 등록 실행 안내
- `wizard-cli-tui-step-flow`: Wizard, CLI, TUI 단계 연결
- `registration-result-reporting`: Step 10 결과 표와 다음 조치 정리

### MLflow 범용 skill

- `mlflow-onboarding`: Tracking, Evaluation, Registry, Tracing 중 시작 경로 선택
- `mlflow-experiment-tracking`: params, metrics, artifacts, datasets 기록 점검
- `mlflow-registration-check`: 모델 등록 전 필수 파일과 설정 확인
- `mlflow-model-registry-deployment`: registry, serving, deployment readiness 점검
- `instrumenting-with-mlflow-tracing`: GenAI 앱과 agent 코드에 tracing 추가
- `analyze-mlflow-trace`: trace span, latency, error, metadata 분석
- `retrieving-mlflow-traces`: MLflow trace 검색과 필터링 안내
- `agent-evaluation`: agent 품질 평가와 regression 비교
- `closed-network-validation`: 폐쇄망/내부망 환경 반입 전 점검
- `ai-studio-runtime-template`: AI Studio 등록용 runtime scaffold 점검

## 권장 작업 흐름

1. `@mlflow`로 모델 테스트 시나리오 전체를 시작합니다.
2. `sample-model-matrix-generation`으로 샘플 모델 set을 정합니다.
3. `model-sample-selection-flow`로 샘플 또는 `work/` 모델을 선택합니다.
4. `model-project-scan-validation`과 `mlflow-readiness-validation`으로 Step 2~5 검증을 수행합니다.
5. `registration-gap-fill-planning`으로 Step 6 보완 계획을 만들고 승인 항목을 분리합니다.
6. `run-model-template-planning`과 `prepare-only-validation`으로 Step 7~8 준비 검증을 정의합니다.
7. `mlflow-registration-execution`으로 Step 9 local/remote 등록 실행 조건을 안내합니다.
8. `registration-result-reporting`으로 Step 10 리포트를 정리합니다.

## OpenCode 참고

이 저장소는 OpenCode의 project-local skill 경로인 `.opencode/skills/<name>/SKILL.md`를 사용합니다. OpenCode skill frontmatter에는 `name`, `description`, `license`, `compatibility`를 넣었습니다.

## License

MIT
