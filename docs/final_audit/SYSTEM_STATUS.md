# SYSTEM STATUS — Acuity LMS AI

**Generated:** 2026-06-25
**Audit Scope:** Entire repository (backend + frontend + infra)
**Status:** PRE-ALPHA — Not production ready, not demo ready

---

## 1. Executive Summary

Acuity LMS AI is a partially implemented AI-Native Personalized Schooling Platform. The backend is structurally well-organized (modular monolith, repository/service/router pattern) with approximately 75 API endpoints across 14 modules. The frontend (React + Vite + TypeScript) has 15 pages across 4 roles. The AI teacher uses LangGraph with 7 nodes and Gemini integration.

**Critical blockers (must fix before any demo):**

| # | Issue | Area | Severity |
|---|-------|------|----------|
| 1 | No route guards or role-based access on any frontend page | Frontend | CRITICAL |
| 2 | Assessment `correctIndex: 0` — every question marks first option correct | Frontend | CRITICAL |
| 3 | No database-backed tests; all 331 tests use mocks | Testing | CRITICAL |
| 4 | GuardrailService never called — all LLM output reaches user unchecked | AI | CRITICAL |
| 5 | Qdrant embedding generation is broken (LLM text output parsed as vectors) | AI | CRITICAL |
| 6 | LangGraph has no default edge — unrecognized action crashes graph | AI | CRITICAL |
| 7 | No error handling in any graph node — any exception crashes graph | AI | CRITICAL |
| 8 | Password reset email never sent (no SMTP infrastructure) | Auth | CRITICAL |
| 9 | Default JWT secret hardcoded in source | Security | CRITICAL |
| 10 | Progress update uses wrong ID (`lesson.id` instead of `existing.id`) | Backend | CRITICAL |

---

## 2. Module Status Overview

| Module | Status | Completion | Tests | Issues |
|--------|--------|-----------|-------|--------|
| Backend Core (config, DB, logging) | ✅ Complete | 95% | N/A | Debug leaks SQL by default; hardcoded defaults |
| Auth (register, login, refresh, logout) | ✅ Complete | 90% | 22 unit + 8 skipped HTTP | No email for password reset; no rate limiting |
| Auth (forgot/reset password) | ⚠️ Broken | 50% | Partial | Email never sent; token returned to caller but discarded |
| RBAC / Security | ✅ Complete | 85% | Tested | No rate limiting; JWT secret in source; email in token |
| Curriculum CRUD (courses→modules→lessons→concepts→contents→exercises→examples→objectives) | ✅ Complete | 100% | 15 unit | Wrong schema on content update endpoint |
| Knowledge Graph | ✅ Complete | 100% | 11 unit | N+1 query in get_prerequisites |
| Enrollment | ✅ Complete | 95% | 9 unit | No role guard; any auth user can enroll |
| Progress | ⚠️ Broken | 80% | 9 unit | **CRITICAL: update uses wrong ID** |
| Mastery | ✅ Complete | 95% | 10 unit | Empty response for non-existent records |
| Pacing | ⚠️ Broken | 70% | 9 unit | Generate endpoint is dead code; response has empty course_id |
| Teaching Sessions | ✅ Complete | 95% | 16 unit | Attempt FK constraint mismatch with service |
| AI Teacher Graph | ⚠️ Broken | 60% | 22 unit | No error handling; no guardrails; no retry; mock-only |
| AI Memory System | ⚠️ Broken | 50% | 21 unit | Qdrant embeddings broken; `hash()` IDs unstable |
| AI Diagnosis | ✅ Complete | 85% | 15 unit | Hardcoded expected_answer |
| AI Guardrails | ❌ Disconnected | 90% | 0 | Code exists but never called from any node |
| AI Evaluation Harness | ⚠️ Buggy | 70% | 15 unit | Graph invoked twice doubling cost; model_calls miscounts |
| Parent Dashboard | ✅ Complete | 95% | 26 unit | N+1 queries in 3 methods |
| Reports | ✅ Complete | 90% | 20 unit + 3 HTTP | Duplicated parent access verification |
| Content Ingestion | ✅ Complete | 95% | 22 unit | Hardcoded upload dir; dir creation on every instantiation |
| Diagnosis (business layer) | ❌ Stub | 10% | 0 | Model only; no CRUD service |
| Memory (business layer) | ❌ Stub | 10% | 0 | Model only; no CRUD service |
| Audit Logging | ❌ Disconnected | 90% | 0 | Model exists but never written to |
| Monitoring | ✅ Complete | 90% | 0 | In-memory only; lost on restart |
| Docker / DevOps | ⚠️ Partial | 40% | N/A | Dockerfile broken; compose missing app service |
| Frontend — Auth & Routing | ⚠️ Broken | 50% | 0 | **No guards; no role protection** |
| Frontend — Landing | ✅ Complete | 100% | 0 | Demo-ready |
| Frontend — Login/Register | ✅ Complete | 85% | 0 | No forgot-password link |
| Frontend — Student Dashboard | ⚠️ Buggy | 70% | 0 | Fake parameter scores; no multi-course |
| Frontend — AI Tutor | ⚠️ Partial | 70% | 0 | No endSession on unmount |
| Frontend — Assessment | ❌ Broken | 40% | 0 | **correctIndex: 0 bug** |
| Frontend — Progress | ✅ Complete | 80% | 0 | Assumes 0-1 mastery range |
| Frontend — Learning Path | ⚠️ Partial | 70% | 0 | No empty state |
| Frontend — Parent Dashboard | ⚠️ Partial | 60% | 0 | First-student only; non-functional buttons |
| Frontend — Admin Dashboard | ⚠️ Partial | 70% | 0 | Arbitrary metric mappings |
| Frontend — Admin Students | ⚠️ Partial | 60% | 0 | Search is decorative; no pagination |
| Frontend — Admin Analytics | ⚠️ Partial | 50% | 0 | Static numbers only; no charts |
| Frontend — Profile | ✅ Complete | 80% | 0 | Read-only |
| Frontend — Student Onboarding | ⚠️ Partial | 70% | 0 | Silent error catch; first-course only |
| Tests — Backend | ⚠️ Partial | 60% | 331 tests | No DB-backed tests; 8 skipped; no HTTP tests for 10 of 14 modules |
| Tests — Frontend | ❌ Missing | 0% | 0 | No test framework installed |
| Documentation | ✅ Complete | 85% | N/A | Docs mostly aligned; some outdated references |

---

## 3. Backend Health

### 3.1 API Endpoints

| Module | Prefix | Auth | Endpoints | Status |
|--------|--------|------|-----------|--------|
| Health | `/api/v1/health` | Public | 1 | ✅ |
| Auth | `/api/v1/auth` | Public (except logout) | 6 | ✅ (forgot/reset broken) |
| Curriculum | `/api/v1/courses, /modules, /lessons, /concepts` | Admin/Student | 26 | ✅ |
| Knowledge Graph | `/api/v1/knowledge-graph` | Admin | 3 | ✅ |
| Enrollment | `/api/v1/enrollments` | Student | 3 | ✅ (missing role guard) |
| Progress | `/api/v1/lessons/{id}/progress` | Student | 2 | ⚠️ (broken update) |
| Mastery | `/api/v1/mastery` | Student | 3 | ✅ |
| Pacing | `/api/v1/pacing` | Student | 3 | ⚠️ (generate is dead code) |
| Teaching Sessions | `/api/v1/sessions` | Student | 5 | ✅ |
| AI Teacher | `/api/v1/teacher` | Student | 2 | ⚠️ (no error handling) |
| AI Evaluation | `/api/v1/ai/evaluation` | Internal | 6 | ⚠️ (harness bugs) |
| Parent Dashboard | `/api/v1/parent` | Parent | 12 | ✅ |
| Reports | `/api/v1/reports` | Auth | 3 | ✅ |
| Content Ingestion | `/api/v1/content` | Admin | 9 | ✅ |
| **Total** | | | **~84** | |

### 3.2 Database

| Metric | Value |
|--------|-------|
| Tables | 30 |
| ENUM types | 14 |
| Migrations | 4 |
| Alembic head | Up-to-date |
| Schema-doc alignment | ✅ Good |

### 3.3 AI System

| Component | Lines | Status |
|-----------|-------|--------|
| LangGraph graph | ~78 | ⚠️ No error handling, no default edge |
| Teach node | ~45 | ⚠️ No guardrails |
| Ask question node | ~20 | ⚠️ No guardrails |
| Evaluate response node | ~50 | ⚠️ No guardrails |
| Diagnose node | ~45 | ⚠️ No guardrails |
| Provide example node | ~30 | ⚠️ No guardrails |
| Complete concept node | ~15 | ✅ |
| Retrieve memories node | ~20 | ⚠️ No error handling |
| GeminiService | ~90 | ⚠️ No retry, mock fallback silent |
| GuardrailService | ~100 | ❌ Orphaned (never called) |
| MemoryService | ~95 | ⚠️ Qdrant integration broken |
| DiagnosisService | ~100 | ✅ |
| Evaluation harness | ~170 | ⚠️ Double invocations |

---

## 4. Frontend Health

| Metric | Value |
|--------|-------|
| Pages | 15 |
| API service modules | 13 |
| Custom hooks | 5 |
| Shared components | 1 |
| Tests | 0 |
| TypeScript strict mode | ✅ On |

### 4.1 Critical Frontend Issues

1. **No route guards** — any user can navigate to any route without auth
2. **No role-based access** — student can access admin pages and vice versa
3. **Assessment `correctIndex: 0`** — all questions mark first option correct
4. **authStore not persisted** — `currentUser` is null on page reload
5. **Topbar not reactive** — doesn't update on login/logout
6. **Fake parameter scores** on student dashboard (invented multipliers)
7. **Sequential assessment submissions** (not parallel)
8. **Onboarding silently swallows all errors**
9. **Several non-functional buttons** (Download Report, Filters, Notifications)

---

## 5. Testing Health

| Area | Tests | Coverage |
|------|-------|----------|
| Unit tests | 312 | Services, repos, schemas |
| HTTP API tests | 11 | Health (1), Parent (2), Reports (3), Evaluation (1), Auth (0), everything else (0) |
| Integration tests | 19 | All mocked — no real DB |
| AI flow tests | 82 | All mocked — no real Gemini |
| Frontend tests | 0 | 0 |
| **Total** | **331** | **323 active, 8 skipped** |

---

## 6. Infrastructure Health

| Component | Status | Notes |
|-----------|--------|-------|
| PostgreSQL | ✅ Ready | Docker compose only |
| Backend Dockerfile | ⚠️ Broken | `pip install .` before source copy |
| Frontend build | ✅ Works | Vite dev server |
| Redis | ❌ Missing | Not in compose, no client |
| Qdrant | ❌ Missing | Not in compose, broken integration |
| CI/CD | ❌ Missing | No pipelines |
| Monitoring | ⚠️ In-memory | Lost on restart |
| Health checks | ⚠️ Partial | DB only, no AI/Gemini check |

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Unauthorized data access via unprotected frontend routes | HIGH | CRITICAL | Add route guards + role checks |
| Wrong assessment scoring | HIGH | HIGH | Fix correctIndex: 0 |
| Data loss from unchecked LLM output | MEDIUM | HIGH | Wire guardrails into graph |
| AI system silently serving mock responses in production | MEDIUM | HIGH | Detect and alert on mock fallback |
| JWT token forgery with default secret | LOW (prod deployment) | CRITICAL | Validate SECRET_KEY at startup |
| Silent data corruption from Repository.update() | MEDIUM | HIGH | Add field validation |
| Docker build fails in CI/CD | HIGH | MEDIUM | Fix Dockerfile |

---

## 8. Overall Scorecard

| Category | Score (0-10) |
|----------|:------------:|
| Backend Implementation | 7 |
| Backend Correctness | 5 |
| AI System | 4 |
| Frontend Implementation | 5 |
| Frontend Correctness | 3 |
| Security | 3 |
| Testing | 4 |
| Infrastructure/DevOps | 3 |
| Documentation | 7 |
| **Overall** | **4.5** |
