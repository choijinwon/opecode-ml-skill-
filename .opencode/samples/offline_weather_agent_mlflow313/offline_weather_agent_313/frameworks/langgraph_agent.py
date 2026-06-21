from typing import TypedDict

import mlflow
from mlflow.entities import SpanType

from offline_weather_agent_313.config import configure_mlflow
from offline_weather_agent_313.config import llm_api_key, llm_base_url, qwen_model_name
from offline_weather_agent_313.weather import extract_city, get_weather, weather_data_text


class WeatherState(TypedDict):
    question: str
    city: str
    weather_data: str
    answer: str


def build_llm():
    """LangGraph node에서 사용할 OpenAI-compatible Qwen client를 만든다."""
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=qwen_model_name(),
        base_url=llm_base_url(),
        api_key=llm_api_key(),
        temperature=0.2,
    )


def select_city_node(state: WeatherState) -> WeatherState:
    """질문에서 도시를 고르는 LangGraph node다."""
    return {**state, "city": extract_city(state["question"])}


def weather_tool_node(state: WeatherState) -> WeatherState:
    """로컬 날씨 도구를 호출하는 LangGraph node다."""
    weather = get_weather(state["city"])
    return {**state, "weather_data": weather_data_text(weather)}


def llm_node(state: WeatherState) -> WeatherState:
    """Qwen 모델로 최종 답변을 생성하는 LangGraph node다."""
    from langchain_core.messages import HumanMessage, SystemMessage

    llm = build_llm()
    response = llm.invoke(
        [
            SystemMessage(content="너는 폐쇄망에서 동작하는 한국어 날씨 비서다. 제공된 날씨 데이터만 사용한다."),
            HumanMessage(
                content=(
                    f"질문: {state['question']}\n"
                    f"날씨 데이터: {state['weather_data']}\n"
                    "한국어로 짧고 자연스럽게 답해줘."
                )
            ),
        ]
    )
    return {**state, "answer": response.content}


def build_graph():
    """LangGraph workflow를 만든다: 도시 선택 -> 날씨 도구 -> LLM 답변."""
    from langgraph.graph import END, START, StateGraph

    graph = StateGraph(WeatherState)
    graph.add_node("select_city", select_city_node)
    graph.add_node("get_weather", weather_tool_node)
    graph.add_node("call_qwen", llm_node)
    graph.add_edge(START, "select_city")
    graph.add_edge("select_city", "get_weather")
    graph.add_edge("get_weather", "call_qwen")
    graph.add_edge("call_qwen", END)
    return graph.compile()


@mlflow.trace(name="langgraph_weather_agent_313", span_type=SpanType.AGENT)
def answer_with_langgraph(question: str, user_id: str = "langgraph-user", session_id: str = "langgraph-session") -> str:
    """LangGraph workflow 전체를 MLflow agent span으로 묶는다."""
    mlflow.update_current_trace(
        metadata={
            "mlflow.trace.user": user_id,
            "mlflow.trace.session": session_id,
            "framework": "langgraph",
        }
    )
    graph = build_graph()
    result = graph.invoke({"question": question, "city": "", "weather_data": "", "answer": ""})
    return result["answer"]


def main() -> None:
    """CLI에서 LangGraph 샘플을 실행한다."""
    import sys

    configure_mlflow()
    mlflow.langchain.autolog()
    question = " ".join(sys.argv[1:]).strip() or "부산 날씨 알려줘"
    print(answer_with_langgraph(question))


if __name__ == "__main__":
    main()
