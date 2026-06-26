# OpenCode MLflow Scripts

이 폴더의 실행 스크립트는 유지보수를 위해 5개만 둔다.

```text
bootstrap_sample_project.py
check_environment.py
run_training.py
validate_mlflow_project.py
verify_mlflow.py
```

## validate_mlflow_project.py

모델 프로젝트 구조, `data/**` 모델 파일, 필수 폴더, 다음 단계를 분석한다.

```text
python .opencode/scripts/validate_mlflow_project.py --project <model-project-folder>
python .opencode/scripts/validate_mlflow_project.py --project <model-project-folder> --json
```

## bootstrap_sample_project.py

모델이 없을 때 `sklearn_sample`, `pytorch_sample`, `tensorflow_sample` 중 하나를 워크스페이스로 복사한다.

```text
python .opencode/scripts/bootstrap_sample_project.py --list
python .opencode/scripts/bootstrap_sample_project.py --project <model-project-folder> --sample sklearn --execute
```

## check_environment.py

Python, MLflow, 필수 폴더, `ai_studio.env` 상태를 확인한다. secret 값은 출력하지 않는다.
`--install-requirements`를 명시하면 `requirements.txt` 기준으로 패키지를 설치한다.
배포 오류 로그가 있으면 `--error-log`로 원인/조치 가이드를 출력한다.
`--qwen-diagnose`를 명시하면 `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL` 기준으로 Qwen 추가 진단을 수행한다.

```text
python .opencode/scripts/check_environment.py --project <model-project-folder>
python .opencode/scripts/check_environment.py --project <model-project-folder> --json
python .opencode/scripts/check_environment.py --project <model-project-folder> --install-requirements
python .opencode/scripts/check_environment.py --project <model-project-folder> --error-log deploy.log
python .opencode/scripts/check_environment.py --project <model-project-folder> --error-log deploy.log --qwen-diagnose
```

## run_training.py

모델 준비와 실행을 담당한다.

- 필수 폴더와 기본 파일 생성
- `aiu_studio/` 실행 템플릿 폴더 복사
- 모델 파일은 `aiu_studio/`로 복사하지 않고 `data/**`에서 직접 읽음
- `runtest.py`를 우선 참조해서 선택 모델 기준 `runtest_2.py` 생성
- 일반 `run_test.py`, `run_test2.py` 생성
- 필요 시 생성된 entrypoint 실행

`--target-index` 또는 `--target-model`을 사용하면 선택 모델 기준으로 아래 항목을 자동 처리한다.

```text
6. MODEL_PATH = DATA_MODEL_PATH
7. runtest.py 우선 참조, 없으면 run_test.py 참조
8. 선택 모델 형식에 맞는 runtest_2.py 생성
```

```text
python .opencode/scripts/run_training.py --project <model-project-folder>
python .opencode/scripts/run_training.py --project <model-project-folder> --execute
python .opencode/scripts/run_training.py --project <model-project-folder> --target-index 1 --output runtest_2.py --force
python .opencode/scripts/run_training.py --project <model-project-folder> --target-model data/model.pkl --template runtest.py --output runtest_2.py --force
```

## verify_mlflow.py

MLflow experiment run, artifact, model registry를 확인하고 분석 결과 리포트를 출력한다.
리포트에는 `status`, `summary`, run/artifact/model/registry 상태, 후속 조치가 포함된다.

```text
python .opencode/scripts/verify_mlflow.py --tracking-uri http://127.0.0.1:5000 --experiment-name <name>
python .opencode/scripts/verify_mlflow.py --tracking-uri http://127.0.0.1:5000 --experiment-id <id> --registered-model <model-name>
```
