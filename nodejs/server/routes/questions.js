import express from 'express';
import { getDb } from '../db/database.js';

const router = express.Router();

router.get('/questions', async (req, res) => {
    /** Fetch all exam questions */
    try {
        const db = await getDb();
        const questionsCollection = db.collection('questions');

        // Fetch all questions, excluding MongoDB's _id field
        const questions = await questionsCollection.find({}).project({ _id: 0 }).toArray();

        res.status(200).json({
            success: true,
            questions: questions
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

export default router;

