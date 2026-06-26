import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    project_dir = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    analyzer = Path(__file__).resolve().with_name("validate_mlflow_project.py")

    print("[Workspace Analysis]")

    if not analyzer.exists():
        print("- 상태: 분석 스크립트를 찾지 못했습니다.")
        print("- 다음 단계: OpenCode에서 '이 워크스페이스를 분석해줘'라고 요청하세요.")
        return 0

    try:
        result = subprocess.run(
            [sys.executable, str(analyzer), "--project", str(project_dir), "--json"],
            cwd=project_dir,
            check=False,
            capture_output=True,
            text=True,
            timeout=8,
        )
    except Exception as exc:
        print(f"- 상태: 분석 실패 ({exc})")
        print("- 다음 단계: OpenCode에서 '이 워크스페이스를 분석해줘'라고 요청하세요.")
        return 0

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = None

    if result.returncode != 0 and payload is None:
        print("- 상태: 분석 실패")
        detail = (result.stderr or result.stdout).strip().splitlines()
        if detail:
            print(f"- 사유: {detail[-1][:160]}")
        print("- 다음 단계: OpenCode에서 '이 워크스페이스를 분석해줘'라고 요청하세요.")
        return 0

    if payload is None:
        print("- 상태: 분석 결과 파싱 실패")
        print("- 다음 단계: OpenCode에서 '이 워크스페이스를 분석해줘'라고 요청하세요.")
        return 0

    checks = payload.get("checks", [])
    evidence = []
    review_items = []

    for check in checks:
        status = check.get("status")
        name = check.get("name", "")
        message = check.get("message", "")
        if status == "pass":
            evidence.extend(check.get("evidence", [])[:3])
        elif status in {"warn", "block", "fail"}:
            review_items.append(f"{name}: {message}")

    model_artifact_paths = payload.get("model_artifact_paths") or payload.get("data_model_files") or []
    model_found = bool(payload.get("model_found") or model_artifact_paths)
    data_dir_paths = payload.get("data_dir_paths") or []
    data_file_count = payload.get("data_file_count", 0)
    unsupported_data_files = payload.get("unsupported_data_files") or []

    print(f"- 분석 대상: {payload.get('selected_project', str(project_dir))}")
    print(f"- data/** 트리 상태: {'있음' if data_dir_paths else '없음'}")
    if data_dir_paths:
        print(f"- data/ 파일 수: {data_file_count}")
    print(f"- 모델 상태: {'있음' if model_found else '없음 또는 추가 확인 필요'}")
    if model_artifact_paths:
        print(f"- 선택 가능한 모델: {len(model_artifact_paths)}개")
        for index, item in enumerate(model_artifact_paths[:9], start=1):
            print(f"  {index}. {item}")
        if len(model_artifact_paths) > 9:
            print(f"  - 외 {len(model_artifact_paths) - 9}개")
    elif unsupported_data_files:
        print(f"- 지원하지 않는 data 파일: {len(unsupported_data_files)}개")
        for index, item in enumerate(unsupported_data_files[:5], start=1):
            print(f"  {index}. {item}")

    if evidence:
        print("- 발견 항목:")
        for item in sorted(set(str(x) for x in evidence if x))[:6]:
            print(f"  - {item}")

    if review_items:
        print("- 확인 필요:")
        for item in review_items[:4]:
            print(f"  - {item}")

    print("- 다음 단계:")
    if model_found:
        if len(model_artifact_paths) > 1:
            print("  - 판단 결과: needs_user_input (사용할 모델 번호 또는 경로 선택 필요)")
        else:
            print("  - 판단 결과: ready_for_selected_run_test")
        print("  - 먼저 위 모델 목록에서 사용할 모델 번호 또는 경로를 선택하세요.")
        print("  - 선택 후 프로젝트 루트에 aiu_studio/ 폴더를 생성/보존하고 data/** 파일을 병합 복사하세요.")
        print("  - 그 다음 선택 모델 형식에 맞게 runtest_2.py 생성을 진행하세요.")
        print("  - 이후 환경 검증, 추론 테스트, MLflow 등록 검증 순서로 진행하세요.")
        print("  - 실제 모델 선택/파일 생성/환경 검증 실행은 OpenCode 빌드모드에서 선택해주세요.")
        print("  - 추천 요청: 1번 모델로 runtest_2.py 만들어줘.")
    else:
        print("  - 판단 결과: needs_user_input (실제 모델 프로젝트 경로 지정 또는 data/** 반입 필요)")
        if data_dir_paths:
            print("  - data/ 트리는 있지만 지원 모델 확장자를 찾지 못했습니다.")
            print("  - .pkl, .joblib, .pt, .onnx, .keras 등 지원 모델 파일을 data/ 하위 폴더 어디든 넣어주세요.")
        else:
            print("  - 폐쇄망에 모델이 있으면 실제 모델 프로젝트 경로를 지정하거나 data/ 하위 트리로 반입한 뒤 다시 분석하세요.")
            print("  - 기존 모델을 반입하지 못할 때만 sklearn / pytorch / tensorflow 중 하나를 선택해 샘플을 생성할 수 있습니다.")
        print("  - 실제 샘플 복사/모델 생성/검증 실행은 OpenCode 빌드모드에서 선택해주세요.")
        print("  - 추천 요청: 모델이 없으니 sklearn 샘플로 생성해줘.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
