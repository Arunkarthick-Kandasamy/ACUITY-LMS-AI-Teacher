# API Contracts — AI-Native Personalized Schooling Platform (MVP)

## Conventions

| Convention | Standard |
|---|---|
| Base URL | `/api/v1` |
| Auth | `Authorization: Bearer <JWT>` |
| Request IDs | All UUIDs — `{id}` in path means UUID |
| Pagination | `?page=1&per_page=20` — returned in `meta` |
| Timestamps | ISO 8601 with UTC (`2026-06-20T14:30:00Z`) |
| Response envelope | `{ "status": "success", "data": {...}, "meta": {...} }` |
| Error envelope | `{ "status": "error", "error": { "code": "...", "message": "...", "details": [...] } }` |

---

## 1. Authentication

### POST /auth/register

Register a new user.

**Auth:** Public

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecureP@ss123",
  "full_name": "Jane Doe",
  "role": "student"
}
```

**Validation Rules:**
| Field | Rule |
|---|---|
| email | Valid email format, max 255 chars, unique in system |
| password | Min 8 chars, at least 1 uppercase, 1 lowercase, 1 digit |
| full_name | Required, max 150 chars |
| role | Must be one of: `admin`, `student`, `parent` |

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "user_id": "uuid",
    "email": "user@example.com",
    "full_name": "Jane Doe",
    "role": "student",
    "created_at": "2026-06-20T14:30:00Z"
  }
}
```

---

### POST /auth/login

Authenticate and receive tokens.

**Auth:** Public

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecureP@ss123"
}
```

**Validation Rules:**
| Field | Rule |
|---|---|
| email | Valid email format |
| password | Required |

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "dGhpcyBpcyBhIHJlZnJl...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "user_id": "uuid",
      "email": "user@example.com",
      "full_name": "Jane Doe",
      "role": "student"
    }
  }
}
```

---

### POST /auth/refresh

Exchange a refresh token for a new access token.

**Auth:** Public (with valid refresh token)

**Request Body:**
```json
{
  "refresh_token": "dGhpcyBpcyBhIHJlZnJl..."
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "dGhpcyBpcyBhIHJlZnJl...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

---

### POST /auth/logout

Invalidate the current session.

**Auth:** Any authenticated user

**Request Body:** (none)

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "message": "Logged out successfully"
  }
}
```

---

### POST /auth/forgot-password

Send password reset email.

**Auth:** Public

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Validation Rules:**
| Field | Rule |
|---|---|
| email | Valid email format |

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "message": "If the email exists, a reset link has been sent"
  }
}
```

---

### POST /auth/reset-password

Reset password using token from email.

**Auth:** Public

**Request Body:**
```json
{
  "token": "reset-token-from-email",
  "new_password": "NewSecureP@ss456"
}
```

**Validation Rules:**
| Field | Rule |
|---|---|
| token | Required, valid non-expired reset token |
| new_password | Min 8 chars, at least 1 uppercase, 1 lowercase, 1 digit |

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "message": "Password reset successfully"
  }
}
```

---

## 2. Admin

### GET /admin/users

List all users with optional filters.

**Auth:** Admin

**Query Parameters:**
| Param | Type | Description |
|---|---|---|
| `role` | `user_role` | Filter by role |
| `is_active` | `boolean` | Filter by active status |
| `search` | `string` | Search by name or email |
| `page` | `integer` | Default: 1 |
| `per_page` | `integer` | Default: 20, Max: 100 |

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "user_id": "uuid",
      "email": "user@example.com",
      "full_name": "Jane Doe",
      "role": "student",
      "is_active": true,
      "created_at": "2026-06-20T14:30:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 152,
    "total_pages": 8
  }
}
```

---

### GET /admin/users/{user_id}

Get detailed user information.

**Auth:** Admin

**Response (200) — Student:**
```json
{
  "status": "success",
  "data": {
    "user_id": "uuid",
    "email": "student@example.com",
    "full_name": "Jane Doe",
    "role": "student",
    "is_active": true,
    "profile": {
      "grade_level": "Grade 10",
      "avg_session_duration_minutes": 28,
      "current_streak_days": 5
    },
    "enrollments": [
      {
        "enrollment_id": "uuid",
        "course_title": "Algebra I",
        "status": "active",
        "progress_pct": 45.2,
        "enrolled_at": "2026-05-01T10:00:00Z"
      }
    ],
    "created_at": "2026-06-20T14:30:00Z"
  }
}
```

---

### PATCH /admin/users/{user_id}/status

Activate or deactivate a user.

**Auth:** Admin

**Request Body:**
```json
{
  "is_active": false
}
```

**Validation Rules:**
| Field | Rule |
|---|---|
| is_active | Required, boolean |

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "user_id": "uuid",
    "is_active": false,
    "updated_at": "2026-06-20T15:00:00Z"
  }
}
```

---

### GET /admin/dashboard

System-wide overview statistics.

**Auth:** Admin

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "total_users": 250,
    "total_students": 180,
    "total_parents": 60,
    "total_admins": 10,
    "total_courses": 12,
    "active_enrollments": 320,
    "active_sessions_today": 45,
    "completion_rate_avg": 0.68
  }
}
```

---

### GET /admin/courses/{course_id}/analytics

Per-course analytics for admins.

**Auth:** Admin

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "course_id": "uuid",
    "course_title": "Algebra I",
    "total_enrolled": 85,
    "active_students": 62,
    "completion_rate": 0.42,
    "avg_mastery": 0.71,
    "avg_session_minutes": 32,
    "concept_mastery_breakdown": [
      {"concept_title": "Linear Equations", "avg_mastery": 0.85, "total_attempts": 340},
      {"concept_title": "Quadratic Functions", "avg_mastery": 0.62, "total_attempts": 210}
    ],
    "common_misconceptions": [
      {"concept_title": "Linear Equations", "misconception": "Distributive property error", "student_count": 18}
    ]
  }
}
```

---

## 3. Curriculum

### POST /courses

Create a new course.

**Auth:** Admin

**Request Body:**
```json
{
  "code": "MATH-ALG-101",
  "title": "Algebra I",
  "description": "Foundational algebra covering linear equations, quadratics, and systems.",
  "total_duration_hours": 40,
  "default_deadline_days": 90
}
```

**Validation Rules:**
| Field | Rule |
|---|---|
| code | Required, max 50 chars, unique |
| title | Required, max 200 chars |
| description | Optional |
| total_duration_hours | Required, integer >= 1 |
| default_deadline_days | Required, integer >= 1 |

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "course_id": "uuid",
    "code": "MATH-ALG-101",
    "title": "Algebra I",
    "description": "Foundational algebra covering linear equations, quadratics, and systems.",
    "total_duration_hours": 40,
    "default_deadline_days": 90,
    "is_published": false,
    "created_by": "uuid",
    "created_at": "2026-06-20T14:30:00Z"
  }
}
```

---

### GET /courses

List all courses.

**Auth:** Any authenticated user

**Query Parameters:**
| Param | Type | Description |
|---|---|---|
| `is_published` | `boolean` | Filter by published status |
| `search` | `string` | Search by title or code |
| `page` | `integer` | Default: 1 |
| `per_page` | `integer` | Default: 20 |

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "course_id": "uuid",
      "code": "MATH-ALG-101",
      "title": "Algebra I",
      "description": "Foundational algebra covering linear equations, quadratics, and systems.",
      "total_duration_hours": 40,
      "default_deadline_days": 90,
      "is_published": true,
      "module_count": 6,
      "lesson_count": 24,
      "created_at": "2026-06-20T14:30:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 12,
    "total_pages": 1
  }
}
```

---

### GET /courses/{course_id}

Get full course details with module tree.

**Auth:** Any authenticated user

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "course_id": "uuid",
    "code": "MATH-ALG-101",
    "title": "Algebra I",
    "description": "Foundational algebra covering linear equations, quadratics, and systems.",
    "total_duration_hours": 40,
    "default_deadline_days": 90,
    "is_published": true,
    "modules": [
      {
        "module_id": "uuid",
        "title": "Linear Equations",
        "order_index": 1,
        "lessons": [
          {
            "lesson_id": "uuid",
            "title": "Introduction to Variables",
            "order_index": 1,
            "estimated_duration_minutes": 30,
            "concept_count": 3
          }
        ]
      }
    ],
    "created_at": "2026-06-20T14:30:00Z"
  }
}
```

---

### PUT /courses/{course_id}

Update course details.

**Auth:** Admin

**Request Body:**
```json
{
  "title": "Algebra I (Updated)",
  "description": "Updated description.",
  "total_duration_hours": 45,
  "default_deadline_days": 100
}
```

**Validation Rules:** Same as POST /courses (all fields optional for PATCH)

**Response (200):** Same structure as POST /courses

---

### DELETE /courses/{course_id}

Delete a course. Only allowed if no active enrollments.

**Auth:** Admin

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "message": "Course deleted successfully"
  }
}
```

**Error (409):**
```json
{
  "status": "error",
  "error": {
    "code": "HAS_ACTIVE_ENROLLMENTS",
    "message": "Cannot delete course with 15 active enrollments. Cancel enrollments first."
  }
}
```

---

### PUT /courses/{course_id}/publish

Toggle course published status.

**Auth:** Admin

**Request Body:**
```json
{
  "is_published": true
}
```

**Validation Rules:**
| Field | Rule |
|---|---|
| is_published | Required, boolean |

**Validation:** Course must have at least one module with at least one lesson to publish.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "course_id": "uuid",
    "is_published": true,
    "updated_at": "2026-06-20T15:00:00Z"
  }
}
```

---

### POST /courses/{course_id}/modules

Create a module within a course.

**Auth:** Admin

**Request Body:**
```json
{
  "title": "Linear Equations",
  "description": "Solving and graphing linear equations.",
  "order_index": 1,
  "estimated_duration_hours": 8
}
```

**Validation Rules:**
| Field | Rule |
|---|---|
| title | Required, max 200 chars |
| description | Optional |
| order_index | Required, integer >= 1, unique within course |
| estimated_duration_hours | Optional, integer > 0 |

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "module_id": "uuid",
    "course_id": "uuid",
    "title": "Linear Equations",
    "description": "Solving and graphing linear equations.",
    "order_index": 1,
    "estimated_duration_hours": 8,
    "created_at": "2026-06-20T14:30:00Z"
  }
}
```

---

### GET /courses/{course_id}/modules

List all modules in a course.

**Auth:** Any authenticated user

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "module_id": "uuid",
      "title": "Linear Equations",
      "description": "Solving and graphing linear equations.",
      "order_index": 1,
      "estimated_duration_hours": 8,
      "lesson_count": 4
    }
  ]
}
```

---

### PUT /modules/{module_id}

Update module.

**Auth:** Admin

**Request Body:** Partial update — same fields as POST with same validation.

**Response (200):** Same structure as POST /courses/{course_id}/modules

---

### DELETE /modules/{module_id}

Delete a module.

**Auth:** Admin

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "message": "Module deleted successfully"
  }
}
```

---

### POST /modules/{module_id}/lessons

Create a lesson within a module.

**Auth:** Admin

**Request Body:**
```json
{
  "title": "Introduction to Variables",
  "content_url": "https://cdn.example.com/lessons/variables-v1.mp4",
  "order_index": 1,
  "estimated_duration_minutes": 30,
  "is_required": true,
  "status": "draft"
}
```

**Validation Rules:**
| Field | Rule |
|---|---|
| title | Required, max 200 chars |
| content_url | Optional, valid URL |
| order_index | Required, integer >= 1, unique within module |
| estimated_duration_minutes | Optional, integer > 0 |
| is_required | Optional, boolean, default: true |
| status | Optional, enum: `draft` | `published` | `archived`, default: `draft` |

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "lesson_id": "uuid",
    "module_id": "uuid",
    "title": "Introduction to Variables",
    "content_url": "https://cdn.example.com/lessons/variables-v1.mp4",
    "order_index": 1,
    "estimated_duration_minutes": 30,
    "is_required": true,
    "status": "draft",
    "created_at": "2026-06-20T14:30:00Z"
  }
}
```

---

### GET /modules/{module_id}/lessons

List all lessons in a module.

**Auth:** Any authenticated user

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "lesson_id": "uuid",
      "title": "Introduction to Variables",
      "order_index": 1,
      "estimated_duration_minutes": 30,
      "status": "published",
      "concept_count": 3
    }
  ]
}
```

---

### PUT /lessons/{lesson_id}

Update lesson.

**Auth:** Admin

**Request Body:** Partial update — same fields as POST with same validation.

**Response (200):** Same structure as POST /modules/{module_id}/lessons

---

### DELETE /lessons/{lesson_id}

Delete a lesson.

**Auth:** Admin

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "message": "Lesson deleted successfully"
  }
}
```

---

### POST /lessons/{lesson_id}/concepts

Create a concept within a lesson.

**Auth:** Admin

**Request Body:**
```json
{
  "title": "What is a Variable?",
  "description": "Define variables and their role in algebraic expressions.",
  "order_index": 1,
  "estimated_duration_minutes": 10
}
```

**Validation Rules:**
| Field | Rule |
|---|---|
| title | Required, max 200 chars |
| description | Optional |
| order_index | Required, integer >= 1, unique within lesson |
| estimated_duration_minutes | Optional, integer > 0 |

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "concept_id": "uuid",
    "lesson_id": "uuid",
    "title": "What is a Variable?",
    "description": "Define variables and their role in algebraic expressions.",
    "order_index": 1,
    "estimated_duration_minutes": 10,
    "created_at": "2026-06-20T14:30:00Z"
  }
}
```

---

### GET /lessons/{lesson_id}/concepts

List all concepts in a lesson.

**Auth:** Any authenticated user

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "concept_id": "uuid",
      "title": "What is a Variable?",
      "description": "Define variables and their role in algebraic expressions.",
      "order_index": 1,
      "estimated_duration_minutes": 10,
      "content_count": 3,
      "exercise_count": 5
    }
  ]
}
```

---

### PUT /concepts/{concept_id}

Update concept.

**Auth:** Admin

**Request Body:** Partial update — same fields as POST with same validation.

**Response (200):** Same structure as POST /lessons/{lesson_id}/concepts

---

### DELETE /concepts/{concept_id}

Delete a concept.

**Auth:** Admin

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "message": "Concept deleted successfully"
  }
}
```

---

### POST /concepts/{concept_id}/contents

Add teaching content to a concept.

**Auth:** Admin

**Request Body:**
```json
{
  "content_type": "explanation",
  "content": "A variable is a symbol, usually a letter, that represents an unknown number. For example, in the expression x + 5 = 10, the variable x represents 5.",
  "order_index": 1
}
```

**Validation Rules:**
| Field | Rule |
|---|---|
| content_type | Required, enum: `explanation` | `example` | `visualization` | `analogy` | `summary` |
| content | Required, valid markdown content |
| order_index | Required, integer >= 0, unique per (concept_id, content_type) |

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "content_id": "uuid",
    "concept_id": "uuid",
    "content_type": "explanation",
    "content": "A variable is a symbol...",
    "order_index": 1,
    "version": 1,
    "created_at": "2026-06-20T14:30:00Z"
  }
}
```

---

### GET /concepts/{concept_id}/contents

List all teaching contents for a concept.

**Auth:** Any authenticated user

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "content_id": "uuid",
      "content_type": "explanation",
      "content": "A variable is a symbol...",
      "order_index": 1,
      "version": 1,
      "updated_at": "2026-06-20T14:30:00Z"
    }
  ]
}
```

---

### PUT /concept-contents/{content_id}

Update teaching content.

**Auth:** Admin

**Request Body:**
```json
{
  "content": "Updated content..."
}
```

**Validation Rules:** At least one field must be provided.

**Response (200):** Updated content object.

---

### DELETE /concept-contents/{content_id}

Delete teaching content.

**Auth:** Admin

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "message": "Content deleted successfully"
  }
}
```

---

### POST /concepts/{concept_id}/exercises

Create an exercise for a concept.

**Auth:** Admin

**Request Body:**
```json
{
  "question_type": "mcq",
  "prompt": "What is the value of x in x + 5 = 12?",
  "options": {
    "A": "5",
    "B": "7",
    "C": "12",
    "D": "17"
  },
  "correct_answer": "B",
  "difficulty": 0.4,
  "order_index": 1,
  "tags": ["variables", "addition", "basics"]
}
```

**Validation Rules:**
| Field | Rule |
|---|---|
| question_type | Required, enum: `mcq` | `multi_select` | `short_answer` | `fill_blank` |
| prompt | Required |
| options | Required for `mcq` and `multi_select` |
| correct_answer | Required |
| difficulty | Optional, float 0.0–1.0, default: 0.5 |
| order_index | Required, integer >= 1 |
| tags | Optional, string array |

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "exercise_id": "uuid",
    "concept_id": "uuid",
    "question_type": "mcq",
    "prompt": "What is the value of x in x + 5 = 12?",
    "options": {"A": "5", "B": "7", "C": "12", "D": "17"},
    "difficulty": 0.4,
    "order_index": 1,
    "tags": ["variables", "addition", "basics"],
    "created_at": "2026-06-20T14:30:00Z"
  }
}
```

---

### GET /concepts/{concept_id}/exercises

List all exercises for a concept.

**Auth:** Any authenticated user

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "exercise_id": "uuid",
      "question_type": "mcq",
      "prompt": "What is the value of x in x + 5 = 12?",
      "difficulty": 0.4,
      "order_index": 1,
      "tags": ["variables", "addition", "basics"]
    }
  ]
}
```

*Note: `correct_answer` and `options` are excluded from list view and returned only on individual GET for active teaching sessions.*

---

### PUT /exercises/{exercise_id}

Update exercise.

**Auth:** Admin

**Request Body:** Partial update — same fields as POST with same validation.

**Response (200):** Same structure as POST /concepts/{concept_id}/exercises (includes `correct_answer`)

---

### DELETE /exercises/{exercise_id}

Delete an exercise.

**Auth:** Admin

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "message": "Exercise deleted successfully"
  }
}
```

---

### POST /concepts/{concept_id}/examples

Create an example for a concept.

**Auth:** Admin

**Request Body:**
```json
{
  "content": "If you have 3 apples and someone gives you 2 more, you have 5 apples. So 3 + 2 = 5.",
  "explanation": "This demonstrates how variables represent unknown quantities that can be solved for.",
  "order_index": 1,
  "tags": ["real-world", "addition"]
}
```

**Validation Rules:**
| Field | Rule |
|---|---|
| content | Required |
| explanation | Optional |
| order_index | Required, integer >= 1 |
| tags | Optional, string array |

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "example_id": "uuid",
    "concept_id": "uuid",
    "content": "If you have 3 apples...",
    "explanation": "This demonstrates...",
    "order_index": 1,
    "tags": ["real-world", "addition"],
    "created_at": "2026-06-20T14:30:00Z"
  }
}
```

---

### PUT /examples/{example_id}

Update example.

**Auth:** Admin

**Response (200):** Updated example object.

---

### DELETE /examples/{example_id}

Delete an example.

**Auth:** Admin

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "message": "Example deleted successfully"
  }
}
```

---

### POST /lessons/{lesson_id}/objectives

Create a learning objective.

**Auth:** Admin

**Request Body:**
```json
{
  "code": "ALG.VAR.01",
  "description": "Student can define a variable and solve simple one-step equations.",
  "success_criterion": {
    "min_attempts": 3,
    "min_accuracy": 0.8,
    "required_exercise_types": ["mcq", "short_answer"]
  },
  "order_index": 1
}
```

**Validation Rules:**
| Field | Rule |
|---|---|
| code | Required, max 50 chars, unique within lesson |
| description | Required |
| success_criterion | Optional, JSON object |
| order_index | Required, integer >= 1 |

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "objective_id": "uuid",
    "lesson_id": "uuid",
    "code": "ALG.VAR.01",
    "description": "Student can define a variable and solve simple one-step equations.",
    "success_criterion": {"min_attempts": 3, "min_accuracy": 0.8, "required_exercise_types": ["mcq", "short_answer"]},
    "order_index": 1,
    "created_at": "2026-06-20T14:30:00Z"
  }
}
```

---

### PUT /objectives/{objective_id}

Update learning objective.

**Auth:** Admin

**Response (200):** Updated objective object.

---

### DELETE /objectives/{objective_id}

Delete a learning objective.

**Auth:** Admin

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "message": "Objective deleted successfully"
  }
}
```

---

### POST /knowledge-graph/edges

Create a prerequisite edge between two knowledge nodes.

**Auth:** Admin

**Request Body:**
```json
{
  "source_node_id": "uuid",
  "target_node_id": "uuid",
  "relationship": "requires",
  "weight": 0.8
}
```

**Validation Rules:**
| Field | Rule |
|---|---|
| source_node_id | Required, must exist in knowledge_nodes |
| target_node_id | Required, must exist in knowledge_nodes, != source_node_id |
| relationship | Required, enum: `requires` | `reinforces` | `contains` |
| weight | Optional, float 0.0–1.0, default: 1.0 |

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "edge_id": "uuid",
    "source_node_id": "uuid",
    "target_node_id": "uuid",
    "relationship": "requires",
    "weight": 0.8,
    "created_at": "2026-06-20T14:30:00Z"
  }
}
```

---

### DELETE /knowledge-graph/edges/{edge_id}

Remove a knowledge graph edge.

**Auth:** Admin

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "message": "Edge deleted successfully"
  }
}
```

---

### GET /knowledge-graph/concepts/{concept_id}/prerequisites

Get all prerequisite nodes for a given concept.

**Auth:** Any authenticated user

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "concept_id": "uuid",
    "concept_title": "What is a Variable?",
    "prerequisites": [
      {
        "node_id": "uuid",
        "label": "Basic Number Sense",
        "relationship": "requires",
        "weight": 0.9,
        "is_mastered": true,
        "student_mastery": 0.95
      },
      {
        "node_id": "uuid",
        "label": "Addition and Subtraction",
        "relationship": "requires",
        "weight": 0.7,
        "is_mastered": false,
        "student_mastery": 0.45
      }
    ]
  }
}
```

*Note: `is_mastered` and `student_mastery` are populated only for the authenticated student.*

---

## 4. Student Learning

### POST /enrollments

Enroll the authenticated student in a course.

**Auth:** Student

**Request Body:**
```json
{
  "course_id": "uuid",
  "target_completion_date": "2026-09-20"
}
```

**Validation Rules:**
| Field | Rule |
|---|---|
| course_id | Required, must be a published course |
| target_completion_date | Optional, must be in the future |

**Business Rules:**
- Student must not have an existing active enrollment in the same course.

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "enrollment_id": "uuid",
    "course_id": "uuid",
    "course_title": "Algebra I",
    "status": "active",
    "target_completion_date": "2026-09-20",
    "enrolled_at": "2026-06-20T14:30:00Z",
    "schedule": {
      "target_lessons_per_week": 3,
      "current_week": 1,
      "pace_status": "on_track",
      "milestones": [
        {"week": 1, "expected_concept": "What is a Variable?", "deadline": "2026-06-27"}
      ]
    }
  }
}
```

---

### GET /enrollments

List the authenticated student's enrollments.

**Auth:** Student

**Query Parameters:**
| Param | Type | Description |
|---|---|---|
| `status` | `enrollment_status` | Filter by status |

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "enrollment_id": "uuid",
      "course_id": "uuid",
      "course_title": "Algebra I",
      "status": "active",
      "progress_pct": 35.0,
      "current_concept": "Solving Two-Step Equations",
      "target_completion_date": "2026-09-20",
      "pace_status": "on_track",
      "enrolled_at": "2026-05-01T10:00:00Z"
    }
  ]
}
```

---

### GET /enrollments/{enrollment_id}

Get detailed enrollment information.

**Auth:** Student (own) or Parent (linked student)

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "enrollment_id": "uuid",
    "course_id": "uuid",
    "course_title": "Algebra I",
    "status": "active",
    "enrolled_at": "2026-05-01T10:00:00Z",
    "started_at": "2026-05-02T09:00:00Z",
    "target_completion_date": "2026-09-20",
    "schedule": {
      "target_lessons_per_week": 3,
      "current_week": 8,
      "pace_status": "on_track",
      "milestones": [
        {"week": 1, "expected_concept": "What is a Variable?", "deadline": "2026-06-27", "completed": true},
        {"week": 2, "expected_concept": "Solving One-Step Equations", "deadline": "2026-07-04", "completed": true},
        {"week": 8, "expected_concept": "Graphing Linear Equations", "deadline": "2026-08-22", "completed": false}
      ]
    },
    "progress": {
      "total_concepts": 24,
      "completed_concepts": 8,
      "overall_mastery": 0.72,
      "total_sessions": 15,
      "total_time_minutes": 420
    }
  }
}
```

---

### PATCH /enrollments/{enrollment_id}

Update enrollment status (pause/resume).

**Auth:** Student (own)

**Request Body:**
```json
{
  "status": "paused"
}
```

**Validation Rules:**
| Field | Rule |
|---|---|
| status | Must be `paused` or `active` (not `completed` or `dropped` — those require admin) |

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "enrollment_id": "uuid",
    "status": "paused",
    "updated_at": "2026-06-20T15:00:00Z"
  }
}
```

---

### GET /courses/{course_id}/curriculum

Get the full curriculum tree for a course.

**Auth:** Any authenticated user

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "course_id": "uuid",
    "course_title": "Algebra I",
    "modules": [
      {
        "module_id": "uuid",
        "title": "Linear Equations",
        "order_index": 1,
        "lessons": [
          {
            "lesson_id": "uuid",
            "title": "Introduction to Variables",
            "order_index": 1,
            "concepts": [
              {
                "concept_id": "uuid",
                "title": "What is a Variable?",
                "order_index": 1,
                "mastery_level": 0.85
              }
            ]
          }
        ]
      }
    ]
  }
}
```

*Note: `mastery_level` is included only for authenticated students with enrollment.*

---

### GET /lessons/{lesson_id}

Get lesson details with concept list.

**Auth:** Any authenticated user

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "lesson_id": "uuid",
    "module_id": "uuid",
    "title": "Introduction to Variables",
    "content_url": "https://cdn.example.com/lessons/variables-v1.mp4",
    "order_index": 1,
    "estimated_duration_minutes": 30,
    "status": "published",
    "concepts": [
      {
        "concept_id": "uuid",
        "title": "What is a Variable?",
        "description": "Define variables and their role in algebraic expressions.",
        "order_index": 1,
        "estimated_duration_minutes": 10
      }
    ]
  }
}
```

---

### GET /concepts/{concept_id}

Get concept details with content and exercises.

**Auth:** Any authenticated user

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "concept_id": "uuid",
    "lesson_id": "uuid",
    "title": "What is a Variable?",
    "description": "Define variables and their role in algebraic expressions.",
    "order_index": 1,
    "estimated_duration_minutes": 10,
    "contents": [
      {
        "content_id": "uuid",
        "content_type": "explanation",
        "content": "A variable is a symbol...",
        "order_index": 1
      }
    ],
    "examples": [
      {
        "example_id": "uuid",
        "content": "If you have 3 apples...",
        "explanation": "This demonstrates..."
      }
    ],
    "exercise_count": 5,
    "mastery": {
      "mastery_level": 0.85,
      "total_attempts": 4,
      "consecutive_correct": 3
    }
  }
}
```

*Note: `mastery` is included only for authenticated students with enrollment. Exercises are listed separately to separate content from assessment.*

---

### GET /lessons/{lesson_id}/progress

Get the authenticated student's progress for a lesson.

**Auth:** Student

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "lesson_id": "uuid",
    "lesson_title": "Introduction to Variables",
    "status": "in_progress",
    "started_at": "2026-06-19T10:00:00Z",
    "time_spent_seconds": 720,
    "completion_percentage": 60.0,
    "concepts": [
      {
        "concept_id": "uuid",
        "title": "What is a Variable?",
        "mastery_level": 0.85,
        "status": "completed"
      },
      {
        "concept_id": "uuid",
        "title": "Using Variables in Expressions",
        "mastery_level": 0.3,
        "status": "in_progress"
      }
    ]
  }
}
```

---

## 5. Teaching Session

### POST /sessions

Start a new teaching session or resume the most recent active one.

**Auth:** Student

**Request Body:**
```json
{
  "course_id": "uuid",
  "resume_last": true
}
```

**Validation Rules:**
| Field | Rule |
|---|---|
| course_id | Required, student must be enrolled and enrollment must be `active` |
| resume_last | Optional, boolean. If true and an active session exists, return it instead of creating new |

**Response (201 — New Session):**
```json
{
  "status": "success",
  "data": {
    "session_id": "uuid",
    "student_id": "uuid",
    "course_id": "uuid",
    "course_title": "Algebra I",
    "state": "active",
    "current_concept": {
      "concept_id": "uuid",
      "title": "What is a Variable?",
      "order_index": 1
    },
    "current_lesson": {
      "lesson_id": "uuid",
      "title": "Introduction to Variables"
    },
    "context_summary": {
      "concepts_taught_this_session": 0,
      "exercises_answered": 0,
      "session_duration_minutes": 0
    },
    "started_at": "2026-06-20T14:30:00Z",
    "last_activity_at": "2026-06-20T14:30:00Z"
  }
}
```

**Response (200 — Resumed Session):**
```json
{
  "status": "success",
  "data": {
    "session_id": "uuid",
    "student_id": "uuid",
    "course_id": "uuid",
    "state": "active",
    "current_concept": {...},
    "current_lesson": {...},
    "context_summary": {
      "concepts_taught_this_session": 3,
      "exercises_answered": 7,
      "session_duration_minutes": 28
    },
    "resumed": true,
    "started_at": "2026-06-20T14:00:00Z",
    "last_activity_at": "2026-06-20T14:30:00Z"
  }
}
```

---

### GET /sessions/active

Get the student's currently active session (if any).

**Auth:** Student

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "session_id": "uuid",
    "course_id": "uuid",
    "state": "active",
    "current_concept": {...},
    "started_at": "2026-06-20T14:00:00Z",
    "last_activity_at": "2026-06-20T14:28:00Z"
  }
}
```

**Response (200 — No Active Session):**
```json
{
  "status": "success",
  "data": null
}
```

---

### GET /sessions/{session_id}

Get teaching session details.

**Auth:** Student (own)

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "session_id": "uuid",
    "course_id": "uuid",
    "student_id": "uuid",
    "state": "active",
    "current_concept": {...},
    "current_lesson": {...},
    "context": {
      "concepts_covered": ["concept_id_1", "concept_id_2"],
      "current_action": "teaching",
      "teaching_history": [
        {"action": "teach", "concept_id": "uuid", "timestamp": "..."},
        {"action": "quiz", "concept_id": "uuid", "timestamp": "..."},
        {"action": "remediate", "concept_id": "uuid", "timestamp": "..."}
      ]
    },
    "started_at": "2026-06-20T14:00:00Z",
    "last_activity_at": "2026-06-20T14:28:00Z"
  }
}
```

---

### PATCH /sessions/{session_id}

Update session state (pause or end).

**Auth:** Student (own)

**Request Body:**
```json
{
  "state": "paused"
}
```

**Validation Rules:**
| Field | Rule |
|---|---|
| state | Must be `paused` or `completed`. Cannot transition from `completed` or `interrupted` |

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "session_id": "uuid",
    "state": "paused",
    "updated_at": "2026-06-20T15:00:00Z"
  }
}
```

---

### POST /sessions/{session_id}/next

Get the AI's next teaching action. This is the primary AI interaction endpoint.

The AI orchestrator evaluates the current state (mastery, misconceptions, pacing) and decides what to do next.

**Auth:** Student (own)

**Request Body:** (none — AI uses session context)

**Response (200) — Teach Action:**
```json
{
  "status": "success",
  "data": {
    "action": "teach",
    "concept_id": "uuid",
    "concept_title": "What is a Variable?",
    "content": {
      "content_type": "explanation",
      "body": "A variable is a symbol, usually a letter, that represents an unknown number..."
    },
    "context": {
      "concept_progress": "new",
      "prerequisites_satisfied": true,
      "pacing_note": "On track for weekly goal"
    }
  }
}
```

**Response (200) — Quiz Action:**
```json
{
  "status": "success",
  "data": {
    "action": "quiz",
    "concept_id": "uuid",
    "concept_title": "What is a Variable?",
    "exercise": {
      "exercise_id": "uuid",
      "question_type": "mcq",
      "prompt": "What is the value of x in x + 5 = 12?",
      "options": {"A": "5", "B": "7", "C": "12", "D": "17"}
    },
    "context": {
      "concept_progress": "taught",
      "reason": "Initial check for understanding",
      "attempt_number": 1
    }
  }
}
```

**Response (200) — Remediate Action:**
```json
{
  "status": "success",
  "data": {
    "action": "remediate",
    "concept_id": "uuid",
    "concept_title": "Basic Number Sense",
    "reason": "Prerequisite not mastered",
    "content": {
      "content_type": "explanation",
      "body": "Let's review the basics first. Numbers represent quantities..."
    },
    "context": {
      "original_concept": "What is a Variable?",
      "missing_prerequisite": "Basic Number Sense",
      "student_mastery": 0.3,
      "required_mastery": 0.7
    }
  }
}
```

**Response (200) — Revise Action:**
```json
{
  "status": "success",
  "data": {
    "action": "revise",
    "concept_id": "uuid",
    "concept_title": "What is a Variable?",
    "reason": "Spaced repetition trigger — revision due",
    "content": {
      "content_type": "summary",
      "body": "Quick recap: A variable represents an unknown number..."
    }
  }
}
```

**Response (200) — Session Complete:**
```json
{
  "status": "success",
  "data": {
    "action": "session_complete",
    "reason": "All concepts for this session covered",
    "summary": {
      "concepts_taught": 3,
      "exercises_answered": 5,
      "accuracy": 0.8,
      "recommendation": "Great session! Review 'Graphing' concepts next time."
    },
    "pacing_update": {
      "pace_status": "on_track",
      "next_session_recommendation": "Continue with 'Using Variables in Expressions'"
    }
  }
}
```

---

### POST /sessions/{session_id}/respond

Submit a student's response to the current exercise.

**Auth:** Student (own)

**Request Body:**
```json
{
  "exercise_id": "uuid",
  "response": "7"
}
```

**Validation Rules:**
| Field | Rule |
|---|---|
| exercise_id | Required, must match the current active exercise in the session |
| response | Required, non-empty string |

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "attempt_id": "uuid",
    "exercise_id": "uuid",
    "response": "7",
    "is_correct": true,
    "score": 1.0,
    "ai_feedback": "Correct! x = 7 because 7 + 5 = 12. Well done!",
    "mastery_update": {
      "concept_id": "uuid",
      "previous_mastery": 0.5,
      "new_mastery": 0.7,
      "consecutive_correct": 2
    },
    "misconception_detected": false,
    "next_action_hint": "Ready for next concept"
  }
}
```

**Response (200) — With Misconception:**
```json
{
  "status": "success",
  "data": {
    "attempt_id": "uuid",
    "is_correct": false,
    "score": 0.0,
    "ai_feedback": "Not quite. It looks like you subtracted 12 from 5 instead of 5 from 12. Remember: to isolate x, subtract 5 from BOTH sides.",
    "mastery_update": {
      "previous_mastery": 0.5,
      "new_mastery": 0.4
    },
    "misconception_detected": {
      "misconception_id": "uuid",
      "category": "procedural",
      "description": "Student reverses the operation when isolating a variable",
      "evidence": {"response": "17", "expected_operation": "subtract", "performed_operation": "add"}
    },
    "next_action_hint": "Remediation recommended"
  }
}
```

---

### GET /sessions/{session_id}/history

Get the attempt history for a session.

**Auth:** Student (own)

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "session_id": "uuid",
    "attempts": [
      {
        "attempt_id": "uuid",
        "exercise_id": "uuid",
        "concept_title": "What is a Variable?",
        "response": "7",
        "is_correct": true,
        "score": 1.0,
        "attempted_at": "2026-06-20T14:25:00Z",
        "attempt_number": 1
      }
    ],
    "summary": {
      "total_attempts": 5,
      "correct": 4,
      "accuracy": 0.8,
      "concepts_covered": 3
    }
  }
}
```

---

## 6. Assessment

### POST /sessions/{session_id}/quiz

Request the AI to generate a custom quiz for the current concept.

**Auth:** Student (own)

**Request Body:**
```json
{
  "difficulty": 0.6,
  "question_count": 3,
  "focus_areas": ["word problems"]
}
```

**Validation Rules:**
| Field | Rule |
|---|---|
| difficulty | Optional, float 0.0–1.0, default: concept's current difficulty |
| question_count | Optional, integer 1–10, default: 3 |
| focus_areas | Optional, string array |

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "exercises": [
      {
        "exercise_id": "uuid",
        "question_type": "short_answer",
        "prompt": "If a number plus 8 equals 15, what is the number?",
        "difficulty": 0.6
      },
      {
        "exercise_id": "uuid",
        "question_type": "mcq",
        "prompt": "Which equation represents 'a number increased by 6 is 20'?",
        "options": {"A": "x - 6 = 20", "B": "x + 6 = 20", "C": "6x = 20", "D": "x / 6 = 20"},
        "difficulty": 0.6
      }
    ],
    "session_context": "Generated quiz for 'What is a Variable?' — difficulty: 0.6"
  }
}
```

---

### GET /exercises/{exercise_id}

Get exercise details (for the current active exercise in a session).

**Auth:** Student (own, within active session)

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "exercise_id": "uuid",
    "question_type": "mcq",
    "prompt": "What is the value of x in x + 5 = 12?",
    "options": {"A": "5", "B": "7", "C": "12", "D": "17"},
    "difficulty": 0.4
  }
}
```

*Note: `correct_answer` is never exposed via GET — only used internally for grading.*

---

### POST /exercises/{exercise_id}/grade

Request AI grading for a specific exercise (typically used for non-MCQ types).

**Auth:** Student (own, within active session)

**Request Body:**
```json
{
  "response": "The variable x equals 7 because 12 minus 5 is 7.",
  "teaching_session_id": "uuid"
}
```

**Validation Rules:**
| Field | Rule |
|---|---|
| response | Required |
| teaching_session_id | Required, must be active and belong to student |

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "attempt_id": "uuid",
    "exercise_id": "uuid",
    "response": "The variable x equals 7 because 12 minus 5 is 7.",
    "is_correct": true,
    "score": 1.0,
    "ai_feedback": "Excellent explanation! You correctly identified that x = 7.",
    "confidence": 0.95
  }
}
```

---

### GET /attempts/{attempt_id}

Get a single attempt's details.

**Auth:** Student (own) or Parent (linked student)

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "attempt_id": "uuid",
    "exercise_id": "uuid",
    "concept_title": "What is a Variable?",
    "question_type": "mcq",
    "prompt": "What is the value of x in x + 5 = 12?",
    "response": "7",
    "is_correct": true,
    "score": 1.0,
    "ai_feedback": "Correct! x = 7 because 7 + 5 = 12.",
    "attempt_number": 1,
    "attempted_at": "2026-06-20T14:25:00Z",
    "time_taken_seconds": 45
  }
}
```

---

### GET /attempts

List attempts for the authenticated student.

**Auth:** Student

**Query Parameters:**
| Param | Type | Description |
|---|---|---|
| `course_id` | `UUID` | Filter by course |
| `concept_id` | `UUID` | Filter by concept |
| `is_correct` | `boolean` | Filter by correctness |
| `from` | `ISO8601` | Start date |
| `to` | `ISO8601` | End date |
| `page` | `integer` | Default: 1 |
| `per_page` | `integer` | Default: 20 |

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "attempt_id": "uuid",
      "concept_title": "What is a Variable?",
      "question_type": "mcq",
      "prompt": "What is the value of x in x + 5 = 12?",
      "is_correct": true,
      "attempted_at": "2026-06-20T14:25:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 85,
    "total_pages": 5
  }
}
```

---

## 7. Mastery Tracking

### GET /mastery

Get the authenticated student's overall mastery overview.

**Auth:** Student

**Query Parameters:**
| Param | Type | Description |
|---|---|---|
| `course_id` | `UUID` | Required — scope to a course |

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "course_id": "uuid",
    "course_title": "Algebra I",
    "overall_mastery": 0.72,
    "total_concepts": 24,
    "mastered_concepts": 12,
    "in_progress_concepts": 5,
    "not_started_concepts": 7,
    "concepts": [
      {
        "concept_id": "uuid",
        "title": "What is a Variable?",
        "mastery_level": 0.95,
        "status": "mastered",
        "last_attempted": "2026-06-19T10:00:00Z",
        "total_attempts": 4,
        "next_review_at": "2026-07-03T10:00:00Z"
      },
      {
        "concept_id": "uuid",
        "title": "Using Variables in Expressions",
        "mastery_level": 0.35,
        "status": "in_progress",
        "last_attempted": "2026-06-20T14:25:00Z",
        "total_attempts": 2,
        "next_review_at": null
      }
    ]
  }
}
```

*Status mapping: mastery >= 0.8 → `mastered`, mastery > 0 and < 0.8 → `in_progress`, mastery = 0 → `not_started`.*

---

### GET /mastery/concepts/{concept_id}

Get detailed mastery for a specific concept.

**Auth:** Student

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "concept_id": "uuid",
    "concept_title": "What is a Variable?",
    "lesson_id": "uuid",
    "mastery_level": 0.85,
    "mastery_history": [
      {"date": "2026-06-18", "mastery": 0.3, "attempts": 1},
      {"date": "2026-06-19", "mastery": 0.6, "attempts": 2},
      {"date": "2026-06-20", "mastery": 0.85, "attempts": 1}
    ],
    "recent_attempts": [
      {
        "attempt_id": "uuid",
        "is_correct": true,
        "score": 1.0,
        "attempted_at": "2026-06-20T14:25:00Z"
      }
    ],
    "prerequisites": [
      {
        "node_id": "uuid",
        "label": "Basic Number Sense",
        "mastery": 0.95,
        "is_satisfied": true
      }
    ],
    "next_review_at": "2026-07-04T14:25:00Z"
  }
}
```

---

### GET /mastery/courses/{course_id}

Get aggregated mastery summary for a course.

**Auth:** Student (must be enrolled)

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "course_id": "uuid",
    "course_title": "Algebra I",
    "overall_mastery": 0.72,
    "by_module": [
      {
        "module_id": "uuid",
        "module_title": "Linear Equations",
        "mastery": 0.85,
        "concepts_total": 8,
        "concepts_mastered": 6
      }
    ],
    "weakest_concepts": [
      {
        "concept_id": "uuid",
        "title": "Graphing Linear Equations",
        "mastery": 0.2,
        "total_attempts": 1
      }
    ],
    "pacing": {
      "pace_status": "on_track",
      "current_week": 8,
      "total_weeks": 13,
      "completion_projection": "2026-08-15"
    }
  }
}
```

---

### GET /diagnosis

Get all active misconceptions for the authenticated student.

**Auth:** Student

**Query Parameters:**
| Param | Type | Description |
|---|---|---|
| `course_id` | `UUID` | Filter by course |
| `is_resolved` | `boolean` | Filter by resolution status |

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "total_active": 3,
    "total_resolved": 5,
    "misconceptions": [
      {
        "misconception_id": "uuid",
        "concept_id": "uuid",
        "concept_title": "Solving One-Step Equations",
        "category": "procedural",
        "description": "Student reverses the operation when isolating a variable",
        "detected_at": "2026-06-19T10:30:00Z",
        "frequency": 3,
        "is_resolved": false,
        "evidence": [
          {"response": "17", "exercise_prompt": "x + 5 = 12", "expected": "7"},
          {"response": "8", "exercise_prompt": "x + 3 = 5", "expected": "2"}
        ]
      }
    ]
  }
}
```

---

### GET /diagnosis/concepts/{concept_id}

Get misconceptions for a specific concept.

**Auth:** Student

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "concept_id": "uuid",
    "concept_title": "Solving One-Step Equations",
    "misconceptions": [
      {
        "misconception_id": "uuid",
        "category": "procedural",
        "description": "Student reverses the operation when isolating a variable",
        "frequency": 3,
        "is_resolved": false
      }
    ]
  }
}
```

---

### PATCH /diagnosis/{misconception_id}/resolve

Mark a misconception as resolved.

**Auth:** Student (own) or Admin

**Request Body:**
```json
{
  "is_resolved": true
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "misconception_id": "uuid",
    "is_resolved": true,
    "resolved_at": "2026-06-20T15:00:00Z"
  }
}
```

---

### GET /memory

Get summary of the student's AI memory entries.

**Auth:** Student

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "memory_count": 8,
    "entries": [
      {
        "key": "pace_preference",
        "value": {"preferred_session_length": 25, "breaks_needed": true},
        "importance": 0.9,
        "updated_at": "2026-06-15T10:00:00Z"
      },
      {
        "key": "common_stumble_on_fractions",
        "value": {"concept_id": "uuid", "description": "Consistently confuses numerator and denominator in division"},
        "importance": 0.8,
        "updated_at": "2026-06-18T14:00:00Z"
      }
    ]
  }
}
```

---

### GET /memory/{key}

Get a specific memory entry by key.

**Auth:** Student

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "key": "pace_preference",
    "value": {"preferred_session_length": 25, "breaks_needed": true},
    "importance": 0.9,
    "created_at": "2026-06-10T10:00:00Z",
    "updated_at": "2026-06-15T10:00:00Z"
  }
}
```

---

### GET /pacing

Get the student's pacing status for a course.

**Auth:** Student

**Query Parameters:**
| Param | Type | Description |
|---|---|---|
| `course_id` | `UUID` | Required — scope to a course |

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "course_id": "uuid",
    "course_title": "Algebra I",
    "enrolled_at": "2026-05-01T10:00:00Z",
    "target_completion_date": "2026-09-20",
    "days_remaining": 92,
    "pace_status": "behind",
    "target_lessons_per_week": 3,
    "actual_lessons_per_week": 2.1,
    "current_week": 8,
    "total_weeks": 20,
    "completion_projected": "2026-10-15",
    "milestones": [
      {"week": 8, "expected_concept": "Graphing Linear Equations", "status": "behind", "days_overdue": 5}
    ],
    "recommendation": "Increase to 4 lessons per week to meet the target completion date."
  }
}
```

---

## 8. Parent Reports

### GET /parent/students

List students linked to the authenticated parent.

**Auth:** Parent

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "student_id": "uuid",
      "full_name": "Jane Doe Jr.",
      "grade_level": "Grade 10",
      "active_courses": 2,
      "overall_mastery_avg": 0.74,
      "last_active": "2026-06-20T10:00:00Z",
      "current_streak_days": 5
    }
  ]
}
```

---

### GET /parent/students/{student_id}/progress

Get a high-level progress summary for a linked student.

**Auth:** Parent

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "student_id": "uuid",
    "full_name": "Jane Doe Jr.",
    "grade_level": "Grade 10",
    "courses": [
      {
        "course_id": "uuid",
        "course_title": "Algebra I",
        "status": "active",
        "overall_mastery": 0.72,
        "progress_pct": 35.0,
        "concepts_mastered": 12,
        "concepts_total": 24,
        "pace_status": "on_track",
        "last_session": "2026-06-20T14:30:00Z",
        "total_time_spent_minutes": 420
      }
    ],
    "weekly_summary": {
      "sessions_this_week": 3,
      "time_spent_minutes": 95,
      "concepts_learned": 2,
      "exercises_answered": 12,
      "accuracy": 0.83
    }
  }
}
```

---

### GET /parent/students/{student_id}/mastery

Get detailed mastery breakdown for a linked student.

**Auth:** Parent

**Query Parameters:**
| Param | Type | Description |
|---|---|---|
| `course_id` | `UUID` | Filter by course |

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "student_id": "uuid",
    "student_name": "Jane Doe Jr.",
    "courses": [
      {
        "course_id": "uuid",
        "course_title": "Algebra I",
        "overall_mastery": 0.72,
        "by_module": [
          {
            "module_title": "Linear Equations",
            "mastery": 0.85,
            "concepts": [
              {"title": "What is a Variable?", "mastery": 0.95, "status": "mastered"},
              {"title": "Solving One-Step Equations", "mastery": 0.6, "status": "in_progress"}
            ]
          }
        ]
      }
    ]
  }
}
```

---

### GET /parent/students/{student_id}/misconceptions

Get active misconceptions for a linked student.

**Auth:** Parent

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "student_name": "Jane Doe Jr.",
    "active_count": 3,
    "misconceptions": [
      {
        "concept_title": "Solving One-Step Equations",
        "category": "procedural",
        "description": "Reverses the operation when isolating a variable",
        "frequency": 3,
        "detected_at": "2026-06-19T10:30:00Z"
      }
    ]
  }
}
```

---

### GET /parent/students/{student_id}/reports

List generated reports for a linked student.

**Auth:** Parent

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "report_id": "uuid",
      "report_type": "weekly",
      "generated_at": "2026-06-20T08:00:00Z",
      "summary": "Jane had a productive week. She mastered 2 new concepts in Algebra I and maintained an 83% accuracy rate.",
      "is_read": false
    }
  ]
}
```

---

### GET /parent/students/{student_id}/reports/{report_id}

Get full report details.

**Auth:** Parent

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "report_id": "uuid",
    "student_name": "Jane Doe Jr.",
    "report_type": "weekly",
    "generated_at": "2026-06-20T08:00:00Z",
    "period": {"from": "2026-06-13", "to": "2026-06-20"},
    "summary": "Jane had a productive week. She mastered 2 new concepts in Algebra I and maintained an 83% accuracy rate.",
    "sections": [
      {
        "heading": "What Was Covered",
        "body": "This week Jane worked on 'Solving One-Step Equations' and 'Using Variables in Expressions'."
      },
      {
        "heading": "Strengths",
        "body": "Jane excels at identifying the correct operation for simple equations."
      },
      {
        "heading": "Areas for Improvement",
        "body": "Jane occasionally reverses operations when the variable is on the right side of the equation."
      },
      {
        "heading": "Recommendation",
        "body": "Practice 2–3 additional equations daily where the variable appears on the right side."
      }
    ],
    "metrics": {
      "sessions": 3,
      "time_spent_minutes": 95,
      "concepts_learned": 2,
      "exercises_answered": 12,
      "accuracy": 0.83,
      "mastery_change": "+0.08"
    },
    "recommendations": [
      {"priority": "high", "action": "Practice right-side variable equations", "expected_outcome": "Improve procedural accuracy"},
      {"priority": "medium", "action": "Review fraction basics before next module", "expected_outcome": "Prepare for rational expressions"}
    ],
    "pdf_url": "https://cdn.example.com/reports/weekly-jane-doe-2026-06-20.pdf"
  }
}
```

---

### POST /parent/students/{student_id}/reports/generate

Request on-demand generation of a custom report.

**Auth:** Parent

**Request Body:**
```json
{
  "report_type": "milestone",
  "focus_course_id": "uuid",
  "include_sections": ["mastery", "misconceptions", "recommendations"]
}
```

**Validation Rules:**
| Field | Rule |
|---|---|
| report_type | Required, enum: `weekly` | `monthly` | `milestone` |
| focus_course_id | Optional — if omitted, includes all courses |
| include_sections | Optional — if omitted, includes all sections |

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "report_id": "uuid",
    "report_type": "milestone",
    "generated_at": "2026-06-20T15:00:00Z",
    "status": "generating",
    "estimated_completion_seconds": 15
  }
}
```

---

### GET /parent/students/{student_id}/sessions

Get recent session activity for a linked student.

**Auth:** Parent

**Query Parameters:**
| Param | Type | Description |
|---|---|---|
| `limit` | `integer` | Default: 10, Max: 50 |

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "session_id": "uuid",
      "course_title": "Algebra I",
      "date": "2026-06-20",
      "duration_minutes": 32,
      "concepts_covered": ["What is a Variable?"],
      "exercises_answered": 5,
      "accuracy": 0.8,
      "state": "completed"
    }
  ]
}
```

---

### GET /parent/dashboard

Parent dashboard overview — aggregate data for all linked students.

**Auth:** Parent

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "students": [
      {
        "student_id": "uuid",
        "full_name": "Jane Doe Jr.",
        "overall_mastery_avg": 0.74,
        "active_courses": 2,
        "last_active": "2026-06-20T14:30:00Z",
        "concepts_mastered_this_week": 2,
        "alerts": [
          {"severity": "warning", "message": "Jane is falling behind in Geometry Basics", "course_id": "uuid"}
        ]
      }
    ],
    "aggregate": {
      "total_children": 2,
      "children_with_alerts": 1,
      "unread_reports": 3,
      "weekly_family_avg_accuracy": 0.79
    }
  }
}
```

---

## Error Reference

| HTTP Code | Error Code | When |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Request body fails validation rules |
| 401 | `UNAUTHORIZED` | Missing or expired JWT |
| 403 | `FORBIDDEN` | Authenticated but wrong role |
| 404 | `NOT_FOUND` | Resource does not exist |
| 409 | `CONFLICT` | Duplicate active enrollment, course code conflict |
| 409 | `HAS_ACTIVE_ENROLLMENTS` | Attempting to delete course with active students |
| 422 | `UNPROCESSABLE_ENTITY` | Business rule violation (e.g., resume_last but no prior session) |
| 429 | `RATE_LIMITED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Unexpected server error |

## Authorization Matrix

| Endpoint Group | Admin | Student | Parent | Public |
|---|---|---|---|---|
| `/auth/*` | — | — | — | ✓ |
| `/admin/*` | ✓ | — | — | — |
| `/courses` | CRUD | R | R | — |
| `/modules` | CRUD | R | R | — |
| `/lessons` | CRUD | R | R | — |
| `/concepts` | CRUD | R | R | — |
| `/exercises` | CRUD | R* | — | — |
| `/enrollments` | — | Own | Linked | — |
| `/sessions` | — | Own | — | — |
| `/mastery` | All | Own | Linked | — |
| `/diagnosis` | — | Own | Linked | — |
| `/memory` | — | Own | — | — |
| `/pacing` | — | Own | Linked | — |
| `/parent/*` | — | — | Linked | — |

*R = Read. R* = Read within active session only. CRUD = Create, Read, Update, Delete. Own = own data only. Linked = data of linked students only.
