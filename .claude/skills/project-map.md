# Skill: project-map

## Purpose
Full orientation for this repo. Read this first when starting a new session or before any cross-cutting change.

## When to Use
- First message of a session touching multiple layers
- Before planning a new feature that spans backend + frontend
- When uncertain which file owns a responsibility

## Repo Paths in Scope
All of `python/server/` and `python/client/`. Ignore `nodejs/`.

## Current File Ownership

| Responsibility | File |
|---|---|
| Flask app setup, CORS, startup | `python/server/app.py` |
| MongoDB connect + seed questions | `python/server/db/database.py` |
| Fetch questions endpoint | `python/server/routes/questions.py` |
| Submit answers + grading trigger | `python/server/routes/submissions.py` |
| Azure OpenAI grading logic | `python/server/services/grading.py` (to create) |
| API base URL + all HTTP calls | `python/client/src/api/examApi.js` |
| Main exam page, state, submit flow | `python/client/src/pages/ExamPage.jsx` |
| Question display component | `python/client/src/components/Question.jsx` |
| List wrapper | `python/client/src/components/QuestionList.jsx` |
| Submit button | `python/client/src/components/SubmitButton.jsx` |

## Data Models

**Question (MongoDB `questions` collection):**
```json
{ "id": 1, "text": "...", "rubric": "..." }
```

**Submission (MongoDB `submissions` collection):**
```json
{
  "studentId": "...",
  "answers": [{ "questionId": 1, "answer": "..." }],
  "submittedAt": "ISODate",
  "graded": false,
  "gradedAt": "ISODate",
  "grades": [{ "questionId": 1, "score": 8, "feedback": "..." }]
}
```

## API Contract

| Method | Path | Request | Response |
|---|---|---|---|
| GET | /questions | — | `{success, questions: [{id, text, rubric}]}` |
| POST | /submit | `{studentId, answers[]}` | `{success, submissionId}` |
| GET | /submission/:id | — | `{success, submission: {..., grades}}` |

## Done Definition
All three endpoints working, submission document includes `grades` array after POST /submit, frontend displays grades.
