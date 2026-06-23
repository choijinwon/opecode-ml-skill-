from __future__ import annotations

import json
import urllib.error
import urllib.request

import mlflow
from mlflow.entities import SpanType

from design_agent_core.config import ai_studio_settings


def _fallback_answer(request: str, task_type: str, guidelines: list[dict[str, str]], reason: str) -> str:
    guide = guidelines[0]["content"] if guidelines else "사용자 목표, 핵심 행동, 정보 구조를 먼저 정의해야 합니다."
    return (
        f"1. 목표\n{request} 요청을 '{task_type}' 디자인 브리프로 정리합니다.\n\n"
        f"2. 대상 사용자\n주요 사용자는 빠르게 정보를 이해하고 다음 행동을 결정해야 하는 사용자입니다.\n\n"
        f"3. 화면/콘텐츠 구조\n- 첫 영역: 핵심 가치와 주요 행동\n- 본문: 주요 기능, 사용 흐름, 신뢰 요소\n- 하단: 다음 행동 또는 문의 경로\n\n"
        f"4. 시각 스타일\n- {guide}\n- 색상은 2~3개 역할 중심으로 제한하고, 강조색은 주요 행동에만 사용합니다.\n\n"
        f"5. 컴포넌트/인터랙션\n- 명확한 CTA\n- 상태가 보이는 입력/필터/카드\n- 모바일에서 한 손 조작 가능한 간격\n\n"
        f"6. 접근성/주의사항\n- 텍스트 대비와 터치 영역을 확보합니다.\n- 과장 표현과 모호한 마케팅 문구는 피합니다.\n\n"
        f"7. 다음 작업\n와이어프레임, 카피 초안, 컴포넌트 목록을 분리해 작성합니다.\n\n"
        f"(local fallback: {reason})"
    )


@mlflow.trace(name="call_ai_studio_llm", span_type=SpanType.LLM)
def call_ai_studio_llm(
    request_text: str,
    task_type: str,
    messages: list[dict[str, str]],
    guidelines: list[dict[str, str]],
) -> str:
    settings = ai_studio_settings()
    if not settings["base_url"] or not settings["api_key"]:
        return _fallback_answer(request_text, task_type, guidelines, "missing endpoint or api key")

    payload = {
        "model": settings["model"],
        "messages": messages,
        "temperature": 0.3,
        "stream": False,
    }
    request = urllib.request.Request(
        f"{settings['base_url']}/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings['api_key']}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"].strip()
    except (KeyError, TimeoutError, urllib.error.URLError, urllib.error.HTTPError) as exc:
        return _fallback_answer(request_text, task_type, guidelines, exc.__class__.__name__)
