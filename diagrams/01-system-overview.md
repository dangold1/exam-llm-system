# 01 — System Overview

## Runtime topology

```mermaid
flowchart LR
    Browser["Browser<br/>React + Vite<br/>localhost:3000"]
    Flask["Flask API<br/>localhost:5001"]
    Mongo[("MongoDB<br/>localhost:27017<br/>db: exam_system")]
    Azure["Azure OpenAI<br/>deployment: gpt-5-nano"]

    Browser -- "GET /questions" --> Flask
    Browser -- "POST /submit" --> Flask
    Browser -- "GET /submission/:id" --> Flask
    Flask -- "find / insert / update" --> Mongo
    Flask -- "chat.completions.create" --> Azure
```

## Layered backend architecture

```mermaid
flowchart TB
    subgraph Route["Route layer (thin)"]
        SubR["routes/submissions.py<br/>POST /submit<br/>GET /submission/:id"]
        QstR["routes/questions.py<br/>GET /questions"]
    end

    subgraph Service["Service layer (orchestration)"]
        GS["GradingService<br/>fan-out, fallback, metadata"]
    end

    subgraph Adapter["Adapter layer (transport + retry)"]
        Grader["AzureOpenAIGrader<br/>chat.completions, JSON repair, retries"]
    end

    subgraph Pure["Pure helpers (no I/O)"]
        Prompt["prompt_builder.py<br/>system + user messages, few-shot"]
        Rubric["rubric_format.py<br/>raw rubric → numbered criteria"]
        Models["models.py<br/>Pydantic GradeResult / GradingError"]
    end

    subgraph Infra["Infra"]
        DB["db/database.py<br/>MongoClient + seed"]
    end

    SubR --> GS
    SubR --> DB
    QstR --> DB
    GS --> Grader
    GS --> Rubric
    GS --> Models
    Grader --> Prompt
    Grader --> Models
    Grader --> Azure[(Azure OpenAI)]
```

### Why this layering matters (interview talking points)

| Layer | Responsibility | Knows about |
|---|---|---|
| Route | HTTP shape, status codes, request validation | Flask, JSON, blueprint |
| Service | Business orchestration, fallback policy, metadata | Grader interface, models |
| Adapter | Azure transport, retries, JSON repair | OpenAI SDK, retry/backoff |
| Pure helpers | Deterministic transforms | Strings + Pydantic only |
| Infra | DB connection + seed | pymongo |

**Test isolation**: `GradingService` is unit-testable by injecting a fake `AzureOpenAIGrader`.
**Swap-ability**: replacing Azure OpenAI with another provider only touches the adapter.
**Fail-safe path**: any exception bubbling out of the grader is caught by the service and turned
into a structured fallback `GradeResult`, so persistence never gets garbage.

## Frontend layering

```mermaid
flowchart TB
    Page["pages/ExamPage.jsx<br/>state machine, submit orchestration"]
    Api["api/examApi.js<br/>fetchQuestions / submitAnswers / fetchSubmission"]
    QList["components/QuestionList.jsx"]
    Q["components/Question.jsx"]
    Btn["components/SubmitButton.jsx"]
    GR["components/GradeResult.jsx"]

    Page --> Api
    Page --> QList --> Q
    Page --> Btn
    Page --> GR
```

The page owns all state; components are dumb and re-render from props. The API layer is the
**only** place HTTP details live — switching base URL, adding auth, or moving to fetch is a
one-file change.

## File-to-responsibility map

```
python/server/
  app.py                          Flask bootstrap, CORS, blueprint registration
  db/database.py                  MongoClient singleton, seed 5 sample questions
  routes/questions.py             GET /questions
  routes/submissions.py           POST /submit, GET /submission/:id (thin)
  services/
    models.py                     Pydantic: GradeResult (validation rules), GradingError
    prompt_builder.py             System prompt + few-shot + schema-repair message
    rubric_format.py              Normalize raw rubric strings into numbered criteria
    azure_openai_grader.py        AzureOpenAIGrader: client, retries, JSON extraction
    grading_service.py            GradingService: per-question fan-out + fallback
  requirements.txt                Flask, flask-cors, pymongo, python-dotenv, openai, pydantic

python/client/src/
  api/examApi.js                  3 functions, 1 base URL
  pages/ExamPage.jsx              State machine: loading → answering → analyzing → graded
  components/Question.jsx         Single question + textarea
  components/QuestionList.jsx     Maps questions to Question
  components/SubmitButton.jsx     Submit button with submitting state
  components/GradeResult.jsx      Per-question score card; "failed" badge if grading_status='failed'
  styles/*.css                    Plain CSS, no UI library
  vite.config.js                  Dev server :3000, proxy targets :5001
```

## Configuration boundary

All config flows through environment variables loaded from `python/server/.env`:

```
MONGODB_URI, DB_NAME, PORT
AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY (or AZURE_OPENAI_AD_TOKEN),
AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_API_VERSION
GRADING_MAX_WORKERS (optional), GRADING_MAX_COMPLETION_TOKENS (optional),
GRADING_REASONING_EFFORT (optional), GRADING_VERBOSITY (optional),
GRADING_SEED (optional, deterministic grading aid)
```

No secrets in code, no secrets in repo, no secrets in the frontend bundle.
