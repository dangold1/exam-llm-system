import React from 'react'
import '../styles/Question.css'

function Question({ question, answer, onAnswerChange, disabled }) {
  return (
    <div className="question">
      <div className="question-header">
        <span className="question-number">Question {question.id}</span>
      </div>
      <div className="question-text">{question.text}</div>
      <textarea
        className="answer-input"
        value={answer}
        onChange={(e) => onAnswerChange(e.target.value)}
        placeholder="Type your answer here..."
        rows="6"
        disabled={disabled}
      />
    </div>
  )
}

export default Question

