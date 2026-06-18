---
name: mlflow-registration-execution
description: Step 9~10에서 로컬 file store 또는 원격 MLflow 등록 실행 조건과 결과 처리를 정의한다.
license: MIT
compatibility: opencode
metadata:
  flow: local-model-registration
  stage: 06-registration
  step: 9
---

# MLflow Registration Execution

## When To Use

- `run_model.py --register` 실행 조건을 안내할 때
- 로컬 `MLFLOW_TRACKING_URI=file:./mlruns` 등록과 원격 MLflow 등록을 구분해야 할 때
- 등록 결과를 Step 10 리포트로 넘겨야 할 때

## Local Mode

- `MLFLOW_TRACKING_URI` 또는 `MLFLOW_TRACKING_URL`이 비어 있으면 local file store를 기본값으로 안내한다.
- local run, artifact, registered model name 후보를 표시한다.
- 테스트 목적의 등록 성공 여부를 리포트한다.

## Remote Mode

- `ai_studio.env`에 tracking URL, username/password, experiment, registered model name이 있는지 확인한다.
- secret 값은 표시하지 않는다.
- 원격 등록 실행은 사용자의 명시적 승인 이후에만 안내한다.

## Output

- registration command
- local/remote mode
- experiment name
- registered model name
- run id 또는 local run path
- 다음 단계: `registration-result-reporting`

## Safety

- credential을 생성하거나 저장하지 않는다.
- 등록 실패 시 에러 로그를 민감정보 마스킹 후 요약한다.
