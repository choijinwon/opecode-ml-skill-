# Offline Weather Agent MLflow Sample

폐쇄망에서 OpenCode 챗봇으로 MLflow 등록 준비 상태를 점검하기 위한 AI Studio 스타일 샘플입니다.

## Required Layout

```text
aiu_custom/
├── __init__.py
├── predict.py
└── model_wrapper.py
config/
├── config.json
├── model_config.json
├── train_config.json
└── mlflow_config.json
local_serving/
├── serving_app.py
└── README.md
saved_model/
└── local_model.*
get-pip.py
input_example.json
model_summary.txt
requirements.txt
run_model.py
```

## OpenCode Chat Prompt

```text
현재 폴더를 모델 프로젝트 root로 보고 MLflow 등록 가능한 구조인지 점검해줘.
폴더명은 판단하지 말고 내부 파일 구조만 확인해줘.
직접 실행 명령은 안내하지 말고 부족한 파일과 설정만 알려줘.
MLflow 설정값은 코드 내부 상수 또는 config/mlflow_config.json 기준으로 확인해줘.
secret 값은 출력하지 마.
```

## MLflow Settings

MLflow 값은 `.env`가 아니라 아래 위치에서 확인합니다.

- `run_model.py` 코드 내부 상수
- `config/mlflow_config.json`

확인할 값:

- `mlflow_tracking_url`
- `mlflow_tracking_username`
- `mlflow_tracking_password`
- `mlflow_experiment_name`
- `mlflow_register_model_name`

## Notes

- `aiu_custom/model_wrapper.py`는 AI Studio pyfunc 방식의 필수 wrapper입니다.
- `local_serving/`은 로컬 서빙 책임을 분리하기 위한 참고 구조입니다.
- `saved_model/local_model.*`는 로컬 모델 export 또는 학습 산출물 위치입니다.
- OpenCode 챗봇 응답에서는 직접 실행 명령 대신 구조와 보완 기준만 안내합니다.

## Output Folder Roles

- `saved_model/`: 학습된 원본 모델 파일을 보관합니다.
- `model/`: MLflow 등록용 pyfunc 모델 패키지를 보관합니다.
- `artifacts/`: MLflow run, experiment, model registry 기록을 보관합니다.
- `local_serving/`: 배포 없이 로컬 서빙으로 확인한 테스트 결과를 보관합니다.

