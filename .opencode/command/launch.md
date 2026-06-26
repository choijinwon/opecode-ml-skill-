---
description: Show the MLflow model project launch guide on demand.
agent: launch
---

Show the short Launch Guide again, then ask the user which area they want to inspect next.

Use this exact guide:

```text
[Launch Guide]
목적: MLflow 모델 프로젝트 분석, 샘플 생성, 배포 오류 가이드를 단계별로 진행합니다.
기준: 사용자가 가져온 모델 파일은 항상 프로젝트 루트의 data/ 하위 트리에 둡니다.

Process A. 모델이 있을 때
1. data/** 모델 탐지
2. model_artifact_paths에서 대상 모델 선택
3. aiu_studio/ 템플릿 폴더만 복사
4. 선택 모델을 직접 읽는 runtest_2.py 생성
5. 환경 검증, 추론 테스트, MLflow 분석 리포트 확인

Process B. 모델이 없을 때
1. 폐쇄망 모델을 data/** 아래로 반입
2. 재분석 후 모델이 발견되면 Process A 진행
3. 실제 모델 반입이 어려울 때만 sklearn / pytorch / tensorflow 샘플 선택
4. 선택 샘플을 폴더째 복사하고 해당 샘플 폴더 기준으로 진행

추천 첫 요청:
- 이 워크스페이스를 MLflow 5단계 기준으로 분석해줘.
- 1번 모델로 runtest_2.py 만들어줘.
- 모델이 없으면 sklearn 샘플로 생성해줘.
- 배포 오류 로그 분석해줘.

보안 규칙: API key, password, token 값은 출력하지 않고 서버 배포 시 Secret/환경변수를 사용합니다.
상세 가이드: .opencode/LAUNCH_GUIDE.md
```

<details>
<summary>모델이 있을 때</summary>

### Step 1. 모델 탐지 및 선택
- [ ] `data/**` 모델 목록 확인
- [ ] 모델 번호 또는 경로 선택

### Step 2. 자동 생성
- [ ] `aiu_studio/` 템플릿 폴더만 복사
- [ ] 선택 모델을 직접 읽는 `runtest_2.py` 생성

### Step 3. 검증
- [ ] 환경 검증
- [ ] 추론
- [ ] MLflow 분석 리포트 확인

</details>

<details>
<summary>모델이 없을 때</summary>

### Step 1. 모델 반입
- [ ] 폐쇄망 모델이 있으면 `data/**` 아래로 반입 후 재분석

### Step 2. 샘플 생성
- [ ] 모델 반입이 어렵다면 `sklearn` / `pytorch` / `tensorflow` 샘플 선택
- [ ] 선택 샘플을 폴더째 복사하고 해당 폴더 기준으로 진행

</details>
