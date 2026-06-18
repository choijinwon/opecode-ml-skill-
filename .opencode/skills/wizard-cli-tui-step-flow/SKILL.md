---
name: wizard-cli-tui-step-flow
description: 초급자 Wizard, CLI, TUI에서 모델 생성/선택/검증/등록 단계가 같은 상태 흐름을 쓰도록 정의한다.
license: MIT
compatibility: opencode
metadata:
  flow: model-test-scenario
  stage: 07-interface
  step: 1
---

# Wizard CLI TUI Step Flow

## When To Use

- 같은 기능을 Wizard, CLI, TUI에서 일관되게 보여줘야 할 때
- Step 1 모델 선택 화면과 Step 10 결과 화면을 설계할 때
- CLI 명령과 Wizard 상태를 연결해야 할 때

## Interface Commands

- `aiu sample list`
- `aiu sample create --kind tensorflow`
- `aiu sample create --kind large10`
- `aiu validate <project>`
- `aiu register <project> --dry-run`
- `aiu register <project>`

## Wizard Steps

- Step 1: sample/work 모델 목록 표시와 선택
- Step 2~5: scan, dependency, config, artifact, input example 검증
- Step 6: 보완 계획 승인
- Step 7~8: `--prepare-only` 준비 검증
- Step 9: MLflow 등록 실행 안내
- Step 10: 결과 리포트 표시

## Output

- interface별 command mapping
- 화면에 보여줄 상태 필드
- 다음 단계 버튼 또는 입력 명령
- 실패 시 복귀할 단계
