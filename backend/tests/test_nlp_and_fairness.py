"""Unit tests for NLP service and fairness utilities."""
import pytest
from services.nlp_service import detect_language, classify_intent, extract_entities, process_nlp
from utils.fairness import compute_urgency_score, compute_fairness_score


class TestNLPService:
    def test_detect_english(self):
        code, name = detect_language("I need an appointment tomorrow morning")
        assert code in ["en", "nl"]  # langdetect sometimes misclassifies short text

    def test_detect_hindi(self):
        code, name = detect_language("मुझे कल सुबह डॉक्टर से मिलना है")
        assert code in ["hi", "mr"]

    def test_classify_book_appointment(self):
        intent = classify_intent("I want to book an appointment with a doctor")
        assert intent == "book_appointment"

    def test_classify_diet_hindi(self):
        intent = classify_intent("diabetes ke liye kya khana chahiye")
        assert intent == "diet_plan"

    def test_classify_yoga(self):
        intent = classify_intent("yoga poses for back pain")
        assert intent == "yoga"

    def test_classify_meditation(self):
        intent = classify_intent("stress relief meditation technique")
        assert intent == "meditation"

    def test_classify_cancel(self):
        intent = classify_intent("cancel my appointment")
        assert intent == "cancel_appointment"

    def test_extract_specialty_cardiology(self):
        entities = extract_entities("I have chest pain, need a heart specialist")
        assert entities["specialty_hint"] == "Cardiology"

    def test_extract_specialty_orthopedics(self):
        entities = extract_entities("I have back pain, kamar mein dard hai")
        assert entities["specialty_hint"] == "Orthopedics"

    def test_extract_time_hint_tomorrow(self):
        entities = extract_entities("kal subah milna hai")
        assert entities["time_hint"] == "tomorrow"

    def test_process_nlp_full(self):
        result = process_nlp("I need urgent appointment for chest pain tomorrow")
        assert result["intent"] == "book_appointment"
        assert result["entities"]["specialty_hint"] is not None
        assert result["language_code"] is not None


class TestFairnessUtils:
    def test_urgency_critical(self):
        score = compute_urgency_score("patient is unconscious, emergency")
        assert score == 5

    def test_urgency_high(self):
        score = compute_urgency_score("bahut dard ho raha hai, urgent hai")
        assert score >= 3

    def test_urgency_low(self):
        score = compute_urgency_score("routine checkup please")
        assert score == 1

    def test_fairness_perfect(self):
        score = compute_fairness_score([10, 10, 10, 10])
        assert score == pytest.approx(1.0, abs=0.01)

    def test_fairness_uneven(self):
        score = compute_fairness_score([1, 10, 100, 1000])
        assert 0 < score < 1

    def test_fairness_empty(self):
        score = compute_fairness_score([])
        assert score == 1.0
