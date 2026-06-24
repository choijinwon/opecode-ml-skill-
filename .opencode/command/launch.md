---
description: Show the MLflow model project launch guide on demand.
agent: launch
---

Show the short Launch Guide again, then ask the user which area they want to inspect next.

Use this exact guide:

```text
[Launch Guide]
이 프로젝트는 MLflow 모델 프로젝트 분석과 샘플 생성을 돕는 OpenCode 패키지입니다.
처음 진입하면 워크스페이스를 먼저 분석해 모델 있음/없음을 확인합니다.

모델이 있으면 본인 모델 경로를 기준으로 MLflow 5단계를 진행합니다.
모델이 없으면 sklearn / pytorch / tensorflow 중 하나를 선택해 샘플 폴더를 생성합니다.

샘플 생성 결과는 <workspace>/sklearn_sample/ 같은 폴더로 복사됩니다.

추천 첫 요청:
- 이 워크스페이스를 MLflow 5단계 기준으로 분석해줘.
- 모델이 없으면 sklearn 샘플로 생성해줘.

보안 규칙: API key, password, token 값은 출력하지 않고 서버 배포 시 Secret/환경변수를 사용합니다.
상세 가이드: .opencode/LAUNCH_GUIDE.md
```
