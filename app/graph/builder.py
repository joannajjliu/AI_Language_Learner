"""LangGraph builder for the learning loop."""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.graph.agents.evaluator import evaluator_agent
from app.graph.agents.lesson import lesson_agent
from app.graph.agents.memory import memory_agent
from app.graph.agents.planner import planner_agent
from app.graph.agents.practice import practice_agent
from app.graph.state import LearningState


def _route_from_start(state: LearningState) -> str:
    """Enter full generation, submit-only evaluation, or practice-only refresh."""
    action = state.get("request_action") or "full"
    if action == "submit_answers":
        return "evaluator"
    if action == "new_exercises":
        return "practice"
    return "planner"


def _route_after_practice(state: LearningState) -> str:
    """After generating exercises: evaluate, or exit when refreshing questions only."""
    action = state.get("request_action") or "full"
    if action == "new_exercises":
        return "end"
    return "evaluator"


def _route_after_memory(state: LearningState) -> str:
    """Decide whether to loop the graph or terminate."""
    action = state.get("request_action") or "full"
    if action == "submit_answers":
        return "end"
    should_loop = state.get("evaluation", {}).get("needs_review", False)
    loop_count = state.get("loop_count", 0)
    return "planner" if should_loop and loop_count < 2 else "end"


def build_learning_graph():
    """Create and compile the learning workflow graph."""
    graph = StateGraph(LearningState)

    graph.add_node("planner", planner_agent)
    graph.add_node("lesson", lesson_agent)
    graph.add_node("practice", practice_agent)
    graph.add_node("evaluator", evaluator_agent)
    graph.add_node("memory", memory_agent)

    graph.add_conditional_edges(
        START,
        _route_from_start,
        {
            "planner": "planner",
            "practice": "practice",
            "evaluator": "evaluator",
        },
    )
    graph.add_edge("planner", "lesson")
    graph.add_edge("lesson", "practice")
    graph.add_conditional_edges(
        "practice",
        _route_after_practice,
        {"evaluator": "evaluator", "end": END},
    )
    graph.add_edge("evaluator", "memory")
    graph.add_conditional_edges(
        "memory",
        _route_after_memory,
        {"planner": "planner", "end": END},
    )

    return graph.compile()


learning_graph = build_learning_graph()
