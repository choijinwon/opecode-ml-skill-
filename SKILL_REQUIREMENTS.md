# Skill Requirements

## 1. 목적

이 문서는 OpenCode MLflow Local Model Skills의 요구 사항을 정의한다.

이 skill pack은 사용자가 이미 보유한 로컬 모델 프로젝트를 OpenCode에서 단계별로 확인하고, MLflow 등록 준비에 필요한 다음 조치를 안내하기 위한 것이다.

## 2. 배포 범위

배포 대상은 OpenCode skill 파일뿐이다.

포함 범위:

- `.opencode/skills/<skill-name>/SKILL.md`
- skill 사용 순서와 확인 기준
- MLflow 등록 준비 관점의 안내 문구

제외 범위:

- 앱, CLI, TUI, Wizard 구현
- 샘플 모델 생성
- 자동 스캐너 프로그램
- 파일 자동 생성 또는 자동 수정
- 리포트 파일 생성
- 원격 MLflow 서버 직접 연결 또는 등록 실행

## 3. 대상 사용자

- 로컬에 모델 프로젝트를 가져온 사용자
- OpenCode를 사용해 모델 등록 준비 상태를 확인하려는 사용자
- MLflow local file store 또는 원격 MLflow 등록 전에 필요한 파일과 설정을 점검하려는 사용자

## 4. 네이밍 규칙

모든 skill은 다음 규칙을 따른다.

- 폴더명과 `SKILL.md` frontmatter의 `name`은 반드시 동일해야 한다.
- 이름은 lowercase kebab-case를 사용한다.
- 모든 skill 이름은 `agent-mlflow-skill-` prefix로 시작한다.
- 이름은 사용자가 이해하기 쉬운 짧은 동사/명사 조합을 사용한다.

현재 skill 목록:

| Step | Skill |
| --- | --- |
| 1 | `agent-mlflow-skill-model-select` |
| 2 | `agent-mlflow-skill-project-check` |
| 3 | `agent-mlflow-skill-mlflow-check` |
| 4 | `agent-mlflow-skill-gap-guide` |
| 5 | `agent-mlflow-skill-run-model-guide` |
| 6 | `agent-mlflow-skill-prepare-check` |
| 7 | `agent-mlflow-skill-register-guide` |

## 5. 공통 Skill 요구사항

각 skill은 다음 frontmatter를 포함해야 한다.

```yaml
---
name: agent-mlflow-skill-...
description: ...
license: MIT
compatibility: opencode
metadata:
  flow: local-model-registration
  stage: ...
  step: ...
---
```

각 skill 본문은 다음 섹션을 갖는 것을 권장한다.

- `When To Use`
- `Inputs`, `Checklist`, `Checks`, 또는 해당 단계에 맞는 기준
- `Output`
- `Safety`

## 6. 단계별 기능 요구사항

### 6.1 Model Select

Skill: `agent-mlflow-skill-model-select`

목적:

- 사용자가 가져온 로컬 모델 프로젝트 경로를 선택하도록 안내한다.

요구사항:

- 사용자가 명시한 경로가 있으면 그 경로를 우선한다.
- 명시 경로가 없으면 현재 프로젝트 루트와 `work/` 아래 후보를 안내한다.
- 후보별 framework, artifact 위치, 주요 파일 존재 여부를 요약하도록 안내한다.
- 여러 후보가 있으면 하나를 선택하도록 안내한다.
- 파일 생성, 복사, 이동은 안내하지 않는다.

다음 단계:

- `agent-mlflow-skill-project-check`

### 6.2 Project Check

Skill: `agent-mlflow-skill-project-check`

목적:

- 선택된 모델 프로젝트의 기본 등록 준비 파일을 확인하도록 안내한다.

확인 항목:

- `requirements.txt`
- `train.py` 또는 추론 entrypoint
- `run_model.py`
- `config.json`
- `ai_studio.env`
- `input_example.json`
- model artifact 경로와 크기
- framework 후보

출력 요구사항:

- 발견된 파일
- 누락된 파일
- framework와 artifact 요약
- pass/warn/block 수준의 상태 구분

다음 단계:

- `agent-mlflow-skill-mlflow-check`

### 6.3 MLflow Check

Skill: `agent-mlflow-skill-mlflow-check`

목적:

- MLflow local/remote 등록 준비 상태 확인 기준을 안내한다.

확인 항목:

- `mlflow` dependency 포함 여부
- `MLFLOW_TRACKING_URI` 또는 `MLFLOW_TRACKING_URL`
- experiment name
- registered model name
- local file store fallback 가능 여부
- username/password 존재 여부

안전 요구사항:

- secret 값은 출력하지 않는다.
- 원격 서버 연결이나 등록 실행을 수행하지 않는다.

다음 단계:

- `agent-mlflow-skill-gap-guide`

### 6.4 Gap Guide

Skill: `agent-mlflow-skill-gap-guide`

목적:

- 부족한 파일과 설정을 보완 방향별로 분류하도록 안내한다.

분류 기준:

- `safe`: 새 파일 추가 안내가 가능한 항목
- `review_required`: 기존 코드나 dependency 변경이 필요한 항목
- `blocked`: credential 직접 삽입, artifact 삭제, 프로젝트 외부 수정 등 금지 항목

출력 요구사항:

- 추가가 필요한 파일 목록
- 수정이 필요한 파일 목록
- 사용자 확인이 필요한 항목
- 차단된 항목과 이유

다음 단계:

- `agent-mlflow-skill-run-model-guide`

### 6.5 Run Model Guide

Skill: `agent-mlflow-skill-run-model-guide`

목적:

- `run_model.py`가 제공해야 할 옵션과 동작 기준을 안내한다.

필수 옵션:

- `--prepare-only`
- `--register`
- `--env-file`
- `--config`
- `--model`

동작 기준:

- Windows 경로와 공백 포함 경로를 고려한다.
- local file store fallback을 고려한다.
- `mlflow.pyfunc.log_model(...)`과 `registered_model_name` 사용 흐름을 안내한다.
- 원격 설정이 비어 있으면 local mode 안내를 제공한다.

다음 단계:

- `agent-mlflow-skill-prepare-check`

### 6.6 Prepare Check

Skill: `agent-mlflow-skill-prepare-check`

목적:

- `run_model.py --prepare-only`로 등록 전 확인할 항목을 안내한다.

확인 항목:

- model artifact path 존재 여부
- `config.json` 파싱 가능 여부
- `input_example.json` 파싱 가능 여부
- wrapper가 모델 준비를 수행하거나 준비 과정을 simulate할 수 있는지 여부
- output directory 쓰기 가능 여부
- Windows path normalization 가능 여부

안전 요구사항:

- 원격 MLflow 등록을 수행하지 않는다.
- 준비 검증 산출물은 프로젝트 내부 또는 `.aiu/` 아래로 제한하도록 안내한다.

다음 단계:

- `agent-mlflow-skill-register-guide`

### 6.7 Register Guide

Skill: `agent-mlflow-skill-register-guide`

목적:

- local file store 또는 원격 MLflow 등록 실행 조건과 주의사항을 안내한다.

Local mode 요구사항:

- `MLFLOW_TRACKING_URI` 또는 `MLFLOW_TRACKING_URL`이 비어 있으면 `file:./mlruns` fallback을 안내한다.
- local run, artifact, registered model name 후보를 안내한다.

Remote mode 요구사항:

- `ai_studio.env`에 tracking URL, username/password, experiment, registered model name이 있는지 확인하도록 안내한다.
- secret 값은 표시하지 않는다.
- 원격 등록은 사용자의 명시적 승인 이후에만 안내한다.

출력 요구사항:

- registration command
- local/remote mode
- experiment name
- registered model name
- run id 또는 local run path
- next action

## 7. 안전 요구사항

- credential, token, password, API key는 출력하지 않는다.
- 사용자의 모델 artifact를 이동, 삭제, 복사하지 않는다.
- 기존 파일 덮어쓰기를 기본 안내로 삼지 않는다.
- 원격 MLflow 등록 실행은 명시적 승인 전에는 안내 수준에 머문다.
- 외부 다운로드를 요구하지 않는다.
- 샘플 모델 생성을 요구하지 않는다.

## 8. 검수 기준

배포 전 다음 조건을 만족해야 한다.

- skill은 7개만 존재한다.
- 모든 skill 폴더명은 `agent-mlflow-skill-`로 시작한다.
- 모든 `SKILL.md` frontmatter의 `name`은 폴더명과 동일하다.
- 모든 skill 이름은 lowercase kebab-case이다.
- README와 SKILLS 인덱스의 이름이 실제 폴더명과 일치한다.
- 앱, CLI, TUI, 자동 스캐너, 샘플 생성기, 리포트 생성 기능을 배포한다고 오해될 문구가 없어야 한다.

## 9. 설치 요구사항

사용자는 자신의 프로젝트 루트에 skill 폴더를 복사해 사용한다.

```bash
cp -R .opencode/skills /path/to/user-project/.opencode/
```

OpenCode는 프로젝트 로컬 `.opencode/skills/<skill-name>/SKILL.md`를 읽어 skill로 사용한다.
