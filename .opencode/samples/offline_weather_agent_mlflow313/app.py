"""uvicorn app:app 실행을 유지하기 위한 얇은 entrypoint."""

from offline_weather_agent_313.web import create_app

app = create_app()
