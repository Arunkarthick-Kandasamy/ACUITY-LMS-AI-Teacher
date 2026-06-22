# Codebase Statistics

## Project Metrics

| Metric | Value |
|--------|:-----:|
| **Total Python Source Files** | ~189 (including `__pycache__`) |
| **Meaningful Python Modules** | ~80 (excluding caches, egg-info) |
| **Test Files** | 18 unit + 5 integration = **23** |
| **Config/Infrastructure Files** | ~15 (Docker, Makefile, configs, migrations) |
| **Markdown Documentation Files** | 5 (Architecture, API, DB, Impl Plan, + audit) |
| **Total Lines of Code (approx)** | ~15,000-18,000 |

---

## File Count by Module

| Module | Path | `.py` Files | Key Contents |
|--------|------|:----------:|--------------|
| Main App | `app/` | 1 | FastAPI factory, main.py |
| Config | `app/config.py` | 1 | Pydantic Settings |
| Infrastructure | `app/infrastructure/` | 2 | Database, logging |
| Common | `app/common/` | 7 | Base model, types, exceptions, repository, response, constants, context |
| API | `app/api/` | 1 | Health endpoint |
| Auth | `app/auth/` | 5 | Router, service, schemas, repository, dependencies |
| Security | `app/security/` | 3 | JWT, password, config |
| Users | `app/users/` | 4 | Models, repository, schemas, service |
| Curriculum | `app/curriculum/` | 5 | Models, repository, router, schemas, service |
| Enrollment | `app/enrollment/` | 5 | Models, repository, router, schemas, service |
| Progress | `app/progress/` | 5 | Models, repository, router, schemas, service |
| Mastery | `app/mastery/` | 5 | Models, repository, router, schemas, service |
| Pacing | `app/pacing/` | 5 | Models, repository, router, schemas, service |
| Knowledge Graph | `app/knowledge_graph/` | 5 | Models, repository, router, schemas, service |
| Teaching Sessions | `app/teaching_sessions/` | 4 | Repository, router, schemas, service |
| Teaching | `app/teaching/` | 1 | Models (Session, Progress, Attempt) |
| AI | `app/ai/` | 25+ | Router, state, prompts, 7 nodes, graphs, diagnosis, memory, guardrails, evaluation, services, prompt registry |
| Reports | `app/reports/` | 5 | Models, prompts, router, schemas, service |
| Parent Dashboard | `app/parent_dashboard/` | 4 | Repository, router, schemas, service |
| Content Ingestion | `app/content_ingestion/` | 12 | Models, parsers (3), prompts, repository, router, schemas, service, AI (2) |
| Monitoring | `app/monitoring/` | 3 | Metrics, middleware, models |
| Audit | `app/audit/` | 1 | AuditLog model |
| Evaluation | `app/evaluation/` | 1 | Evaluation models |
| Migrations | `alembic/versions/` | 4 | Migration scripts |

---

## Code Counts

### Models (SQLAlchemy ORM)
| Module | Models |
|--------|:------:|
| `users/models.py` | 3 (User, StudentProfile, ParentStudentLink) |
| `curriculum/models.py` | 8 (Course, Module, Lesson, Concept, ConceptContent, LearningObjective, Example, Exercise) |
| `teaching/models.py` | 3 (TeachingSession, LessonProgress, Attempt) |
| `enrollment/models.py` | 2 (StudentCourseEnrollment, CourseSchedule) |
| `mastery/models.py` | 1 (MasteryRecord) |
| `knowledge_graph/models.py` | 2 (KnowledgeNode, KnowledgeEdge) |
| `diagnosis/models.py` | 1 (Misconception) |
| `memory/models.py` | 2 (StudentMemory, MemoryEntry) |
| `reports/models.py` | 1 (Report) |
| `auth/models.py` | 2 (RefreshToken, PasswordResetToken) |
| `audit/models.py` | 1 (AuditLog) |
| `evaluation/models.py` | 2 (GraphTrace, TeacherMetricsSnapshot) |
| `content_ingestion/models.py` | 2 (ContentUpload, CurriculumDraft) |
| **Total** | **30** |

### Services
| Module | File | Services |
|--------|------|:--------:|
| Auth | `auth/service.py` | AuthService |
| Users | `users/service.py` | UserService |
| Curriculum | `curriculum/service.py` | CourseService |
| Enrollment | `enrollment/service.py` | EnrollmentService |
| Progress | `progress/service.py` | ProgressService |
| Mastery | `mastery/service.py` | MasteryService |
| Pacing | `pacing/service.py` | PacingService |
| Knowledge Graph | `knowledge_graph/service.py` | KnowledgeGraphService |
| Teaching Sessions | `teaching_sessions/service.py` | SessionService |
| Parent Dashboard | `parent_dashboard/service.py` | ParentDashboardService |
| Reports | `reports/service.py` | ReportService |
| Content Ingestion | `content_ingestion/service.py` | ContentIngestionService |
| AI Memory | `ai/memory/service.py` | MemoryService |
| AI Memory Extraction | `ai/memory/extraction.py` | MemoryExtractor |
| AI Memory Retrieval | `ai/memory/retrieval.py` | MemoryRetriever |
| AI Diagnosis | `ai/diagnosis/service.py` | DiagnosisService |
| AI Guardrails | `ai/guardrails/service.py` | GuardrailService |
| AI Gemini | `ai/services/gemini.py` | GeminiService |
| AI Evaluation | `ai/evaluation/metrics.py` | (compute_metrics functions) |
| AI Evaluation Harness | `ai/evaluation/harness.py` | (run_evaluation functions) |
| Content Extraction | `content_ingestion/ai/extractor.py` | ContentExtractor |
| Curriculum Generation | `content_ingestion/ai/curriculum_generator.py` | CurriculumGenerator |
| Monitoring | `monitoring/metrics.py` | MetricsCollector |
| Monitoring | `monitoring/middleware.py` | MonitoringMiddleware |
| **Total Services** | | **~23** |

### Repositories
| Module | File | Repositories |
|--------|------|:------------:|
| Auth | `auth/repository.py` | RefreshTokenRepository, PasswordResetTokenRepository |
| Users | `users/repository.py` | UserRepository |
| Mastery | `mastery/repository.py` | MasteryRepository |
| Knowledge Graph | `knowledge_graph/repository.py` | KnowledgeNodeRepository, KnowledgeEdgeRepository |
| Progress | `progress/repository.py` | ProgressRepository |
| Enrollment | `enrollment/repository.py` | EnrollmentRepository |
| Pacing | `pacing/repository.py` | PacingRepository |
| Teaching Sessions | `teaching_sessions/repository.py` | SessionRepository |
| Parent Dashboard | `parent_dashboard/repository.py` | ParentStudentLinkRepository, MisconceptionRepository, ParentTeachingSessionRepository |
| Content Ingestion | `content_ingestion/repository.py` | ContentUploadRepository, CurriculumDraftRepository |
| **Total Repositories** | | **~15** |

### Routers
| Module | File | Endpoints |
|--------|------|:---------:|
| Health | `api/routes/health.py` | 1 |
| Auth | `auth/router.py` | 6 |
| Curriculum | `curriculum/router.py` | 36 |
| Enrollment | `enrollment/router.py` | 3 |
| Progress | `progress/router.py` | 5 |
| Mastery | `mastery/router.py` | 3 |
| Pacing | `pacing/router.py` | 3 |
| Knowledge Graph | `knowledge_graph/router.py` | 3 |
| Teaching Sessions | `teaching_sessions/router.py` | 5 |
| AI Teacher | `ai/router.py` | 1 |
| AI Evaluation | `ai/evaluation/router.py` | 3 |
| Parent Dashboard | `parent_dashboard/router.py` | 12 |
| Content Ingestion | `content_ingestion/router.py` | 6 |
| Reports | `reports/router.py` | 3 |
| **Total Routers** | **14** | **90 endpoints** |

---

## Dependency Count

### Core Dependencies (from pyproject.toml)
| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | >=0.115.0 | Web framework |
| uvicorn | >=0.32.0 | ASGI server |
| sqlalchemy | >=2.0.36 | ORM |
| asyncpg | >=0.30.0 | PostgreSQL driver |
| pydantic | >=2.10.0 | Data validation |
| pydantic-settings | >=2.6.0 | Configuration |
| python-json-logger | >=2.0.0 | Structured logging |
| python-multipart | >=0.0.18 | File upload support |
| alembic | >=1.14.0 | Database migrations |
| psycopg2-binary | >=2.9.0 | Sync PostgreSQL driver (for Alembic) |
| python-jose | >=3.3.0 | JWT tokens |
| passlib | >=1.7.4 | Password hashing |
| bcrypt | >=4.1.0 | Bcrypt algorithm |
| langgraph | >=0.4.0 | AI state machine |
| google-genai | >=1.14.0 | Gemini API |
| **Core count** | **15** | |

### Dev Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| pytest | >=8.3.0 | Testing framework |
| pytest-asyncio | >=0.24.0 | Async test support |
| httpx | >=0.28.0 | HTTP client for testing |
| ruff | >=0.8.0 | Python linter |
| **Dev count** | **4** | |

### Optional Dependencies
| Package | Purpose |
|---------|---------|
| qdrant-client | Vector database for semantic memory retrieval |
| **Optional count** | **1** | |

**Total Dependencies: 20**

---

## Test Count Summary

| Test File | Test Functions | Type |
|-----------|:-------------:|:----:|
| `test_auth.py` | 19 | Unit + Integration (5 skipped) |
| `test_content_ingestion.py` | 25 | Unit |
| `test_curriculum.py` | 21 | Unit |
| `test_diagnosis.py` | 16 | Unit + Integration |
| `test_enrollment.py` | 9 | Unit |
| `test_evaluation.py` | 30 | Unit + Integration |
| `test_health.py` | 3 | Integration |
| `test_knowledge_graph.py` | 9 | Unit |
| `test_mastery.py` | 7 | Unit |
| `test_memory.py` | 30 | Unit + Integration |
| `test_pacing.py` | 8 | Unit |
| `test_parent_dashboard.py` | 39 | Unit |
| `test_progress.py` | 8 | Unit |
| `test_rbac.py` | 11 | Unit + Integration (3 skipped) |
| `test_reports.py` | 30 | Unit |
| `test_teacher_graph.py` | 21 | Unit + Integration |
| `test_teaching_sessions.py` | 18 | Unit |
| `tests/integration/test_content_ingestion_flow.py` | 1 | Integration |
| `tests/integration/test_diagnosis_flow.py` | 3 | Integration |
| `tests/integration/test_memory_extraction.py` | 6 | Integration |
| `tests/integration/test_parent_report.py` | 3 | Integration |
| `tests/integration/test_teaching_flow.py` | 6 | Integration |
| **TOTAL** | **331** (323 active) | |

---

## Code Quality Metrics

### Lint Status
| Check | Result |
|-------|--------|
| Ruff errors (E category) | 14 remaining (E501 line length in test files) |
| Ruff errors (B category) | 13 (B008 — FastAPI Depends pattern, pre-existing) |
| Ruff warnings (F category) | 0 (auto-fixed) |
| Ruff warnings (I category) | 0 (auto-fixed) |

### Test Health
| Metric | Value |
|--------|:-----:|
| Tests passing | 323 / 331 (97.6%) |
| Tests skipped | 8 (2.4%) |
| Async tests | 246 (74.3%) |
| Sync tests | 79 (23.9%) |
| Test files | 23 |
| conftest files | 2 |

---

## Project Size Metrics

| Dimension | Value |
|-----------|:-----:|
| Python source files | ~80 meaningful modules |
| Total lines of Python | ~15,000-18,000 (estimated) |
| Database tables | 30 |
| API endpoints | 90 |
| Test functions | 323 active |
| Services | ~23 |
| Repositories | ~15 |
| Routers | 14 |
| SQLAlchemy models | 30 |
| Migration files | 4 |
| Python enum types | 14 |
| External dependencies | 20 |
| Docker images | 2 (builder + runtime) |
| Docker Compose services | 1 (PostgreSQL) |
| Makefile targets | 10 |
| Top-level markdown docs | 5 (new: +12 audit docs) |
