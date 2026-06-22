import importlib.util
from typing import TypedDict

import mlflow
from mlflow.entities import SpanType

from offline_weather_agent_core.config import configure_mlflow
from offline_weather_agent_core.config import llm_api_key, llm_base_url, qwen_model_name
from offline_weather_agent_core.prompting import render_prompt_messages, to_langchain_messages
from offline_weather_agent_core.retrieval import context_text, retrieve_context
from offline_weather_agent_core.weather import extract_city, get_weather, weather_data_text


class WeatherState(TypedDict):
    question: str
    city: str
    weather_data: str
    rag_context: str
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


def retrieve_context_node(state: WeatherState) -> WeatherState:
    """질문과 관련된 로컬 RAG 문서를 검색하는 LangGraph node다."""
    contexts = retrieve_context(state["question"])
    return {**state, "rag_context": context_text(contexts)}


def llm_node(state: WeatherState) -> WeatherState:
    """Qwen 모델로 최종 답변을 생성하는 LangGraph node다."""
    llm = build_llm()
    weather = get_weather(state["city"])
    contexts = retrieve_context(state["question"])
    prompt_messages = render_prompt_messages(state["question"], weather, contexts)
    response = llm.invoke(to_langchain_messages(prompt_messages))
    return {**state, "answer": response.content}


def build_graph():
    """LangGraph workflow를 만든다: 도시 선택 -> 날씨 도구 -> LLM 답변."""
    from langgraph.graph import END, START, StateGraph

    graph = StateGraph(WeatherState)
    graph.add_node("select_city", select_city_node)
    graph.add_node("get_weather", weather_tool_node)
    graph.add_node("retrieve_context", retrieve_context_node)
    graph.add_node("call_qwen", llm_node)
    graph.add_edge(START, "select_city")
    graph.add_edge("select_city", "get_weather")
    graph.add_edge("get_weather", "retrieve_context")
    graph.add_edge("retrieve_context", "call_qwen")
    graph.add_edge("call_qwen", END)
    return graph.compile()


def _missing_dependency_message() -> str | None:
    if importlib.util.find_spec("langgraph") is None:
        return "[langgraph unavailable] langgraph 패키지가 현재 로컬 환경에 설치되어 있지 않습니다."
    if importlib.util.find_spec("langchain_core") is None:
        return "[langgraph unavailable] langchain_core 패키지가 현재 로컬 환경에 설치되어 있지 않습니다."
    if importlib.util.find_spec("langchain_openai") is None:
        return "[langgraph unavailable] langchain_openai 패키지가 현재 로컬 환경에 설치되어 있지 않습니다."
    return None


@mlflow.trace(name="langgraph_weather_agent", span_type=SpanType.AGENT)
def answer_with_langgraph(question: str, user_id: str = "langgraph-user", session_id: str = "langgraph-session") -> str:
    """LangGraph workflow 전체를 MLflow agent span으로 묶는다."""
    mlflow.update_current_trace(
        user=user_id,
        session_id=session_id,
        tags={
            "user_id": user_id,
            "session_id": session_id,
        },
        metadata={
            "framework": "langgraph",
        }
    )
    missing = _missing_dependency_message()
    if missing is not None:
        return missing
    graph = build_graph()
    result = graph.invoke({"question": question, "city": "", "weather_data": "", "rag_context": "", "answer": ""})
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
