# Database Audit

## Overview

- **Engine:** PostgreSQL 16 (via asyncpg driver)
- **ORM:** SQLAlchemy 2.0 Async
- **Migrations:** Alembic (4 migration files)
- **Tables:** 30
- **ENUM types:** 14
- **Connection pool:** pool_size=5, max_overflow=10, pool_pre_ping=True, pool_recycle=3600

---

## Entity-Relationship Diagram

```
┌─────────────┐     ┌──────────────────┐     ┌───────────────────┐
│    users    │1───*│ student_profiles │1───*│ parent_student_   │
│             │     │                  │     │ links             │
│ PK: id      │     │ PK: id           │     │                   │
│ email (UQ)  │     │ FK: user_id      │     │ PK: id            │
│ role (enum) │     │ grade_level      │     │ FK: parent_id     │
│ is_active   │     │ avg_session_dur  │     │ FK: student_id    │
│             │     │ current_streak   │     │ (UQ: parent_id,   │
└──────┬──────┘     │ metadata (JSONB) │     │  student_id)      │
       │            └────────┬─────────┘     └───────────────────┘
       │                     │
       │                     │
       │       ┌─────────────┼──────────────────────────┐
       │       │             │                          │
       ▼       ▼             ▼                          ▼
┌──────────────┐   ┌─────────────────┐   ┌─────────────────────┐
│   courses    │   │ student_course_  │   │   teaching_sessions │
│              │   │ enrollments     │   │                     │
│ PK: id       │   │                 │   │ PK: id              │
│ code (UQ)    │   │ PK: id          │   │ FK: student_id      │
│ created_by   │*──│ FK: student_id  │*──│ FK: course_id       │
│ (FK: users)  │   │ FK: course_id   │   │ FK: current_concept │
│ is_published │   │ status (enum)   │   │ FK: current_lesson  │
└──────┬───────┘   │ UQ: student_id, │   │ state (enum)        │
       │           │     course_id   │   │ context (JSONB)     │
       │           └────────┬────────┘   └──────────┬──────────┘
       │                    │                        │
       ▼                    ▼                        │
┌──────────────┐   ┌─────────────────┐              │
│   modules    │   │ course_schedules│              │
│              │   │                 │              │
│ PK: id       │   │ PK: id          │              │
│ FK: course_id│   │ FK: enrollment  │              │
│ UQ: (course, │   │ pace_status     │              │
│     order)   │   │ milestones(JSONB)│             │
└──────┬───────┘   │ UQ: enrollment   │              │
       │           └─────────────────┘              │
       ▼                                            │
┌──────────────┐   ┌──────────────────┐             │
│   lessons    │   │  lesson_progress │             │
│              │   │                  │             │
│ PK: id       │*──│ PK: id           │             │
│ FK: module_id│   │ FK: student_id   │             │
│ status (enum)│   │ FK: lesson_id    │             │
│ UQ: (module, │   │ status (enum)    │             │
│     order)   │   │ time_spent_sec   │             │
└──────┬───────┘   │ UQ: student,lessn│             │
       │           └──────────────────┘             │
       ▼                                            │
┌──────────────┐   ┌──────────────────┐             │
│   concepts   │   │  mastery_records │             │
│              │   │                  │             │
│ PK: id       │*──│ PK: id           │             │
│ FK: lesson_id│   │ FK: student_id   │             │
│ UQ: (lesson, │   │ FK: concept_id   │             │
│     order)   │   │ mastery_level    │             │
└──────┬───────┘   │ next_review_at   │             │
       │           │ UQ: student,conpt│             │
       │           └──────────────────┘             │
       │                                            │
       ├────────────────────┐                       │
       │                    │                       │
       ▼                    ▼                       ▼
┌──────────────┐   ┌──────────────────┐   ┌──────────────────┐
│concept_      │   │   exercises      │   │  misconceptions  │
│ contents     │   │                  │   │                  │
│              │   │ PK: id           │   │ PK: id           │
│ PK: id       │   │ FK: concept_id   │   │ FK: student_id   │
│ FK: concept  │   │ question_type    │   │ FK: concept_id   │
│ content_type │   │ prompt           │   │ FK: session_id   │
│ UQ: (concept,│   │ correct_answer   │   │ category (enum)  │
│  type,order) │   │ difficulty (idx) │   │ evidence (JSONB) │
└──────────────┘   └────────┬─────────┘   │ frequency        │
                            │              │ is_resolved      │
                            ▼              └──────────────────┘
                    ┌──────────────────┐
                    │    attempts      │
                    │                  │
                    │ PK: id           │
                    │ FK: student_id   │
                    │ FK: exercise_id  │
                    │ FK: session_id   │
                    │ is_correct       │
                    │ score            │
                    │ ai_feedback      │
                    │ attempt_number   │
                    │ metadata (JSONB) │
                    └──────────────────┘

┌──────────────────┐   ┌──────────────────┐   ┌─────────────────┐
│ knowledge_nodes  │   │ knowledge_edges  │   │ learning_       │
│                  │   │                  │   │ objectives      │
│ PK: id           │1──*│ PK: id           │   │                 │
│ FK: concept_id   │   │ FK: source_node  │   │ PK: id          │
│ FK: objective_id │   │ FK: target_node  │   │ FK: lesson_id   │
│ node_type (enum) │   │ relationship     │   │ code (UQ, idx)  │
│ label (idx)      │   │ (enum)           │   │ description     │
│ CHECK: concept   │   │ weight           │   │ success_crit    │
│   OR objective   │   │ UQ: source,target│   │ order_index     │
│ metadata (JSONB) │   │     ,relationship│   └─────────────────┘
└──────────────────┘   │ CHECK: source <> │
                        │    target        │
                        └──────────────────┘

┌──────────────────┐   ┌──────────────────┐   ┌─────────────────┐
│ student_memories │   │ memory_entries   │   │    examples     │
│                  │   │                  │   │                 │
│ PK: id           │   │ PK: id           │   │ PK: id          │
│ FK: student_id   │   │ FK: student_id   │   │ FK: concept_id  │
│ key              │   │ memory_key       │   │ content         │
│ value (JSONB)    │   │ memory_text      │   │ explanation     │
│ importance (idx) │   │ confidence       │   │ order_index     │
│ UQ: student,key  │   │ is_active        │   │ tags (ARRAY)    │
└──────────────────┘   │ UQ: student,key, │   └─────────────────┘
                       │      text        │
                       └──────────────────┘

┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│   reports        │   │   audit_logs     │   │  refresh_tokens  │
│                  │   │                  │   │                  │
│ PK: id           │   │ PK: id           │   │ PK: id           │
│ FK: student_id   │   │ FK: user_id      │   │ FK: user_id      │
│ FK: parent_id    │   │ action (idx)     │   │ token_hash (idx) │
│ report_type(enum)│   │ entity_type      │   │ expires_at       │
│ title            │   │ entity_id        │   │ revoked_at       │
│ report_data(JSONB)│  │ old_value (JSONB)│   └──────────────────┘
│ recommendations  │   │ new_value (JSONB)│   ┌──────────────────┐
│ is_read          │   │ timestamp (idx)  │   │password_reset_   │
└──────────────────┘   └──────────────────┘   │ tokens           │
                                               │                  │
┌──────────────────┐   ┌──────────────────┐   │ PK: id           │
│ content_uploads  │   │ curriculum_drafts│   │ FK: user_id      │
│                  │   │                  │   │ token_hash (idx) │
│ PK: id           │1──*│ PK: id           │   │ expires_at       │
│ FK: user_id      │   │ FK: upload_id    │   │ used_at          │
│ filename         │   │ FK: created_by   │   └──────────────────┘
│ file_type        │   │ title            │
│ file_size        │   │ status (draft→   │   ┌──────────────────┐
│ file_path        │   │        approved→ │   │  graph_traces    │
│ status (pending→ │   │        published)│   │                  │
│   extracting→    │   │ generated_data   │   │ PK: id           │
│   completed/fail)│   │   (JSONB)        │   │ FK: session_id   │
│ extracted_text   │   │ FK: course_id    │   │ trace_data(JSONB)│
│ error_message    │   └──────────────────┘   │ node_transitions │
└──────────────────┘                          │ token_usage      │
                                               │ final_action     │
                                               │ final_mastery    │
                                               │ model_calls      │
                                               └──────────────────┘
```

---

## Full Table Inventory

| # | Table | Model Class | Module | Created In | Rows Est. |
|---|-------|-------------|--------|------------|:---------:|
| 1 | `users` | `User` | `users/models.py` | 0001 | Core |
| 2 | `student_profiles` | `StudentProfile` | `users/models.py` | 0001 | Core |
| 3 | `parent_student_links` | `ParentStudentLink` | `users/models.py` | 0001 | Core |
| 4 | `courses` | `Course` | `curriculum/models.py` | 0001 | Core |
| 5 | `modules` | `Module` | `curriculum/models.py` | 0001 | Core |
| 6 | `lessons` | `Lesson` | `curriculum/models.py` | 0001 | Core |
| 7 | `concepts` | `Concept` | `curriculum/models.py` | 0001 | Core |
| 8 | `concept_contents` | `ConceptContent` | `curriculum/models.py` | 0001 | Core |
| 9 | `learning_objectives` | `LearningObjective` | `curriculum/models.py` | 0001 | Core |
| 10 | `examples` | `Example` | `curriculum/models.py` | 0001 | Core |
| 11 | `exercises` | `Exercise` | `curriculum/models.py` | 0001 | Core |
| 12 | `teaching_sessions` | `TeachingSession` | `teaching/models.py` | 0001 | Core |
| 13 | `lesson_progress` | `LessonProgress` | `teaching/models.py` | 0001 | Core |
| 14 | `attempts` | `Attempt` | `teaching/models.py` | 0001 | Core |
| 15 | `student_course_enrollments` | `StudentCourseEnrollment` | `enrollment/models.py` | 0001 | Core |
| 16 | `course_schedules` | `CourseSchedule` | `enrollment/models.py` | 0001 | Core |
| 17 | `mastery_records` | `MasteryRecord` | `mastery/models.py` | 0001 | Core |
| 18 | `knowledge_nodes` | `KnowledgeNode` | `knowledge_graph/models.py` | 0001 | Core |
| 19 | `knowledge_edges` | `KnowledgeEdge` | `knowledge_graph/models.py` | 0001 | Core |
| 20 | `misconceptions` | `Misconception` | `diagnosis/models.py` | 0001 | Core |
| 21 | `student_memories` | `StudentMemory` | `memory/models.py` | 0001 | Core |
| 22 | `memory_entries` | `MemoryEntry` | `memory/models.py` | 0001 | Core |
| 23 | `reports` | `Report` | `reports/models.py` | 0001 | Core |
| 24 | `refresh_tokens` | `RefreshToken` | `auth/models.py` | 0002 | Core |
| 25 | `password_reset_tokens` | `PasswordResetToken` | `auth/models.py` | 0002 | Core |
| 26 | `audit_logs` | `AuditLog` | `audit/models.py` | 0001 | Low |
| 27 | `graph_traces` | `GraphTrace` | `evaluation/models.py` | 0001 | Low |
| 28 | `teacher_metrics_snapshots` | `TeacherMetricsSnapshot` | `evaluation/models.py` | 0001 | Low |
| 29 | `content_uploads` | `ContentUpload` | `content_ingestion/models.py` | 0004 | Core |
| 30 | `curriculum_drafts` | `CurriculumDraft` | `content_ingestion/models.py` | 0004 | Core |

---

## ENUM Types (14)

| Enum Name | Python Class | Values |
|-----------|-------------|--------|
| `user_role` | `UserRole` | `admin`, `student`, `parent` |
| `lesson_status` | `LessonStatus` | `draft`, `published`, `archived` |
| `concept_content_type` | `ConceptContentType` | `explanation`, `example`, `visualization`, `analogy`, `summary` |
| `question_type` | `QuestionType` | `mcq`, `multi_select`, `short_answer`, `fill_blank` |
| `enrollment_status` | `EnrollmentStatus` | `active`, `paused`, `completed`, `dropped` |
| `session_state` | `SessionState` | `active`, `paused`, `completed`, `interrupted` |
| `lesson_progress_status` | `LessonProgressStatus` | `not_started`, `in_progress`, `completed`, `skipped` |
| `misconception_category` | `MisconceptionCategory` | `procedural`, `conceptual`, `factual`, `careless` |
| `edge_relationship` | `EdgeRelationship` | `requires`, `reinforces`, `contains` |
| `pace_status` | `PaceStatus` | `on_track`, `behind`, `ahead` |
| `report_type` | `ReportType` | `weekly`, `monthly`, `milestone` |
| `node_type` | `NodeType` | `concept`, `objective` |
| _(not in DB)_ | `UploadStatus` | `pending`, `extracting`, `completed`, `failed` |
| _(not in DB)_ | `DraftStatus` | `draft`, `approved`, `rejected`, `published` |

**Note:** `UploadStatus` and `DraftStatus` are VARCHAR(20) fields, not PG ENUMs — managed in Python.

---

## Indexes Summary

All tables have indexes on:
- Primary key (`id`) via UUIDMixin
- Foreign key columns (automatically or explicitly indexed)
- Status/type columns frequently queried

**Notable indexes:**
- `users.email` — unique index
- `courses.code` — unique index
- `exercises.difficulty` — sorted access for adaptive questioning
- `mastery_records.next_review_at` — spaced repetition scheduling
- `mastery_records.mastery_level` — ranking queries
- `knowledge_nodes.label`, `knowledge_nodes.node_type` — graph traversal
- `knowledge_nodes.concept_id`, `knowledge_nodes.objective_id` — entity linking
- `audit_logs.action`, `audit_logs.timestamp` — audit trail queries

---

## Constraints Summary

### Unique Constraints
1. `users.email`
2. `courses.code`
3. `modules(course_id, order_index)`
4. `lessons(module_id, order_index)`
5. `concepts(lesson_id, order_index)`
6. `concept_contents(concept_id, content_type, order_index)`
7. `learning_objectives(lesson_id, code)`
8. `lesson_progress(student_id, lesson_id)`
9. `student_course_enrollments(student_id, course_id)` — named `uq_student_active_enrollment`
10. `course_schedules(enrollment_id)` — one schedule per enrollment
11. `mastery_records(student_id, concept_id)`
12. `student_memories(student_id, key)`
13. `memory_entries(student_id, memory_key, memory_text)`
14. `knowledge_edges(source_node_id, target_node_id, relationship)`
15. `parent_student_links(parent_id, student_id)`

### Check Constraints
1. `knowledge_nodes`: `concept_id IS NOT NULL OR objective_id IS NOT NULL`
2. `knowledge_edges`: `source_node_id <> target_node_id` (no self-loops)

### Foreign Key Constraints
- All FKs use CASCADE on DELETE except:
  - `teaching_sessions.current_concept_id` → ON DELETE SET NULL
  - `teaching_sessions.current_lesson_id` → ON DELETE SET NULL
  - `knowledge_nodes.concept_id` → ON DELETE SET NULL
  - `knowledge_nodes.objective_id` → ON DELETE SET NULL
  - `audit_logs.user_id` → ON DELETE SET NULL
  - `reports.parent_id` → ON DELETE SET NULL
  - `curriculum_drafts.upload_id` → ON DELETE SET NULL
  - `curriculum_drafts.course_id` → ON DELETE SET NULL
  - `student_course_enrollments.current_concept_id` → ON DELETE SET NULL
  - `misconceptions.detected_in_session_id` → ON DELETE SET NULL

---

## Migration History

| Migration | Revises | Date | Description |
|-----------|---------|------|-------------|
| `0001_create_all_tables.py` | _(none)_ | — | 12 ENUMs + 23 tables (core schema) |
| `0002_create_auth_tables.py` | 0001 | — | `refresh_tokens`, `password_reset_tokens` |
| `0003_add_report_title_and_data.py` | 0002 | — | `reports.title`, `reports.report_data` (JSONB) |
| `0004_add_content_ingestion_tables.py` | 0003 | — | `content_uploads`, `curriculum_drafts` |

---

## Usage Analysis

### Heavily Used Tables (Core business operations)
- `users`, `student_profiles` — authentication, authorization
- `courses`, `modules`, `lessons`, `concepts` — curriculum backbone
- `teaching_sessions` — active teaching sessions
- `lesson_progress` — per-student progress tracking
- `attempts` — student exercise answers
- `mastery_records` — concept mastery scoring
- `knowledge_nodes`, `knowledge_edges` — knowledge graph prerequisites
- `student_course_enrollments`, `course_schedules` — enrollment and pacing

### Medium Usage
- `concept_contents` — teaching content storage
- `exercises`, `examples` — exercise/example bank
- `learning_objectives` — curriculum objectives
- `misconceptions` — diagnosis output storage
- `reports` — generated parent reports
- `refresh_tokens`, `password_reset_tokens` — auth token management
- `content_uploads`, `curriculum_drafts` — content ingestion pipeline

### Low Usage / Append-Only
- `audit_logs` — model exists but no service writes to it systematically
- `graph_traces` — evaluation harness traces
- `teacher_metrics_snapshots` — metrics snapshots
- `student_memories`, `memory_entries` — memory extraction (only written during teaching sessions)

### Tables with No Direct Service
- `audit_logs` — model exists, no service layer or router
- `memory_entries` — only accessed through MemoryService internally
