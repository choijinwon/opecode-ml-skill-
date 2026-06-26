---
name: agent-mlflow-skill-environment-check
description: Use when the user asks "환경 검증", "dependency 확인", "MLflow 설치", "API key 위치", or environment check; verifies Python, dependencies, MLflow, env vars, and optional MLflow settings.
license: MIT
compatibility: opencode
metadata:
  flow: ml-workspace-development
  stage: 02-environment-check
  step: 2
---

# Execution Environment Check

## When To Use

- 프로젝트 구조 분석 후 실제 실행 가능성을 확인할 때
- Python, virtualenv, dependency, MLflow version을 확인해야 할 때
- 폐쇄망 또는 로컬 환경에서 외부 다운로드 없이 실행 준비 상태를 판단해야 할 때
- MLflow tracking URI, experiment 설정 위치를 확인해야 할 때
- 학습 모델 생성 전에 Python, dependency, MLflow 설치 상태를 확인해야 할 때

## Guidance Checks

- Python 실행 파일과 버전을 확인한다.
- virtualenv 또는 conda 환경 사용 여부를 확인한다.
- dependency 파일을 확인한다.
  - `requirements.txt`
  - `pyproject.toml`
  - `environment.yml`
- `requirements.txt`가 있으면 설치 명령을 계산한다.
- 사용자가 설치를 명확히 요청하면 `--install-requirements`로 `python -m pip install -r requirements.txt`를 실행한다.
- 핵심 dependency 설치 여부를 확인한다.
  - `mlflow`
  - framework dependency: `sklearn`, `torch`, `tensorflow`, `transformers`
- MLflow version을 확인한다.
- 환경 변수 설정 위치를 확인한다.
  - `MLFLOW_TRACKING_URI`
  - `MLFLOW_EXPERIMENT_NAME`
  - `MLFLOW_EXPERIMENT_ID`
- 환경변수와 선택 설정 파일 `config/mlflow_config.json` 상태를 확인한다.
- secret 값은 출력하지 않고 `set`, `empty`, `missing` 상태만 표시한다.
- 로컬/원격 MLflow 중 어떤 tracking target을 쓰는지 확인한다.
- 배포 오류 로그가 있으면 `--error-log`로 룰 기반 오류 가이드를 생성한다.
- 사용자가 Qwen 진단을 요청하면 `--qwen-diagnose`로 로컬 Qwen endpoint에 오류 요약을 요청한다.
  - `OPENAI_BASE_URL`
  - `OPENAI_API_KEY`
  - `OPENAI_MODEL`

## Output

- Python 환경 요약
- dependency 파일 존재 여부
- `requirements.txt` 설치 명령 및 실행 여부
- 설치된 핵심 dependency와 version
- MLflow 설치/version 상태
- 환경 변수 설정 상태
- 선택 MLflow 설정 상태
- 로컬/원격 tracking target 판단
- 배포 오류 분류와 조치 가이드
- Qwen 진단 상태 및 요약
- 실행 전 차단 항목
- 다음 단계: `agent-mlflow-skill-train-model`

## Failure Classification

- `missing_dependency`: 필요한 패키지가 없음
- `version_mismatch`: 설치 버전이 기대 범위와 다름
- `optional_config_missing`: 선택 MLflow 설정이 없음. 필수 실패로 보지 않는다.
- `config_error`: 설정 파일은 있으나 읽거나 해석할 수 없음
- `tracking_unreachable`: MLflow tracking server에 접근할 수 없음
- `missing_python_package`: Python 패키지 누락
- `mlflow_file_store_policy`: MLflow 3.x file store 정책 오류
- `auth_or_permission_error`: 인증 또는 권한 문제
- `network_or_tracking_unreachable`: endpoint, tracking server, DNS, 방화벽 문제
- `file_not_found`: 모델 또는 설정 파일 경로 문제

## Safety

- secret 값을 로그나 응답에 포함하지 않는다.
- 외부 패키지 설치는 사용자가 명확히 요청한 경우에만 `--install-requirements`로 수행한다.
- Qwen 진단은 사용자가 명확히 요청한 경우에만 `--qwen-diagnose`로 수행한다.
- 폐쇄망에서는 내부 패키지 저장소 정책을 우선 확인해야 한다.
