---
name: mlflow-readiness-validation
description: 선택된 프로젝트가 MLflow local/remote 등록 테스트를 수행할 준비가 되었는지 검증한다.
license: MIT
compatibility: opencode
metadata:
  flow: model-test-scenario
  stage: 03-validation
  step: 3
---

# MLflow Readiness Validation

## When To Use

- Step 2~5에서 MLflow 의존성, tracking URI, experiment, registered model name을 점검할 때
- 로컬 `file:./mlruns` 테스트와 원격 MLflow 등록 조건을 나눠 판단할 때
- `run_model.py --register` 전에 readiness summary가 필요할 때

## Checklist

- `mlflow` dependency가 requirements에 포함되어 있는지 확인한다.
- `MLFLOW_TRACKING_URI` 또는 `MLFLOW_TRACKING_URL` 설정 여부를 확인한다.
- experiment name과 registered model name 후보를 확인한다.
- local file store fallback 가능 여부를 확인한다.
- username/password는 존재 여부만 표시하고 값은 숨긴다.

## Output

- local registration readiness
- remote registration readiness
- missing dependency/config list
- recommended fallback mode
- 다음 단계: `registration-gap-fill-planning`

## Safety

- 원격 서버 연결이나 등록 실행은 하지 않는다.
- secret 값을 로그, trace, report에 포함하지 않는다.
