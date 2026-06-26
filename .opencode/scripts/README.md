# OpenCode MLflow Scripts

이 폴더는 `.opencode/skills`의 MLflow 5단계 흐름을 보조하는 로컬 스크립트를 포함한다.

대상은 사용자가 지정한 모델 프로젝트 폴더다.

## Script Mapping

```text
Step 1  프로젝트 구조 분석
        validate_mlflow_project.py
        bootstrap_sample_project.py

Step 2  실행 환경 검증
        check_environment.py

Step 3  로컬 학습 실행 및 모델 생성 확인
        run_training.py
        test_local_sample.py

Step 4  추론 테스트
        test_inference.py

Step 5  MLflow Run/Model 기록 확인
        verify_mlflow.py
```

## Scripts

### validate_mlflow_project.py

모델 프로젝트 폴더를 분석한다.

```text
python .opencode/scripts/validate_mlflow_project.py --project <model-project-folder>
python .opencode/scripts/validate_mlflow_project.py --project <model-project-folder> --json
```

### bootstrap_sample_project.py

모델 프로젝트 폴더에 실행 가능한 모델이 없을 때, 샘플 3개 중 하나를 선택해 워크스페이스 아래로 샘플 폴더째 복사한다.

선택 가능한 샘플은 원본에 `aiu_custom/`, `local_serving/`, `save_model/` 기본 폴더가 있어야 한다.

샘플 목록:

```text
python .opencode/scripts/bootstrap_sample_project.py --list
```

복사 전 확인:

```text
python .opencode/scripts/bootstrap_sample_project.py --project <model-project-folder> --sample sklearn
python .opencode/scripts/bootstrap_sample_project.py --project <model-project-folder> --sample pytorch
python .opencode/scripts/bootstrap_sample_project.py --project <model-project-folder> --sample tensorflow
```

실제 폴더 복사:

```text
python .opencode/scripts/bootstrap_sample_project.py --project <model-project-folder> --sample sklearn --execute
```

복사 대상은 소스 구조 중심이며 `.venv/`, `__pycache__/`, `model/`, `saved_model/`, `artifacts/ai_studio/`, `mlruns/`, `mlartifacts/`, `mlflow.db` 같은 생성 산출물은 제외한다.

복사 후 `aiu_custom/`, `local_serving/`, `save_model/` 필수 폴더는 항상 복사된 샘플 폴더 안에 보장한다.

기존 파일이 있을 때 덮어쓰기는 사용자가 명시적으로 요청한 경우에만 사용한다.

```text
python .opencode/scripts/bootstrap_sample_project.py --project <model-project-folder> --sample sklearn --execute --force
```

### check_environment.py

Python, dependency, MLflow, `ai_studio.env` 상태를 확인한다.

Secret 값은 출력하지 않고 `set`, `empty`, `missing` 상태만 출력한다.

학습 모델 생성 필수 파일:

```text
ai_studio.env
```

필수 키:

```text
mlflow_tracking_url
mlflow_tracking_username
mlflow_tracking_password
mlflow_experiment_name
mlflow_register_model_name
```

```text
python .opencode/scripts/check_environment.py --project <model-project-folder>
python .opencode/scripts/check_environment.py --project <model-project-folder> --json
```

### run_training.py

기존 모델 프로젝트를 실행한다. 모델이 없고 샘플을 가져와야 하면 먼저 `bootstrap_sample_project.py`로 사용자가 선택한 샘플 폴더를 복사한다.

기본값은 안전 모드다. 실제 실행은 `--execute`를 명시해야 한다.
실행 전 `ai_studio.env` 필수 키가 있는지 확인한다.
`data/` 폴더 안에 모델 형식 파일이 있으면 `data/` 안의 파일 전체를
프로젝트 루트의 `aiu_studio/` 폴더로 복사한다. 필수 구조나 실행 파일이 없으면
`aiu_custom/`, `local_serving/`, `save_model/`, `aiu_studio/`, `ai_studio.env`, `run_test.py`, `run_test2.py`
계열 파일을 자동 생성한다.

```text
python .opencode/scripts/run_training.py --project <model-project-folder>
python .opencode/scripts/run_training.py --project <model-project-folder> --execute
```

### ensure_run_test_entrypoints.py

`data/` 폴더 안에 모델 형식 파일은 있는데 실행 파일이 없을 때 제공 실행 파일을 생성한다.

```text
python .opencode/scripts/ensure_run_test_entrypoints.py --project <model-project-folder>
python .opencode/scripts/ensure_run_test_entrypoints.py --project <model-project-folder> --execute
```

대상 모델을 직접 선택해서 별도 실행 파일을 만들 수도 있다.
이 경우 먼저 `data/` 안의 파일 전체를 프로젝트 루트의 `aiu_studio/` 폴더로 복사한다.
그 다음 기존 `runtest.py` 또는 `run_test.py`를 템플릿으로 참고해서 선택 모델 형식에 맞는 `runtest_2.py`를 생성한다.

```text
python .opencode/scripts/ensure_run_test_entrypoints.py --project <model-project-folder> --target-model data/model.pkl --output runtest_2.py --execute
python .opencode/scripts/ensure_run_test_entrypoints.py --project <model-project-folder> --target-model model.pkl --output runtest_2.py --execute
python .opencode/scripts/ensure_run_test_entrypoints.py --project <model-project-folder> --target-model data/model.pkl --template runtest.py --output runtest_2.py --execute
```

이 모드는 선택한 `data/` 모델 파일의 확장자를 기준으로 로더를 결정하고, 템플릿 파일의 모델 경로와 모델 형식 상수만 새 대상 모델 기준으로 변환한다.
템플릿을 찾지 못하면 내장 실행 템플릿으로 생성한다.

생성 규칙:

```text
data/ 안의 첫 번째 모델 파일 -> run_test.py
data/ 안의 두 번째 모델 파일 -> run_test2.py
data/ 안의 세 번째 모델 파일 -> run_test3.py
```

지원 모델 확장자:

```text
.pkl, .joblib, .pt, .pth, .onnx, .h5, .keras, .bst, .ubj, .safetensors
```

### ensure_required_project_files.py

`data/` 폴더 안에 모델 형식 파일이 있을 때 AI Studio 연동에 필요한 기본 파일을 생성한다.
`data/` 안의 파일 전체는 프로젝트 루트의 `aiu_studio/` 폴더로 복사한다.

```text
python .opencode/scripts/ensure_required_project_files.py --project <model-project-folder>
python .opencode/scripts/ensure_required_project_files.py --project <model-project-folder> --execute
```

생성 대상:

```text
aiu_custom/
local_serving/
save_model/
aiu_studio/
requirements.txt
input_example.json
ai_studio.env
ai_studio.env.example
aiu_custom/predict.py
local_serving/serving_app.py
```

`aiu_custom/predict.py`는 `aiu_studio/`에 복사된 모델 파일을 우선 로드하고,
없으면 원본 `data/` 모델 파일을 로드한다.

폐쇄망 모델 선택 샘플:

```text
sklearn
pytorch
tensorflow
```

다른 샘플은 임의로 선택하지 않는다.

### test_local_sample.py

선택형 샘플 자체를 테스트한다.

```text
python .opencode/scripts/test_local_sample.py --sample sklearn
python .opencode/scripts/test_local_sample.py --sample all
```

### test_inference.py

모델 로드와 input example 기반 predict를 테스트한다.

기본값은 안전 모드다. 실제 추론은 `--execute`를 명시해야 한다.

```text
python .opencode/scripts/test_inference.py --project <model-project-folder>
python .opencode/scripts/test_inference.py --project <model-project-folder> --execute
```

### verify_mlflow.py

MLflow experiment, run, artifact, registered model 상태를 확인한다.

```text
python .opencode/scripts/verify_mlflow.py --tracking-uri http://127.0.0.1:5000 --experiment-name <name>
python .opencode/scripts/verify_mlflow.py --tracking-uri http://127.0.0.1:5000 --experiment-id <id> --registered-model <model-name>
```

## Safety

- 실제 학습/추론 실행은 `--execute`가 있을 때만 수행한다.
- secret 값은 출력하지 않는다.
- 샘플 원본은 직접 수정하지 않는다.
- 모델 프로젝트 폴더에 기존 작업 경로가 있으면 기본적으로 덮어쓰지 않는다.
