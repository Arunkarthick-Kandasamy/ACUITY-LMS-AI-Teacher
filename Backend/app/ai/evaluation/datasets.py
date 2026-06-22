from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvaluationScenario:
    label: str
    concept_title: str
    concept_description: str
    concept_content: list[dict]
    examples: list[dict]
    student_response: str | None
    current_action: str | None
    mastery_estimate: float
    expected_action: str | None
    expected_nodes: list[str]
    expected_mastery_range: tuple[float, float]
    prerequisite_concepts: list[dict] = field(default_factory=list)
    memory_context: str | None = None
    diagnosis_result: dict | None = None


MASTERED_STUDENT = EvaluationScenario(
    label="mastered_student",
    concept_title="Variables",
    concept_description="Understanding variables in programming",
    concept_content=[
        {"content_type": "explanation", "content": "A variable is a container for storing data values."}
    ],
    examples=[],
    student_response="A variable stores data that can be changed.",
    current_action="ask_question",
    mastery_estimate=0.0,
    expected_action="complete_concept",
    expected_nodes=["evaluate_response", "diagnose", "complete_concept"],
    expected_mastery_range=(0.7, 1.0),
)

STRUGGLING_STUDENT = EvaluationScenario(
    label="struggling_student",
    concept_title="Variables",
    concept_description="Understanding variables in programming",
    concept_content=[
        {"content_type": "explanation", "content": "A variable is a container for storing data values."}
    ],
    examples=[{"content": "x = 5", "explanation": "Assigns value 5 to variable x"}],
    student_response="I don't know what a variable is.",
    current_action="ask_question",
    mastery_estimate=0.0,
    expected_action="reteach",
    expected_nodes=["evaluate_response", "diagnose", "retrieve_memories", "teach", "ask_question"],
    expected_mastery_range=(0.0, 0.5),
)

MISCONCEPTION_CASE = EvaluationScenario(
    label="misconception_case",
    concept_title="Variables",
    concept_description="Understanding variables in programming",
    concept_content=[
        {"content_type": "explanation", "content": "A variable is a container for storing data values."}
    ],
    examples=[],
    student_response="A variable is something that always stays the same.",
    current_action="ask_question",
    mastery_estimate=0.0,
    expected_action="example",
    expected_nodes=["evaluate_response", "diagnose", "provide_example", "ask_question"],
    expected_mastery_range=(0.0, 0.5),
)

PREREQUISITE_GAP_CASE = EvaluationScenario(
    label="prerequisite_gap_case",
    concept_title="Functions",
    concept_description="Understanding functions in programming",
    concept_content=[
        {"content_type": "explanation", "content": "A function is a reusable block of code."}
    ],
    examples=[{"content": "def add(a, b): return a + b", "explanation": "Function example"}],
    student_response="I don't understand how data flows through functions.",
    current_action="ask_question",
    mastery_estimate=0.0,
    expected_action="prerequisite",
    expected_nodes=["evaluate_response", "diagnose", "retrieve_memories", "teach", "ask_question"],
    expected_mastery_range=(0.0, 0.5),
    prerequisite_concepts=[
        {"id": "con-1", "label": "Variables", "title": "Variables", "relationship": "requires"},
    ],
)

SCENARIOS: list[EvaluationScenario] = [
    MASTERED_STUDENT,
    STRUGGLING_STUDENT,
    MISCONCEPTION_CASE,
    PREREQUISITE_GAP_CASE,
]

SCENARIO_MAP: dict[str, EvaluationScenario] = {s.label: s for s in SCENARIOS}


def get_scenario(label: str) -> EvaluationScenario | None:
    return SCENARIO_MAP.get(label)


def build_initial_state(scenario: EvaluationScenario) -> dict[str, Any]:
    return {
        "session_id": "eval-session",
        "student_id": "eval-student",
        "concept_id": "eval-concept",
        "lesson_id": "eval-lesson",
        "current_action": scenario.current_action,
        "conversation_history": [],
        "student_response": scenario.student_response,
        "mastery_estimate": scenario.mastery_estimate,
        "teaching_content": "Teaching content placeholder.",
        "question": "What is a variable?",
        "evaluation": None,
        "example_content": None,
        "errors": [],
        "concept_title": scenario.concept_title,
        "concept_description": scenario.concept_description,
        "concept_content": scenario.concept_content,
        "examples": scenario.examples,
        "prerequisite_concepts": scenario.prerequisite_concepts,
        "recommended_action": None,
        "diagnosis_result": None,
        "expected_answer": None,
        "memory_context": scenario.memory_context,
        "memory_observations": [],
    }
