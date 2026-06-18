---
name: model-scenario-orchestrator
description: 다양한 샘플 모델 생성, 선택, 검증, MLflow 등록 테스트를 Step 1~10 흐름으로 조율한다.
license: MIT
compatibility: opencode
metadata:
  flow: model-test-scenario
  stage: 00-orchestration
  step: 0
---

# Model Scenario Orchestrator

## When To Use

- 사용자가 "모델 테스트 시나리오", "샘플 모델 선택", "MLflow 등록까지 한 번에" 같은 전체 흐름을 요청할 때
- Wizard, CLI, TUI에서 어떤 단계 skill을 먼저 써야 할지 결정해야 할 때
- 구현 코드를 바로 만들기보다 단계별 기능 명세를 정리해야 할 때

## Responsibilities

- Step 1~10 전체 진행 상태를 추적한다.
- 사용자의 목적을 sample generation, selection, validation, preparation, registration, reporting 중 하나로 분류한다.
- 필요한 하위 skill을 순서대로 호출한다.
- 각 단계의 입력, 산출물, 차단 조건을 짧게 요약한다.

## Step Routing

1. 샘플 생성: `sample-model-matrix-generation`
2. 모델 선택: `model-sample-selection-flow`
3. 프로젝트 스캔: `model-project-scan-validation`
4. MLflow 준비 검증: `mlflow-readiness-validation`
5. 누락 파일 보완 계획: `registration-gap-fill-planning`
6. `run_model.py` 템플릿 계획: `run-model-template-planning`
7. prepare-only 검증: `prepare-only-validation`
8. MLflow 등록 실행 안내: `mlflow-registration-execution`
9. Wizard/CLI/TUI 연결: `wizard-cli-tui-step-flow`
10. 결과 리포트: `registration-result-reporting`

## Output

- 현재 단계
- 다음에 사용할 skill
- 사용자가 선택한 모델 또는 프로젝트
- 검증 통과/보완 필요/차단 항목
- 다음 명령 또는 Wizard 액션

## Safety

- 외부 다운로드를 전제로 하지 않는다.
- 삭제, 대규모 구조 변경, credential 삽입은 계획에서 제외한다.
- 실제 원격 MLflow 등록은 사용자가 설정과 실행을 승인한 경우에만 안내한다.
