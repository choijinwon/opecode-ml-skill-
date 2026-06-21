import sys

import mlflow

from offline_weather_agent_313.config import configure_mlflow
from offline_weather_agent_313.frameworks.langgraph_agent import answer_with_langgraph


def main() -> None:
    configure_mlflow()
    mlflow.langchain.autolog()
    question = " ".join(sys.argv[1:]).strip() or "서울 날씨 알려줘"
    print(answer_with_langgraph(question))


if __name__ == "__main__":
    main()
