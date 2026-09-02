const express = require("express");
const cors = require("cors");
require("dotenv").config();

const recoveryRoutes = require("./routes/recovery");

const app = express();

app.use(cors());
app.use(express.json());

app.use("/api/recovery", recoveryRoutes);

app.get("/health", (req, res) => {
    res.json({
        status: "ok",
        service: "revenue-recovery-backend"
    });
});

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
    console.log(`Backend running on http://localhost:${PORT}`);
});