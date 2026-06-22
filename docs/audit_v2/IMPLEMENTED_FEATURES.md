# Implemented Features

> Audit based solely on source code, models, routers, tests, and configuration. No plans, README claims, or architecture documents used as evidence for implementation status.

---

## Authentication & Authorization

### User Registration
**Status:** Implemented
**Evidence:**
- `app/auth/router.py:43` — `POST /register` endpoint
- `app/auth/service.py:15` — `register()` method with email uniqueness check, password hashing, role assignment
- `app/auth/schemas.py:10` — `RegisterRequest` schema with `email`, `password`, `full_name`, `role`
- `app/users/models.py:11` — `User` model with `email`, `password_hash`, `role`, `is_active`
- `app/security/password.py:10` — `hash_password()`, `verify_password()`, `validate_password_strength()`
- `app/security/jwt.py:12` — `create_access_token()`, `create_refresh_token()`
- `tests/test_auth.py:45` — `TestAuthService::test_register_success` unit test

### User Login (JWT)
**Status:** Implemented
**Evidence:**
- `app/auth/router.py:67` — `POST /login` endpoint
- `app/auth/service.py:45` — `login()` method with credential verification, token generation
- `app/auth/schemas.py:35` — `LoginRequest`, `TokenResponse`
- `app/security/jwt.py:12` — Token creation and decoding
- `tests/test_auth.py:60` — `TestAuthService::test_login_success` unit test
- `tests/test_auth.py:72` — `TestAuthService::test_login_wrong_password` failure test

### Token Refresh
**Status:** Implemented
**Evidence:**
- `app/auth/router.py:84` — `POST /refresh` endpoint
- `app/auth/service.py:70` — `refresh()` method verifying refresh token hash, issuing new pair
- `app/auth/models.py:10` — `RefreshToken` model with `token_hash`, `expires_at`, `revoked_at`
- `app/auth/repository.py:10` — `RefreshTokenRepository`
- `tests/test_auth.py:18` — `TestJWT::test_create_and_decode_refresh_token`
- `tests/test_auth.py:35` — `TestAuthService::test_hash_token_consistency`

### Token Logout (Revoke)
**Status:** Implemented
**Evidence:**
- `app/auth/router.py:102` — `POST /logout` endpoint
- `app/auth/service.py:95` — `logout()` method revoking all refresh tokens for user

### Forgot Password
**Status:** Implemented (endpoint exists, email delivery absent)
**Evidence:**
- `app/auth/router.py:120` — `POST /forgot-password` endpoint
- `app/auth/service.py:110` — `forgot_password()` method creating reset token
- `app/auth/models.py:35` — `PasswordResetToken` model
- **Email sending NOT implemented** — `app/auth/service.py:120` stores token but has no SMTP/email API call

### Reset Password
**Status:** Implemented
**Evidence:**
- `app/auth/router.py:138` — `POST /reset-password` endpoint
- `app/auth/service.py:130` — `reset_password()` method verifying token, updating password hash

### Password Strength Validation
**Status:** Implemented
**Evidence:**
- `app/security/password.py:35` — `validate_password_strength()` requiring min 8 chars, uppercase, lowercase, digit
- `tests/test_auth.py:30` — `TestPasswordHashing::test_password_strength_validation`

### Role-Based Access Control
**Status:** Implemented (role checks exist, resource-level permissions inconsistent)
**Evidence:**
- `app/auth/dependencies.py:25` — `require_role()` dependency
- `app/security/rbac.py:15` — `RoleChecker` class
- `tests/test_rbac.py:40` — `TestRBAC::test_admin_required` unit test
- `tests/test_rbac.py:121,129,150` — **Skipped** HTTP-level RBAC tests (require live database)

---

## Curriculum Management

### Course CRUD
**Status:** Implemented
**Evidence:**
- `app/curriculum/router.py:54` — `POST /courses`, `GET /courses`, `GET /courses/{id}`, `PUT /courses/{id}`, `DELETE /courses/{id}`
- `app/curriculum/service.py:20` — `CourseService` with full CRUD
- `app/curriculum/models.py:11` — `Course` model
- `app/curriculum/repository.py:10` — `CourseRepository`
- `tests/test_curriculum.py:15` — Course service tests

### Module CRUD
**Status:** Implemented
**Evidence:**
- `app/curriculum/router.py:54` — `POST /courses/{id}/modules`, `GET /courses/{id}/modules`, `PUT /modules/{id}`, `DELETE /modules/{id}`
- `app/curriculum/service.py:80` — Module operations
- `app/curriculum/models.py:35` — `Module` model
- `tests/test_curriculum.py:45` — Module service tests

### Lesson CRUD
**Status:** Implemented
**Evidence:**
- `app/curriculum/router.py:54` — `POST /modules/{id}/lessons`, `GET /modules/{id}/lessons`, `GET /lessons/{id}`, `PUT /lessons/{id}`, `DELETE /lessons/{id}`
- `app/curriculum/service.py:130` — Lesson operations
- `app/curriculum/models.py:55` — `Lesson` model
- `tests/test_curriculum.py:70` — Lesson service tests

### Concept CRUD
**Status:** Implemented
**Evidence:**
- `app/curriculum/router.py:54` — `POST /lessons/{id}/concepts`, `GET /lessons/{id}/concepts`, `GET /concepts/{id}`, `PUT /concepts/{id}`, `DELETE /concepts/{id}`
- `app/curriculum/service.py:180` — Concept operations
- `app/curriculum/models.py:75` — `Concept` model
- `tests/test_curriculum.py:95` — Concept service tests

### Concept Content CRUD
**Status:** Implemented
**Evidence:**
- `app/curriculum/router.py:54` — `POST /concepts/{id}/contents`, `GET /concepts/{id}/contents`, `PUT /concept-contents/{id}`, `DELETE /concept-contents/{id}`
- `app/curriculum/service.py:230` — Content operations
- `app/curriculum/models.py:95` — `ConceptContent` model
- `tests/test_curriculum.py:115` — Content service tests

### Learning Objective CRUD
**Status:** Implemented
**Evidence:**
- `app/curriculum/router.py:54` — `POST /lessons/{id}/objectives`, `GET /lessons/{id}/objectives`, `PUT /objectives/{id}`, `DELETE /objectives/{id}`
- `app/curriculum/service.py:280` — Objective operations
- `app/curriculum/models.py:135` — `LearningObjective` model
- `tests/test_curriculum.py:145` — Objective service tests

### Exercise CRUD
**Status:** Implemented
**Evidence:**
- `app/curriculum/router.py:54` — `POST /concepts/{id}/exercises`, `GET /concepts/{id}/exercises`, `PUT /exercises/{id}`, `DELETE /exercises/{id}`
- `app/curriculum/service.py:330` — Exercise operations
- `app/curriculum/models.py:115` — `Exercise` model
- `tests/test_curriculum.py:130` — Exercise service tests

### Example CRUD
**Status:** Implemented
**Evidence:**
- `app/curriculum/router.py:54` — `POST /concepts/{id}/examples`, `GET /concepts/{id}/examples`, `PUT /examples/{id}`, `DELETE /examples/{id}`
- `app/curriculum/service.py:380` — Example operations
- `app/curriculum/models.py:155` — `Example` model
- `tests/test_curriculum.py:160` — Example service tests

### Course Publish Workflow
**Status:** Implemented
**Evidence:**
- `app/curriculum/router.py:54` — `PUT /courses/{id}/publish`
- `app/curriculum/service.py:410` — Publish logic with validation (must have modules + lessons)

---

## Knowledge Graph

### Knowledge Edge CRUD
**Status:** Implemented
**Evidence:**
- `app/knowledge_graph/router.py:21` — `POST /knowledge-graph/edges`, `DELETE /knowledge-graph/edges/{id}`
- `app/knowledge_graph/service.py:20` — `create_edge()`, `delete_edge()`
- `app/knowledge_graph/models.py:30` — `KnowledgeEdge` model
- `app/knowledge_graph/repository.py:36` — `KnowledgeEdgeRepository`
- `tests/test_knowledge_graph.py:15` — Edge CRUD tests

### Prerequisite Traversal
**Status:** Implemented
**Evidence:**
- `app/knowledge_graph/router.py:21` — `GET /knowledge-graph/concepts/{id}/prerequisites`
- `app/knowledge_graph/service.py:45` — `get_prerequisites()` traversing "requires" relationships
- `tests/test_knowledge_graph.py:45` — Prerequisite traversal test

---

## Enrollment & Scheduling

### Student Course Enrollment
**Status:** Implemented
**Evidence:**
- `app/enrollment/router.py:15` — `POST /enrollments`
- `app/enrollment/service.py:20` — `enroll()` with duplicate and published-course checks
- `app/enrollment/models.py:11` — `StudentCourseEnrollment` model
- `tests/test_enrollment.py:15` — Enrollment service test

### Enrollment Listing
**Status:** Implemented
**Evidence:**
- `app/enrollment/router.py:15` — `GET /enrollments`, `GET /enrollments/{id}`
- `app/enrollment/service.py:55` — `list_enrollments()`, `get_enrollment()`

---

## Student Progress

### Lesson Progress Tracking
**Status:** Implemented
**Evidence:**
- `app/progress/router.py:15` — `GET /lessons/{id}/progress`
- `app/progress/service.py:20` — `get_lesson_progress()`, `update_lesson_progress()`
- `app/teaching/models.py:35` — `LessonProgress` model
- `app/progress/repository.py:10` — `LessonProgressRepository`
- `tests/test_progress.py:15` — Progress service tests

### Attempt Recording
**Status:** Implemented
**Evidence:**
- `app/teaching_sessions/service.py:90` — `record_attempt()` linked to session
- `app/teaching/models.py:25` — `Attempt` model
- `tests/test_teaching_sessions.py:45` — Attempt history test

### Attempt History
**Status:** Implemented
**Evidence:**
- `app/teaching_sessions/router.py:21` — `GET /sessions/{id}/history`
- `tests/test_teaching_sessions.py:55` — Session history test

### Concept Mastery Scoring
**Status:** Implemented
**Evidence:**
- `app/mastery/service.py:20` — `get_mastery()`, `update_mastery()`, `get_or_create_mastery()`
- `app/mastery/models.py:11` — `MasteryRecord` model
- `app/mastery/repository.py:10` — `MasteryRecordRepository`
- `app/mastery/router.py:15` — `GET /mastery`
- `tests/test_mastery.py:15` — Mastery service tests

---

## Teaching Sessions

### Start Session
**Status:** Implemented
**Evidence:**
- `app/teaching_sessions/router.py:21` — `POST /sessions` with `resume_last` support
- `app/teaching_sessions/service.py:25` — `create_session()` with enrollment validation
- `app/teaching/models.py:11` — `TeachingSession` model with state machine
- `tests/test_teaching_sessions.py:15` — Session creation test

### Resume Session
**Status:** Implemented
**Evidence:**
- `app/teaching_sessions/service.py:50` — Auto-resume logic on duplicate create
- `tests/test_teaching_sessions.py:25` — Resume test

### Pause/End Session
**Status:** Implemented
**Evidence:**
- `app/teaching_sessions/router.py:21` — `PATCH /sessions/{id}` (state: paused/completed)
- `app/teaching_sessions/service.py:65` — `update_session_state()` with transition validation
- `tests/test_teaching_sessions.py:35` — Update session test

---

## Parent Dashboard

### Parent-Student Linking
**Status:** Implemented
**Evidence:**
- `app/users/models.py:43` — `ParentStudentLink` model
- `app/parent_dashboard/service.py:20` — Parent dashboard service with linked-student queries

### Parent Dashboard (12 read-only views)
**Status:** Implemented
**Evidence:**
- `app/parent_dashboard/router.py:20` — 12 GET endpoints:
  - `GET /parent/students`
  - `GET /parent/students/{id}/progress`
  - `GET /parent/students/{id}/mastery`
  - `GET /parent/students/{id}/misconceptions`
  - `GET /parent/students/{id}/sessions`
  - `GET /parent/students/{id}/reports`
  - `GET /parent/students/{id}/reports/{rid}`
  - `POST /parent/students/{id}/reports/generate`
  - `PATCH /parent/students/{id}/reports/{rid}/read`
  - `GET /parent/dashboard`
  - (and others)
- `app/parent_dashboard/service.py` — Full service implementation
- `tests/test_parent_dashboard.py:15` — 12 parent dashboard service tests

### AI-Generated Reports
**Status:** Implemented (AI-generated narrative via Gemini, mock in tests)
**Evidence:**
- `app/reports/service.py:25` — `generate_report()` with AI narrative generation integrated
- `app/reports/models.py:11` — `Report` model
- `app/reports/router.py:15` — Report CRUD endpoints
- `tests/test_reports.py:15` — Report service tests (mock AI)
- `tests/integration/test_report_generation.py` — Integration test (mock AI)

---

## Content Ingestion

### File Upload (TXT, PDF, DOCX)
**Status:** Implemented
**Evidence:**
- `app/content_ingestion/router.py:20` — `POST /content/upload`
- `app/content_ingestion/service.py:25` — `ContentIngestionService` with file parsing
- `app/content_ingestion/parsers/` — TXT, PDF, DOCX parsers
- `tests/test_content_ingestion.py:40` — Parser tests

### AI Text Extraction
**Status:** Implemented (mock Gemini in tests)
**Evidence:**
- `app/content_ingestion/service.py:80` — `extract_content()` calling Gemini
- `tests/test_content_ingestion.py:120` — Extraction tests (mock AI)

### AI Curriculum Generation
**Status:** Implemented (mock Gemini in tests)
**Evidence:**
- `app/content_ingestion/service.py:130` — `generate_curriculum()` creating course/module/lesson/concept from extracted content
- `tests/test_content_ingestion.py:180` — Generator tests (mock AI)

### Draft Lifecycle (Draft → Approve → Publish)
**Status:** Implemented
**Evidence:**
- `app/content_ingestion/router.py:20` — `PUT /content/approve`, `PUT /content/reject`, `GET /content/submissions`
- `app/content_ingestion/models.py:19` — `DraftStatus` enum with `draft`, `approved`, `rejected`, `published`

---

## AI Evaluation Harness

### Evaluation Datasets, Metrics, Reports
**Status:** Implemented
**Evidence:**
- `app/ai/evaluation/service.py:20` — `EvaluationService` with pre-built scenarios
- `app/ai/evaluation/router.py:15` — 6 evaluation endpoints
- `app/ai/evaluation/models/metrics.py:15` — Metric computation
- `app/ai/evaluation/models/reports.py:20` — Report generation
- `tests/test_evaluation.py:15` — 30 evaluation tests

---

## Infrastructure

### PostgreSQL with asyncpg
**Status:** Implemented
**Evidence:**
- `app/infrastructure/database.py:15` — Async engine using `asyncpg`
- `docker-compose.yml:1-15` — PostgreSQL 16 Alpine service

### SQLAlchemy ORM
**Status:** Implemented
**Evidence:**
- `app/infrastructure/database.py:30` — `async_sessionmaker`, `Base`, `get_db()`
- 30 SQLAlchemy models across 10+ model files

### Alembic Migrations
**Status:** Implemented
**Evidence:**
- `alembic.ini` — Migration configuration
- `alembic/versions/` — 4 version files
- `alembic/env.py` — async migration environment

### Structured Logging
**Status:** Implemented
**Evidence:**
- `app/infrastructure/logging.py:20` — JSON-formatted logging with `timestamp`, `level`, `module`, `request_id`

### Configuration Management
**Status:** Implemented (default secrets in source)
**Evidence:**
- `app/config.py:10-85` — pydantic-settings with env file support
- `.env.example` — Template for required environment variables

### Seed Data Script
**Status:** Implemented
**Evidence:**
- `scripts/seed_data.py` — Creates admin user and demo course

### Shared Base Model (UUIDMixin)
**Status:** Implemented
**Evidence:**
- `app/common/base.py:10` — `UUIDMixin` with UUID PK, `created_at`, `updated_at`
- `app/common/types.py` — 13 enum types
- `app/common/exceptions.py` — Exception hierarchy
- `app/common/constants.py` — Shared constants
