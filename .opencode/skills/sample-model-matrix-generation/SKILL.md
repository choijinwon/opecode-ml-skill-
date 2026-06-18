---
name: sample-model-matrix-generation
description: 폐쇄망 테스트용 10개 샘플 모델 프리셋과 생성 산출물 matrix를 정의한다.
license: MIT
compatibility: opencode
metadata:
  flow: model-test-scenario
  stage: 01-sample-generation
  step: 1
---

# Sample Model Matrix Generation

## When To Use

- `/sample all`, `/sample large10`, `/sample tensorflow`, `/sample pytorch` 같은 샘플 생성 명령을 설계할 때
- 외부 다운로드 없이 dummy artifact 기반 샘플 모델 세트를 정의해야 할 때
- 샘플별 필수 파일 목록과 테스트 목적을 정리해야 할 때

## Model Presets

- TensorFlow 스타일 샘플
- PyTorch 스타일 샘플
- scikit-learn 스타일 샘플
- ONNX 스타일 샘플
- XGBoost 스타일 샘플
- HuggingFace 스타일 샘플
- Sora 오류 재현 샘플
- 대형 artifact 샘플
- 최소 pyfunc wrapper 샘플
- 등록 실패/복구 테스트 샘플

## Required Artifacts Per Sample

- `requirements.txt`
- `train.py`
- model artifact directory or dummy model file
- `config.json`
- `ai_studio.env`
- `input_example.json`
- `run_model.py`

## Output

- 샘플 kind 목록
- 생성 위치: `.aiu/sample_projects/<sample-name>/`
- 각 샘플의 framework, artifact size, expected command
- Windows 권한 보정 필요 여부

## Safety

- 실제 모델 다운로드를 요구하지 않는다.
- dummy artifact는 작고 재생성 가능해야 한다.
- 대형 artifact 샘플도 테스트용 placeholder 또는 로컬 생성 파일로 제한한다.
