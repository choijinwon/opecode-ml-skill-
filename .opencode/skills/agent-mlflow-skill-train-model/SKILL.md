---
name: agent-mlflow-skill-train-model
description: Use when the user asks "학습 실행", "모델 생성", "프로젝트 진입점", "save_model 확인", "data 모델 파일", or train model; checks local training entrypoint, data model files, config, and input example.
license: MIT
compatibility: opencode
metadata:
  flow: ml-workspace-development
  stage: 03-train-model
  step: 3
---

# Local Training And Model Creation

## When To Use

- 실행 환경 검증 후 로컬 학습을 실행하거나 학습 가능 여부를 확인할 때
- 학습 결과로 모델 파일이 생성되는지 확인해야 할 때
- `train.py`, notebook, `프로젝트 진입점 --prepare-only`, custom training script 중 실제 학습 entrypoint를 판단해야 할 때
- 학습 산출물이 MLflow 등록이나 추론 테스트에 충분한지 확인해야 할 때
- Step 0에서 사용자가 선택한 샘플 폴더가 워크스페이스로 복사된 뒤 모델을 생성해야 할 때

## Guidance Checks

- Step 1에서 `model_found: true`이면 발견된 기존 프로젝트를 그대로 실행 대상으로 사용한다.
- 기존 프로젝트가 있으면 샘플을 준비하거나 복사하지 않는다.
- Step 1에서 `model_found: false`이면 먼저 `agent-mlflow-skill-sample-bootstrap`으로 샘플 폴더를 워크스페이스에 복사해야 한다.
- Step 0에서 복사된 샘플 폴더를 실행 대상으로 사용한다.
- 이 단계에서는 샘플 원본을 복사하지 않는다.
- 학습 entrypoint 후보를 확인한다.
  - `train.py`
  - `scripts/train.py`
  - `프로젝트 진입점`
  - `run_test.py`, `run_test2.py`
  - framework별 학습 스크립트
- `data/` 폴더 안에 모델 형식 파일이 있으면 `data/` 안의 파일 전체를 프로젝트 루트의 `aiu_studio/` 폴더로 복사한다.
- `data/` 폴더 안에 모델 형식 파일은 있는데 필수 구조나 실행 파일이 없으면 제공된 템플릿으로 필수 파일과 `run_test.py`를 생성한다.
  - `data/` 안의 모델 파일이 1개이면 `run_test.py`
  - 다른 모델 파일이 추가로 있으면 `run_test2.py`, `run_test3.py` 순서로 생성한다.
  - 모델 확장자에 따라 sklearn/joblib, PyTorch, ONNX, TensorFlow/Keras, XGBoost, safetensors 로더를 사용한다.
- 사용자가 대상 모델을 직접 선택하면 `agent-mlflow-skill-selected-run-test` 기준으로 선택 모델 전용 실행 파일을 생성한다.
  - 기본 출력 파일명은 `runtest_2.py`
  - 기존 `runtest.py` 또는 `run_test.py`를 템플릿으로 참고한다.
  - 기존 `runtest.py`와 `run_test.py`는 수정하지 않는다.
  - 선택한 모델 파일은 반드시 `data/` 아래에 있어야 한다.
- 학습 전에 필요한 입력 파일을 확인한다.
  - dataset 경로
  - config 파일
  - 환경변수 또는 `config/mlflow_config.json`
  - pretrained/model base 경로
  - output directory
- 필요한 환경변수 또는 선택 MLflow 설정을 확인한다.
  - `mlflow_tracking_url`
  - `mlflow_tracking_username`
  - `mlflow_tracking_password`
  - `mlflow_experiment_name`
  - `mlflow_register_model_name`
- 학습 실행이 가능한 모드인지 확인한다.
  - 실제 학습
  - dry run
  - prepare-only
  - smoke test
- 학습 후 생성되어야 하는 파일을 확인한다.
  - data model file
  - tokenizer/preprocessor
  - config
  - input example
  - metrics/log file
- 생성된 모델 파일의 위치와 크기를 확인한다.
- 모델 파일이 빈 파일이거나 placeholder인지 확인한다.

## Existing Model Execution

사용자가 지정한 모델 프로젝트 폴더에 모델 프로젝트가 존재하는 경우, 이 단계의 책임은 기존 프로젝트를 기준으로 학습 또는 모델 생성 entrypoint를 실행하고 산출물을 확인하는 것이다.

### Required Behavior

```text
1. Step 1의 selected_project_path를 실행 기준 경로로 사용한다.
2. train_entrypoint, 프로젝트 진입점, run_test.py 계열 파일을 확인한다.
3. 필요한 config/input/dataset/model path를 확인한다.
4. prepare-only, dry run, smoke test가 있으면 먼저 실행한다.
5. 필요한 환경변수 또는 선택 MLflow 설정이 준비되었는지 확인한다.
6. 실제 학습 또는 모델 export를 실행한다.
7. 기존 모델 파일을 덮어쓸 가능성이 있으면 사용자 확인을 받는다.
8. 생성 또는 갱신된 data/ 또는 save_model/ 경로를 확인한다.
9. Step 4 추론 테스트에 사용할 model path와 input example을 넘긴다.
```

기존 모델 프로젝트가 있으면 `.opencode/samples`의 선택형 샘플은 사용하지 않는다.

### Missing Required Files With Existing Data Model

`data/` 폴더 안에 모델 파일은 있는데 `aiu_custom/`, `local_serving/`, `save_model/`, `aiu_studio/`, 실행 파일이 없으면 실패로만 끝내지 않는다.
모델 파일은 `aiu_studio/`로 복사하지 않고 `data/**` 원본 경로에서 직접 읽는다.
아래 스크립트로 필수 구조와 모델 형식에 맞는 smoke test entrypoint를 생성한다.

```text
python .opencode/scripts/run_training.py --project <model-project-folder>
```

```text
python .opencode/scripts/run_training.py --project <model-project-folder>
```

생성 규칙:

```text
data/ 안의 첫 번째 모델 파일 -> run_test.py
data/ 안의 두 번째 모델 파일 -> run_test2.py
data/ 안의 세 번째 모델 파일 -> run_test3.py
```

지원 모델 확장자:

```text
sklearn/python: .pkl, .pickle, .sav, .joblib, .dill, .cloudpickle
PyTorch/HF:     .pt, .pth, .ckpt, .bin, .safetensors
ONNX:           .onnx, .ort
TensorFlow:     .h5, .hdf5, .keras, .pb, .tflite
Boosting:       .bst, .ubj, .xgb, .cbm, .lgb
Portable/LLM:   .pmml, .mlmodel, .gguf, .ggml, .mar, .nemo, .engine, .plan, .npz
```

### Selected Data Model Run Test

사용자가 특정 대상 모델을 선택하면 전체 자동 생성 순서와 별개로 선택 모델 전용 실행 파일을 만든다.
이때 `aiu_studio/` 실행 템플릿 폴더만 복사하고, 기존 `runtest.py` 또는 `run_test.py`를 참고해 `runtest_2.py`를 생성한다.
기존 `runtest.py`는 수정하지 않는다. 선택 모델의 경로와 모델 형식으로 변환된 결과는 반드시 새 파일 `runtest_2.py`로 생성한다.
이미 `runtest_2.py`가 있고 사용자가 재생성을 요청하면 `--force`를 사용한다.

```text
python .opencode/scripts/run_training.py --project <model-project-folder> --target-model data/<model-file> --output runtest_2.py --force
```

예시:

```text
python .opencode/scripts/run_training.py --project <model-project-folder> --target-model data/model.onnx --template runtest.py --output runtest_2.py --force
```

이 흐름은 `agent-mlflow-skill-selected-run-test`를 우선 사용한다.

## Sample-Based Model Creation

사용자가 지정한 모델 프로젝트 폴더에 모델이 없어 Step 0에서 선택형 샘플 폴더가 복사된 경우, 이 단계의 책임은 복사된 샘플 폴더에서 모델 파일을 생성하는 것이다.

### Required Behavior

```text
1. selected_sample 값을 확인한다. 허용값은 sklearn, pytorch, tensorflow이다.
2. target_project_path를 확인한다.
3. 복사된 샘플 폴더에 aiu_custom/, local_serving/, save_model/이 있는지 확인한다.
4. requirements/config/input_example을 확인한다.
5. 필요한 환경변수 또는 선택 MLflow 설정이 준비되었는지 확인한다.
6. prepare-only 또는 smoke test가 있으면 먼저 실행 가능성을 검증한다.
7. 로컬 학습 또는 로컬 모델 export를 실행한다.
8. 생성된 data/ 또는 save_model/ 경로를 확인한다.
9. 다음 단계의 inference-test에서 사용할 input example과 model path를 넘긴다.
```

### Sample Selection Assumptions

선택형 샘플은 아래 3개다.

```text
sklearn    -> .opencode/samples/sklearn_sample
pytorch    -> .opencode/samples/pytorch_sample
tensorflow -> .opencode/samples/tensorflow_sample
```

선택형 샘플 폴더가 복사되지 않았으면 이 단계에서 임의로 복사하지 않는다. `sample_bootstrap_required`로 분류하고 Step 0으로 돌아가 사용자의 샘플 선택을 받는다.

### Expected Outputs From Sample

샘플 기반 생성 후 최소한 아래 중 하나는 있어야 한다.

```text
aiu_custom/
local_serving/
save_model/
aiu_studio/
model/
artifacts/
saved_model/
MLmodel
python_model.pkl
framework native model file
input_example.json
```

## Output

- 선택된 학습 entrypoint
- 기존 모델 프로젝트 실행 여부
- 샘플 기반 생성 여부
- 선택된 샘플 이름과 작업 경로
- 학습 실행 방식
- 필요한 입력 파일 목록
- 생성된 data 모델 파일 목록
- 생성된 필수 파일 목록
- 생성된 run_test.py 계열 실행 파일 목록
- 생성되지 않은 필수 산출물
- 학습 로그 요약
- 다음 단계: `agent-mlflow-skill-inference-test`

## Failure Classification

- `missing_train_entrypoint`: 학습/실행 스크립트를 찾을 수 없고 run_test.py 자동 생성도 불가함
- `sample_not_found`: 선택된 샘플 원본을 찾을 수 없음
- `sample_bootstrap_required`: 샘플 폴더가 아직 워크스페이스로 복사되지 않음
- `missing_dataset`: 학습 데이터 또는 입력 파일이 없음
- `missing_config`: 학습 설정 파일이 없음
- `optional_config_missing`: 선택 MLflow 설정이 없음. 필수 실패로 보지 않는다.
- `runtime_error`: 학습 실행 중 예외 발생
- `data_model_file_not_created`: 학습은 끝났지만 모델 파일이 생성되지 않음
- `data_model_file_invalid`: 생성 파일이 비어 있거나 로드 불가함

## Safety

- 오래 걸리는 학습은 사용자에게 예상 비용과 시간을 먼저 설명한다.
- 기존 모델 파일을 덮어쓸 수 있으면 실행 전 경로를 명확히 확인한다.
- 샘플 원본을 직접 수정하지 않고 복사된 샘플 폴더에서 실행한다.
- 원격 학습이나 외부 데이터 다운로드는 기본 동작으로 가정하지 않는다.
