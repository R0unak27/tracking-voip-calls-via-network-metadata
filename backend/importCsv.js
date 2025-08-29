// importCsv.js
import fs from "fs";
import csv from "csv-parser";
import mongoose from "mongoose";
import dotenv from "dotenv";
import Call from "./models/callRecord.js";

dotenv.config();

// MongoDB connect
mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log("✅ MongoDB Connected"))
  .catch(err => console.log("❌ Error: " + err));

const results = [];

fs.createReadStream("CDR_.csv")  // 👈 make sure this file is in backend folder
  .pipe(csv())
  .on("data", (row) => {
    // convert "True"/"False" strings → actual boolean
    if (row.is_blacklisted !== undefined) {
      row.is_blacklisted = row.is_blacklisted.toLowerCase() === "true";
    }

    results.push(row);
  })
  .on("end", async () => {
    try {
      await Call.insertMany(results);
      console.log("🎉 CSV Data Imported Successfully!");
    } catch (error) {
      console.error("❌ Error importing data:", error);
    } finally {
      mongoose.connection.close();
    }
  });
