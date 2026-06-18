# Skill Apply Guide

## 1. 목적

이 문서는 OpenCode MLflow Local Model Skills를 사용자 로컬 모델 프로젝트에 적용하는 방법을 안내한다.

이 저장소는 실행 프로그램이 아니라 OpenCode skill 파일만 제공한다. 사용자는 `.opencode/skills` 폴더를 자신의 모델 프로젝트에 복사한 뒤, OpenCode에서 자연어로 점검을 요청한다.

## 2. 적용 대상

적용 대상은 다음과 같은 로컬 모델 프로젝트다.

- 사용자가 직접 가져온 ML/GenAI 모델 프로젝트
- `requirements.txt`, `train.py`, `run_model.py`, `config.json`, `ai_studio.env`, `input_example.json` 중 일부 또는 전체를 가진 프로젝트
- 사용자 환경의 MLflow tracking URI 또는 원격 MLflow 등록 준비 상태를 확인하려는 프로젝트

## 3. 포함되는 Skill

```text
.opencode/skills/
├── agent-mlflow-skill-model-select/
├── agent-mlflow-skill-project-check/
├── agent-mlflow-skill-mlflow-check/
├── agent-mlflow-skill-gap-guide/
├── agent-mlflow-skill-run-model-guide/
├── agent-mlflow-skill-prepare-check/
└── agent-mlflow-skill-register-guide/
```

## 4. 적용 전 확인

사용자 프로젝트 루트에서 다음을 확인한다.

```text
user-project/
├── model artifact 또는 saved_model/
├── requirements.txt
├── train.py 또는 inference entrypoint
├── run_model.py
├── config.json
├── ai_studio.env
└── input_example.json
```

모든 파일이 없어도 된다. 부족한 파일은 skill이 "무엇이 필요한지" 안내한다.

## 5. 적용 방법

### 5.1 새 프로젝트에 적용

사용자 모델 프로젝트에 `.opencode` 폴더가 없다면 다음처럼 복사한다.

```bash
mkdir -p /path/to/user-project/.opencode
cp -R .opencode/skills /path/to/user-project/.opencode/
```

적용 후 구조:

```text
/path/to/user-project/
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

### 5.2 이미 `.opencode`가 있는 프로젝트에 적용

기존 `.opencode/skills`가 있다면 이 저장소의 skill 폴더만 병합한다.

```bash
mkdir -p /path/to/user-project/.opencode/skills
cp -R .opencode/skills/agent-mlflow-skill-* /path/to/user-project/.opencode/skills/
```

기존 skill과 이름이 겹치면 덮어쓰기 전에 내용을 비교한다.

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
run_model.py가 가져야 할 옵션을 알려줘.
--prepare-only 전에 확인할 항목을 정리해줘.
원격 MLflow 등록 전에 ai_studio.env에서 확인할 키를 알려줘.
이 모델이 TensorFlow/PyTorch/sklearn/ONNX/HuggingFace 중 어떤 유형인지 근거와 함께 봐줘.
```

## 7. 권장 사용 흐름

1. `agent-mlflow-skill-model-select`
   - 로컬 모델 경로를 선택한다.
2. `agent-mlflow-skill-project-check`
   - 프로젝트 파일, artifact 상태, 모델 타입별 체크 기준을 확인한다.
3. `agent-mlflow-skill-mlflow-check`
   - MLflow dependency와 tracking 설정을 확인한다.
4. `agent-mlflow-skill-gap-guide`
   - 부족한 파일과 설정을 보완 방향별로 분류한다.
5. `agent-mlflow-skill-run-model-guide`
   - `run_model.py` 옵션과 책임을 확인한다.
6. `agent-mlflow-skill-prepare-check`
   - `--prepare-only` 검증 기준을 확인한다.
7. `agent-mlflow-skill-register-guide`
   - local/remote MLflow 등록 실행 조건을 확인한다.

## 8. 적용 확인 방법

사용자 프로젝트에서 다음 파일들이 존재하면 적용된 것이다.

```bash
ls .opencode/skills/agent-mlflow-skill-*/SKILL.md
```

예상되는 skill 수는 7개다.

```text
agent-mlflow-skill-model-select
agent-mlflow-skill-project-check
agent-mlflow-skill-mlflow-check
agent-mlflow-skill-gap-guide
agent-mlflow-skill-run-model-guide
agent-mlflow-skill-prepare-check
agent-mlflow-skill-register-guide
```

## 9. 업데이트 방법

이 저장소의 skill을 최신 버전으로 다시 복사한다.

```bash
cp -R .opencode/skills/agent-mlflow-skill-* /path/to/user-project/.opencode/skills/
```

사용자 프로젝트에서 skill을 직접 수정했다면, 덮어쓰기 전에 diff를 확인한다.

## 10. 주의사항

- 이 skill pack은 모델 파일을 생성하지 않는다.
- 이 skill pack은 프로젝트 파일을 자동 수정하지 않는다.
- 이 skill pack은 MLflow 서버에 직접 연결하지 않는다.
- secret 값은 출력하지 않는 방향으로 사용해야 한다.
- 원격 등록은 사용자가 명시적으로 실행하기 전까지 안내 수준에 머문다.

## 11. 문제 해결

OpenCode가 skill을 못 찾는 경우:

- OpenCode를 사용자 프로젝트 루트에서 실행했는지 확인한다.
- `.opencode/skills/<skill-name>/SKILL.md` 구조인지 확인한다.
- `SKILL.md`의 frontmatter `name`이 폴더명과 같은지 확인한다.

skill 이름이 너무 길게 느껴지는 경우:

- 사용자는 skill 이름을 직접 입력하지 않아도 된다.
- "MLflow 등록 준비를 단계별로 봐줘"처럼 자연어로 요청하면 된다.

원격 MLflow 설정이 없는 경우:

- 사용자 환경에 맞는 `MLFLOW_TRACKING_URI` 또는 `MLFLOW_TRACKING_URL` 값을 먼저 확인한다.
- 원격 등록 정보는 `ai_studio.env`에 준비한 뒤 다시 확인한다.
