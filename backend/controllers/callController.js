import Alert from "../models/alert.js";
import Call from "../models/callRecord.js";
import { computeRisk } from "../utils/risk.js";

// =================== API FUNCTIONS ===================

// GET /api/calls
export const getAllCalls = async (req, res) => {
  try {
    const {
      caller_id, callee_id, status, protocol,
      from, to,
      minDuration, maxDuration,
      page = 1, limit = 20,
      sort = "-call_start_time"
    } = req.query;

    const q = {};
    if (caller_id) q.caller_id = caller_id;
    if (callee_id) q.callee_id = callee_id;
    if (status)    q.call_status = status;
    if (protocol)  q.protocol = protocol;

    if (from || to) {
      q.call_start_time = {};
      if (from) q.call_start_time.$gte = new Date(from);
      if (to)   q.call_start_time.$lte = new Date(to);
    }

    if (minDuration || maxDuration) {
      q.call_duration_seconds = {};
      if (minDuration) q.call_duration_seconds.$gte = Number(minDuration);
      if (maxDuration) q.call_duration_seconds.$lte = Number(maxDuration);
    }

    const skip = (Number(page) - 1) * Number(limit);

    const [items, total] = await Promise.all([
      Call.find(q).sort(sort).skip(skip).limit(Number(limit)),
      Call.countDocuments(q)
    ]);

    res.json({ page: Number(page), limit: Number(limit), total, items });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// GET /api/calls/suspicious
export const getSuspiciousCalls = async (req, res) => {
  try {
    const minScore = Number(req.query.minScore || 50);
    const calls = await Call.find({ risk_score: { $gte: minScore } })
      .sort("-risk_score -call_start_time");
    res.json(calls);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// POST /api/calls/recompute -> API version
export const recomputeSuspicionAll = async (_req, res) => {
  try {
    const updated = await recomputeAllCalls();
    res.json({ message: "Risk recomputed", updated });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// GET /api/calls/stats
export const getStats = async (_req, res) => {
  try {
    const [totals, perDay, topCallers, topPairs, protocols] = await Promise.all([
      Call.aggregate([
        { $group: { _id: null, totalCalls: { $sum: 1 }, suspiciousCalls: { $sum: { $cond: [{ $eq: ["$suspicious", true] }, 1, 0] } }, avgDuration: { $avg: "$call_duration_seconds" } } }
      ]),
      Call.aggregate([
        { $group: { _id: { $dateToString: { date: "$call_start_time", format: "%Y-%m-%d" } }, count: { $sum: 1 } } },
        { $sort: { _id: 1 } }
      ]),
      Call.aggregate([
        { $group: { _id: "$caller_id", calls: { $sum: 1 } } },
        { $sort: { calls: -1 } },
        { $limit: 10 }
      ]),
      Call.aggregate([
        { $group: { _id: { caller: "$caller_id", callee: "$callee_id" }, calls: { $sum: 1 } } },
        { $sort: { calls: -1 } },
        { $limit: 10 }
      ]),
      Call.aggregate([
        { $group: { _id: "$protocol", calls: { $sum: 1 } } },
        { $sort: { calls: -1 } }
      ])
    ]);

    res.json({
      totals: totals[0] || { totalCalls: 0, suspiciousCalls: 0, avgDuration: 0 },
      perDay,
      topCallers,
      topPairs,
      protocols
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// =================== INTERNAL FUNCTION FOR SCHEDULER ===================
export const recomputeAllCalls = async () => {
  const cursor = Call.find().cursor();
  let updated = 0;

  for (let doc = await cursor.next(); doc != null; doc = await cursor.next()) {
    const { risk_score, suspicious, suspicion_reasons } = computeRisk(doc);

    doc.risk_score = risk_score;
    doc.suspicious = suspicious;
    doc.suspicion_reasons = suspicion_reasons;
    await doc.save();

    if (suspicious) {
      await Alert.create({
        call_id: doc._id,
        message: `Suspicious call from ${doc.caller_id} to ${doc.callee_id}: ${suspicion_reasons.join(", ")}`
      });
    }

    updated++;
  }

  return updated;
};
