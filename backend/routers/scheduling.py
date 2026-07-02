"""Scheduling router — natural language appointment booking."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from services.scheduling_service import (
    book_appointment, get_available_slots,
    get_patient_appointments, cancel_appointment
)
from services.email_service import send_appointment_email
from utils.auth import get_current_user

router = APIRouter(prefix="/api/v1/schedule", tags=["Scheduling"])


class ScheduleRequest(BaseModel):
    text: str
    urgency_keywords: Optional[list] = []


async def _email_task(user, result):
    """Background email sender — never raises, never blocks booking."""
    try:
        await send_appointment_email(
            to_email=user.get("email", ""),
            patient_name=user.get("name", "Patient"),
            doctor_name=result.get("doctor", "Doctor"),
            specialty=result.get("specialty", "General"),
            slot_time=result.get("slot_time", ""),
            appointment_id=result.get("appointment_id", ""),
        )
    except Exception as e:
        print(f"[EMAIL BACKGROUND ERROR] {e}")


@router.post("/request", summary="Book appointment via natural language")
async def request_appointment(
    req: ScheduleRequest,
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user)
):
    result = await book_appointment(user["user_id"], req.text)
    if "error" in result:
        raise HTTPException(status_code=503, detail=result["error"])

    # ── Send confirmation email via FastAPI BackgroundTasks ────────────────
    background_tasks.add_task(_email_task, user, result)

    return result


@router.get("/slots", summary="Get available slots")
async def available_slots(specialty: str = "General"):
    slots = await get_available_slots(specialty)
    return {"specialty": specialty, "slots": slots, "count": len(slots)}


@router.get("/my-appointments", summary="Get patient's appointments")
async def my_appointments(user=Depends(get_current_user)):
    apts = await get_patient_appointments(user["user_id"])
    return {"appointments": apts, "count": len(apts)}


@router.delete("/{appointment_id}", summary="Cancel an appointment")
async def cancel(appointment_id: str, user=Depends(get_current_user)):
    success = await cancel_appointment(appointment_id, user["user_id"])
    if not success:
        raise HTTPException(status_code=404, detail="Appointment not found or not yours.")
    return {"message": "Appointment cancelled successfully."}


@router.get("/{appointment_id}/explain", summary="Explain slot assignment reasoning")
async def explain_appointment(appointment_id: str, user=Depends(get_current_user)):
    from database.db import appointments_col
    from bson import ObjectId
    apt = await appointments_col.find_one({"_id": ObjectId(appointment_id), "patient_id": user["user_id"]})
    if not apt:
        raise HTTPException(status_code=404, detail="Appointment not found.")
    return {
        "appointment_id": appointment_id,
        "slot": apt.get("slot_time"),
        "doctor": apt.get("doctor_name"),
        "urgency_score": apt.get("urgency"),
        "fairness_score": apt.get("fairness_score"),
        "explanation": (
            f"Intent detected: {apt.get('nlp_result', {}).get('intent', 'N/A')}. "
            f"Language: {apt.get('nlp_result', {}).get('language_name', 'N/A')}. "
            f"Urgency level {apt.get('urgency', 1)}/5. "
            f"Slot selected for {apt.get('specialty', 'General')} with doctor {apt.get('doctor_name')}. "
            f"System fairness index: {apt.get('fairness_score', 'N/A')}."
        )
    }
