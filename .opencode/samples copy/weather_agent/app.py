import os
import uuid

import mlflow
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from weather_agent import load_dotenv, weather_agent


load_dotenv()
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5001"))
mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT_NAME", "weather-agent"))

app = FastAPI(title="Weather Agent")


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    user_id: str = "web-user"


class ChatResponse(BaseModel):
    answer: str
    session_id: str


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return HTML


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    session_id = request.session_id or f"weather-web-{uuid.uuid4().hex[:10]}"
    answer = weather_agent(request.message, user_id=request.user_id, session_id=session_id)
    return ChatResponse(answer=answer, session_id=session_id)


HTML = """
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Weather Agent</title>
  <style>
    :root {
      color-scheme: light;
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
      grid-template-rows: auto 1fr auto;
    }

    header {
      height: 64px;
      border-bottom: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.92);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 clamp(16px, 4vw, 40px);
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 10px;
      font-weight: 700;
    }

    .mark {
      width: 34px;
      height: 34px;
      border-radius: 8px;
      background: var(--accent);
      color: white;
      display: grid;
      place-items: center;
      font-size: 18px;
      line-height: 1;
    }

    .status {
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }

    main {
      width: min(920px, 100%);
      margin: 0 auto;
      padding: 18px clamp(12px, 3vw, 24px);
      display: grid;
      grid-template-rows: 1fr;
      min-height: 0;
    }

    .chat {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      min-height: calc(100vh - 168px);
      display: grid;
      grid-template-rows: 1fr auto;
      overflow: hidden;
    }

    .messages {
      padding: 18px;
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
      padding: 12px;
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      background: #fbfcfd;
    }

    input {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px 13px;
      font-size: 15px;
      color: var(--text);
      background: white;
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

    button:disabled {
      opacity: 0.55;
      cursor: wait;
    }

    button:hover:not(:disabled) { background: var(--accent-dark); }

    footer {
      min-height: 44px;
      color: var(--muted);
      font-size: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0 16px 10px;
    }

    @media (max-width: 640px) {
      header { height: 58px; }
      .status { display: none; }
      main { padding: 10px; }
      .chat { min-height: calc(100vh - 122px); }
      .messages { padding: 12px; }
      .msg { max-width: 92%; font-size: 14px; }
      .composer { grid-template-columns: 1fr auto; padding: 10px; }
    }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <div class="mark" aria-hidden="true">☀</div>
      <div>Weather Agent</div>
    </div>
    <div class="status" id="session">MLflow tracing enabled</div>
  </header>

  <main>
    <section class="chat" aria-label="Weather chat">
      <div class="messages" id="messages">
        <div class="msg assistant">안녕하세요. 서울, 부산, 제주 날씨를 물어보세요.</div>
      </div>
      <form class="composer" id="form">
        <input id="input" autocomplete="off" placeholder="서울 날씨 알려줘" />
        <button id="send" type="submit" aria-label="Send">
          <svg width="21" height="21" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M5 12h13M13 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </form>
    </section>
  </main>

  <footer>Experiment: weather-agent · Model: qwen2.5-coder:14b</footer>

  <script>
    const messages = document.getElementById("messages");
    const form = document.getElementById("form");
    const input = document.getElementById("input");
    const send = document.getElementById("send");
    const sessionLabel = document.getElementById("session");
    let sessionId = localStorage.getItem("weather-agent-session-id") || "";

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
      input.focus();
      send.disabled = true;

      try {
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message, session_id: sessionId, user_id: "web-user" }),
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        sessionId = data.session_id;
        localStorage.setItem("weather-agent-session-id", sessionId);
        sessionLabel.textContent = `Session ${sessionId}`;
        addMessage("assistant", data.answer);
      } catch (error) {
        addMessage("assistant", `요청 처리 중 오류가 났습니다. ${error.message}`);
      } finally {
        send.disabled = false;
      }
    });
  </script>
</body>
</html>
"""
