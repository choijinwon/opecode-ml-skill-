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
- 사용자가 지정한 모델 프로젝트 폴더에 모델 프로젝트가 없어서 `.opencode/samples` 아래 샘플 3개 중 하나를 선택해 루트로 복사해야 할 때

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

사용자가 지정한 모델 프로젝트 폴더에서 학습/추론 가능한 모델 프로젝트를 찾지 못하면 실패로 끝내지 않는다. 프로젝트 루트가 비어 있거나 `.opencode`만 있으면 `.opencode/samples` 아래 샘플 3개 중 하나를 사용자가 선택하게 하고, 선택한 샘플을 프로젝트 루트로 복사해 모델 생성과 테스트 흐름을 진행할 수 있게 한다.

### Selectable Samples

사용자가 선택할 수 있는 샘플은 아래 3개다.

```text
1. weather
   source: .opencode/samples/offline_weather_agent
   purpose: 기본 폴더 구조 기반 날씨 에이전트, Prompt/Trace/Session/Judge/Dataset 구조 확인

2. legal
   source: .opencode/samples/legal_agent_mlflow_aistudio
   purpose: 국가법령정보 API, 법률 질의응답, GenAI/MLflow/AI Studio endpoint 연결

3. design
   source: .opencode/samples/design_agent_mlflow_aistudio
   purpose: 소스 분석 기반 디자인 가이드 생성, GenAI/MLflow/AI Studio endpoint 연결
```

이 3개 외의 샘플은 임의로 선택하지 않는다.

선택형 샘플은 원본 폴더에 아래 기본 폴더가 있어야 한다.

```text
aiu_custom/
local_serving/
save_model/
```

아래 폴더는 사용자가 폐쇄망 모델을 직접 넣는 기본 슬롯이다. 내용이 비어 있으면 선택형 루트 복사 대상으로 사용하지 않는다.

```text
sklearn_sample/
pytorch_sample/
tensorflow_sample/
```

### Empty Project Root Rule

프로젝트 루트에 아래 항목만 있으면 비어 있는 프로젝트로 본다.

```text
.opencode/
.git/
.gitignore
.DS_Store
```

그 외 파일이나 폴더가 있으면 기존 작업물이 있다고 보고 루트 복사를 중단한다. 사용자가 명시적으로 덮어쓰기를 요청한 경우에만 `--force`를 사용한다.

### Selected Sample Handling

선택된 샘플은 원본을 직접 수정하지 않는다. 대상 프로젝트가 비어 있으면 샘플 내용을 사용자가 지정한 모델 프로젝트 루트로 복사한다.

```text
<model-project-folder>/aiu_custom/
<model-project-folder>/local_serving/
<model-project-folder>/save_model/
<model-project-folder>/run_model.py
<model-project-folder>/requirements.txt
<model-project-folder>/input_example.json
```

루트 복사에서는 실행에 필요하지 않은 생성 산출물을 제외한다.

```text
model/
saved_model/
artifacts/ai_studio/
.venv/
__pycache__/
mlruns/
mlartifacts/
mlflow.db
```

복사 후 아래 필수 폴더는 항상 루트에 있어야 한다. 샘플 원본에 없으면 빈 폴더로 생성한다.

```text
aiu_custom/
local_serving/
save_model/
```

복사는 `agent-mlflow-skill-sample-bootstrap` 스킬과 아래 스크립트를 기준으로 한다.

```text
python .opencode/scripts/bootstrap_sample_project.py --project <model-project-folder> --sample weather --execute
python .opencode/scripts/bootstrap_sample_project.py --project <model-project-folder> --sample legal --execute
python .opencode/scripts/bootstrap_sample_project.py --project <model-project-folder> --sample design --execute
```

샘플 선택 결과에는 반드시 다음을 포함한다.

```text
model_found: false
selected_sample
sample_source_path
target_project_root
copy_mode: root
required_dirs: aiu_custom, local_serving, save_model
next_action
```

## Output

- 선택된 프로젝트 경로
- 모델 프로젝트 발견 여부
- 모델이 있을 때 발견된 학습/추론/model artifact 경로
- 모델이 없을 때 사용자가 선택할 샘플 3개
- 선택된 샘플 원본 경로와 루트 복사 대상 경로
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
- 샘플을 루트로 복사해야 하면 사용자 선택을 먼저 받은 뒤 `agent-mlflow-skill-sample-bootstrap` 기준으로 처리한다.
- credential 값은 출력하지 않는다.
- framework가 불명확하면 `unknown/custom`으로 둔다.
