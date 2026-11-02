import React from 'react'
import '../styles/GradeResult.css'

function GradeResult({ grade, questionText }) {
  const failed = grade.grading_status === 'failed'
  const pct = grade.max_score ? grade.score / grade.max_score : 0
  const tone = failed ? 'failed' : pct >= 0.8 ? 'good' : pct >= 0.5 ? 'ok' : 'low'

  return (
    <div className={`grade-result grade-${tone}`}>
      <div className="grade-header">
        <span className="grade-qid">Question {grade.question_id}</span>
        <span className="grade-score">
          {grade.score} / {grade.max_score}
          {failed && <span className="grade-failed-badge"> grading failed</span>}
        </span>
      </div>
      {questionText && <div className="grade-qtext">{questionText}</div>}
      <div className="grade-feedback">{grade.feedback}</div>
      {(grade.matched_criteria?.length > 0 || grade.missed_criteria?.length > 0) && (
        <div className="grade-criteria">
          {grade.matched_criteria?.length > 0 && (
            <div className="criteria matched">
              <strong>Matched:</strong> {grade.matched_criteria.join(', ')}
            </div>
          )}
          {grade.missed_criteria?.length > 0 && (
            <div className="criteria missed">
              <strong>Missed:</strong> {grade.missed_criteria.join(', ')}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default GradeResult
