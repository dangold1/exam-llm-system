from typing import Dict, List

_FEW_SHOT = """
Example (shape only; different topic):
Question: What is 2+2?
Rubric lines: 1. State the sum 2. Show brief reasoning
Student Answer: The sum is four because 2+2 equals 4.
Valid JSON:
{"question_id":99,"score":2,"max_score":2,"feedback":"States the sum and gives reasoning.","matched_criteria":["State the sum","Show brief reasoning"],"missed_criteria":[]}
""".strip()


def build_system_prompt(max_score: int) -> str:
    return f"""You are an exam grader. Use ONLY: the exam question, the numbered rubric criteria, and the student's answer.
Rules:
- No outside knowledge unless the rubric explicitly includes it.
- Do not assume facts not stated in the student answer. If evidence is missing or vague, lower the score and say what is missing in feedback.
- matched_criteria: short strings naming rubric points the answer clearly satisfies (verbatim or paraphrase tied to the answer).
- missed_criteria: short strings for rubric points not addressed or too weak to count.
- matched_criteria and missed_criteria must be disjoint (no item in both).
- Score is an integer from 0 through {max_score} inclusive. 0 = no evidence for rubric; {max_score} = all criteria clearly met.
- max_score in JSON must equal {max_score}.
- feedback: max 500 characters, concise, evidence-based, rubric-linked.
- Output VALID JSON only — no prose, no markdown, no code fences.

Required JSON keys: question_id, score, max_score, feedback, matched_criteria, missed_criteria.

{_FEW_SHOT}
"""


def build_schema_repair_user_message(max_score: int) -> str:
    return (
        "Your previous output failed parsing or validation. Reply with a single JSON object only.\n"
        f"Required keys: question_id (int), score (int from 0 to {max_score}), max_score (int, exactly {max_score}), "
        "feedback (string, max 500 chars, cite the student answer), "
        "matched_criteria (JSON array of short strings), missed_criteria (JSON array of short strings).\n"
        "Constraints: 0 <= score <= max_score; matched_criteria and missed_criteria must not overlap; "
        "no markdown or code fences."
    )


def build_messages(
    question_id: int,
    question_text: str,
    rubric: str,
    student_answer: str,
    max_score: int = 10,
) -> List[Dict[str, str]]:
    """Pure prompt construction. No I/O. `rubric` should be pre-formatted (e.g. via format_rubric_for_prompt)."""
    user = (
        f"question_id: {question_id}\n"
        f"max_score: {max_score}\n"
        f"Question:\n{question_text}\n\n"
        f"{rubric}\n\n"
        f"Student Answer:\n{student_answer or '(empty)'}\n\n"
        "Respond with one JSON object only."
    )
    return [
        {"role": "system", "content": build_system_prompt(max_score)},
        {"role": "user", "content": user},
    ]
