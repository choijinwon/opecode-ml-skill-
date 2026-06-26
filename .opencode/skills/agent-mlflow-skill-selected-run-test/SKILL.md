---
name: agent-mlflow-skill-selected-run-test
description: Use when the user selects a target data model file and asks to copy the aiu_studio template folder, keep model files in data/**, reference runtest.py or run_test.py, then create runtest_2.py or another model-format-specific run test file.
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
- 사용자가 "선택된 모델 양식으로 변환", "`runtest.py` 참고", "`runtest_2.py` 새로 생성"처럼 요청할 때
- 직전 Project Analyze 결과에서 `model_found: true`와 `model_artifact_paths`가 표시된 뒤, 사용자가 `1`, `1번`, `첫 번째`, 모델 파일명, 모델 경로처럼 대상 모델을 선택했을 때

## Required Behavior

1. 사용자가 지정한 모델 프로젝트 폴더를 확인한다.
2. 직전 분석 결과의 `model_artifact_paths`가 있으면 사용자의 번호 선택을 해당 경로로 해석한다.
3. `<model-project-folder>/data/` 아래에 지원 모델 형식 파일이 있는지 확인한다.
4. 대상 모델 확장자를 기준으로 모델 형식을 판별한다.
5. `run_training.py --target-index/--target-model` 실행 시 아래 항목을 자동 처리한다.
6. 자동: `aiu_studio/` 실행 템플릿 폴더만 프로젝트 루트의 `aiu_studio/`로 복사한다.
7. 자동: 선택된 모델 파일은 `aiu_studio/`로 복사하지 않고 원래 위치인 `data/**`에서 직접 읽는다.
8. 자동: 기존 `runtest.py`를 먼저 템플릿으로 사용하고, 없으면 `run_test.py`를 템플릿으로 사용한다.
9. 자동: 템플릿의 모델 경로와 모델 형식 상수를 대상 모델 기준으로 바꾼다.
10. 자동: 기존 템플릿 파일은 수정하지 않고 새 파일 `runtest_2.py`를 생성한다.
11. 출력 파일명은 사용자가 지정하면 그 값을 사용하고, 없으면 `runtest_2.py`를 기본값으로 사용한다.
12. 기존 출력 파일이 있으면 기본적으로 덮어쓰지 않는다.
13. 사용자가 "새로 생성", "다시 생성", "변환 안됨", "덮어써"처럼 재생성을 요청하면 `--force`를 사용한다.

## Template Conversion Rules

`runtest.py` 또는 `run_test.py`에서 아래 상수명이 있으면 선택 모델 기준으로 치환한다.

```text
모델 원본 경로:
- DATA_MODEL_PATH
- SOURCE_MODEL_PATH

aiu_studio 실행 템플릿 폴더:
- AIU_STUDIO_DIR
- AI_STUDIO_DIR

실제 로드 경로:
- MODEL_PATH
- MODEL_FILE
- MODEL_FILE_PATH
- MODEL_ARTIFACT_PATH
- ARTIFACT_PATH
- TARGET_MODEL_PATH
- SELECTED_MODEL_PATH

모델 형식:
- MODEL_KIND
- MODEL_TYPE
- MODEL_FORMAT
- FRAMEWORK

모델 이름:
- MODEL_NAME
- MODEL_ID
```

템플릿에서 일부 상수만 찾으면 찾은 상수는 치환하고, 없는 `DATA_MODEL_PATH`, `AIU_STUDIO_DIR`, `MODEL_PATH`, `MODEL_KIND`, `MODEL_NAME`은 새 `runtest_2.py`에 보강한다.
템플릿에서 위 상수명을 전혀 찾지 못하면 템플릿을 억지로 수정하지 않고, 선택 모델 형식에 맞는 표준 `runtest_2.py`를 생성한다.

## Command

기본 명령:

```text
python .opencode/scripts/run_training.py --project <model-project-folder> --target-model data/<model-file> --output runtest_2.py --force
```

Project Analyze에서 표시된 모델 번호를 그대로 사용할 수도 있다.
이 명령은 선택 번호에 해당하는 모델을 찾고, 기존 `runtest.py` 또는 `run_test.py`를 참조해서 선택 모델 형식에 맞게 `runtest_2.py`를 생성한다.
또한 `aiu_studio/` 실행 템플릿 폴더를 프로젝트 루트로 복사한다. 모델 파일은 복사하지 않는다.

```text
python .opencode/scripts/run_training.py --project <model-project-folder> --target-index 1 --output runtest_2.py --force
```

대상 모델을 `data/` 기준 파일명으로 줄 수도 있다.

```text
python .opencode/scripts/run_training.py --project <model-project-folder> --target-model <model-file> --output runtest_2.py --force
```

템플릿을 명시할 수도 있다.

```text
python .opencode/scripts/run_training.py --project <model-project-folder> --target-model data/<model-file> --template runtest.py --output runtest_2.py --force
```

덮어쓰기:

```text
python .opencode/scripts/run_training.py --project <model-project-folder> --target-model data/<model-file> --output runtest_2.py --force
```

재생성 요청이 있으면 아래 명령을 우선 사용한다.

```text
python .opencode/scripts/run_training.py --project <model-project-folder> --target-model data/<model-file> --template runtest.py --output runtest_2.py --force
```

## Supported Model Suffixes

```text
sklearn/python: .pkl, .pickle, .sav, .joblib, .dill, .cloudpickle
PyTorch/HF:     .pt, .pth, .ckpt, .bin, .safetensors
ONNX:           .onnx, .ort
TensorFlow:     .h5, .hdf5, .keras, .pb, .tflite
Boosting:       .bst, .ubj, .xgb, .cbm, .lgb
Portable/LLM:   .pmml, .mlmodel, .gguf, .ggml, .mar, .nemo, .engine, .plan, .npz
```

## Output

- 선택된 프로젝트 경로
- 선택된 data 모델 파일 경로
- 복사된 `aiu_studio/` 실행 템플릿 폴더 경로
- `aiu_studio/`로 복사된 템플릿 파일 목록
- 모델 파일은 복사하지 않고 `data/**`에서 직접 읽는다는 안내
- 판별된 모델 형식
- 생성된 실행 파일 경로
- 생성 여부 또는 skip 사유
- 다음 단계: 생성된 `runtest_2.py`를 `--load-only`로 실행한 뒤 `agent-mlflow-skill-environment-check` 또는 `agent-mlflow-skill-inference-test`로 진행

## Safety

- `data/` 밖의 모델 파일은 대상 모델로 사용하지 않는다.
- 기존 `runtest.py`와 `run_test.py`는 수정하지 않는다.
- 기존 `runtest_2.py`가 있으면 사용자가 명시적으로 덮어쓰기를 요청하기 전까지 보존한다.
- `.pt`, `.pth`, `.ckpt`, `.bin`, `.safetensors` 모델은 실제 로드에 `torch` 또는 `safetensors`가 필요하다.
- 해당 dependency가 없는 폐쇄망 환경에서는 `runtest_2.py --load-only`가 dependency 필요 메시지를 출력하게 하고, 스킬 응답에서는 런타임 설치/활성화가 필요하다고 안내한다.
- `torch`가 설치되어 있어도 선택한 파일이 빈 파일, placeholder, 다른 형식이면 `load_error` 메시지로 안내하고 스크립트 자체는 종료되지 않게 한다.
- secret 값은 출력하지 않는다.
