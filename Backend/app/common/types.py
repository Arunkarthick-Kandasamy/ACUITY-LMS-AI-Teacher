from __future__ import annotations

import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STUDENT = "student"
    PARENT = "parent"
    TEACHER = "teacher"


class LessonStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ConceptContentType(str, enum.Enum):
    EXPLANATION = "explanation"
    EXAMPLE = "example"
    VISUALIZATION = "visualization"
    ANALOGY = "analogy"
    SUMMARY = "summary"


class QuestionType(str, enum.Enum):
    MCQ = "mcq"
    MULTI_SELECT = "multi_select"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    NUMERIC = "numeric"
    FILL_BLANK = "fill_blank"


class EnrollmentStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    DROPPED = "dropped"


class SessionState(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"


class LessonProgressStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class MisconceptionCategory(str, enum.Enum):
    PROCEDURAL = "procedural"
    CONCEPTUAL = "conceptual"
    FACTUAL = "factual"
    CARELESS = "careless"


class EdgeRelationship(str, enum.Enum):
    REQUIRES = "requires"
    REINFORCES = "reinforces"
    CONTAINS = "contains"


class AssessmentType(str, enum.Enum):
    QUIZ = "quiz"
    PRACTICE_TEST = "practice_test"
    CHAPTER_TEST = "chapter_test"
    DIAGNOSTIC = "diagnostic"
    FINAL = "final"


class PaceStatus(str, enum.Enum):
    ON_TRACK = "on_track"
    BEHIND = "behind"
    AHEAD = "ahead"


class ReportType(str, enum.Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    MILESTONE = "milestone"


class NodeType(str, enum.Enum):
    CONCEPT = "concept"
    OBJECTIVE = "objective"
