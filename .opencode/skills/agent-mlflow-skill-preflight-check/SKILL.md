---
name: agent-mlflow-skill-preflight-check
description: 등록 전 사전 준비 검증 단계가 있는지 확인하고, 실행 전 점검 기준을 안내한다.
license: MIT
compatibility: opencode
metadata:
  flow: local-model-registration
  stage: 06-preflight-check
  step: 6
---

# Preflight Check Guidance

## When To Use

- MLflow 등록 실행 전 사전 준비 검증 기준을 설계할 때
- 등록/실행 entrypoint에 등록 전 점검 단계가 있는지 확인할 때
- artifact, config, input example을 실제 등록 전에 어떤 기준으로 확인할지 정해야 할 때

## Guidance Checks

- 등록 전에 artifact 경로 존재 여부를 확인할 수 있는 단계가 있는지 본다.
- 설정 파일이 있으면 parse 또는 읽기 검증이 가능한지 본다.
- input example이 있으면 parse 또는 읽기 검증이 가능한지 본다.
- wrapper 또는 entrypoint가 모델 준비 단계를 분리해서 점검할 수 있는지 본다.
- 출력 또는 작업 디렉터리 쓰기 가능 여부를 확인할 수 있는지 본다.
- Windows 경로와 공백 경로를 다룰 수 있는지 본다.
- 사전 준비 검증 단계가 remote MLflow 등록을 바로 수행하지 않는지 본다.

사전 준비 검증 단계의 형태는 프로젝트마다 다를 수 있다. 예를 들면 다음과 같다.

- 별도 옵션으로 모델 로드와 artifact 확인만 수행하는 모드
- 등록 함수 호출 전 입력 파일, 설정 파일, 경로만 확인하는 내부 preflight 단계
- 모델 wrapper 초기화만 수행하고 등록은 생략하는 smoke test 단계
- 실행 스크립트와 별도 검증 스크립트로 준비 상태만 확인하는 구조

## Output

- 등록 전 사전 준비 검증 단계 존재 여부 확인 기준
- 사용자 프로젝트에 맞춘 사전 점검 질문
- 등록 전 확인할 항목 checklist
- 실패 시 분류 기준
- 사용자 친화적 보완 안내 기준
- 다음 단계: `agent-mlflow-skill-register-guide`

## Safety

- 이 skill은 사전 준비 검증 단계를 직접 실행하지 않는다.
- OpenCode 챗봇 응답에서는 `python run_model.py --prepare-only` 같은 직접 실행 명령을 사용자에게 지시하지 않는다.
- 대신 entrypoint에 등록 전 사전 준비 검증 기능이 있는지, 그 기능이 artifact/config/input example/wrapper를 확인하는지 설명한다.
- 특정 옵션 이름을 전제하지 않고, 사용자가 확인해야 할 조건과 질문만 안내한다.
- 이 단계는 MLflow 원격 등록을 수행하도록 지시하지 않는다.
- 실제 실행 여부는 사용자와 프로젝트 운영 절차에 맡기고, 스킬은 안전한 경로 사용 필요성만 안내한다.
