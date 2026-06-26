# OpenCode MLflow 5단계 시작 가이드

이 프로젝트는 ML 개발자가 로컬/폐쇄망 모델 프로젝트를 MLflow 기준으로 점검하고, 현재 분석 경로에 모델이 없을 때 실제 폐쇄망 모델 경로 지정 또는 기본 샘플 생성을 선택하도록 돕습니다.

## 먼저 할 일

1. 점검할 모델 프로젝트 폴더를 정합니다.
2. 프로젝트에 아래 필수 구성이 있는지 확인합니다.

```text
aiu_custom/
local_serving/
save_model/
```

3. 필요하면 환경변수 또는 `config/mlflow_config.json`으로 MLflow 연결 값을 준비합니다.

## OpenCode에 이렇게 요청하세요

가장 권장하는 첫 요청:

```text
이 워크스페이스를 먼저 분석해줘. 모델이 있으면 기존 모델 기준으로 진행하고, 모델이 없으면 sklearn/pytorch/tensorflow 중 선택해서 생성해줘.
```

```text
내 모델 프로젝트 폴더를 MLflow 5단계 기준으로 분석해줘.
```

```text
/path/to/my-model-project 경로를 기준으로 프로젝트 구조 분석부터 MLflow 기록 확인까지 진행해줘.
```

```text
모델이 없으면 sklearn, pytorch, tensorflow 샘플 중 하나를 선택해서 폴더째 가져와줘.
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
- 현재 분석 경로에 모델이 없지만 폐쇄망 프로젝트에 모델이 있으면 실제 모델 프로젝트 경로를 지정하거나 모델 파일을 `<model-project-folder>/data/**` 아래로 반입한 뒤 다시 분석합니다.
- 샘플 생성은 기존 모델을 반입하지 못할 때만 `sklearn`, `pytorch`, `tensorflow` 중 하나를 사용자가 선택해 샘플 폴더째 복사합니다.
- 모델이 발견되면 샘플 선택 질문을 하지 않고 기존 모델 프로젝트로 진행합니다.
- `sklearn_sample/`, `pytorch_sample/`, `tensorflow_sample/`은 폐쇄망에서 사용자가 직접 모델을 넣는 기본 폴더입니다.
- 외부 다운로드나 원격 등록은 사용자가 명확히 요청한 경우에만 수행합니다.
