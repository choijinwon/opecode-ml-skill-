# OpenCode MLflow Scripts

이 폴더는 `.opencode/skills`의 MLflow 5단계 흐름을 보조하는 로컬 스크립트를 포함한다.

대상은 사용자가 지정한 모델 프로젝트 폴더다.

## Script Mapping

```text
Step 1  프로젝트 구조 분석
        validate_mlflow_project.py

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

기존 모델 프로젝트를 실행하거나, 모델이 없으면 표준 샘플 3개 중 하나를 작업 경로에 준비한다.

기본값은 안전 모드다. 실제 실행은 `--execute`를 명시해야 한다.
실행 전 `ai_studio.env` 필수 키가 있는지 확인한다.

```text
python .opencode/scripts/run_training.py --project <model-project-folder>
python .opencode/scripts/run_training.py --project <model-project-folder> --execute
```

표준 샘플 우선순위:

```text
sklearn_sample
pytorch_sample
tensorflow_sample
```

다른 샘플은 임의로 선택하지 않는다.

### test_local_sample.py

표준 샘플 자체를 테스트한다.

```text
python .opencode/scripts/test_local_sample.py --sample sklearn_sample
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
