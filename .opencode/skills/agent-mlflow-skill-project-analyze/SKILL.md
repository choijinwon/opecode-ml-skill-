---
name: agent-mlflow-skill-project-analyze
description: 사용자가 지정한 모델 프로젝트 폴더의 ML 프로젝트 구조를 분석하고 framework, entrypoint, artifact, config, input example, aiu_custom 구성 여부를 정리한다.
license: MIT
compatibility: opencode
metadata:
  flow: ml-workspace-development
  stage: 01-project-analyze
  step: 1
---

# Project Structure Analysis

## When To Use

- 사용자가 지정한 모델 프로젝트 폴더의 ML 프로젝트 구조를 분석해 달라고 요청할 때
- 학습, 추론, MLflow 등록 전에 어떤 파일이 있는지 확인해야 할 때
- 프로젝트가 sklearn, PyTorch, TensorFlow, HuggingFace, custom pyfunc 중 무엇에 가까운지 판단해야 할 때
- `aiu_custom`, `local_serving`, `save_model`, `run_model.py`, `input_example.json` 같은 구성 요소가 필요한지 확인해야 할 때
- 사용자가 지정한 모델 프로젝트 폴더에 모델 프로젝트가 없어서 `.opencode/samples` 아래 샘플 모델을 자동 선택해야 할 때

## Guidance Checks

- 현재 작업 경로와 사용자가 지정한 프로젝트 경로를 확인한다.
- 핵심 파일 존재 여부를 확인한다.
  - `requirements.txt`, `pyproject.toml`, `environment.yml`
  - `train.py`, `app.py`, `main.py`, `run_model.py`
  - `config.json`, `.env.example`, `input_example.json`
  - `aiu_custom/`, `aiu_custom/model_wrapper.py`, `aiu_custom/predict.py`
  - `local_serving/`
  - `save_model/`
  - `artifacts/`, `model/`, `mlruns/`, `mlartifacts/`
- framework 후보를 근거와 함께 분류한다.
  - sklearn: `sklearn`, `.pkl`, `.joblib`, `.fit()`
  - PyTorch: `torch`, `.pt`, `.pth`, `state_dict`
  - TensorFlow/Keras: `tensorflow`, `keras`, `.h5`, `.keras`, `saved_model.pb`
  - HuggingFace: `transformers`, tokenizer files, `model.safetensors`
  - Custom pyfunc: `mlflow.pyfunc.PythonModel`, `aiu_custom`, `ModelWrapper`
- 모델 artifact 후보와 생성 위치를 확인한다.
- 학습 entrypoint와 추론 entrypoint를 분리해서 표시한다.
- 누락 항목은 실패로 단정하지 않고 다음 단계에서 확인할 항목으로 분류한다.

## Model Found Flow

사용자가 지정한 모델 프로젝트 폴더에서 학습/추론 가능한 모델 프로젝트가 발견되면 샘플을 선택하지 않는다. 발견된 프로젝트를 기준으로 분석 결과를 만들고, 이후 단계에서 해당 프로젝트를 직접 실행한다.

모델 프로젝트가 있다고 판단하는 기준은 다음 중 하나 이상이다.

```text
학습 entrypoint 존재: train.py, scripts/train.py
실행/등록 entrypoint 존재: run_model.py
추론 entrypoint 존재: predict.py, app.py, main.py
필수 폴더 존재: aiu_custom/, local_serving/, save_model/
모델 wrapper 존재: aiu_custom/model_wrapper.py, aiu_custom/predict.py
모델 artifact 존재: save_model/, model/, artifacts/, saved_model/, .pkl, .joblib, .pt, .pth, .h5, .keras
MLflow model 존재: MLmodel, python_model.pkl
input example 존재: input_example.json
```

모델이 발견된 경우 출력에는 반드시 다음을 포함한다.

```text
model_found: true
selected_project_path
framework
train_entrypoint
inference_entrypoint
model_artifact_path
input_example_path
next_action: 발견된 프로젝트로 Step 2 환경 검증 후 Step 3 실행
```

모델이 발견되면 `.opencode/samples`는 참조하지 않는다.

## No Model Found Fallback

사용자가 지정한 모델 프로젝트 폴더에서 학습/추론 가능한 모델 프로젝트를 찾지 못하면 실패로 끝내지 않는다. `.opencode/samples` 아래 샘플 모델 후보를 자동으로 선택해 해당 모델 프로젝트 폴더를 대상으로 모델 생성과 테스트 흐름을 진행할 수 있게 한다.

### Standard Sample Priority

샘플이 여러 개 있으면 아래 순서로 자동 선택한다.

```text
1. sklearn_sample
2. pytorch_sample
3. tensorflow_sample
```

이 3개는 ML 개발자에게 가장 일반적인 학습 흐름을 제공하는 표준 샘플 후보로 본다.

표준 3개 샘플이 모두 없으면 다른 샘플을 임의로 선택하지 않는다. 이 경우 `sample_not_found`로 분류하고, `sklearn_sample`, `pytorch_sample`, `tensorflow_sample` 중 어떤 샘플을 추가해야 하는지 안내한다.

### Selected Sample Handling

자동 선택된 샘플은 원본을 직접 덮어쓰지 않는다. 사용자가 지정한 모델 프로젝트 폴더에서 사용할 작업 경로를 따로 정한다.

권장 작업 경로 예시는 다음과 같다.

```text
<model-project-folder>/work/<selected-sample-name>
```

이미 같은 경로가 있으면 덮어쓰기 전에 사용자 확인이 필요하다.

자동 선택 결과에는 반드시 다음을 포함한다.

```text
model_found: false
selected_sample
selection_reason
sample_source_path
recommended_workspace_path
next_action
```

## Output

- 선택된 프로젝트 경로
- 모델 프로젝트 발견 여부
- 모델이 있을 때 발견된 학습/추론/model artifact 경로
- 모델이 없을 때 자동 선택된 샘플과 선택 근거
- 샘플 원본 경로와 권장 작업 경로
- 발견된 핵심 파일 목록
- 누락되었거나 확인 필요한 파일 목록
- framework 후보와 판단 근거
- 학습 entrypoint 후보
- 추론 entrypoint 후보
- 모델 artifact 후보
- `aiu_custom` 필요 여부
- 필수 폴더 존재 여부: `aiu_custom/`, `local_serving/`, `save_model/`
- 다음 단계: `agent-mlflow-skill-environment-check`

## Safety

- 이 단계에서는 파일을 수정하지 않는다.
- 모델 artifact를 이동하거나 복사하지 않는다.
- 샘플 원본 디렉터리를 직접 덮어쓰지 않는다.
- 샘플을 사용자가 지정한 모델 프로젝트 폴더 작업 경로로 복사하거나 생성해야 하면 사용자 요청 또는 후속 실행 단계에서 처리한다.
- credential 값은 출력하지 않는다.
- framework가 불명확하면 `unknown/custom`으로 둔다.
