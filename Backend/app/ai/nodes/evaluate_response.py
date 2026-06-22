from __future__ import annotations

from app.ai.evaluators.mastery import estimate_mastery_from_score
from app.ai.prompts import PROMPT_EVALUATE, SYSTEM_EVALUATE
from app.ai.services.gemini import GeminiService
from app.ai.state import TeacherState


async def evaluate_response_node(state: TeacherState) -> dict:
    gemini = GeminiService()

    prompt = PROMPT_EVALUATE.format(
        concept_title=state.get("concept_title", "Unknown Concept"),
        teaching_content=state.get("teaching_content", ""),
        question=state.get("question", ""),
        student_response=state.get("student_response", ""),
        conversation_history=_format_history(state.get("conversation_history", [])),
    )

    result = await gemini.generate_json(prompt, SYSTEM_EVALUATE)

    score = result.get("score", 0.5)
    feedback = result.get("feedback", "")

    mastery = estimate_mastery_from_score(score)

    history = list(state.get("conversation_history", []))
    history.append({"role": "student", "content": state.get("student_response", "")})
    history.append({"role": "teacher", "content": f"Feedback: {feedback}"})

    return {
        "evaluation": feedback,
        "mastery_estimate": mastery,
        "conversation_history": history,
        "student_response": None,
    }


def _format_history(history: list[dict]) -> str:
    if not history:
        return "No previous conversation."
    lines = []
    for entry in history[-4:]:
        role = entry.get("role", "unknown")
        content = entry.get("content", "")
        # Truncate long content for prompt size
        if len(content) > 500:
            content = content[:500] + "..."
        lines.append(f"{role.capitalize()}: {content}")
    return "\n".join(lines)
