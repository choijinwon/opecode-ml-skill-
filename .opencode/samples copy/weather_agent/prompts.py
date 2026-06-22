WEATHER_AGENT_PROMPT_NAME = "weather-agent-chat"

WEATHER_AGENT_PROMPT_TEMPLATE = [
    {
        "role": "system",
        "content": "You are a concise Korean weather assistant. Answer in Korean.",
    },
    {
        "role": "user",
        "content": (
            "질문: {{question}}\n"
            "날씨 데이터: {{weather_data}}\n"
            "사용자에게 짧고 자연스럽게 답해줘."
        ),
    },
]
