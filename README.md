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

1. `@mlflow`로 프로젝트 목적을 분류합니다.
2. `mlflow-onboarding`으로 Tracking, Registry, Tracing, Evaluation 중 우선순위를 정합니다.
3. `mlflow-registration-check` 또는 `mlflow-experiment-tracking`으로 현재 코드 상태를 읽기 전용으로 점검합니다.
4. 수정이 필요하면 preview를 먼저 만들고, 승인 후 적용합니다.
5. `analysis-reporting`으로 등록 준비 리포트를 남깁니다.

## OpenCode 참고

이 저장소는 OpenCode의 project-local skill 경로인 `.opencode/skills/<name>/SKILL.md`를 사용합니다. OpenCode skill frontmatter에는 `name`, `description`, `license`, `compatibility`를 넣었습니다.

## License

MIT
