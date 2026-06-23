from __future__ import annotations

from typing import TypedDict

import mlflow
from mlflow.entities import SpanType

from design_agent_core.core import classify_design_task
from design_agent_core.llm import call_ai_studio_llm
from design_agent_core.prompts import render_prompt
from design_agent_core.retrieval import retrieve_design_guidelines


class DesignAgentState(TypedDict, total=False):
    request: str
    user_id: str
    session_id: str
    task_type: str
    guidelines: list[dict[str, str]]
    messages: list[dict[str, str]]
    answer: str


@mlflow.trace(name="langgraph_design_agent", span_type=SpanType.AGENT)
def answer_with_langgraph(
    request: str,
    user_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, object]:
    trace_user = user_id or "design-langgraph-user"
    trace_session = session_id or "design-langgraph-session"
    mlflow.update_current_trace(
        user=trace_user,
        session_id=trace_session,
        tags={"framework": "langgraph", "app": "design-agent-ai-studio", "domain": "design"},
        metadata={
            "mlflow.trace.user": trace_user,
            "mlflow.trace.session": trace_session,
            "framework": "langgraph",
        },
    )
    state: DesignAgentState = {
        "request": request,
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
        "task_type": state["task_type"],
        "guidelines": state["guidelines"],
        "user_id": trace_user,
        "session_id": trace_session,
    }


@mlflow.trace(name="langgraph_node_classify", span_type=SpanType.TOOL)
def _classify_node(state: DesignAgentState) -> DesignAgentState:
    state["task_type"] = classify_design_task(state["request"])
    return state


@mlflow.trace(name="langgraph_node_retrieve", span_type=SpanType.RETRIEVER)
def _retrieve_node(state: DesignAgentState) -> DesignAgentState:
    state["guidelines"] = retrieve_design_guidelines(state["request"])
    return state


@mlflow.trace(name="langgraph_node_prompt", span_type=SpanType.TOOL)
def _prompt_node(state: DesignAgentState) -> DesignAgentState:
    state["messages"] = render_prompt(
        state["request"],
        state["task_type"],
        state.get("guidelines", []),
    )
    return state


@mlflow.trace(name="langgraph_node_llm", span_type=SpanType.LLM)
def _llm_node(state: DesignAgentState) -> DesignAgentState:
    state["answer"] = call_ai_studio_llm(
        state["request"],
        state["task_type"],
        state.get("messages", []),
        state.get("guidelines", []),
    )
    return state


def _run_linear_graph(state: DesignAgentState) -> DesignAgentState:
    for node in (_classify_node, _retrieve_node, _prompt_node, _llm_node):
        state = node(state)
    return state


def _run_state_graph(state: DesignAgentState) -> DesignAgentState:
    from langgraph.graph import END, StateGraph

    graph = StateGraph(DesignAgentState)
    graph.add_node("classify", _classify_node)
    graph.add_node("retrieve", _retrieve_node)
    graph.add_node("prompt", _prompt_node)
    graph.add_node("llm", _llm_node)
    graph.set_entry_point("classify")
    graph.add_edge("classify", "retrieve")
    graph.add_edge("retrieve", "prompt")
    graph.add_edge("prompt", "llm")
    graph.add_edge("llm", END)
    return graph.compile().invoke(state)


def _langgraph_available() -> bool:
    try:
        from langgraph.graph import StateGraph  # noqa: F401
    except Exception:
        return False
    return True
