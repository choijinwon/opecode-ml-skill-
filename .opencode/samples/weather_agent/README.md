# Weather Agent MLflow Tracing Sample

로컬 Qwen 또는 OpenAI-compatible 서버를 호출하는 간단한 날씨 에이전트 샘플이다.
MLflow Tracing에는 다음 span이 기록된다.

- `weather_agent`: 전체 에이전트 실행
- `get_weather`: 날씨 도구 호출
- `call_qwen`: 로컬 Qwen LLM 호출

## Run

MLflow UI가 `http://127.0.0.1:5001`에서 실행 중인 상태에서:

```bash
.venv/bin/python .opencode/samples/weather_agent/weather_agent.py "서울 날씨 알려줘"
```

Qwen/Ollama 기본값:

```bash
export LOCAL_QWEN_BASE_URL=http://localhost:11434/v1
export LOCAL_QWEN_API_KEY=ollama
export WEATHER_AGENT_MODEL=qwen2.5-coder:14b
```

Qwen 서버가 꺼져 있거나 연결되지 않아도 fallback 응답을 반환하므로 MLflow trace 확인은 가능하다.

## Chat UI

웹 챗봇 화면을 실행하려면:

```bash
.venv/bin/uvicorn app:app --app-dir .opencode/samples/weather_agent --host 127.0.0.1 --port 8000
```

브라우저에서 `http://127.0.0.1:8000`을 열면 된다. 채팅 요청은 MLflow experiment
`weather-agent`에 trace와 chat session으로 기록된다.
