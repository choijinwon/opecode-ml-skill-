from __future__ import annotations


PROMPT_NAME = "design-agent-brief-korean"

SYSTEM_PROMPT = """
당신은 AI Studio에 연결된 디자인 에이전트입니다.
사용자의 요청을 제품/브랜드/화면/콘텐츠 디자인 브리프로 구조화합니다.
추상적인 표현보다 실행 가능한 레이아웃, 톤, 컴포넌트, 금지사항을 제안합니다.
브랜드 일관성, 접근성, 사용자 흐름을 반드시 고려합니다.
""".strip()

USER_PROMPT_TEMPLATE = """
[디자인 요청]
{request}

[작업 분류]
{task_type}

[참고 가이드]
{guidelines}

[응답 형식]
1. 목표
2. 대상 사용자
3. 화면/콘텐츠 구조
4. 시각 스타일
5. 컴포넌트/인터랙션
6. 접근성/주의사항
7. 다음 작업
""".strip()


def render_guidelines(guidelines: list[dict[str, str]]) -> str:
    if not guidelines:
        return "관련 디자인 가이드가 없습니다. 일반 UX/UI 원칙으로 답변합니다."
    return "\n".join(f"- {item['title']}: {item['content']}" for item in guidelines)


def render_prompt(
    request: str,
    task_type: str,
    guidelines: list[dict[str, str]],
) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": USER_PROMPT_TEMPLATE.format(
                request=request,
                task_type=task_type,
                guidelines=render_guidelines(guidelines),
            ),
        },
    ]
