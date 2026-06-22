# Production Readiness Audit

## Readiness Score: **32/100**

| Category | Score | Reasoning |
|----------|:-----:|-----------|
| Logging | 6/10 | Structured JSON logging for production; dev-mode human-readable; request_id in all logs; SQLAlchemy/httpx suppressed |
| Monitoring | 3/10 | In-memory metrics collector (lost on restart); no external monitoring integration; no alerting |
| Error Handling | 7/10 | Consistent AppException hierarchy; global exception handlers; unhandled exception fallback |
| API Design | 8/10 | Consistent response format; proper HTTP status codes; Pydantic validation; OpenAPI docs |
| Auth Security | 5/10 | JWT with refresh tokens; password hashing; but default secret key, no rate limiting |
| Database | 6/10 | Connection pool with health check; migrations; but no connection retry logic |
| Docker | 5/10 | Multi-stage Dockerfile; non-root user; but no docker-compose for app itself (DB only) |
| Health Checks | 4/10 | Simple health endpoint (DB ping); no dependency checks, no readiness/liveness probes |
| Backups | 0/10 | No backup strategy for PostgreSQL |
| AI Guardrails | 4/10 | Guardrails implemented but not used in production teaching flow; Gemini falls back to mock silently |
| CI/CD | 0/10 | No continuous integration or deployment |
| Documentation | 5/10 | Architecture, API, DB docs exist; no operations runbook, no deployment guide |
| Scalability | 3/10 | Monolithic; no caching; no async task queue for AI calls (blocking within request) |
| Compliance | 0/10 | No GDPR, FERPA, or data retention policies implemented |

---

## Detailed Assessment

### 1. Logging

**Current State:**
- Structured JSON logging in production (`python-json-logger`)
- Human-readable formatting in development
- `request_id` context variable injected via `RequestIDFilter`
- SQLAlchemy engine logs suppressed to WARNING
- HTTPX logs suppressed to WARNING

**Gaps:**
- No log rotation configured
- No log aggregation (ELK, Loki, Datadog)
- No separate error log stream
- No PII scrubbing in logs
- No structured logging for AI model calls (token usage, latency logged via in-memory metrics only)

### 2. Monitoring

**Current State:**
- `MetricsCollector` class collects AI request metrics, graph execution metrics, endpoint metrics
- In-memory storage with 10,000-entry cap per metric type
- Middleware records endpoint duration and status codes

**Gaps:**
- All metrics are in-memory → lost on restart
- No external metrics provider (Prometheus, OpenTelemetry, Datadog)
- No alerting rules
- no `/metrics` endpoint exposing metrics to scraping tools
- No health check for AI service (Gemini API availability)
- No error budget tracking

### 3. Error Handling

**Current State:**
- `AppException` hierarchy with status_code, code, message, details
- Global exception handler returns consistent `{status: "error", error: {...}}` format
- Unhandled exception handler returns 500 with generic message and logs full traceback

**Gaps:**
- Error details may leak internal implementation info in dev mode
- No retry logic for transient failures (database connection, API calls)
- No circuit breaker for external dependencies (Gemini API)

### 4. Deployment

**Current State:**
- `Dockerfile` — Multi-stage build (builder → runtime), Python 3.12-slim, non-root user
- `docker-compose.yml` — PostgreSQL 16 with persistent volume and healthcheck
- `Makefile` — dev, test, lint, format, docker commands
- `uvicorn` as ASGI server

**Gaps:**
- No docker-compose service for the app itself (only PostgreSQL)
- No environment-specific configurations (dev/staging/production)
- No migration automation in Docker entrypoint
- No CI/CD pipeline (GitHub Actions, GitLab CI)
- No container registry
- No orchestration config (Kubernetes manifests absent)

### 5. Health Checks

**Current State:**
- `GET /api/v1/health` returns `{status: "ok"|"degraded", version, database: "connected"|"disconnected"}`

**Gaps:**
- No readiness/liveness probe differentiation
- No dependency health (Gemini API, Qdrant if configured)
- No deep health check (DB connection pool utilization, memory usage)
- Not used in Dockerfile (no HEALTHCHECK instruction)

### 6. Database

**Current State:**
- Connection pool: pool_size=5, max_overflow=10
- `pool_pre_ping=True` — validates connections before use
- `pool_recycle=3600` — recycles connections hourly
- Alembic for schema migrations
- 4 migration files covering full schema evolution

**Gaps:**
- No database backup strategy (automated pg_dump)
- No connection retry on startup (app crashes if DB unavailable)
- No read replicas for scaling
- No query performance monitoring
- No migration rollback plan

### 7. AI System

**Current State:**
- `GeminiService` with `generate()` and `generate_json()` methods
- Guardrails: empty detection, JSON validation, hallucination prevention, fallback responses
- In-memory metrics for AI latency, token usage, error rates

**Gaps:**
- **Gemini silently falls back to mock** when API key is missing (`_mock_gemini_response`) with no warning
- Guardrails are NOT used in the production teaching flow — they're only used in the evaluation harness
- No retry/backoff for Gemini API failures
- No cost tracking per session/user
- No A/B testing framework for prompt variations
- No content moderation for generated output

### 8. Scalability

**Current State:**
- Stateless application (session state stored in DB)
- Async endpoints (non-blocking I/O)

**Gaps:**
- AI calls block the request thread (no background task queue — Celery/Redis)
- No caching layer (Redis/Memcached for curriculum data)
- No horizontal scaling configuration
- DB connection pool may become bottleneck under load
- No CDN for static content
- No database read replicas

### 9. Security

See [SECURITY_AUDIT.md](./SECURITY_AUDIT.md) for detailed assessment.

Key production concerns:
- Default JWT secret key
- No rate limiting
- No HTTPS
- Missing production secret management

### 10. CI/CD

**Current State:** Nonexistent.

**Required:**
- GitHub Actions (or equivalent) for:
  - Lint (ruff) on PR
  - Test suite (pytest) on PR
  - Docker build + push on merge to main
  - Migration validation (alembic check)
  - Security scanning (bandit, safety)

---

## Production Go-Live Checklist

### Phase 1 — Minimum Viable Production (Week 1-2)
- [ ] Set strong `SECRET_KEY` and `GEMINI_API_KEY`
- [ ] Enable HTTPS (reverse proxy: nginx/Caddy)
- [ ] Add rate limiting middleware
- [ ] Add docker-compose service for app
- [ ] Set up CI (lint + test)
- [ ] Fix Gemini mock fallback to log warning
- [ ] Add database backup automation

### Phase 2 — Monitoring & Reliability (Week 3-4)
- [ ] Switch to external metrics provider (Prometheus)
- [ ] Add liveness/readiness probes
- [ ] Implement retry logic for Gemini API
- [ ] Add AI cost tracking
- [ ] Set up log aggregation
- [ ] Add migration automation to deployment

### Phase 3 — Hardening (Month 2)
- [ ] Enable guardrails in production teaching flow
- [ ] Add async task queue for AI calls
- [ ] Implement refresh token reuse detection
- [ ] Performance benchmark + optimize DB queries
- [ ] Security audit + penetration testing
- [ ] Add health check for all dependencies

### Phase 4 — Scale (Month 3+)
- [ ] Horizontal scaling configuration
- [ ] Caching layer (Redis)
- [ ] Database read replicas
- [ ] CDN for file uploads
- [ ] A/B testing for AI prompts
