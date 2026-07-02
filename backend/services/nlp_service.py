"""
NLP Service — Multilingual Intent Classification.
MVP: langdetect + keyword matching (no GPU required).
Upgrade path: replace classify_intent() with mBERT/IndicBERT fine-tuned model.
"""
from langdetect import detect, LangDetectException
from typing import Tuple

# ── Intent keyword maps (English + Hindi/Hinglish) ──────────────────────────
INTENT_PATTERNS = {
    "book_appointment": [
        "appointment", "book", "schedule", "doctor", "milna", "bulao",
        "dikha", "dikhaiye", "slot", "meet", "consult", "milna hai"
    ],
    "cancel_appointment": [
        "cancel", "raddh", "nahi aana", "band karo", "delete appointment"
    ],
    "diet_plan": [
        "diet", "khana", "food", "meal", "kya khana", "nutrition",
        "kha sakta", "nahi khana", "diabetes diet", "bp diet"
    ],
    "yoga": [
        "yoga", "asana", "vyayam", "exercise", "stretch", "pose",
        "dard ke liye yoga", "back pain yoga"
    ],
    "meditation": [
        "meditation", "dhyan", "stress", "relief", "calm", "relax",
        "neend", "sleep", "anxiety", "man shant"
    ],
    "general_info": []
}

LANGUAGE_MAP = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu",
    "gu": "Gujarati",
}


def detect_language(text: str) -> Tuple[str, str]:
    """Detect language code and human-readable name."""
    try:
        code = detect(text)
        name = LANGUAGE_MAP.get(code, code.upper())
        return code, name
    except LangDetectException:
        return "en", "English"


def classify_intent(text: str) -> str:
    """
    Rule-based intent classification.
    Returns the best-matching intent key.
    Cancel takes priority when cancel keywords are present (avoids "cancel appointment"
    being misclassified as book_appointment due to the shared keyword "appointment").
    """
    text_lower = text.lower()

    # High-priority check: cancel explicitly overrides booking intent
    cancel_triggers = ["cancel", "raddh", "nahi aana", "band karo", "delete appointment"]
    if any(kw in text_lower for kw in cancel_triggers):
        return "cancel_appointment"

    scores = {}
    for intent, keywords in INTENT_PATTERNS.items():
        scores[intent] = sum(1 for kw in keywords if kw in text_lower)

    best_intent = max(scores, key=scores.get)
    # If no keyword matched, fall back to general_info
    if scores[best_intent] == 0:
        return "general_info"
    return best_intent


def extract_entities(text: str) -> dict:
    """
    Lightweight entity extraction: urgency indicators, specialty hints, conditions.
    """
    entities = {"conditions": [], "specialty_hint": None, "time_hint": None}

    condition_map = {
        "diabetes": ["sugar", "diabetes", "madhumeh"],
        "hypertension": ["bp", "blood pressure", "hypertension", "high bp"],
        "back_pain": ["back pain", "kamar dard", "peeth dard"],
        "heart": ["heart", "dil", "chest pain", "cardiac"],
        "anxiety": ["anxiety", "stress", "tension", "ghabrahat"],
        "general": []
    }
    specialty_map = {
        "Cardiology": ["heart", "dil", "chest", "cardiac"],
        "Orthopedics": ["bone", "joint", "kamar", "back", "ghutna", "knee"],
        "Neurology": ["brain", "dimag", "sir dard", "migraine", "headache"],
        "General": []
    }
    time_hints = {
        "kal": "tomorrow", "aaj": "today", "tomorrow": "tomorrow",
        "today": "today", "morning": "morning", "subah": "morning",
        "evening": "evening", "sham": "evening"
    }

    text_lower = text.lower()

    for cond, kws in condition_map.items():
        if any(kw in text_lower for kw in kws):
            entities["conditions"].append(cond)

    for spec, kws in specialty_map.items():
        if any(kw in text_lower for kw in kws):
            entities["specialty_hint"] = spec
            break
    if not entities["specialty_hint"]:
        entities["specialty_hint"] = "General"

    for hint, value in time_hints.items():
        if hint in text_lower:
            entities["time_hint"] = value
            break

    return entities


def process_nlp(text: str) -> dict:
    """Full NLP pipeline: detect language → classify intent → extract entities."""
    lang_code, lang_name = detect_language(text)
    intent = classify_intent(text)
    entities = extract_entities(text)
    return {
        "original_text": text,
        "language_code": lang_code,
        "language_name": lang_name,
        "intent": intent,
        "entities": entities,
    }
