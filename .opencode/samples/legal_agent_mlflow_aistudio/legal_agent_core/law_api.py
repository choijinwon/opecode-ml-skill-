from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from legal_agent_core.config import load_env_file


def law_api_settings() -> dict[str, str]:
    load_env_file()
    return {
        "oc": os.getenv("LAW_API_OC", ""),
        "base_url": os.getenv("LAW_API_BASE_URL", "http://www.law.go.kr/DRF/lawSearch.do"),
        "target": os.getenv("LAW_API_TARGET", "eflaw"),
    }


def build_law_search_params(
    query: str,
    display: int = 5,
    page: int = 1,
    response_type: str = "XML",
) -> dict[str, str]:
    """법제처 lawSearch.do 법령검색 요청 변수를 만든다.

    기본 요청 변수:
    - OC: OpenAPI 사용자 인증값
    - target: 목록조회 대상. 활용가이드 예시는 현행법령 기준 eflaw
    - type: XML 또는 JSON
    - query: 검색어
    - display: 조회 건수
    - page: 페이지 번호
    """
    settings = law_api_settings()
    return {
        "OC": settings["oc"],
        "target": settings["target"],
        "type": response_type,
        "query": query,
        "display": str(display),
        "page": str(page),
    }


def search_law_guide(query: str, display: int = 5) -> list[dict[str, str]]:
    """국가법령정보 법령검색 API에서 법률 가이드를 조회한다.

    LAW_API_OC가 없거나 API 호출이 실패하면 빈 목록을 반환한다.
    에이전트는 빈 목록일 때 로컬 샘플 지식으로 fallback한다.
    """
    settings = law_api_settings()
    if not settings["oc"]:
        return []

    params = build_law_search_params(query=query, display=display)
    url = f"{settings['base_url']}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            body = response.read().decode("utf-8", errors="replace")
    except Exception:
        return []

    if params["type"].upper() == "JSON":
        return _parse_json_response(body)
    return _parse_xml_response(body)


def _parse_json_response(body: str) -> list[dict[str, str]]:
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return []

    law_items = payload.get("LawSearch", {}).get("law", [])
    if isinstance(law_items, dict):
        law_items = [law_items]

    results = []
    for item in law_items:
        title = str(item.get("법령명한글") or item.get("lawNm") or item.get("title") or "")
        law_id = str(item.get("법령ID") or item.get("lawId") or "")
        link = _normalize_law_link(str(item.get("법령상세링크") or item.get("lawServiceUrl") or ""))
        if title:
            results.append(
                {
                    "id": law_id or title,
                    "title": title,
                    "content": f"국가법령정보 목록조회 결과입니다. 본문조회 상세 링크: {link or '미제공'}",
                    "source": "law.go.kr",
                    "detail_link": link,
                }
            )
    return results


def _parse_xml_response(body: str) -> list[dict[str, str]]:
    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        return []

    results = []
    for law in root.findall(".//law"):
        title = _find_text(law, ["법령명한글", "lawNm", "법령명"])
        law_id = _find_text(law, ["법령ID", "lawId"])
        link = _normalize_law_link(_find_text(law, ["법령상세링크", "lawServiceUrl", "상세링크"]))
        if title:
            results.append(
                {
                    "id": law_id or title,
                    "title": title,
                    "content": f"국가법령정보 목록조회 결과입니다. 본문조회 상세 링크: {link or '미제공'}",
                    "source": "law.go.kr",
                    "detail_link": link,
                }
            )
    return results


def _find_text(element: ET.Element, names: list[str]) -> str:
    for name in names:
        found = element.find(name)
        if found is not None and found.text:
            return found.text.strip()
    return ""


def _normalize_law_link(link: str) -> str:
    if not link:
        return ""
    if link.startswith("http://") or link.startswith("https://"):
        return link
    if link.startswith("/"):
        return f"https://www.law.go.kr{link}"
    return link
