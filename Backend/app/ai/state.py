from __future__ import annotations

import enum
from typing import TypedDict


class TeacherAction(str, enum.Enum):
    TEACH = "teach"
    ASK_QUESTION = "ask_question"
    EVALUATE_RESPONSE = "evaluate_response"
    DIAGNOSE = "diagnose"
    PROVIDE_EXAMPLE = "provide_example"
    COMPLETE_CONCEPT = "complete_concept"


class TeacherState(TypedDict, total=False):
    session_id: str
    student_id: str
    concept_id: str
    lesson_id: str
    current_action: TeacherAction
    conversation_history: list[dict]
    student_response: str | None
    mastery_estimate: float
    teaching_content: str | None
    question: str | None
    evaluation: str | None
    example_content: str | None
    errors: list[str]
    concept_title: str | None
    concept_description: str | None
    concept_content: list[dict]
    examples: list[dict]
    # Diagnosis fields
    recommended_action: str | None
    diagnosis_result: dict | None
    prerequisite_concepts: list[dict]
    expected_answer: str | None
    # Memory fields
    memory_context: str | None
    memory_observations: list[dict]
