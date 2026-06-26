---
name: agent-mlflow-skill-project-analyze
description: Use when the user asks "분석해줘", "MLflow 5단계", "모델 있음/없음", "워크스페이스 분석", or project structure analysis; analyzes framework, entrypoint, data model files, config, input example, aiu_custom/local_serving/save_model/aiu_studio.
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
- `aiu_custom`, `local_serving`, `save_model`, `aiu_studio`, `프로젝트 진입점`, `input_example.json` 같은 구성 요소가 필요한지 확인해야 할 때
- 사용자가 지정한 모델 프로젝트 폴더에 모델 프로젝트가 없어서 `.opencode/samples` 아래 샘플 3개 중 하나를 선택해 폴더째 복사해야 할 때

## Guidance Checks

- 현재 작업 경로와 사용자가 지정한 프로젝트 경로를 확인한다.
- 사용자가 가져온 모델 파일은 프로젝트 루트의 `data/` 하위 트리 안에 두는 것이 기본 계약임을 안내한다.
- 폐쇄망에 모델이 있다고 사용자가 말하면, 현재 워크스페이스에서 보이지 않는 모델을 `model_found: true`로 추정하지 않는다.
- 이 경우 실제 모델 프로젝트 경로를 지정하게 하거나, 폐쇄망 모델 파일을 `<model-project-folder>/data/**` 아래로 반입한 뒤 재분석하도록 안내한다.
- 사용자가 루트 경로를 지정했으면, 루트의 `data/**` 트리 안에 모델 형식 파일이 있는지 먼저 찾는다.
  - 예: `<root>/data/model.pkl`, `<root>/data/model.pt`, `<root>/data/model.onnx`, `<root>/data/model.gguf`
- 핵심 파일 존재 여부를 확인한다.
  - `requirements.txt`, `pyproject.toml`, `environment.yml`
  - `train.py`, `app.py`, `main.py`, `프로젝트 진입점`
  - `config.json`, `.env.example`, `input_example.json`
  - `aiu_custom/`, `aiu_custom/model_wrapper.py`, `aiu_custom/predict.py`
  - `local_serving/`
  - `save_model/`
  - `aiu_studio/`
  - `data/` 안의 모델 형식 파일
  - `MLflow 로컬 실행 산출물`, `mlartifacts/`
- framework 후보를 근거와 함께 분류한다.
  - sklearn: `sklearn`, `.pkl`, `.joblib`, `.fit()`
  - PyTorch: `torch`, `.pt`, `.pth`, `state_dict`
  - TensorFlow/Keras: `tensorflow`, `keras`, `.h5`, `.keras`, `saved_model.pb`
  - HuggingFace: `transformers`, tokenizer files, `model.safetensors`
  - Custom pyfunc: `mlflow.pyfunc.PythonModel`, `aiu_custom`, `ModelWrapper`
- `data/` 안의 모델 파일 후보와 생성 위치를 확인한다.
- `aiu_studio/` 폴더는 폐쇄망 AI Studio 반입 대상이므로 존재 여부를 명확히 표시한다.
- `aiu_studio/`가 이미 있으면 이후 실행 단계에서 삭제하지 않고 보존/병합 복사해야 한다.
- 학습 entrypoint와 추론 entrypoint를 분리해서 표시한다.
- 누락 항목은 실패로 단정하지 않고 다음 단계에서 확인할 항목으로 분류한다.

## Initial Workspace Guide

사용자가 아래처럼 넓게 요청하면, 바로 샘플 선택부터 묻지 말고 먼저 워크스페이스를 분석한다.

```text
이 워크스페이스 분석해줘
현재 프로젝트 봐줘
MLflow 5단계로 봐줘
모델 있으면 진행하고 없으면 샘플로 시작해줘
```

첫 응답 흐름은 아래 순서를 따른다.

```text
1. 현재 워크스페이스 경로를 확인한다.
2. 루트 및 하위 프로젝트의 `data/**` 트리에서 모델 형식 파일을 찾고, 실행 entrypoint와 필수 폴더를 확인한다.
3. model_found 값을 먼저 결정한다.
4. model_found: true이면 `model_artifact_paths` 목록을 먼저 보여주고 사용자가 모델을 선택하게 한다.
   - 모델이 1개뿐이면 기본 선택값으로 제안하되, 다음 실행 단계는 `agent-mlflow-skill-selected-run-test`로 이어진다고 안내한다.
   - 모델이 여러 개이면 번호 또는 경로 선택을 요청한다.
   - 사용자가 번호나 경로를 선택하면 프로젝트 분석을 반복하지 않고 `agent-mlflow-skill-selected-run-test`로 진행한다.
5. model_found: false이면 먼저 현재 분석 경로에 `data/**` 모델이 없음을 설명한다.
   - 사용자가 폐쇄망에 모델이 있다고 말한 상황이면 샘플 선택보다 실제 모델 프로젝트 경로 지정 또는 `data/**` 반입을 우선 안내한다.
   - 사용자가 샘플로 시작하겠다고 선택한 경우에만 sklearn/pytorch/tensorflow 선택 가이드를 출력한다.
```

`data_model_files`가 1개 이상이면 `model_found`는 반드시 true로 판단한다.
필수 폴더나 선택 MLflow 설정이 누락되어도 모델 없음으로 바꾸지 않는다.
누락 항목은 별도 block/warn 항목으로만 분류한다.

초기 분석 응답은 아래 구조를 사용한다. 문장은 자연스럽게 바꿔도 되지만 순서는 유지한다.

```text
워크스페이스를 먼저 분석했습니다.

확인 기준:
- 프로젝트 진입점, train.py, predict.py
- aiu_custom/
- local_serving/
- save_model/
- aiu_studio/
- data/
- input_example.json
- sklearn/python: data/*.pkl, data/*.pickle, data/*.sav, data/*.joblib, data/*.dill, data/*.cloudpickle
- PyTorch/HF: data/*.pt, data/*.pth, data/*.ckpt, data/*.bin, data/*.safetensors
- ONNX/TensorFlow: data/*.onnx, data/*.ort, data/*.h5, data/*.hdf5, data/*.keras, data/*.pb, data/*.tflite
- Boosting/portable/LLM: data/*.bst, data/*.ubj, data/*.xgb, data/*.cbm, data/*.lgb, data/*.pmml, data/*.mlmodel, data/*.gguf, data/*.ggml, data/*.mar, data/*.nemo, data/*.engine, data/*.plan, data/*.npz

분석 결과:
- model_found: true | false
- 발견 항목:
- 누락 항목:
- 다음 단계:
```

## Model Found Flow

사용자가 지정한 모델 프로젝트 폴더에서 학습/추론 가능한 모델 프로젝트가 발견되면 샘플을 선택하지 않는다. 발견된 프로젝트를 기준으로 분석 결과를 만들고, 이후 단계에서 해당 프로젝트를 직접 실행한다.

중요 규칙:

```text
`data/` 안의 모델 형식 파일 또는 실행 entrypoint가 하나라도 발견되면 사용자에게 샘플 선택 질문을 하지 않는다.
샘플 선택은 model_found: false일 때만 진행한다.
```

모델 프로젝트가 있다고 판단하는 기준은 다음 중 하나 이상이다.

```text
학습 entrypoint 존재: train.py, scripts/train.py
실행/등록 entrypoint 존재: 프로젝트 진입점
추론 entrypoint 존재: predict.py, app.py, main.py
필수 폴더 존재: aiu_custom/, local_serving/, save_model/, aiu_studio/
모델 wrapper 존재: aiu_custom/model_wrapper.py, aiu_custom/predict.py
데이터 모델 파일 존재: 지원 확장자의 파일이 data/ 아래에 있음
MLflow model 존재: MLmodel, python_model.pkl
input example 존재: input_example.json
```

사용자가 지정한 경로가 상위 루트이고, 모델 폴더가 하위에 있으면 하위 모델 폴더를 `selected_project_path`로 선택한다.

```text
<root>/sklearn_sample/
<root>/pytorch_sample/
<root>/tensorflow_sample/
<root>/data/
```

모델이 발견된 경우 출력에는 반드시 다음을 포함한다.

```text
model_found: true
selected_project_path
framework
train_entrypoint
inference_entrypoint
model_artifact_path
model_artifact_paths
data_model_files
input_example_path
next_action: model_artifact_paths 중 사용할 모델 선택
```

`model_artifact_paths`는 사용자가 선택할 수 있도록 번호 목록으로 보여준다.
`model_artifact_path`는 기본 선택값이며, 목록의 첫 번째 모델 경로를 사용한다.
모델이 1개만 있어도 사용자가 확인할 수 있도록 경로를 보여주고 선택 확인을 받는다.
사용자가 `1`, `1번`, `첫 번째`, 모델 파일명, 모델 경로처럼 응답하면 분석 스킬을 다시 실행하지 않는다.
그 응답은 모델 선택으로 처리하고 `agent-mlflow-skill-selected-run-test` 단계로 이어간다.

모델이 발견된 경우 사용자에게 보여줄 가이드는 아래 방향으로 작성한다.

```text
실행 가능한 모델 구성을 찾았습니다.
샘플은 사용하지 않고 기존 모델 프로젝트 기준으로 진행합니다.

다음 단계:
1. 사용할 모델 번호 또는 경로 선택
2. 프로젝트 루트에 `aiu_studio/` 폴더 생성 또는 기존 폴더 보존
3. 선택 모델 기준 `data/**` 파일을 루트 `aiu_studio/` 폴더로 병합 복사
4. 선택 모델 형식에 맞는 `runtest_2.py` 생성
5. `agent-mlflow-skill-environment-check`로 dependency 확인
6. `agent-mlflow-skill-inference-test`로 추론 테스트
7. `agent-mlflow-skill-mlflow-verify`로 MLflow 기록 확인
```

모델이 발견되면 `.opencode/samples`는 참조하지 않는다.

## No Model Found Fallback

사용자가 지정한 모델 프로젝트 폴더에서 학습/추론 가능한 모델 프로젝트를 찾지 못하면 실패로 끝내지 않는다. `.opencode/samples` 아래 샘플 3개 중 하나를 사용자가 선택하게 하고, 선택한 샘플 폴더를 워크스페이스 아래로 폴더째 복사해 모델 생성과 테스트 흐름을 진행할 수 있게 한다.

현재 분석 경로에 모델이 없는 경우, 폐쇄망 모델 존재 여부를 먼저 분리한다.

사용자가 폐쇄망에 모델이 있다고 말했거나 실제 모델 프로젝트가 따로 있다고 말한 경우:

```text
현재 분석 경로에서는 data/ 모델 파일을 찾지 못했습니다.
폐쇄망에 모델이 있다면 실제 모델 프로젝트 경로를 지정하거나, 모델 파일을 <model-project-folder>/data/** 아래로 반입한 뒤 다시 분석해야 합니다.
샘플 생성은 기존 모델을 반입하지 못할 때만 진행합니다.
```

사용자가 샘플로 시작하겠다고 하거나 폐쇄망 모델을 반입할 수 없는 경우에는 아래처럼 선택을 요청한다.

```text
현재 워크스페이스에서 실행 가능한 모델을 찾지 못했습니다.

아래 샘플 중 하나를 선택해서 워크스페이스에 폴더째 복사할 수 있습니다.

1. sklearn
2. pytorch
3. tensorflow

원하는 샘플 번호 또는 이름을 알려주세요.
```

사용자가 선택하기 전에는 샘플을 복사하지 않는다.

모델이 없는 경우 사용자에게 보여줄 가이드는 아래 방향으로 작성한다.

```text
실행 가능한 모델 구성을 찾지 못했습니다.
기본 모델 샘플로 시작할 수 있습니다.

선택 가능:
1. sklearn
2. pytorch
3. tensorflow

원하는 번호나 이름을 알려주면 해당 샘플 폴더를 워크스페이스에 복사하겠습니다.
```

### Selectable Samples

사용자가 선택할 수 있는 샘플은 아래 3개다.

```text
1. sklearn
   source: .opencode/samples/sklearn_sample
   purpose: 폐쇄망 sklearn 모델 프로젝트 기본 구조

2. pytorch
   source: .opencode/samples/pytorch_sample
   purpose: 폐쇄망 PyTorch 모델 프로젝트 기본 구조

3. tensorflow
   source: .opencode/samples/tensorflow_sample
   purpose: 폐쇄망 TensorFlow/Keras 모델 프로젝트 기본 구조
```

이 3개 외의 샘플은 임의로 선택하지 않는다.

선택형 샘플은 원본 폴더에 아래 기본 폴더가 있어야 한다.

```text
aiu_custom/
local_serving/
save_model/
aiu_studio/
```

아래 폴더는 사용자가 폐쇄망 모델을 직접 넣는 기본 슬롯이며, 워크스페이스에 모델이 없을 때 선택형 폴더 복사 대상으로 사용한다.

```text
sklearn_sample/
pytorch_sample/
tensorflow_sample/
```

### Workspace Copy Rule

기본 복사 방식은 `copy_mode: folder`다. 샘플 내용을 루트에 풀어놓지 않고 샘플 폴더 자체를 복사한다.

```text
<model-project-folder>/sklearn_sample/
<model-project-folder>/pytorch_sample/
<model-project-folder>/tensorflow_sample/
```

워크스페이스에 기존 파일이 있어도 대상 샘플 폴더가 없으면 복사할 수 있다. 같은 이름의 샘플 폴더가 이미 있으면 기본적으로 중단한다. 사용자가 명시적으로 덮어쓰기를 요청한 경우에만 `--force`를 사용한다.

### Selected Sample Handling

선택된 샘플은 원본을 직접 수정하지 않는다. 샘플 폴더 자체를 사용자가 지정한 워크스페이스 아래로 복사한다.

```text
<model-project-folder>/<sample-folder>/aiu_custom/
<model-project-folder>/<sample-folder>/local_serving/
<model-project-folder>/<sample-folder>/save_model/
<model-project-folder>/<sample-folder>/aiu_studio/
<model-project-folder>/<sample-folder>/<project-entrypoint>
<model-project-folder>/<sample-folder>/requirements.txt
<model-project-folder>/<sample-folder>/input_example.json
```

폴더 복사에서는 실행에 필요하지 않은 생성 산출물을 제외한다.

```text
model/
saved_model/
artifacts/ai_studio/
.venv/
__pycache__/
MLflow 로컬 실행 산출물
mlartifacts/
mlflow.db
```

복사 후 아래 필수 폴더는 항상 복사된 샘플 폴더 안에 있어야 한다. 샘플 원본에 없으면 빈 폴더로 생성한다.

```text
aiu_custom/
local_serving/
save_model/
aiu_studio/
```

복사는 `agent-mlflow-skill-sample-bootstrap` 스킬과 아래 스크립트를 기준으로 한다.

```text
python .opencode/scripts/bootstrap_sample_project.py --project <model-project-folder> --sample sklearn --execute
python .opencode/scripts/bootstrap_sample_project.py --project <model-project-folder> --sample pytorch --execute
python .opencode/scripts/bootstrap_sample_project.py --project <model-project-folder> --sample tensorflow --execute
```

샘플 선택 결과에는 반드시 다음을 포함한다.

```text
model_found: false
selected_sample
sample_source_path
target_project_path
copy_mode: folder
required_dirs: aiu_custom, local_serving, save_model, aiu_studio
next_action
```

## Output

- 선택된 프로젝트 경로
- 모델 프로젝트 발견 여부
- 모델이 있을 때 발견된 학습/추론/data 모델 파일 경로
- 모델이 없을 때 사용자가 선택할 샘플 3개
- 선택된 샘플 원본 경로와 폴더 복사 대상 경로
- 발견된 핵심 파일 목록
- 누락되었거나 확인 필요한 파일 목록
- framework 후보와 판단 근거
- 학습 entrypoint 후보
- 추론 entrypoint 후보
- `data/` 모델 파일 후보
- `aiu_custom` 필요 여부
- 필수 폴더 존재 여부: `aiu_custom/`, `local_serving/`, `save_model/`, `aiu_studio/`
- 다음 단계: `agent-mlflow-skill-environment-check`

## Safety

- 이 단계에서는 파일을 수정하지 않는다.
- 분석 단계에서는 `data/` 모델 파일을 이동하거나 복사하지 않는다.
- 샘플 원본 디렉터리를 직접 덮어쓰지 않는다.
- 샘플을 폴더째 복사해야 하면 사용자 선택을 먼저 받은 뒤 `agent-mlflow-skill-sample-bootstrap` 기준으로 처리한다.
- 모델이 발견된 경우에는 샘플 선택을 제안하지 않는다.
- credential 값은 출력하지 않는다.
- framework가 불명확하면 `unknown/custom`으로 둔다.
