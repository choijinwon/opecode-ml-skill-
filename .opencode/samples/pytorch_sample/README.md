# pytorch_sample

PyTorch 기반 로컬 모델 프로젝트 예시다.

구성:

- `requirements.txt`
- `train.py`
- `register_model.py`
- `config.json`
- `input_example.json`
- `artifacts/`

사용 흐름:

1. 의존성을 설치한다.
2. `train.py`를 실행해 `artifacts/model.pt`를 생성한다.
3. OpenCode에서 이 폴더를 기준으로 skill 점검을 요청한다.

이 샘플은 CPU 환경 기준의 간단한 분류 모델 예시다.
