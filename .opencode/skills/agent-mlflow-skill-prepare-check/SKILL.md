---
name: agent-mlflow-skill-prepare-check
description: run_model.py --prepare-only로 모델 artifact 준비와 입력 예제를 확인하는 기준을 안내한다.
license: MIT
compatibility: opencode
metadata:
  flow: local-model-registration
  stage: 06-prepare-only
  step: 6
---

# Prepare Only Validation

## When To Use

- MLflow 등록 실행 전 local preparation smoke test를 설계할 때
- `run_model.py --prepare-only` 결과에서 어떤 상태를 확인할지 정해야 할 때
- artifact, config, input example이 실제로 함께 동작하는지 확인해야 할 때

## Checks

- model artifact path exists
- `config.json` parses
- `input_example.json` parses
- wrapper can load or simulate model preparation
- output directory is writable
- Windows path normalization works

## Output

- prepare-only command
- success/failure status
- error category
- user-friendly repair hint
- 다음 단계: `agent-mlflow-skill-register-guide`

## Safety

- 이 단계는 MLflow 원격 등록을 수행하지 않는다.
- 준비 검증 산출물은 프로젝트 내부 또는 `.aiu/` 아래로 제한한다.
