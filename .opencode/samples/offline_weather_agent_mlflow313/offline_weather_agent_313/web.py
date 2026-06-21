import uuid

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from offline_weather_agent_313.config import configure_mlflow
from offline_weather_agent_313.core import answer_weather


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    user_id: str = "offline-web-user"


class ChatResponse(BaseModel):
    answer: str
    session_id: str


def create_app() -> FastAPI:
    """FastAPI 앱 factory다. uvicorn에서는 이 모듈의 app 객체를 사용한다."""
    app = FastAPI(title="Offline Weather Agent MLflow 3.13")

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return HTML

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "sample": "mlflow-3.13.0"}

    @app.post("/api/chat", response_model=ChatResponse)
    def chat(request: ChatRequest) -> ChatResponse:
        """HTML 화면에서 호출하는 채팅 API다. session_id는 MLflow chat session으로 연결된다."""
        configure_mlflow()
        session_id = request.session_id or f"weather-313-{uuid.uuid4().hex[:10]}"
        answer = answer_weather(request.message, user_id=request.user_id, session_id=session_id)
        return ChatResponse(answer=answer, session_id=session_id)

    return app


app = create_app()


HTML = """
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Offline Weather Agent 3.13</title>
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
      grid-template-columns: 1fr 46px;
      gap: 10px;
    }
    input {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px 13px;
      font-size: 15px;
      outline: none;
    }
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
    }
  </style>
</head>
<body>
  <header>
    <div class="brand"><div class="mark">3.13</div><div>Offline Weather Agent</div></div>
    <div class="status" id="session">local only</div>
  </header>
  <main>
    <section class="chat">
      <div class="messages" id="messages">
        <div class="msg assistant">MLflow 3.13.0용 폐쇄망 샘플입니다. 서울, 부산, 제주, 대구, 인천 날씨를 물어보세요.</div>
      </div>
      <form class="composer" id="form">
        <input id="input" autocomplete="off" placeholder="서울 날씨 알려줘">
        <button id="send" type="submit" aria-label="Send">
          <svg width="21" height="21" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M5 12h13M13 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </form>
    </section>
  </main>
  <footer>MLflow 3.13.0 + Ollama/Qwen on localhost</footer>
  <script>
    const messages = document.getElementById("messages");
    const form = document.getElementById("form");
    const input = document.getElementById("input");
    const send = document.getElementById("send");
    const session = document.getElementById("session");
    let sessionId = localStorage.getItem("offline-weather-313-session-id") || "";

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
          body: JSON.stringify({message, session_id: sessionId, user_id: "offline-web-user"})
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        sessionId = data.session_id;
        localStorage.setItem("offline-weather-313-session-id", sessionId);
        session.textContent = sessionId;
        addMessage("assistant", data.answer);
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
