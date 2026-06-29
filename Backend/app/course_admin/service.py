from __future__ import annotations

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.services.gemini import GeminiService
from app.common.exceptions import ConflictException, ForbiddenException, NotFoundException, ValidationException
from app.common.types import UserRole
from app.content_ingestion.parsers import parse_file
from app.course_admin.models import (
    Course,
    CourseStatus,
    KnowledgeSource,
    PipelineStage,
    PipelineStageName,
    StageStatus,
    STAGE_ORDER,
    STAGE_LABELS,
)
from app.course_admin.repository import CourseRepository, KnowledgeSourceRepository, PipelineStageRepository
from app.curriculum.service import CourseService
from app.users.models import User

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(__file__).parent.parent / "content_ingestion" / "uploads"


def _log(stage: PipelineStage, message: str, level: str = "info") -> None:
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "message": message,
        "level": level,
    }
    logs = list(stage.stage_logs or [])
    logs.append(entry)
    stage.stage_logs = logs


class PipelineOrchestrator:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.course_repo = CourseRepository(session)
        self.stage_repo = PipelineStageRepository(session)
        self.source_repo = KnowledgeSourceRepository(session)
        self.course_service = CourseService(session)
        self.gemini = GeminiService()

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    async def create_course(self, current_user: User, name: str, description: str | None = None) -> Course:
        course = await self.course_repo.create(
            user_id=current_user.id,
            name=name,
            description=description,
            status=CourseStatus.DRAFT,
        )
        for stage_name in STAGE_ORDER:
            await self.stage_repo.create(
                course_id=course.id,
                stage_name=stage_name.value,
                status=StageStatus.PENDING.value,
                progress_pct=0,
                stage_logs=[{"ts": datetime.now(timezone.utc).isoformat(), "message": "Awaiting processing", "level": "info"}],
            )
        await self._reload_course(course)
        return course

    async def get_course(self, current_user: User, course_id: str) -> Course:
        course = await self.course_repo.get(course_id)
        if course is None:
            raise NotFoundException(message="Course not found")
        self._verify_access(current_user, course.user_id)
        return course

    async def list_courses(self, current_user: User) -> list[Course]:
        return await self.course_repo.find_by_user(current_user.id)

    async def delete_course(self, current_user: User, course_id: str) -> None:
        course = await self.get_course(current_user, course_id)
        if course.status == CourseStatus.DEPLOYED.value:
            raise ConflictException(
                message="Cannot delete a published course. Archive it first.",
                code="PUBLISHED_COURSE",
            )
        deleted = await self.course_repo.delete(course_id)
        if not deleted:
            raise NotFoundException(message="Course not found")

    async def retry_stage(self, current_user: User, course_id: str, stage_name: str) -> Course:
        await self.get_course(current_user, course_id)
        stage = await self.stage_repo.find_by_stage(course_id, stage_name)
        if stage is None:
            raise NotFoundException(message="Stage not found")
        stage.status = StageStatus.PENDING.value
        stage.progress_pct = 0
        stage.error_message = None
        stage.retry_count += 1
        stage.started_at = None
        stage.completed_at = None
        _log(stage, f"Retry #{stage.retry_count} initiated")
        await self.session.flush()
        course = await self._load_full_course(course_id)
        self._sync_status(course)
        return course

    # ------------------------------------------------------------------
    # Knowledge Source ingestion
    # ------------------------------------------------------------------

    async def upload_source(self, current_user: User, course_id: str, filename: str, content: bytes) -> KnowledgeSource:
        course = await self.get_course(current_user, course_id)
        file_type = self._file_type(filename)
        if file_type is None:
            raise ValidationException(message="Unsupported type. Use pdf, docx, or txt.", code="UNSUPPORTED_TYPE")
        if len(content) == 0:
            raise ValidationException(message="File is empty", code="EMPTY_FILE")
        if len(content) > 50 * 1024 * 1024:
            raise ValidationException(message="File exceeds 50MB limit", code="FILE_TOO_LARGE")

        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        stored = self._save(content, filename)

        source = await self.source_repo.create(
            course_id=course_id,
            filename=filename,
            file_type=file_type,
            file_size=len(content),
            file_path=str(stored),
            status="uploaded",
        )

        stage = await self.stage_repo.find_by_stage(course_id, PipelineStageName.UPLOAD.value)
        if stage:
            stage.progress_pct = min(100, stage.progress_pct + 50)
            _log(stage, f"Uploaded: {filename} ({(len(content) / 1024):.0f} KB)")
            await self.session.flush()

        return source

    # ------------------------------------------------------------------
    # Background processing engine
    # ------------------------------------------------------------------

    async def run_stage_background(self, current_user: User, course_id: str, stage_name: str) -> Course:
        course = await self.get_course(current_user, course_id)
        stage = await self.stage_repo.find_by_stage(course_id, stage_name)
        if stage is None:
            raise NotFoundException(message="Stage not found")

        stage.status = StageStatus.IN_PROGRESS.value
        stage.started_at = datetime.now(timezone.utc)
        stage.error_message = None
        stage.progress_pct = 0
        _log(stage, "Starting...")
        await self.session.flush()

        asyncio.create_task(self._execute_stage(course_id, stage_name, current_user.id))
        return course

    async def _execute_stage(self, course_id: str, stage_name: str, user_id: str) -> None:
        try:
            async with self._new_session() as session:
                orch = PipelineOrchestrator(session)
                course = await orch._load_full_course(course_id)
                if course is None:
                    logger.error("Course %s not found for background task", course_id)
                    return
                stage = await orch.stage_repo.find_by_stage(course_id, stage_name)
                if stage is None or stage.status != StageStatus.IN_PROGRESS.value:
                    return

                stage.progress_pct = 5
                _log(stage, "Loaded course context")
                await session.flush()

                runner = getattr(orch, f"_run_{stage_name}", None)
                if runner is None:
                    _log(stage, f"No handler for stage '{stage_name}'", "error")
                    stage.status = StageStatus.FAILED.value
                    stage.error_message = f"No handler for stage '{stage_name}'"
                    stage.completed_at = datetime.now(timezone.utc)
                    await session.flush()
                    return

                await runner(course, stage)
        except Exception as e:
            logger.error("Background stage %s for course %s failed: %s", stage_name, course_id, e)
            try:
                async with self._new_session() as session:
                    stage_repo = PipelineStageRepository(session)
                    stage = await stage_repo.find_by_stage(course_id, stage_name)
                    if stage:
                        stage.status = StageStatus.FAILED.value
                        stage.error_message = str(e)
                        stage.completed_at = datetime.now(timezone.utc)
                        _log(stage, f"Fatal error: {e}", "error")
                        await session.flush()
            except Exception as e2:
                logger.error("Failed to record failure for stage %s: %s", stage_name, e2)

    # ------------------------------------------------------------------
    # Stage: upload
    # ------------------------------------------------------------------

    async def _run_upload(self, course: Course, stage: PipelineStage) -> None:
        _log(stage, f"{len(course.sources)} file(s) uploaded")
        stage.progress_pct = 100
        stage.status = StageStatus.COMPLETED.value
        stage.completed_at = datetime.now(timezone.utc)
        stage.output_data = {"sources": [{"id": str(s.id), "name": s.filename, "size": s.file_size} for s in course.sources]}
        await self.session.flush()

    # ------------------------------------------------------------------
    # Stage: extract
    # ------------------------------------------------------------------

    async def _run_extract(self, course: Course, stage: PipelineStage) -> None:
        total = len(course.sources)
        for idx, source in enumerate(course.sources):
            if source.status == "extracted":
                continue
            pct = int((idx / total) * 80) + 10
            stage.progress_pct = pct
            _log(stage, f"Extracting: {source.filename}")
            await self.session.flush()

            try:
                text = parse_file(source.file_path, source.file_type)
                source.extracted_text = text
                source.status = "extracted"
                _log(stage, f"Extracted {len(text)} chars from {source.filename}")
            except Exception as e:
                source.status = "failed"
                source.error_message = str(e)
                _log(stage, f"Extraction failed for {source.filename}: {e}", "error")

            await self.session.flush()

        failed = sum(1 for s in course.sources if s.status == "failed")
        extracted_count = sum(1 for s in course.sources if s.status == "extracted")

        accumulated = ""
        for s in course.sources:
            if s.extracted_text:
                accumulated += f"\n\n--- {s.filename} ---\n\n{s.extracted_text}"

        course.knowledge_sources = {
            "total": total,
            "extracted": extracted_count,
            "failed": failed,
            "total_chars": len(accumulated),
        }

        if failed == total:
            stage.status = StageStatus.FAILED.value
            stage.error_message = "All files failed extraction"
            _log(stage, "All files failed extraction", "error")
        else:
            stage.progress_pct = 100
            stage.status = StageStatus.COMPLETED.value
            _log(stage, f"Extraction complete: {extracted_count}/{total} files")
        stage.completed_at = datetime.now(timezone.utc)
        stage.output_data = {"extracted": extracted_count, "failed": failed, "total_chars": len(accumulated)}
        await self.session.flush()

    # ------------------------------------------------------------------
    # Stage: understand
    # ------------------------------------------------------------------

    async def _run_understand(self, course: Course, stage: PipelineStage) -> None:
        all_text = ""
        for s in course.sources:
            if s.extracted_text:
                all_text += f"\n\n--- {s.filename} ---\n\n{s.extracted_text}"

        if not all_text:
            stage.status = StageStatus.FAILED.value
            stage.error_message = "No extracted text available"
            _log(stage, "No extracted text to analyze", "error")
            stage.completed_at = datetime.now(timezone.utc)
            await self.session.flush()
            return

        stage.progress_pct = 10
        _log(stage, f"Analyzing {len(all_text)} characters of content")
        await self.session.flush()

        stage.progress_pct = 20
        _log(stage, "Extracting concepts and relationships via AI")
        await self.session.flush()

        try:
            prompt = (
                "You are an expert curriculum analyst. Analyze the following educational content.\n\n"
                "Extract and return a JSON object with:\n"
                "1. \"concepts\": array of {title: string, description: string, difficulty: 1-5, keywords: string[], bloom_taxonomy_level: string}\n"
                "2. \"relationships\": array of {source: string, target: string, type: \"prerequisite\" | \"related_to\" | \"contains\" | \"reinforces\"}\n"
                "3. \"teaching_order\": array of concept titles in pedagogical order\n"
                "4. \"subject_domain\": string — the subject area (e.g. Mathematics, Physics)\n"
                "5. \"estimated_grade_level\": string — e.g. \"9-12\", \"undergraduate\"\n"
                "6. \"missing_prerequisites\": array of concepts the learner should know first (inferred gaps)\n\n"
                "Be thorough. Extract ALL concepts, not just major ones.\n\n"
                f"CONTENT:\n{all_text[:60000]}"
            )
            result = await self.gemini.generate_json(prompt)
            stage.progress_pct = 80
            _log(stage, f"Extracted {len(result.get('concepts', []))} concepts, {len(result.get('relationships', []))} relationships")
            await self.session.flush()

            course.knowledge_graph_data = result
            stage.output_data = {
                "concept_count": len(result.get("concepts", [])),
                "relationship_count": len(result.get("relationships", [])),
                "domain": result.get("subject_domain", ""),
                "missing_prerequisites": result.get("missing_prerequisites", []),
            }

            stage.progress_pct = 100
            stage.status = StageStatus.COMPLETED.value
            _log(stage, "Knowledge graph built successfully")
        except Exception as e:
            stage.status = StageStatus.FAILED.value
            stage.error_message = str(e)
            _log(stage, f"AI understanding failed: {e}", "error")

        stage.completed_at = datetime.now(timezone.utc)
        await self.session.flush()

    # ------------------------------------------------------------------
    # Stage: validate
    # ------------------------------------------------------------------

    async def _run_validate(self, course: Course, stage: PipelineStage) -> None:
        kg = course.knowledge_graph_data
        if not kg:
            stage.status = StageStatus.FAILED.value
            stage.error_message = "No knowledge graph data to validate"
            stage.completed_at = datetime.now(timezone.utc)
            await self.session.flush()
            return

        concepts = kg.get("concepts", [])
        rels = kg.get("relationships", [])
        teaching_order = kg.get("teaching_order", [])

        issues = []
        if not concepts:
            issues.append("No concepts extracted")
        if not teaching_order:
            issues.append("No teaching order defined")
        concept_titles = {c["title"] for c in concepts}
        for rel in rels:
            if rel.get("source") not in concept_titles:
                issues.append(f"Relationship source '{rel.get('source')}' missing from concepts")
            if rel.get("target") not in concept_titles:
                issues.append(f"Relationship target '{rel.get('target')}' missing from concepts")

        stage.output_data = {
            "concept_count": len(concepts),
            "relationship_count": len(rels),
            "teaching_order_length": len(teaching_order),
            "issues": issues,
            "quality_score": max(0, 100 - len(issues) * 10),
        }

        stage.status = StageStatus.COMPLETED.value
        _log(stage, f"Validation complete: {len(concepts)} concepts, {len(rels)} relationships")
        if issues:
            for iss in issues[:5]:
                _log(stage, f"Issue: {iss}", "warning")
        stage.completed_at = datetime.now(timezone.utc)
        await self.session.flush()

    # ------------------------------------------------------------------
    # Stage: profile
    # ------------------------------------------------------------------

    async def _run_profile(self, course: Course, stage: PipelineStage) -> None:
        kg = course.knowledge_graph_data
        if not kg:
            stage.status = StageStatus.FAILED.value
            stage.error_message = "Knowledge graph required"
            _log(stage, "Knowledge graph missing", "error")
            stage.completed_at = datetime.now(timezone.utc)
            await self.session.flush()
            return

        stage.progress_pct = 20
        _log(stage, "Generating teaching profile from knowledge graph")
        await self.session.flush()

        try:
            prompt = (
                "Create a detailed teaching profile for a course based on the content knowledge graph.\n"
                "Return a JSON object with:\n"
                "1. teaching_style: string — one of: socratic, explanatory, interactive, adaptive, flipped_classroom\n"
                "2. difficulty_curve: 1-5 (1=gentle, 5=steep)\n"
                "3. explanation_depth: string — one of: basic, moderate, deep, comprehensive\n"
                "4. preferred_example_types: array of strings (e.g. real_world, analogy, visual, case_study)\n"
                "5. assessment_style: string — one of: quiz_based, project_based, mixed, continuous\n"
                "6. strengths: array of strings — topic areas the course excels at based on concept depth\n"
                "7. weaknesses: array of strings — areas needing human oversight\n"
                "8. adaptation_rules: {struggling: string, advancing: string} — how to adapt\n"
                "9. pacing: {default_minutes_per_concept: int, max_minutes_per_concept: int}\n"
                "10. language_complexity: string — one of: simple, moderate, academic, adaptive\n\n"
                f"KNOWLEDGE_GRAPH:\n{json.dumps(kg, indent=2)[:12000]}"
            )
            result = await self.gemini.generate_json(prompt)
            course.teaching_profile = result
            stage.output_data = {
                "teaching_style": result.get("teaching_style"),
                "explanation_depth": result.get("explanation_depth"),
                "assessment_style": result.get("assessment_style"),
                "strengths": result.get("strengths", []),
            }
            _log(stage, f"Profile generated: {result.get('teaching_style')} style, {result.get('explanation_depth')} depth")
            stage.progress_pct = 100
            stage.status = StageStatus.COMPLETED.value
        except Exception as e:
            stage.status = StageStatus.FAILED.value
            stage.error_message = str(e)
            _log(stage, f"Profile generation failed: {e}", "error")

        stage.completed_at = datetime.now(timezone.utc)
        await self.session.flush()

    # ------------------------------------------------------------------
    # Stage: structure
    # ------------------------------------------------------------------

    async def _run_structure(self, course: Course, stage: PipelineStage) -> None:
        kg = course.knowledge_graph_data
        profile = course.teaching_profile
        if not kg or not profile:
            stage.status = StageStatus.FAILED.value
            stage.error_message = "Knowledge graph and profile required"
            stage.completed_at = datetime.now(timezone.utc)
            await self.session.flush()
            return

        stage.progress_pct = 10
        _log(stage, "Generating course structure from knowledge graph and teaching profile")
        await self.session.flush()

        try:
            prompt = (
                "Design a complete course structure. Return valid JSON:\n"
                "{\n"
                '  "title": "Course Title",\n'
                '  "description": "Course description",\n'
                '  "total_duration_hours": number,\n'
                '  "default_deadline_days": number,\n'
                '  "code_hint": "unique-course-code",\n'
                '  "target_audience": string,\n'
                '  "prerequisites": [strings],\n'
                '  "learning_outcomes": [strings],\n'
                '  "modules": [{\n'
                '    "title": string,\n'
                '    "description": string,\n'
                '    "order_index": number,\n'
                '    "estimated_duration_hours": number,\n'
                '    "lessons": [{\n'
                '      "title": string,\n'
                '      "order_index": number,\n'
                '      "estimated_duration_minutes": number,\n'
                '      "is_required": bool,\n'
                '      "objectives": [{"code": string, "description": string, "order_index": number}],\n'
                '      "concepts": [{"title": string, "description": string, "order_index": number, "estimated_duration_minutes": number}]\n'
                "    }]\n"
                "  }]\n"
                "}\n\n"
                f"KNOWLEDGE_GRAPH:\n{json.dumps(kg, indent=2)[:8000]}\n"
                f"TEACHING_PROFILE:\n{json.dumps(profile, indent=2)[:5000]}"
            )
            result = await self.gemini.generate_json(prompt)
            course.course_structure = result
            stage.progress_pct = 100
            stage.status = StageStatus.COMPLETED.value

            mod_count = len(result.get("modules", []))
            lesson_count = sum(len(m.get("lessons", [])) for m in result.get("modules", []))
            concept_count = sum(
                sum(len(l.get("concepts", [])) for l in m.get("lessons", []))
                for m in result.get("modules", [])
            )
            stage.output_data = {
                "modules": mod_count,
                "lessons": lesson_count,
                "concepts": concept_count,
                "title": result.get("title"),
                "total_hours": result.get("total_duration_hours"),
            }
            _log(stage, f"Structure generated: {mod_count} modules, {lesson_count} lessons, {concept_count} concepts")
        except Exception as e:
            stage.status = StageStatus.FAILED.value
            stage.error_message = str(e)
            _log(stage, f"Structure generation failed: {e}", "error")

        stage.completed_at = datetime.now(timezone.utc)
        await self.session.flush()

    # ------------------------------------------------------------------
    # Stage: generate (content + assessments)
    # ------------------------------------------------------------------

    async def _run_generate(self, course: Course, stage: PipelineStage) -> None:
        structure = course.course_structure
        profile = course.teaching_profile
        if not structure or not profile:
            stage.status = StageStatus.FAILED.value
            stage.error_message = "Course structure and profile required"
            stage.completed_at = datetime.now(timezone.utc)
            await self.session.flush()
            return

        all_text = ""
        for s in course.sources:
            if s.extracted_text:
                all_text += f"\n\n--- {s.filename} ---\n\n{s.extracted_text}"

        concepts_list = []
        for mod in structure.get("modules", []):
            for lesson in mod.get("lessons", []):
                for con in lesson.get("concepts", []):
                    concepts_list.append(con)

        total_concepts = len(concepts_list)
        _log(stage, f"Generating content for {total_concepts} concepts")
        await self.session.flush()

        for idx, concept in enumerate(concepts_list):
            stage.progress_pct = int((idx / total_concepts) * 90) + 5
            _log(stage, f"Generating: {concept.get('title', 'Untitled')} ({idx + 1}/{total_concepts})")
            await self.session.flush()

            try:
                prompt = (
                    f"Generate comprehensive teaching content for the concept '{concept.get('title')}'.\n"
                    f"Description: {concept.get('description', '')}\n\n"
                    "Return JSON:\n"
                    "{\n"
                    '  "explanation": "2-3 paragraph comprehensive explanation",\n'
                    '  "examples": [{"content": string, "explanation": string}],\n'
                    '  "exercises": [{"question_type": "mcq|true_false|short_answer", "prompt": string, "options": {}|null, "correct_answer": string, "difficulty": 0-1}],\n'
                    '  "key_points": [string],\n'
                    '  "common_misconceptions": [{"misconception": string, "correction": string}],\n'
                    '  "analogies": [string],\n'
                    '  "estimated_difficulty": 1-5,\n'
                    '  "bloom_level": "remember|understand|apply|analyze|evaluate|create"\n'
                    "}\n\n"
                    f"Teaching style: {profile.get('teaching_style', 'explanatory')}\n"
                    f"Depth: {profile.get('explanation_depth', 'moderate')}\n"
                    f"Reference: {all_text[:10000]}"
                )
                result = await self.gemini.generate_json(prompt)
                concept["content"] = result
            except Exception as e:
                _log(stage, f"Failed to generate content for '{concept.get('title')}': {e}", "warning")
                concept["content"] = {"explanation": "", "examples": [], "exercises": [], "key_points": [], "common_misconceptions": []}

            await self.session.flush()

        course.course_structure = structure
        stage.progress_pct = 95
        _log(stage, "Content generation complete. Running quality check...")
        await self.session.flush()

        concepts_with_content = sum(1 for c in concepts_list if c.get("content", {}).get("explanation"))
        total_exercises = sum(
            len(c.get("content", {}).get("exercises", []))
            for c in concepts_list if c.get("content")
        )
        stage.output_data = {
            "concepts_generated": concepts_with_content,
            "total_exercises": total_exercises,
            "total_concepts": total_concepts,
            "coverage_pct": round(concepts_with_content / total_concepts * 100) if total_concepts else 0,
        }
        stage.progress_pct = 100
        stage.status = StageStatus.COMPLETED.value
        _log(stage, f"Generated content for {concepts_with_content}/{total_concepts} concepts with {total_exercises} exercises")
        stage.completed_at = datetime.now(timezone.utc)
        await self.session.flush()

    # ------------------------------------------------------------------
    # Stage: review
    # ------------------------------------------------------------------

    async def _run_review(self, course: Course, stage: PipelineStage) -> None:
        structure = course.course_structure
        if not structure:
            stage.status = StageStatus.FAILED.value
            stage.error_message = "No content to review"
            stage.completed_at = datetime.now(timezone.utc)
            await self.session.flush()
            return

        mod_count = len(structure.get("modules", []))
        lesson_count = sum(len(m.get("lessons", [])) for m in structure.get("modules", []))
        concept_count = sum(
            sum(len(l.get("concepts", [])) for l in m.get("lessons", []))
            for m in structure.get("modules", [])
        )
        concepts_with_content = sum(
            1 for m in structure.get("modules", [])
            for l in m.get("lessons", [])
            for c in l.get("concepts", [])
            if c.get("content", {}).get("explanation")
        )

        total_exercises = sum(
            len(c.get("content", {}).get("exercises", []))
            for m in structure.get("modules", [])
            for l in m.get("lessons", [])
            for c in l.get("concepts", []) if c.get("content")
        )

        coverage = round(concepts_with_content / concept_count * 100) if concept_count else 0

        stage.output_data = {
            "modules": mod_count,
            "lessons": lesson_count,
            "concepts": concept_count,
            "concepts_with_content": concepts_with_content,
            "exercises": total_exercises,
            "coverage_pct": coverage,
        }
        stage.progress_pct = 100
        stage.status = StageStatus.COMPLETED.value
        course.status = CourseStatus.REVIEW.value
        _log(stage, f"Review complete: {coverage}% coverage, {total_exercises} exercises")
        stage.completed_at = datetime.now(timezone.utc)
        await self.session.flush()

    # ------------------------------------------------------------------
    # Stage: simulate
    # ------------------------------------------------------------------

    async def _run_simulate(self, course: Course, stage: PipelineStage) -> None:
        structure = course.course_structure
        profile = course.teaching_profile
        if not structure or not profile:
            stage.status = StageStatus.FAILED.value
            stage.error_message = "Course structure and profile required"
            stage.completed_at = datetime.now(timezone.utc)
            await self.session.flush()
            return

        concept_titles = [
            c.get("title", "")
            for m in structure.get("modules", [])
            for l in m.get("lessons", [])
            for c in l.get("concepts", [])
        ]

        if not concept_titles:
            stage.status = StageStatus.FAILED.value
            stage.error_message = "No concepts to simulate"
            stage.completed_at = datetime.now(timezone.utc)
            await self.session.flush()
            return

        stage.progress_pct = 20
        sample = concept_titles[:5]
        _log(stage, f"Running simulation on {len(sample)} sample concepts")
        await self.session.flush()

        try:
            prompt = (
                "Simulate a course conducting a lesson. Use the teaching profile and concepts.\n"
                "Return JSON:\n"
                "{\n"
                '  "sample_interaction": [{"role": "teacher|student", "message": string}],\n'
                '  "estimated_effectiveness": 0.0-1.0,\n'
                '  "potential_challenges": [string],\n'
                '  "recommended_adjustments": [string],\n'
                '  "strengths_observed": [string],\n'
                '  "engagement_score": 0.0-1.0,\n'
                '  "clarity_score": 0.0-1.0,\n'
                '  "adaptability_score": 0.0-1.0\n'
                "}\n\n"
                f"PROFILE:\n{json.dumps(profile, indent=2)[:3000]}\n"
                f"CONCEPTS:\n{json.dumps(sample)}"
            )
            result = await self.gemini.generate_json(prompt)
            course.simulation_results = result
            stage.output_data = {
                "effectiveness": result.get("estimated_effectiveness"),
                "engagement": result.get("engagement_score"),
                "clarity": result.get("clarity_score"),
                "challenges": result.get("potential_challenges", []),
            }
            stage.progress_pct = 100
            stage.status = StageStatus.COMPLETED.value
            _log(stage, f"Simulation complete. Effectiveness: {result.get('estimated_effectiveness', 0):.0%}")
        except Exception as e:
            stage.status = StageStatus.FAILED.value
            stage.error_message = str(e)
            _log(stage, f"Simulation failed: {e}", "error")

        stage.completed_at = datetime.now(timezone.utc)
        await self.session.flush()

    # ------------------------------------------------------------------
    # Stage: deploy
    # ------------------------------------------------------------------

    async def _run_deploy(self, course: Course, stage: PipelineStage) -> None:
        structure = course.course_structure
        if not structure:
            stage.status = StageStatus.FAILED.value
            stage.error_message = "No course structure to deploy"
            stage.completed_at = datetime.now(timezone.utc)
            await self.session.flush()
            return

        _log(stage, "Creating course in the system")
        stage.progress_pct = 10
        await self.session.flush()

        try:
            course_code = f"AI-{uuid.uuid4().hex[:6].upper()}"
            created = await self.course_service.create_course(
                user_id=course.user_id,
                code=course_code,
                title=structure.get("title", course.name)[:200],
                description=structure.get("description", course.description or "")[:500],
                total_duration_hours=structure.get("total_duration_hours", 40),
                default_deadline_days=structure.get("default_deadline_days", 90),
            )
            stage.progress_pct = 20
            _log(stage, f"Course created: {created.title}")
            await self.session.flush()

            for mi, mod_data in enumerate(structure.get("modules", [])):
                module = await self.course_service.create_module(
                    course_id=created.id,
                    title=mod_data.get("title", f"Module {mi + 1}")[:200],
                    description=mod_data.get("description", "")[:500],
                    order_index=mod_data.get("order_index", mi + 1),
                    estimated_duration_hours=mod_data.get("estimated_duration_hours", 8),
                )
                _log(stage, f"  Module: {module.title}")

                for li, lsn_data in enumerate(mod_data.get("lessons", [])):
                    lesson = await self.course_service.create_lesson(
                        module_id=module.id,
                        title=lsn_data.get("title", f"Lesson {li + 1}")[:200],
                        order_index=lsn_data.get("order_index", li + 1),
                        estimated_duration_minutes=lsn_data.get("estimated_duration_minutes", 30),
                        is_required=lsn_data.get("is_required", True),
                        status="draft",
                    )

                    for obj_data in lsn_data.get("objectives", []):
                        await self.course_service.create_objective(
                            lesson_id=lesson.id,
                            code=obj_data.get("code", f"KG.{li + 1}.{obj_data.get('order_index', 1)}"),
                            description=obj_data.get("description", "")[:500],
                            order_index=obj_data.get("order_index", 1),
                        )

                    for ci, con_data in enumerate(lsn_data.get("concepts", [])):
                        concept = await self.course_service.create_concept(
                            lesson_id=lesson.id,
                            title=con_data.get("title", f"Concept {ci + 1}")[:200],
                            description=con_data.get("description", "")[:500],
                            order_index=con_data.get("order_index", ci + 1),
                            estimated_duration_minutes=con_data.get("estimated_duration_minutes", 15),
                        )

                        content_data = con_data.get("content", {})
                        if content_data:
                            if content_data.get("explanation"):
                                await self.course_service.create_content(
                                    concept_id=concept.id,
                                    content_type="explanation",
                                    content=content_data["explanation"][:5000],
                                    order_index=0,
                                )
                            if content_data.get("key_points"):
                                await self.course_service.create_content(
                                    concept_id=concept.id,
                                    content_type="summary",
                                    content="\n".join(f"- {p}" for p in content_data["key_points"][:10])[:5000],
                                    order_index=1,
                                )
                            for ex in content_data.get("examples", [])[:5]:
                                await self.course_service.create_example(
                                    concept_id=concept.id,
                                    content=ex.get("content", str(ex)) if isinstance(ex, dict) else str(ex),
                                    explanation=ex.get("explanation", "") if isinstance(ex, dict) else "",
                                    order_index=ex.get("order_index", 1) if isinstance(ex, dict) else 1,
                                )
                            for ex in content_data.get("exercises", [])[:10]:
                                await self.course_service.create_exercise(
                                    concept_id=concept.id,
                                    question_type=ex.get("question_type", "short_answer"),
                                    prompt=ex.get("prompt", ""),
                                    options=ex.get("options"),
                                    correct_answer=ex.get("correct_answer", ""),
                                    difficulty=ex.get("difficulty", 0.5),
                                    order_index=ex.get("order_index", 1),
                                )

            course.course_id = created.id
            stage.progress_pct = 90
            _log(stage, "Course materials deployed")
            await self.session.flush()

            stage.progress_pct = 100
            stage.status = StageStatus.COMPLETED.value
            course.status = CourseStatus.DEPLOYED.value
            stage.output_data = {"course_id": str(created.id), "course_code": course_code, "course_title": created.title}
            _log(stage, f"Course published: {created.title} ({course_code})")
        except Exception as e:
            stage.status = StageStatus.FAILED.value
            stage.error_message = str(e)
            _log(stage, f"Publish failed: {e}", "error")

        stage.completed_at = datetime.now(timezone.utc)
        await self.session.flush()

    # ------------------------------------------------------------------
    # Profile / KG / Structure manual updates
    # ------------------------------------------------------------------

    async def update_kg(self, current_user: User, course_id: str, kg_data: dict) -> Course:
        course = await self.get_course(current_user, course_id)
        course.knowledge_graph_data = kg_data
        await self.session.flush()
        stage = await self.stage_repo.find_by_stage(course_id, PipelineStageName.VALIDATE.value)
        if stage and stage.status != StageStatus.COMPLETED.value:
            stage.status = StageStatus.COMPLETED.value
            stage.progress_pct = 100
            stage.completed_at = datetime.now(timezone.utc)
            _log(stage, "Knowledge graph validated manually")
            await self.session.flush()
        return course

    async def update_profile(self, current_user: User, course_id: str, profile: dict) -> Course:
        course = await self.get_course(current_user, course_id)
        course.teaching_profile = profile
        await self.session.flush()
        return course

    async def update_structure(self, current_user: User, course_id: str, structure: dict) -> Course:
        course = await self.get_course(current_user, course_id)
        course.course_structure = structure
        await self.session.flush()
        return course

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _verify_access(self, current_user: User, owner_id: str) -> None:
        if current_user.role != UserRole.ADMIN and current_user.id != owner_id:
            raise ForbiddenException(code="ACCESS_DENIED", message="You do not have access to this resource")

    async def _load_full_course(self, course_id: str) -> Course | None:
        stmt = (
            select(Course)
            .options(selectinload(Course.stages), selectinload(Course.sources))
            .where(Course.id == course_id)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def _reload_course(self, course: Course) -> None:
        await self.session.refresh(course)
        for rel in ("stages", "sources"):
            if rel in course.__dict__:
                del course.__dict__[rel]

    def _sync_status(self, course: Course) -> None:
        stages = {s.stage_name: s.status for s in (course.stages or [])}
        completed = sum(1 for s in STAGE_ORDER if stages.get(s.value) == StageStatus.COMPLETED.value)
        failed = sum(1 for s in STAGE_ORDER if stages.get(s.value) == StageStatus.FAILED.value)
        if completed == len(STAGE_ORDER):
            course.status = CourseStatus.DEPLOYED.value
        elif course.status == CourseStatus.DEPLOYED.value:
            pass
        elif completed >= len(STAGE_ORDER) - 2:
            course.status = CourseStatus.REVIEW.value
        elif completed > 0 or failed > 0:
            course.status = CourseStatus.TRAINING.value

    def _new_session(self) -> AsyncSession:
        from app.infrastructure.database import async_session_factory
        if async_session_factory is None:
            raise RuntimeError("Database not initialized")
        return async_session_factory()

    @staticmethod
    def _file_type(filename: str) -> str | None:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        return ext if ext in ("txt", "pdf", "docx") else None

    @staticmethod
    def _save(content: bytes, filename: str) -> Path:
        p = UPLOAD_DIR / f"{uuid.uuid4().hex}_{filename}"
        p.write_bytes(content)
        return p
