# OpenCode MLflow Local Model Skills

사용자가 이미 가져온 로컬 모델 프로젝트를 OpenCode에서 단계별로 점검하도록 돕는 skill pack이며, 정적 샘플 프로젝트도 함께 제공합니다.

이 저장소는 앱, CLI, TUI, 샘플 생성기, 자동 스캐너를 배포하지 않습니다. 사용자에게 제공하는 것은 OpenCode가 읽는 `.opencode/skills/<name>/SKILL.md` 파일, 정적 샘플 프로젝트, 로컬 검증 스크립트입니다.

## 포함된 Skill

```text
.opencode/
└── skills/
    ├── agent-mlflow-skill-model-select/
    ├── agent-mlflow-skill-project-check/
    ├── agent-mlflow-skill-mlflow-check/
    ├── agent-mlflow-skill-gap-guide/
    ├── agent-mlflow-skill-run-model-guide/
    ├── agent-mlflow-skill-preflight-check/
    └── agent-mlflow-skill-register-guide/
```

## 포함된 Sample

```text
.opencode/samples/
├── pytorch_sample/
├── sklearn_sample/
└── tensorflow_sample/
```

상세 요구사항은 [SKILL_REQUIREMENTS.md](SKILL_REQUIREMENTS.md)를 확인하세요.
구성 분석은 [SKILL_ANALYSIS_REPORT.md](SKILL_ANALYSIS_REPORT.md)를 확인하세요.
적용 방법은 [SKILL_APPLY_GUIDE.md](SKILL_APPLY_GUIDE.md)를 확인하세요.
테스트 시나리오는 [SKILL_TEST_SCENARIOS.md](SKILL_TEST_SCENARIOS.md)를 확인하세요.

## 단계

1. 로컬 모델 경로 선택
2. 프로젝트 스캔 안내
3. MLflow 준비 검증 안내
4. 부족한 파일/설정 보완 안내
5. 등록/실행 entrypoint 기능 안내
6. 등록 전 사전 준비 검증 기준 안내
7. local/remote MLflow 등록 안내

## 사용 방법

사용자의 ML 프로젝트 루트에 `.opencode` 폴더를 복사합니다.

```bash
cp -R .opencode /path/to/user-project/
```

그다음 사용자는 OpenCode에서 자연어로 요청합니다.

```text
이 로컬 모델 프로젝트를 MLflow 등록 준비 관점에서 단계별로 봐줘
./my-model 경로를 기준으로 필요한 파일이 뭔지 알려줘
등록/실행 entrypoint가 어떤 기능을 제공하면 좋은지 알려줘
원격 MLflow 등록 전에 사전 준비 검증 단계가 있으면 무엇을 확인해야 하는지 알려줘
```

샘플 구조를 먼저 확인하려면 `.opencode/samples/` 아래 프로젝트를 참고합니다. `.opencode` 전체를 복사하면 스킬, 샘플, 검증 스크립트가 함께 적용됩니다.

로컬 환경까지 테스트하려면 아래 스크립트를 사용할 수 있습니다.

```bash
python .opencode/scripts/test_local_sample.py --sample all --python /path/to/python3.12
```

특정 샘플만 테스트할 수도 있습니다.

```bash
python .opencode/scripts/test_local_sample.py --sample pytorch_sample --python /path/to/python3.12
```

`kserve==0.15.0` 제약 때문에 로컬 테스트에는 Python 3.9~3.12가 필요합니다.

스킬의 7단계 기준으로 프로젝트를 검증하려면 아래 스크립트를 사용할 수 있습니다. Windows 10/11에서도 같은 명령 구조로 동작합니다.

```bash
python .opencode/scripts/validate_mlflow_project.py --project .opencode/samples/sklearn_sample
```

경로를 주지 않으면 현재 루트 또는 `.opencode/samples/`에서 자동 후보를 선택합니다.

```bash
python .opencode/scripts/validate_mlflow_project.py
```

검증 항목은 다음 순서입니다.

1. 로컬 모델 경로 선택
2. 프로젝트 스캔 안내
3. MLflow 준비 검증 안내
4. 부족한 파일/설정 보완 안내
5. 등록/실행 entrypoint 기능 안내
6. 등록 전 사전 준비 검증 기준 안내
7. local/remote MLflow 등록 안내

Windows 기준으로는 경로 길이, 공백 포함 경로, 쓰기 권한도 함께 확인합니다.

## 범위

- 파일을 자동 생성하지 않습니다.
- 정적 샘플 프로젝트를 제공합니다.
- 실행 중 샘플 생성기를 돌리지 않습니다.
- 별도 스캐너 프로그램을 실행하지 않습니다.
- 리포트 파일을 만들지 않습니다.
- OpenCode가 로컬 파일을 읽고 skill 지침에 따라 다음 조치를 안내하는 용도입니다.

## License

MIT
