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

전체 프로세스를 복사해야 하면 아래 블록을 사용한다.

```text
[OpenCode MLflow 모델 프로젝트 진행 프로세스]

0. 기본 기준
- 사용자가 가져온 모델 파일은 항상 프로젝트 루트의 data/ 하위 트리에 둔다.
- API key, password, token 값은 출력하지 않는다.
- 서버 배포 시 secret 값은 Secret 또는 환경변수로 주입한다.

1. 워크스페이스 분석
- 현재 분석 경로가 실제 모델 프로젝트인지 확인한다.
- data/** 하위에서 모델 파일을 전체 탐색한다.
- 모델이 발견되면 model_found: true와 model_artifact_paths 목록을 제공한다.
- 모델이 발견되지 않으면 model_found: false로 보고하고 모델 반입 또는 샘플 생성을 안내한다.

2. 모델이 있을 때
- 사용자가 model_artifact_paths에서 대상 모델 번호 또는 경로를 선택한다.
- 선택 모델 확장자를 기준으로 모델 형식을 판별한다.
- aiu_studio/ 실행 템플릿 폴더만 프로젝트 루트로 복사한다.
- 모델 파일은 aiu_studio/로 복사하지 않고 data/** 원본 위치에서 직접 읽는다.
- runtest.py를 우선 참조하고, 없으면 run_test.py를 참조한다.
- 선택 모델을 직접 읽는 runtest_2.py를 생성한다.

3. 모델이 없을 때
- 폐쇄망에 실제 모델이 있으면 모델 프로젝트 경로를 지정하거나 data/** 아래로 반입한다.
- 반입 후 워크스페이스를 다시 분석한다.
- 재분석에서 모델이 발견되면 모델 있음 프로세스로 전환한다.
- 실제 모델 반입이 어려울 때만 sklearn / pytorch / tensorflow 샘플 중 하나를 선택한다.
- 선택한 샘플은 루트에 풀지 않고 샘플 폴더째 복사한다.
- 복사된 샘플 폴더 기준으로 다시 모델 있음 프로세스를 진행한다.

4. 환경 검증
- Python 실행 환경을 확인한다.
- MLflow 설치 여부를 확인한다.
- requirements.txt가 있으면 필요한 패키지를 확인한다.
- 설치가 필요한 경우 명시적으로 --install-requirements 옵션을 선택한다.
- secret 값은 값 자체가 아니라 set, empty, missing 상태만 확인한다.

5. 추론 테스트
- 생성된 runtest_2.py로 선택 모델 로드가 가능한지 확인한다.
- aiu_custom/predict.py 기준으로 추론 가능 여부를 확인한다.
- 입력 예시는 input_example.json 또는 프로젝트 기본 입력을 사용한다.

6. MLflow 분석 리포트
- verify_mlflow.py로 MLflow Run 생성 여부를 확인한다.
- artifact 기록 여부를 확인한다.
- model registry 기록 여부를 확인한다.
- 결과는 pass / warn / block 상태로 정리한다.
- block 상태이면 후속 조치 가이드를 함께 제공한다.

7. 배포 오류 처리
- 배포 오류 로그 또는 에러 메시지를 수집한다.
- secret 값은 제거하거나 마스킹한다.
- check_environment.py --error-log deploy.log로 룰 기반 오류 가이드를 확인한다.
- 폐쇄망 Qwen endpoint가 있으면 --qwen-diagnose로 추가 진단한다.
- 조치 후 환경 검증과 MLflow 분석 리포트를 다시 확인한다.
```

모델이 있을 때 상세 프로세스만 복사해야 하면 아래 블록을 사용한다.

```text
[모델이 있을 때 상세 진행 프로세스]

전제
- 사용자가 가져온 모델 파일은 프로젝트 루트의 data/ 하위 트리에 존재한다.
- 모델 파일은 aiu_studio/로 복사하지 않는다.
- aiu_studio/는 실행 템플릿 폴더만 복사한다.
- 선택된 모델은 data/** 원본 경로에서 직접 읽는다.
- secret 값은 출력하지 않고 set, empty, missing 상태만 확인한다.

Step 1. 프로젝트 기준 경로 확인
- 사용자가 지정한 모델 프로젝트 폴더를 기준으로 분석한다.
- 현재 작업 경로가 실제 모델 프로젝트 루트인지 확인한다.
- 필수 폴더 aiu_custom/, local_serving/, save_model/ 존재 여부를 확인한다.
- ai_studio.env 또는 환경변수는 값이 아니라 존재 여부만 확인한다.

Step 2. data/ 하위 모델 탐지
- 프로젝트 루트 기준 data/** 전체를 재귀 탐색한다.
- .pkl, .joblib, .pickle, .pt, .pth, .onnx, .keras, .h5, .pb, .sav 등 모델 확장자를 확인한다.
- 모델 파일이 하나 이상 발견되면 model_found: true로 판단한다.
- 발견된 모델은 model_artifact_paths 목록으로 번호와 경로를 제공한다.

Step 3. 대상 모델 선택
- 사용자가 model_artifact_paths 목록에서 사용할 모델 번호 또는 경로를 선택한다.
- 모델이 1개뿐이어도 기본 선택값으로 제안하고 사용자의 선택을 확인한다.
- 선택 이후에는 프로젝트 분석을 반복하지 않고 선택 모델 실행 파일 생성 단계로 진행한다.

Step 4. 모델 형식 판별
- 선택된 모델 파일의 확장자를 기준으로 모델 로더 방식을 결정한다.
- .pkl, .pickle, .joblib, .sav는 pickle/joblib 계열로 처리한다.
- .pt, .pth는 PyTorch 계열로 처리한다.
- .onnx는 ONNX Runtime 계열로 처리한다.
- .keras, .h5는 Keras/TensorFlow 계열로 처리한다.
- 지원하지 않는 형식이면 unsupported model format으로 보고하고 필요한 로더 구현 가이드를 제공한다.

Step 5. aiu_studio/ 템플릿 준비
- 프로젝트 루트에 aiu_studio/ 폴더가 없으면 템플릿 폴더를 복사한다.
- 이미 aiu_studio/ 폴더가 있으면 기존 파일을 보존하고 필요한 파일만 확인한다.
- 모델 파일은 aiu_studio/ 안으로 복사하지 않는다.
- aiu_studio/는 AI Studio 실행에 필요한 predict, serving, config, helper 파일 중심으로 관리한다.

Step 6. runtest.py 참조
- 프로젝트에 runtest.py가 있으면 우선 참조한다.
- runtest.py가 없고 run_test.py가 있으면 run_test.py를 참조한다.
- 둘 다 없으면 선택 모델 형식에 맞는 기본 실행 템플릿을 사용한다.
- 기존 실행 파일의 입력 구조, predict 호출 방식, 반환 형식을 최대한 유지한다.

Step 7. runtest_2.py 생성
- 선택된 모델 경로를 DATA_MODEL_PATH로 고정한다.
- MODEL_PATH = DATA_MODEL_PATH 방식으로 data/** 원본 모델을 직접 읽게 만든다.
- 선택 모델 형식에 맞는 로더 코드를 생성한다.
- aiu_custom/predict.py와 연결 가능한 형태로 추론 함수를 구성한다.
- 생성 결과는 프로젝트 루트 또는 aiu_studio/ 실행 기준에서 호출 가능해야 한다.

Step 8. 환경 검증
- Python 실행 가능 여부를 확인한다.
- MLflow 설치 여부를 확인한다.
- requirements.txt가 있으면 필요한 패키지 목록을 확인한다.
- 패키지가 누락되면 설치 명령을 제안한다.
- 자동 설치는 사용자가 명시적으로 선택한 경우에만 진행한다.

Step 9. 선택 모델 로드 테스트
- 생성된 runtest_2.py로 선택 모델이 정상 로드되는지 확인한다.
- import 오류, 파일 경로 오류, 로더 오류를 분리해서 보고한다.
- torch, onnxruntime, tensorflow, joblib 등 필요한 패키지가 없으면 누락 패키지로 안내한다.

Step 10. 추론 테스트
- input_example.json이 있으면 해당 입력으로 추론한다.
- input_example.json이 없으면 모델 형식별 기본 샘플 입력을 사용한다.
- aiu_custom/predict.py 기준으로 입력과 출력 구조가 맞는지 확인한다.
- 추론 결과 또는 오류 메시지를 요약한다.

Step 11. MLflow 분석 리포트
- verify_mlflow.py로 MLflow Run 생성 여부를 확인한다.
- artifact 기록 여부를 확인한다.
- model registry 기록 여부를 확인한다.
- 결과를 pass, warn, block 상태로 정리한다.
- block 상태이면 원인과 다음 조치 가이드를 함께 제공한다.

Step 12. 다음 조치
- pass이면 AI Studio endpoint 연결 또는 배포 검증 단계로 진행한다.
- warn이면 누락된 artifact, registry, dependency를 보완한다.
- block이면 오류 로그를 기준으로 배포 오류 가이드를 실행한다.
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
