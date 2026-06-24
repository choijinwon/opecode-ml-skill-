# sklearn_sample

폐쇄망에서 사용자가 sklearn 계열 모델 샘플을 넣는 기본 폴더입니다.

이 폴더는 기본 자리만 제공합니다. 실제 모델 코드, 데이터, artifact는 사용 환경에 맞게 추가합니다.

권장 구조:

```text
aiu_custom/
local_serving/
save_model/
run_model.py
input_example.json
requirements.txt
ai_studio.env.example
```

주의:

- 실제 API key, password, token 값은 넣지 않습니다.
- Git에는 `.env`, `ai_studio.env`, 대용량 모델 artifact를 올리지 않습니다.
- 루트 복사용 선택형 샘플은 `weather`, `legal`, `design`이고, 이 폴더는 사용자 모델 슬롯입니다.
