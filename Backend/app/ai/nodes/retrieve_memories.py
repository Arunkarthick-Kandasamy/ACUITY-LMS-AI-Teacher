from __future__ import annotations

from app.ai.memory.service import MemoryService
from app.ai.state import TeacherState


async def retrieve_memories_node(state: TeacherState) -> dict:
    service = MemoryService()

    student_id = state.get("student_id", "")
    concept_id = state.get("concept_id", "")
    lesson_id = state.get("lesson_id", "")

    context = await service.retrieve_relevant(student_id, concept_id, lesson_id)

    memory_context = await service.format_memory_context(student_id, concept_id, lesson_id)

    return {
        "memory_context": memory_context,
        "memory_observations": [o.model_dump(mode="json") for o in context.observations],
    }
