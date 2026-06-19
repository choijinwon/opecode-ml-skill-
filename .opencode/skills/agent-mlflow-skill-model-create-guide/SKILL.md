---
name: agent-mlflow-skill-model-create-guide
description: 처음 모델을 개발하는 사용자가 OpenCode 챗봇으로 MLflow 등록 가능한 모델 프로젝트 구조를 만들 수 있도록 모델 유형 선택, 파일 구성, aiu_custom wrapper, run_model.py 책임, 환경값 위치를 단계별로 안내한다.
license: MIT
compatibility: opencode
metadata:
  flow: local-model-registration
  stage: 00-model-create-guidance
  step: 0
---

# Model Creation Guidance

## When To Use

- 사용자가 처음 모델을 개발하고 MLflow 등록 가능한 프로젝트 구조를 만들고 싶다고 말할 때
- OpenCode 챗봇을 통해 sklearn, PyTorch, TensorFlow 중 하나의 시작 구조를 잡아야 할 때
- 폐쇄망 환경에서 외부 다운로드 없이 로컬/내부 패키지 정책에 맞는 프로젝트 뼈대를 설계해야 할 때
- 사용자가 아직 모델 root 폴더 구조, artifact 저장 위치, `aiu_custom`, `run_model.py` 역할을 모를 때

## Creation Flow

1. 모델 유형을 먼저 정한다.
   - 기본 추천은 가장 가벼운 `sklearn`
   - 사용자가 딥러닝을 원하면 `pytorch` 또는 `tensorflow`
2. 현재 OpenCode root 또는 사용자가 지정한 경로를 모델 프로젝트 root로 본다.
   - 폴더명은 판단 기준으로 쓰지 않는다.
   - `local_model`, `work`, 샘플명 같은 고정 이름을 요구하지 않는다.
3. 생성 또는 안내할 기본 구조를 제안한다.

```text
<model-root>/
├── requirements.txt
├── train.py
├── config.json
├── input_example.json
├── run_model.py
├── aiu_custom/
│   ├── __init__.py
│   └── predict.py
└── artifacts/
```

4. `train.py`는 학습 후 `config.json`의 artifact 경로에 모델 파일을 저장하도록 안내한다.
5. `aiu_custom/predict.py`는 `ModelWrapper`를 제공해야 한다.
   - `mlflow.pyfunc.PythonModel` 상속
   - `load_context`에서 model/config artifact 로드
   - `predict`에서 입력을 받아 추론 수행
6. `run_model.py`는 책임을 분리해야 한다.
   - 등록 전 준비 상태 확인 책임
   - MLflow 등록 책임
   - MLflow 환경값 설정 위치 제공
   - `mlflow.pyfunc.log_model(..., code_paths=["aiu_custom"], python_model=ModelWrapper())` 흐름 제공
7. MLflow 환경값은 코드 내부 상수 또는 프로젝트 config에 둔다.
   - 아래 키의 설정 위치만 확인한다.

```text
mlflow_tracking_url
mlflow_tracking_username
mlflow_tracking_password
mlflow_experiment_name
mlflow_register_model_name
```

## Chatbot Behavior

- 사용자가 "만들어줘"라고 명확히 요청하면 파일 생성을 도울 수 있다.
- 사용자가 "점검해줘"라고 요청하면 기존 파일을 읽고 부족한 항목만 안내한다.
- 실행 명령을 사용자에게 지시하지 않는다.
- 폐쇄망 환경에서는 외부 다운로드, pip 설치, 원격 문서 조회를 전제로 하지 않는다.
- dependency가 없으면 설치 명령이 아니라 누락 항목과 내부 패키지 정책 확인 필요성으로 안내한다.
- secret 값은 출력하지 않는다. 값 존재 여부, 비어 있음, 설정 위치만 말한다.

## Required Output

- 선택한 모델 유형
- 생성 또는 보완할 파일 구조
- 각 파일의 역할
- `aiu_custom` 필수 여부
- MLflow 환경값 설정 위치
- 등록 전 사전 준비 검증 기능 기준
- 다음 단계: `agent-mlflow-skill-model-select` 또는 `agent-mlflow-skill-project-check`

## Safety

- 폴더명을 기준으로 판단하지 않는다.
- 사용자가 명확히 요청하지 않으면 파일을 생성하지 않는다.
- credential 값을 만들거나 노출하지 않는다.
- OpenCode 챗봇 응답에서는 직접 실행 명령 대신 파일/기능/설정 기준을 안내한다.
