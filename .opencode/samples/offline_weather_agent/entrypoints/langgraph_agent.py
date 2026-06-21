import sys

import mlflow

from offline_weather_agent_core.config import configure_mlflow
from offline_weather_agent_core.frameworks.langgraph_agent import answer_with_langgraph


def main() -> None:
    """LangGraph 기반 날씨 에이전트를 한 번 실행한다."""
    configure_mlflow()
    mlflow.langchain.autolog()
    question = " ".join(sys.argv[1:]).strip() or "부산 날씨 알려줘"
    print(answer_with_langgraph(question))
