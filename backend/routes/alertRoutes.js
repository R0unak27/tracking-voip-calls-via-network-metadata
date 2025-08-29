// routes/alertRoutes.js
import express from "express";
import Alert from "../models/alert.js";

const router = express.Router();

router.get("/", async (req, res) => {
  try {
    const alerts = await Alert.find().sort({ timestamp: -1 });
    res.json(alerts);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

export default router;
