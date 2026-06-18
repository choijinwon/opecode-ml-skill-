---
name: registration-result-reporting
description: Step 10에서 샘플 생성, 검증, prepare-only, MLflow 등록 결과를 표 형태로 요약한다.
license: MIT
compatibility: opencode
metadata:
  flow: model-test-scenario
  stage: 08-reporting
  step: 10
---

# Registration Result Reporting

## When To Use

- Step 10 최종 리포트를 만들어야 할 때
- Wizard/TUI/CLI 출력에 같은 결과 요약을 써야 할 때
- 성공, 경고, 차단 항목과 다음 조치를 분리해야 할 때

## Report Fields

- selected project
- framework
- artifact size
- required files status
- MLflow dependency status
- prepare-only result
- registration mode: local or remote
- run id or local run path
- registered model name
- next action

## Output

- compact result table
- pass/warn/block summary
- user-friendly next steps
- commands used
- masked error summary when failed

## Safety

- secret 값을 표에 넣지 않는다.
- 대형 로그 전문 대신 핵심 원인과 재현 명령만 표시한다.
