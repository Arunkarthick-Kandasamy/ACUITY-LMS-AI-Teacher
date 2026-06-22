# Roadmap Recommendations

## Assessment Philosophy

This document is based strictly on the actual codebase analysis — not on previous plans or external requirements. Recommendations are ranked by business impact (what a user or stakeholder would notice).

---

## What Is Complete (Ship-Ready)

| Feature | Notes |
|---------|-------|
| User registration + login + JWT | Full auth flow with refresh tokens |
| Course/Module/Lesson/Concept CRUD | Complete hierarchy with ordering, uniqueness constraints |
| Knowledge Graph | Nodes, edges, prerequisite traversal |
| Student Enrollment | Enroll, list, status lifecycle |
| Lesson Progress Tracking | Per-student per-lesson with completion percentage |
| Concept Mastery Scoring | Per-student per-concept with spaced repetition |
| Teaching Sessions | Start, pause, resume, end with context persistence |
| Attempt Recording | Per-exercise with correctness, score, AI feedback |
| Parent Dashboard (12 read endpoints) | Full read-only view of linked student data |
| Content Ingestion Pipeline | Upload TXT/PDF/DOCX → AI extract → review → approve → publish |
| AI Reports Generation | Weekly/monthly/milestone reports with risk indicators |
| Pacing/Scheduling | Per-enrollment schedule with pace status tracking |
| Evaluation Harness | Metrics, traces, 4 scenarios for testing the AI graph |
| Database Schema | 30 tables with migrations, constraints, indexes |

---

## What Is Partially Complete

| Feature | Status | Missing |
|---------|--------|---------|
| AI Teacher Graph | Core loop works | Guardrails not integrated; no real Gemini testing; no student response streaming |
| Memory System | Extraction + DB storage works | Qdrant not deployed; semantic search never tested |
| AI Guardrails | Code exists | Not wired into production teaching flow |
| Testing | 323 tests | No E2E tests; 8 skipped; missing guardrail + teach endpoint + UserService tests |
| Security | Basic JWT + bcrypt | Missing: rate limiting, audit logging, email delivery, secret rotation |
| Monitoring | In-memory metrics | No persistent storage, no alerting, no Prometheus integration |
| Documentation | Architecture, API, DB docs | Missing: deployment guide, operations runbook, contributor guide |

---

## What Is Missing

| Feature | Business Impact | Why It Matters |
|---------|:---------------:|----------------|
| **Frontend** | Critical | No user interface exists; product cannot be used without API clients |
| **E2E Tests** | High | Cannot confidently deploy without testing real database + AI behavior |
| **Email Service** | High | Password reset feature is non-functional |
| **Rate Limiting** | High | Vulnerable to abuse; AI costs could spiral |
| **Production Secret Management** | Critical | Security risk: default JWT secret in source code |
| **CI/CD Pipeline** | High | Manual deployment only; no automated testing on PRs |
| **Real Gemini Testing** | High | All development uses mock AI responses; real behavior may differ |
| **Async AI Task Queue** | Medium | Current calls block HTTP request; bad UX for long-running AI generation |
| **CDN for File Uploads** | Medium | Content uploads stored on application filesystem; not scalable |
| **Log Aggregation** | Medium | No centralized log viewing for production issues |
| **Database Backups** | High | No backup strategy = data loss risk |
| **GDPR/FERPA Compliance** | Medium | No data retention or export policies |

---

## Recommendations by Priority

### 🚨 Must Have (Pre-Launch)

| # | Item | Effort | Business Impact | Notes |
|---|------|:------:|:---------------:|-------|
| 1 | **Frontend MVP** | 3-6 months | Critical | Without UI, the platform has zero users. Recommend React/Next.js given CORS config for localhost:3000 and :5173 |
| 2 | **Production Secret Management** | 1 day | Critical | Set strong SECRET_KEY via env var; remove default |
| 3 | **Rate Limiting** | 2 days | High | Implement `slowapi` or nginx rate limiting before any production deployment |
| 4 | **Email Service Integration** | 3 days | High | Password reset requires email delivery (SendGrid, AWS SES) |
| 5 | **CI/CD Pipeline** | 3 days | High | GitHub Actions: lint → test → build → deploy |
| 6 | **Database Backups** | 1 day | High | Automated pg_dump to cloud storage |
| 7 | **E2E Test Infrastructure** | 1 week | High | Docker Compose test database for pytest |

### ✅ Should Have (Pre-Beta)

| # | Item | Effort | Business Impact |
|---|------|:------:|:---------------:|
| 8 | **Guardrail Integration** | 1 week | Medium — AI output quality assurance |
| 9 | **Real Gemini Testing** | 2 days | Medium — validate prompt quality |
| 10 | **Fix Mock Fallback Warning** | 1 hour | Medium — prevent silent failures |
| 11 | **HTTPS Termination** | 1 day | Medium — security requirement |
| 12 | **Async Task Queue for AI** | 2 weeks | Medium — non-blocking AI calls |
| 13 | **Async Draft Endpoint Fix** | 1 hour | Low — API contract correctness |
| 14 | **Unskip Auth API Tests** | 2 days | Medium — test gap closure |
| 15 | **Audit Logging Implementation** | 3 days | Medium — compliance, debugging |

### 🌟 Nice To Have (Post-Beta)

| # | Item | Effort | Business Impact |
|---|------|:------:|:---------------:|
| 16 | **Monitoring (Prometheus/Grafana)** | 2 weeks | Medium — operational visibility |
| 17 | **Log Aggregation (Loki/ELK)** | 1 week | Low — operational improvement |
| 18 | **Caching Layer (Redis)** | 1 week | Medium — performance |
| 19 | **Content Delivery Network** | 3 days | Low — file upload scaling |
| 20 | **Horizontal Scaling Config** | 2 weeks | Medium — growth readiness |
| 21 | **Resource-Level Permissions** | 1 week | Medium — student data isolation |
| 22 | **Refresh Token Reuse Detection** | 2 days | Low — security hardening |
| 23 | **Prompt A/B Testing** | 2 weeks | Low — AI optimization |
| 24 | **Remove Technical Debt Items** | 1 week | Low — code quality |

---

## Effort-Impact Matrix

```
                    High Impact
                        │
        Must Do         │    Must Do
        (9, 10)         │    (1-7)
                        │
    Low Effort ─────────┼─────────── High Effort
                        │
        Quick Wins      │    Strategic
        (11, 13)        │    (8, 12, 16, 18, 20)
                        │
                    Low Impact
```

### Quick Wins (Low Effort, High Impact)
1. Production secret management (1 day)
2. Rate limiting (2 days)
3. Fix mock fallback warning (1 hour)
4. Fix asymmetric endpoint naming (1 hour)
5. HTTPS termination (1 day)

### Strategic Investments (High Effort, High Impact)
1. Frontend (3-6 months)
2. E2E test infrastructure (1 week)
3. Async task queue (2 weeks)
4. Monitoring infrastructure (2 weeks)
5. Horizontal scaling (2 weeks)

---

## Recommended Phased Roadmap

### Phase 1 — Production Hardening (2 weeks)
1. Production secret management
2. Rate limiting
3. HTTPS termination
4. Database backups
5. Email service integration
6. Fix mock fallback warning
7. Fix asymmetric endpoint naming
8. CI/CD pipeline (lint + test on PR)

### Phase 2 — Quality Assurance (2 weeks)
1. E2E test infrastructure
2. Unskip auth API tests
3. Guardrail integration into teaching flow
4. Real Gemini API testing + prompt refinement
5. Async task queue for AI calls

### Phase 3 — Features Complete (4 weeks)
1. Frontend MVP begins (ongoing)
2. Audit logging implementation
3. Resource-level permission checks
4. Refresh token reuse detection
5. Monitoring with external metrics

### Phase 4 — Scale & Optimize (Ongoing)
1. Frontend MVP complete
2. Caching layer
3. Content delivery network
4. Horizontal scaling
5. Prompt A/B testing
6. Performance optimization
