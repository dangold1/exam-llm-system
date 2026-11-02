# Skill: react-client

## Purpose
Guide for all React + Vite changes in `python/client/`.

## When to Use
- Adding grade/feedback display after submission
- Adding new API calls (fetchSubmission)
- Creating new components (e.g., GradeResult)
- Styling changes

## Repo Paths in Scope
```
python/client/src/
  api/examApi.js
  pages/ExamPage.jsx
  components/Question.jsx
  components/QuestionList.jsx
  components/SubmitButton.jsx
  components/GradeResult.jsx    # new if needed
  styles/
```

## Files Likely to Change
- `api/examApi.js` — add `fetchSubmission(submissionId)`
- `pages/ExamPage.jsx` — show grades after submit
- `components/` — add `GradeResult.jsx` for per-question grade display (optional, keep simple)

## Adding fetchSubmission to examApi.js

```js
export const fetchSubmission = async (submissionId) => {
    const response = await axios.get(`${API_BASE_URL}/submission/${submissionId}`)
    return response.data
}
```

## ExamPage Flow After Submit

1. `POST /submit` returns `submissionId`
2. Store `submissionId` in state
3. Call `fetchSubmission(submissionId)` to get `submission.grades`
4. Set `grades` state, render per-question feedback

```jsx
const [grades, setGrades] = useState(null);

const handleSubmit = async () => {
  // ... existing validation ...
  const result = await submitAnswers(studentId, answersArray);
  const graded = await fetchSubmission(result.submissionId);
  setGrades(graded.submission.grades);
  setSubmitted(true);
};
```

## Grade Display Pattern

Keep it simple — inline in ExamPage or a minimal GradeResult component:

```jsx
{grades && (
  <div className="grades-section">
    <h2>Results</h2>
    {grades.map(g => (
      <div key={g.questionId} className="grade-item">
        <strong>Q{g.questionId}:</strong> {g.score}/10
        <p>{g.feedback}</p>
      </div>
    ))}
  </div>
)}
```

## Best-Practice Constraints
- No new routing library — single page is fine
- No Redux or context — useState is sufficient
- Keep components small and interview-readable
- API_BASE_URL stays `http://localhost:5000`
- Do not add TypeScript — keep JSX
- Loading/error states: show simple text, not spinner libraries

## Expected Output / Done Definition
- After submission, grades section appears below submit button
- Each question shows score (0-10) and feedback string
- No page reload required; state-driven display
