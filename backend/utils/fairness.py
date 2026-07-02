"""
Fairness utilities for the Scheduling Engine.
MVP: Track wait times and compute fairness score.
"""
from typing import List
from statistics import mean, stdev


def compute_fairness_score(wait_times: List[float]) -> float:
    """
    Compute a fairness score (0-1) based on Jain's Fairness Index.
    Higher = fairer distribution of wait times.
    """
    if not wait_times or len(wait_times) == 0:
        return 1.0
    n = len(wait_times)
    sum_xi = sum(wait_times)
    sum_xi_sq = sum(x ** 2 for x in wait_times)
    if sum_xi_sq == 0:
        return 1.0
    return (sum_xi ** 2) / (n * sum_xi_sq)


def compute_urgency_score(text: str, keywords: List[str] = None) -> int:
    """
    Rule-based urgency scoring from 1 (low) to 5 (critical).
    Checks for urgency keywords in patient's input text.
    """
    critical_words = ["emergency", "chest pain", "stroke", "unconscious", "bleeding",
                      "aatank", "dil dard", "behoshi", "khoon", "seene mein dard"]
    high_words = ["urgent", "severe", "bahut dard", "bahut tez", "heart", "breathing"]
    medium_words = ["pain", "dard", "fever", "bukhar", "vomiting", "ulti", "headache"]

    text_lower = text.lower()
    all_keywords = (keywords or []) + []

    for word in critical_words:
        if word in text_lower:
            return 5
    for word in high_words:
        if word in text_lower:
            return 4
    for word in medium_words:
        if word in text_lower:
            return 3
    return 1
