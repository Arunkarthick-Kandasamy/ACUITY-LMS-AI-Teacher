# Test Inventory

> Counts extracted from `pytest --collect-only` and manual verification of test files.

---

## Total Test Count

| Metric | Value |
|--------|:-----:|
| **Tests collected** | **331** |
| **Tests skipped** | **8** |
| **Active tests** | **323** |
| **Test files** | **22** |
| **Async tests** | ~246 (74.3%) |
| **Sync tests** | ~79 (23.9%) |

---

## Skipped Tests

| File | Line | Test | Reason |
|------|:----:|------|--------|
| `tests/test_auth.py` | 253 | `test_register_validation_email` | requires live database |
| `tests/test_auth.py` | 270 | `test_register_validation_weak_password` | requires live database |
| `tests/test_auth.py` | 286 | `test_login_validation_empty_body` | requires live database |
| `tests/test_auth.py` | 297 | `test_forgot_password_returns_same_message` | requires live database |
| `tests/test_auth.py` | 311 | `test_auth_routes_require_body` | requires live database |
| `tests/test_rbac.py` | 121 | `test_access_without_token` | requires live database |
| `tests/test_rbac.py` | 129 | `test_access_with_expired_token` | requires live database |
| `tests/test_rbac.py` | 150 | `test_malformed_token` | requires live database |

**All 8 skipped tests require a live database for HTTP integration testing.**

---

## Tests Per File

### Unit Tests (17 files, 306 tests)

| File | Tests | Test Classes | Coverage |
|------|:-----:|:------------:|----------|
| `tests/test_auth.py` | 19 | TestPasswordHashing, TestJWT, TestAuthService, TestAuthAPI | Password, JWT, Auth service, Auth API (5 skipped) |
| `tests/test_content_ingestion.py` | 32 | TestSchemas, TestParsers, TestContentExtractor, TestCurriculumGenerator, TestContentIngestionService | Parsers, extractor, generator, service |
| `tests/test_curriculum.py` | 21 | TestCourseServiceCourse, TestCourseServiceModule, TestCourseServiceLesson, TestCourseServiceConcept, TestCourseServiceContent, TestCourseServiceExample, TestCourseServiceExercise, TestCourseServiceObjective | Full curriculum CRUD |
| `tests/test_diagnosis.py` | 16 | TestDiagnosisService, TestDiagnoseNode, TestDecisionRouter, TestGraphIntegration | Diagnosis service, graph routing |
| `tests/test_enrollment.py` | 9 | TestEnrollmentService | Enroll, list, get |
| `tests/test_evaluation.py` | 30 | TestDatasets, TestMetrics, TestReports, TestHarness, TestRouter | Datasets, metrics computation, reports, harness, routes |
| `tests/test_health.py` | 3 | TestHealthEndpoint | Health check |
| `tests/test_knowledge_graph.py` | 9 | TestKnowledgeGraphEdge | Edge CRUD, prerequisites |
| `tests/test_mastery.py` | 10 | TestMasteryService | Get, update, get or create |
| `tests/test_memory.py` | 3 | TestMemoryExtraction | Memory extraction node |
| `tests/test_pacing.py` | 7 | TestPacingService | Get pacing status, creation |
| `tests/test_parent_dashboard.py` | 12 | TestParentDashboardService | 12 parent dashboard methods |
| `tests/test_progress.py` | 8 | TestProgressService | Get progress, update progress |
| `tests/test_reports.py` | 13 | TestReportService | Generate report, get reports, list reports, mark read |
| `tests/test_rbac.py` | 7 | TestRBAC | Role checks, permission logic (3 skipped) |
| `tests/test_teaching_sessions.py` | 5 | TestTeachingSessionService | Create, get active, get by id, update, history |
| `tests/test_teacher_graph.py` | 21 | TestTeacherGraph | Graph initialization, state transitions, teach, ask, evaluate, diagnose, provide example, complete |

### Integration Tests (5 files, 19 tests)

| File | Tests | Scenario |
|------|:-----:|----------|
| `tests/integration/test_memory_extraction.py` | 3 | Memory extraction from conversation |
| `tests/integration/test_report_generation.py` | 3 | Full report generation pipeline |
| `tests/integration/test_content_ingestion_pipeline.py` | 4 | File upload → parse → extract → generate |
| `tests/integration/test_diagnosis_flow.py` | 4 | Diagnosis end-to-end |
| `tests/integration/test_teaching_flow.py` | 5 | Full teaching loop (all mock AI) |

### Missing Test Coverage

| File/Module | Test Gap | Evidence |
|-------------|----------|----------|
| `app/ai/guardrails/` (5 files) | Zero tests | No test file exists for guardrails |
| `app/ai/router.py` | No HTTP test for `/teacher/teach` | `tests/` contains no `test_ai_router.py` |
| `app/auth/router.py` (HTTP layer) | 5 tests skipped | Require live database; no test DB fixture |
| `app/teaching/service.py` (Attempt model) | No dedicated attempt test | Attempt tested only through session tests |
| `app/audit/models.py` | Zero tests | No audit-related test |
