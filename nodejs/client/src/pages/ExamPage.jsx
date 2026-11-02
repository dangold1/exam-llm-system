import React, { useState, useEffect } from "react";
import QuestionList from "../components/QuestionList";
import SubmitButton from "../components/SubmitButton";
import { fetchQuestions, submitAnswers } from "../api/examApi";
import "../styles/ExamPage.css";

function ExamPage() {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [studentId, setStudentId] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadQuestions();
  }, []);

  const loadQuestions = async () => {
    try {
      setLoading(true);
      const data = await fetchQuestions();
      setQuestions(data.questions);

      // Initialize answers object
      const initialAnswers = {};
      data.questions.forEach((q) => {
        initialAnswers[q.id] = "";
      });
      setAnswers(initialAnswers);
    } catch (err) {
      setError(
        "Failed to load questions. Please make sure the backend is running."
      );
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionId, value) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: value,
    }));
  };

  const handleSubmit = async () => {
    if (!studentId.trim()) {
      alert("Please enter your Student ID");
      return;
    }

    // Convert answers object to array format
    const answersArray = Object.entries(answers).map(
      ([questionId, answer]) => ({
        questionId: parseInt(questionId),
        answer: answer,
      })
    );

    try {
      setSubmitting(true);
      await submitAnswers(studentId, answersArray);
      setSubmitted(true);
      setTimeout(() => setSubmitted(false), 3000);
    } catch (err) {
      setError("Failed to submit answers. Please try again.");
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading questions...</div>;
  }

  if (error && questions.length === 0) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="exam-page">
      <header className="exam-header">
        <h1>Auto-Graded Exam System</h1>
        <p>Answer all questions below and submit when ready</p>
      </header>

      <div className="student-id-section">
        <label htmlFor="studentId">Student ID:</label>
        <input
          id="studentId"
          type="text"
          value={studentId}
          onChange={(e) => setStudentId(e.target.value)}
          placeholder="Enter your student ID"
          disabled={submitting}
        />
      </div>

      <QuestionList
        questions={questions}
        answers={answers}
        onAnswerChange={handleAnswerChange}
        disabled={submitting}
      />

      <SubmitButton
        onClick={handleSubmit}
        disabled={submitting || !studentId.trim()}
        submitting={submitting}
      />

      {submitted && (
        <div className="success-message">✓ Submitted successfully!</div>
      )}

      {error && questions.length > 0 && (
        <div className="error-message">{error}</div>
      )}
    </div>
  );
}

export default ExamPage;

