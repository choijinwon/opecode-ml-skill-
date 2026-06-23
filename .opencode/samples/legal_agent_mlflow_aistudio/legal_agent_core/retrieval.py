from __future__ import annotations

import mlflow
from mlflow.entities import SpanType

from legal_agent_core.law_api import search_law_guide


LEGAL_KNOWLEDGE_BASE = [
    {
        "id": "contract-termination",
        "title": "계약 해지 검토",
        "keywords": ["계약", "해지", "위약", "통보", "해제"],
        "content": "계약 해지는 계약서의 해지 조항, 통지 방식, 위약금, 손해배상 조항을 먼저 확인해야 합니다.",
    },
    {
        "id": "employment",
        "title": "근로/인사 이슈",
        "keywords": ["근로", "해고", "연차", "임금", "징계"],
        "content": "근로 이슈는 취업규칙, 근로계약서, 징계 절차, 서면 통지 여부가 중요합니다.",
    },
    {
        "id": "privacy",
        "title": "개인정보 처리",
        "keywords": ["개인정보", "동의", "파기", "위탁", "보관"],
        "content": "개인정보는 수집 목적, 동의 근거, 보관 기간, 제3자 제공 여부를 기준으로 점검합니다.",
    },
    {
        "id": "ip",
        "title": "지식재산권",
        "keywords": ["저작권", "상표", "특허", "라이선스", "소스"],
        "content": "지식재산권은 권리 귀속, 이용 허락 범위, 2차적 저작물, 오픈소스 라이선스를 확인합니다.",
    },
]


@mlflow.trace(name="retrieve_legal_context", span_type=SpanType.RETRIEVER)
def retrieve_legal_context(question: str, limit: int = 2) -> list[dict[str, str]]:
    """간단한 키워드 기반 검색 예시다.

    LAW_API_OC가 있으면 국가법령정보 법령검색 API를 먼저 조회한다.
    없거나 실패하면 로컬 샘플 지식으로 fallback한다.
    실제 AI Studio 적용 시 이 부분은 사내 문서 검색 API, vector DB, RAG 검색 API로 교체할 수 있다.
    """
    law_api_results = search_law_guide(question, display=limit)
    if law_api_results:
        return law_api_results

    normalized = question.lower()
    scored: list[tuple[int, dict[str, str]]] = []
    for item in LEGAL_KNOWLEDGE_BASE:
        score = sum(1 for keyword in item["keywords"] if keyword in normalized)
        if score:
            scored.append((score, item))
    scored.sort(key=lambda row: row[0], reverse=True)
    return [item for _, item in scored[:limit]]
