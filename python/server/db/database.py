from pathlib import Path

from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

client = None
db = None

def get_db():
    """Get database instance"""
    global client, db
    if db is None:
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        db_name = os.getenv('DB_NAME', 'exam_system')
        client = MongoClient(mongodb_uri)
        db = client[db_name]
    return db

def init_db():
    """Initialize database with sample questions if empty"""
    db = get_db()
    questions_collection = db.questions
    
    # Check if questions already exist
    if questions_collection.count_documents({}) == 0:
        sample_questions = [
            {
                "id": 1,
                "maxScore": 10,
                "text": "Explain the concept of polymorphism in object-oriented programming with an example.",
                "rubric": "Should mention: method overriding/overloading, inheritance, different forms, code example"
            },
            {
                "id": 2,
                "maxScore": 10,
                "text": "What are the main differences between SQL and NoSQL databases? When would you use each?",
                "rubric": "Should mention: structure (schema vs schemaless), scalability, use cases, examples"
            },
            {
                "id": 3,
                "maxScore": 10,
                "text": "Describe how the HTTP protocol works and explain the difference between GET and POST requests.",
                "rubric": "Should mention: request-response cycle, stateless nature, GET for retrieval, POST for submission"
            },
            {
                "id": 4,
                "maxScore": 10,
                "text": "What is the purpose of version control systems like Git? Explain branches and merging.",
                "rubric": "Should mention: tracking changes, collaboration, branches for features, merging code"
            },
            {
                "id": 5,
                "maxScore": 10,
                "text": "Explain the concept of Big O notation and why it's important in algorithm analysis.",
                "rubric": "Should mention: time/space complexity, scalability, comparing algorithms, common notations"
            }
        ]
        
        questions_collection.insert_many(sample_questions)
        print(f"Inserted {len(sample_questions)} sample questions into database")
    else:
        print(f"Database already contains {questions_collection.count_documents({})} questions")

