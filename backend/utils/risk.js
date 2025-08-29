// utils/risk.js

// === Helper Functions ===
const isVeryLong = (sec) => sec >= 3600;          // >= 1 hour
const isVeryShort = (sec) => sec > 0 && sec <= 5; // ≤ 5 sec
const lowQuality = (q) => q !== undefined && q <= 2;
const manyPrevCalls = (n) => n !== undefined && n >= 100;
const badStatus = (s) => ["failed", "dropped"].includes((s || "").toLowerCase());

// Private IP check
const isPrivateIP = (ip = "") => {
  return (
    ip.startsWith("10.") ||
    ip.startsWith("192.168.") ||
    ip.startsWith("172.16.") || ip.startsWith("172.17.") || ip.startsWith("172.18.") ||
    ip.startsWith("172.19.") || ip.startsWith("172.20.") || ip.startsWith("172.21.") ||
    ip.startsWith("172.22.") || ip.startsWith("172.23.") || ip.startsWith("172.24.") ||
    ip.startsWith("172.25.") || ip.startsWith("172.26.") || ip.startsWith("172.27.") ||
    ip.startsWith("172.28.") || ip.startsWith("172.29.") || ip.startsWith("172.30.") ||
    ip.startsWith("172.31.")
  );
};

// === Country Prefix Map ===
// Ye map tum expand kar sakti ho as needed
const countryPrefixMap = {
  "+91": "India",
  "+92": "Pakistan",
  "+86": "China",
  "+7": "Russia",
  "+234": "Nigeria",
  "+93": "Afghanistan"
};

// High-risk countries list
const highRiskCountries = ["Nigeria", "Pakistan", "Russia", "China", "Afghanistan"];

export function computeRisk(call) {
  let score = 0;
  const reasons = [];

  // 1) Blacklist
  if (call.is_blacklisted === true) {
    score += 60;
    reasons.push("Caller is blacklisted");
  }

  // 2) Duration anomalies
  if (isVeryLong(call.call_duration_seconds)) {
    score += 25;
    reasons.push("Very long call (>= 1h)");
  } else if (isVeryShort(call.call_duration_seconds)) {
    score += 15;
    reasons.push("Very short call (≤ 5s)");
  }

  // 3) Call status problems
  if (badStatus(call.call_status)) {
    score += 20;
    reasons.push(`Call status: ${call.call_status}`);
  }

  // 4) Low call quality
  if (lowQuality(call.call_quality)) {
    score += 15;
    reasons.push(`Low call quality (${call.call_quality})`);
  }

  // 5) Too many previous calls
  if (manyPrevCalls(call.number_of_previous_calls)) {
    score += 20;
    reasons.push(`High previous calls (${call.number_of_previous_calls})`);
  }

  // 6) Private IP anomaly
  if (isPrivateIP(call.source_ip) || isPrivateIP(call.destination_ip)) {
    score += 10;
    reasons.push("Private IP observed in CDR path");
  }

  // 7) Caller ID prefix vs Location mismatch
  if (call.caller_id) {
    for (const prefix in countryPrefixMap) {
      if (call.caller_id.startsWith(prefix)) {
        const expectedCountry = countryPrefixMap[prefix];
        if (
          call.caller_location &&
          !call.caller_location.toLowerCase().includes(expectedCountry.toLowerCase())
        ) {
          score += 25;
          reasons.push(
            `Caller ID prefix ${prefix} indicates ${expectedCountry}, but location is ${call.caller_location}`
          );
        }
      }
    }
  }

  // 8) Calls to high-risk regions
  if (highRiskCountries.some(c => (call.callee_location || "").includes(c))) {
    score += 30;
    reasons.push(`Call made to high-risk region: ${call.callee_location}`);
  }

  // 9) Odd call timing (midnight activity)
  if (call.call_start_time) {
    const hour = new Date(call.call_start_time).getHours();
    if (hour >= 0 && hour <= 4) {
      score += 15;
      reasons.push("Unusual call timing (midnight activity)");
    }
  }

  // Clamp score 0–100
  score = Math.max(0, Math.min(100, score));

  return {
    risk_score: score,
    suspicious: score >= 50, // threshold
    suspicion_reasons: reasons
  };
}
