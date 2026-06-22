# Security Audit

## Authentication

### JWT Implementation
- **Library:** `python-jose` with `cryptography`
- **Algorithm:** HS256 (HMAC-SHA256)
- **Access Token Expiry:** 30 minutes (configurable)
- **Refresh Token Expiry:** 7 days (configurable)
- **Token Type Check:** Access tokens have `"type": "access"`, refresh tokens have `"type": "refresh"` with `"jti"` claim
- **Secret Key:** Configurable via `SECRET_KEY` env var; default is `"change-me-in-production-use-a-real-secret"`

### JWT Payload (Access Token)
```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "role": "student",
  "type": "access",
  "iat": <timestamp>,
  "exp": <timestamp>
}
```

### Token Validation Flow
```
Authorization: Bearer <token>
  → get_token_from_header() — validates "Bearer" prefix
  → get_current_user() — decodes token, checks type=="access", extracts sub
  → user_repo.get(user_id) — loads User from DB
  → get_current_active_user() — checks User.is_active
```

### Refresh Token Rotation
- Refresh tokens are stored as SHA-256 hashes in `refresh_tokens` table
- On refresh: old token is revoked (`revoked_at` set), new token issued
- No refresh token reuse detection (if a stolen token is used after legitimate rotation, the original remains revoked)

---

## Password Security

### Hashing
- **Algorithm:** bcrypt via `passlib` with `CryptContext`
- **Bcrypt Version:** `>=4.1.0,<5.0.0`
- **Hash Format:** `$2b$...`

### Password Strength Validation
```
^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$
```
- Minimum 8 characters
- At least 1 lowercase letter
- At least 1 uppercase letter
- At least 1 digit
- **Missing:** Special character requirement
- **Missing:** Common password dictionary check

### Password Reset
- Token stored as SHA-256 hash in `password_reset_tokens` table
- Token expires after 1 hour
- **Critical Missing:** No email sending configured — reset tokens are generated and stored but never delivered to users

---

## Authorization (RBAC)

### Roles
| Role | Enum Value | Permissions |
|------|-----------|-------------|
| Admin | `admin` | Full access to all endpoints, content management |
| Student | `student` | Teaching sessions, progress, own data |
| Parent | `parent` | Read-only access to linked students' data |

### Role Checker
```python
def require_roles(*allowed_roles: UserRole):
    # Returns a dependency that checks current_user.role
```

### Authorization Coverage
| Auth Level | Count | Endpoints |
|------------|:-----:|-----------|
| Public | 7 | register, login, refresh, forgot-password, reset-password, health, root |
| Authenticated | 55 | All student-facing and parent endpoints |
| Admin-only | 28 | Curriculum CRUD, knowledge graph, content ingestion |

### Issues
1. **No resource-level permissions** — Any authenticated student can access `/progress/`, `/mastery/`, `/sessions/` without verifying they own the resource. The `get_current_active_user` dependency only checks authentication, not ownership.
2. **Ownership checks are inconsistent** — Some services check `current_user.id == resource.user_id` manually (e.g., `ContentIngestionService`), others rely entirely on RBAC.
3. **Parent access verification exists** but is in the service layer, not as a reusable dependency.

---

## Risk Assessment

| # | Risk | Severity | Impact | Existing Mitigation |
|---|------|----------|--------|-------------------|
| 1 | **Default secret key in production** | **Critical** | Full JWT forgery | None — app starts with default key |
| 2 | **No email sending for password reset** | **High** | Password reset is non-functional | Token generation works; delivery is not implemented |
| 3 | **No rate limiting** | **High** | Brute force login, DoS | None |
| 4 | **Logging may expose secrets** | **Medium** | Error messages include exception strings that may contain sensitive data | `ValidationException` messages contain field names; no PII policy |
| 5 | **No CSRF protection** | **Medium** | Not applicable (API-only, no browser session cookies) | Set-Cookie not used; all auth via Bearer header |
| 6 | **No refresh token reuse detection** | **Medium** | Stolen refresh token can be used once before rotation | Single-use rotation limits window |
| 7 | **Inconsistent ownership checks** | **Medium** | Students may access other students' data | Role checks exist but ownership not enforced everywhere |
| 8 | **No CORS restriction in dev** | **Low** | CORS allows all origins by default in dev | Configurable via `CORS_ORIGINS` env var |
| 9 | **Weak password policy** | **Low** | Password only requires 8 chars, upper, lower, digit | No special character or dictionary check |
| 10 | **Qdrant default connection** | **Low** | If Qdrant is not deployed, connection timeout on startup | Qdrant connection is optional with graceful fallback |
| 11 | **Audit logging not used** | **Low** | No audit trail for sensitive operations | Table exists but no service writes to it |

---

## Production Security Concerns

### Critical
1. **Secret key management** — Default key is hardcoded in source code; no secret rotation
2. **No HTTPS** — No TLS configuration in the application or Docker setup

### High
3. **API exposed without rate limiting** — All endpoints can be hammered
4. **No input sanitization on file uploads** — Content ingestion accepts arbitrary filenames (though UUID-prefixed on disk)
5. **Gemini API key in plaintext env var** — Not encrypted at rest on the server

### Medium
6. **No request size limits** — FastAPI default 1MB limit applies; no file size limit in content upload beyond app-level check
7. **`SQLALCHEMY_WARN_20` not set** — SQLAlchemy 2.0 deprecation warnings not explicitly configured
8. **Docker runs as non-root user** ✅ — Good practice already implemented

---

## Security Checklist

| Control | Status | Notes |
|---------|--------|-------|
| Password hashing (bcrypt) | ✅ Implemented | Via passlib |
| JWT with expiry | ✅ Implemented | Access + refresh tokens |
| Token validation | ✅ Implemented | Type check, expiry, user check |
| Active user check | ✅ Implemented | `get_current_active_user` |
| RBAC role checks | ✅ Implemented | `require_roles()` decorator |
| CORS configuration | ✅ Implemented | Configurable origins |
| Non-root Docker user | ✅ Implemented | `USER app` in Dockerfile |
| Email/password validation | ✅ Partial | Format check exists, no delivery |
| Secret management | ❌ Missing | Default key in source code |
| Rate limiting | ❌ Missing | No protection |
| CSRF protection | N/A | API-only, token-based auth |
| Audit logging | ❌ Not Implemented | Table exists, no service usage |
| HTTPS/TLS | ❌ Missing | No SSL termination |
| Input size limits | ❌ Missing | File size only in app code |
| Ownership checks | ❌ Inconsistent | Manual checks in some services |
| SQL injection protection | ✅ ORM | SQLAlchemy parameterized queries |
| XSS protection | ✅ API-only | No HTML rendering |
| Request validation | ✅ Pydantic | All inputs validated |
| Dependency vulnerability scanning | ❌ Missing | No Snyk/Dependabot |
