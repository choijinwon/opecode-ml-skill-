# Skill Apply Guide

## 1. 목적

이 문서는 OpenCode MLflow Local Model Skills를 사용자 로컬 모델 프로젝트에 적용하는 방법을 안내한다.

이 저장소는 실행 프로그램이 아니라 OpenCode skill 파일, 정적 샘플 프로젝트, 로컬 검증 스크립트를 제공한다. 사용자는 `.opencode` 폴더를 자신의 모델 프로젝트에 복사하거나, `.opencode/samples/` 아래 샘플을 참고 프로젝트로 사용할 수 있다.

## 2. 적용 대상

적용 대상은 다음과 같은 로컬 모델 프로젝트다.

- 처음 개발하는 ML/GenAI 모델 프로젝트
- 사용자가 직접 가져온 ML/GenAI 모델 프로젝트
- `requirements.txt`, `train.py`, `config.json`, MLflow 코드 내부 설정, `input_example.json` 중 일부 또는 전체를 가진 프로젝트.
- 사용자 환경의 MLflow tracking URI 또는 원격 MLflow 등록 준비 상태를 확인하려는 프로젝트

## 3. 포함되는 Skill

```text
.opencode/skills/
├── agent-mlflow-skill-model-create-guide/
├── agent-mlflow-skill-model-select/
├── agent-mlflow-skill-project-check/
├── agent-mlflow-skill-mlflow-check/
├── agent-mlflow-skill-gap-guide/
├── agent-mlflow-skill-run-model-guide/
├── agent-mlflow-skill-preflight-check/
└── agent-mlflow-skill-register-guide/
```

## 3.1 포함되는 Sample

```text
.opencode/samples/
├── pytorch_sample/
├── sklearn_sample/
└── tensorflow_sample/
```

## 4. 적용 전 확인

사용자 프로젝트 루트에서 다음을 확인한다.

```text
user-project/
├── model artifact 또는 saved_model/
├── requirements.txt
├── train.py 또는 inference entrypoint
├── 등록/실행 entrypoint
├── aiu_custom/ (AI Studio pyfunc 방식이면 필수)
├── config.json
├── MLflow 코드 내부 설정 또는 config
└── input_example.json
```

모든 파일이 없어도 된다. 부족한 파일은 skill이 "무엇이 필요한지" 안내한다.
처음 개발하는 프로젝트라면 `agent-mlflow-skill-model-create-guide`가 위 구조를 만들기 위한 파일 역할과 작성 기준을 먼저 안내한다.

## 5. 적용 방법

### 5.1 새 프로젝트에 적용

사용자 모델 프로젝트에 `.opencode` 폴더가 없다면 다음처럼 전체 폴더를 복사한다.

```bash
cp -R .opencode /path/to/user-project/
```

적용 후 구조:

```text
/path/to/user-project/
└── .opencode/
    ├── skills/
    ├── samples/
    └── scripts/
```

### 5.2 이미 `.opencode`가 있는 프로젝트에 적용

기존 `.opencode`가 있다면 이 저장소의 `skills`, `samples`, `scripts`를 필요한 범위만 병합한다.

```bash
mkdir -p /path/to/user-project/.opencode/skills
cp -R .opencode/skills/agent-mlflow-skill-* /path/to/user-project/.opencode/skills/
cp -R .opencode/samples /path/to/user-project/.opencode/
cp -R .opencode/scripts /path/to/user-project/.opencode/
```

기존 skill과 이름이 겹치면 덮어쓰기 전에 내용을 비교한다.

### 5.3 샘플 프로젝트 사용

샘플 구조를 먼저 확인하려면 `.opencode/samples/` 아래 프로젝트를 참고한다. 샘플을 별도 작업 디렉터리로 복사해 테스트할 때도 `.opencode` 전체를 함께 두면 된다.

```bash
cp -R .opencode/samples/pytorch_sample /path/to/workspace/
cp -R .opencode /path/to/workspace/pytorch_sample/
```

## 6. OpenCode에서 사용하는 방법

사용자 프로젝트 루트에서 OpenCode를 실행한다.

```bash
cd /path/to/user-project
opencode
```

그다음 자연어로 요청한다.

```text
이 프로젝트를 MLflow 등록 준비 관점에서 단계별로 봐줘.
```

경로를 직접 지정할 수도 있다.

```text
./my-model 경로를 기준으로 MLflow 등록에 필요한 파일을 확인해줘.
```

특정 단계만 요청할 수도 있다.

```text
등록/실행 entrypoint가 제공하면 좋은 기능을 알려줘.
등록 전 사전 준비 검증 단계에서 확인할 항목을 정리해줘.
원격 MLflow 등록 전에 코드 내부 설정에서 확인할 값을 알려줘.
이 모델이 TensorFlow/PyTorch/sklearn/ONNX/HuggingFace 중 어떤 유형인지 근거와 함께 봐줘.
```

샘플 프로젝트를 사용할 때도 같은 방식으로 요청하면 된다.

## 7. 권장 사용 흐름

0. `agent-mlflow-skill-model-create-guide`
   - 처음 모델을 개발하는 경우 MLflow 등록 가능한 프로젝트 구조와 파일 역할을 정한다.
1. `agent-mlflow-skill-model-select`
   - 로컬 모델 경로 또는 제공 샘플을 자동 후보 선정 규칙으로 정한다.
2. `agent-mlflow-skill-project-check`
   - 프로젝트 파일, artifact 상태, 모델 타입별 체크 기준을 확인한다.
3. `agent-mlflow-skill-mlflow-check`
   - MLflow dependency와 tracking 설정을 확인한다.
4. `agent-mlflow-skill-gap-guide`
   - 부족한 파일과 설정을 보완 방향별로 분류한다.
5. `agent-mlflow-skill-run-model-guide`
   - 등록/실행 entrypoint 기능과 책임을 확인한다.
6. `agent-mlflow-skill-preflight-check`
   - 등록 전 사전 준비 검증 단계 존재 여부와 실행 전 확인 기준을 확인한다.
7. `agent-mlflow-skill-register-guide`
   - local/remote MLflow 등록 방식과 사전 확인 항목을 확인한다.

## 8. 폐쇄망 등록 가이드 프롬프트

OpenCode 챗봇에서 폐쇄망 환경을 기준으로 점검하려면 아래 프롬프트를 그대로 사용할 수 있다.

```text
나는 폐쇄망 환경에서 처음 모델을 개발하는 개발자야.

현재 열려 있는 폴더를 모델 프로젝트 root로 보고,
MLflow 등록 가능한 구조인지 단계별로 점검해줘.

중요 조건:
- 폴더 이름은 사용자마다 다르니 폴더명으로 판단하지 마.
- 외부 다운로드, pip 설치, 원격 문서 조회를 전제로 하지 마.
- 직접 실행 명령은 안내하지 마.
- 내가 명확히 만들라고 요청하지 않으면 파일을 자동 생성하거나 수정하지 마.
- MLflow 설정값은 코드 내부 상수 또는 프로젝트 config 기준으로 확인해줘.
- secret 값은 절대 출력하지 마.

확인할 항목:
1. requirements.txt 존재 여부
2. train.py 또는 학습 entrypoint 존재 여부
3. 모델 artifact 저장 위치
4. config.json 존재 여부
5. input_example.json 존재 여부
6. run_model.py 존재 여부
7. aiu_custom/ 폴더 존재 여부
8. aiu_custom/predict.py 존재 여부
9. ModelWrapper 클래스 존재 여부
10. ModelWrapper가 load_context와 predict를 제공하는지 여부
11. run_model.py가 mlflow.pyfunc.log_model을 사용하는지 여부
12. code_paths=["aiu_custom"] 구조인지 여부
13. MLflow 코드 내부 설정값 위치 확인

MLflow 코드 내부 설정값:
- mlflow_tracking_url
- mlflow_tracking_username
- mlflow_tracking_password
- mlflow_experiment_name
- mlflow_register_model_name

출력 형식:
- 현재 판단한 모델 root
- 발견된 파일
- 부족한 파일
- AI Studio pyfunc 등록 가능 여부
- MLflow 설정값 준비 상태
- local/remote MLflow 등록 전 확인할 점
- 내가 다음에 보완해야 할 항목

다시 강조:
실행 명령은 쓰지 말고,
파일 구조와 설정 기준만 보고 안내해줘.
```

샘플로 먼저 테스트할 때는 첫 문단만 아래처럼 바꾼다.

```text
.opencode/samples/sklearn_sample 샘플을 모델 프로젝트 root로 보고,
MLflow 등록 가능한 구조인지 단계별로 점검해줘.
```

## 9. 적용 확인 방법

사용자 프로젝트에서 다음 파일들이 존재하면 적용된 것이다.

```bash
ls .opencode/skills/agent-mlflow-skill-*/SKILL.md
```

예상되는 skill 수는 8개다.

```text
agent-mlflow-skill-model-create-guide
agent-mlflow-skill-model-select
agent-mlflow-skill-project-check
agent-mlflow-skill-mlflow-check
agent-mlflow-skill-gap-guide
agent-mlflow-skill-run-model-guide
agent-mlflow-skill-preflight-check
agent-mlflow-skill-register-guide
```

## 10. 업데이트 방법

이 저장소의 skill을 최신 버전으로 다시 복사한다.

```bash
cp -R .opencode/skills/agent-mlflow-skill-* /path/to/user-project/.opencode/skills/
```

사용자 프로젝트에서 skill을 직접 수정했다면, 덮어쓰기 전에 diff를 확인한다.

## 11. 주의사항

- 이 skill pack은 모델 파일을 생성하지 않는다.
- 이 skill pack은 프로젝트 파일을 자동 수정하지 않는다.
- 이 skill pack은 MLflow 서버에 직접 연결하지 않는다.
- secret 값은 출력하지 않는 방향으로 사용해야 한다.
- 원격 등록은 사용자가 명시적으로 실행하기 전까지 안내 수준에 머문다.

## 12. 문제 해결

OpenCode가 skill을 못 찾는 경우:

- OpenCode를 사용자 프로젝트 루트에서 실행했는지 확인한다.
- `.opencode/skills/<skill-name>/SKILL.md` 구조인지 확인한다.
- `SKILL.md`의 frontmatter `name`이 폴더명과 같은지 확인한다.

skill 이름이 너무 길게 느껴지는 경우:

- 사용자는 skill 이름을 직접 입력하지 않아도 된다.
- "MLflow 등록 준비를 단계별로 봐줘"처럼 자연어로 요청하면 된다.

원격 MLflow 설정이 없는 경우:

- 사용자 환경에 맞는 `mlflow_tracking_url` 값을 먼저 확인한다.
- 원격 등록 정보는 사용자 프로젝트의 코드 내부 상수 또는 config 기준으로 준비한 뒤 다시 확인한다.
