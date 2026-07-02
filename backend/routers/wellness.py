"""Wellness router — Phase 2: PDF export, conditions list, notifications."""
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
from services.wellness_service import (
    get_diet_plan, get_yoga_recommendations,
    get_meditation_plan, log_wellness_feedback, get_all_supported_conditions
)
from services.pdf_service import generate_diet_pdf
from services.nlp_service import process_nlp
from utils.auth import get_current_user

router = APIRouter(prefix="/api/v1/wellness", tags=["Wellness"])


class DietRequest(BaseModel):
    condition: str
    preferences: Optional[str] = "vegetarian"
    region: Optional[str] = "North Indian"


class YogaRequest(BaseModel):
    condition: str
    severity: Optional[str] = "mild"


class MeditationRequest(BaseModel):
    goal: str
    feedback: Optional[str] = None


class FeedbackRequest(BaseModel):
    module: str          # diet | yoga | meditation
    rating: int          # 1-5
    comment: Optional[str] = ""


@router.get("/conditions", summary="List all supported conditions per module")
async def supported_conditions():
    return get_all_supported_conditions()


@router.post("/diet", summary="Get 7-day Indian diet plan")
async def diet_plan(req: DietRequest):
    plan = get_diet_plan(req.condition, req.preferences, req.region)
    return plan


@router.post("/diet/pdf", summary="Download 7-day diet plan as PDF")
async def diet_pdf(req: DietRequest):
    pdf_bytes = generate_diet_pdf(req.condition, req.preferences, req.region)
    # If reportlab installed → PDF, else → plain text
    is_pdf = pdf_bytes[:4] == b"%PDF"
    media_type = "application/pdf" if is_pdf else "text/plain"
    filename = f"diet_plan_{req.condition}.pdf" if is_pdf else f"diet_plan_{req.condition}.txt"
    return Response(
        content=pdf_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.post("/yoga", summary="Get yoga recommendations for a health condition")
async def yoga_recommendations(req: YogaRequest):
    recs = get_yoga_recommendations(req.condition, req.severity)
    return recs


@router.post("/meditation", summary="Get daily meditation plan")
async def meditation_plan(req: MeditationRequest):
    plan = get_meditation_plan(req.goal, req.feedback)
    return plan


@router.post("/feedback", summary="Submit wellness feedback for personalization")
async def submit_feedback(req: FeedbackRequest, user=Depends(get_current_user)):
    await log_wellness_feedback(user["user_id"], req.module, req.rating, req.comment)
    return {"message": "Feedback recorded. Thank you! Your plan will adapt over time."}


@router.post("/analyze-text", summary="NLP analysis — detect language and intent from text")
async def analyze_text(body: dict):
    """Utility endpoint: run NLP pipeline on any text."""
    text = body.get("text", "")
    if not text:
        return {"error": "text field is required"}
    return process_nlp(text)
