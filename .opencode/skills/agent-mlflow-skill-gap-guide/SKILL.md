---
name: agent-mlflow-skill-gap-guide
description: MLflow 등록 준비 과정에서 부족한 파일, 설정, 판단 항목을 안내 가능한 수준으로 분류한다.
license: MIT
compatibility: opencode
metadata:
  flow: local-model-registration
  stage: 04-gap-guidance
  step: 4
---

# Registration Gap Guidance

## When To Use

- 프로젝트 스캔이나 MLflow 준비 검증 후 누락 항목이 발견되었을 때
- 사용자에게 무엇이 비어 있는지와 어떤 수준으로 안내할 수 있는지 정리해야 할 때
- 안전하게 설명 가능한 항목과 사람 판단이 필요한 항목을 분리해야 할 때

## Classifications

- `safe`
  추가 확인 질문이나 일반적인 보완 방향을 바로 안내할 수 있는 항목이다.
  예: input example 위치 확인, 설정 파일 존재 여부 확인, artifact 경로 확인, MLflow 관련 키 위치 질문
- `review_required`
  프로젝트별 구현 차이 때문에 사람 판단 없이 단정하면 위험한 항목이다.
  예: 등록 entrypoint 후보가 여러 개인 경우, wrapper 파일 역할이 불명확한 경우, 의존성 파일 수정 여부 판단, framework 추정은 되지만 확정 근거가 약한 경우
- `blocked`
  다음 단계로 넘어가기 전에 핵심 정보가 부족하거나, 현재 스킬 범위를 넘어서는 조치가 필요한 항목이다.
  예: 모델 artifact 자체를 찾지 못한 경우, 등록 대상 경로가 불명확한 경우, 인증 정보가 필요한데 제공 위치를 전혀 모르는 경우, 프로젝트 외부 시스템 정책 확인이 필요한 경우

## Guidance Rules

- 특정 파일명이 없다고 바로 실패로 단정하지 않는다.
- 사용자가 임의 이름의 entrypoint, 환경 파일, 설정 파일을 쓸 수 있다고 본다.
- 부족 항목은 "무엇이 없는가"보다 "무엇을 확인해야 하는가" 형태로 안내한다.
- 자동 생성, 자동 수정, 자동 등록처럼 읽히는 표현은 쓰지 않는다.
- 프로젝트 내부 파일과 외부 운영 환경 이슈를 구분해서 설명한다.

## Output

- 확인이 필요한 부족 항목 목록
- 각 항목의 분류: `safe`, `review_required`, `blocked`
- 사용자에게 물어봐야 할 질문
- 다음 단계로 넘길 수 있는 항목과 아직 넘기면 안 되는 항목
- 차단 사유와 필요한 추가 정보
- 다음 단계: `agent-mlflow-skill-run-model-guide`

## Safety

- 이 skill은 보완 안내만 수행한다.
- 파일 생성, 수정, 삭제를 직접 수행하지 않는다.
- 승인 없이 특정 구현 방식이나 파일 구조를 강제하지 않는다.
- 기존 사용자 파일을 덮어쓰는 방향은 항상 `review_required` 이상으로 본다.
