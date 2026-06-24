# OpenCode MLflow 5단계 시작 가이드

이 프로젝트는 ML 개발자가 로컬/폐쇄망 모델 프로젝트를 MLflow 기준으로 점검하고, 모델이 없을 때 기본 샘플을 생성하도록 돕습니다.

## 먼저 할 일

1. 점검할 모델 프로젝트 폴더를 정합니다.
2. 프로젝트에 아래 필수 구성이 있는지 확인합니다.

```text
aiu_custom/
local_serving/
save_model/
ai_studio.env
```

3. `ai_studio.env`에 MLflow 연결 값을 준비합니다.

```env
mlflow_tracking_url=""
mlflow_tracking_username=""
mlflow_tracking_password=""
mlflow_experiment_name=""
mlflow_register_model_name=""
```

## OpenCode에 이렇게 요청하세요

가장 권장하는 첫 요청:

```text
이 워크스페이스를 먼저 분석해줘. 모델이 있으면 기존 모델 기준으로 진행하고, 모델이 없으면 sklearn/pytorch/tensorflow 중 선택해서 시작할 수 있게 가이드해줘.
```

```text
내 모델 프로젝트 폴더를 MLflow 5단계 기준으로 분석해줘.
```

```text
/path/to/my-model-project 경로를 기준으로 프로젝트 구조 분석부터 MLflow 기록 확인까지 진행해줘.
```

```text
모델이 없으면 sklearn, pytorch, tensorflow 샘플 중 하나를 선택해서 프로젝트 루트로 가져와줘.
```

## 5단계 흐름

```text
Step 1 Project Analyze
Step 2 Environment Check
Step 3 Train Model
Step 4 Inference Test
Step 5 MLflow Verify
```

## 중요한 규칙

- API key, password, token 값은 출력하지 않습니다.
- `mlflow_tracking_password`는 값이 아니라 `set`, `empty`, `missing` 상태만 확인합니다.
- 처음에는 샘플 선택부터 묻지 않고 워크스페이스를 먼저 분석합니다.
- 모델 프로젝트에 모델이 있으면 샘플을 사용하지 않습니다.
- 모델이 없고 프로젝트 루트가 비어 있을 때만 `sklearn`, `pytorch`, `tensorflow` 중 하나를 사용자가 선택해 루트로 복사합니다.
- 모델이 발견되면 샘플 선택 질문을 하지 않고 기존 모델 프로젝트로 진행합니다.
- `sklearn_sample/`, `pytorch_sample/`, `tensorflow_sample/`은 폐쇄망에서 사용자가 직접 모델을 넣는 기본 폴더입니다.
- 외부 다운로드나 원격 등록은 사용자가 명확히 요청한 경우에만 수행합니다.
