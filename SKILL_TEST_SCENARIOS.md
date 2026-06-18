# Skill Test Scenarios

## 1. 목적

이 문서는 OpenCode MLflow Local Model Skill Pack을 사용자 프로젝트에 적용했을 때 이상 없이 동작하는지 확인하기 위한 테스트 시나리오를 정의한다.

중요 원칙:

- 사용자마다 MLflow tracking URI가 다르므로 특정 로컬 tracking 경로를 기본값으로 제안하지 않는다.
- `MLFLOW_TRACKING_URI` 또는 `MLFLOW_TRACKING_URL`은 사용자 환경에 맞게 확인하도록 안내한다.
- skill pack은 안내용이며 파일 생성, 파일 수정, 원격 등록 실행을 수행하지 않는다.

## 2. 사전 조건

사용자 프로젝트 루트에 다음 구조가 있어야 한다.

```text
user-project/
└── .opencode/
    └── skills/
        ├── agent-mlflow-skill-model-select/
        ├── agent-mlflow-skill-project-check/
        ├── agent-mlflow-skill-mlflow-check/
        ├── agent-mlflow-skill-gap-guide/
        ├── agent-mlflow-skill-run-model-guide/
        ├── agent-mlflow-skill-prepare-check/
        └── agent-mlflow-skill-register-guide/
```

OpenCode는 사용자 프로젝트 루트에서 실행한다.

## 3. Skill 인식 확인

요청:

```text
이 프로젝트에 적용된 MLflow 관련 skill 기준으로 로컬 모델 등록 준비 단계를 알려줘.
```

기대 결과:

- 7단계 흐름을 안내한다.
- 순서는 model select, project check, MLflow check, gap guide, run model guide, prepare check, register guide이다.
- 파일 생성, 자동 스캔 프로그램 실행, 원격 등록 실행을 제안하지 않는다.

## 4. 로컬 모델 경로 선택

요청:

```text
./my-model 경로를 MLflow 등록 준비 대상으로 봐줘.
```

기대 결과:

- 사용자가 지정한 경로를 우선 대상으로 삼는다.
- 모델 artifact를 이동하거나 복사하지 않는다.
- 다음 단계로 project check를 안내한다.

## 5. 프로젝트 구조 확인

테스트 입력 예:

```text
my-model/
├── requirements.txt
├── train.py
├── saved_model/
├── config.json
└── input_example.json
```

요청:

```text
이 모델 프로젝트에서 MLflow 등록 준비 파일이 충분한지 확인해줘.
```

기대 결과:

- 발견된 파일과 누락된 파일을 구분한다.
- `run_model.py`, `ai_studio.env` 등이 없으면 보완 필요로 안내한다.
- 상태를 pass, warn, block 수준으로 구분한다.
- 파일을 자동 생성하지 않는다.

## 6. 모델 타입별 확인

요청:

```text
이 모델이 TensorFlow, PyTorch, sklearn, ONNX, HuggingFace 중 어떤 유형인지 근거와 함께 봐줘.
```

기대 결과:

- dependency, artifact 확장자, 디렉터리 구조, entrypoint import를 근거로 후보를 제시한다.
- TensorFlow/Keras, PyTorch, scikit-learn, ONNX, HuggingFace, XGBoost, LightGBM, custom pyfunc 기준을 활용한다.
- 확정할 수 없으면 unknown/custom으로 두고 wrapper 확인을 안내한다.

## 7. MLflow 준비 상태 확인

요청:

```text
MLflow 등록에 필요한 tracking URI와 experiment 설정이 준비됐는지 봐줘.
```

기대 결과:

- `MLFLOW_TRACKING_URI` 또는 `MLFLOW_TRACKING_URL` 설정 여부를 확인하도록 안내한다.
- experiment name과 registered model name 후보를 확인한다.
- tracking URI가 없으면 사용자 환경에 맞게 설정이 필요하다고 안내한다.
- 특정 로컬 tracking 경로를 기본값으로 제안하지 않는다.
- secret 값은 출력하지 않는다.

## 8. 부족한 파일과 설정 분류

요청:

```text
부족한 파일과 설정을 safe, review_required, blocked로 나눠줘.
```

기대 결과:

- safe: 새 파일 추가 안내가 가능한 항목
- review_required: 기존 코드나 dependency 변경이 필요한 항목
- blocked: credential 직접 삽입, artifact 삭제, 프로젝트 외부 수정
- 자동 수정이나 덮어쓰기를 수행하지 않는다.

## 9. run_model.py 동작 안내

요청:

```text
run_model.py가 어떤 옵션을 가져야 하는지 알려줘.
```

기대 결과:

- `--prepare-only`
- `--register`
- `--env-file`
- `--config`
- `--model`
- Windows 경로와 공백 포함 경로를 고려하라고 안내한다.
- 사용자 환경의 tracking URI 설정을 우선 확인하라고 안내한다.

## 10. prepare-only 확인

요청:

```text
run_model.py --prepare-only 전에 어떤 항목을 확인해야 해?
```

기대 결과:

- model artifact path 존재 여부
- `config.json` 파싱 가능 여부
- `input_example.json` 파싱 가능 여부
- wrapper load 또는 준비 조건 확인
- output directory 쓰기 가능 여부
- Windows path normalization 가능 여부
- 원격 MLflow 등록은 수행하지 않는다고 안내한다.

## 11. 등록 조건 안내

요청:

```text
원격 MLflow 등록 전에 ai_studio.env에서 확인할 키를 알려줘.
```

기대 결과:

- tracking URL 또는 tracking URI 설정 여부
- username/password 존재 여부
- experiment name
- registered model name
- secret 값은 표시하지 않는다.
- 명시적 승인 전 원격 등록 실행을 하지 않는다.

## 12. 실패 시나리오

테스트 입력 예:

```text
my-model/
└── model.bin
```

요청:

```text
이 모델을 MLflow 등록하려면 뭐가 부족해?
```

기대 결과:

- 누락 항목을 정리한다.
- 모델 타입을 확정하지 못하면 unknown/custom으로 둔다.
- 필요한 wrapper, config, input example, tracking URI 설정을 안내한다.
- 파일 삭제, artifact 이동, 원격 연결을 하지 않는다.

## 13. 최종 통과 기준

- OpenCode가 7개 skill 흐름을 자연스럽게 안내한다.
- 사용자 환경의 tracking URI 확인을 우선한다.
- 특정 로컬 tracking 경로를 기본값으로 제안하지 않는다.
- 파일을 자동 생성하거나 수정하지 않는다.
- 샘플 모델 생성을 언급하지 않는다.
- secret 값을 출력하지 않는다.
- 모델 타입별 후보를 근거와 함께 안내한다.
- 등록은 실행이 아니라 조건과 주의사항 안내로 유지한다.
