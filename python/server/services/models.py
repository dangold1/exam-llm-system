from typing import Annotated, Any, List, Literal

from pydantic import BaseModel, Field, StringConstraints, field_validator, model_validator


class QuestionInput(BaseModel):
    id: int
    text: str
    rubric: str


class StudentAnswer(BaseModel):
    questionId: int
    answer: str


CriterionStr = Annotated[str, StringConstraints(max_length=160, strip_whitespace=True)]


class GradeResult(BaseModel):
    question_id: int
    score: int = Field(ge=0)
    max_score: int = Field(ge=1, le=100)
    grading_status: Literal["ok", "failed"] = "ok"
    feedback: str = Field(min_length=1, max_length=500)
    matched_criteria: List[CriterionStr] = Field(default_factory=list, max_length=20)
    missed_criteria: List[CriterionStr] = Field(default_factory=list, max_length=20)

    @field_validator("matched_criteria", "missed_criteria", mode="before")
    @classmethod
    def drop_empty_strings(cls, v: Any) -> Any:
        if v is None:
            return []
        if isinstance(v, list):
            return [x for x in v if x is not None and str(x).strip() != ""]
        return v

    @model_validator(mode="after")
    def score_and_criteria_consistency(self):
        if self.score > self.max_score:
            raise ValueError(f"score ({self.score}) must not exceed max_score ({self.max_score})")

        def norm(s: str) -> str:
            return " ".join(s.lower().split())

        matched_n = {norm(x) for x in self.matched_criteria}
        missed_n = {norm(x) for x in self.missed_criteria}
        overlap = matched_n & missed_n
        if overlap:
            raise ValueError("matched_criteria and missed_criteria must not list the same criterion")
        return self


class GradingError(Exception):
    """Raised when grading a single question cannot complete after retries."""
