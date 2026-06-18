---
name: agent-mlflow-skill-register-guide
description: 사용자 환경의 MLflow tracking URI 또는 원격 MLflow 등록 실행 조건과 주의사항을 안내한다.
license: MIT
compatibility: opencode
metadata:
  flow: local-model-registration
  stage: 07-registration
  step: 7
---

# MLflow Registration Execution

## When To Use

- `run_model.py --register` 실행 조건을 안내할 때
- 사용자 설정 `MLFLOW_TRACKING_URI` 등록과 원격 MLflow 등록을 구분해야 할 때
- 등록 실행 조건과 다음 조치를 안내해야 할 때

## Configured Tracking URI

- `MLFLOW_TRACKING_URI` 또는 `MLFLOW_TRACKING_URL`이 비어 있으면 사용자에게 tracking URI 설정이 필요하다고 안내한다.
- 사용자 설정 tracking URI, artifact, registered model name 후보를 표시한다.
- 테스트 목적의 등록 성공 여부를 짧게 요약한다.

## Remote Mode

- `ai_studio.env`에 tracking URL, username/password, experiment, registered model name이 있는지 확인한다.
- secret 값은 표시하지 않는다.
- 원격 등록 실행은 사용자의 명시적 승인 이후에만 안내한다.

## Output

- registration command
- tracking URI/remote mode
- experiment name
- registered model name
- run id 또는 tracking output path
- next action

## Safety

- credential을 생성하거나 저장하지 않는다.
- 등록 실패 시 에러 로그를 민감정보 마스킹 후 요약한다.
