# 02 — User Flow (Questions & Answers)

The student-facing flow from "page load" to "see graded results", with both the UI state machine
and the network sequence.

## High-level journey

```mermaid
flowchart LR
    A["Open<br/>localhost:3000"] --> B["Load questions<br/>(GET /questions)"]
    B --> C["Enter Student ID"]
    C --> D["Answer 5 open-ended<br/>questions in textareas"]
    D --> E["Click Submit"]
    E --> F["Backend grades<br/>via Azure OpenAI"]
    F --> G["Render per-question<br/>score + feedback"]
    G --> H["Take Exam Again<br/>(reset state)"]
    H --> C
```

## Frontend state machine — `ExamPage.jsx`

```mermaid
stateDiagram-v2
    [*] --> loading
    loading --> answering: questions fetched
    loading --> error: fetch failed
    answering --> analyzing: handleSubmit() (studentId valid)
    answering --> answering: typing in textarea / studentId
    analyzing --> graded: /submit returns success + grades
    analyzing --> graded: fallback fetch /submission/:id ok
    analyzing --> error: network or server error
    graded --> answering: handleRetake() resets state
    error --> answering: user retries
```

State variables in the page:

| Variable | Meaning |
|---|---|
| `questions` | Array from GET /questions |
| `answers` | `{ [questionId]: text }` map keyed by question id |
| `studentId` | Required before submit is enabled |
| `loading` | Initial questions fetch |
| `submitting` | POST /submit in flight |
| `grading` | After submit returned, before grades are bound to state |
| `gradedSubmission` | `{ studentId, totalScore, maxScore, grades[] }` once available |
| `error` | Last user-facing error string |

`analyzing = submitting || grading` drives a full-screen "Analyzing Exam" overlay so the user
gets one consistent loading affordance for the whole submit-and-grade round-trip.

## Network sequence — happy path

```mermaid
sequenceDiagram
    autonumber
    actor U as Student
    participant UI as ExamPage
    participant API as examApi.js
    participant FL as Flask /submit
    participant DB as MongoDB
    participant GS as GradingService
    participant AZ as Azure OpenAI

    U->>UI: Load page
    UI->>API: fetchQuestions()
    API->>FL: GET /questions
    FL->>DB: questions.find({}, {_id:0})
    DB-->>FL: [5 questions]
    FL-->>API: { success, questions }
    API-->>UI: render QuestionList

    U->>UI: Type studentId + 5 answers
    U->>UI: Click Submit
    UI->>API: submitAnswers(studentId, answers[])
    API->>FL: POST /submit { studentId, answers }
    FL->>DB: submissions.insert_one({ graded:false, ... })
    DB-->>FL: ObjectId
    FL->>GS: grade_submission(questions, answers)
    par per-question (ThreadPool, capped)
        GS->>AZ: chat.completions.create (Q1)
        GS->>AZ: chat.completions.create (Q2)
        GS->>AZ: ...
    end
    AZ-->>GS: JSON grades
    GS-->>FL: [GradeResult, ...]
    FL->>DB: submissions.update_one($set graded, grades, totals, model)
    FL-->>API: { success, submissionId, graded, totalScore, maxScore, grades }
    API-->>UI: setGradedSubmission(...)
    UI-->>U: Show GradeResult cards + total
```

The frontend prefers the inline `grades` returned by `/submit` (single round-trip).
If `/submit` doesn't carry them (legacy / partial response), it falls back to
`fetchSubmission(submissionId)` so the contract stays compatible.

## Failure paths the user can see

```mermaid
flowchart TB
    Submit["POST /submit"]
    Submit -->|HTTP 400 missing field| BadReq["Inline error message<br/>'Failed to submit and grade'"]
    Submit -->|HTTP 502 grading service crash| Crash["Inline error message<br/>'Grading unavailable: ...'"]
    Submit -->|HTTP 201, grading partially failed| Partial["Show graded view;<br/>failed questions render with<br/>purple 'grading failed' badge"]
    Submit -->|HTTP 201 success| Ok["Show graded view, all green/orange/red<br/>by score ratio"]
```

Key UX rule: the user **always** lands on a deterministic next state. There is no infinite spinner
and no silent failure; every Azure error becomes either an HTTP 502 (total) or a per-question
fallback grade (partial) that the UI clearly labels.

## Component data flow

```mermaid
flowchart LR
    Page["ExamPage<br/>(stateful)"]
    QL["QuestionList<br/>(props)"]
    Q["Question<br/>(props)"]
    SB["SubmitButton<br/>(props)"]
    GR["GradeResult<br/>(props)"]

    Page -- "questions, answers, onChange" --> QL --> Q
    Page -- "onClick, disabled, submitting" --> SB
    Page -- "grade, questionText (per item)" --> GR
```

All children are presentational. Adding a new field to grade output (e.g. confidence) only changes
`GradeResult.jsx` and `models.py` — no plumbing through intermediate components.
