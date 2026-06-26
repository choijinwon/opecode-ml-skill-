# OpenCode 시작 가이드

이 저장소는 ML 개발자가 **사용자가 지정한 모델 프로젝트 폴더**를 대상으로 MLflow 모델 생성과 검증을 5단계로 진행하도록 돕는 OpenCode skill pack입니다.

처음 사용자가 무엇을 해야 할지 묻거나 모델 프로젝트 점검을 요청하면 아래 순서로 안내합니다.

1. Project Analyze: 모델 프로젝트 구조와 필수 폴더를 분석합니다.
2. Environment Check: Python, dependency, MLflow를 확인합니다.
3. Train Model: 기존 모델을 실행하거나 사용자가 선택한 샘플로 모델을 생성합니다.
4. Inference Test: `input_example.json` 기반으로 추론을 검증합니다.
5. MLflow Verify: MLflow Run, artifact, registered model 기록을 확인합니다.

필수 프로젝트 계약:

```text
aiu_custom/
local_serving/
save_model/
aiu_studio/
```

Secret 값은 절대 출력하지 않습니다. password와 API key는 값이 아니라 `set`, `empty`, `missing` 상태만 말합니다.

사용자가 가져온 모델 파일은 항상 모델 프로젝트 루트의 `data/` 폴더 안에 둡니다. `data/` 안에 sklearn/python, PyTorch/HF, ONNX, TensorFlow, Boosting, portable/LLM 계열 모델 파일이 있으면 기존 프로젝트를 분석해서 실행합니다. 이 경우 `data/` 안의 파일 전체를 프로젝트 루트의 `aiu_studio/` 폴더로 복사해 사용합니다. 모델이 없고 프로젝트 루트가 비어 있으면 `.opencode/samples`의 `sklearn_sample`, `pytorch_sample`, `tensorflow_sample` 중 하나를 사용자가 선택해 폴더째 복사합니다.

상세 문서는 `.opencode/skills/MLFLOW_5_STEP_GUIDE.md`와 `.opencode/skills/MLFLOW_5_STEP_ARCHITECTURE.md`를 기준으로 합니다.
