# Execution Plan

> Prioritized roadmap built from findings in `FOUNDER_SUMMARY.md`, `MISSING_FEATURES.md`, `PRODUCTION_GAPS.md`, and `AUDIT_DISCREPANCIES.md`. All effort and risk ratings are based on codebase evidence — no speculation.

---

## Scoring Guide

| Score | Business Impact | Technical Risk |
|-------|----------------|----------------|
| 1-3   | Minor UX/admin convenience | Trivial change, well-understood |
| 4-6   | Moderate productivity gain | Some unknowns, existing patterns |
| 7-8   | Core feature blocked | Architectural change or new infra |
| 9-10  | System unusable / security breach | High complexity, untested approach |

**Effort:** S = 1-3 days, M = ~1 week, L = 2-4 weeks, XL = 5+ weeks.

---

## Complete Feature Inventory

> All missing or partial features from the audit, ordered by priority group.

---

## Group 1 — Must Complete Before Pilot

**Rationale:** Each of these items is a hard blocker for a real external pilot. Without them the system is either insecure, non-deployable, or its core value proposition (AI teaching) is untested with a real LLM. These should be completed before any pilot participant receives credentials.

| # | Feature | Category | Business Impact | Tech Risk | Pilot Blocker | Effort |
|---|---------|----------|:-:|:-:|:-:|:-:|
| 1 | **Default JWT secret -> env-required** | Security | 10 | 2 | Yes | S |
| 2 | **Rate limiting middleware** | Security | 8 | 3 | Yes | S |
| 3 | **Email delivery for password reset** | Security | 8 | 4 | Yes | M |
| 4 | **Guardrails integrated into production flow** | AI Safety | 9 | 4 | Yes | M |
| 5 | **Real Gemini API validation + integration test** | AI Core | 9 | 5 | Yes | M |
| 6 | **Docker Compose -- add app service** | Infrastructure | 9 | 3 | Yes | S |
| 7 | **Enrollment pause/resume endpoint** | API Completeness | 6 | 2 | Yes | S |
| 8 | **Teach endpoint HTTP test** | Testing | 7 | 2 | Yes | S |

### Recommendations

1. **Default JWT secret -> env-required** -- Change `app/config.py:37` to fail at startup if `SECRET_KEY` is unset. Add validation — no default value. Dependencies: None.

2. **Rate limiting middleware** -- Add `slowapi` to `pyproject.toml`. Register `Limiter` middleware in `app/main.py:50`. Per-endpoint limits: 10/min for auth, 30/min for AI, 100/min for curriculum. Dependencies: None.

3. **Email delivery for password reset** -- Add SMTP settings to `app/config.py`. Add email-sending step to `app/auth/service.py:forgot_password()`. Use `aiosmtplib`. Dependencies: SMTP config.

4. **Guardrails integrated into production flow** -- Call `GuardrailService` after each Gemini response in `app/ai/nodes/teach.py:25`, `evaluate.py:30`, `diagnose.py:35`. Add guardrail tests. Dependencies: None.

5. **Real Gemini API validation + integration test** -- Replace `app/ai/services/gemini.py:39` mock fallback with real API call. Add integration test with known prompt asserting valid JSON output. Add `gemini_api_key` to CI secrets. Dependencies: Gemini API key.

6. **Docker Compose -- add app service** -- Add `app:` service to `docker-compose.yml` with build context, port 8000:8000, depends_on PostgreSQL, env from `.env`. Dependencies: Dockerfile.

7. **Enrollment pause/resume endpoint** -- Implement `PATCH /enrollments/{id}` in `app/enrollment/router.py:25`. Logic exists in service, missing HTTP route. Dependencies: None.

8. **Teach endpoint HTTP test** -- Add `tests/test_ai_router.py` with TestClient test for `POST /teacher/teach` using mock Gemini. Dependencies: None.

---

## Group 2 -- Strongly Recommended Before Pilot

**Rationale:** These items significantly improve pilot safety, reliability, and usefulness. Without them the pilot will work but risks data loss, poor observability, and brittle deployment. Address before or during early pilot to avoid firefighting.

| # | Feature | Category | Business Impact | Tech Risk | Pilot Blocker | Effort |
|---|---------|----------|:-:|:-:|:-:|:-:|
| 9 | **Database backup automation** | Infrastructure | 8 | 2 | No | S |
| 10 | **Comprehensive health check** | Infrastructure | 6 | 3 | No | S |
| 11 | **CI/CD pipeline (GitHub Actions)** | Infrastructure | 7 | 4 | No | M |
| 12 | **Production monitoring (Prometheus metrics)** | Infrastructure | 7 | 5 | No | L |
| 13 | **HTTPS termination** | Security | 7 | 3 | No | M |
| 14 | **Audit log writes** | Security | 6 | 3 | No | M |
| 15 | **Async task queue for AI calls** | AI Performance | 7 | 6 | No | L |
| 16 | **Fix 8 skipped tests (test DB fixture)** | Testing | 5 | 4 | No | M |
| 17 | **Resource-level permission checks** | Security | 5 | 4 | No | M |
| 18 | **Idle session detection** | Session Mgmt | 5 | 3 | No | S |

### Recommendations

9. **Database backup automation** -- Add `pg_dump` cron via `docker-compose` or `scripts/backup_db.py`. Mount backup volume. Dependencies: None.

10. **Comprehensive health check** -- Extend `app/api/routes/health.py:13` to check Gemini API key, DB, disk space. Per-component status response. Dependencies: None.

11. **CI/CD pipeline** -- Add `.github/workflows/ci.yml`: pytest on push/PR, lint, test matrix (3.11, 3.12). Dependencies: GitHub repo.

12. **Production monitoring** -- Add `prometheus-client` dep. Instrument `app/monitoring/metrics.py` with request count, latency, AI call duration, error rate. Expose `/metrics` endpoint. Dependencies: None.

13. **HTTPS termination** -- Add SSL key/cert to uvicorn in `Dockerfile:24`. Or add nginx/Caddy reverse proxy in `docker-compose.yml`. Dependencies: Domain + cert.

14. **Audit log writes** -- Add middleware in `app/main.py` logging all mutating requests to `AuditLog` table. Includes user_id, action, resource_type, resource_id, details. Dependencies: None.

15. **Async task queue for AI calls** -- Extract AI graph from HTTP handler. Add background queue (`arq` or `anyio`). Return 202 with task ID, polling endpoint. Dependencies: Redis (or in-memory).

16. **Fix 8 skipped tests** -- Create test DB fixture via `testcontainers` or SQLite. Enable skipped auth/RBAC HTTP tests. Dependencies: None.

17. **Resource-level permission checks** -- Audit services. Add ownership guards in `app/curriculum/service.py` and `app/mastery/service.py`. Dependencies: None.

18. **Idle session detection** -- In `app/teaching_sessions/service.py:get_active_session()`: auto-interrupt if `last_activity_at` > 30 min. Dependencies: None.

---

## Group 3 -- Post-Pilot Enhancements

**Rationale:** These add real value but require heavier investment or pilot usage data to guide priority. Building before pilot risks building features nobody uses.

| # | Feature | Category | Business Impact | Tech Risk | Pilot Blocker | Effort |
|---|---------|----------|:-:|:-:|:-:|:-:|
| 19 | **Frontend (MVP)** | Product | 10 | 8 | No | XL |
| 20 | **Redis -- session cache + LLM cache** | Infrastructure | 6 | 4 | No | L |
| 21 | **Qdrant -- deploy + index pipeline** | AI Infra | 6 | 5 | No | L |
| 22 | **Adaptive pacing engine** | AI Enhancement | 6 | 6 | No | L |
| 23 | **AI quiz generation endpoint** | API Completeness | 6 | 5 | No | M |
| 24 | **Student response streaming** | AI UX | 5 | 6 | No | L |
| 25 | **Mastery detail + course aggregate endpoints** | API Completeness | 4 | 2 | No | S |
| 26 | **Guardrail tests** | Testing | 5 | 3 | No | S |
| 27 | **End-to-end test (real DB + real AI)** | Testing | 6 | 6 | No | M |
| 28 | **Diagnosis list + update endpoints** | API Completeness | 4 | 2 | No | S |
| 29 | **Admin panel endpoints** | API Completeness | 4 | 3 | No | M |

### Recommendations

19. **Frontend (MVP)** -- Build React/Vite SPA: login, curriculum browser, teaching session UI, parent dashboard. Start with student flow. Leverage OpenAPI schema. Dependencies: None (but XL effort).

20. **Redis** -- Add to `docker-compose.yml`. Implement `app/infrastructure/redis.py`. Add LLM response caching in `app/ai/services/gemini.py` (prompt hash key, 1hr TTL). Dependencies: Docker Compose Redis service.

21. **Qdrant -- deploy + index** -- Add to `docker-compose.yml`. Move client to `app/infrastructure/qdrant.py`. Index concepts on create/update. Wire semantic retrieval into teacher graph. Dependencies: Docker Compose Qdrant service.

22. **Adaptive pacing** -- New `app/scheduling/service.py`. Adjust `target_lessons_per_week` based on mastery velocity and deadline. Generate `next_review_at`. Dependencies: Pilot usage data.

23. **AI quiz generation** -- `POST /sessions/{id}/quiz`. Uses GeminiService with quiz-generation prompt. Dependencies: None.

24. **Student response streaming** -- WebSocket endpoint for sessions. Stream via Gemini streaming API. Dependencies: None.

25. **Mastery detail + course aggregate** -- `GET /mastery/concepts/{id}`, `GET /mastery/courses/{id}`. Data exists in service. Dependencies: None.

26. **Guardrail tests** -- `tests/test_guardrails.py`: all 4 GuardrailService methods. Dependencies: None.

27. **E2E test** -- `tests/integration/test_e2e_teaching_flow.py` with real PostgreSQL + real Gemini. Dependencies: Test DB container, Gemini API key.

28. **Diagnosis list + update** -- `GET /diagnosis`, `GET /diagnosis/concepts/{id}`, `PATCH /diagnosis/{id}/resolve`. Service methods exist. Dependencies: None.

29. **Admin panel endpoints** -- `GET /admin/users`, `GET /admin/dashboard`, etc. (from API_CONTRACTS.md). Read-only queries. Dependencies: None.

---

## Group 4 -- Nice To Have

**Rationale:** Speculative features from ARCHITECTURE.md not validated by user demand. Do not start until pilot feedback confirms need.

| # | Feature | Category | Business Impact | Tech Risk | Pilot Blocker | Effort |
|---|---------|----------|:-:|:-:|:-:|:-:|
| 30 | **API client SDK** | Tooling | 4 | 5 | No | L |
| 31 | **Jinja2 prompt templates** | AI Refactor | 3 | 3 | No | M |
| 32 | **Jinja2 report templates** | Product | 3 | 3 | No | M |
| 33 | **PDF report generation** | Product | 3 | 5 | No | L |
| 34 | **Report scheduling (weekly auto)** | Product | 3 | 5 | No | M |
| 35 | **Refresh token reuse detection** | Security | 4 | 4 | No | M |
| 36 | **Separate diagnosis/pacing graphs** | AI Refactor | 2 | 5 | No | L |
| 37 | **Log aggregation** | Infrastructure | 3 | 4 | No | M |
| 38 | **Horizontal scaling config** | Infrastructure | 3 | 5 | No | M |
| 39 | **Insights module** | Product | 2 | 6 | No | XL |
| 40 | **Assessment module** | Product | 2 | 6 | No | XL |
| 41 | **Docker HEALTHCHECK** | Infrastructure | 2 | 2 | No | S |
| 42 | **Non-root user fix** | Infrastructure | 2 | 2 | No | S |

### Recommendations

30. **API client SDK** -- Generate via `openapi-generator`. Only if pilot partners request it.

31. **Jinja2 prompt templates** -- Migrate from Python strings to Jinja2. Low value vs effort.

32. **Jinja2 report templates** -- Template system for report formatting. Only if report customization becomes important.

33. **PDF report generation** -- WeasyPrint-based. Only if pilot requires downloadable PDFs.

34. **Report scheduling** -- Weekly automated generation via background task. Requires task queue infra first.

35. **Refresh token reuse detection** -- Add token family/session tracking. Only if token theft becomes a concern.

36. **Separate diagnosis/pacing graphs** -- Extract from single teacher.py. Only if graph complexity warrants.

37. **Log aggregation** -- Filebeat/Loki/CloudWatch. Only if debugging production issues requires it.

38. **Horizontal scaling** -- Session affinity, distributed cache. Only if load requires multiple instances.

39. **Insights module** -- New `app/insights/`. Entirely speculative from ARCHITECTURE.md.

40. **Assessment module** -- New `app/assessment/`. Entirely speculative from ARCHITECTURE.md.

41. **Docker HEALTHCHECK** -- Add `HEALTHCHECK` instruction to `Dockerfile`. S trivial.

42. **Non-root user fix** -- Move `pip install` before USER switch in `Dockerfile`. S trivial.

---

## Effort Summary

| Priority Group | S | M | L | XL | Total Items |
|---------------|:-:|:-:|:-:|:--:|:-----------:|
| Group 1: Must Complete Before Pilot | 4 | 4 | 0 | 0 | 8 |
| Group 2: Strongly Recommended | 3 | 4 | 3 | 0 | 10 |
| Group 3: Post-Pilot | 3 | 3 | 4 | 1 | 11 |
| Group 4: Nice To Have | 2 | 4 | 3 | 2 | 13 |

---

## Recommended Next 30 Days

**Goal:** Eliminate all 8 pilot blockers (Group 1) and complete the 3 highest-value Group 2 items. At the end of 30 days, the system should be secure, deployable, and ready for external pilot participants.

### Week 1 (Days 1-7): Security & Deployment Foundations

| Day | Task | Assignee | Deliverable |
|:---:|------|----------|-------------|
| 1 | **Default JWT secret -> env-required** | Backend | `app/config.py` validates `SECRET_KEY` is set, fails fast with clear error |
| 1 | **Add rate limiting** | Backend | `slowapi` installed, middleware registered, per-endpoint limits configured |
| 2 | **Docker Compose app service** | Backend | Full `docker-compose up` starts app + PostgreSQL, health endpoint responds |
| 2-3 | **Comprehensive health check** | Backend | `GET /health` returns DB status, Gemini key validity, disk space |
| 3-4 | **Database backup automation** | Backend | `scripts/backup_db.py` or cron job, backup volume mounted |
| 4-5 | **Teach endpoint HTTP test** | Backend | `tests/test_ai_router.py` with TestClient, mock Gemini |
| 5-7 | **CI/CD pipeline (GitHub Actions)** | Backend | Push triggers test run, lint check, test results reported |

**Week 1 exit criteria:** `docker-compose up` runs the full stack. `pytest` passes all 331 tests. CI passes on every push. No default secrets in source.

### Week 2 (Days 8-14): AI Hardening & Email

| Day | Task | Assignee | Deliverable |
|:---:|------|----------|-------------|
| 8-9 | **Guardrails integration** | Backend | `GuardrailService` called after each Gemini response in all nodes. Guardrail tests added. |
| 9-10 | **Gemini real API validation** | Backend | Mock fallback replaced. Integration test with real Gemini call. |
| 10-11 | **Email delivery** | Backend | SMTP config in `app/config.py`. Password reset sends actual email. |
| 11-12 | **Enrollment pause/resume** | Backend | `PATCH /enrollments/{id}` implemented and tested. |
| 12-14 | **Idle session detection** | Backend | Auto-interrupt after 30 min inactivity. Session state machine complete. |

**Week 2 exit criteria:** AI teaching flow runs with real Gemini. Guardrails protect all AI output. Password reset emails deliver. All Group 1 items complete.

### Week 3 (Days 15-21): Observability & Remaining Group 2

| Day | Task | Assignee | Deliverable |
|:---:|------|----------|-------------|
| 15-16 | **Audit log writes** | Backend | Middleware logs all mutations to `AuditLog` table. |
| 16-17 | **Resource-level permission checks** | Backend | Ownership guards in curriculum + mastery services. |
| 17-18 | **Fix 8 skipped tests** | Backend | Test DB fixture enables auth/RBAC HTTP tests. All 339 tests pass. |
| 18-19 | **HTTPS termination** | Infra | SSL cert + uvicorn SSL config. Or nginx reverse proxy in docker-compose. |
| 19-21 | **Production monitoring (Prometheus)** | Backend | `/metrics` endpoint. Request count, AI latency, error rate counters. |

**Week 3 exit criteria:** All mutations are audited. Permissions are consistent. All tests pass including formerly skipped ones. HTTPS is configured. Metrics are observable.

### Week 4 (Days 22-30): Async AI, Missing APIs, Pilot Readiness

| Day | Task | Assignee | Deliverable |
|:---:|------|----------|-------------|
| 22-24 | **Async task queue for AI calls** | Backend | AI graph extracted from HTTP handler. Returns 202 + polling endpoint. |
| 24-25 | **Mastery detail + course aggregate endpoints** | Backend | `GET /mastery/concepts/{id}`, `GET /mastery/courses/{id}` |
| 25-26 | **Diagnosis list + update endpoints** | Backend | `GET /diagnosis`, `GET /diagnosis/concepts/{id}`, `PATCH /diagnosis/{id}/resolve` |
| 26-27 | **AI quiz generation endpoint** | Backend | `POST /sessions/{id}/quiz` |
| 27-28 | **Admin panel endpoints** | Backend | `GET /admin/users`, `GET /admin/dashboard` |
| 28-30 | **Pilot readiness review** | All | Checklist walkthrough. Deploy to staging. Invite pilot participants. |

**Week 4 exit criteria:** AI calls are non-blocking. All 6 missing API_CONTRACTS.md endpoints are implemented. Admin can manage users. Staging environment is ready for pilot.

---

## Post-30-Day Priorities

After the initial 30 days, prioritize based on pilot feedback:

| Priority | Feature | Trigger |
|----------|---------|---------|
| High | **Frontend (MVP)** | Pilot partners ask "where is the website?" |
| High | **E2E test** | Before any production deployment |
| Medium | **Redis** | Latency from uncached LLM calls becomes noticeable |
| Medium | **Qdrant** | Semantic memory retrieval quality is insufficient |
| Low | **Adaptive pacing** | After enough usage data to calibrate |
| Low | **Student response streaming** | Users complain about response wait time |
