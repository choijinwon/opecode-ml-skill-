# Sample Projects

이 폴더는 OpenCode skill pack과 함께 배포하는 정적 샘플 프로젝트를 포함한다.

포함된 샘플:

- `pytorch_sample`
- `sklearn_sample`
- `tensorflow_sample`

공통 원칙:

- 각 샘플은 skill 점검 대상이 되는 최소 프로젝트 구조를 제공한다.
- 실제 model artifact는 기본 포함하지 않고, 학습 단계가 수행되는 환경에서 생성한다.
- `register_model.py`는 등록 전 사전 준비 검증 단계와 MLflow 등록 흐름 예시를 담는다.
- `프로젝트 진입점`와 `aiu_custom/`은 AI Studio 스타일 pyfunc 등록 흐름 예시를 담는다.
- 샘플은 사용자가 자신의 프로젝트 구조를 이해하는 참고용이며, 고정 표준을 강제하지 않는다.
- OpenCode 챗봇 응답에서는 사용자에게 개별 Python 명령 실행을 지시하지 않고, 파일/기능 존재 여부와 보완 기준을 안내한다.

배포 전 로컬 환경 테스트:

- 샘플 구조 검증: `python .opencode/scripts/validate_mlflow_project.py --project .opencode/samples/sklearn_sample`
- 샘플 실행 준비: `python .opencode/scripts/run_training.py --project .opencode/samples/sklearn_sample --python /path/to/python3.12`
- 다른 샘플 검증: `python .opencode/scripts/validate_mlflow_project.py --project .opencode/samples/pytorch_sample`

테스트 흐름:

1. 샘플 폴더 안에 `.venv`를 만든다.
2. `requirements.txt`를 설치한다.
3. 학습 entrypoint를 호출해 artifact 생성을 확인한다.
4. 등록 전 사전 준비 검증 기능이 동작하는지 확인한다.
5. `프로젝트 진입점`가 있으면 AI Studio pyfunc용 사전 준비 검증 기능도 확인한다.

선택 동작:

- `--register`를 주면 MLflow 등록 예시까지 검증한다.

스킬 기준 검증:

- 자동 후보 선택: `python .opencode/scripts/validate_mlflow_project.py`
- 특정 샘플 검증: `python .opencode/scripts/validate_mlflow_project.py --project .opencode/samples/sklearn_sample`
- JSON 출력: `python .opencode/scripts/validate_mlflow_project.py --project .opencode/samples/sklearn_sample --json`
- 쓰기 권한 확인 제외: `python .opencode/scripts/validate_mlflow_project.py --project .opencode/samples/sklearn_sample --no-write-check`

Python 버전 조건:

- `kserve==0.15.0` 제약 때문에 Python 3.9~3.12를 사용해야 한다.
- Python 3.13 이상에서는 스크립트가 실패하도록 막아둔다.

의존성 메모:

- 샘플 실행용 `requirements.txt`는 로컬 설치 가능성을 우선한 목록이다.
- PyPI에서 해석되지 않는 패키지는 샘플 실행용 목록에서 제외했다.
