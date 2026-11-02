# Skill: verification-checklist

## Purpose
End-to-end checklist to confirm the full grading flow is working before claiming done.

## When to Use
- Before marking any grading-related task complete
- After implementing grading service or submission route changes
- After frontend grade display changes

## Manual Verification Steps

### 1. Backend Health
```bash
curl http://localhost:5000/
# Expected: {"message": "Auto-Graded Exam API"}

curl http://localhost:5000/questions
# Expected: {"success": true, "questions": [...5 items with id/text/rubric...]}
```

### 2. Submit and Grade
```bash
curl -X POST http://localhost:5000/submit \
  -H "Content-Type: application/json" \
  -d '{
    "studentId": "test123",
    "answers": [
      {"questionId": 1, "answer": "Polymorphism allows objects to take many forms..."},
      {"questionId": 2, "answer": "SQL is structured, NoSQL is schemaless..."},
      {"questionId": 3, "answer": "HTTP is stateless, GET retrieves, POST submits..."},
      {"questionId": 4, "answer": "Git tracks changes, branches allow parallel work..."},
      {"questionId": 5, "answer": "Big O describes worst-case complexity growth..."}
    ]
  }'
# Expected: {"success": true, "submissionId": "<objectid>"}
```

### 3. Retrieve Graded Submission
```bash
curl http://localhost:5000/submission/<submissionId from step 2>
# Expected:
# {
#   "success": true,
#   "submission": {
#     "studentId": "test123",
#     "graded": true,
#     "gradedAt": "...",
#     "grades": [
#       {"questionId": 1, "score": <0-10>, "feedback": "..."},
#       ...5 items
#     ]
#   }
# }
```

### 4. MongoDB Verification
```bash
mongosh
use exam_system
db.submissions.findOne({}).grades
# Must be array of 5 items, each with questionId/score/feedback
```

### 5. Frontend Verification
1. Open http://localhost:3000
2. Enter any student ID
3. Fill in answers for all 5 questions
4. Click Submit
5. Grades section should appear with score + feedback per question
6. No console errors, no blank screen

## Checklist

- [ ] GET /questions returns 5 questions with rubrics
- [ ] POST /submit returns submissionId immediately (or after grading)
- [ ] Submission in MongoDB has `graded: true` and `grades` array
- [ ] GET /submission/:id returns full submission with grades
- [ ] Each grade has `questionId`, `score` (int 0-10), `feedback` (non-empty string)
- [ ] Frontend displays grades after submit without page reload
- [ ] No unhandled exceptions in Flask logs
- [ ] Azure OpenAI error does not crash the submission endpoint (fallback grade returned)

## Done Definition
All checklist items pass. Curl tests match expected responses. Frontend shows grades.
