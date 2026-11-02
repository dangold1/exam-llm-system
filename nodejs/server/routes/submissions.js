import express from 'express';
import { getDb } from '../db/database.js';

const router = express.Router();

router.post('/submit', async (req, res) => {
    /** Submit student answers */
    try {
        const data = req.body;

        // Validate required fields
        if (!data || !data.studentId || !data.answers) {
            return res.status(400).json({
                success: false,
                error: 'Missing required fields: studentId and answers'
            });
        }

        const studentId = data.studentId;
        const answers = data.answers;

        // Validate answers format
        if (!Array.isArray(answers)) {
            return res.status(400).json({
                success: false,
                error: 'Answers must be an array'
            });
        }

        const db = await getDb();
        const submissionsCollection = db.collection('submissions');

        // Create submission document
        const submission = {
            studentId: studentId,
            answers: answers,
            submittedAt: new Date(),
            graded: false
        };

        // Insert into database
        const result = await submissionsCollection.insertOne(submission);

        res.status(201).json({
            success: true,
            message: 'Answers submitted successfully',
            submissionId: result.insertedId.toString()
        });

    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

export default router;

