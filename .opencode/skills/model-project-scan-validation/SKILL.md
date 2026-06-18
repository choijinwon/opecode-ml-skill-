---
name: model-project-scan-validation
description: 선택된 모델 프로젝트의 entrypoint, artifact, config, input example, requirements를 읽기 전용으로 스캔한다.
license: MIT
compatibility: opencode
metadata:
  flow: local-model-registration
  stage: 03-validation
  step: 2
---

# Model Project Scan Validation

## When To Use

- Step 2~5에서 선택된 프로젝트가 등록 가능한 구조인지 확인할 때
- 학습 entrypoint, 모델 artifact, 환경 파일, 입력 예제를 찾을 때
- 수정 전 read-only 상태 보고서를 만들어야 할 때

## Checklist

- `requirements.txt` 존재 여부
- `train.py` 또는 추론 entrypoint 존재 여부
- `run_model.py` 존재 여부
- `config.json` 존재 여부
- `ai_studio.env` 존재 여부
- `input_example.json` 존재 여부
- model artifact 경로와 크기
- framework 추정 결과

## Output

- pass/warn/block 판정
- 발견된 파일 목록
- 누락 파일 목록
- framework와 artifact 요약
- 다음 단계: `mlflow-readiness-validation`

## Safety

- 이 단계에서는 파일을 수정하지 않는다.
- credential 값은 출력하지 않고 key 이름만 표시한다.
