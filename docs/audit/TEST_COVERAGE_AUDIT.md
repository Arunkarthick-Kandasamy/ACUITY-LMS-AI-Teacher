# Test Coverage Audit

## Overall Statistics

| Metric | Count |
|--------|:-----:|
| **Total Tests Collected** | **331** |
| **Active (passing) Tests** | **323** (97.6%) |
| **Skipped Tests** | **8** (2.4%) |
| **Async Tests** | 246 (74.3%) |
| **Sync Tests** | 79 (23.9%) |
| **Unit Tests** | ~304 |
| **Integration Tests** | ~27 |
| **E2E Tests** | **0** |

---

## Tests Per Module

| Module | Unit Tests | Integration Tests | Total | Coverage Assessment |
|--------|:----------:|:-----------------:|:-----:|:------------------:|
| Auth & RBAC | 22 | 0 (8 skipped) | 30 | **Good service, poor API** |
| AI Teacher Graph | 21 | 10 | 31 | **Good** |
| AI Diagnosis | 12 | 4 | 16 | **Good** |
| AI Memory | 27 | 9 | 36 | **Good** |
| AI Evaluation | 27 | 3 | 30 | **Good** |
| AI Guardrails | 0 | 0 | **0** | ❌ **No tests** |
| Content Ingestion | 25 | 1 | 26 | **Good** |
| Curriculum CRUD | 21 | 0 | 21 | **Good** |
| Enrollment | 9 | 0 | 9 | **Good** |
| Pacing | 8 | 0 | 8 | **Good** |
| Progress | 8 | 0 | 8 | **Good** |
| Mastery | 7 | 0 | 7 | **Good** |
| Knowledge Graph | 9 | 0 | 9 | **Good** |
| Parent Dashboard | 37 | 0 | 39 | **Good** |
| Reports | 27 | 3 | 33 | **Good** |
| Teaching Sessions | 18 | 0 | 18 | **Good** |
| Health | 0 | 3 | 3 | **Good** |
| **Users Service** | **0** | **0** | **0** | ❌ **No tests** |
| **Monitoring** | **0** | **0** | **0** | ❌ **No tests** |
| **Audit** | **0** | **0** | **0** | ❌ **No tests** |

---

## Untested Areas

### Modules With Zero Test Coverage

#### 1. `app/users/service.py` — UserService
- **Methods:** CRUD operations for User model
- **Risk:** User creation, updates, and profile management have no test coverage
- **Mitigation:** Currently low risk since auth tests mock users, but any changes to UserService could break auth flows silently

#### 2. `app/monitoring/` — MonitoringService + MetricsCollector
- **Methods:** `record_ai_request`, `record_graph_execution`, `record_endpoint`, `get_all_metrics`, etc.
- **Risk:** Metrics system is purely in-memory; untested means metrics could silently break
- **Mitigation:** Low business impact since no production monitoring depends on it

#### 3. `app/ai/guardrails/` — GuardrailService
- **Components:** EmptyResponseDetector, JsonValidator, HallucinationPreventer, FallbackHandler
- **Risk:** Guardrails are safety-critical for AI output quality; untested means bad AI responses could reach users
- **Mitigation:** Guardrails are only used in evaluation harness, not in production teaching flow yet

#### 4. `app/audit/` — AuditLog model
- **Methods:** No service — model only
- **Risk:** Low — audit logging is not yet implemented in any service

### Missing Endpoint Tests

| Endpoint | Method | Risk |
|----------|:------:|:----:|
| `/auth/refresh` | POST | Medium — token refresh is critical auth flow |
| `/auth/logout` | POST | Low — token invalidation |
| `/auth/reset-password` | POST | Medium — password reset flow |
| `/teacher/teach` | POST | High — **the** core AI endpoint has no direct test |
| `/lessons/{id}` | GET | Low — covered by service test |
| `/concepts/{id}` | GET | Low — covered by service test |
| `/concepts/{id}/contents` | GET | Low |
| `/modules/{id}/lessons` | GET | Low |
| `/lessons/{id}/concepts` | GET | Low |
| `/lessons/{id}/objectives` | GET | Low |
| `/concepts/{id}/exercises` | GET | Low |
| `/concepts/{id}/examples` | GET | Low |

### Skipped Tests (8)

All skipped with reason `"requires live database"`:

| Test Class | Tests | File |
|------------|-------|------|
| `TestAuthAPI` | 5 | `test_auth.py` |
| `TestAuthRBACIntegration` | 3 | `test_rbac.py` |

These tests require a real PostgreSQL connection and test actual HTTP request/response with the ASGI transport. They validate:
- Email format validation
- Password strength validation
- Empty request body handling
- Forgot-password security (same message for existing/non-existing email)
- Missing/invalid/expired JWT handling

---

## Integration Test Coverage

| Integration Test | Module | What It Tests | Mocks |
|-----------------|--------|---------------|-------|
| `test_teaching_flow.py` (6) | AI | Individual graph nodes | Gemini |
| `test_diagnosis_flow.py` (3) | AI | Diagnose node routing | Gemini, DiagnosisService |
| `test_memory_extraction.py` (6) | AI | MemoryExtractor logic | Pure logic (no mocks needed) |
| `test_content_ingestion_flow.py` (1) | Content Ingestion | Full upload→generate→approve→publish | File, extractor, session |
| `test_parent_report.py` (3) | Reports | Report generation flow | Gemini, session |
| `TestGraphIntegration` in `test_diagnosis.py` (3) | AI | Graph with diagnose routing | Graph nodes |
| `TestGraphIntegration` in `test_teacher_graph.py` (4) | AI | Full graph teach→evaluate→diagnose | Graph nodes |
| `TestGraphMemoryIntegration` in `test_memory.py` (3) | AI | Memory retrieval before teach | Graph nodes |
| `TestHarness` in `test_evaluation.py` (3) | Evaluation | Evaluation harness with tracing | Graph nodes |

### Integration Test Quality Rating

- **Strong:** Teaching flow, memory extraction, parent report, evaluation harness
- **Adequate:** Content ingestion, graph integration tests
- **Weak:** No cross-module integration tests (e.g., enrollment→progress→mastery pipeline)

---

## Test Quality Assessment

### Strengths
1. **Consistent pattern** — All tests use MagicMock + AsyncMock + patch uniformly
2. **Service-layer coverage** — All services have thorough unit tests for success/failure paths
3. **Schema validation** — All Pydantic models have constructor/validation tests
4. **Graph integration** — LangGraph flows tested end-to-end with mocked nodes
5. **Content ingestion** — Full pipeline tested from upload through publish
6. **Memory extraction** — 11 distinct scenarios tested

### Weaknesses
1. **No E2E tests** — All 331 tests mock the database; zero tests with real PostgreSQL
2. **Skipped HTTP tests** — 8 tests skipped that would verify real API behavior
3. **Missing guardrail tests** — Safety-critical AI guardrails have no direct tests
4. **Missing teach endpoint test** — `POST /teacher/teach` is the core AI entry point with no test
5. **No property-based testing** — No random/fuzz testing for edge cases
6. **No performance tests** — No load/benchmark tests
7. **No security tests** — No tests for SQL injection, XSS, rate limiting, etc.
8. **No snapshot/approval tests** — No golden file testing for AI outputs

---

## Recommendations

### Must Fix (High Impact)
1. **Add E2E test infrastructure** — Docker-based test database for `pytest`
2. **Test `POST /teacher/teach`** — The core AI endpoint is completely untested
3. **Test guardrails** — EmptyResponseDetector, JsonValidator, HallucinationPreventer
4. **Unskip auth API tests** — Auth flow validation needs a real DB

### Should Fix (Medium Impact)
5. **Add UserService tests** — User CRUD operations
6. **Add cross-module integration tests** — e.g., enrollment→session→progress flow
7. **Test teach endpoint HTTP integration** — Verify request/response with mocked AI

### Nice to Have (Low Impact)
8. **Fuzz testing for curriculum CRUD** — Random inputs to find edge cases
9. **Performance benchmarks** — Latency for graph execution
10. **Snapshot testing for AI outputs** — Track changes in prompt responses
