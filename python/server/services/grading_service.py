import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Optional

from .azure_openai_grader import AzureOpenAIGrader
from .models import GradeResult, GradingError
from .rubric_format import format_rubric_for_prompt

log = logging.getLogger(__name__)

DEFAULT_MAX_SCORE = 10
MAX_SCORE_CAP = 100
_FEEDBACK_MAX = 500


def _max_score_for_question(q: dict) -> int:
    raw = q.get("maxScore")
    if raw is None:
        return DEFAULT_MAX_SCORE
    try:
        n = int(raw)
    except (TypeError, ValueError):
        return DEFAULT_MAX_SCORE
    return max(1, min(n, MAX_SCORE_CAP))


class GradingService:
    """Orchestrates per-question grading. Not aware of transport or DB."""

    def __init__(self, grader: Optional[AzureOpenAIGrader] = None):
        self._grader = grader  # lazy init so import is safe without env vars

    def _get_grader(self) -> AzureOpenAIGrader:
        if self._grader is None:
            self._grader = AzureOpenAIGrader()
        return self._grader

    def grade_submission(
        self,
        questions: List[Dict[str, Any]],
        answers: List[Dict[str, Any]],
    ) -> List[GradeResult]:
        by_id = {q["id"]: q for q in questions}
        try:
            grader = self._get_grader()
        except Exception as e:
            log.error("Grader unavailable: %s", e, exc_info=True)
            reason = (str(e) or "").strip() or type(e).__name__
            return [
                self._fallback(
                    a.get("questionId"),
                    reason,
                    _max_score_for_question(by_id[qid]) if (qid := a.get("questionId")) in by_id else DEFAULT_MAX_SCORE,
                )
                for a in answers
            ]

        def grade_answer(ans: Dict[str, Any]) -> GradeResult:
            qid = ans.get("questionId")
            q = by_id.get(qid)
            if not q:
                return self._fallback(qid, "Question not found", DEFAULT_MAX_SCORE)
            max_score = _max_score_for_question(q)
            try:
                return grader.grade_one(
                    question_id=qid,
                    question_text=q["text"],
                    rubric=format_rubric_for_prompt(q.get("rubric") or ""),
                    student_answer=ans.get("answer", ""),
                    max_score=max_score,
                )
            except GradingError as e:
                log.warning("Fallback grade for q=%s: %s", qid, e)
                return self._fallback(qid, str(e), max_score)
            except Exception as e:  # defensive: never let one bad call poison the batch
                log.exception("Unexpected grading error for q=%s", qid)
                return self._fallback(qid, f"unexpected: {type(e).__name__}", max_score)

        n = len(answers)
        if n == 0:
            return []
        try:
            default_workers = min(5, n)
            max_workers = int(os.getenv("GRADING_MAX_WORKERS", str(default_workers)))
        except ValueError:
            max_workers = default_workers
        max_workers = max(1, min(max_workers, n, 8))

        if max_workers == 1:
            return [grade_answer(a) for a in answers]

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            return list(executor.map(grade_answer, answers))

    @staticmethod
    def _fallback(
        question_id: Optional[int],
        reason: str,
        max_score: int = DEFAULT_MAX_SCORE,
    ) -> GradeResult:
        fb = f"Grading unavailable: {reason}"
        if len(fb) > _FEEDBACK_MAX:
            fb = fb[: _FEEDBACK_MAX - 3] + "..."
        return GradeResult(
            question_id=question_id if question_id is not None else 0,
            score=0,
            max_score=max_score,
            grading_status="failed",
            feedback=fb,
            matched_criteria=[],
            missed_criteria=[],
        )

    @staticmethod
    def model_metadata() -> Dict[str, str]:
        def _strip(s: str) -> str:
            return (s or "").strip().strip('"').strip("'")

        api_ver = (
            _strip(os.getenv("AZURE_OPENAI_API_VERSION"))
            or _strip(os.getenv("AZURE_OPENAI_VERSION"))
            or _strip(os.getenv("OPENAI_API_VERSION"))
            or "2024-12-01-preview"
        )
        return {
            "provider": "azure-openai",
            "deployment": _strip(os.getenv("AZURE_OPENAI_DEPLOYMENT")) or "gpt-5-nano",
            "api_version": api_ver,
        }
