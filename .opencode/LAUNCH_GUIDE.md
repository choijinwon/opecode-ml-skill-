# OpenCode Launch Guide

이 문서는 `.opencode` 패키지를 받은 사용자의 OpenCode 시작 화면 문구를 정의합니다.

## 실행 화면용 짧은 안내

OpenCode 기본 로고 자체는 OpenCode 내장 화면이라 `.opencode` 설정으로 교체하지 않습니다. 대신 `.opencode/bin/opencode` launcher를 PATH에 등록하면 `opencode .` 실행 직전에 아래 짧은 안내를 처음 한 번만 보여줍니다.

```text
[Launch Guide]
이 프로젝트는 MLflow 모델 프로젝트 분석과 샘플 생성을 돕는 OpenCode 패키지입니다.
처음 진입하면 워크스페이스를 먼저 분석해 모델 있음/없음을 확인합니다.

모델이 있으면 본인 모델 경로를 기준으로 MLflow 5단계를 진행합니다.
모델이 없으면 sklearn / pytorch / tensorflow 중 하나를 선택해 샘플을 생성합니다.

실제 복사/모델 생성/환경 검증 실행은 OpenCode 빌드모드에서 선택해주세요.

추천 첫 요청:
- 이 워크스페이스를 MLflow 5단계 기준으로 분석해줘.
- 모델이 없으면 sklearn 샘플로 생성해줘.

보안 규칙: API key, password, token 값은 출력하지 않고 서버 배포 시 Secret/환경변수를 사용합니다.
```

다시 보고 싶으면 `opencode --reset-launch` 또는 `./.opencode/start --reset-launch`로 초기화한 뒤 다시 실행합니다.

## 권장 실행 방식

권장 실행 방식은 shell launcher를 설치한 뒤 저장소 루트에서 OpenCode를 그대로 실행하는 것입니다.

```bash
./.opencode/install-shell-launcher.sh
source ~/.zshrc
```

```bash
opencode .
```

이 방식은 Launch Guide와 워크스페이스 분석 요약을 최초 1회 출력한 뒤 OpenCode를 실행합니다.

OpenCode 실행 직전에 Launch Guide를 한 번만 보고 싶으면 아래 스크립트를 직접 사용할 수도 있습니다.

```bash
./.opencode/start
```

동작 순서:

```text
1. .opencode/start 실행
2. .opencode/.launch_seen 파일이 없으면 짧은 Launch Guide와 워크스페이스 분석 요약 출력
3. 사용자가 Enter 입력
4. .opencode/.launch_seen 생성
5. opencode 프로젝트 실행
6. 다음 실행부터는 Launch Guide를 건너뜀
```

## 터미널 출력 방식

다시 보고 싶으면 sentinel 파일을 초기화합니다.

```bash
./.opencode/start --reset-launch
```

초기 진입 문구는 플러그인이 아니라 터미널 런처가 담당합니다. 표시 여부는 `.opencode/.launch_seen` 파일로 저장합니다.

또는 특정 프로젝트 폴더를 직접 지정합니다.

```bash
opencode /path/to/model-project
```

## 환경변수 로드 후 실행

로컬 모델 또는 사내 OpenAI 호환 endpoint를 사용할 때는 `.env` 또는 서버 환경변수를 먼저 로드합니다.

```bash
set -a
source .env
set +a
opencode .
```

예시 환경변수:

```env
OPENAI_API_KEY="your-internal-qwen-key"
OPENAI_BASE_URL="http://xxx.xxx.xxx.xxx:포트/v1"
OPENAI_MODEL="qwen3.6"
OPENAI_MODELS="qwen3.6,gpt20,gamma"
```

실제 API key, password, token 값은 Git에 올리지 않습니다.

## OpenCode에서 입력할 첫 질문

```text
이 워크스페이스를 MLflow 5단계 기준으로 분석해줘.
```

```text
모델이 없으면 sklearn 샘플로 생성해줘.
```

```text
모델이 있으면 내 모델 경로 기준으로 환경 검증부터 진행해줘.
```

## 포함된 주요 파일

```text
.opencode/START_GUIDE.md
.opencode/skills/MLFLOW_5_STEP_GUIDE.md
.opencode/skills/MLFLOW_5_STEP_ARCHITECTURE.md
.opencode/samples/offline_weather_agent_mlflow313/
```

## 서버 배포 시 실행 방안

서버에서는 `.env` 파일을 Git에 포함하지 말고 Secret 또는 환경변수로 주입합니다.

```text
Local 개발자 PC
  -> .env 또는 ai_studio.env 사용

Git
  -> .env.example, ai_studio.env.example만 관리

Server
  -> Docker/Kubernetes/CI Secret/환경변수로 주입
```

서버에서 OpenCode를 실행해야 한다면 아래 흐름을 권장합니다.

```bash
export OPENAI_API_KEY="..."
export OPENAI_BASE_URL="..."
export OPENAI_MODEL="qwen3.6"
opencode .
```

## 문제 발생 시 확인

```bash
which opencode
opencode --help
opencode debug config
chmod +x ./.opencode/start
./.opencode/start --help
```
