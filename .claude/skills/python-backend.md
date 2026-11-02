# Skill: python-backend

## Purpose
Guide for all Flask + MongoDB changes in `python/server/`.

## When to Use
- Modifying routes (questions, submissions)
- Adding new routes (e.g., GET /submission/<id>)
- Changing DB schema or queries
- Adding new service files

## Repo Paths in Scope
```
python/server/
  app.py
  db/database.py
  routes/questions.py
  routes/submissions.py
  routes/__init__.py
  services/grading.py      # to create
  requirements.txt
```

## Files Likely to Change
- `routes/submissions.py` — add grading call + update submission doc
- `routes/questions.py` — unlikely to change
- `db/database.py` — only if schema changes are needed
- `app.py` — only if new blueprint is added
- `requirements.txt` — add `openai>=1.0.0`

## Best-Practice Constraints
- Routes stay thin: extract grading logic into `services/grading.py`
- One blueprint per route file; register in `app.py`
- Use `get_db()` from `db/database.py`; do not create new MongoClient instances
- Return consistent shape: `{success: bool, ...payload}` or `{success: false, error: "..."}`
- MongoDB ObjectId must be `str(result.inserted_id)` before JSON serialization
- `graded: false` is set on insert; update in-place with `update_one` after grading
- Do not add auth middleware or rate limiting — out of scope

## Adding GET /submission/<submission_id>

```python
from bson import ObjectId

@submissions_bp.route('/submission/<submission_id>', methods=['GET'])
def get_submission(submission_id):
    try:
        db = get_db()
        doc = db.submissions.find_one({"_id": ObjectId(submission_id)})
        if not doc:
            return jsonify({"success": False, "error": "Not found"}), 404
        doc["_id"] = str(doc["_id"])
        doc["submittedAt"] = doc["submittedAt"].isoformat()
        if doc.get("gradedAt"):
            doc["gradedAt"] = doc["gradedAt"].isoformat()
        return jsonify({"success": True, "submission": doc}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
```

## Expected Output / Done Definition
- `POST /submit` returns `submissionId` and submission in DB has `grades` array populated
- `GET /submission/<id>` returns full document including grades
- No unhandled exceptions; all errors return `{success: false, error: "..."}`
