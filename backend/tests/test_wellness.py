"""Unit tests for Wellness service — diet, yoga, meditation."""
import pytest
from services.wellness_service import get_diet_plan, get_yoga_recommendations, get_meditation_plan


class TestDietPlanner:
    def test_diabetes_has_7_days(self):
        plan = get_diet_plan("diabetes")
        assert len(plan["plan"]) == 7

    def test_hypertension_plan(self):
        plan = get_diet_plan("hypertension")
        assert "avoid" in plan
        assert len(plan["avoid"]) > 0

    def test_unknown_condition_defaults_to_general(self):
        plan = get_diet_plan("xyz_unknown")
        assert plan["plan"] is not None

    def test_all_days_have_meals(self):
        plan = get_diet_plan("diabetes")
        for day, meals in plan["plan"].items():
            assert "breakfast" in meals
            assert "lunch" in meals
            assert "dinner" in meals
            assert "snacks" in meals

    def test_disclaimer_present(self):
        plan = get_diet_plan("general")
        assert "disclaimer" in plan
        assert len(plan["disclaimer"]) > 0


class TestYogaRecommender:
    def test_back_pain_has_poses(self):
        recs = get_yoga_recommendations("back_pain")
        assert len(recs["recommended_poses"]) > 0

    def test_back_pain_has_avoid(self):
        recs = get_yoga_recommendations("back_pain")
        assert len(recs["avoid_poses"]) > 0

    def test_severe_falls_back_to_general(self):
        recs = get_yoga_recommendations("back_pain", "severe")
        assert recs["recommended_poses"] is not None

    def test_unknown_condition_defaults_to_general(self):
        recs = get_yoga_recommendations("unknown")
        assert "recommended_poses" in recs


class TestMeditationSystem:
    def test_stress_plan(self):
        plan = get_meditation_plan("stress")
        assert plan["technique"] is not None
        assert len(plan["daily_steps"]) > 0

    def test_sleep_plan(self):
        plan = get_meditation_plan("sleep")
        assert "daily_steps" in plan
        assert len(plan["daily_steps"]) >= 3

    def test_feedback_adaptation(self):
        plan = get_meditation_plan("stress", feedback="too long")
        assert plan["adapted_from_feedback"] is True

    def test_unknown_goal_defaults_to_general(self):
        plan = get_meditation_plan("unknown")
        assert "technique" in plan
