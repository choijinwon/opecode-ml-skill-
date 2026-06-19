# tensorflow_sample

TensorFlow/Keras 기반 로컬 모델 프로젝트 예시다.

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
2. 학습 단계에서 `artifacts/model.keras`가 생성되는 구조를 확인한다.
3. OpenCode에서 이 폴더를 기준으로 skill 점검을 요청한다.

AI Studio 스타일 pyfunc 등록 흐름에서는 `aiu_custom/` 폴더가 필수 구성이다.
