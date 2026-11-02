## User Standards
- Python Flask backend only — nodejs/ is permanently ignored
- Thin routes: business logic in services/, not route handlers
- Consistent API response shape: {success: bool, ...payload} or {success: false, error: "..."}
- MongoDB ObjectId must be str() before JSON serialization
- No auth, no caching, no pagination — out of assignment scope
- React stays simple: useState only, no routing library changes, no TypeScript
- Validate only at system boundary (request payload)

## Common Gotchas
- `bson.ObjectId` import needed for GET /submission/<id> — `from bson import ObjectId`
- Azure OpenAI SDK is `openai>=1.0.0` (new SDK), not the old 0.x API
- AzureOpenAI client uses `azure_endpoint`, not `api_base`
- Model response must be parsed as JSON — wrap in try/except per question
- `datetime.utcnow()` must be `.isoformat()` before returning in JSON response
- Questions rubric field already exists in MongoDB — no migration needed
- `python/client` and `nodejs/client` are identical — only ever touch `python/client`

## Project SKILL_HINTS
- Backend changes: .claude/skills/python-backend.md
- Azure OpenAI / grading: .claude/skills/azure-openai-grading.md
- Frontend changes: .claude/skills/react-client.md
- Setup / env / commands: .claude/skills/env-and-commands.md
- Verification: .claude/skills/verification-checklist.md
- Full orientation: .claude/skills/project-map.md

## Last Updated
2026-04-14
