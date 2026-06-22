from __future__ import annotations

from app.ai.state import TeacherAction, TeacherState


async def complete_concept_node(state: TeacherState) -> dict:
    history = list(state.get("conversation_history", []))
    history.append({
        "role": "teacher",
        "content": (
            "Great job! You have demonstrated a good understanding of this concept. "
            "Let's move on to the next topic."
        ),
    })

    return {
        "current_action": TeacherAction.COMPLETE_CONCEPT,
        "conversation_history": history,
    }
