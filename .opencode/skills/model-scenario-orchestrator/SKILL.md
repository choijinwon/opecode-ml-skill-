---
name: model-scenario-orchestrator
description: 사용자가 가져온 로컬 모델 프로젝트의 선택, 검증, MLflow 등록 준비를 Step 1~9 흐름으로 조율한다.
license: MIT
compatibility: opencode
metadata:
  flow: local-model-registration
  stage: 00-orchestration
  step: 0
---

# Model Scenario Orchestrator

## When To Use

- 사용자가 "가져온 모델 점검", "로컬 모델 MLflow 등록", "등록 준비를 단계별로 알려줘" 같은 전체 흐름을 요청할 때
- 로컬 프로젝트에서 어떤 단계 skill을 먼저 써야 할지 결정해야 할 때
- 구현 코드를 바로 만들기보다 단계별 기능 명세를 정리해야 할 때

## Responsibilities

- Step 1~9 전체 진행 상태를 추적한다.
- 사용자의 목적을 intake, validation, preparation, registration, reporting 중 하나로 분류한다.
- 필요한 하위 skill을 순서대로 호출한다.
- 각 단계의 입력, 산출물, 차단 조건을 짧게 요약한다.

## Step Routing

1. 로컬 모델 선택: `local-model-intake-flow`
2. 프로젝트 스캔: `model-project-scan-validation`
3. MLflow 준비 검증: `mlflow-readiness-validation`
4. 누락 파일 보완 안내: `registration-gap-fill-planning`
5. `run_model.py` 동작 계획: `run-model-template-planning`
6. prepare-only 검증: `prepare-only-validation`
7. MLflow 등록 실행 안내: `mlflow-registration-execution`
8. Wizard/CLI/TUI 연결: `wizard-cli-tui-step-flow`
9. 결과 리포트: `registration-result-reporting`

## Output

- 현재 단계
- 다음에 사용할 skill
- 사용자가 가져온 모델 프로젝트
- 검증 통과/보완 필요/차단 항목
- 다음 명령 또는 Wizard 액션

## Safety

- 외부 다운로드나 샘플 생성을 전제로 하지 않는다.
- 삭제, 대규모 구조 변경, credential 삽입은 계획에서 제외한다.
- 실제 원격 MLflow 등록은 사용자가 설정과 실행을 승인한 경우에만 안내한다.
