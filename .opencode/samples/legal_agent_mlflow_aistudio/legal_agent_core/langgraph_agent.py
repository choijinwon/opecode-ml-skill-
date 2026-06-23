from __future__ import annotations

from typing import TypedDict

import mlflow
from mlflow.entities import SpanType

from legal_agent_core.core import classify_legal_topic
from legal_agent_core.llm import call_ai_studio_llm
from legal_agent_core.prompts import render_prompt
from legal_agent_core.retrieval import retrieve_legal_context


class LegalAgentState(TypedDict, total=False):
    question: str
    user_id: str
    session_id: str
    topic: str
    contexts: list[dict[str, str]]
    messages: list[dict[str, str]]
    answer: str


@mlflow.trace(name="langgraph_legal_agent", span_type=SpanType.AGENT)
def answer_with_langgraph(
    question: str,
    user_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, object]:
    """LangGraph StateGraph 기반 실행 예시다.

    LangGraph가 설치되어 있으면 StateGraph로 실행하고, 없으면 같은 노드 함수를
    순서대로 호출한다. AI Studio Viewer에서는 이 노드 구조가 화면 설계 기준이 된다.
    """
    trace_user = user_id or "legal-langgraph-user"
    trace_session = session_id or "legal-langgraph-session"
    mlflow.update_current_trace(
        user=trace_user,
        session_id=trace_session,
        tags={
            "framework": "langgraph",
            "app": "legal-agent-ai-studio",
            "domain": "legal",
        },
        metadata={
            "mlflow.trace.user": trace_user,
            "mlflow.trace.session": trace_session,
            "framework": "langgraph",
        },
    )

    state: LegalAgentState = {
        "question": question,
        "user_id": trace_user,
        "session_id": trace_session,
    }
    graph_available = _langgraph_available()
    if graph_available:
        state = _run_state_graph(state)
    else:
        state = _run_linear_graph(state)

    return {
        "framework": "langgraph",
        "langgraph_available": graph_available,
        "answer": state["answer"],
        "topic": state["topic"],
        "contexts": state["contexts"],
        "user_id": trace_user,
        "session_id": trace_session,
    }


@mlflow.trace(name="langgraph_node_classify", span_type=SpanType.TOOL)
def _classify_node(state: LegalAgentState) -> LegalAgentState:
    state["topic"] = classify_legal_topic(state["question"])
    return state


@mlflow.trace(name="langgraph_node_retrieve", span_type=SpanType.RETRIEVER)
def _retrieve_node(state: LegalAgentState) -> LegalAgentState:
    state["contexts"] = retrieve_legal_context(state["question"])
    return state


@mlflow.trace(name="langgraph_node_prompt", span_type=SpanType.TOOL)
def _prompt_node(state: LegalAgentState) -> LegalAgentState:
    state["messages"] = render_prompt(
        state["question"],
        state["topic"],
        state.get("contexts", []),
    )
    return state


@mlflow.trace(name="langgraph_node_llm", span_type=SpanType.LLM)
def _llm_node(state: LegalAgentState) -> LegalAgentState:
    state["answer"] = call_ai_studio_llm(
        state["question"],
        state["topic"],
        state.get("messages", []),
        state.get("contexts", []),
    )
    return state


def _run_linear_graph(state: LegalAgentState) -> LegalAgentState:
    for node in (_classify_node, _retrieve_node, _prompt_node, _llm_node):
        state = node(state)
    return state


def _run_state_graph(state: LegalAgentState) -> LegalAgentState:
    from langgraph.graph import END, StateGraph

    graph = StateGraph(LegalAgentState)
    graph.add_node("classify", _classify_node)
    graph.add_node("retrieve", _retrieve_node)
    graph.add_node("prompt", _prompt_node)
    graph.add_node("llm", _llm_node)
    graph.set_entry_point("classify")
    graph.add_edge("classify", "retrieve")
    graph.add_edge("retrieve", "prompt")
    graph.add_edge("prompt", "llm")
    graph.add_edge("llm", END)
    app = graph.compile()
    return app.invoke(state)


def _langgraph_available() -> bool:
    try:
        from langgraph.graph import StateGraph  # noqa: F401
    except Exception:
        return False
    return True
