# Audit Discrepancies — Previous Audit vs Actual Code

> Compares claims made in the first audit (`docs/audit/`, since deleted) against verifiable source-code evidence. Designed to correct overclaims and identify where the first audit relied on planning documents or estimates instead of code. All line-number references below are historical — the first audit files have been removed as they were superseded by `docs/audit_v2/`.

---

## 1. Completion Percentage Estimates (No Evidence)

**Claim (docs/audit/PROJECT_STATUS.md:22-33):** Percentage estimates for "Backend API 85%", "AI Teacher Graph 80%", "Database Schema 95%", "Overall 65%".

**Evidence:**
- No methodology section describes how these percentages were calculated
- No measurable criteria (e.g., "90% = all CRUD routes for a module exist")
- `Backend/app/` contains 158 `.py` files, 9544 LOC — but there is no rubric mapping to a target total
- `docs/audit/PROJECT_STATUS.md:41-52` lists "P1-P8 Complete" for ALL phases, contradicting the 65% overall figure

**Verdict:** Estimates without evidence. Removed from this audit.

---

## 2. Phase Labels Misaligned with IMPLEMENTATION_PLAN.md

**Claim (docs/audit/PROJECT_STATUS.md:43-52):**

| Phase in First Audit | Claimed Status | Actual Plan |
|---------------------|----------------|-------------|
| P1: Foundation | Complete | Matches IMPLEMENTATION_PLAN.md Phase 1 |
| P2: Core Curriculum | Complete | Actually matches Phase 3 (Curriculum) in plan |
| P3: AI Teacher | Complete | Actually matches Phase 6 (AI Teacher MVP) in plan |
| P4: Student Features | Complete | Actually combines Phases 4 (Enrollments) + 5 (Sessions) |
| P5: Parent Features | Complete | Actually matches Phase 7 (Parent Intelligence) |
| P6: Advanced AI | Complete | **No such phase exists** in IMPLEMENTATION_PLAN.md |
| P7: Content Ingestion | Complete | **No such phase exists** in IMPLEMENTATION_PLAN.md |
| P8: Production Readiness | Not Started | **No such phase exists** in IMPLEMENTATION_PLAN.md |

**Verdict:** The first audit invented phases P6-P8 that do not appear in `IMPLEMENTATION_PLAN.md:3-17`. Content Ingestion is not a planned phase. These labels are misleading.

---

## 3. Knowledge Node CRUD Overclaimed

**Claim (docs/audit/FEATURE_MATRIX.md:32):** "Knowledge Node CRUD: ✅ Implemented, Tested, Production Ready."

**Evidence:**
- `app/knowledge_graph/router.py` — only defines 3 endpoints: `POST /edges`, `DELETE /edges/{id}`, `GET /concepts/{id}/prerequisites`
- `app/knowledge_graph/models.py` — defines `KnowledgeNode` and `KnowledgeEdge` models
- `app/knowledge_graph/repository.py` — `KnowledgeNodeRepository` is imported but has **no CRUD methods defined** that operate standalone
- `app/knowledge_graph/service.py` — `KnowledgeGraphService` only has `create_edge()`, `delete_edge()`, `get_prerequisites()`
- Knowledge nodes are created indirectly through content ingestion, not through a dedicated CRUD router

**Verdict:** Only edge CRUD and prerequisite traversal exist. No standalone node CRUD router. **Overclaimed.**

---

## 4. Redis Infrastructure Claimed But Not Present

**Claim (docs/audit/SYSTEM_ARCHITECTURE.md):** System architecture diagram includes Redis as a service. `docs/audit/PROJECT_STATUS.md:5` mentions "Redis for caching" in description.

**Evidence:**
- `docker-compose.yml` — No Redis service defined
- `pyproject.toml` — No `redis` dependency
- `app/infrastructure/` — No `redis.py` file
- `app/config.py` — No Redis configuration fields
- No calls to any Redis client exist anywhere in `app/`
- `app/ai/services/` — No LLM response cache implementation

**Verdict:** Redis does not exist in the codebase in any form. The planned ARCHITECTURE.md diagram (root level) shows Redis, but it was never implemented.

---

## 5. Qdrant Vector DB Claimed But Not Deployed

**Claim (docs/audit/AI_SYSTEM_AUDIT.md:28-29):** System diagram shows Qdrant as part of the production data flow. `docs/audit/AI_SYSTEM_AUDIT.md:46-47` refers to "Memory retrieval (Qdrant vector DB optional)".

**Evidence:**
- `docker-compose.yml` — No Qdrant service defined
- `pyproject.toml:31-33` — Qdrant is an **optional** dependency (`pip install acuity-lms-ai[qdrant]`)
- `app/ai/memory/retrieval.py:151` — Client attempts connection to `localhost:6333` but silently falls back on failure
- `app/ai/memory/retrieval.py:213` — Embeddings fall back to mock when Qdrant is unavailable
- No Qdrant health check in `app/api/routes/health.py`

**Verdict:** Qdrant code exists but is optional, untested, and not deployable. The diagram implies production integration that doesn't exist.

---

## 6. Guardrails Claimed as Production Feature

**Claim (docs/audit/AI_SYSTEM_AUDIT.md:29):** System diagram shows `GuardrailService` as part of the production pipeline. `docs/audit/FEATURE_MATRIX.md:65` marks guardrails as "✅ Implemented, ❌ Tested, ❌ Production Ready".

**Evidence:**
- `app/ai/guardrails/service.py` — Full implementation of JSON validation, empty detection, hallucination prevention
- Zero calls to `GuardrailService` in any node file (`app/ai/nodes/`)
- `app/ai/router.py` — No guardrail usage in the teach endpoint
- `app/ai/services/gemini.py` — No guardrail calls after `generate()`
- No guardrail test file exists in `tests/`

**Verdict:** Guardrails are a standalone module with zero integration into the production flow. The diagram is misleading.

---

## 7. "Pacing Status Tracking" Overclaimed

**Claim (docs/audit/FEATURE_MATRIX.md:40):** "Pace Status Tracking: ✅ On track / Behind / Ahead. Implemented, Tested, Production Ready."

**Evidence:**
- `app/pacing/service.py:25` — `get_pacing_status()` calculates pace but uses static milestone comparison logic
- `app/pacing/models.py:11` — `PacingRecord` model exists but its data is populated via the service, not through user interaction
- `app/pacing/router.py` — Only 1 GET endpoint
- `app/pacing/repository.py` — Basic CRUD
- No adaptive pacing (deadline pressure, mastery velocity) as described in `IMPLEMENTATION_PLAN.md:475` — this is a planned Phase 6 deliverable
- No revision scheduling as described in `IMPLEMENTATION_PLAN.md:476`

**Verdict:** Basic pacing tracking is implemented, but adaptive pacing + revision scheduling (as described in the plan) are NOT implemented.

---

## 8. "Attempt Recording with AI Feedback" Overclaimed

**Claim (docs/audit/FEATURE_MATRIX.md:43):** "Attempt Recording: ✅ With AI feedback. Implemented, Tested, Production Ready."

**Evidence:**
- `app/teaching/service.py` — `record_attempt()` records the attempt but AI feedback is generated through `app/ai/node.py` which runs in the teaching graph, not inline in the attempt recording
- `tests/test_attempts.py:15` — `test_record_attempt()` does not assert AI feedback content
- The AI feedback field in `Attempt` model (`app/teaching/models.py:25` — `ai_feedback`) is populated by the graph evaluation node, not by the attempt recording service itself

**Verdict:** Attempt recording works, but "AI feedback" depends on the teaching graph being invoked — it's not an automatic property of the recording endpoint.

---

## 9. "RBAC Complete" Overclaimed

**Claim (docs/audit/FEATURE_MATRIX.md:13):** "RBAC (Admin/Student/Parent): ✅ Implemented, Tested, Production Ready."

**Evidence:**
- `app/auth/dependencies.py:25` — `require_role()` dependency checks role at endpoint level
- `app/security/rbac.py:15` — `RoleChecker` class implements role-based access
- However, 3 RBAC tests in `tests/test_rbac.py:121,129,150` are **skipped** (`@pytest.mark.skip(reason="requires live database")`)
- No integration test exercises the RBAC middleware in an HTTP context
- `docs/audit_v2/PRODUCTION_GAPS.md:102-108` — Resource-level permission checks are inconsistent across services

**Verdict:** Role-level checks exist but are untested at the HTTP layer. Resource-level ownership is inconsistent. Marked as "Partial" in this audit.

---

## 10. Missing Qdrant/Redis from Previous Audit's Gap Analysis

**Claim (docs/audit/PRODUCTION_READINESS_AUDIT.md):** Production gaps analysis covers Docker, monitoring, rate limiting, etc.

**Evidence:**
- No mention in the first audit's production gaps of the fact that Redis is entirely missing from the codebase despite being in the architecture
- No mention that Qdrant is optional/undeployable
- These are not just "production gaps" — they are unimplemented planned services

**Verdict:** The first audit failed to flag that 2 of the 3 planned infrastructure services (Redis, Qdrant) are absent from the deployable stack.

---

## Summary

| Category | First Audit Claim | Corrected Status |
|----------|-------------------|-----------------|
| Completion % | 65% overall | Removed — estimate without evidence |
| Redis | Included in architecture | Not present at all |
| Qdrant | Production service | Optional, undeployable dependency |
| Guardrails | System component | Code exists, zero production integration |
| Knowledge Node CRUD | ✅ Implemented | Only edge CRUD, no standalone node CRUD |
| RBAC | ✅ Production Ready | Role checks exist but HTTP-tests skipped |
| Adaptive Pacing | ✅ Implemented | Basic tracking only, no adaptive engine |
| Phases P6-P8 | "Complete" | Phases do not exist in plan |
