---
name: agent-mlflow-skill-project-check
description: 선택된 모델 프로젝트의 entrypoint, artifact, config, input example, requirements 확인 기준을 안내한다.
license: MIT
compatibility: opencode
metadata:
  flow: local-model-registration
  stage: 02-project-check
  step: 2
---

# Model Project Scan Guidance

## When To Use

- Step 2에서 선택된 프로젝트가 등록 가능한 구조인지 확인할 때
- 학습 entrypoint, 모델 artifact, MLflow 코드 내부 설정, 입력 예제를 확인할 때
- 수정 전 read-only 확인 기준이 필요할 때

## Guidance Checks

- `requirements.txt` 존재 여부
- `train.py` 또는 추론 entrypoint 존재 여부
- 등록/실행 entrypoint 또는 등록 절차 문서 존재 여부
- `config.json` 존재 여부
- MLflow 설정 방식 확인. 코드 내부 상수 또는 프로젝트 config를 기준으로 확인한다.
- `input_example.json` 존재 여부
- model artifact 경로와 크기
- framework 추정 결과
- AI Studio pyfunc 방식이면 `aiu_custom/`, `aiu_custom/predict.py`, `ModelWrapper` 존재 여부. `code_paths=["aiu_custom"]` 또는 `from aiu_custom...` import가 있으면 필수로 본다.

## Model Type Matrix

| Model type | Detection hints | Artifact checks | MLflow registration notes |
| --- | --- | --- | --- |
| TensorFlow / Keras | `tensorflow`, `keras`, `saved_model.pb`, `.h5`, `.keras` | SavedModel directory, `variables/`, `.h5` or `.keras` file | `mlflow.tensorflow` or pyfunc wrapper path를 확인한다. |
| PyTorch | `torch`, `.pt`, `.pth`, TorchScript, `state_dict` | weight file, model class source, tokenizer/preprocess code if needed | model class와 weights를 함께 재현할 수 있는지 확인한다. |
| scikit-learn | `sklearn`, `scikit-learn`, `.pkl`, `.joblib` | pickle/joblib artifact, feature order, preprocessing pipeline | `predict`/`predict_proba` 가능 객체인지 확인한다. |
| ONNX | `onnx`, `.onnx`, `onnxruntime` | `.onnx` file, input/output names, opset compatibility | input schema와 runtime dependency를 확인한다. |
| HuggingFace | `transformers`, `config.json`, tokenizer files, `pytorch_model.bin`, `model.safetensors` | model weights, tokenizer, config, generation/inference task | task type과 tokenizer dependency를 함께 확인한다. |
| XGBoost | `xgboost`, `.bst`, `.json`, `.ubj`, `.pkl` | booster/model file, feature names, objective | native booster인지 sklearn wrapper인지 구분한다. |
| LightGBM | `lightgbm`, `.txt`, `.pkl`, `.joblib` | booster text file or wrapper artifact, feature names | native booster와 sklearn wrapper 등록 방식을 구분한다. |
| Custom pyfunc | `PythonModel`, `mlflow.pyfunc`, custom wrapper files, `aiu_custom` import | `aiu_custom/`, `aiu_custom/predict.py`, `ModelWrapper`, artifact directory, dependency files | `load_context`와 `predict` 계약을 확인한다. AI Studio pyfunc 방식에서는 `aiu_custom`을 필수 구성으로 본다. |

## Framework Detection Rules

- `requirements.txt`, `pyproject.toml`, `environment.yml`에서 framework dependency를 먼저 확인한다.
- artifact 확장자와 디렉터리 구조로 후보 framework를 보강한다.
- training/inference entrypoint import 문에서 실제 사용 framework를 확인한다.
- `run_model.py` 또는 등록 entrypoint가 `aiu_custom`을 참조하면 `aiu_custom/` 폴더 누락은 block으로 분류한다.
- 여러 후보가 있으면 primary model framework와 preprocessing framework를 분리해 표시한다.
- framework를 확정할 수 없으면 `unknown/custom`으로 두고 wrapper 요구사항을 먼저 안내한다.

## Output

- pass/warn/block 판정
- 발견된 파일 목록
- 누락 파일 목록
- framework와 artifact 요약
- 모델 유형별 근거와 필요한 runtime 요소
- 권장 MLflow flavor 또는 pyfunc wrapper 방향
- 다음 단계: `agent-mlflow-skill-mlflow-check`

## Safety

- 이 단계에서는 파일을 수정하지 않는다.
- credential 값은 출력하지 않고 key 이름만 표시한다.
- framework는 추정 결과일 수 있으며, 확정이 어려우면 `unknown/custom`으로 유지한다.
