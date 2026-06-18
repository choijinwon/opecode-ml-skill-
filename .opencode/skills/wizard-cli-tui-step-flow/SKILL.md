---
name: wizard-cli-tui-step-flow
description: 초급자 Wizard, CLI, TUI에서 로컬 모델 선택/검증/등록 안내 단계가 같은 상태 흐름을 쓰도록 정의한다.
license: MIT
compatibility: opencode
metadata:
  flow: local-model-registration
  stage: 07-interface
  step: 1
---

# Wizard CLI TUI Step Flow

## When To Use

- 같은 로컬 모델 안내 기능을 Wizard, CLI, TUI에서 일관되게 보여줘야 할 때
- Step 1 모델 선택 화면과 단계 상태 표시를 설계할 때
- CLI 명령과 Wizard 상태를 연결해야 할 때

## Interface Commands

- `aiu analyze <project>`
- `aiu validate <project>`
- `aiu register <project> --dry-run`
- `aiu register <project>`

## Wizard Steps

- Step 1: 현재 프로젝트, 명시 경로, `work/` 로컬 모델 후보 표시와 선택
- Step 2~4: scan, dependency, config, artifact, input example 검증
- Step 5: 보완 안내와 승인 필요 항목 표시
- Step 6: `--prepare-only` 준비 검증 안내
- Step 7~8: MLflow 등록 실행 조건 안내
- Step 9: 다음 실행 명령 또는 보완 필요 항목 표시

## Output

- interface별 command mapping
- 화면에 보여줄 상태 필드
- 다음 단계 버튼 또는 입력 명령
- 실패 시 복귀할 단계
