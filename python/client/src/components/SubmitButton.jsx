import React from 'react'
import '../styles/SubmitButton.css'

function SubmitButton({ onClick, disabled, submitting }) {
  return (
    <button
      className="submit-button"
      onClick={onClick}
      disabled={disabled}
    >
      {submitting ? 'Submitting...' : 'Submit Exam'}
    </button>
  )
}

export default SubmitButton

