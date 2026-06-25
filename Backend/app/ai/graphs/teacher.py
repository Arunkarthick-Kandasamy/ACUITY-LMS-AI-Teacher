from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.ai.nodes.ask_question import ask_question_node
from app.ai.nodes.complete_concept import complete_concept_node
from app.ai.nodes.diagnose import diagnose_node
from app.ai.nodes.evaluate_response import evaluate_response_node
from app.ai.nodes.provide_example import provide_example_node
from app.ai.nodes.retrieve_memories import retrieve_memories_node
from app.ai.nodes.teach import teach_node
from app.ai.state import TeacherState


def decide_entry(state: TeacherState) -> str:
    student_response = state.get("student_response")
    current_action = state.get("current_action")

    if student_response and current_action in ("ask_question", "evaluate_response"):
        return "evaluate_response"

    return "retrieve_memories"


def decide_after_evaluation(state: TeacherState) -> str:
    return "diagnose"


RETURN_ACTION_MAP: dict[str, str] = {
    "reteach": "retrieve_memories",
    "prerequisite": "retrieve_memories",
    "example": "provide_example",
    "continue": "complete_concept",
}


def decide_after_diagnosis(state: TeacherState) -> str:
    recommended = state.get("recommended_action")
    if recommended is None:
        return "example"
    return recommended if recommended in RETURN_ACTION_MAP else "example"


def build_teacher_graph() -> StateGraph:
    builder = StateGraph(TeacherState)

    builder.add_node("retrieve_memories", retrieve_memories_node)
    builder.add_node("teach", teach_node)
    builder.add_node("ask_question", ask_question_node)
    builder.add_node("evaluate_response", evaluate_response_node)
    builder.add_node("diagnose", diagnose_node)
    builder.add_node("provide_example", provide_example_node)
    builder.add_node("complete_concept", complete_concept_node)

    builder.set_conditional_entry_point(
        decide_entry,
        {
            "retrieve_memories": "retrieve_memories",
            "evaluate_response": "evaluate_response",
        },
    )

    builder.add_edge("retrieve_memories", "teach")
    builder.add_edge("teach", "ask_question")
    builder.add_edge("ask_question", END)
    builder.add_edge("complete_concept", END)

    builder.add_edge("evaluate_response", "diagnose")

    builder.add_conditional_edges(
        "diagnose",
        decide_after_diagnosis,
        RETURN_ACTION_MAP,
    )

    builder.add_edge("provide_example", "ask_question")

    return builder


teacher_graph = build_teacher_graph().compile()
