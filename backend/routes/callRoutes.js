import express from "express";
import {
  getAllCalls,
  getSuspiciousCalls,
  getStats,
  recomputeSuspicionAll
} from "../controllers/callController.js";

const router = express.Router();

router.get("/", getAllCalls);                 // list/search/paginate
router.get("/suspicious", getSuspiciousCalls);// suspicious by score
router.get("/stats", getStats);               // analytics
router.post("/recompute", recomputeSuspicionAll); // recompute risk for all

export default router;
