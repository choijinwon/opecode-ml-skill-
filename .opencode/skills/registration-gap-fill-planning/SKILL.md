---
name: registration-gap-fill-planning
description: MLflow 등록에 부족한 파일과 설정을 보완 안내 대상으로 분류한다.
license: MIT
compatibility: opencode
metadata:
  flow: local-model-registration
  stage: 04-gap-guidance
  step: 4
---

# Registration Gap Fill Planning

## When To Use

- 검증 결과 누락 파일이 발견되었고, 보완 안내 계획만 만들어야 할 때
- 사용자에게 추가/수정 후보를 보여줘야 할 때
- 위험한 자동 수정과 안전한 scaffold 안내를 분리해야 할 때

## Classifications

- safe: `config.json`, `ai_studio.env.example`, `input_example.json`, wrapper scaffold 추가 안내
- review_required: `requirements.txt`, `run_model.py`, serving wrapper 수정
- blocked: credential 직접 삽입, 기존 artifact 삭제, 프로젝트 외부 수정

## Output

- 추가가 필요한 파일 목록
- 수정할 파일 목록
- 사용자의 승인이 필요한 항목
- 차단된 항목과 이유
- 다음 단계: `run-model-template-planning`

## Safety

- 이 skill은 안내 계획만 작성한다.
- 승인 없이 파일 변경을 지시하지 않는다.
- 기존 사용자 파일을 덮어쓰는 계획은 별도 review_required로 표시한다.
