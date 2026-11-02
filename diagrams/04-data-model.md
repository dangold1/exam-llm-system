# 04 — Data Model & Contracts

The shapes that travel between layers. Same JSON contract, frontend to MongoDB.

## API contracts

```mermaid
flowchart LR
    subgraph Client
        F1["fetchQuestions()"]
        F2["submitAnswers(studentId, answers)"]
        F3["fetchSubmission(id)"]
    end
    subgraph Server
        E1["GET /questions"]
        E2["POST /submit"]
        E3["GET /submission/:id"]
    end

    F1 --> E1
    F2 --> E2
    F3 --> E3
```

### `GET /questions`

```json
{
  "success": true,
  "questions": [
    { "id": 1, "text": "Explain polymorphism...", "rubric": "Should mention: ..." }
  ]
}
```

### `POST /submit`

Request:
```json
{
  "studentId": "abc123",
  "answers": [
    { "questionId": 1, "answer": "Polymorphism lets..." }
  ]
}
```

Response 201 (graded synchronously, inline):
```json
{
  "success": true,
  "status": "graded",
  "submissionId": "65f0a1...",
  "graded": true,
  "totalScore": 34,
  "maxScore": 50,
  "grades": [ /* GradeResult[] */ ]
}
```

Response 502 (grading service totally failed, submission stored ungraded):
```json
{
  "success": false,
  "status": "grading_error",
  "submissionId": "65f0a1...",
  "graded": false,
  "totalScore": null,
  "maxScore": null,
  "grades": null,
  "error": "Grading unavailable: <Type>"
}
```

### `GET /submission/<submission_id>`

```json
{
  "success": true,
  "submission": {
    "_id": "65f0a1...",
    "studentId": "abc123",
    "submittedAt": "2026-04-15T12:00:00",
    "gradedAt":   "2026-04-15T12:00:04",
    "graded": true,
    "answers":  [ { "questionId": 1, "answer": "..." } ],
    "grades":   [ /* GradeResult[] */ ],
    "totalScore": 34,
    "maxScore": 50,
    "model": {
      "provider": "azure-openai",
      "deployment": "gpt-5-nano",
      "api_version": "2024-12-01-preview"
    }
  }
}
```

`400` invalid id, `404` not found, `500` unexpected.

## `GradeResult` JSON (the unit of grading)

```json
{
  "question_id": 1,
  "score": 7,
  "max_score": 10,
  "grading_status": "ok",
  "feedback": "Covered inheritance and overriding; missed concrete code example.",
  "matched_criteria": ["inheritance", "method overriding"],
  "missed_criteria": ["code example"]
}
```

Validated by `services/models.py :: GradeResult` (Pydantic v2). Constraints:

| Field | Rule |
|---|---|
| `score` | int, `0 ≤ score ≤ max_score` |
| `max_score` | int, `1..100` |
| `grading_status` | `"ok"` \| `"failed"` |
| `feedback` | non-empty, ≤ 500 chars |
| `matched_criteria` | ≤ 20 items, each ≤ 160 chars, trimmed, non-empty |
| `missed_criteria` | same constraints |
| disjointness | `matched_criteria` and `missed_criteria` must not share an item |

Fallback grade (per-question failure) keeps the same shape:
```json
{
  "question_id": 3,
  "score": 0,
  "max_score": 10,
  "grading_status": "failed",
  "feedback": "Grading unavailable: transient: APITimeoutError",
  "matched_criteria": [],
  "missed_criteria": []
}
```

## MongoDB collections — `db: exam_system`

```mermaid
erDiagram
    QUESTIONS ||..o{ SUBMISSION_ANSWERS : "referenced by id"
    QUESTIONS {
        int id PK
        string text
        string rubric
    }
    SUBMISSIONS {
        ObjectId _id PK
        string studentId
        Date submittedAt
        Date gradedAt
        bool graded
        array answers
        array grades
        int totalScore
        int maxScore
        object model
    }
    SUBMISSION_ANSWERS {
        int questionId
        string answer
    }
    SUBMISSION_GRADES {
        int question_id
        int score
        int max_score
        string grading_status
        string feedback
        array matched_criteria
        array missed_criteria
    }
    SUBMISSIONS ||--o{ SUBMISSION_ANSWERS : "answers[]"
    SUBMISSIONS ||--o{ SUBMISSION_GRADES  : "grades[]"
```

`questions` is seeded by `db/database.py :: init_db()` on first run with 5 CS questions
(polymorphism, SQL vs NoSQL, HTTP, Git, Big-O).

## Lifecycle of a submission document

```mermaid
sequenceDiagram
    participant R as routes/submissions.py
    participant DB as MongoDB
    participant GS as GradingService

    R->>DB: insert_one({ studentId, answers, submittedAt, graded:false })
    DB-->>R: ObjectId
    R->>GS: grade_submission(questions, answers)
    GS-->>R: List[GradeResult]
    R->>DB: update_one({_id}, $set { graded:true, gradedAt, grades, totalScore, maxScore, model })
    Note over DB: Single update — no intermediate "partial" doc state.
```

If `GradingService` raises (rare, only env/init crashes), the document remains `graded:false`
and is reachable via `GET /submission/:id` for retry tooling — no orphan state and no corrupted
grades persisted.

## Why snake_case in `grades[]` but camelCase elsewhere

`grades[]` items mirror the **Pydantic schema**, which mirrors the **LLM JSON schema**. Keeping
those three the same shape removes a translation layer and keeps the contract one-to-one. The
surrounding submission fields (`studentId`, `submittedAt`, `gradedAt`, `totalScore`, `maxScore`)
follow the existing JS-style camelCase the route already used. The frontend reads both naturally.
