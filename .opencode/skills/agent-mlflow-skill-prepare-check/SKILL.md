---
name: agent-mlflow-skill-prepare-check
description: 등록/실행 entrypoint에 prepare-only 기능이 있는지 확인하고, 실행 전 점검 기준을 안내한다.
license: MIT
compatibility: opencode
metadata:
  flow: local-model-registration
  stage: 06-prepare-only
  step: 6
---

# Prepare Only Check Guidance

## When To Use

- MLflow 등록 실행 전 local preparation smoke test 기준을 설계할 때
- 등록/실행 entrypoint에 prepare-only와 동등한 기능이 있는지 확인할 때
- artifact, config, input example을 실제 실행 전에 어떤 기준으로 확인할지 정해야 할 때

## Guidance Checks

- model artifact path exists
- `config.json` parses
- `input_example.json` parses
- wrapper can load or simulate model preparation
- output directory is writable
- Windows path normalization works
- prepare-only가 remote MLflow 등록을 수행하지 않는지 확인한다.

## Output

- prepare-only 기능 존재 여부 확인 기준
- 사용자 프로젝트에 맞춘 기능 확인 질문
- 실행 전 확인할 항목 checklist
- 실패 시 분류할 error category 기준
- user-friendly repair hint 기준
- 다음 단계: `agent-mlflow-skill-register-guide`

## Safety

- 이 skill은 prepare-only를 직접 실행하지 않는다.
- prepare-only 실행 명령을 제시하지 않고, 사용자가 확인해야 할 조건과 질문만 안내한다.
- 이 단계는 MLflow 원격 등록을 수행하도록 지시하지 않는다.
- 실제 실행 여부는 사용자와 프로젝트 운영 절차에 맡기고, 스킬은 안전한 경로 사용 필요성만 안내한다.
