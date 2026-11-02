import { MongoClient } from 'mongodb';
import dotenv from 'dotenv';

dotenv.config();

let client = null;
let db = null;

export async function getDb() {
  /** Get database instance */
  if (db === null) {
    const mongodbUri = process.env.MONGODB_URI || 'mongodb://localhost:27017/';
    const dbName = process.env.DB_NAME || 'exam_system';
    client = new MongoClient(mongodbUri);
    await client.connect();
    db = client.db(dbName);
    console.log('Connected to MongoDB');
  }
  return db;
}

export async function initDb() {
  /** Initialize database with sample questions if empty */
  const db = await getDb();
  const questionsCollection = db.collection('questions');
  
  // Check if questions already exist
  const count = await questionsCollection.countDocuments({});
  
  if (count === 0) {
    const sampleQuestions = [
      {
        id: 1,
        text: "Explain the concept of polymorphism in object-oriented programming with an example.",
        rubric: "Should mention: method overriding/overloading, inheritance, different forms, code example"
      },
      {
        id: 2,
        text: "What are the main differences between SQL and NoSQL databases? When would you use each?",
        rubric: "Should mention: structure (schema vs schemaless), scalability, use cases, examples"
      },
      {
        id: 3,
        text: "Describe how the HTTP protocol works and explain the difference between GET and POST requests.",
        rubric: "Should mention: request-response cycle, stateless nature, GET for retrieval, POST for submission"
      },
      {
        id: 4,
        text: "What is the purpose of version control systems like Git? Explain branches and merging.",
        rubric: "Should mention: tracking changes, collaboration, branches for features, merging code"
      },
      {
        id: 5,
        text: "Explain the concept of Big O notation and why it's important in algorithm analysis.",
        rubric: "Should mention: time/space complexity, scalability, comparing algorithms, common notations"
      }
    ];
    
    await questionsCollection.insertMany(sampleQuestions);
    console.log(`Inserted ${sampleQuestions.length} sample questions into database`);
  } else {
    console.log(`Database already contains ${count} questions`);
  }
}

