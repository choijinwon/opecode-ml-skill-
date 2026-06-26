---
name: agent-mlflow-skill-selected-run-test
description: Use when the user selects a target data model file and asks to copy data files to aiu_studio, reference runtest.py or run_test.py, and create runtest_2.py or another model-format-specific run test file.
license: MIT
compatibility: opencode
metadata:
  flow: ml-workspace-development
  stage: 03-train-model
  step: 3
---

# Selected Data Model Run Test

## When To Use

- 사용자가 특정 모델 파일을 선택해서 그 모델 기준 실행 파일을 만들고 싶다고 할 때
- `data/model.pkl` 같은 대상 모델 파일을 지정하고 `runtest_2.py`를 생성해 달라고 할 때
- 기존 `runtest.py` 또는 `run_test.py`와 같은 템플릿 구조를 유지하면서 다른 모델 형식용 실행 파일이 필요할 때
- 여러 모델 중 하나를 선택해 smoke test entrypoint를 분리해야 할 때

## Required Behavior

1. 사용자가 지정한 모델 프로젝트 폴더를 확인한다.
2. `<model-project-folder>/data/` 아래에 지원 모델 형식 파일이 있는지 확인한다.
3. 모델이 있으면 `data/` 안의 파일 전체를 프로젝트 루트의 `aiu_studio/` 폴더로 복사한다.
4. 대상 모델 파일이 반드시 `<model-project-folder>/data/` 아래에 있는지 확인한다.
5. 대상 모델 확장자를 기준으로 모델 형식을 판별한다.
6. 기존 `runtest.py`를 먼저 템플릿으로 사용하고, 없으면 `run_test.py`를 템플릿으로 사용한다.
7. 템플릿의 모델 경로와 모델 형식 상수를 대상 모델 기준으로 바꿔 `runtest_2.py`를 생성한다.
8. 출력 파일명은 사용자가 지정하면 그 값을 사용하고, 없으면 `runtest_2.py`를 기본값으로 사용한다.
9. 기존 출력 파일이 있으면 기본적으로 덮어쓰지 않는다.
10. 덮어쓰기를 사용자가 명시하면 `--force`를 사용한다.

## Command

기본 명령:

```text
python .opencode/scripts/ensure_run_test_entrypoints.py --project <model-project-folder> --target-model data/<model-file> --output runtest_2.py --execute
```

대상 모델을 `data/` 기준 파일명으로 줄 수도 있다.

```text
python .opencode/scripts/ensure_run_test_entrypoints.py --project <model-project-folder> --target-model <model-file> --output runtest_2.py --execute
```

템플릿을 명시할 수도 있다.

```text
python .opencode/scripts/ensure_run_test_entrypoints.py --project <model-project-folder> --target-model data/<model-file> --template runtest.py --output runtest_2.py --execute
```

덮어쓰기:

```text
python .opencode/scripts/ensure_run_test_entrypoints.py --project <model-project-folder> --target-model data/<model-file> --output runtest_2.py --execute --force
```

## Supported Model Suffixes

```text
.pkl
.joblib
.pt
.pth
.onnx
.h5
.keras
.bst
.ubj
.safetensors
```

## Output

- 선택된 프로젝트 경로
- 선택된 data 모델 파일 경로
- `aiu_studio/`로 복사된 파일 목록
- 판별된 모델 형식
- 생성된 실행 파일 경로
- 생성 여부 또는 skip 사유
- 다음 단계: 생성된 `runtest_2.py`를 `--load-only`로 실행

## Safety

- `data/` 밖의 모델 파일은 대상 모델로 사용하지 않는다.
- 기존 `runtest.py`와 `run_test.py`는 수정하지 않는다.
- 기존 `runtest_2.py`가 있으면 사용자가 명시적으로 덮어쓰기를 요청하기 전까지 보존한다.
- secret 값은 출력하지 않는다.
