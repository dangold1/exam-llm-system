## Current Focus
Exam System — Python Flask + React. Preparing shared memory context for Azure OpenAI grading assignment.

## Recent Changes
- Created root CLAUDE.md with full project spec
- Created .claude/skills/ with 6 focused skill files
- Mapped existing Python-only project structure

## Next Steps
- Implement `python/server/services/grading.py` (Azure OpenAI grading service)
- Update `python/server/routes/submissions.py` to call grading and update submission doc
- Add `openai>=1.0.0` to `python/server/requirements.txt`
- Add `GET /submission/<id>` endpoint
- Update `python/client/src/api/examApi.js` with `fetchSubmission`
- Update `python/client/src/pages/ExamPage.jsx` to display grades

## Decisions
- Active stack: Python Flask + React Vite only. nodejs/ is ignored.
- Grading is synchronous in POST /submit (simple, interview-appropriate)
- No auth, no pagination, no caching — out of scope
- Azure OpenAI credentials from .env only

## Learnings
- Questions already include `rubric` field in MongoDB — no schema change needed
- Submission doc already has `graded: false` flag — update in-place after grading
- `python/client` and `nodejs/client` are identical frontends — only touch `python/client`

## References
- Plan: N/A
- Design: N/A
- Skills: .claude/skills/
- Project map: .claude/skills/project-map.md

## Blockers
None

## Session Settings
AUTO_PROCEED: false

## Last Updated
2026-04-14
