"""
AI Health Score Engine — Phase 3.
Computes a 0–100 risk-adjusted health score for a patient
based on their conditions, appointment urgency history, and wellness feedback.

Score interpretation:
  85–100 : Excellent
  70–84  : Good
  55–69  : Fair
  40–54  : At Risk
  0–39   : Needs Attention
"""
from typing import List, Optional
from datetime import datetime, timedelta

# ── Risk weights per condition ────────────────────────────────────────────────
CONDITION_RISK = {
    "heart_disease": 25,
    "diabetes": 18,
    "hypertension": 16,
    "obesity": 14,
    "arthritis": 12,
    "pcos": 10,
    "thyroid": 10,
    "back_pain": 8,
    "anxiety": 8,
    "general": 0,
}

# ── Lifestyle / wellness positive factors ─────────────────────────────────────
WELLNESS_BONUS = {
    "diet":      5,
    "yoga":      6,
    "meditation": 5,
}


def compute_health_score(
    conditions: List[str],
    urgency_history: List[int],         # list of urgency scores (1-5) from past appointments
    wellness_ratings: List[dict],       # list of {"module": str, "rating": int} from feedback logs
    age: Optional[int] = None,
) -> dict:
    """
    Compute an AI health score for the patient.
    Returns score (0–100), risk level, breakdown, and recommendations.
    """
    base_score = 100.0

    # ── 1. Condition deductions ───────────────────────────────────────────────
    condition_penalty = 0
    condition_details = {}
    for c in conditions:
        key = c.lower().replace(" ", "_")
        penalty = CONDITION_RISK.get(key, 5)  # unknown condition = small penalty
        condition_penalty += penalty
        condition_details[c] = penalty

    # Cap condition penalty at 40 (to leave room for other factors)
    condition_penalty = min(condition_penalty, 40)
    base_score -= condition_penalty

    # ── 2. Appointment urgency history ────────────────────────────────────────
    urgency_penalty = 0
    if urgency_history:
        avg_urgency = sum(urgency_history) / len(urgency_history)
        recent_high = sum(1 for u in urgency_history[-5:] if u >= 4)  # last 5 appointments
        urgency_penalty = min((avg_urgency - 1) * 3 + recent_high * 2, 20)
    base_score -= urgency_penalty

    # ── 3. Age factor ─────────────────────────────────────────────────────────
    age_penalty = 0
    if age:
        if age > 70:
            age_penalty = 8
        elif age > 60:
            age_penalty = 5
        elif age > 50:
            age_penalty = 3
        elif age > 40:
            age_penalty = 1
    base_score -= age_penalty

    # ── 4. Wellness engagement bonus ──────────────────────────────────────────
    wellness_bonus = 0
    module_ratings = {}
    for log in wellness_ratings:
        mod = log.get("module", "")
        rating = log.get("rating", 3)
        # Weight = bonus factor * (rating / 5)
        bonus = WELLNESS_BONUS.get(mod, 2) * (rating / 5)
        wellness_bonus += bonus
        module_ratings[mod] = module_ratings.get(mod, []) + [rating]

    wellness_bonus = min(wellness_bonus, 15)  # cap bonus at 15
    base_score += wellness_bonus

    final_score = max(0.0, min(100.0, base_score))

    # ── 5. Risk level ─────────────────────────────────────────────────────────
    if final_score >= 85:
        risk_level = "Excellent"
        risk_color = "#00c9a7"
    elif final_score >= 70:
        risk_level = "Good"
        risk_color = "#22c55e"
    elif final_score >= 55:
        risk_level = "Fair"
        risk_color = "#f59e0b"
    elif final_score >= 40:
        risk_level = "At Risk"
        risk_color = "#f97316"
    else:
        risk_level = "Needs Attention"
        risk_color = "#f43f5e"

    # ── 6. Personalised recommendations ──────────────────────────────────────
    recommendations = []
    if "diabetes" in [c.lower() for c in conditions]:
        recommendations.append("Monitor blood sugar daily. Follow low-GI diet plan.")
    if "hypertension" in [c.lower() for c in conditions]:
        recommendations.append("Measure BP morning and evening. Reduce sodium intake.")
    if "heart_disease" in [c.lower() for c in conditions]:
        recommendations.append("Avoid exertion. Take prescribed medication regularly.")
    if any(u >= 4 for u in urgency_history[-3:]):
        recommendations.append("You had recent high-urgency visits. Regular check-ups recommended.")
    if not any(log.get("module") == "meditation" for log in wellness_ratings):
        recommendations.append("Start a daily 10-minute meditation practice to reduce stress.")
    if not any(log.get("module") == "yoga" for log in wellness_ratings):
        recommendations.append("Add gentle yoga to your routine for joint and mental health.")
    if not recommendations:
        recommendations.append("Great health profile! Maintain your wellness routine.")

    return {
        "score": round(final_score, 1),
        "risk_level": risk_level,
        "risk_color": risk_color,
        "breakdown": {
            "base": 100,
            "condition_penalty": -round(condition_penalty, 1),
            "urgency_penalty": -round(urgency_penalty, 1),
            "age_penalty": -round(age_penalty, 1),
            "wellness_bonus": round(wellness_bonus, 1),
        },
        "conditions_assessed": condition_details,
        "recommendations": recommendations[:4],  # top 4
        "computed_at": datetime.utcnow().isoformat(),
    }


def personalize_wellness(
    condition: str,
    feedback_logs: List[dict],
    module: str = "diet"
) -> dict:
    """
    Use stored feedback history to personalize wellness recommendations.
    Returns adaptation hints for the wellness service.
    """
    if not feedback_logs:
        return {"adapted": False, "hints": []}

    # Filter logs for this module
    module_logs = [l for l in feedback_logs if l.get("module") == module]
    if not module_logs:
        return {"adapted": False, "hints": []}

    avg_rating = sum(l.get("rating", 3) for l in module_logs) / len(module_logs)
    low_ratings = [l for l in module_logs if l.get("rating", 5) <= 2]
    comments = [l.get("comment", "").lower() for l in module_logs if l.get("comment")]

    hints = []
    if avg_rating < 3:
        hints.append("Consider simplifying the plan — user finds it complex.")
    if any("too long" in c for c in comments):
        hints.append("Shorten session duration — user prefers briefer plans.")
    if any("boring" in c or "repetitive" in c for c in comments):
        hints.append("Add variety — user finds current plan repetitive.")
    if any("not working" in c for c in comments):
        hints.append("Increase intensity or try an alternative technique.")
    if avg_rating >= 4:
        hints.append("User is satisfied — maintain current approach.")

    return {
        "adapted": True,
        "avg_rating": round(avg_rating, 2),
        "total_feedbacks": len(module_logs),
        "hints": hints,
        "suggestion": "increase_intensity" if avg_rating >= 4 else "simplify",
    }
