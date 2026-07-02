"""
Notification Service — In-app appointment reminder mock.
Phase 2: Stores reminders in MongoDB. 
Phase 3 upgrade: replace with actual email/SMS via sendgrid/twilio.
"""
from datetime import datetime, timedelta
from database.db import db

notifications_col = db["notifications"]


async def create_reminder(patient_id: str, appointment_id: str, slot_time: str, doctor_name: str):
    """Create an appointment reminder 24h before the slot."""
    slot_dt = datetime.fromisoformat(slot_time)
    remind_at = slot_dt - timedelta(hours=24)
    await notifications_col.insert_one({
        "patient_id": patient_id,
        "appointment_id": appointment_id,
        "type": "appointment_reminder",
        "message": f"Reminder: Your appointment with {doctor_name} is tomorrow at {slot_dt.strftime('%I:%M %p')}.",
        "remind_at": remind_at.isoformat(),
        "slot_time": slot_time,
        "read": False,
        "created_at": datetime.utcnow().isoformat(),
    })


async def get_notifications(patient_id: str) -> list:
    """Get all unread notifications for a patient."""
    notes = await notifications_col.find(
        {"patient_id": patient_id}
    ).sort("created_at", -1).to_list(length=20)
    for n in notes:
        n["_id"] = str(n["_id"])
    return notes


async def mark_read(notification_id: str, patient_id: str):
    """Mark a notification as read."""
    from bson import ObjectId
    await notifications_col.update_one(
        {"_id": ObjectId(notification_id), "patient_id": patient_id},
        {"$set": {"read": True}}
    )
