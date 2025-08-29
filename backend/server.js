import express from "express";
import mongoose from "mongoose";
import dotenv from "dotenv";
import callRoutes from "./routes/callRoutes.js";
import alertRoutes from "./routes/alertRoutes.js";
import { recomputeAllCalls } from "./controllers/callController.js";

dotenv.config();
const app = express();

app.use(express.json());

// ===== ROUTES =====
app.use("/api/calls", callRoutes);
app.use("/api/alerts", alertRoutes);

// ===== MONGODB =====
mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log("✅ MongoDB Connected"))
  .catch(err => console.error("❌ MongoDB Connection Error:", err));

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`🚀 Server running on port ${PORT}`));

// ===== SCHEDULER =====
// Run immediately on server start
recomputeAllCalls()
  .then(updated => console.log(`✅ Initial risk recomputation done (${updated} records)`))
  .catch(err => console.error("❌ Error in initial recompute:", err));

// Run every 5 minutes
setInterval(() => {
  console.log("⏱ Running scheduled risk computation...");
  recomputeAllCalls()
    .then(updated => console.log(`✅ Risk recomputation done (${updated} records)`))
    .catch(err => console.error("❌ Error in scheduled recompute:", err));
}, 5 * 60 * 1000);
