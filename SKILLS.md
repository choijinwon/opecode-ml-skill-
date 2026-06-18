# Skill Index

## Local Model Registration Flow

| Step | Skill | Purpose |
| --- | --- | --- |
| 0 | `model-scenario-orchestrator` | 사용자가 가져온 로컬 모델의 선택, 검증, prepare-only, MLflow 등록 안내, 리포트 전체 흐름을 조율합니다. |
| 1 | `local-model-intake-flow` | 현재 프로젝트, 명시 경로, `work/` 아래 로컬 모델 후보를 탐지하고 선택하도록 안내합니다. |
| 2-4 | `model-project-scan-validation` | requirements, entrypoint, artifact, config, env, input example을 읽기 전용으로 스캔합니다. |
| 2-4 | `mlflow-readiness-validation` | MLflow dependency, tracking URI, experiment, registered model name, local fallback을 검증합니다. |
| 5 | `registration-gap-fill-planning` | 부족한 파일과 설정을 safe, review_required, blocked로 나눠 보완 안내를 만듭니다. |
| 5 | `run-model-template-planning` | `run_model.py`의 `--prepare-only`, `--register`, `--env-file`, `--config`, `--model` 동작을 정의합니다. |
| 6 | `prepare-only-validation` | `run_model.py --prepare-only` 준비 검증 흐름과 실패 원인 분류를 정의합니다. |
| 7-8 | `mlflow-registration-execution` | local `file:./mlruns` 또는 원격 MLflow 등록 실행 조건을 정의합니다. |
| 1-9 | `wizard-cli-tui-step-flow` | Wizard, CLI, TUI가 같은 단계 상태를 쓰도록 명령과 화면 필드를 매핑합니다. |
| 9 | `registration-result-reporting` | 최종 결과 표, pass/warn/block 요약, 다음 조치를 정리합니다. |

## Existing MLflow Skills

| Skill | Purpose |
| --- | --- |
| `agent-evaluation` | Agent 품질 평가와 regression 비교를 설계합니다. |
| `ai-studio-runtime-template` | AI Studio 등록용 runtime scaffold를 점검합니다. |
| `analysis-reporting` | 분석 결과와 등록 준비 상태를 리포트로 정리합니다. |
| `analyze-mlflow-chat-session` | MLflow에 남은 chat session 기록을 분석합니다. |
| `analyze-mlflow-trace` | MLflow trace span, latency, error, metadata를 분석합니다. |
| `closed-network-validation` | 폐쇄망 반입과 내부망 실행 전 제약을 점검합니다. |
| `error-log-repair` | 오류 로그를 바탕으로 원인과 수정 후보를 정리합니다. |
| `instrumenting-with-mlflow-tracing` | Python/TypeScript GenAI 앱에 MLflow Tracing을 붙입니다. |
| `job-template-draft` | 학습/등록 Job Template 초안을 만듭니다. |
| `local-serving-validation` | 로컬 서빙 검증 절차와 입력 예제를 점검합니다. |
| `ml-platform-onboarding-orchestrator` | 전체 ML 플랫폼 온보딩 흐름을 조율합니다. |
| `mlflow-ai-gateway` | MLflow AI Gateway 사용과 설정을 안내합니다. |
| `mlflow-experiment-tracking` | params, metrics, artifacts, datasets logging 상태를 점검합니다. |
| `mlflow-model-registry-deployment` | 모델 registry와 deployment readiness를 점검합니다. |
| `mlflow-onboarding` | 신규 사용자가 MLflow 시작 경로를 고르도록 돕습니다. |
| `mlflow-prompt-management` | prompt versioning과 관리 흐름을 점검합니다. |
| `mlflow-prompt-optimization` | prompt 실험과 최적화 평가 흐름을 설계합니다. |
| `mlflow-registration-check` | 모델 등록 전 필수 파일과 설정을 확인합니다. |
| `model-project-standardization` | ML 프로젝트 구조와 실행 파일을 표준화합니다. |
| `querying-mlflow-metrics` | MLflow metric 검색과 비교 분석을 안내합니다. |
| `retrieving-mlflow-traces` | MLflow trace 검색, 필터링, 내보내기 흐름을 안내합니다. |
| `searching-mlflow-docs` | MLflow 문서 검색과 근거 정리를 지원합니다. |
