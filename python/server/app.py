from pathlib import Path

from dotenv import load_dotenv

# Load python/server/.env before any module reads os.environ (works from any cwd).
load_dotenv(Path(__file__).resolve().parent / ".env")

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from db.database import init_db, get_db
from routes.questions import questions_bp
from routes.submissions import submissions_bp

app = Flask(__name__)
CORS(app)

# Initialize database on startup
with app.app_context():
    init_db()

# Register blueprints
app.register_blueprint(questions_bp)
app.register_blueprint(submissions_bp)

@app.route('/')
def home():
    return jsonify({"message": "Auto-Graded Exam API"})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, port=port)

