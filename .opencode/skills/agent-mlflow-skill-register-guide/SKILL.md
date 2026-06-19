---
name: agent-mlflow-skill-register-guide
description: 사용자 환경의 MLflow 등록 방식, 사전 확인 항목, 주의사항을 안내한다.
license: MIT
compatibility: opencode
metadata:
  flow: local-model-registration
  stage: 07-registration
  step: 7
---

# MLflow Registration Guidance

## When To Use

- 등록/실행 entrypoint의 등록 단계에 들어가기 전 확인 항목을 정리할 때
- local MLflow와 remote MLflow 등록 방식을 구분해야 할 때
- 등록 전에 확정해야 할 설정과 사용자 판단 항목을 안내해야 할 때

## Registration Scope

- 현재 프로젝트가 local MLflow를 전제로 하는지, remote MLflow를 전제로 하는지 확인한다.
- tracking URI 또는 tracking URL이 어디에서 관리되는지 확인한다.
- experiment name과 registered model name이 운영 규칙에 맞게 정해져 있는지 확인한다.

## Registration Checks

- 사용자 프로젝트의 환경 변수, 설정 파일, 배포 환경 변수 중 어디에 MLflow 설정이 있는지 확인한다.
- tracking target, artifact 위치, 모델 이름 규칙, experiment 규칙이 정해져 있는지 확인한다.
- remote MLflow를 쓰는 경우 인증 방식과 secret 주입 위치를 확인한다. 특정 env 파일명을 요구하지 않는다.
- 등록에 사용하는 entrypoint가 실제로 모델 로드, signature/input example, artifact 참조를 포함하는지 확인한다.
- local과 remote 중 어느 경로로 등록할지 사용자가 명확히 선택했는지 확인한다.

## Output

- registration mode: `local` 또는 `remote`
- tracking 설정 위치
- experiment name
- registered model name
- 등록 전에 확인할 항목 checklist
- 사용자에게 물어봐야 할 질문
- 다음 단계 또는 보류 사유

## Safety

- credential을 생성하거나 저장하지 않는다.
- secret 값을 출력하거나 노출하지 않는다.
- 등록 실행 자체를 이 skill의 기본 동작으로 가정하지 않는다.
- 명령 예시, 실행 순서, 실제 등록 수행은 사용자 운영 절차와 분리해서 다룬다.
