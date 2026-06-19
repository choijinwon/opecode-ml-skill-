---
name: agent-mlflow-skill-run-model-guide
description: MLflow 등록 테스트용 등록/실행 entrypoint가 제공하면 좋은 기능과 동작 기준을 안내한다.
license: MIT
compatibility: opencode
metadata:
  flow: local-model-registration
  stage: 05-run-model-guidance
  step: 5
---

# Registration Entrypoint Guidance

## When To Use

- 등록/실행 entrypoint 구성 또는 보강 안내를 설계할 때
- 등록 전 사전 준비 검증 단계, register 단계, env/config/model path 전달 등 사용자 entrypoint가 제공하면 좋은 기능을 정의할 때
- 모델별 wrapper 차이는 숨기고 공통 등록 흐름을 제공해야 할 때

## Guidance Checks

- 사전 준비 검증 기능: artifact와 config를 읽고 등록 전 준비 상태만 확인한다.
- register 기능: MLflow logging/register 실행 조건을 분리한다.
- environment config 전달 기능: 사용자 프로젝트의 환경 변수/설정 방식을 읽을 수 있게 한다.
- config path 전달 기능: `config.json` 경로를 받을 수 있게 한다.
- model path 전달 기능: model artifact 경로를 명시할 수 있게 한다.

옵션 이름이나 구현 방식은 사용자 프로젝트마다 달라도 된다. 중요한 것은 같은 책임을 수행하는 단계가 있는지 확인하는 것이다.

## Entrypoint Responsibilities

- Windows 경로와 공백이 있는 경로를 처리한다.
- 사용자 환경의 tracking URI 설정을 지원한다.
- `mlflow.pyfunc.log_model(...)`과 `registered_model_name` 사용 흐름을 갖는다.
- 원격 설정이 비어 있으면 친절한 tracking URI 설정 안내를 출력한다.

## Output

- entrypoint가 제공하면 좋은 기능 목록
- 기능별 기대 동작
- framework별 wrapper 필요 여부
- 다음 단계: `agent-mlflow-skill-preflight-check`

## Safety

- 이 skill은 특정 파일명이나 옵션명을 강제하지 않는다.
- entrypoint 구현 방식을 하나로 표준화했다고 가정하지 않는다.
- 실제 실행 명령이나 등록 수행을 기본 동작으로 전제하지 않는다.
