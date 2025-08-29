// models/callRecord.js
import mongoose from "mongoose";

const callRecordSchema = new mongoose.Schema({
  caller_id: String,
  callee_id: String,
  source_ip: String,
  destination_ip: String,
  call_start_time: Date,
  call_duration_seconds: Number,
  call_type: String,      // inbound | outbound
  call_status: String,    // completed | dropped | failed
  protocol: String,       // SIP | IAX2 | H.323
  call_quality: Number,   // 1..5
  is_blacklisted: Boolean,
  number_of_previous_calls: Number,
  caller_location: String,
  callee_location: String,

  suspicious: { type: Boolean, default: false },
  risk_score: { type: Number, default: 0 },          // 0..100
  suspicion_reasons: { type: [String], default: [] } // why flagged
});

export default mongoose.model("CallRecord", callRecordSchema);
