---
name: agent-mlflow-skill-mlflow-check
description: 선택된 프로젝트가 MLflow 등록 준비 상태를 갖추었는지 확인하는 기준을 안내한다.
license: MIT
compatibility: opencode
metadata:
  flow: local-model-registration
  stage: 03-mlflow-check
  step: 3
---

# MLflow Readiness Guidance

## When To Use

- MLflow 의존성, tracking 설정 위치, experiment, registered model name을 점검할 때
- local MLflow와 remote MLflow 준비 상태를 나눠 판단할 때
- 등록 단계 전 MLflow 관련 누락 항목을 정리해야 할 때

## Guidance Checks

- `mlflow` dependency가 requirements에 포함되어 있는지 확인한다.
- tracking URI 또는 tracking URL 설정 위치를 확인한다.
- experiment name과 registered model name 후보를 확인한다.
- local/remote 중 어떤 등록 방식을 전제로 하는지 확인한다.
- 인증 정보는 존재 여부와 주입 위치만 확인한다.
- 인증 정보는 존재 여부만 표시하고 값은 숨긴다.

## Output

- MLflow 준비 상태 요약
- local/remote 등록 방식별 확인 결과
- 누락된 dependency 또는 설정 항목
- 사용자에게 확인할 MLflow 관련 질문
- 다음 단계: `agent-mlflow-skill-gap-guide`

## Safety

- 원격 서버 연결이나 등록 실행은 하지 않는다.
- secret 값을 로그, trace, 화면 출력에 포함하지 않는다.
- 특정 tracking URI 값이나 저장 위치를 기본값으로 가정하지 않는다.
