"""
Admin Router — System-wide statistics, patient list, appointment management.
NOTE: In production, protect with an admin role check.
For MVP, any logged-in user with 'admin' in their email gets access.
"""
from fastapi import APIRouter, Depends, HTTPException
from database.db import patients_col, appointments_col, doctors_col, wellness_logs_col
from utils.auth import get_current_user
from utils.fairness import compute_fairness_score
from datetime import datetime

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


async def require_admin(user=Depends(get_current_user)):
    """Simple admin gate: email must contain 'admin'."""
    if "admin" not in user.get("email", ""):
        raise HTTPException(status_code=403, detail="Admin access required.")
    return user


@router.get("/stats", summary="System-wide statistics")
async def get_stats(user=Depends(get_current_user)):
    """Dashboard stats — available to all logged-in users."""
    total_patients = await patients_col.count_documents({})
    total_appointments = await appointments_col.count_documents({})
    confirmed = await appointments_col.count_documents({"status": "confirmed"})
    cancelled = await appointments_col.count_documents({"status": "cancelled"})
    total_doctors = await doctors_col.count_documents({})
    total_feedback = await wellness_logs_col.count_documents({})

    # Fairness stats from recent appointments
    recent = await appointments_col.find(
        {}, {"wait_hours": 1, "urgency": 1}
    ).sort("created_at", -1).limit(50).to_list(length=50)

    wait_times = [r.get("wait_hours", 0) for r in recent]
    fairness = compute_fairness_score(wait_times)

    urgency_dist = {str(i): 0 for i in range(1, 6)}
    for r in recent:
        u = str(r.get("urgency", 1))
        urgency_dist[u] = urgency_dist.get(u, 0) + 1

    return {
        "patients": total_patients,
        "appointments": {
            "total": total_appointments,
            "confirmed": confirmed,
            "cancelled": cancelled,
        },
        "doctors": total_doctors,
        "wellness_feedbacks": total_feedback,
        "fairness_index": round(fairness, 4),
        "urgency_distribution": urgency_dist,
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.get("/appointments", summary="All appointments")
async def all_appointments(
    limit: int = 50,
    status: str = None,
    user=Depends(get_current_user)
):
    """List all appointments with optional status filter."""
    query = {}
    if status:
        query["status"] = status
    apts = await appointments_col.find(query).sort("created_at", -1).to_list(length=limit)
    for a in apts:
        a["_id"] = str(a["_id"])
    return {"appointments": apts, "count": len(apts)}


@router.get("/patients", summary="All patients")
async def all_patients(user=Depends(get_current_user)):
    patients = await patients_col.find({}, {"password": 0}).to_list(length=200)
    for p in patients:
        p["_id"] = str(p["_id"])
    return {"patients": patients, "count": len(patients)}


@router.get("/doctors", summary="List all doctors with slot counts")
async def all_doctors(user=Depends(get_current_user)):
    doctors = await doctors_col.find({}).to_list(length=50)
    result = []
    for d in doctors:
        result.append({
            "id": str(d["_id"]),
            "name": d["name"],
            "specialty": d["specialty"],
            "available_slots_count": len([
                s for s in d.get("available_slots", [])
                if s > datetime.utcnow().isoformat()
            ]),
        })
    return {"doctors": result, "count": len(result)}


@router.post("/doctors/add", summary="Add a new doctor (admin)")
async def add_doctor(body: dict, user=Depends(require_admin)):
    from services.scheduling_service import generate_slots
    name = body.get("name")
    specialty = body.get("specialty", "General")
    if not name:
        raise HTTPException(status_code=400, detail="Doctor name is required.")
    from datetime import timedelta
    slots = [s.isoformat() for s in generate_slots(datetime.utcnow() + timedelta(days=1))]
    result = await doctors_col.insert_one({"name": name, "specialty": specialty, "available_slots": slots})
    return {"message": f"Doctor {name} added.", "id": str(result.inserted_id)}


@router.get("/wellness-feedback", summary="All wellness feedback logs (admin)")
async def wellness_feedback(user=Depends(require_admin)):
    logs = await wellness_logs_col.find({}).sort("timestamp", -1).to_list(length=100)
    for l in logs:
        l["_id"] = str(l["_id"])
    return {"logs": logs, "count": len(logs)}


@router.get("/analytics/fairness", summary="Fairness analytics over time")
async def fairness_analytics(user=Depends(get_current_user)):
    """Return fairness index per day for the last 7 days."""
    from datetime import timedelta
    result = []
    base = datetime.utcnow()
    for day_offset in range(6, -1, -1):
        day = base - timedelta(days=day_offset)
        day_str = day.strftime("%Y-%m-%d")
        apts = await appointments_col.find(
            {"created_at": {"$regex": f"^{day_str}"}},
            {"wait_hours": 1}
        ).to_list(length=100)
        waits = [a.get("wait_hours", 0) for a in apts]
        result.append({
            "date": day_str,
            "appointments": len(apts),
            "fairness_index": round(compute_fairness_score(waits), 4),
        })
    return {"fairness_over_time": result}
