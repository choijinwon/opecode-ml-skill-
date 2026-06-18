---
name: run-model-template-planning
description: MLflow 등록 테스트용 run_model.py 템플릿의 옵션, 책임, 검증 동작을 정의한다.
license: MIT
compatibility: opencode
metadata:
  flow: model-test-scenario
  stage: 04-gap-fill
  step: 6
---

# Run Model Template Planning

## When To Use

- `run_model.py` 생성 또는 보강 기능을 설계할 때
- `--prepare-only`, `--register`, `--env-file`, `--config`, `--model` 옵션 의미를 정의할 때
- 모델별 wrapper 차이는 숨기고 공통 등록 흐름을 제공해야 할 때

## Required CLI Options

- `--prepare-only`: artifact와 config를 읽고 등록 전 준비만 검증한다.
- `--register`: MLflow logging/register를 실행한다.
- `--env-file`: `ai_studio.env` 같은 환경 파일을 읽는다.
- `--config`: `config.json` 경로를 받는다.
- `--model`: model artifact 경로를 명시한다.

## Runtime Responsibilities

- Windows 경로와 공백이 있는 경로를 처리한다.
- local file store fallback을 지원한다.
- `mlflow.pyfunc.log_model(...)`과 `registered_model_name` 사용 흐름을 갖는다.
- 원격 설정이 비어 있으면 친절한 local mode 안내를 출력한다.

## Output

- 템플릿 기능 목록
- 옵션별 expected behavior
- framework별 wrapper 필요 여부
- 다음 단계: `prepare-only-validation`
