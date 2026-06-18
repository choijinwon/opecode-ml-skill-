# OpenCode MLflow Local Model Skills

사용자가 이미 가져온 로컬 모델 프로젝트를 OpenCode에서 단계별로 점검하도록 돕는 단순 skill pack입니다.

이 저장소는 앱, CLI, TUI, 샘플 생성기, 자동 스캐너를 배포하지 않습니다. 사용자에게 제공하는 것은 OpenCode가 읽는 `.opencode/skills/<name>/SKILL.md` 파일뿐입니다.

## 포함된 Skill

```text
.opencode/
└── skills/
    ├── agent-mlflow-skill-model-select/
    ├── agent-mlflow-skill-project-check/
    ├── agent-mlflow-skill-mlflow-check/
    ├── agent-mlflow-skill-gap-guide/
    ├── agent-mlflow-skill-run-model-guide/
    ├── agent-mlflow-skill-prepare-check/
    └── agent-mlflow-skill-register-guide/
```

## 단계

1. 로컬 모델 경로 선택
2. 프로젝트 스캔 안내
3. MLflow 준비 검증 안내
4. 부족한 파일/설정 보완 안내
5. `run_model.py` 동작 안내
6. `--prepare-only` 검증 안내
7. local/remote MLflow 등록 안내

## 사용 방법

사용자의 ML 프로젝트 루트에 skill 폴더를 복사합니다.

```bash
cp -R .opencode/skills /path/to/user-project/.opencode/
```

그다음 사용자는 OpenCode에서 자연어로 요청합니다.

```text
이 로컬 모델 프로젝트를 MLflow 등록 준비 관점에서 단계별로 봐줘
./my-model 경로를 기준으로 필요한 파일이 뭔지 알려줘
run_model.py가 어떤 옵션을 가져야 하는지 알려줘
원격 MLflow 등록 전에 prepare-only로 뭘 확인해야 하는지 알려줘
```

## 범위

- 파일을 자동 생성하지 않습니다.
- 샘플 모델을 만들지 않습니다.
- 별도 스캐너 프로그램을 실행하지 않습니다.
- 리포트 파일을 만들지 않습니다.
- OpenCode가 로컬 파일을 읽고 skill 지침에 따라 다음 조치를 안내하는 용도입니다.

## License

MIT
