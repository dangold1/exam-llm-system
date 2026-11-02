# Exam System — CLAUDE.md

## Project Purpose

Live interview assignment. A full-stack auto-graded exam app where a student submits answers, the backend grades them using Azure OpenAI, and the UI displays structured per-question feedback.

---

## Active Stack

| Layer | Technology | Path |
|---|---|---|
| Backend | Python 3, Flask 3, pymongo | `python/server/` |
| Frontend | React 18, Vite, Axios | `python/client/` |
| Database | MongoDB (local, port 27017) | db: `exam_system` |
| AI Grading | Azure OpenAI (GPT-4 deployment) | via `openai` SDK |

**Ignore completely:** `nodejs/` — do not read, modify, or reference any files there.

---

## Exact Paths

```
python/
  server/
    app.py                    # Flask entrypoint
    db/database.py            # MongoDB connection + seed
    routes/questions.py       # GET /questions
    routes/submissions.py     # POST /submit  (add grading here)
    services/grading.py       # NEW — Azure OpenAI grading logic
    requirements.txt
  client/
    src/
      api/examApi.js          # API calls (add fetchSubmission)
      pages/ExamPage.jsx      # Main page (add results display)
      components/             # Question, QuestionList, SubmitButton
      styles/                 # CSS
```

---

## Run Commands

```bash
# Backend (first time)
cd python/server
python -m venv venv
source venv/bin/activate          # Mac/Linux
pip install -r requirements.txt

# Backend (every time)
cd python/server
source venv/bin/activate
python app.py
# Running on http://localhost:5000

# Frontend (first time)
cd python/client
npm install

# Frontend (every time)
cd python/client
npm run dev
# Running on http://localhost:3000
```

---

## Environment Variables — `python/server/.env`

```env
MONGODB_URI=mongodb://localhost:27017/
DB_NAME=exam_system
PORT=5000
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=<key>
AZURE_OPENAI_DEPLOYMENT=<deployment-name>
AZURE_OPENAI_API_VERSION=2024-02-01
```

### Optional: grading reproducibility and debugging

Per-question grades can **differ across runs** for the same answers (model sampling, default temperature on some deployments, validation retries). The pipeline in `routes/submissions.py` and `services/grading_service.py` is deterministic; variance comes from the LLM call in `services/azure_openai_grader.py`.

Optional `python/server/.env` knobs:

- **`GRADING_SEED`** — integer; passed as `seed` on `chat.completions.create` when supported. If Azure returns an error mentioning `seed`, it is retried once without `seed`.
- **`GRADING_SEED_INCLUDE_QUESTION_ID`** — `true` / `1` / `yes` to combine `GRADING_SEED` with `question_id` (mod \(2^{31}-1\)) for per-question stability.
- **`GRADING_LOG_COMPLETION_PREVIEW`** — e.g. `200` to log the first N characters of the model output at INFO (useful for debugging parse issues).

Other tuning variables are documented in comments in `azure_openai_grader.py` (e.g. `GRADING_MAX_COMPLETION_TOKENS`, `GRADING_MAX_WORKERS`, `GRADING_REASONING_EFFORT`, `GRADING_VERBOSITY`). Set root logger to DEBUG to log every completion id and `finish_reason`.

---

## Currently Implemented

- `GET /questions` — returns all questions with `id`, `text`, `rubric`
- `POST /submit` — validates payload, stores `{studentId, answers, submittedAt, graded: false}`, returns `submissionId`
- React ExamPage — loads questions, collects answers, submits, shows brief success toast
- MongoDB seeded with 5 CS questions each with a rubric string

---

## Missing — Assignment Completion Targets

1. **`python/server/services/grading.py`** — call Azure OpenAI with question text + rubric + student answer, return `{score, feedback}` per question
2. **`python/server/routes/submissions.py`** — after inserting raw submission, call grading service, update document with `{graded: true, gradedAt, grades: [{questionId, score, feedback}]}`
3. **`python/server/requirements.txt`** — add `openai>=1.0.0`
4. **`GET /submission/<submission_id>`** — retrieve graded submission by ID
5. **`python/client/src/api/examApi.js`** — add `fetchSubmission(submissionId)`
6. **`python/client/src/pages/ExamPage.jsx`** — after submit, poll/fetch graded result, display `score` + `feedback` per question
7. **`python/client/src/components/GradeResult.jsx`** — optional component for per-question grade display

---

## Coding Rules

- Thin routes: business logic lives in `services/`, not in route handlers
- No new files unless strictly necessary
- No auth, no caching, no pagination — out of scope
- Validate only at system boundary (request payload); trust internal data
- `graded: false` already stored on submission — update in-place after grading
- Return `submissionId` from POST /submit so frontend can fetch results
- Azure OpenAI prompt must include: question text, rubric, student answer; request JSON response `{score: 0-10, feedback: "string"}`
- Frontend stays simple: no routing library changes, no state management beyond useState

---

## Routing Guidance

| Task | Skill |
|---|---|
| Adding/modifying Flask routes or DB logic | `.claude/skills/python-backend.md` |
| Grading service / Azure OpenAI integration | `.claude/skills/azure-openai-grading.md` |
| React UI changes (display grades, new components) | `.claude/skills/react-client.md` |
| .env setup, install commands, ports | `.claude/skills/env-and-commands.md` |
| Verifying the full flow end-to-end | `.claude/skills/verification-checklist.md` |
| Full project orientation | `.claude/skills/project-map.md` |
