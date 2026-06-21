"""FastAPI 앱 entrypoint."""

from offline_weather_agent_core.web import create_app

app = create_app()
