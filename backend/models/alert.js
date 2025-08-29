// models/alert.js
import mongoose from "mongoose";

const alertSchema = new mongoose.Schema({
  call_id: { type: mongoose.Schema.Types.ObjectId, ref: "CallRecord" },
  message: String,
  timestamp: { type: Date, default: Date.now }
});

export default mongoose.model("Alert", alertSchema);
