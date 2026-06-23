from __future__ import annotations

import json
import urllib.error
import urllib.request

import mlflow
from mlflow.entities import SpanType

from legal_agent_core.config import ai_studio_settings
from legal_agent_core.prompts import SAFETY_NOTICE


def _fallback_answer(question: str, topic: str, contexts: list[dict[str, str]], reason: str) -> str:
    context_text = contexts[0]["content"] if contexts else "질문과 관련된 계약서, 사내 규정, 법령 근거를 먼저 확인해야 합니다."
    return (
        f"질문은 '{topic}' 영역으로 보입니다.\n\n"
        f"핵심 확인 사항은 다음과 같습니다.\n"
        f"- {context_text}\n"
        f"- 사실관계, 문서 원본, 통지 시점, 상대방 답변 기록을 함께 확인해야 합니다.\n"
        f"- 결론을 단정하기 전에 관할 법령과 계약 조항을 대조해야 합니다.\n\n"
        f"{SAFETY_NOTICE}\n"
        f"(local fallback: {reason})"
    )


@mlflow.trace(name="call_ai_studio_llm", span_type=SpanType.LLM)
def call_ai_studio_llm(
    question: str,
    topic: str,
    messages: list[dict[str, str]],
    contexts: list[dict[str, str]],
) -> str:
    """OpenAI 호환 AI Studio endpoint를 호출한다.

    OPENAI_BASE_URL은 보통 http://host:port/v1 형태다.
    네트워크/키가 없으면 폐쇄망 개발 중에도 샘플이 돌도록 fallback 답변을 반환한다.
    """
    settings = ai_studio_settings()
    if not settings["base_url"] or not settings["api_key"]:
        return _fallback_answer(question, topic, contexts, "missing endpoint or api key")

    payload = {
        "model": settings["model"],
        "messages": messages,
        "temperature": 0.2,
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
        answer = body["choices"][0]["message"]["content"].strip()
        if SAFETY_NOTICE not in answer:
            answer = f"{answer}\n\n{SAFETY_NOTICE}"
        return answer
    except (KeyError, TimeoutError, urllib.error.URLError, urllib.error.HTTPError) as exc:
        return _fallback_answer(question, topic, contexts, exc.__class__.__name__)
