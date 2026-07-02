"""
Enhanced NLP Service — Phase 3.
Adds semantic similarity using sentence-transformers (multilingual-MiniLM-L6-v2).
Falls back to keyword matching if transformers not installed.
"""
import os
from typing import List, Tuple

# ── Intent labels and their semantic descriptions ────────────────────────────
INTENT_DESCRIPTIONS = {
    "book_appointment":   "I want to schedule or book a doctor appointment",
    "cancel_appointment": "I want to cancel or delete my appointment",
    "diet_plan":          "I need a diet or food plan for my health condition",
    "yoga":               "I want yoga exercises or poses for my condition",
    "meditation":         "I want meditation or breathing exercises for stress",
    "general_info":       "I have a general health question",
}


def get_semantic_intent(text: str) -> Tuple[str, float]:
    """
    Use sentence-transformers to compute cosine similarity between
    input text and each intent description.
    Returns (intent, confidence_score).
    Falls back to keyword rules if model not available.
    """
    try:
        from sentence_transformers import SentenceTransformer, util
        import torch

        model_name = os.getenv("ST_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
        # Cache model at module level to avoid reloading
        if not hasattr(get_semantic_intent, "_model"):
            get_semantic_intent._model = SentenceTransformer(model_name)

        model = get_semantic_intent._model
        descriptions = list(INTENT_DESCRIPTIONS.values())
        intent_keys = list(INTENT_DESCRIPTIONS.keys())

        # Encode query and descriptions
        query_emb = model.encode(text, convert_to_tensor=True)
        desc_emb = model.encode(descriptions, convert_to_tensor=True)

        # Cosine similarity
        scores = util.cos_sim(query_emb, desc_emb)[0].tolist()
        best_idx = scores.index(max(scores))
        return intent_keys[best_idx], round(max(scores), 4)

    except ImportError:
        return None, 0.0  # signal to fall back to keyword matching


def get_semantic_language_hint(text: str) -> str:
    """
    Lightweight Hindi script detector (no external library needed).
    Returns 'hi' if Hindi Unicode chars found, 'en' otherwise.
    """
    hindi_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    # Hinglish detection: mostly Latin but has Hindi keywords
    hinglish_keywords = ["hai", "mujhe", "karo", "chahiye", "milna", "dard", "bahut", "kal", "subah"]
    text_lower = text.lower()
    hinglish_hits = sum(1 for kw in hinglish_keywords if kw in text_lower)

    if hindi_chars > 2:
        return "hi"
    elif hinglish_hits >= 2:
        return "hi"  # Hinglish → treat as Hindi
    return "en"
