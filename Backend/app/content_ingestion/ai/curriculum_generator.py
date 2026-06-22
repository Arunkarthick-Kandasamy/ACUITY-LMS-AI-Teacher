from __future__ import annotations

import logging
import re
import uuid
from typing import Any

from app.common.types import NodeType
from app.curriculum.service import CourseService
from app.knowledge_graph.service import KnowledgeGraphService

logger = logging.getLogger(__name__)


class CurriculumGenerator:
    def __init__(self, course_service: CourseService, kg_service: KnowledgeGraphService) -> None:
        self.course_service = course_service
        self.kg_service = kg_service
        self._concept_node_map: dict[str, str] = {}

    async def publish(self, user_id: str, generated_data: dict[str, Any]) -> str:
        self._concept_node_map = {}

        course = await self.course_service.create_course(
            user_id=user_id,
            code=self._generate_code(generated_data.get("title", "Generated Course")),
            title=generated_data.get("title", "Generated Course"),
            description=generated_data.get("description", ""),
            total_duration_hours=generated_data.get("total_duration_hours", 40),
            default_deadline_days=generated_data.get("default_deadline_days", 90),
        )

        for mod_data in generated_data.get("modules", []):
            module = await self.course_service.create_module(
                course_id=course.id,
                title=mod_data.get("title", "Untitled Module"),
                description=mod_data.get("description", ""),
                order_index=mod_data.get("order_index", 1),
                estimated_duration_hours=mod_data.get("estimated_duration_hours", 8),
            )

            for lsn_data in mod_data.get("lessons", []):
                lesson = await self.course_service.create_lesson(
                    module_id=module.id,
                    title=lsn_data.get("title", "Untitled Lesson"),
                    order_index=lsn_data.get("order_index", 1),
                    estimated_duration_minutes=lsn_data.get("estimated_duration_minutes", 30),
                    is_required=lsn_data.get("is_required", True),
                    status="draft",
                )

                for obj_data in lsn_data.get("objectives", []):
                    await self.course_service.create_objective(
                        lesson_id=lesson.id,
                        code=obj_data.get("code", f"GEN.{lesson.order_index}.{obj_data.get('order_index', 1)}"),
                        description=obj_data.get("description", ""),
                        order_index=obj_data.get("order_index", 1),
                    )

                for con_data in lsn_data.get("concepts", []):
                    concept = await self.course_service.create_concept(
                        lesson_id=lesson.id,
                        title=con_data.get("title", "Untitled Concept"),
                        description=con_data.get("description", ""),
                        order_index=con_data.get("order_index", 1),
                        estimated_duration_minutes=con_data.get("estimated_duration_minutes", 15),
                    )

                    node = await self.kg_service.node_repo.create(
                        concept_id=concept.id,
                        node_type=NodeType.CONCEPT,
                        label=concept.title,
                    )
                    self._concept_node_map[concept.title] = node.id

                    for ct_data in con_data.get("contents", []):
                        await self.course_service.create_content(
                            concept_id=concept.id,
                            content_type=ct_data.get("content_type", "explanation"),
                            content=ct_data.get("content", ""),
                            order_index=ct_data.get("order_index", 0),
                        )

                    for ex_data in con_data.get("exercises", []):
                        await self.course_service.create_exercise(
                            concept_id=concept.id,
                            question_type=ex_data.get("question_type", "short_answer"),
                            prompt=ex_data.get("prompt", ""),
                            options=ex_data.get("options"),
                            correct_answer=ex_data.get("correct_answer", ""),
                            difficulty=ex_data.get("difficulty", 0.5),
                            order_index=ex_data.get("order_index", 1),
                        )

                    for eg_data in con_data.get("examples", []):
                        await self.course_service.create_example(
                            concept_id=concept.id,
                            content=eg_data.get("content", ""),
                            explanation=eg_data.get("explanation", ""),
                            order_index=eg_data.get("order_index", 1),
                            tags=eg_data.get("tags", []),
                        )

        await self._create_knowledge_edges(generated_data.get("knowledge_graph", []))

        return course.id

    async def _create_knowledge_edges(self, kg_edges: list[dict[str, Any]]) -> None:
        for edge_data in kg_edges:
            source_title = edge_data.get("source_concept_title", "")
            target_title = edge_data.get("target_concept_title", "")
            if not source_title or not target_title:
                continue

            source_id = self._concept_node_map.get(source_title)
            target_id = self._concept_node_map.get(target_title)

            if source_id is None:
                node = await self.kg_service.node_repo.find_by_label(source_title)
                source_id = node.id if node else None
            if target_id is None:
                node = await self.kg_service.node_repo.find_by_label(target_title)
                target_id = node.id if node else None

            if source_id and target_id and source_id != target_id:
                try:
                    await self.kg_service.create_edge(
                        source_node_id=source_id,
                        target_node_id=target_id,
                        relationship=edge_data.get("relationship", "requires"),
                        weight=edge_data.get("weight", 0.8),
                    )
                except Exception as e:
                    logger.warning(
                        "Failed to create KG edge '%s' -> '%s': %s",
                        source_title, target_title, e,
                    )

    @staticmethod
    def _generate_code(title: str) -> str:
        safe = re.sub(r"[^a-zA-Z0-9]+", "-", title).strip("-").upper()
        if not safe:
            safe = "COURSE"
        short_id = uuid.uuid4().hex[:6].upper()
        return f"{safe}-{short_id}"
