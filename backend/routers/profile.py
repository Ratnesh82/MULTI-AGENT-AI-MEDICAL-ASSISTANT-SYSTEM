"""
Profile Router — Phase 3.
Endpoints: patient profile, health score, notifications, full health report PDF.
"""
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from utils.auth import get_current_user
from database.db import patients_col, appointments_col, wellness_logs_col
from services.health_score_service import compute_health_score, personalize_wellness
from services.notification_service import get_notifications, mark_read

router = APIRouter(prefix="/api/v1/profile", tags=["Profile"])


@router.get("/me", summary="Get current patient profile + health score")
async def get_profile(user=Depends(get_current_user)):
    patient_id = user["user_id"]

    # Fetch patient record
    patient = await patients_col.find_one(
        {"_id_str": patient_id} if True else {},
        {"password": 0}
    )

    # Appointment history — urgency scores
    apts = await appointments_col.find(
        {"patient_id": patient_id}
    ).sort("created_at", -1).to_list(length=50)
    urgency_history = [a.get("urgency", 1) for a in apts]

    # Wellness feedback logs
    logs = await wellness_logs_col.find(
        {"patient_id": patient_id}
    ).to_list(length=100)
    wellness_ratings = [{"module": l.get("module"), "rating": l.get("rating", 3)} for l in logs]

    # Conditions — extracted from appointment records
    conditions = list({a.get("specialty", "general").lower() for a in apts if a.get("specialty")})
    if not conditions:
        conditions = ["general"]

    # Compute health score
    health_score = compute_health_score(
        conditions=conditions,
        urgency_history=urgency_history,
        wellness_ratings=wellness_ratings,
        age=user.get("age")
    )

    # Recent appointments (last 5)
    recent_apts = []
    for a in apts[:5]:
        a["_id"] = str(a["_id"])
        recent_apts.append(a)

    # Personalization hints
    personalization = {
        mod: personalize_wellness(conditions[0] if conditions else "general", logs, mod)
        for mod in ["diet", "yoga", "meditation"]
    }

    return {
        "patient_id": patient_id,
        "email": user.get("email"),
        "name": user.get("name", "Patient"),
        "health_score": health_score,
        "conditions": conditions,
        "appointment_count": len(apts),
        "recent_appointments": recent_apts,
        "wellness_personalization": personalization,
        "wellness_feedback_count": len(logs),
    }


@router.get("/health-score", summary="Compute AI health score for current patient")
async def health_score_endpoint(user=Depends(get_current_user)):
    patient_id = user["user_id"]
    apts = await appointments_col.find({"patient_id": patient_id}).to_list(length=50)
    logs = await wellness_logs_col.find({"patient_id": patient_id}).to_list(length=100)
    urgency_history = [a.get("urgency", 1) for a in apts]
    wellness_ratings = [{"module": l.get("module"), "rating": l.get("rating", 3)} for l in logs]
    conditions = list({a.get("specialty", "general").lower() for a in apts})
    score = compute_health_score(conditions or ["general"], urgency_history, wellness_ratings)
    return score


@router.get("/notifications", summary="Get in-app notifications for current patient")
async def notifications(user=Depends(get_current_user)):
    notes = await get_notifications(user["user_id"])
    return {"notifications": notes, "unread": sum(1 for n in notes if not n.get("read"))}


@router.post("/notifications/{notification_id}/read", summary="Mark notification as read")
async def mark_notification_read(notification_id: str, user=Depends(get_current_user)):
    await mark_read(notification_id, user["user_id"])
    return {"message": "Marked as read"}


@router.get("/report/pdf", summary="Download full health report as PDF")
async def full_health_report(user=Depends(get_current_user)):
    """Generate a comprehensive health report PDF for the patient."""
    patient_id = user["user_id"]

    apts = await appointments_col.find({"patient_id": patient_id}).sort("created_at", -1).to_list(50)
    logs = await wellness_logs_col.find({"patient_id": patient_id}).to_list(100)
    urgency_history = [a.get("urgency", 1) for a in apts]
    wellness_ratings = [{"module": l.get("module"), "rating": l.get("rating", 3)} for l in logs]
    conditions = list({a.get("specialty", "general").lower() for a in apts}) or ["general"]
    score = compute_health_score(conditions, urgency_history, wellness_ratings)

    pdf_bytes = _build_health_report_pdf(user, apts, logs, score, conditions)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="health_report.pdf"'}
    )


def _build_health_report_pdf(user, apts, logs, score, conditions) -> bytes:
    from datetime import datetime
    name = user.get("name", "Patient")
    email = user.get("email", "")

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, HRFlowable
        from reportlab.lib.units import cm
        import io

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        elems = []

        # Title
        title_s = ParagraphStyle("t", parent=styles["Heading1"], fontSize=20,
                                 textColor=colors.HexColor("#00c9a7"), spaceAfter=4)
        elems.append(Paragraph("FCMAS-W Health Report", title_s))
        sub_s = ParagraphStyle("s", parent=styles["Normal"], fontSize=10,
                               textColor=colors.HexColor("#8b949e"))
        elems.append(Paragraph(f"Patient: {name} | {email} | Generated: {datetime.utcnow().strftime('%d %b %Y %H:%M')} UTC", sub_s))
        elems.append(Spacer(1, 0.4*cm))
        elems.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#00c9a7")))
        elems.append(Spacer(1, 0.4*cm))

        # Health score
        hs_s = ParagraphStyle("hs", parent=styles["Heading2"], fontSize=14,
                              textColor=colors.HexColor(score["risk_color"]))
        elems.append(Paragraph(f"AI Health Score: {score['score']}/100 — {score['risk_level']}", hs_s))

        breakdown = score["breakdown"]
        bd_data = [["Factor", "Impact"],
                   ["Base Score", "+100"],
                   ["Condition Penalty", str(breakdown["condition_penalty"])],
                   ["Urgency History Penalty", str(breakdown["urgency_penalty"])],
                   ["Wellness Engagement Bonus", f"+{breakdown['wellness_bonus']}"]]
        bd_table = Table(bd_data, colWidths=[10*cm, 4*cm])
        bd_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#00c9a7")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#30363d")),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f0fbf8")]),
            ("ALIGN", (1,0), (1,-1), "CENTER"),
        ]))
        elems.append(bd_table)
        elems.append(Spacer(1, 0.4*cm))

        # Recommendations
        rec_s = ParagraphStyle("r", parent=styles["Heading2"], fontSize=12,
                               textColor=colors.HexColor("#0ea5e9"), spaceBefore=8)
        elems.append(Paragraph("Personalised Recommendations", rec_s))
        for rec in score["recommendations"]:
            elems.append(Paragraph(f"• {rec}", styles["Normal"]))
        elems.append(Spacer(1, 0.4*cm))

        # Appointment history
        if apts:
            elems.append(Paragraph("Recent Appointments", rec_s))
            apt_data = [["Date", "Doctor", "Specialty", "Urgency", "Status"]]
            for a in apts[:10]:
                slot = a.get("slot_time", "")[:10]
                apt_data.append([slot, a.get("doctor_name",""), a.get("specialty",""),
                                  str(a.get("urgency",1)), a.get("status","")])
            apt_table = Table(apt_data, colWidths=[2.5*cm, 4*cm, 3.5*cm, 2*cm, 2.5*cm])
            apt_table.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0ea5e9")),
                ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE", (0,0), (-1,-1), 8),
                ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#30363d")),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f0f8ff")]),
            ]))
            elems.append(apt_table)

        elems.append(Spacer(1, 0.5*cm))
        disc_s = ParagraphStyle("d", parent=styles["Normal"], fontSize=8,
                                textColor=colors.gray)
        elems.append(Paragraph("⚕️ This report is AI-generated for informational purposes only. Always consult a qualified medical professional.", disc_s))

        doc.build(elems)
        return buffer.getvalue()

    except ImportError:
        # Plain text fallback
        lines = [
            f"FCMAS-W Health Report — {name} ({email})",
            f"Generated: {datetime.utcnow().isoformat()}",
            "", f"AI Health Score: {score['score']}/100 — {score['risk_level']}",
            "", "Recommendations:", *[f"  • {r}" for r in score["recommendations"]],
            "", f"Conditions: {', '.join(conditions)}",
            f"Total Appointments: {len(apts)}",
        ]
        return "\n".join(lines).encode("utf-8")
