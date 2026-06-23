from __future__ import annotations

import mlflow
from mlflow.entities import SpanType


DESIGN_GUIDELINES = [
    {
        "id": "dashboard",
        "title": "운영형 대시보드",
        "keywords": ["대시보드", "admin", "관리자", "saas", "crm", "운영"],
        "content": "운영 도구는 정보 밀도, 스캔성, 필터/정렬, 반복 작업 효율을 우선한다.",
    },
    {
        "id": "onboarding",
        "title": "온보딩 화면",
        "keywords": ["온보딩", "가입", "시작", "튜토리얼", "첫 화면"],
        "content": "온보딩은 핵심 행동을 1개로 줄이고, 입력 단계와 진행 상태를 명확히 보여준다.",
    },
    {
        "id": "brand",
        "title": "브랜드 일관성",
        "keywords": ["브랜드", "톤", "카피", "색상", "로고"],
        "content": "브랜드 표현은 색상, 타이포그래피, 문장 톤, 이미지 스타일을 일관되게 유지한다.",
    },
    {
        "id": "landing",
        "title": "랜딩 페이지",
        "keywords": ["랜딩", "홈페이지", "마케팅", "소개", "전환"],
        "content": "랜딩은 첫 화면에서 대상, 제안, 주요 행동이 즉시 이해되어야 한다.",
    },
    {
        "id": "accessibility",
        "title": "접근성",
        "keywords": ["접근성", "색약", "대비", "키보드", "모바일"],
        "content": "텍스트 대비, 포커스 상태, 터치 영역, 반응형 레이아웃을 기본 조건으로 점검한다.",
    },
]


@mlflow.trace(name="retrieve_design_guidelines", span_type=SpanType.RETRIEVER)
def retrieve_design_guidelines(request: str, limit: int = 3) -> list[dict[str, str]]:
    normalized = request.lower()
    scored: list[tuple[int, dict[str, str]]] = []
    for item in DESIGN_GUIDELINES:
        score = sum(1 for keyword in item["keywords"] if keyword in normalized)
        if score:
            scored.append((score, item))
    scored.sort(key=lambda row: row[0], reverse=True)
    return [item for _, item in scored[:limit]]
