# sklearn_sample

scikit-learn 기반 로컬 모델 프로젝트 예시다.

구성:

- `requirements.txt`
- `train.py`
- `register_model.py`
- `run_model.py`
- `aiu_custom/`
- `config.json`
- `input_example.json`
- `artifacts/`

사용 흐름:

1. 의존성을 설치한다.
2. 학습 단계에서 `artifacts/model.joblib`가 생성되는 구조를 확인한다.
3. OpenCode에서 이 폴더를 기준으로 skill 점검을 요청한다.

AI Studio 스타일 pyfunc 등록 흐름에서는 `run_model.py`가 등록 전 사전 준비 검증 기능과 등록 기능을 분리해 제공하는지 확인한다.
OpenCode 챗봇 응답에서는 사용자가 이 파일을 직접 실행하도록 지시하지 않고, 해당 기능이 있는지와 부족한 설정이 무엇인지 안내한다.

`run_model.py`는 `mlflow.pyfunc.log_model(..., code_paths=["aiu_custom"])` 구조를 사용하므로 `aiu_custom/` 폴더는 필수 구성이다.
