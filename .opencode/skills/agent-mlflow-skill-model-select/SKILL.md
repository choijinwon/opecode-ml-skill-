---
name: agent-mlflow-skill-model-select
description: 사용자가 가져온 로컬 모델 프로젝트를 찾고 MLflow 등록 검증 대상으로 선택하도록 안내한다.
license: MIT
compatibility: opencode
metadata:
  flow: local-model-registration
  stage: 01-intake
  step: 1
---

# Model Select

## When To Use

- 사용자가 직접 가져온 모델 프로젝트를 OpenCode에서 점검하려고 할 때
- 사용자가 지정한 경로 또는 현재 프로젝트 루트에서 모델 후보를 찾아야 할 때
- 모델 생성 없이 기존 artifact와 코드만 기준으로 MLflow 등록 준비를 안내해야 할 때

## Inputs

- current repository root
- explicit project path from the user
- known files: `requirements.txt`, `train.py`, `config.json`, optional environment/config files, `input_example.json`

## Selection Rules

- 사용자가 경로를 지정하면 그 경로를 우선한다.
- 경로가 없으면 OpenCode를 실행한 현재 프로젝트 루트를 기준으로 모델 후보를 찾는다.
- 후보별 framework, artifact 위치, 주요 파일 존재 여부를 요약한다.
- 여러 후보가 있으면 하나를 선택하도록 안내한다.
- 선택이 끝나면 `agent-mlflow-skill-project-check`으로 넘긴다.

## Output

- selected project path
- detected framework candidates
- detected artifact candidates
- existing registration files
- missing critical files summary
- next skill: `agent-mlflow-skill-project-check`

## Safety

- 이 단계에서는 파일을 만들거나 수정하지 않는다.
- 모델 artifact를 이동하거나 복사하지 않는다.
- credential 값은 읽어도 출력하지 않는다.
