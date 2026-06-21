import importlib.util

import mlflow
from mlflow.entities import SpanType

from offline_weather_agent_core.config import configure_mlflow
from offline_weather_agent_core.config import llm_api_key, llm_base_url, qwen_model_name
from offline_weather_agent_core.retrieval import context_text, retrieve_context
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
                "질문: {question}\n날씨 데이터: {weather_data}\n로컬 검색 문서:\n{rag_context}\n한국어로 자연스럽게 답해줘.",
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


def _missing_dependency_message() -> str | None:
    if importlib.util.find_spec("langchain_core") is None:
        return "[langchain unavailable] langchain_core 패키지가 현재 로컬 환경에 설치되어 있지 않습니다."
    if importlib.util.find_spec("langchain_openai") is None:
        return "[langchain unavailable] langchain_openai 패키지가 현재 로컬 환경에 설치되어 있지 않습니다."
    return None


@mlflow.trace(name="langchain_weather_agent", span_type=SpanType.AGENT)
def answer_with_langchain(question: str, user_id: str = "langchain-user", session_id: str = "langchain-session") -> str:
    """LangChain 실행 전체를 MLflow agent span으로 묶는다."""
    mlflow.update_current_trace(
        user=user_id,
        session_id=session_id,
        tags={
            "user_id": user_id,
            "session_id": session_id,
        },
        metadata={
            "framework": "langchain",
        }
    )
    missing = _missing_dependency_message()
    if missing is not None:
        return missing
    weather = get_weather(extract_city(question))
    contexts = retrieve_context(question)
    chain = build_chain()
    response = chain.invoke(
        {
            "question": question,
            "weather_data": weather_data_text(weather),
            "rag_context": context_text(contexts),
        }
    )
    return response.content


def main() -> None:
    """CLI에서 LangChain 샘플을 실행한다."""
    import sys

    configure_mlflow()
    mlflow.langchain.autolog()
    question = " ".join(sys.argv[1:]).strip() or "서울 날씨 알려줘"
    print(answer_with_langchain(question))


if __name__ == "__main__":
    main()
