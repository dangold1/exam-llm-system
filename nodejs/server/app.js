import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { initDb, getDb } from './db/database.js';
import questionsRouter from './routes/questions.js';
import submissionsRouter from './routes/submissions.js';

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.use('/', questionsRouter);
app.use('/', submissionsRouter);

// Root route
app.get('/', (req, res) => {
  res.json({ message: 'Auto-Graded Exam API' });
});

// Initialize database and start server
async function startServer() {
  try {
    await initDb();
    app.listen(PORT, () => {
      console.log(`Server running on http://localhost:${PORT}`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
}

startServer();

