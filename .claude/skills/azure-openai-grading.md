# Skill: azure-openai-grading

## Purpose
Implement the grading service that calls Azure OpenAI to score and provide feedback on student answers.

## When to Use
- Creating `python/server/services/grading.py`
- Changing prompt structure or response parsing
- Debugging grading failures or malformed responses

## Repo Paths in Scope
```
python/server/services/grading.py    # new file
python/server/routes/submissions.py  # calls grading service
python/server/requirements.txt       # add openai>=1.0.0
python/server/.env                   # AZURE_OPENAI_* vars
```

## Required Env Vars
```env
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.co/
AZURE_OPENAI_API_KEY=<key>
AZURE_OPENAI_DEPLOYMENT=<deployment-name>
AZURE_OPENAI_API_VERSION=2024-02-01
```

## Grading Service Pattern

```python
# python/server/services/grading.py
import os
import json
from openai import AzureOpenAI

def get_openai_client():
    return AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
    )

def grade_answer(question_text: str, rubric: str, student_answer: str) -> dict:
    """Returns {score: int (0-10), feedback: str}"""
    client = get_openai_client()
    prompt = f"""You are an exam grader. Grade the following student answer.

Question: {question_text}
Grading Rubric: {rubric}
Student Answer: {student_answer}

Respond with valid JSON only, no extra text:
{{"score": <integer 0-10>, "feedback": "<concise feedback string>"}}"""

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    content = response.choices[0].message.content.strip()
    return json.loads(content)

def grade_submission(questions: list, answers: list) -> list:
    """
    questions: [{id, text, rubric}, ...]
    answers:   [{questionId, answer}, ...]
    returns:   [{questionId, score, feedback}, ...]
    """
    question_map = {q["id"]: q for q in questions}
    grades = []
    for ans in answers:
        q = question_map.get(ans["questionId"])
        if not q:
            grades.append({"questionId": ans["questionId"], "score": 0, "feedback": "Question not found"})
            continue
        try:
            result = grade_answer(q["text"], q["rubric"], ans["answer"])
            grades.append({"questionId": ans["questionId"], "score": result["score"], "feedback": result["feedback"]})
        except Exception as e:
            grades.append({"questionId": ans["questionId"], "score": 0, "feedback": f"Grading error: {str(e)}"})
    return grades
```

## Integration into submissions.py

After inserting the raw submission, fetch questions and call `grade_submission`:

```python
from services.grading import grade_submission
from datetime import datetime

# After result = submissions_collection.insert_one(submission)
questions = list(db.questions.find({}, {'_id': 0}))
grades = grade_submission(questions, answers)
db.submissions.update_one(
    {"_id": result.inserted_id},
    {"$set": {"graded": True, "gradedAt": datetime.utcnow(), "grades": grades}}
)
```

## Best-Practice Constraints
- Single AzureOpenAI client instantiation per request is fine at interview scale
- Always parse JSON from model response; wrap in try/except per question
- temperature=0.2 for deterministic grading
- Do not expose raw OpenAI errors to the client — log and return a fallback grade
- Keep `grade_answer` and `grade_submission` as pure functions (no DB access)

## Expected Output / Done Definition
- `grade_submission()` returns a list with one entry per answer
- Each entry has `questionId`, `score` (int 0-10), `feedback` (string)
- Submission document in MongoDB updated with `grades`, `graded: true`, `gradedAt`
- If Azure OpenAI is unavailable, function returns fallback grades without crashing
