---
name: agent-mlflow-skill-sample-bootstrap
description: 사용자가 지정한 모델 프로젝트 폴더가 비어 있을 때 OpenCode 샘플 3개 중 하나를 선택하게 하고, 선택한 샘플을 프로젝트 루트로 복사해 GenAI/MLflow/AI Studio 모델 프로젝트를 시작한다.
license: MIT
compatibility: opencode
metadata:
  flow: ml-workspace-development
  stage: 00-sample-bootstrap
  step: 0
---

# Sample Bootstrap

## When To Use

- 사용자가 "현재 프로젝트에 아무것도 없다", "샘플을 루트로 가져오고 싶다", "샘플 3개 중 선택해서 시작하고 싶다"고 요청할 때
- 모델 프로젝트 폴더에 `.opencode`만 있고 실제 모델 코드가 없을 때
- 폐쇄망 기본 모델 샘플을 빠르게 프로젝트 루트에 구성해야 할 때
- Project Analyze 결과에서 `model_found: false`가 나온 뒤 사용자가 `sklearn`, `pytorch`, `tensorflow`, `1번`, `2번`, `3번`처럼 선택했을 때

이 스킬은 `agent-mlflow-skill-project-analyze` 결과가 `model_found: false`일 때만 사용한다. 모델 파일이나 실행 entrypoint가 있으면 이 스킬을 실행하지 않는다.

## Natural Language Selection

사용자 선택은 고정 문구가 아니어도 된다. 아래 입력은 모두 선택으로 해석한다.

```text
1, 1번, 첫 번째, sklearn, 사이킷런
2, 2번, 두 번째, pytorch, torch, 파이토치
3, 3번, 세 번째, tensorflow, tf, keras, 텐서플로우, 케라스
```

선택 매핑:

```text
1 | 1번 | 첫 번째 | sklearn | 사이킷런 -> sklearn
2 | 2번 | 두 번째 | pytorch | torch | 파이토치 -> pytorch
3 | 3번 | 세 번째 | tensorflow | tf | keras | 텐서플로우 | 케라스 -> tensorflow
```

선택이 모호하면 복사하지 말고 다시 선택을 요청한다.

## Selectable Samples

사용자에게 아래 3개 중 하나를 선택하게 한다.

```text
1. sklearn
   샘플 폴더: .opencode/samples/sklearn_sample
   목적: 폐쇄망 sklearn 모델 프로젝트 기본 구조

2. pytorch
   샘플 폴더: .opencode/samples/pytorch_sample
   목적: 폐쇄망 PyTorch 모델 프로젝트 기본 구조

3. tensorflow
   샘플 폴더: .opencode/samples/tensorflow_sample
   목적: 폐쇄망 TensorFlow/Keras 모델 프로젝트 기본 구조
```

## Empty Project Rule

프로젝트 루트가 아래 항목만 가지고 있으면 비어 있는 프로젝트로 본다.

```text
.opencode/
.git/
.gitignore
.DS_Store
```

그 외 파일이나 폴더가 있으면 기존 작업물이 있다고 보고 기본적으로 루트 복사를 중단한다. 덮어쓰기는 사용자가 명시적으로 요청했을 때만 수행한다.

## Required Sample Folder Rule

선택형 샘플은 아래 기본 폴더를 원본 샘플 안에 가지고 있어야 한다.

```text
aiu_custom/
local_serving/
save_model/
```

기본 폴더가 없는 샘플은 선택형 루트 복사 대상으로 사용하지 않는다.

## Copy Rule

선택한 샘플의 내용을 프로젝트 루트로 복사한다.

```text
<project-root>/aiu_custom/
<project-root>/local_serving/
<project-root>/save_model/
<project-root>/run_model.py
<project-root>/requirements.txt
<project-root>/input_example.json
```

복사하지 않는 항목:

```text
.venv/
__pycache__/
mlruns/
mlartifacts/
mlflow.db
.DS_Store
model/
saved_model/
artifacts/ai_studio/
```

복사 후 아래 필수 폴더는 항상 프로젝트 루트에 존재해야 한다. 샘플 원본에 없으면 빈 폴더로 생성한다.

```text
aiu_custom/
local_serving/
save_model/
```

## Script

샘플 목록 확인:

```text
python .opencode/scripts/bootstrap_sample_project.py --list
```

복사 전 dry-run:

```text
python .opencode/scripts/bootstrap_sample_project.py --project <model-project-folder> --sample sklearn
python .opencode/scripts/bootstrap_sample_project.py --project <model-project-folder> --sample pytorch
python .opencode/scripts/bootstrap_sample_project.py --project <model-project-folder> --sample tensorflow
```

실제 루트 복사:

```text
python .opencode/scripts/bootstrap_sample_project.py --project <model-project-folder> --sample sklearn --execute
```

기존 파일이 있는데 사용자가 명시적으로 덮어쓰기를 요청한 경우:

```text
python .opencode/scripts/bootstrap_sample_project.py --project <model-project-folder> --sample sklearn --execute --force
```

## Required Response

샘플 복사 전 사용자에게 반드시 아래 형식으로 선택지를 보여준다.

```text
현재 모델 프로젝트가 비어 있습니다. 아래 샘플 중 하나를 선택할 수 있습니다.

1. sklearn - sklearn 모델
2. pytorch - PyTorch 모델
3. tensorflow - TensorFlow/Keras 모델

원하는 샘플 번호 또는 이름을 알려주세요.
```

선택 질문을 출력해야 하는 조건:

```text
model_found: false
project_empty: true
```

선택 질문을 출력하지 않는 조건:

```text
model_found: true
project_empty: false
```

사용자가 선택하면 아래 정보를 출력한다.

```text
selected_sample
sample_source_path
target_project_root
copy_mode: root
ignored_generated_files
next_action
```

## Safety

- 사용자 선택 없이 임의로 샘플을 복사하지 않는다.
- 모델이 발견된 워크스페이스에서는 샘플 선택을 요청하지 않는다.
- 프로젝트 루트가 비어 있지 않으면 기본적으로 중단한다.
- secret 값은 복사 후에도 출력하지 않는다.
- `.env`, `ai_studio.env`의 실제 key/password/token 값은 출력하지 않는다.
- 샘플 원본 폴더는 수정하지 않는다.
