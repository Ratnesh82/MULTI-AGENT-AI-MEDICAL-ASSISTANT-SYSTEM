"""
Scheduling Engine — MVP Rule-Based Implementation.
Priority Queue approach: sorts candidates by urgency + fairness (wait time).
Upgrade path: replace schedule() with PPO RL agent via stable-baselines3.
"""
from datetime import datetime, timedelta
from typing import List, Optional
from bson import ObjectId
from database.db import appointments_col, doctors_col
from utils.fairness import compute_urgency_score, compute_fairness_score
from services.nlp_service import process_nlp


# ── Doctor seed data (loaded if DB is empty) ────────────────────────────────
SEED_DOCTORS = [
    {"name": "Dr. Anjali Sharma", "specialty": "General", "available_slots": []},
    {"name": "Dr. Rajesh Verma", "specialty": "Cardiology", "available_slots": []},
    {"name": "Dr. Priya Singh", "specialty": "Orthopedics", "available_slots": []},
    {"name": "Dr. Amit Gupta", "specialty": "Neurology", "available_slots": []},
    {"name": "Dr. Sunita Patel", "specialty": "General", "available_slots": []},
]


def generate_slots(start: datetime, days: int = 7, slots_per_day: int = 8) -> List[datetime]:
    """Generate hour-wise appointment slots for N days starting from start."""
    slots = []
    for d in range(days):
        base = start.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=d)
        for h in range(slots_per_day):
            slots.append(base + timedelta(hours=h))
    return slots


async def seed_doctors_if_empty():
    """Seed doctor collection with default doctors if empty."""
    count = await doctors_col.count_documents({})
    if count == 0:
        tomorrow = datetime.utcnow() + timedelta(days=1)
        for doc in SEED_DOCTORS:
            doc_copy = doc.copy()
            doc_copy["available_slots"] = [
                s.isoformat() for s in generate_slots(tomorrow)
            ]
            await doctors_col.insert_one(doc_copy)


async def find_best_slot(specialty: str, urgency: int) -> Optional[dict]:
    """
    Find the earliest available slot for a given specialty.
    Urgency 4-5 → earliest slot across ALL general doctors.
    Urgency 1-3 → matched specialty doctor first.
    """
    await seed_doctors_if_empty()

    # Build query: for high urgency prefer general availability
    query = {"specialty": specialty} if urgency < 4 else {"specialty": "General"}
    doctors = await doctors_col.find(query).to_list(length=10)

    if not doctors:
        doctors = await doctors_col.find({}).to_list(length=10)

    now_iso = datetime.utcnow().isoformat()
    best_doctor = None
    best_slot = None

    for doctor in doctors:
        for slot in doctor.get("available_slots", []):
            if slot > now_iso:
                if best_slot is None or slot < best_slot:
                    best_slot = slot
                    best_doctor = doctor

    return {"doctor": best_doctor, "slot": best_slot}


def build_explanation(urgency: int, specialty: str, slot: str, fairness: float) -> str:
    """Generate human-readable explanation for slot assignment."""
    urgency_label = {5: "Critical", 4: "High", 3: "Moderate", 2: "Low", 1: "Routine"}.get(urgency, "Routine")
    slot_dt = datetime.fromisoformat(slot).strftime("%d %b %Y at %I:%M %p")
    return (
        f"Urgency level detected: {urgency_label} (score {urgency}/5). "
        f"Best available {specialty} slot assigned: {slot_dt}. "
        f"System fairness index: {fairness:.2f}/1.00 — "
        f"{'Fair distribution maintained.' if fairness > 0.7 else 'Some imbalance detected, monitoring.'}"
    )


async def book_appointment(patient_id: str, text: str) -> dict:
    """
    Main scheduling entry point.
    1. NLP → intent + entities
    2. Urgency scoring
    3. Find best slot (priority-aware)
    4. Remove slot from doctor availability
    5. Persist appointment
    6. Return result with explanation
    """
    # Step 1: NLP
    nlp_result = process_nlp(text)
    specialty = nlp_result["entities"].get("specialty_hint", "General")

    # Step 2: Urgency
    urgency = compute_urgency_score(text)

    # Step 3: Find slot
    slot_info = await find_best_slot(specialty, urgency)
    if not slot_info or not slot_info["slot"]:
        return {"error": "No available slots found. Please try again later."}

    doctor = slot_info["doctor"]
    slot = slot_info["slot"]

    # Step 4: Remove booked slot from doctor's availability
    updated_slots = [s for s in doctor["available_slots"] if s != slot]
    await doctors_col.update_one(
        {"_id": doctor["_id"]},
        {"$set": {"available_slots": updated_slots}}
    )

    # Step 5: Compute fairness across recent appointments
    recent = await appointments_col.find(
        {}, {"wait_hours": 1}
    ).sort("created_at", -1).limit(20).to_list(length=20)
    wait_times = [r.get("wait_hours", 0) for r in recent]

    # Compute wait time in hours for this appointment
    slot_dt = datetime.fromisoformat(slot)
    wait_hours = (slot_dt - datetime.utcnow()).total_seconds() / 3600
    wait_times.append(wait_hours)
    fairness = compute_fairness_score(wait_times)

    # Step 6: Persist appointment
    appointment = {
        "patient_id": patient_id,
        "doctor_id": str(doctor["_id"]),
        "doctor_name": doctor["name"],
        "specialty": specialty,
        "slot_time": slot,
        "urgency": urgency,
        "wait_hours": round(wait_hours, 2),
        "fairness_score": round(fairness, 4),
        "status": "confirmed",
        "created_at": datetime.utcnow().isoformat(),
        "nlp_result": nlp_result,
    }
    result = await appointments_col.insert_one(appointment)

    explanation = build_explanation(urgency, specialty, slot, fairness)

    return {
        "appointment_id": str(result.inserted_id),
        "slot": slot,
        "doctor": doctor["name"],
        "specialty": specialty,
        "urgency_score": urgency,
        "fairness_score": round(fairness, 4),
        "language_detected": nlp_result["language_name"],
        "intent": nlp_result["intent"],
        "explanation": explanation,
    }


async def get_available_slots(specialty: str = "General") -> List[dict]:
    """Return all available slots for a specialty."""
    await seed_doctors_if_empty()
    doctors = await doctors_col.find({"specialty": specialty}).to_list(length=10)
    slots = []
    now_iso = datetime.utcnow().isoformat()
    for doctor in doctors:
        for slot in doctor.get("available_slots", []):
            if slot > now_iso:
                slots.append({
                    "doctor": doctor["name"],
                    "specialty": doctor["specialty"],
                    "slot": slot,
                })
    return sorted(slots, key=lambda x: x["slot"])[:20]


async def get_patient_appointments(patient_id: str) -> List[dict]:
    """Retrieve all appointments for a patient."""
    appointments = await appointments_col.find(
        {"patient_id": patient_id}
    ).sort("slot_time", 1).to_list(length=50)
    for apt in appointments:
        apt["_id"] = str(apt["_id"])
    return appointments


async def cancel_appointment(appointment_id: str, patient_id: str) -> bool:
    """Cancel an appointment and return the slot to the doctor."""
    apt = await appointments_col.find_one({"_id": ObjectId(appointment_id), "patient_id": patient_id})
    if not apt:
        return False
    # Return slot to doctor
    await doctors_col.update_one(
        {"_id": ObjectId(apt["doctor_id"])},
        {"$push": {"available_slots": apt["slot_time"]}}
    )
    await appointments_col.update_one(
        {"_id": ObjectId(appointment_id)},
        {"$set": {"status": "cancelled"}}
    )
    return True
