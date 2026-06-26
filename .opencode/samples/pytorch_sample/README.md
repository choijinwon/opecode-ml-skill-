# pytorch_sample

폐쇄망에서 사용자가 PyTorch 계열 모델 샘플을 넣는 기본 폴더입니다.

이 폴더는 기본 자리만 제공합니다. 실제 모델 코드, 데이터, artifact는 사용 환경에 맞게 추가합니다.

권장 구조:

```text
aiu_custom/
local_serving/
save_model/
aiu_studio/
프로젝트 진입점
input_example.json
requirements.txt
```

PyTorch 모델 파일(`.pt`, `.pth`, `.ckpt`, `.bin`, `.safetensors`)을 실제 로드하려면 실행 환경에 `torch`가 필요합니다.
폐쇄망에서는 내부 패키지 저장소나 사전 설치된 Python 환경을 사용하세요.

주의:

- 실제 API key, password, token 값은 넣지 않습니다.
- Git에는 `.env`, 대용량 모델 artifact를 올리지 않습니다.
- 사용자 워크스페이스에 모델이 없으면 `sklearn`, `pytorch`, `tensorflow` 중 하나로 이 폴더를 루트에 복사할 수 있습니다.
