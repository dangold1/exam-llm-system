import logging
from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from flask import Blueprint, jsonify, request

from db.database import get_db
from services.grading_service import GradingService

log = logging.getLogger(__name__)

submissions_bp = Blueprint('submissions', __name__)
_grading_service = GradingService()


@submissions_bp.route('/submit', methods=['POST'])
def submit_answers():
    """Accept student answers, grade synchronously, persist, and return submissionId."""
    data = request.get_json(silent=True)
    if not data or 'studentId' not in data or 'answers' not in data:
        return jsonify({"success": False, "error": "Missing required fields: studentId and answers"}), 400

    student_id = data['studentId']
    answers = data['answers']
    if not isinstance(answers, list):
        return jsonify({"success": False, "error": "Answers must be an array"}), 400

    db = get_db()
    submission = {
        "studentId": student_id,
        "answers": answers,
        "submittedAt": datetime.utcnow(),
        "graded": False,
    }
    result = db.submissions.insert_one(submission)
    submission_id = str(result.inserted_id)

    try:
        questions = list(db.questions.find({}, {'_id': 0}))
        grades = _grading_service.grade_submission(questions, answers)
    except Exception as e:
        log.exception("Grading service crashed for submission %s", submission_id)
        return jsonify({
            "success": False,
            "status": "grading_error",
            "submissionId": submission_id,
            "graded": False,
            "totalScore": None,
            "maxScore": None,
            "grades": None,
            "error": f"Grading unavailable: {type(e).__name__}",
        }), 502

    grades_payload = [g.model_dump() for g in grades]
    total = sum(g["score"] for g in grades_payload)
    max_total = sum(g["max_score"] for g in grades_payload)

    db.submissions.update_one(
        {"_id": result.inserted_id},
        {"$set": {
            "graded": True,
            "gradedAt": datetime.utcnow(),
            "grades": grades_payload,
            "totalScore": total,
            "maxScore": max_total,
            "model": GradingService.model_metadata(),
        }},
    )

    return jsonify({
        "success": True,
        "status": "graded",
        "submissionId": submission_id,
        "graded": True,
        "totalScore": total,
        "maxScore": max_total,
        "grades": grades_payload,
    }), 201


@submissions_bp.route('/submission/<submission_id>', methods=['GET'])
def get_submission(submission_id):
    """Retrieve a graded submission by id."""
    try:
        oid = ObjectId(submission_id)
    except (InvalidId, TypeError):
        return jsonify({"success": False, "error": "Invalid submission id"}), 400

    doc = get_db().submissions.find_one({"_id": oid})
    if not doc:
        return jsonify({"success": False, "error": "Not found"}), 404

    doc["_id"] = str(doc["_id"])
    if isinstance(doc.get("submittedAt"), datetime):
        doc["submittedAt"] = doc["submittedAt"].isoformat()
    if isinstance(doc.get("gradedAt"), datetime):
        doc["gradedAt"] = doc["gradedAt"].isoformat()

    return jsonify({"success": True, "submission": doc}), 200
