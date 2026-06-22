from __future__ import annotations


def answer_weather(question: str) -> str:
    city = "서울"
    for candidate in ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "제주"]:
        if candidate in question:
            city = candidate
            break
    return (
        f"{city} 기준 폐쇄망 데모 응답입니다. "
        "현재 날씨 시스템은 MLflow registry/judge 데모용으로 연결되었습니다."
    )

