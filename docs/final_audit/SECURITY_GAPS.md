# SECURITY GAPS — Acuity LMS AI

**Generated:** 2026-06-25
**Severity:** CRITICAL = immediate exploitation risk, HIGH = significant vulnerability

---

## CRITICAL

### S1: Default JWT Secret in Source Code

**File:** `Backend/app/config.py:37`
**Issue:** `secret_key` defaults to `"change-me-in-production-use-a-real-secret"`. If any deployment fails to set `SECRET_KEY` in env, JWT tokens can be forged trivially.

**Risk:** Token forgery → complete account takeover → privilege escalation.

**Evidence:** The placeholder string is publicly known and searchable in source control.

**Fix:** Either remove the default (required field) or add a startup assertion in production:
```python
if self.environment != "development" and "change-me" in self.secret_key:
    raise RuntimeError("SECRET_KEY must be changed for production!")
```

---

### S2: SQL Query Logging Leaks Data by Default

**File:** `Backend/app/infrastructure/database.py:37`
**Issue:** `echo=settings.debug` — with `debug=True` as default in `config.py:21`, all SQL statements including bind parameters are logged to stdout.

**Risk:** In staging/production with default config, SQL and data values (potentially including PII, hashed passwords, tokens) are leaked to logs.

**Evidence:** `config.py:21` sets `debug: bool = True`. No environment override required to trigger this.

**Fix:** Change `debug` default to `False`. Set `DEBUG=true` only in `.env.development`.

---

### S3: Missing Authentication Guards on Frontend Routes

**File:** `acuity-frontend/src/router/index.tsx:32-63`
**Issue:** No auth or role-based guards on any route. Unauthenticated users can access all pages.

**Risk:** Unauthorized access to student/parent/admin data. Viewing of PII, course content, progress data.

**Fix:** Implement route guard components that check `authStore.isAuthenticated` and `authStore.currentUser.role`.

---

## HIGH

### S4: No Rate Limiting on Any Endpoint

**Files:** `Backend/app/auth/router.py:43,67,84,102,115,130`
**Issue:** No rate limiting on login, registration, password reset, or any other endpoint. Constants `DEFAULT_RATE_LIMIT` and `LOGIN_RATE_LIMIT` exist in `constants.py` but are unused.

**Risk:** Brute-force password attacks. Denial of service. Password reset token brute-force.

**Fix:** Implement rate limiting middleware (e.g., slowapi) or per-endpoint dependencies.

---

### S5: Email Address Exposed in JWT Access Token

**File:** `Backend/app/security/jwt.py:16`
**Issue:** `"email": email` is embedded in the JWT payload. If a token is leaked (e.g., in logs, XSS), the user's email address is exposed.

**Risk:** Unnecessary PII exposure. The `sub` claim (user UUID) is sufficient for authorization.

**Fix:** Remove `"email"` from the access token payload.

---

### S6: LoginRequest Schema Lacks Validation

**File:** `Backend/app/auth/schemas.py:17-19`
**Issue:** `LoginRequest` has no constraints. Empty strings, extremely long payloads, injection-style inputs are accepted at the schema level.

**Risk:** Potential for abuse via oversized inputs (memory exhaustion), though DB/crypto layer provides some protection.

**Fix:** Add `min_length`, `max_length`, regex validation consistent with `RegisterRequest`.

---

### S7: Audit Logging Entirely Missing

**File:** `Backend/app/audit/models.py` (model exists), no callers anywhere
**Issue:** No CRUD operation, auth event, or AI interaction produces an audit record. No traceability.

**Risk:** Cannot detect or investigate security incidents. Non-compliance with data protection regulations (GDPR, SOC2, etc.).

**Fix:** Write a middleware or service decorator that creates `AuditLog` records for all mutating operations.

---

### S8: Unvalidated AI Output Reaches Users

**File:** `Backend/app/ai/guardrails/service.py` (never called)
**Issue:** `GuardrailService` is well-implemented but never invoked. All LLM output (teaching content, questions, evaluations, diagnoses) flows directly to the student.

**Risk:** Students may receive harmful, inappropriate, or hallucinated content. Empty responses, disclaimers, or fabricated information.

**Fix:** Wire guardrails into every graph node's LLM output path.

---

### S9: CORS Allows All Origins in Development

**File:** `Backend/app/main.py:61-62`
**Issue:** `allow_methods=["*"]` and `allow_headers=["*"]`. In production, this should be restricted.

**Risk:** If deployed with dev config, any website can make cross-origin requests to the API.

**Fix:** Set explicit allow lists for methods and headers in production.

---

### S10: No Security Headers Middleware

**File:** `Backend/app/main.py` (missing)
**Issue:** No helmet-style headers: `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`, `Content-Security-Policy`.

**Risk:** Vulnerable to clickjacking, MIME-type sniffing, XSS via inline scripts.

**Fix:** Add middleware to set security headers on all responses.

---

## MEDIUM

### S11: Password Policy Lacks Special Character Requirement

**File:** `Backend/app/security/password.py:11`
**Issue:** Regex requires 8+ chars, lowercase, uppercase, digit — but no special character. `Password1` passes validation.

**Risk:** Reduced password entropy.

**Fix:** Add `(?=.*[!@#$%^&*(),.?":{}|<>])` to require at least one special character.

---

### S12: No Account Lockout

**File:** `Backend/app/auth/` (entire module)
**Issue:** No tracking of failed login attempts. No lockout after N failures.

**Risk:** Unlimited brute-force attempts on user passwords.

**Fix:** Add `failed_login_attempts` column to `User` model and lock account after threshold.

---

### S13: Password Reset Token Not Revocable

**File:** `Backend/app/auth/models.py:24-35`
**Issue:** `PasswordResetToken` has `expires_at` and `used_at` but no `revoked_at`. Token cannot be proactively invalidated.

**Risk:** If a user suspects their reset email was intercepted, there is no way to revoke the token.

**Fix:** Add `revoked_at` column and check it in `get_valid_by_hash`.

---

### S14: .env.example Missing Security Variables

**File:** `Backend/.env.example`
**Issue:** Missing `SECRET_KEY` entry. New deployments following the template get the insecure default.

**Risk:** Accidental production deployment with default JWT secret.

**Fix:** Add `SECRET_KEY=change-me-in-production` with a comment explaining it must be changed.

---

### S15: Same JWT Secret for Access and Refresh Tokens

**File:** `Backend/app/security/jwt.py:12-34`
**Issue:** Both token types use the same secret and algorithm. Compromising the secret compromises both token types.

**Risk:** If secret is leaked, both access and refresh tokens can be forged.

**Fix:** Use separate secrets or asymmetric keys (RS256) for each token type.

---

### S16: Docs/Redoc May Be Enabled in Production

**File:** `Backend/app/main.py:48-49`
**Issue:** Docs disabled only when `settings.is_development` is `False`. An env misconfiguration (missing `ENVIRONMENT=production`) leaves docs open.

**Risk:** API schema and endpoints exposed to anyone.

**Fix:** Use an explicit `ENABLE_DOCS` env var defaulting to `False`.

---

## LOW

### S17: Search Input in Admin Page Is Decorative

**File:** `acuity-frontend/src/pages/admin/StudentsPage.tsx:29-31`
**Issue:** `onChange` is empty. User types but nothing happens.

**Risk:** No direct security risk, but violates user trust.

---

### S18: Repository.update() Silently Ignores Misspelled Field Names

**File:** `Backend/app/common/repository.py:53`
**Issue:** `if hasattr(instance, key): setattr(...)` — a typo like `"emial"` instead of `"email"` silently succeeds with no effect.

**Risk:** Data silently fails to update without any error. Not a direct security issue but can cause data integrity problems.

---

## SECURITY SUMMARY

| Severity | Count | Key Risks |
|----------|:-----:|-----------|
| CRITICAL | 3 | JWT secret, SQL leak, no frontend guards |
| HIGH | 7 | No rate limiting, email in JWT, no audit, unvalidated AI, permissive CORS, no security headers, missing validators |
| MEDIUM | 6 | Password policy, account lockout, token revocation, .env.example, shared secrets, docs exposure |
| LOW | 2 | Decorative search, silent update |
| **Total** | **18** | |

---

## IMMEDIATE ACTIONS (Production Blockers)

1. **Change `SECRET_KEY` default** — add startup assertion or make required
2. **Change `debug` default to `False`** — prevent SQL/data leaks
3. **Add frontend route guards** — prevent unauthorized access
4. **Add rate limiting** on auth endpoints
5. **Remove email from JWT payload**
6. **Add audit logging middleware**
7. **Wire guardrails into AI graph**
