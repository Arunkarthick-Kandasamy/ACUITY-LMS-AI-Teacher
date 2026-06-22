# Production Gaps

> Only gaps supported by evidence from source code. No speculation about future requirements.

---

## 1. No Frontend Exists

| | |
|---|---|
| **Gap** | The entire application is a backend-only API. No user interface exists. |
| **Why it matters** | Product cannot be used without external API clients. No student, teacher, or parent can interact with the system. |
| **Evidence** | No frontend directory exists. No `package.json`, HTML, JS/TS, or UI framework files anywhere in project. CORS config in `app/config.py:32` allows `localhost:3000` and `localhost:5173` (React/Vite dev servers) suggesting frontend was planned but not started. |

---

## 2. Default JWT Secret in Source Code

| | |
|---|---|
| **Gap** | `app/config.py:37` contains a hard-coded default secret key: `"change-me-in-production-use-a-real-secret"` |
| **Why it matters** | If deployed without changing this default, anyone can forge JWT tokens and gain unauthorized access to any account. Critical security vulnerability. |
| **Evidence** | `app/config.py:37`: `secret_key: Annotated[str, Field(default="change-me-in-production-use-a-real-secret")]` |

---

## 3. No Rate Limiting

| | |
|---|---|
| **Gap** | No rate limiting middleware or dependency exists anywhere in the application. |
| **Why it matters** | All endpoints (including AI-powered `/teacher/teach` which calls Gemini API) are unprotected against abuse. An attacker could: (a) brute-force passwords, (b) exhaust AI API budget, (c) degrade database performance. |
| **Evidence** | `pyproject.toml` — No `slowapi` or rate-limiting dependency. `app/main.py` — No rate-limiting middleware registered. No `X-RateLimit-*` headers in any response. |

---

## 4. No Email Delivery

| | |
|---|---|
| **Gap** | Password reset flow creates a token in the database but never sends an email to the user. |
| **Why it matters** | The forgot-password and reset-password features are non-functional without email delivery. Users cannot recover their accounts. |
| **Evidence** | `app/auth/service.py` — `forgot_password()` calls `_create_reset_token()` and stores it, but no SMTP/email API call follows. `app/config.py` — No SMTP configuration fields. `pyproject.toml` — No email library dependency (no `smtplib` usage either in source). |

---

## 5. No CI/CD Pipeline

| | |
|---|---|
| **Gap** | No automated build, test, or deployment pipeline exists. |
| **Why it matters** | Every deployment must be done manually. No automated quality gates. Risk of human error in production deployments. |
| **Evidence** | No `.github/workflows/` directory. No `Jenkinsfile`, `.gitlab-ci.yml`, or any CI config file found. `pyproject.toml:35-37` — pytest config exists but no automation. |

---

## 6. No Production Monitoring

| | |
|---|---|
| **Gap** | Metrics are purely in-memory with no persistence or alerting. |
| **Why it matters** | No way to detect production issues (error spikes, performance degradation, AI API failures) without manual log inspection. |
| **Evidence** | `app/monitoring/metrics.py` — All metrics are in-memory only; lost on process restart. No Prometheus metrics endpoint. No Grafana dashboards. No health check alerting mechanism. |

---

## 7. No Database Backups

| | |
|---|---|
| **Gap** | No automated database backup mechanism exists. |
| **Why it matters** | Data loss in production would be permanent. No recovery path for corrupted or accidentally deleted data. |
| **Evidence** | No backup scripts found. `docker-compose.yml` — PostgreSQL has no backup volume or cron configuration. No database snapshot/restore endpoints. |

---

## 8. Guardrails Not Integrated into Production Flow

| | |
|---|---|
| **Gap** | GuardrailService is fully implemented but never called from any production code path. |
| **Why it matters** | AI-generated content (teaching, evaluation, diagnosis) is not validated before being returned to students. Malformed or hallucinated content can reach users. |
| **Evidence** | `app/ai/guardrails/service.py` — Full implementation. Zero calls in `app/ai/nodes/` or `app/ai/router.py`. Zero tests in `tests/`. |

---

## 9. Missing Infrastructure Services

| | |
|---|---|
| **Gap** | Redis and Qdrant are documented as part of the architecture but are not deployable. |
| **Why it matters** | Memory retrieval falls back to mock. LLM response caching is absent. Semantic search is non-functional. |
| **Evidence** | `docker-compose.yml` — No Redis or Qdrant service defined. `pyproject.toml:31-33` — Qdrant is optional (`[project.optional-dependencies]`). `app/ai/memory/retrieval.py:213` — Falls back to mock on Qdrant connection failure. |

---

## 10. AI Calls Block HTTP Handler

| | |
|---|---|
| **Gap** | AI graph execution is a blocking `await` in the HTTP request handler. |
| **Why it matters** | Long-running AI calls (potentially 5-30 seconds for Gemini) will hold the HTTP worker thread, reducing throughput and potentially timing out. |
| **Evidence** | `app/ai/router.py:170` — `await teacher_graph.ainvoke(initial_state)` — direct blocking call in HTTP handler. No Celery, Redis Queue, or background task infrastructure. |

---

## 11. Real Gemini API Not Tested

| | |
|---|---|
| **Gap** | All AI tests run against mock Gemini responses. |
| **Why it matters** | Real API behavior (latency, token limits, output format consistency, error responses) is completely untested. |
| **Evidence** | `app/config.py:46` — `gemini_api_key` defaults to `""`. `app/ai/services/gemini.py:39` — falls back to mock when API key is missing. All 21 teacher graph tests use `unittest.mock.patch`. All 5 integration tests use mock Gemini. |

---

## Secondary Gaps

| Gap | Evidence |
|-----|----------|
| No HTTPS termination | `app/config.py:24` — No TLS/SSL settings. `Dockerfile:24` — uvicorn runs without `--ssl-keyfile`. |
| No log aggregation | `app/infrastructure/logging.py` — Only stdout (uvicorn default). No log file rotation. No log shipping. |
| No horizontal scaling | No session affinity. No distributed cache. `docker-compose.yml` — Single service only. |
| No Docker HEALTHCHECK | `Dockerfile` — No `HEALTHCHECK` instruction. App container not in `docker-compose.yml`. |
| Non-root user misconfigured | `Dockerfile` — Non-root user created but `pip install` runs before user switch. |
| AuditLog table never written to | `app/audit/models.py:11` — Table defined. Zero callers in any service or middleware. |
| Health check is incomplete | `app/api/routes/health.py:13` — Only checks DB connectivity. Missing: Gemini, Qdrant, disk space. |
