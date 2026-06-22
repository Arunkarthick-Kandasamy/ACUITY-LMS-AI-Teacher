# Codebase Metrics

> Exact numbers extracted from source code. No estimates.

---

## File Counts

| Category | Count | Source |
|----------|:-----:|--------|
| Python files in `Backend/app/` | **158** | `Get-ChildItem -Recurse -Filter "*.py"` on `Backend/app/` |
| Python files in `Backend/tests/` | **26** | `Get-ChildItem -Recurse -Filter "*.py"` on `Backend/tests/` |
| Alembic migration files | **5** | `alembic/versions/*.py` (4 version files + `env.py`) |
| Docker files | **2** | `Dockerfile`, `docker-compose.yml` |
| Config files | **6** | `.env`, `.env.example`, `alembic.ini`, `Makefile`, `pyproject.toml` |

---

## Lines of Code

| Area | Lines | Source |
|------|:-----:|--------|
| All Python (app + tests + alembic) | **16,323** | `Get-ChildItem -Recurse -Filter "*.py" \| Get-Content \| Measure-Object -Line` |
| Backend/app only | **9,544** | Same command scoped to `Backend/app` |

---

## Architecture Components

| Component | Count | Method |
|-----------|:-----:|--------|
| **SQLAlchemy models** | **30** | Grep `class \w+\(UUIDMixin\|class \w+\(Base\)` in `app/**/models.py` |
| **Enum types** | **14** | Counted from `app/common/types.py` and `app/content_ingestion/models.py` |
| **Routers** | **14** | Counted from `app/main.py:127-140` `include_router` calls |
| **API endpoints** | **91** | Counted from router files (see API_INVENTORY.md) |
| **Service classes** | **13** | Grep `class \w+Service` in `app/**/service.py` (excludes nested classes) |
| **Repository classes** | **15** | Grep `class \w+Repository` in `app/**/repository.py` |

---

## Services (13)

| Service | File |
|---------|------|
| `AuthService` | `app/auth/service.py:12` |
| `CourseService` | `app/curriculum/service.py:14` |
| `EnrollmentService` | `app/enrollment/service.py:12` |
| `ProgressService` | `app/progress/service.py:14` |
| `MasteryService` | `app/mastery/service.py:12` |
| `PacingService` | `app/pacing/service.py:14` |
| `TeachingSessionService` | `app/teaching_sessions/service.py:15` |
| `KnowledgeGraphService` | `app/knowledge_graph/service.py:12` |
| `DiagnosisService` | `app/diagnosis/service.py:12` |
| `ReportService` | `app/reports/service.py:14` |
| `ParentDashboardService` | `app/parent_dashboard/service.py:14` |
| `ContentIngestionService` | `app/content_ingestion/service.py:12` |
| `EvaluationService` | `app/ai/evaluation/service.py:12` |

---

## Repositories (15)

| Repository | File |
|------------|------|
| `UserRepository` | `app/users/repository.py:10` |
| `StudentProfileRepository` | `app/users/repository.py:48` |
| `RefreshTokenRepository` | `app/auth/repository.py:10` |
| `CourseRepository` | `app/curriculum/repository.py:10` |
| `ModuleRepository` | `app/curriculum/repository.py:53` |
| `LessonRepository` | `app/curriculum/repository.py:96` |
| `ConceptRepository` | `app/curriculum/repository.py:139` |
| `KnowledgeNodeRepository` | `app/knowledge_graph/repository.py:10` |
| `KnowledgeEdgeRepository` | `app/knowledge_graph/repository.py:36` |
| `EnrollmentRepository` | `app/enrollment/repository.py:10` |
| `LessonProgressRepository` | `app/progress/repository.py:10` |
| `MasteryRecordRepository` | `app/mastery/repository.py:10` |
| `PacingRecordRepository` | `app/pacing/repository.py:10` |
| `TeachingSessionRepository` | `app/teaching_sessions/repository.py:10` |
| `AttemptRepository` | `app/teaching_sessions/repository.py:50` |

---

## Router Index (14 routers, 91 endpoints)

| Router Module | Endpoints | File |
|---------------|:---------:|------|
| `app/api/routes/health.py` | 1 | `app/main.py:127` |
| `app/auth/router.py` | 6 | `app/main.py:128` |
| `app/curriculum/router.py` | 36 | `app/main.py:129` |
| `app/knowledge_graph/router.py` | 3 | `app/main.py:130` |
| `app/enrollment/router.py` | 3 | `app/main.py:131` |
| `app/progress/router.py` | 3 | `app/main.py:132` |
| `app/mastery/router.py` | 1 | `app/main.py:133` |
| `app/pacing/router.py` | 1 | `app/main.py:134` |
| `app/teaching_sessions/router.py` | 4 | `app/main.py:135` |
| `app/parent_dashboard/router.py` | 12 | `app/main.py:136` |
| `app/ai/router.py` | 2 | `app/main.py:137` |
| `app/ai/evaluation/router.py` | 6 | `app/main.py:139` |
| `app/reports/router.py` | 6 | `app/main.py:138` |
| `app/content_ingestion/router.py` | 9 | `app/main.py:140` |

---

## Language Breakdown

| Language | Files | Lines |
|----------|:-----:|:-----:|
| Python (all) | 189 | 16,323 |
| YAML/TOML/INI | 5 | ~200 |
| Docker | 2 | ~80 |
| Shell/Makefile | 1 | ~60 |

---

## Test Metrics

| Metric | Value | Source |
|--------|:-----:|--------|
| Test files | 22 | `Backend/tests/` |
| Total tests collected | 331 | `pytest --collect-only` |
| Active tests | 323 | 331 - 8 skipped |
| Skipped tests | 8 | See TEST_INVENTORY.md |
| Test files with async tests | ~17 of 22 | Async fixtures in `conftest.py` |

---

## Dependency Count

| Category | Count | Source |
|----------|:-----:|--------|
| Core dependencies | ~30 | `pyproject.toml:12-34` `[project]` dependencies |
| Optional dependencies | 1 | `pyproject.toml:31-33` — `qdrant-client` under `[project.optional-dependencies]` |
| Dev dependencies | ~10 | `pyproject.toml:35-44` |

---

## Code Organization

```
Backend/
  app/                  # 158 .py files, 9544 LOC
    __init__.py
    main.py             # FastAPI app entry
    config.py           # pydantic-settings configuration
    api/routes/         # health endpoint
    common/             # base types, enums, exceptions, constants
    users/              # User, StudentProfile models + repo
    auth/               # register, login, refresh, logout, forgot/reset password
    security/           # JWT, password hashing, RBAC
    curriculum/         # Course→Module→Lesson→Concept hierarchy (36 endpoints)
    knowledge_graph/    # Prerequisite edges, 3 endpoints
    enrollment/         # Course enrollment (3 endpoints)
    progress/           # Lesson progress (3 endpoints)
    mastery/            # Concept mastery scoring (1 endpoint)
    pacing/             # Pacing status (1 endpoint)
    teaching_sessions/  # Session lifecycle (4 endpoints)
    teaching/           # Attempt model + progress model
    parent_dashboard/   # 12 read-only parent endpoints
    reports/            # AI-generated reports
    diagnosis/          # Misconception tracking
    memory/             # Student memory model
    audit/              # AuditLog table (empty)
    ai/                 # LangGraph teacher graph, Gemini, memory, evaluation
    content_ingestion/  # File upload, parse, AI extraction
    monitoring/         # In-memory metrics
    infrastructure/     # DB, logging
  tests/                # 22 test files, 26 .py files
    conftest.py         # async fixtures
    test_*.py           # unit + integration tests
  alembic/              # 4 migration versions
  scripts/              # seed_data.py
```
