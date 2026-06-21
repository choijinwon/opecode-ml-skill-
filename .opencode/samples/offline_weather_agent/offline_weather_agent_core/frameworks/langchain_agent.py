import mlflow
from mlflow.entities import SpanType

from offline_weather_agent_core.config import llm_api_key, llm_base_url, qwen_model_name
from offline_weather_agent_core.weather import extract_city, get_weather, weather_data_text


def build_chain():
    """LangChain 체인을 만든다. import는 autolog 설정 이후에 수행한다."""
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_openai import ChatOpenAI

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "너는 폐쇄망에서 동작하는 한국어 날씨 비서다. 제공된 날씨 데이터만 사용해서 짧게 답한다.",
            ),
            (
                "user",
                "질문: {question}\n날씨 데이터: {weather_data}\n한국어로 자연스럽게 답해줘.",
            ),
        ]
    )
    llm = ChatOpenAI(
        model=qwen_model_name(),
        base_url=llm_base_url(),
        api_key=llm_api_key(),
        temperature=0.2,
    )
    return prompt | llm


@mlflow.trace(name="langchain_weather_agent", span_type=SpanType.AGENT)
def answer_with_langchain(question: str, user_id: str = "langchain-user", session_id: str = "langchain-session") -> str:
    """LangChain 실행 전체를 MLflow agent span으로 묶는다."""
    mlflow.update_current_trace(
        metadata={
            "mlflow.trace.user": user_id,
            "mlflow.trace.session": session_id,
            "framework": "langchain",
        }
    )
    weather = get_weather(extract_city(question))
    chain = build_chain()
    response = chain.invoke({"question": question, "weather_data": weather_data_text(weather)})
    return response.content
