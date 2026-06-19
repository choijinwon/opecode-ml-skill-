---
name: agent-mlflow-skill-model-select
description: 로컬 모델 프로젝트 또는 제공 샘플을 자동 후보 선정 규칙에 따라 MLflow 등록 검증 대상으로 정하도록 안내한다.
license: MIT
compatibility: opencode
metadata:
  flow: local-model-registration
  stage: 01-intake
  step: 1
---

# Local Model Auto Selection Guidance

## When To Use

- 사용자가 직접 가져온 모델 프로젝트 또는 저장소가 제공하는 샘플 프로젝트를 OpenCode에서 점검하려고 할 때
- 사용자가 지정한 경로 또는 현재 프로젝트 루트에서 모델 후보를 찾아야 할 때
- 사용자가 직접 후보를 선택하지 않아도 기본 점검 대상을 정해야 할 때
- 모델 생성 없이 기존 artifact와 코드만 기준으로 MLflow 등록 준비를 안내해야 할 때

## Guidance Checks

- 현재 작업 경로와 사용자가 지정한 경로 중 어느 쪽을 기준으로 볼지 정리한다.
- 사용자가 명시한 프로젝트 경로가 있으면 그 경로를 우선 확인한다.
- 명시 경로가 `.opencode/samples/` 아래 샘플 프로젝트여도 동일한 기준으로 확인한다.
- 모델 프로젝트 후보에서 artifact, entrypoint, 설정 파일, 입력 예제 파일 존재 여부를 본다.
- 특정 파일명이 없더라도 등록 절차를 설명할 수 있는 구조인지 함께 본다.

## Auto Selection Rules

- 사용자가 경로를 지정하면 그 경로를 자동 선택한다.
- 경로가 없고 현재 루트에 모델 프로젝트 파일이 있으면 현재 루트를 자동 선택한다.
- 경로가 없고 `.opencode/samples/` 아래 샘플만 명확하면 기본 우선순위로 자동 선택한다.
- 기본 샘플 우선순위는 `sklearn_sample`, `pytorch_sample`, `tensorflow_sample` 순서다.
- 후보별 framework, artifact 위치, 주요 파일 존재 여부를 요약한다.
- 여러 후보가 있어도 우선순위로 하나를 자동 선택하고, 나머지는 대체 후보로 표시한다.
- 자동 선택 근거를 짧게 설명한 뒤 `agent-mlflow-skill-project-check`으로 넘긴다.

## Ambiguity Rules

- 현재 루트와 `.opencode/samples/`가 모두 후보이면 현재 루트를 우선한다.
- 사용자 프로젝트 후보가 여러 개이고 우선순위 근거가 없으면 가장 많은 핵심 파일을 가진 후보를 우선한다.
- 핵심 파일 점수는 `requirements.txt`, entrypoint, artifact, config, input example 순서로 계산한다.
- 동점이면 자동 확정하지 않고 후보와 부족 근거를 요약해 사용자 확인을 요청한다.
- credential 또는 외부 시스템 설정만으로 후보를 선택하지 않는다.

## Output

- 선택된 프로젝트 경로
- 자동 선택 근거
- 추정 framework 후보
- 발견된 artifact 후보
- 등록 관련 파일 존재 여부
- 대체 후보 목록
- 우선 확인이 필요한 누락 항목
- 다음 단계: `agent-mlflow-skill-project-check`

## Safety

- 이 단계에서는 파일을 만들거나 수정하지 않는다.
- 모델 artifact를 이동하거나 복사하지 않는다.
- credential 값은 읽어도 출력하지 않는다.
- 후보가 동점이거나 위험하게 모호하면 자동 확정하지 않고 확인을 요청한다.
