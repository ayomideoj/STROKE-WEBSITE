const express = require('express');
const axios = require('axios');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

// Route to handle data submission to Flask API
app.post('/submit-to-flask', async (req, res) => {
    try {
        // Data to send to Flask API
        const data = {
            gender: req.body.gender,
            age: req.body.age,
            hypertension: req.body.hypertension,
            heart_disease: req.body.heart_disease,
            ever_married: req.body.ever_married,
            work_type: req.body.work_type,
            Residence_type: req.body.Recidence_type,
            avg_glucose_level: req.body.avg_glucose_level,
            bmi: req.body.bmi,
            smoking_status: req.body.smoking_status
        };

        // Send POST request to Flask API
        const response = await axios.post('http://127.0.0.1:5000/submit', data);

        // Return Flask response to the client
        res.json({
            success: true,
            stroke_message: response.data.stroke_message,
            db_message: response.data.db_message
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Start JavaScript server
app.listen(3000, () => {
    console.log('JavaScript server running on http://localhost:3000');
});
