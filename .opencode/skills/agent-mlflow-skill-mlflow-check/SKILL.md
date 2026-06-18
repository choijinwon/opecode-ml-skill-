---
name: agent-mlflow-skill-mlflow-check
description: 선택된 프로젝트가 MLflow tracking URI/remote 등록 테스트를 수행할 준비가 되었는지 확인하는 기준을 안내한다.
license: MIT
compatibility: opencode
metadata:
  flow: local-model-registration
  stage: 03-mlflow-check
  step: 3
---

# MLflow Readiness Validation

## When To Use

- Step 3에서 MLflow 의존성, tracking URI, experiment, registered model name을 점검할 때
- 사용자 설정 tracking URI와 원격 MLflow 등록 조건을 나눠 판단할 때
- 등록/실행 entrypoint의 register 기능을 사용하기 전에 준비 상태 요약이 필요할 때

## Checklist

- `mlflow` dependency가 requirements에 포함되어 있는지 확인한다.
- `MLFLOW_TRACKING_URI` 또는 `MLFLOW_TRACKING_URL` 설정 여부를 확인한다.
- experiment name과 registered model name 후보를 확인한다.
- 사용자 환경의 tracking URI 설정 여부를 확인한다.
- 인증 정보는 존재 여부만 표시하고 값은 숨긴다.

## Output

- configured tracking URI readiness
- remote registration readiness
- missing dependency/config list
- recommended tracking URI setup
- 다음 단계: `agent-mlflow-skill-gap-guide`

## Safety

- 원격 서버 연결이나 등록 실행은 하지 않는다.
- secret 값을 로그, trace, 화면 출력에 포함하지 않는다.
