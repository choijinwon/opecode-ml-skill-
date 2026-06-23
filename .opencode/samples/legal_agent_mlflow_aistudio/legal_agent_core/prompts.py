from __future__ import annotations


PROMPT_NAME = "legal-agent-basic-korean"
SAFETY_NOTICE = "본 답변은 일반적인 법률 정보이며, 구체적인 사건 판단은 변호사 등 전문가 상담이 필요합니다."

SYSTEM_PROMPT = """
당신은 기업 내부 AI Studio에 연결된 법률 정보 안내 에이전트입니다.
사용자의 질문을 법률 자문으로 단정하지 말고, 일반 정보와 확인 항목 중심으로 답변합니다.
불확실한 내용은 추정하지 않고 추가 확인이 필요하다고 말합니다.
항상 마지막에 전문가 상담 필요성을 짧게 안내합니다.
""".strip()

USER_PROMPT_TEMPLATE = """
[질문]
{question}

[분류]
{topic}

[참고 컨텍스트]
{contexts}

[응답 지침]
1. 핵심 답변을 먼저 제시합니다.
2. 확인해야 할 항목을 bullet로 정리합니다.
3. 법률 리스크가 있는 부분은 단정하지 않습니다.
4. 마지막에 면책 문구를 포함합니다.
""".strip()


def render_contexts(contexts: list[dict[str, str]]) -> str:
    if not contexts:
        return "관련 내부 문서가 없습니다. 일반 원칙으로 답변합니다."
    lines = []
    for item in contexts:
        lines.append(f"- {item['title']}: {item['content']}")
    return "\n".join(lines)


def render_prompt(question: str, topic: str, contexts: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": USER_PROMPT_TEMPLATE.format(
                question=question,
                topic=topic,
                contexts=render_contexts(contexts),
            ),
        },
    ]
