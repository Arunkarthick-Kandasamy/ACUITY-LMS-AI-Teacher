from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.diagnosis.service import DiagnosisService
from app.ai.graphs.teacher import teacher_graph
from app.ai.memory.service import MemoryService
from app.ai.state import TeacherAction, TeacherState
from app.auth.dependencies import get_current_active_user
from app.common.response import success_response
from app.config import settings
from app.curriculum.models import Concept, ConceptContent, Example
from app.infrastructure.database import get_session
from app.knowledge_graph.models import KnowledgeEdge, KnowledgeNode
from app.teaching.models import TeachingSession
from app.teaching_sessions.service import SessionService
from app.users.models import User

router = APIRouter(prefix=f"{settings.api_prefix}", tags=["AI Teacher"])


async def _load_session_data(
    session_id: str, db: AsyncSession
) -> tuple[TeachingSession, dict, list[dict], list[dict], list[dict]]:
    stmt = select(TeachingSession).where(TeachingSession.id == session_id)
    result = await db.execute(stmt)
    teaching_session = result.unique().scalar_one_or_none()

    empty = (teaching_session, {}, [], [], [])
    if teaching_session is None or teaching_session.current_concept_id is None:
        return empty

    concept_stmt = select(Concept).where(Concept.id == teaching_session.current_concept_id)
    result = await db.execute(concept_stmt)
    concept = result.unique().scalar_one_or_none()

    if concept is None:
        return teaching_session, {}, [], [], []

    content_stmt = (
        select(ConceptContent)
        .where(ConceptContent.concept_id == concept.id)
        .order_by(ConceptContent.order_index)
    )
    result = await db.execute(content_stmt)
    contents = result.unique().scalars().all()

    example_stmt = (
        select(Example)
        .where(Example.concept_id == concept.id)
        .order_by(Example.order_index)
    )
    result = await db.execute(example_stmt)
    examples = result.unique().scalars().all()

    concept_data = {
        "concept_title": concept.title,
        "concept_description": concept.description or "",
    }
    content_list = []
    for c in contents:
        ct = c.content_type.value if hasattr(c.content_type, "value") else c.content_type
        content_list.append({"content_type": ct, "content": c.content})
    example_list = [
        {"content": e.content, "explanation": e.explanation}
        for e in examples
    ]

    prereq_list = await _load_prerequisites(concept.id, db)

    return teaching_session, concept_data, content_list, example_list, prereq_list


async def _load_prerequisites(
    concept_id: str, db: AsyncSession
) -> list[dict]:
    node_stmt = select(KnowledgeNode).where(
        KnowledgeNode.concept_id == concept_id,
        KnowledgeNode.node_type == "concept",
    )
    result = await db.execute(node_stmt)
    concept_node = result.unique().scalar_one_or_none()
    if concept_node is None:
        return []

    edge_stmt = (
        select(KnowledgeEdge)
        .where(
            KnowledgeEdge.target_node_id == concept_node.id,
            KnowledgeEdge.relationship_type == "requires",
        )
        .join(
            KnowledgeNode,
            KnowledgeEdge.source_node_id == KnowledgeNode.id,
        )
    )
    result = await db.execute(edge_stmt)
    edges = result.unique().scalars().all()

    prereqs = []
    for edge in edges:
        prereq_node_stmt = select(KnowledgeNode).where(
            KnowledgeNode.id == edge.source_node_id
        )
        prereq_result = await db.execute(prereq_node_stmt)
        prereq_node = prereq_result.unique().scalar_one_or_none()
        if prereq_node is not None:
            rel_type = edge.relationship_type
            rel = rel_type.value if hasattr(rel_type, "value") else str(rel_type)
            prereqs.append({
                "id": prereq_node.id,
                "label": prereq_node.label,
                "title": prereq_node.label,
                "concept_id": prereq_node.concept_id,
                "relationship": rel,
            })

    return prereqs


@router.post("/teacher/teach")
async def teach(
    body: dict,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    session_id = body.get("session_id")
    student_response = body.get("student_response")

    if not session_id:
        return success_response({"action": "error", "error": "session_id is required"})

    session_service = SessionService(db)
    profile = await session_service._get_student_profile(current_user.id)
    teaching_session = await session_service._get_session_owned(session_id, profile.id)

    _, concept_data, content_list, example_list, prereq_list = await _load_session_data(
        session_id, db
    )

    conversation_history = teaching_session.context.get("conversation_history", [])
    current_action_raw = teaching_session.context.get("current_action")

    initial_state: TeacherState = {
        "session_id": session_id,
        "student_id": profile.id,
        "concept_id": teaching_session.current_concept_id or "",
        "lesson_id": teaching_session.current_lesson_id or "",
        "current_action": current_action_raw,
        "conversation_history": conversation_history,
        "student_response": student_response,
        "mastery_estimate": teaching_session.context.get("mastery_estimate", 0.0),
        "teaching_content": teaching_session.context.get("teaching_content"),
        "question": teaching_session.context.get("question"),
        "evaluation": teaching_session.context.get("evaluation"),
        "example_content": teaching_session.context.get("example_content"),
        "errors": [],
        "concept_title": concept_data.get("concept_title", "Unknown Concept"),
        "concept_description": concept_data.get("concept_description", ""),
        "concept_content": content_list,
        "examples": example_list,
        "prerequisite_concepts": prereq_list,
        "recommended_action": teaching_session.context.get("recommended_action"),
        "diagnosis_result": teaching_session.context.get("diagnosis_result"),
        "expected_answer": None,
    }

    result = await teacher_graph.ainvoke(initial_state)

    teaching_session.context["conversation_history"] = result.get("conversation_history", [])
    teaching_session.context["current_action"] = (
        result.get("current_action", TeacherAction.TEACH).value
        if isinstance(result.get("current_action"), TeacherAction)
        else result.get("current_action")
    )
    teaching_session.context["mastery_estimate"] = result.get("mastery_estimate", 0.0)
    teaching_session.context["question"] = result.get("question")
    teaching_session.context["teaching_content"] = result.get("teaching_content")
    teaching_session.context["evaluation"] = result.get("evaluation")
    teaching_session.context["example_content"] = result.get("example_content")
    teaching_session.context["recommended_action"] = result.get("recommended_action")
    teaching_session.context["diagnosis_result"] = result.get("diagnosis_result")
    await db.flush()

    diagnosis_result = result.get("diagnosis_result")
    if diagnosis_result and diagnosis_result.get("diagnosis_type") in (
        "misconception", "knowledge_gap"
    ):
        diag_service = DiagnosisService(db)
        await diag_service.persist_misconception(
            student_id=profile.id,
            concept_id=teaching_session.current_concept_id or "",
            category=diagnosis_result.get("misconception_category", "conceptual"),
            description=diagnosis_result.get("misconception") or diagnosis_result.get("knowledge_gap") or "",
            session_id=session_id,
            evidence=diagnosis_result.get("evidence", []),
        )

    memory_service = MemoryService(db)
    await memory_service.extract_and_store(
        student_id=profile.id,
        session_id=session_id,
        concept_title=concept_data.get("concept_title", ""),
        student_response=student_response or "",
        mastery_estimate=result.get("mastery_estimate", 0.0),
        evaluation=result.get("evaluation"),
        diagnosis_type=diagnosis_result.get("diagnosis_type") if diagnosis_result else None,
        misconception=diagnosis_result.get("misconception") if diagnosis_result else None,
        misconception_category=diagnosis_result.get("misconception_category") if diagnosis_result else None,
        knowledge_gap=diagnosis_result.get("knowledge_gap") if diagnosis_result else None,
        recommended_action=result.get("recommended_action"),
        evaluation_score=result.get("mastery_estimate"),
    )

    action = result.get("current_action", TeacherAction.TEACH)
    if isinstance(action, TeacherAction):
        action = action.value

    response_data: dict = {
        "session_id": session_id,
        "action": action,
        "mastery_estimate": result.get("mastery_estimate", 0.0),
    }

    if result.get("teaching_content"):
        response_data["teaching_content"] = result["teaching_content"]
    if result.get("question"):
        response_data["question"] = result["question"]
    if result.get("evaluation"):
        response_data["evaluation"] = result["evaluation"]
    if result.get("example_content"):
        response_data["example_content"] = result["example_content"]
    if result.get("diagnosis_result"):
        response_data["diagnosis"] = result["diagnosis_result"]

    return success_response(response_data)
