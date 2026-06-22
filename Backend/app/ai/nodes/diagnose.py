from __future__ import annotations

from app.ai.diagnosis.service import DiagnosisService
from app.ai.state import TeacherState


async def diagnose_node(state: TeacherState) -> dict:
    service = DiagnosisService()

    conversation_history = _format_history(state.get("conversation_history", []))

    result = await service.diagnose(
        concept_title=state.get("concept_title", "Unknown Concept"),
        concept_description=state.get("concept_description", ""),
        teaching_content=state.get("teaching_content", ""),
        question=state.get("question", ""),
        student_response=state.get("student_response", ""),
        mastery_estimate=state.get("mastery_estimate", 0.0),
        prerequisite_concepts=state.get("prerequisite_concepts", []),
        conversation_history=conversation_history,
    )

    history = list(state.get("conversation_history", []))
    diagnosis_text = _format_diagnosis_message(result)
    history.append({"role": "teacher", "content": diagnosis_text})

    return {
        "diagnosis_result": result.model_dump(mode="json"),
        "recommended_action": result.recommended_action,
        "conversation_history": history,
    }


def _format_history(history: list[dict]) -> str:
    if not history:
        return "No previous conversation."
    lines = []
    for entry in history[-4:]:
        role = entry.get("role", "unknown")
        content = entry.get("content", "")
        if len(content) > 500:
            content = content[:500] + "..."
        lines.append(f"{role.capitalize()}: {content}")
    return "\n".join(lines)


def _format_diagnosis_message(result) -> str:
    parts = []
    if result.misconception:
        parts.append(f"Diagnosis: {result.misconception}")
    if result.knowledge_gap:
        parts.append(f"Knowledge gap: {result.knowledge_gap}")
    if result.remediation:
        parts.append(f"Let's work on: {result.remediation}")
    return " | ".join(parts) if parts else "Let me help you with that."
