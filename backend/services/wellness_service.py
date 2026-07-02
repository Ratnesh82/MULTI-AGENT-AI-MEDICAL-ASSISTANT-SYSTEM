"""
Wellness Engine — Diet, Yoga, and Meditation submodules.
Phase 2: Extended with thyroid, obesity, PCOS, arthritis, heart_disease.
Upgrade path: ML personalization via user feedback history.
"""
from typing import List
from datetime import datetime

# ── DIET KNOWLEDGE BASE ─────────────────────────────────────────────────────
DIET_PLANS = {
    "diabetes": {
        "avoid": ["white rice", "maida (refined flour)", "sweets", "fried food", "sugary drinks", "potato chips"],
        "guidelines": "Low GI foods, high fibre, small frequent meals. Avoid sugar spikes.",
        "plan": {
            "Monday":    {"breakfast": "Oats upma with vegetables", "lunch": "Brown rice + moong dal + sabzi", "dinner": "Multigrain roti + palak paneer", "snacks": "Roasted chana, buttermilk"},
            "Tuesday":   {"breakfast": "Besan chilla with mint chutney", "lunch": "Bajra roti + mixed vegetable curry", "dinner": "Khichdi (moong + brown rice)", "snacks": "Cucumber sticks, green tea"},
            "Wednesday": {"breakfast": "Dalia (broken wheat) porridge", "lunch": "Whole wheat roti + rajma", "dinner": "Soup + grilled paneer salad", "snacks": "Nuts (almonds 5-6), apple"},
            "Thursday":  {"breakfast": "Boiled eggs / sprouts salad", "lunch": "Jowar roti + dal + sabzi", "dinner": "Vegetable khichdi", "snacks": "Roasted makhana, lassi (no sugar)"},
            "Friday":    {"breakfast": "Oats with nuts and seeds", "lunch": "Brown rice + arhar dal + raita", "dinner": "Roti + soya chunks curry", "snacks": "Papaya, warm water with lemon"},
            "Saturday":  {"breakfast": "Idli (rava) with sambar", "lunch": "Mixed grain rice + sambhar", "dinner": "Moong dal cheela + curd", "snacks": "Pear, herbal tea"},
            "Sunday":    {"breakfast": "Uttapam with vegetable toppings", "lunch": "Brown rice + lauki dal", "dinner": "Roti + chana masala", "snacks": "Roasted pumpkin seeds, coconut water (small)"},
        }
    },
    "hypertension": {
        "avoid": ["salt/sodium excess", "pickles", "papad", "processed food", "red meat", "alcohol"],
        "guidelines": "DASH diet principles. Low sodium, high potassium, high magnesium.",
        "plan": {
            "Monday":    {"breakfast": "Banana smoothie (no sugar)", "lunch": "Brown rice + spinach dal", "dinner": "Roti + bhindi sabzi + curd", "snacks": "Walnuts, orange"},
            "Tuesday":   {"breakfast": "Poha with peas (less salt)", "lunch": "Multigrain roti + palak paneer", "dinner": "Vegetable soup + 2 rotis", "snacks": "Pomegranate, green tea"},
            "Wednesday": {"breakfast": "Oats with banana", "lunch": "Rice + fish curry / paneer", "dinner": "Khichdi with ghee", "snacks": "Flaxseeds, coconut water"},
            "Thursday":  {"breakfast": "Idli + sambar (low salt)", "lunch": "Jowar roti + dal + salad", "dinner": "Roti + methi sabzi", "snacks": "Almonds, amla juice"},
            "Friday":    {"breakfast": "Dalia with milk", "lunch": "Brown rice + moong dal", "dinner": "Grilled vegetables + roti", "snacks": "Pear, herbal tea"},
            "Saturday":  {"breakfast": "Sprouts chaat (no salt)", "lunch": "Rice + lauki curry + raita", "dinner": "Roti + soya sabzi", "snacks": "Sunflower seeds, watermelon"},
            "Sunday":    {"breakfast": "Wheat dosa + coconut chutney", "lunch": "Brown rice + arhar dal + beet salad", "dinner": "Vegetable khichdi", "snacks": "Guava, buttermilk"},
        }
    },
    "thyroid": {
        "avoid": ["soy products (raw)", "cabbage (excess)", "broccoli (excess)", "cauliflower (excess)", "refined sugar", "processed food"],
        "guidelines": "Iodine-rich, selenium-rich foods. Avoid goitrogenic foods in excess. Eat at regular intervals.",
        "plan": {
            "Monday":    {"breakfast": "Egg whites + whole wheat toast", "lunch": "Brown rice + fish curry / dal", "dinner": "Roti + sabzi + curd", "snacks": "Pumpkin seeds, banana"},
            "Tuesday":   {"breakfast": "Oats with milk + nuts", "lunch": "Jowar roti + legume curry", "dinner": "Chicken soup / dal soup + roti", "snacks": "Brazil nuts (2-3), orange"},
            "Wednesday": {"breakfast": "Poha with peas", "lunch": "Multigrain roti + palak + dal", "dinner": "Brown rice + sabzi", "snacks": "Sunflower seeds, apple"},
            "Thursday":  {"breakfast": "Sprouts salad + milk", "lunch": "Rice + rajma", "dinner": "Roti + methi sabzi", "snacks": "Walnuts, pear"},
            "Friday":    {"breakfast": "Idli + sambar", "lunch": "Brown rice + fish / paneer", "dinner": "Khichdi + raita", "snacks": "Almonds, coconut water"},
            "Saturday":  {"breakfast": "Dalia + milk", "lunch": "Roti + chickpea curry", "dinner": "Grilled paneer + salad", "snacks": "Flaxseeds, guava"},
            "Sunday":    {"breakfast": "Besan cheela + green chutney", "lunch": "Rice + arhar dal + beet salad", "dinner": "Roti + vegetable curry", "snacks": "Pumpkin seeds, pomegranate"},
        }
    },
    "obesity": {
        "avoid": ["fried food", "soft drinks", "white bread", "maida", "butter", "processed snacks", "alcohol", "late-night eating"],
        "guidelines": "High protein, high fibre, low calorie. Eat 5-6 small meals. No skipping breakfast.",
        "plan": {
            "Monday":    {"breakfast": "Moong dal chilla (no oil)", "lunch": "Brown rice + dal + cucumber salad", "dinner": "Roti + sabzi (no ghee)", "snacks": "Cucumber, lemon water"},
            "Tuesday":   {"breakfast": "Oats + skimmed milk", "lunch": "Jowar roti + palak dal", "dinner": "Grilled paneer + salad", "snacks": "Apple, buttermilk"},
            "Wednesday": {"breakfast": "Sprouts chaat", "lunch": "Multigrain roti + rajma", "dinner": "Vegetable soup + 1 roti", "snacks": "Carrot sticks, green tea"},
            "Thursday":  {"breakfast": "Poha (light, less oil)", "lunch": "Brown rice + chicken / soya curry", "dinner": "Vegetable khichdi", "snacks": "Papaya, herbal tea"},
            "Friday":    {"breakfast": "Boiled egg + wheat toast", "lunch": "Roti + dal + salad", "dinner": "Fish curry / paneer + 1 roti", "snacks": "Pear, coconut water"},
            "Saturday":  {"breakfast": "Dalia with skimmed milk", "lunch": "Brown rice + chana masala", "dinner": "Clear vegetable soup + salad", "snacks": "Guava, lemon water"},
            "Sunday":    {"breakfast": "Idli (2) + sambar", "lunch": "Roti + sabzi + curd (low fat)", "dinner": "Khichdi + cucumber raita", "snacks": "Oranges, mint water"},
        }
    },
    "pcos": {
        "avoid": ["refined carbs", "sugary foods", "processed food", "dairy (excess)", "soy in excess", "alcohol"],
        "guidelines": "Low GI, anti-inflammatory. High fibre, omega-3 rich foods. Avoid insulin spikes.",
        "plan": {
            "Monday":    {"breakfast": "Flaxseed smoothie + oats", "lunch": "Brown rice + dal + sabzi", "dinner": "Roti + palak paneer", "snacks": "Walnuts, apple"},
            "Tuesday":   {"breakfast": "Eggs + whole wheat toast", "lunch": "Jowar roti + chickpea curry", "dinner": "Grilled fish / tofu + salad", "snacks": "Pumpkin seeds, green tea"},
            "Wednesday": {"breakfast": "Sprouts + moong dal chilla", "lunch": "Multigrain roti + rajma", "dinner": "Brown rice + sabzi", "snacks": "Berries, buttermilk"},
            "Thursday":  {"breakfast": "Dalia + nuts + seeds", "lunch": "Roti + dal + cucumber", "dinner": "Chicken / paneer soup + 1 roti", "snacks": "Almonds, pear"},
            "Friday":    {"breakfast": "Oats + skimmed milk", "lunch": "Brown rice + salmon / fish", "dinner": "Vegetable khichdi", "snacks": "Sunflower seeds, orange"},
            "Saturday":  {"breakfast": "Poha + peas + nuts", "lunch": "Roti + soya curry", "dinner": "Grilled paneer + salad", "snacks": "Flaxseeds, coconut water"},
            "Sunday":    {"breakfast": "Idli + sambar (low GI)", "lunch": "Brown rice + arhar dal", "dinner": "Roti + methi sabzi", "snacks": "Guava, herbal tea"},
        }
    },
    "arthritis": {
        "avoid": ["fried food", "red meat", "sugar", "refined flour", "processed food", "excess salt", "alcohol"],
        "guidelines": "Anti-inflammatory diet. Rich in omega-3, turmeric, ginger, vitamin C and D.",
        "plan": {
            "Monday":    {"breakfast": "Turmeric milk + oats", "lunch": "Brown rice + fish curry", "dinner": "Roti + palak sabzi", "snacks": "Walnuts, orange"},
            "Tuesday":   {"breakfast": "Ginger tea + besan cheela", "lunch": "Jowar roti + rajma", "dinner": "Grilled paneer + salad", "snacks": "Almonds, apple"},
            "Wednesday": {"breakfast": "Eggs + whole wheat toast", "lunch": "Multigrain roti + dal", "dinner": "Fish / tofu + brown rice", "snacks": "Pumpkin seeds, green tea"},
            "Thursday":  {"breakfast": "Dalia + milk + flaxseeds", "lunch": "Roti + chickpea curry", "dinner": "Vegetable khichdi", "snacks": "Sunflower seeds, pear"},
            "Friday":    {"breakfast": "Sprouts salad + milk", "lunch": "Brown rice + sabzi + curd", "dinner": "Roti + methi sabzi", "snacks": "Berries, turmeric latte"},
            "Saturday":  {"breakfast": "Oats + nuts", "lunch": "Roti + soya curry + salad", "dinner": "Clear soup + 1 roti", "snacks": "Guava, coconut water"},
            "Sunday":    {"breakfast": "Idli + sambar", "lunch": "Brown rice + arhar dal", "dinner": "Grilled fish + salad", "snacks": "Pomegranate, herbal tea"},
        }
    },
    "heart_disease": {
        "avoid": ["saturated fat", "trans fat", "excess salt", "red meat", "fried food", "alcohol", "sugary drinks"],
        "guidelines": "Heart-healthy: low sodium, low saturated fat, high omega-3, high fibre.",
        "plan": {
            "Monday":    {"breakfast": "Oats + flaxseeds + berries", "lunch": "Brown rice + dal + salad", "dinner": "Grilled fish + 1 roti", "snacks": "Walnuts, coconut water"},
            "Tuesday":   {"breakfast": "Egg whites + whole wheat toast", "lunch": "Jowar roti + rajma", "dinner": "Vegetable soup + 1 roti", "snacks": "Almonds, orange"},
            "Wednesday": {"breakfast": "Dalia + milk", "lunch": "Multigrain roti + sabzi", "dinner": "Brown rice + fish curry", "snacks": "Sunflower seeds, pear"},
            "Thursday":  {"breakfast": "Sprouts + buttermilk", "lunch": "Roti + moong dal", "dinner": "Grilled paneer + salad", "snacks": "Flaxseeds, apple"},
            "Friday":    {"breakfast": "Oats upma", "lunch": "Brown rice + chana masala", "dinner": "Khichdi + cucumber raita", "snacks": "Pumpkin seeds, green tea"},
            "Saturday":  {"breakfast": "Idli + sambar (low salt)", "lunch": "Roti + palak paneer", "dinner": "Fish / tofu + brown rice", "snacks": "Guava, amla juice"},
            "Sunday":    {"breakfast": "Besan cheela", "lunch": "Brown rice + arhar dal + salad", "dinner": "Roti + lauki sabzi", "snacks": "Pomegranate, herbal tea"},
        }
    },
    "general": {
        "avoid": ["excess junk food", "processed snacks", "excess sugar"],
        "guidelines": "Balanced Indian diet with all food groups.",
        "plan": {
            "Monday":    {"breakfast": "Poha with nuts", "lunch": "Dal rice + sabzi", "dinner": "Roti + paneer curry", "snacks": "Fruit, tea"},
            "Tuesday":   {"breakfast": "Idli + sambar", "lunch": "Roti + dal + salad", "dinner": "Rice + curd curry", "snacks": "Sprouts"},
            "Wednesday": {"breakfast": "Upma + green chutney", "lunch": "Pulao + raita", "dinner": "Roti + vegetables", "snacks": "Banana, nuts"},
            "Thursday":  {"breakfast": "Besan cheela", "lunch": "Dal rice + aloo sabzi", "dinner": "Khichdi + ghee", "snacks": "Makhana, lassi"},
            "Friday":    {"breakfast": "Oats + milk", "lunch": "Roti + rajma", "dinner": "Dosa + sambar", "snacks": "Apple, almond"},
            "Saturday":  {"breakfast": "Dalia + nuts", "lunch": "Rice + fish or paneer", "dinner": "Roti + mixed veggie", "snacks": "Coconut water"},
            "Sunday":    {"breakfast": "Paratha + curd (whole wheat)", "lunch": "Special dal makhni + rice", "dinner": "Khichdi + sabzi", "snacks": "Seasonal fruit"},
        }
    }
}

# ── YOGA KNOWLEDGE BASE ─────────────────────────────────────────────────────
YOGA_PLANS = {
    "back_pain": {
        "recommended": [
            "Balasana (Child's Pose) — releases lower back tension",
            "Marjaryasana-Bitilasana (Cat-Cow Pose) — improves spine flexibility",
            "Setu Bandhasana (Bridge Pose) — strengthens back muscles",
            "Bhujangasana (Cobra Pose — gentle) — stretches spine",
            "Supta Matsyendrasana (Supine Twist) — relieves spinal compression",
        ],
        "avoid": ["Halasana (Plow)", "Sirsasana (Headstand)", "Deep forward bends with straight legs"],
        "duration": "20–30 minutes daily",
        "note": "Stop immediately if sharp pain occurs. Begin slowly."
    },
    "hypertension": {
        "recommended": [
            "Savasana (Corpse Pose) — reduces blood pressure",
            "Sukhasana (Easy Pose) with pranayama — calms nervous system",
            "Viparita Karani (Legs-Up-Wall) — gentle inversion",
            "Anulom Vilom (Alternate Nostril Breathing) — stress reduction",
            "Shashankasana (Hare Pose) — relaxes heart",
        ],
        "avoid": ["Sirsasana", "Sarvangasana", "Hot yoga", "Intense backbends"],
        "duration": "20 minutes daily, early morning",
        "note": "Avoid holding breath. Never strain."
    },
    "diabetes": {
        "recommended": [
            "Mandukasana (Frog Pose) — stimulates pancreas",
            "Paschimottanasana (Seated Forward Bend) — massages abdominal organs",
            "Dhanurasana (Bow Pose) — activates pancreatic function",
            "Ardha Matsyendrasana (Half Spinal Twist) — improves insulin sensitivity",
            "Surya Namaskar (Sun Salutation 4–6 rounds) — overall metabolism",
        ],
        "avoid": ["Very intense asanas without warm-up", "Prolonged inversions"],
        "duration": "30 minutes, 5 days/week",
        "note": "Practice before meals. Monitor blood sugar before and after."
    },
    "anxiety": {
        "recommended": [
            "Balasana (Child's Pose) — immediate calm",
            "Uttanasana (Standing Forward Fold) — releases tension",
            "Viparita Karani (Legs-Up-Wall) — nervous system reset",
            "Shavasana + Yoga Nidra — deep relaxation",
            "Bhramari Pranayama (Bee Breath) — reduces anxiety quickly",
        ],
        "avoid": ["Vigorous sequences", "Kapalbhati (if anxiety is acute)"],
        "duration": "15–20 minutes twice daily",
        "note": "Focus on slow exhalation. Never force breathing."
    },
    "thyroid": {
        "recommended": [
            "Sarvangasana (Shoulder Stand) — stimulates thyroid gland",
            "Halasana (Plow Pose) — activates thyroid region",
            "Matsyasana (Fish Pose) — gentle thyroid stretch",
            "Ujjayi Pranayama (Ocean Breath) — regulates metabolism",
            "Surya Namaskar (6 rounds) — whole body metabolism boost",
        ],
        "avoid": ["Overexertion", "Heated yoga for hyperthyroidism"],
        "duration": "25–30 minutes daily",
        "note": "Hypothyroidism can do inversions. Hyperthyroidism: avoid Sarvangasana."
    },
    "obesity": {
        "recommended": [
            "Surya Namaskar (10–12 rounds) — calorie burn, full body",
            "Trikonasana (Triangle Pose) — tones waist",
            "Navasana (Boat Pose) — core strength",
            "Ardha Chandrasana (Half Moon) — balance + toning",
            "Kapalbhati Pranayama (5 minutes) — fat burn, metabolism",
        ],
        "avoid": ["Jumping without warm-up", "Heavy inversions with excess weight"],
        "duration": "45–60 minutes, 5 days/week",
        "note": "Start slow, build intensity. Combine with walking."
    },
    "pcos": {
        "recommended": [
            "Supta Baddha Konasana (Reclining Butterfly) — opens hips, relieves cramps",
            "Setu Bandhasana (Bridge Pose) — strengthens pelvic floor",
            "Bhujangasana (Cobra) — stimulates ovaries",
            "Nadi Shodhana (Alternate Nostril Breathing) — hormone balance",
            "Surya Namaskar (8 rounds) — hormone regulation",
        ],
        "avoid": ["Very intense hot yoga", "Prolonged inversions during menstruation"],
        "duration": "30 minutes daily",
        "note": "Avoid strenuous asanas during heavy menstruation."
    },
    "arthritis": {
        "recommended": [
            "Tadasana (Mountain Pose) — posture alignment, gentle",
            "Balasana (Child's Pose) — joint relief",
            "Vrikshasana (Tree Pose — with support) — gentle balance",
            "Supine leg raises — joint mobility",
            "Anulom Vilom — reduces inflammation markers",
        ],
        "avoid": ["High-impact poses", "Deep squats", "Any pose causing joint pain"],
        "duration": "20 minutes daily, gentle pace",
        "note": "Never force joints. Use blocks/chairs for support."
    },
    "heart_disease": {
        "recommended": [
            "Savasana (Corpse Pose) — heart rate calming",
            "Sukhasana + slow breathing — blood pressure regulation",
            "Anulom Vilom Pranayama — oxygen circulation",
            "Setu Bandhasana (gentle) — mild cardio",
            "Yoga Nidra — stress hormone reduction",
        ],
        "avoid": ["Sirsasana", "Sarvangasana", "Strenuous vinyasa", "Breath retention (Kumbhaka)"],
        "duration": "15–20 minutes, gentle pace only",
        "note": "Always consult cardiologist before yoga. Never hold breath."
    },
    "general": {
        "recommended": [
            "Surya Namaskar (Sun Salutation) — full body warm-up",
            "Trikonasana (Triangle Pose) — balance and stretch",
            "Vrikshasana (Tree Pose) — stability",
            "Bhujangasana (Cobra) — back strength",
            "Anulom Vilom — breathing regulation",
        ],
        "avoid": ["Any pose causing sharp pain or discomfort"],
        "duration": "30 minutes daily",
        "note": "Listen to your body. Progress gradually."
    }
}

# ── MEDITATION KNOWLEDGE BASE ────────────────────────────────────────────────
MEDITATION_PLANS = {
    "stress": {
        "technique": "Body Scan Meditation",
        "duration": "15 minutes",
        "steps": [
            "Find a comfortable seated or lying position.",
            "Close your eyes and take 3 deep breaths.",
            "Slowly scan from head to toe, releasing tension in each muscle group.",
            "When thoughts arise, gently return focus to the body.",
            "End with 2 minutes of gratitude — think of 3 things you appreciate today."
        ],
        "frequency": "Daily, preferably morning or before sleep.",
        "tip": "Use a soft timer so you don't check the clock."
    },
    "sleep": {
        "technique": "4-7-8 Breathing + Yoga Nidra",
        "duration": "20 minutes before bed",
        "steps": [
            "Lie down in Shavasana (flat on back).",
            "Breathe in for 4 counts, hold for 7, exhale for 8. Repeat 4 times.",
            "Progressively relax each body part from toes to head.",
            "Visualize a peaceful place — beach, mountain, garden.",
            "Allow yourself to drift off naturally."
        ],
        "frequency": "Every night 30 minutes before sleep.",
        "tip": "Avoid screens 1 hour before this practice."
    },
    "focus": {
        "technique": "Mindfulness of Breath",
        "duration": "10 minutes",
        "steps": [
            "Sit comfortably with spine straight.",
            "Focus attention on the sensation of breath at the nostrils.",
            "Count each exhale from 1 to 10, then restart.",
            "When distracted, gently note 'thinking' and return to breath.",
            "End with 1 minute of open awareness."
        ],
        "frequency": "Morning daily. Can add a 5-minute version before work tasks.",
        "tip": "Start with 5 minutes if 10 feels too long."
    },
    "pain": {
        "technique": "Loving-Kindness + Pain Acceptance Meditation",
        "duration": "15 minutes",
        "steps": [
            "Sit or lie in the most comfortable position available.",
            "Take 5 slow breaths; on each exhale, soften the area of pain.",
            "Silently say: 'May I be at ease. May this discomfort lessen.'",
            "Visualize warm, golden healing energy flowing to the painful area.",
            "End with 3 slow breaths and gentle movement."
        ],
        "frequency": "2–3 times daily, especially before sleep.",
        "tip": "Acceptance reduces suffering. Fighting pain increases it."
    },
    "hormonal": {
        "technique": "Hormonal Balance Visualization",
        "duration": "12 minutes",
        "steps": [
            "Lie on your back, hands on lower abdomen.",
            "Take slow abdominal breaths for 2 minutes.",
            "Visualize a calm, balanced endocrine system — glowing warmly.",
            "Repeat affirmation: 'My hormones are balanced. My body heals.'",
            "End with Yoga Nidra — full body relaxation for 5 minutes."
        ],
        "frequency": "Daily, especially in the morning.",
        "tip": "Combine with 20-minute walk for best hormonal results."
    },
    "general": {
        "technique": "Mindful Awareness",
        "duration": "10 minutes",
        "steps": [
            "Sit quietly and observe your thoughts without judgment.",
            "Focus on your natural breath.",
            "Let thoughts pass like clouds — don't engage.",
            "Return to breath each time the mind wanders.",
            "End with a positive affirmation."
        ],
        "frequency": "Daily morning practice.",
        "tip": "Consistency matters more than duration."
    }
}

# ── Condition → Meditation goal mapping ─────────────────────────────────────
CONDITION_MEDITATION_MAP = {
    "arthritis": "pain",
    "back_pain": "pain",
    "pcos": "hormonal",
    "thyroid": "hormonal",
    "anxiety": "stress",
    "heart_disease": "stress",
    "hypertension": "stress",
    "obesity": "focus",
    "diabetes": "focus",
    "general": "general",
}


def get_diet_plan(condition: str, preferences: str = "vegetarian", region: str = "North Indian") -> dict:
    """Return a 7-day diet plan for the given condition."""
    condition_key = condition.lower().replace(" ", "_")
    plan = DIET_PLANS.get(condition_key, DIET_PLANS["general"])
    return {
        "condition": condition,
        "preferences": preferences,
        "region": region,
        "guidelines": plan["guidelines"],
        "plan": plan["plan"],
        "avoid": plan["avoid"],
        "disclaimer": "This plan is for general guidance only. Please consult your doctor or dietitian before making dietary changes.",
    }


def get_yoga_recommendations(condition: str, severity: str = "mild") -> dict:
    """Return safe yoga poses for the given health condition."""
    condition_key = condition.lower().replace(" ", "_")
    yoga = YOGA_PLANS.get(condition_key, YOGA_PLANS["general"])
    if severity == "severe":
        yoga = YOGA_PLANS["general"]  # gentler fallback for severe conditions
    return {
        "condition": condition,
        "severity": severity,
        "recommended_poses": yoga["recommended"],
        "avoid_poses": yoga["avoid"],
        "session_duration": yoga["duration"],
        "safety_note": yoga["note"],
    }


def get_meditation_plan(goal: str, feedback: str = None) -> dict:
    """
    Return a daily meditation plan.
    Adapts based on feedback (if provided).
    Also maps health conditions → meditation goals automatically.
    """
    # Map condition names to meditation goals
    goal_key = CONDITION_MEDITATION_MAP.get(goal.lower().replace(" ", "_"), goal.lower())

    # Simple feedback adaptation
    if feedback:
        feedback_lower = feedback.lower()
        if "too long" in feedback_lower:
            goal_key = "focus"  # shorter plan
        elif "not working" in feedback_lower or "still stressed" in feedback_lower:
            goal_key = "stress"

    plan = MEDITATION_PLANS.get(goal_key, MEDITATION_PLANS["general"])
    return {
        "goal": goal,
        "technique": plan["technique"],
        "duration": plan["duration"],
        "daily_steps": plan["steps"],
        "frequency": plan["frequency"],
        "pro_tip": plan["tip"],
        "adapted_from_feedback": feedback is not None,
    }


def generate_diet_pdf_text(plan_data: dict) -> str:
    """
    Generate plain-text representation of the diet plan for PDF export.
    The PDF service will convert this to a properly formatted PDF.
    """
    lines = [
        f"FCMAS-W — 7-Day Diet Plan",
        f"Condition: {plan_data['condition'].upper()}",
        f"Preference: {plan_data['preferences']} | Region: {plan_data['region']}",
        f"Guidelines: {plan_data['guidelines']}",
        "",
        "━" * 60,
        "7-DAY MEAL PLAN",
        "━" * 60,
    ]
    for day, meals in plan_data["plan"].items():
        lines.append(f"\n{day.upper()}")
        lines.append(f"  Breakfast : {meals['breakfast']}")
        lines.append(f"  Lunch     : {meals['lunch']}")
        lines.append(f"  Dinner    : {meals['dinner']}")
        lines.append(f"  Snacks    : {meals['snacks']}")
    lines.append("\n" + "━" * 60)
    lines.append("FOODS TO AVOID: " + ", ".join(plan_data["avoid"]))
    lines.append("━" * 60)
    lines.append(f"\n⚕️  {plan_data['disclaimer']}")
    lines.append("\nGenerated by FCMAS-W Healthcare AI System")
    return "\n".join(lines)


async def log_wellness_feedback(patient_id: str, module: str, rating: int, comment: str):
    """Persist user feedback for future personalization."""
    from database.db import wellness_logs_col
    await wellness_logs_col.insert_one({
        "patient_id": patient_id,
        "module": module,
        "rating": rating,
        "comment": comment,
        "timestamp": datetime.utcnow().isoformat()
    })


def get_all_supported_conditions() -> dict:
    """Return all supported conditions per module."""
    return {
        "diet": list(DIET_PLANS.keys()),
        "yoga": list(YOGA_PLANS.keys()),
        "meditation": list(MEDITATION_PLANS.keys()),
    }
