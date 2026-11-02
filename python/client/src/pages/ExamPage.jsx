import React, { useState, useEffect } from "react";
import QuestionList from "../components/QuestionList";
import SubmitButton from "../components/SubmitButton";
import GradeResult from "../components/GradeResult";
import { fetchQuestions, submitAnswers, fetchSubmission } from "../api/examApi";
import "../styles/ExamPage.css";
import "../styles/GradeResult.css";

function ExamPage() {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [studentId, setStudentId] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [grading, setGrading] = useState(false);
  const [error, setError] = useState(null);
  const [gradedSubmission, setGradedSubmission] = useState(null);

  useEffect(() => {
    loadQuestions();
  }, []);

  const loadQuestions = async () => {
    try {
      setLoading(true);
      const data = await fetchQuestions();
      setQuestions(data.questions);
      const initialAnswers = {};
      data.questions.forEach((q) => {
        initialAnswers[q.id] = "";
      });
      setAnswers(initialAnswers);
    } catch (err) {
      setError("Failed to load questions. Please make sure the backend is running.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionId, value) => {
    setAnswers((prev) => ({ ...prev, [questionId]: value }));
  };

  const handleSubmit = async () => {
    if (!studentId.trim()) {
      alert("Please enter your Student ID");
      return;
    }

    const answersArray = Object.entries(answers).map(([questionId, answer]) => ({
      questionId: parseInt(questionId),
      answer,
    }));

    setError(null);
    setSubmitting(true);
    try {
      const submitResp = await submitAnswers(studentId, answersArray);
      if (!submitResp.submissionId) {
        throw new Error(submitResp.error || "Submission failed");
      }
      setSubmitting(false);
      setGrading(true);
      if (
        submitResp.success &&
        submitResp.graded &&
        Array.isArray(submitResp.grades)
      ) {
        setGradedSubmission({
          studentId,
          graded: true,
          totalScore: submitResp.totalScore,
          maxScore: submitResp.maxScore,
          grades: submitResp.grades,
        });
      } else {
        const graded = await fetchSubmission(submitResp.submissionId);
        if (!graded.success || !graded.submission) {
          throw new Error("Could not load graded submission");
        }
        setGradedSubmission(graded.submission);
      }
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.error ||
          err.message ||
          "Failed to submit and grade. Please try again."
      );
    } finally {
      setSubmitting(false);
      setGrading(false);
    }
  };

  const handleRetake = () => {
    const reset = {};
    questions.forEach((q) => (reset[q.id] = ""));
    setAnswers(reset);
    setGradedSubmission(null);
    setError(null);
  };

  if (loading) return <div className="loading">Loading questions...</div>;
  if (error && questions.length === 0) return <div className="error">{error}</div>;

  const questionById = Object.fromEntries(questions.map((q) => [q.id, q]));
  const analyzing = submitting || grading;

  return (
    <div className="exam-page">
      {analyzing && (
        <div className="exam-analyzing-overlay" role="status" aria-live="polite" aria-busy="true">
          <div className="exam-analyzing-card">
            <div className="exam-analyzing-spinner" aria-hidden />
            <p className="exam-analyzing-label">Analyzing Exam</p>
          </div>
        </div>
      )}

      <header className="exam-header">
        <h1>Auto-Graded Exam System</h1>
        <p>Answer all questions below and submit when ready</p>
      </header>

      {!gradedSubmission && (
        <>
          <div className="student-id-section">
            <label htmlFor="studentId">Student ID:</label>
            <input
              id="studentId"
              type="text"
              value={studentId}
              onChange={(e) => setStudentId(e.target.value)}
              placeholder="Enter your student ID"
              disabled={analyzing}
            />
          </div>

          <QuestionList
            questions={questions}
            answers={answers}
            onAnswerChange={handleAnswerChange}
            disabled={analyzing}
          />

          <SubmitButton
            onClick={handleSubmit}
            disabled={analyzing || !studentId.trim()}
            submitting={analyzing}
          />

          {error && <div className="error-message">{error}</div>}
        </>
      )}

      {gradedSubmission && (
        <div className="grades-section">
          <h2>Results</h2>
          <div className="grades-total">
            Total:{" "}
            {gradedSubmission.totalScore != null ? gradedSubmission.totalScore : "—"} /{" "}
            {gradedSubmission.maxScore != null ? gradedSubmission.maxScore : "—"}
            {gradedSubmission.studentId && <> &middot; Student: {gradedSubmission.studentId}</>}
          </div>
          {(gradedSubmission.grades || []).map((g) => (
            <GradeResult
              key={g.question_id}
              grade={g}
              questionText={questionById[g.question_id]?.text}
            />
          ))}
          <button className="submit-button" onClick={handleRetake} style={{ marginTop: 16 }}>
            Take Exam Again
          </button>
        </div>
      )}
    </div>
  );
}

export default ExamPage;
