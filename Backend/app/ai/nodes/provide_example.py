from __future__ import annotations

from app.ai.prompts import PROMPT_EXAMPLE, SYSTEM_EXAMPLE
from app.ai.services.gemini import GeminiService
from app.ai.state import TeacherAction, TeacherState


async def provide_example_node(state: TeacherState) -> dict:
    gemini = GeminiService()

    example_parts = []
    example_list = state.get("examples", [])
    for ex in example_list:
        parts = []
        if isinstance(ex, dict):
            if ex.get("content"):
                parts.append(ex["content"])
            if ex.get("explanation"):
                parts.append(f"Explanation: {ex['explanation']}")
        example_parts.append("\n".join(parts))

    prompt = PROMPT_EXAMPLE.format(
        concept_title=state.get("concept_title", "Unknown Concept"),
        concept_description=state.get("concept_description", ""),
        example_content="\n\n".join(example_parts) if example_parts else "No examples available.",
    )

    example_content = await gemini.generate(prompt, SYSTEM_EXAMPLE)

    history = list(state.get("conversation_history", []))
    history.append({"role": "teacher", "content": f"Example: {example_content}"})

    return {
        "example_content": example_content,
        "current_action": TeacherAction.ASK_QUESTION,
        "conversation_history": history,
    }
