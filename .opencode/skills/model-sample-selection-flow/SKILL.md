---
name: model-sample-selection-flow
description: 생성된 샘플과 work/ 사용자 모델을 탐지하고 Step 1에서 선택 가능한 목록으로 정리한다.
license: MIT
compatibility: opencode
metadata:
  flow: model-test-scenario
  stage: 02-selection
  step: 1
---

# Model Sample Selection Flow

## When To Use

- Wizard Step 1 또는 TUI input에서 모델 목록을 보여줘야 할 때
- `.aiu/sample_projects/`와 `work/` 아래 프로젝트를 함께 탐지해야 할 때
- 사용자가 모델 이름, sample kind, 경로 중 하나로 선택할 수 있게 해야 할 때

## Inputs

- sample command: `/sample all`, `/sample large10`, `/sample tensorflow`, `/sample pytorch`
- sample root: `.aiu/sample_projects/`
- user model root: `work/`
- selected project path or alias

## Selection Rules

- 샘플 프로젝트와 사용자 프로젝트를 한 목록으로 합친다.
- 같은 이름이 있으면 full path를 표시한다.
- framework, artifact size, 주요 파일 존재 여부를 함께 보여준다.
- 선택이 끝나면 Step 2 validation으로 넘긴다.

## Output

- 선택 가능한 모델 목록
- 선택된 프로젝트 경로
- framework 후보
- missing critical files summary
- 다음 단계: `model-project-scan-validation`
