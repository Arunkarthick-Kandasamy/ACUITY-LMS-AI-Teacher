from __future__ import annotations

from app.ai.prompts import PROMPT_TEACH, SYSTEM_TEACH
from app.ai.services.gemini import GeminiService
from app.ai.state import TeacherAction, TeacherState


async def teach_node(state: TeacherState) -> dict:
    gemini = GeminiService()

    content_parts = []
    concept_content_list = state.get("concept_content", [])
    for cc in concept_content_list:
        content_parts.append(f"[{cc.get('content_type', 'content')}]\n{cc.get('content', '')}")

    memory_context = state.get("memory_context")
    if memory_context is None:
        memory_context = "No prior observations for this student."

    prompt = PROMPT_TEACH.format(
        concept_title=state.get("concept_title", "Unknown Concept"),
        concept_description=state.get("concept_description", ""),
        concept_content="\n\n".join(content_parts) if content_parts else "No additional content available.",
        conversation_history=_format_history(state.get("conversation_history", [])),
        memory_context=memory_context,
    )

    teaching_content = await gemini.generate(prompt, SYSTEM_TEACH)

    history = list(state.get("conversation_history", []))
    history.append({"role": "teacher", "content": teaching_content})

    return {
        "teaching_content": teaching_content,
        "current_action": TeacherAction.ASK_QUESTION,
        "conversation_history": history,
    }


def _format_history(history: list[dict]) -> str:
    if not history:
        return "No previous conversation."
    lines = []
    for entry in history[-4:]:
        role = entry.get("role", "unknown")
        content = entry.get("content", "")
        lines.append(f"{role.capitalize()}: {content}")
    return "\n".join(lines)
