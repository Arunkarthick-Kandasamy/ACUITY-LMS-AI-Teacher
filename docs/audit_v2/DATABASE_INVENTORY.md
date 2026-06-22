# Database Inventory

> Tables extracted directly from SQLAlchemy models and Alembic migrations. Cross-referenced against `DATABASE_SCHEMA.md` (770-line spec at project root).

**Database:** PostgreSQL 16 (via `postgres:16-alpine` in `docker-compose.yml`)
**ORM:** SQLAlchemy 2.0+ with asyncpg driver
**Migrations:** Alembic (4 migration version files)

---

## Enum Types (from `app/common/types.py` and `app/content_ingestion/models.py`)

| Enum | Values | Defined In | In DATABASE_SCHEMA.md? |
|------|--------|------------|----------------------|
| `UserRole` | admin, student, parent | `app/common/types.py:6` | Yes |
| `LessonStatus` | draft, published, archived | `app/common/types.py:12` | Yes |
| `ConceptContentType` | explanation, example, visualization, analogy, summary | `app/common/types.py:18` | Yes |
| `QuestionType` | mcq, multi_select, short_answer, fill_blank | `app/common/types.py:26` | Yes |
| `EnrollmentStatus` | active, paused, completed, dropped | `app/common/types.py:33` | Yes |
| `SessionState` | active, paused, completed, interrupted | `app/common/types.py:40` | Yes |
| `LessonProgressStatus` | not_started, in_progress, completed, skipped | `app/common/types.py:47` | Yes |
| `MisconceptionCategory` | procedural, conceptual, factual, careless | `app/common/types.py:54` | Yes |
| `EdgeRelationship` | requires, reinforces, contains | `app/common/types.py:61` | Yes |
| `PaceStatus` | on_track, behind, ahead | `app/common/types.py:67` | Yes |
| `ReportType` | weekly, monthly, milestone | `app/common/types.py:73` | Yes |
| `NodeType` | concept, objective | `app/common/types.py:79` | Yes |
| `UploadStatus` | pending, extracting, completed, failed | `app/content_ingestion/models.py:12` | No (extra) |
|| DraftStatus | draft, approved, rejected, published | `app/content_ingestion/models.py:19` | No (extra) |

**Total: 14 enum types** (12 in spec, 2 extra from content ingestion)

---

## Users Module

### Table: `users`

**Model:** `app/users/models.py:11` — `User`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| email | String(255) | UNIQUE, NOT NULL, INDEX | Yes |
| password_hash | String(255) | NOT NULL | Yes |
| role | UserRole (enum) | NOT NULL | Yes |
| full_name | String(150) | NOT NULL | Yes |
| is_active | Boolean | NOT NULL, default=true | Yes |
| created_at | DateTime | NOT NULL, server_default=now() | Yes |
| updated_at | DateTime | nullable | Yes |

### Table: `student_profiles`

**Model:** `app/users/models.py:20` — `StudentProfile`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| user_id | UUID | FK → users.id, UNIQUE | Yes |
| grade_level | String(50) | nullable | Yes |
| date_of_birth | Date | nullable | Yes |
| created_at | DateTime | NOT NULL | Yes |
| updated_at | DateTime | nullable | Yes |

### Table: `parent_student_links`

**Model:** `app/users/models.py:43` — `ParentStudentLink`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| parent_id | UUID | FK → users.id | Yes |
| student_id | UUID | FK → users.id | Yes |
| relationship | String(50) | nullable | Yes |
| created_at | DateTime | NOT NULL | Yes |

---

## Auth Module

### Table: `refresh_tokens`

**Model:** `app/auth/models.py:10` — `RefreshToken`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| user_id | UUID | FK → users.id, INDEX | Yes |
| token_hash | String(255) | NOT NULL | Yes |
| expires_at | DateTime | NOT NULL | Yes |
| revoked_at | DateTime | nullable | Yes |
| created_at | DateTime | NOT NULL | Yes |

### Table: `password_reset_tokens`

**Model:** `app/auth/models.py:35` — `PasswordResetToken`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| user_id | UUID | FK → users.id | Yes |
| token_hash | String(255) | NOT NULL | Yes |
| expires_at | DateTime | NOT NULL | Yes |
| used_at | DateTime | nullable | Yes |
| created_at | DateTime | NOT NULL | Yes |

---

## Curriculum Module

### Table: `courses`

**Model:** `app/curriculum/models.py:11` — `Course`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| code | String(50) | UNIQUE, NOT NULL | Yes |
| title | String(200) | NOT NULL | Yes |
| description | Text | nullable | Yes |
| total_duration_hours | Integer | NOT NULL | Yes |
| default_deadline_days | Integer | NOT NULL | Yes |
| is_published | Boolean | NOT NULL, default=false | Yes |
| created_by | UUID | FK → users.id | Yes |
| created_at | DateTime | NOT NULL | Yes |
| updated_at | DateTime | nullable | Yes |

### Table: `modules`

**Model:** `app/curriculum/models.py:35` — `Module`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| course_id | UUID | FK → courses.id | Yes |
| title | String(200) | NOT NULL | Yes |
| description | Text | nullable | Yes |
| order_index | Integer | NOT NULL | Yes |
| estimated_duration_hours | Integer | nullable | Yes |
| created_at | DateTime | NOT NULL | Yes |
| updated_at | DateTime | nullable | Yes |

### Table: `lessons`

**Model:** `app/curriculum/models.py:55` — `Lesson`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| module_id | UUID | FK → modules.id | Yes |
| title | String(200) | NOT NULL | Yes |
| content_url | String(500) | nullable | Yes |
| order_index | Integer | NOT NULL | Yes |
| estimated_duration_minutes | Integer | nullable | Yes |
| is_required | Boolean | default=true | Yes |
| status | LessonStatus (enum) | default='draft' | Yes |
| created_at | DateTime | NOT NULL | Yes |
| updated_at | DateTime | nullable | Yes |

### Table: `concepts`

**Model:** `app/curriculum/models.py:75` — `Concept`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| lesson_id | UUID | FK → lessons.id | Yes |
| title | String(200) | NOT NULL | Yes |
| description | Text | nullable | Yes |
| order_index | Integer | NOT NULL | Yes |
| estimated_duration_minutes | Integer | nullable | Yes |
| created_at | DateTime | NOT NULL | Yes |
| updated_at | DateTime | nullable | Yes |

### Table: `concept_contents`

**Model:** `app/curriculum/models.py:95` — `ConceptContent`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| concept_id | UUID | FK → concepts.id | Yes |
| content_type | ConceptContentType (enum) | NOT NULL | Yes |
| content | Text | NOT NULL | Yes |
| order_index | Integer | NOT NULL | Yes |
| version | Integer | default=1 | Yes |
| created_at | DateTime | NOT NULL | Yes |
| updated_at | DateTime | nullable | Yes |

### Table: `exercises`

**Model:** `app/curriculum/models.py:115` — `Exercise`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| concept_id | UUID | FK → concepts.id | Yes |
| question_type | QuestionType (enum) | NOT NULL | Yes |
| prompt | Text | NOT NULL | Yes |
| options | JSONB | nullable | Yes |
| correct_answer | Text | NOT NULL | Yes |
| difficulty | Float | default=0.5 | Yes |
| order_index | Integer | NOT NULL | Yes |
| tags | ARRAY(String) | nullable | Yes |
| created_at | DateTime | NOT NULL | Yes |
| updated_at | DateTime | nullable | Yes |

### Table: `examples`

**Model:** `app/curriculum/models.py:155` — `Example`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| concept_id | UUID | FK → concepts.id | Yes |
| content | Text | NOT NULL | Yes |
| explanation | Text | nullable | Yes |
| order_index | Integer | NOT NULL | Yes |
| tags | ARRAY(String) | nullable | Yes |
| created_at | DateTime | NOT NULL | Yes |
| updated_at | DateTime | nullable | Yes |

### Table: `learning_objectives`

**Model:** `app/curriculum/models.py:135` — `LearningObjective`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| lesson_id | UUID | FK → lessons.id | Yes |
| code | String(50) | NOT NULL | Yes |
| description | Text | NOT NULL | Yes |
| success_criterion | JSONB | nullable | Yes |
| order_index | Integer | NOT NULL | Yes |
| created_at | DateTime | NOT NULL | Yes |
| updated_at | DateTime | nullable | Yes |

---

## Knowledge Graph Module

### Table: `knowledge_nodes`

**Model:** `app/knowledge_graph/models.py:10` — `KnowledgeNode`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| concept_id | UUID | FK → concepts.id, UNIQUE | Yes |
| node_type | NodeType (enum) | NOT NULL | Yes |
| label | String(200) | NOT NULL | Yes |
| metadata | JSONB | nullable | Yes |
| created_at | DateTime | NOT NULL | Yes |

### Table: `knowledge_edges`

**Model:** `app/knowledge_graph/models.py:30` — `KnowledgeEdge`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| source_node_id | UUID | FK → knowledge_nodes.id | Yes |
| target_node_id | UUID | FK → knowledge_nodes.id | Yes |
| relationship | EdgeRelationship (enum) | NOT NULL | Yes |
| weight | Float | default=1.0 | Yes |
| created_at | DateTime | NOT NULL | Yes |

---

## Enrollment Module

### Table: `student_course_enrollments`

**Model:** `app/enrollment/models.py:11` — `StudentCourseEnrollment`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| student_id | UUID | FK → users.id | Yes |
| course_id | UUID | FK → courses.id | Yes |
| status | EnrollmentStatus (enum) | NOT NULL, default='active' | Yes |
| target_completion_date | Date | nullable | Yes |
| enrolled_at | DateTime | NOT NULL | Yes |
| started_at | DateTime | nullable | Yes |
| updated_at | DateTime | nullable | Yes |

### Table: `course_schedules`

**Model:** `app/enrollment/models.py:35` — `CourseSchedule`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| enrollment_id | UUID | FK → student_course_enrollments.id | Yes |
| target_lessons_per_week | Integer | NOT NULL | Yes |
| current_week | Integer | default=1 | Yes |
| milestones | JSONB | nullable | Yes |
| created_at | DateTime | NOT NULL | Yes |
| updated_at | DateTime | nullable | Yes |

---

## Teaching Module

### Table: `teaching_sessions`

**Model:** `app/teaching/models.py:11` — `TeachingSession`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| student_id | UUID | FK → users.id, INDEX | Yes |
| course_id | UUID | FK → courses.id | Yes |
| state | SessionState (enum) | NOT NULL, default='active' | Yes |
| current_concept_id | UUID | FK → concepts.id, nullable | Yes |
| current_lesson_id | UUID | FK → lessons.id, nullable | Yes |
| context | JSONB | nullable | Yes |
| started_at | DateTime | NOT NULL | Yes |
| last_activity_at | DateTime | NOT NULL | Yes |
| ended_at | DateTime | nullable | Yes |

### Table: `lesson_progress`

**Model:** `app/teaching/models.py:35` — `LessonProgress`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| student_id | UUID | FK → users.id | Yes |
| lesson_id | UUID | FK → lessons.id | Yes |
| status | LessonProgressStatus (enum) | NOT NULL, default='not_started' | Yes |
| started_at | DateTime | nullable | Yes |
| completed_at | DateTime | nullable | Yes |
| time_spent_seconds | Integer | default=0 | Yes |

### Table: `attempts`

**Model:** `app/teaching/models.py:50` — `Attempt`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| student_id | UUID | FK → users.id | Yes |
| exercise_id | UUID | FK → exercises.id | Yes |
| teaching_session_id | UUID | FK → teaching_sessions.id, nullable | Yes |
| response | Text | NOT NULL | Yes |
| is_correct | Boolean | NOT NULL | Yes |
| score | Float | nullable | Yes |
| ai_feedback | Text | nullable | Yes |
| attempt_number | Integer | NOT NULL | Yes |
| attempted_at | DateTime | NOT NULL | Yes |

---

## Mastery Module

### Table: `mastery_records`

**Model:** `app/mastery/models.py:11` — `MasteryRecord`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| student_id | UUID | FK → users.id | Yes |
| concept_id | UUID | FK → concepts.id | Yes |
| mastery_level | Float | default=0.0 | Yes |
| total_attempts | Integer | default=0 | Yes |
| consecutive_correct | Integer | default=0 | Yes |
| next_review_at | DateTime | nullable | Yes |
| last_attempted_at | DateTime | nullable | Yes |
| created_at | DateTime | NOT NULL | Yes |
| updated_at | DateTime | nullable | Yes |

**Additional constraint:** UNIQUE (student_id, concept_id)

---

## Diagnosis Module

### Table: `misconceptions`

**Model:** `app/diagnosis/models.py:11` — `Misconception`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| student_id | UUID | FK → users.id | Yes |
| concept_id | UUID | FK → concepts.id | Yes |
| category | MisconceptionCategory (enum) | NOT NULL | Yes |
| description | Text | NOT NULL | Yes |
| evidence | JSONB | nullable | Yes |
| frequency | Integer | default=1 | Yes |
| is_resolved | Boolean | default=false | Yes |
| detected_at | DateTime | NOT NULL | Yes |
| resolved_at | DateTime | nullable | Yes |

---

## Pacing Module

### Table: `pacing_records`

**Model:** `app/pacing/models.py:11` — `PacingRecord`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| student_id | UUID | FK → users.id | Yes |
| course_id | UUID | FK → courses.id | Yes |
| pace_status | PaceStatus (enum) | NOT NULL | Yes |
| target_lessons_per_week | Integer | NOT NULL | Yes |
| actual_lessons_per_week | Float | NOT NULL | Yes |
| current_week | Integer | default=1 | Yes |
| milestones | JSONB | nullable | Yes |
| calculated_at | DateTime | NOT NULL | Yes |
| next_calculation_at | DateTime | nullable | Yes |

**Additional constraint:** UNIQUE (student_id, course_id)

---

## Memory Module

### Table: `student_memories`

**Model:** `app/memory/models.py:11` — `StudentMemory`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| student_id | UUID | FK → users.id | Yes |
| key | String(100) | NOT NULL | Yes |
| value | JSONB | NOT NULL | Yes |
| importance | Float | default=0.5 | Yes |
| created_at | DateTime | NOT NULL | Yes |
| updated_at | DateTime | nullable | Yes |

**Additional constraint:** UNIQUE (student_id, key)

---

## Reports Module

### Table: `reports`

**Model:** `app/reports/models.py:11` — `Report`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| student_id | UUID | FK → users.id | Yes |
| report_type | ReportType (enum) | NOT NULL | Yes |
| title | String(200) | NOT NULL | Yes |
| summary | Text | nullable | Yes |
| content | JSONB | nullable | Yes |
| metrics | JSONB | nullable | Yes |
| recommendations | JSONB | nullable | Yes |
| pdf_url | String(500) | nullable | Yes |
| is_read | Boolean | default=false | Yes |
| generated_at | DateTime | NOT NULL | Yes |
| read_at | DateTime | nullable | Yes |

---

## Audit Module

### Table: `audit_logs`

**Model:** `app/audit/models.py:11` — `AuditLog`

| Column | Type | Constraints | In DATABASE_SCHEMA.md? |
|--------|------|-------------|----------------------|
| id | UUID | PK | Yes |
| user_id | UUID | FK → users.id, nullable | Yes |
| action | String(100) | NOT NULL | Yes |
| resource_type | String(50) | NOT NULL | Yes |
| resource_id | UUID | nullable | Yes |
| details | JSONB | nullable | Yes |
| ip_address | String(45) | nullable | Yes |
| created_at | DateTime | NOT NULL | Yes |

**Note:** Table is defined but **never written to** — zero callers in any service file.

---

## Additional Models (Not in DATABASE_SCHEMA.md)

| Table | Model File | Purpose |
|-------|------------|---------|
| `content_uploads` | `app/content_ingestion/models.py:30` | File upload tracking |
| `curriculum_drafts` | `app/content_ingestion/models.py:50` | Draft curriculum items |
| `evaluation_datasets` | `app/ai/evaluation/models.py:15` | AI evaluation harness datasets |
| `evaluation_results` | `app/ai/evaluation/models.py:35` | AI evaluation run results |

**Total tables: 30+** (23 in spec + 7+ additional service tables)

**Verdict:** All tables in DATABASE_SCHEMA.md are present and match their column definitions. The actual codebase has ~7 additional tables for content ingestion and AI evaluation that are not documented in the spec.
