import json
import os
import re
import urllib.error
import urllib.request

import mlflow
from mlflow.entities import SpanType

from offline_weather_agent_core.documents import LOCAL_DOCUMENTS


def _tokens(text: str) -> set[str]:
    """간단한 폐쇄망 검색용 토큰화. 외부 embedding 모델 없이 동작한다."""
    normalized = text.lower()
    return {token for token in re.split(r"[^0-9a-zA-Z가-힣.]+", normalized) if len(token) >= 2}


def _score(query_tokens: set[str], document_text: str) -> int:
    document_tokens = _tokens(document_text)
    return len(query_tokens & document_tokens)


def _normalize_api_results(raw_results: object) -> list[dict[str, str]]:
    """검색 API 응답을 agent 내부 표준 형태로 맞춘다."""
    if not isinstance(raw_results, list):
        return []

    normalized = []
    for index, item in enumerate(raw_results):
        if not isinstance(item, dict):
            continue
        text = str(item.get("text") or item.get("content") or item.get("body") or "").strip()
        if not text:
            continue
        normalized.append(
            {
                "id": str(item.get("id") or item.get("doc_id") or f"api-{index + 1}"),
                "title": str(item.get("title") or item.get("source") or "검색 문서"),
                "text": text,
            }
        )
    return normalized


def _retrieve_from_api(question: str, top_k: int) -> list[dict[str, str]]:
    """로컬 문서 검색 API가 설정되어 있으면 API에서 검색 결과를 가져온다."""
    search_url = os.getenv("RAG_SEARCH_API_URL", "").strip()
    if not search_url:
        return []

    payload = {
        "query": question,
        "top_k": top_k,
    }
    request = urllib.request.Request(
        search_url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            **({"Authorization": f"Bearer {os.getenv('RAG_SEARCH_API_KEY')}"} if os.getenv("RAG_SEARCH_API_KEY") else {}),
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=float(os.getenv("RAG_SEARCH_TIMEOUT_SECONDS", "5"))) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (TimeoutError, urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        return []

    if isinstance(body, dict):
        return _normalize_api_results(body.get("results") or body.get("documents") or body.get("data"))
    return _normalize_api_results(body)


def _retrieve_from_local_documents(question: str, top_k: int) -> list[dict[str, str]]:
    """API가 없거나 실패했을 때 사용하는 의존성 없는 로컬 fallback 검색."""
    query_tokens = _tokens(question)
    ranked = sorted(
        (
            (_score(query_tokens, f"{document['title']} {document['text']}"), document)
            for document in LOCAL_DOCUMENTS
        ),
        key=lambda item: item[0],
        reverse=True,
    )
    return [
        {
            "id": document["id"],
            "title": document["title"],
            "text": document["text"],
        }
        for score, document in ranked[:top_k]
        if score > 0
    ]


@mlflow.trace(name="retrieve_local_context", span_type=SpanType.RETRIEVER)
def retrieve_context(question: str, top_k: int = 2) -> list[dict[str, str]]:
    """질문과 관련 있는 로컬 문서를 찾는다.

    RAG_SEARCH_API_URL이 있으면 검색 API를 호출한다.
    API가 없거나 실패하면 의존성 없는 keyword retrieval로 fallback한다.
    """
    api_results = _retrieve_from_api(question, top_k)
    if api_results:
        return api_results[:top_k]
    return _retrieve_from_local_documents(question, top_k)


def context_text(contexts: list[dict[str, str]]) -> str:
    """검색된 문서를 프롬프트에 넣기 쉬운 문자열로 변환한다."""
    if not contexts:
        return "관련 로컬 문서 없음"
    return "\n".join(
        f"- [{context['id']}] {context['title']}: {context['text']}" for context in contexts
    )
