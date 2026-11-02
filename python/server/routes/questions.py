from flask import Blueprint, jsonify
from db.database import get_db

questions_bp = Blueprint('questions', __name__)

@questions_bp.route('/questions', methods=['GET'])
def get_questions():
    """Fetch all exam questions"""
    try:
        db = get_db()
        questions_collection = db.questions
        
        # Fetch all questions, excluding MongoDB's _id field
        questions = list(questions_collection.find({}, {'_id': 0}))
        
        return jsonify({
            "success": True,
            "questions": questions
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

