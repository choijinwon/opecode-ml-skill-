# OpenCode Launch Guide

이 가이드는 `.opencode` 패키지를 받은 사용자가 OpenCode를 어떻게 실행해야 하는지 설명합니다.

## 실행 화면용 짧은 가이드

OpenCode TUI plugin이 실행 화면에서 아래 짧은 가이드를 처음 한 번만 보여줍니다. 빌드/테스트/모델 등록 중에는 자동 출력하지 않습니다.

```text
[Launch Guide]
이 프로젝트는 GenAI - MLflow - AI Studio 적용을 돕는 OpenCode 패키지입니다.
중점 기능은 Prompt, Tracking/Trace, Chat Session, Judge, Dataset입니다.
모델 프로젝트 경로를 알려주면 AI Studio 적용 관점으로 분석할 수 있습니다.

예시:
- 이 프로젝트를 AI Studio 적용 관점에서 분석해줘
- Prompt/Tracking/Session/Judge/Dataset 설계를 정리해줘
- MLflow 기록이 AI Studio 화면에 어떻게 연결되는지 봐줘

보안 규칙: API key, password, token 값은 출력하지 않고 서버 배포 시 Secret/환경변수를 사용합니다.
상세 가이드: .opencode/LAUNCH_GUIDE.md
```

다시 보고 싶으면 OpenCode 안에서 아래 명령을 입력합니다.

```text
/launch
```

## 권장 실행 방식

기본 실행 방식은 저장소 루트에서 OpenCode를 그대로 실행하는 것입니다.

```bash
opencode .
```

이 방식은 Launch Guide를 자동 출력하지 않습니다.

TUI plugin을 사용할 수 없는 환경에서 OpenCode 실행 직전에 Launch Guide를 한 번만 보고 싶으면 아래 스크립트를 사용합니다.

```bash
./.opencode/start
```

동작 순서:

```text
1. .opencode/start 실행
2. .opencode/.launch_seen 파일이 없으면 짧은 Launch Guide 출력
3. 사용자가 Enter 입력
4. .opencode/.launch_seen 생성
5. opencode 프로젝트 실행
6. 다음 실행부터는 Launch Guide를 건너뜀
```

## 터미널 가이드 출력 방식

다시 보고 싶으면 sentinel 파일을 초기화합니다.

```bash
./.opencode/start --reset-launch
```

TUI plugin으로 표시된 welcome guide는 `.opencode/.welcome_guide_seen` 파일로 표시 여부를 저장합니다. 일반적인 재실행에서는 다시 뜨지 않고, 다시 보고 싶으면 채팅에서 `/launch`를 입력합니다.

또는 특정 프로젝트 폴더를 직접 지정합니다.

```bash
opencode /path/to/model-project
```

## 환경변수 로드 후 실행

로컬 Qwen 또는 사내 OpenAI 호환 endpoint를 사용할 때는 `.env` 또는 서버 환경변수를 먼저 로드합니다.

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
내 모델 프로젝트 폴더를 MLflow와 AI Studio 적용 관점에서 분석해줘.
```

```text
GenAI Agent를 만들 때 Prompt, Tracking, Session, Judge, Dataset을 AI Studio에 어떻게 붙이면 되는지 정리해줘.
```

```text
이 프로젝트가 MLflow 기록과 AI Studio 배포 구조를 만족하는지 점검해줘.
```

## 포함된 주요 자료

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
