---
name: agent-mlflow-skill-prepare-check
description: 등록/실행 entrypoint에 prepare-only 또는 dry-run 기능이 있는지 확인하고, 실행 전 점검 기준을 안내한다.
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
- 등록/실행 entrypoint에 prepare-only 또는 dry-run과 동등한 기능이 있는지 확인할 때
- artifact, config, input example을 실제 실행 전에 어떤 기준으로 확인할지 정해야 할 때

## Guidance Checks

- model artifact path exists
- `config.json` parses
- `input_example.json` parses
- wrapper can load or simulate model preparation
- output directory is writable
- Windows path normalization works
- prepare-only 또는 dry-run이 remote MLflow 등록을 수행하지 않는지 확인한다.

## Output

- prepare-only 또는 dry-run 기능 존재 여부 확인 기준
- 사용자 프로젝트에 맞춘 command 예시 또는 확인 질문
- 실행 전 확인할 항목 checklist
- 실패 시 분류할 error category 기준
- user-friendly repair hint 기준
- 다음 단계: `agent-mlflow-skill-register-guide`

## Safety

- 이 skill은 dry-run을 직접 실행하지 않는다.
- 사용자가 명시적으로 실행을 요청하거나 승인한 경우에만 프로젝트의 prepare-only 또는 dry-run 명령 실행을 안내한다.
- 이 단계는 MLflow 원격 등록을 수행하도록 지시하지 않는다.
- 사용자가 실행을 승인해 임시 파일이 생기는 경우에는 사용자 프로젝트가 허용한 안전한 경로를 사용하도록 안내한다.
