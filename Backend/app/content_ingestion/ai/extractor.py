from __future__ import annotations

import logging
from typing import Any

from app.ai.services.gemini import GeminiService

from ..prompts import SYSTEM_CURRICULUM_EXTRACTION, TEXT_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)


class ContentExtractor:
    def __init__(self) -> None:
        self.gemini = GeminiService()

    async def extract(self, raw_text: str) -> dict[str, Any]:
        prompt = TEXT_EXTRACTION_PROMPT.format(raw_text=raw_text)
        try:
            result = await self.gemini.generate_json(prompt, SYSTEM_CURRICULUM_EXTRACTION)
            return self._validate(result)
        except Exception as e:
            logger.warning("Gemini extraction failed, using fallback: %s", e)
            return self._fallback(raw_text)

    def _validate(self, data: dict[str, Any]) -> dict[str, Any]:
        modules = []
        for m in data.get("modules", []):
            lessons = []
            for lsn in m.get("lessons", []):
                concepts = []
                for c in lsn.get("concepts", []):
                    concepts.append({
                        "title": str(c.get("title", "Untitled Concept")),
                        "description": str(c.get("description", "")),
                        "order_index": int(c.get("order_index", 1)),
                        "estimated_duration_minutes": int(c.get("estimated_duration_minutes", 15)),
                        "contents": [
                            {
                                "content_type": str(ct.get("content_type", "explanation")),
                                "content": str(ct.get("content", "")),
                                "order_index": int(ct.get("order_index", 0)),
                            }
                            for ct in c.get("contents", [])
                        ],
                        "exercises": [
                            {
                                "question_type": str(ex.get("question_type", "short_answer")),
                                "prompt": str(ex.get("prompt", "")),
                                "options": ex.get("options"),
                                "correct_answer": str(ex.get("correct_answer", "")),
                                "difficulty": float(ex.get("difficulty", 0.5)),
                                "order_index": int(ex.get("order_index", 1)),
                            }
                            for ex in c.get("exercises", [])
                        ],
                        "examples": [
                            {
                                "content": str(eg.get("content", "")),
                                "explanation": str(eg.get("explanation", "")),
                                "order_index": int(eg.get("order_index", 1)),
                                "tags": list(eg.get("tags", [])),
                            }
                            for eg in c.get("examples", [])
                        ],
                    })
                lessons.append({
                    "title": str(lsn.get("title", "Untitled Lesson")),
                    "order_index": int(lsn.get("order_index", 1)),
                    "estimated_duration_minutes": int(lsn.get("estimated_duration_minutes", 30)),
                    "is_required": bool(lsn.get("is_required", True)),
                    "concepts": concepts,
                    "objectives": [
                        {
                            "code": str(obj.get("code", "")),
                            "description": str(obj.get("description", "")),
                            "order_index": int(obj.get("order_index", 1)),
                        }
                        for obj in lsn.get("objectives", [])
                    ],
                })
            modules.append({
                "title": str(m.get("title", "Untitled Module")),
                "description": str(m.get("description", "")),
                "order_index": int(m.get("order_index", 1)),
                "estimated_duration_hours": int(m.get("estimated_duration_hours", 8)),
                "lessons": lessons,
            })

        return {
            "title": str(data.get("title", "Generated Course")),
            "description": str(data.get("description", "")),
            "total_duration_hours": int(data.get("total_duration_hours", 40)),
            "default_deadline_days": int(data.get("default_deadline_days", 90)),
            "modules": modules,
            "knowledge_graph": [
                {
                    "source_concept_title": str(kg.get("source_concept_title", "")),
                    "target_concept_title": str(kg.get("target_concept_title", "")),
                    "relationship": str(kg.get("relationship", "requires")),
                    "weight": float(kg.get("weight", 0.8)),
                }
                for kg in data.get("knowledge_graph", [])
            ],
        }

    def _fallback(self, raw_text: str) -> dict[str, Any]:
        lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
        title = lines[0] if lines else "Generated Course"
        return {
            "title": title[:300],
            "description": f"Auto-generated curriculum from: {title[:200]}",
            "total_duration_hours": 40,
            "default_deadline_days": 90,
            "modules": [
                {
                    "title": "Main Module",
                    "description": "Primary module generated from uploaded content",
                    "order_index": 1,
                    "estimated_duration_hours": 40,
                    "lessons": [
                        {
                            "title": "Lesson 1",
                            "order_index": 1,
                            "estimated_duration_minutes": 30,
                            "is_required": True,
                            "concepts": [
                                {
                                    "title": title[:200] if len(title) > 200 else title,
                                    "description": "Key concept from uploaded content",
                                    "order_index": 1,
                                    "estimated_duration_minutes": 15,
                                    "contents": [
                                        {
                                            "content_type": "explanation",
                                            "content": raw_text[:5000],
                                            "order_index": 0,
                                        }
                                    ],
                                    "exercises": [],
                                    "examples": [],
                                }
                            ],
                            "objectives": [],
                        }
                    ],
                }
            ],
            "knowledge_graph": [],
        }
