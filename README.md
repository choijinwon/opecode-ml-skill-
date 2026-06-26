# OpenCode MLflow Local Model Skills

처음 모델을 개발하는 사용자와 이미 가져온 로컬 모델 프로젝트를 OpenCode에서 단계별로 점검하려는 사용자를 돕는 skill pack이며, 정적 샘플 프로젝트도 함께 제공합니다.

이 저장소는 앱, CLI, TUI, 샘플 생성기, 자동 스캐너를 배포하지 않습니다. 사용자에게 제공하는 것은 OpenCode가 읽는 `.opencode/skills/<name>/SKILL.md` 파일, 정적 샘플 프로젝트, 로컬 검증 스크립트입니다.

## 포함된 Skill

```text
.opencode/
└── skills/
    ├── agent-mlflow-skill-model-select/
    ├── agent-mlflow-skill-model-create-guide/
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
├── sklearn_sample/
├── pytorch_sample/
├── tensorflow_sample/
├── offline_weather_agent/
├── legal_agent_mlflow_aistudio/
└── design_agent_mlflow_aistudio/
```

`sklearn_sample/`, `pytorch_sample/`, `tensorflow_sample/`은 폐쇄망에서 사용자가 직접 모델 코드와 데이터를 넣기 위한 기본 폴더입니다. 사용자 워크스페이스에 모델이 없으면 이 3개 중 하나를 선택해 폴더째 복사합니다.

상세 요구사항은 [SKILL_REQUIREMENTS.md](SKILL_REQUIREMENTS.md)를 확인하세요.
구성 분석은 [SKILL_ANALYSIS_REPORT.md](SKILL_ANALYSIS_REPORT.md)를 확인하세요.
적용 방법은 [SKILL_APPLY_GUIDE.md](SKILL_APPLY_GUIDE.md)를 확인하세요.
폐쇄망 등록 가이드 프롬프트도 [SKILL_APPLY_GUIDE.md](SKILL_APPLY_GUIDE.md)의 "폐쇄망 등록 가이드 프롬프트" 섹션에 포함되어 있습니다.
테스트 시나리오는 [SKILL_TEST_SCENARIOS.md](SKILL_TEST_SCENARIOS.md)를 확인하세요.
AI Studio Agent Builder 제안서는 [docs/ai-studio-agent-builder-proposal.md](docs/ai-studio-agent-builder-proposal.md)를 확인하세요.
MLflow 메뉴 상세 설명은 [docs/mlflow-menu-guide.md](docs/mlflow-menu-guide.md)를 확인하세요.

## 단계

0. 처음 개발자용 모델 프로젝트 생성 안내
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

기본 실행 방식은 저장소 루트에서 OpenCode를 그대로 실행하는 것입니다.

```bash
opencode .
```

OpenCode 기본 로고 자체는 OpenCode 내장 화면이라 `.opencode` 설정으로 교체하지 않습니다. 대신 `.opencode/bin/opencode` launcher를 PATH에 등록하면 평소처럼 `opencode .`를 입력했을 때 Launch Guide가 터미널에 처음 한 번만 표시된 뒤 OpenCode가 실행됩니다. 채팅 첫 응답에서는 같은 가이드를 다시 출력하지 않습니다.

launcher 설치:

```bash
./.opencode/install-shell-launcher.sh
source ~/.zshrc
```

다시 보고 싶으면:

```bash
opencode --reset-launch
```

OpenCode 실행 직전에 Launch Guide를 한 번만 보여주고 싶으면 `.opencode` 폴더 안의 실행 파일을 직접 사용할 수도 있습니다.

```bash
./.opencode/start
```

이 명령은 `.opencode/LAUNCH_GUIDE.md`의 짧은 안내를 처음 한 번만 터미널에 보여준 뒤 `opencode`를 실행합니다. 다시 보고 싶으면 아래처럼 초기화합니다.

```bash
./.opencode/start --reset-launch
```

상세 시작 가이드는 `.opencode/START_GUIDE.md`에 있습니다. 초기 진입 안내는 플러그인이나 default agent가 아니라 `.opencode/bin/opencode` 런처와 `.opencode/start` 스크립트가 담당합니다.

OpenCode provider API 키를 환경변수로 관리하려면 `.env.example`을 복사해 `.env`를 만들고 필요한 값만 채웁니다. 실제 `.env`는 Git에 올리지 않습니다.

```bash
cp .env.example .env
```

macOS/Linux 셸에서 `.env`를 로드한 뒤 OpenCode를 실행할 수 있습니다.

```bash
set -a
source .env
set +a
opencode
```

OpenCode는 `/connect`로 입력한 인증 정보를 `~/.local/share/opencode/auth.json`에 저장할 수도 있고, `opencode.json`에서는 `{env:VARIABLE_NAME}` 형식으로 환경변수를 참조할 수 있습니다.

로컬 Qwen 모델을 쓰는 경우에는 예시 설정을 복사해서 시작할 수 있습니다. Ollama 기본 포트 기준으로 작성되어 있으며, LM Studio나 llama.cpp를 쓰면 `.env`의 `LOCAL_QWEN_BASE_URL`만 바꿉니다.

```bash
cp opencode.local.example.json opencode.json
cp .env.example .env
```

```bash
set -a
source .env
set +a
opencode
```

그다음 사용자는 OpenCode에서 자연어로 요청합니다.

```text
나는 처음 모델을 개발하는 개발자야. sklearn, pytorch, tensorflow 샘플 중 하나로 MLflow 등록 가능한 모델 프로젝트 구조를 잡아줘
이 로컬 모델 프로젝트를 MLflow 등록 준비 관점에서 단계별로 봐줘
./my-model 경로를 기준으로 필요한 파일이 뭔지 알려줘
등록/실행 entrypoint가 어떤 기능을 제공하면 좋은지 알려줘
원격 MLflow 등록 전에 사전 준비 검증 단계가 있으면 무엇을 확인해야 하는지 알려줘
```

AI Studio pyfunc 방식까지 확인하려면 아래처럼 요청합니다.

```text
이 프로젝트가 AI Studio pyfunc 방식으로 MLflow 등록 가능한지 봐줘.
aiu_custom 폴더, 프로젝트 진입점, ModelWrapper, input_example, config, requirements를 확인해줘.
```

샘플 구조를 먼저 확인하려면 `.opencode/samples/` 아래 프로젝트를 참고합니다. `.opencode` 전체를 복사하면 스킬, 샘플, 검증 스크립트가 함께 적용됩니다.

로컬 환경까지 테스트하려면 아래 스크립트를 사용할 수 있습니다.

```bash
python .opencode/scripts/test_local_sample.py --sample all --python /path/to/python3.12
```

특정 샘플만 테스트할 수도 있습니다.

```bash
python .opencode/scripts/test_local_sample.py --sample sklearn --python /path/to/python3.12
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

검증 스크립트 출력은 7단계 흐름에 더해 `aiu_custom` wrapper, Windows 경로, 쓰기 권한 같은 세부 항목을 함께 표시할 수 있습니다.
Windows 기준으로는 경로 길이, 공백 포함 경로, 쓰기 권한도 함께 확인합니다.

## 범위

- 사용자가 명확히 요청하면 OpenCode가 모델 프로젝트 구조 생성을 도울 수 있습니다.
- 정적 샘플 프로젝트를 제공합니다.
- 실행 중 샘플 생성기를 돌리지 않습니다.
- 별도 스캐너 프로그램을 실행하지 않습니다.
- 리포트 파일을 만들지 않습니다.
- OpenCode가 로컬 파일을 읽고 skill 지침에 따라 다음 조치를 안내하는 용도입니다.

## License

MIT
