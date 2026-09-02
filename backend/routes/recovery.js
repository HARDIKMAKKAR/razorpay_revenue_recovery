const express = require("express");
const axios = require("axios");

const router = express.Router();

const ML_SERVICE_URL =
    process.env.ML_SERVICE_URL || "http://localhost:5001";


router.post("/recommend", async (req, res) => {
    try {
        const response = await axios.post(
            `${ML_SERVICE_URL}/recommend`,
            req.body
        );

        res.json(response.data);

    } catch (error) {

        console.error(
            "ML Service Error:",
            error.message
        );

        res.status(500).json({
            error: "Unable to get recovery recommendation"
        });
    }
});


module.exports = router;