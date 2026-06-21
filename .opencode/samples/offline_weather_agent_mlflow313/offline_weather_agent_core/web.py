import uuid

import mlflow
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from offline_weather_agent_core.config import configure_mlflow, configure_tracing_destination
from offline_weather_agent_core.core import answer_weather

FRAMEWORK_OPTIONS = {"core", "langchain", "langgraph"}


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    user_id: str = "offline-web-user"
    framework: str = "core"


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    framework: str


def _flush_traces() -> None:
    """요청 직후 trace가 UI에 더 빨리 반영되도록 비동기 로깅 큐를 비운다."""
    flush = getattr(mlflow, "flush_trace_async_logging", None)
    if callable(flush):
        flush(terminate=False)


@mlflow.trace(name="offline_weather_web_chat")
def traced_answer(message: str, user_id: str, session_id: str) -> str:
    return answer_weather(message, user_id=user_id, session_id=session_id)


def _normalize_framework(value: str | None) -> str:
    framework = (value or "core").strip().lower()
    return framework if framework in FRAMEWORK_OPTIONS else "core"


def _answer_with_framework(message: str, framework: str, user_id: str, session_id: str) -> str:
    if framework == "langchain":
        try:
            from offline_weather_agent_core.frameworks.langchain_agent import answer_with_langchain
            return answer_with_langchain(message, user_id=user_id, session_id=session_id)
        except ModuleNotFoundError as exc:
            return f"[langchain unavailable] {exc.name} 패키지가 현재 로컬 환경에 설치되어 있지 않습니다."
    if framework == "langgraph":
        try:
            from offline_weather_agent_core.frameworks.langgraph_agent import answer_with_langgraph
            return answer_with_langgraph(message, user_id=user_id, session_id=session_id)
        except ModuleNotFoundError as exc:
            return f"[langgraph unavailable] {exc.name} 패키지가 현재 로컬 환경에 설치되어 있지 않습니다."
    return traced_answer(message, user_id=user_id, session_id=session_id)


def create_app() -> FastAPI:
    """FastAPI 앱 factory다. uvicorn에서는 이 모듈의 app 객체가 이 함수를 사용한다."""
    app = FastAPI(title="Offline Weather Agent MLflow")

    @app.on_event("startup")
    def startup() -> None:
        configure_tracing_destination()

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return HTML

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "sample": "mlflow"}

    @app.post("/api/chat", response_model=ChatResponse)
    def chat(request: ChatRequest) -> ChatResponse:
        """HTML 화면에서 호출하는 채팅 API다. session_id는 MLflow chat session으로 연결된다."""
        configure_tracing_destination()
        session_id = request.session_id or f"weather-web-{uuid.uuid4().hex[:10]}"
        framework = _normalize_framework(request.framework)
        with mlflow.tracing.context(
            session_id=session_id,
            user=request.user_id,
            tags={
                "app": "offline-weather-agent",
                "surface": "web",
                "framework": framework,
            },
            metadata={
                "channel": "web",
                "city_hint": request.message,
                "framework": framework,
            },
        ):
            answer = _answer_with_framework(
                request.message, framework=framework, user_id=request.user_id, session_id=session_id
            )
        _flush_traces()
        return ChatResponse(answer=answer, session_id=session_id, framework=framework)

    return app


app = create_app()


HTML = """
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Offline Weather Agent</title>
  <style>
    :root {
      --bg: #f5f7f9;
      --panel: #ffffff;
      --line: #d8dee6;
      --text: #18202a;
      --muted: #667282;
      --accent: #0f766e;
      --accent-dark: #115e59;
      --user: #e7f0ff;
      --assistant: #eef8f5;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      display: grid;
      grid-template-rows: 58px 1fr 36px;
    }
    header {
      border-bottom: 1px solid var(--line);
      background: var(--panel);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 clamp(14px, 3vw, 34px);
    }
    .brand { display: flex; align-items: center; gap: 10px; font-weight: 700; }
    .mark {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      background: var(--accent);
      color: white;
      display: grid;
      place-items: center;
      font-size: 14px;
      font-weight: 800;
    }
    .status { color: var(--muted); font-size: 13px; }
    main {
      width: min(900px, 100%);
      min-height: 0;
      margin: 0 auto;
      padding: 14px clamp(10px, 3vw, 24px);
    }
    .chat {
      min-height: calc(100vh - 124px);
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      display: grid;
      grid-template-rows: 1fr auto;
      overflow: hidden;
    }
    .messages {
      padding: 16px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .msg {
      max-width: min(78%, 680px);
      padding: 11px 13px;
      border-radius: 8px;
      line-height: 1.55;
      font-size: 15px;
      white-space: pre-wrap;
      word-break: keep-all;
      overflow-wrap: anywhere;
    }
    .msg.user {
      align-self: flex-end;
      background: var(--user);
      border: 1px solid #cfe0ff;
    }
    .msg.assistant {
      align-self: flex-start;
      background: var(--assistant);
      border: 1px solid #cde9df;
    }
    .composer {
      border-top: 1px solid var(--line);
      background: #fbfcfd;
      padding: 12px;
      display: grid;
      grid-template-columns: 140px 1fr 46px;
      gap: 10px;
    }
    select,
    input {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px 13px;
      font-size: 15px;
      outline: none;
    }
    select {
      background: white;
    }
    select:focus,
    input:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.13);
    }
    button {
      width: 46px;
      height: 46px;
      border: 0;
      border-radius: 8px;
      background: var(--accent);
      color: white;
      cursor: pointer;
      display: grid;
      place-items: center;
    }
    button:hover:not(:disabled) { background: var(--accent-dark); }
    button:disabled { opacity: 0.55; cursor: wait; }
    footer {
      color: var(--muted);
      font-size: 12px;
      display: grid;
      place-items: center;
      padding-bottom: 6px;
    }
    @media (max-width: 640px) {
      .status { display: none; }
      main { padding: 10px; }
      .chat { min-height: calc(100vh - 104px); }
      .messages { padding: 12px; }
      .msg { max-width: 92%; font-size: 14px; }
      .composer { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header>
    <div class="brand"><div class="mark">W</div><div>Offline Weather Agent</div></div>
    <div class="status" id="session">local only</div>
  </header>
  <main>
    <section class="chat">
      <div class="messages" id="messages">
        <div class="msg assistant">MLflow.0용 폐쇄망 샘플입니다. 서울, 부산, 제주, 대구, 인천 날씨를 물어보세요.</div>
      </div>
      <form class="composer" id="form">
        <select id="framework" aria-label="Framework">
          <option value="core">core</option>
          <option value="langchain">langchain</option>
          <option value="langgraph">langgraph</option>
        </select>
        <input id="input" autocomplete="off" placeholder="서울 날씨 알려줘">
        <button id="send" type="submit" aria-label="Send">
          <svg width="21" height="21" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M5 12h13M13 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </form>
    </section>
  </main>
  <footer>MLflow.0 + Ollama/Qwen on localhost</footer>
  <script>
    const messages = document.getElementById("messages");
    const form = document.getElementById("form");
    const input = document.getElementById("input");
    const send = document.getElementById("send");
    const session = document.getElementById("session");
    const framework = document.getElementById("framework");
    let sessionId = localStorage.getItem("weather-web-session-id") || "";
    let selectedFramework = localStorage.getItem("weather-web-framework") || "core";
    if (sessionId) session.textContent = sessionId;
    framework.value = selectedFramework;

    framework.addEventListener("change", () => {
      selectedFramework = framework.value;
      localStorage.setItem("weather-web-framework", selectedFramework);
    });

    function addMessage(role, text) {
      const node = document.createElement("div");
      node.className = `msg ${role}`;
      node.textContent = text;
      messages.appendChild(node);
      messages.scrollTop = messages.scrollHeight;
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const message = input.value.trim();
      if (!message) return;
      addMessage("user", message);
      input.value = "";
      send.disabled = true;
      try {
        const res = await fetch("/api/chat", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({
            message,
            session_id: sessionId,
            user_id: "offline-web-user",
            framework: framework.value
          })
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        sessionId = data.session_id;
        localStorage.setItem("weather-web-session-id", sessionId);
        session.textContent = sessionId;
        addMessage("assistant", `[${data.framework}] ${data.answer}`);
      } catch (error) {
        addMessage("assistant", `오류가 발생했습니다. ${error.message}`);
      } finally {
        send.disabled = false;
        input.focus();
      }
    });
  </script>
</body>
</html>
"""
