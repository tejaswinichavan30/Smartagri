"""
Unit tests for SmartAgri Planner Agent LLM & RAG 360 Action Plan Integration.
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from models.agri_llm_service import agri_llm
from app import app


class TestPlannerAgentAi(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_planner_strategy_kannada(self):
        res = agri_llm.generate_planner_agent_strategy(
            crop="ಮೆಕ್ಕೆಜೋಳ",
            disease="ಇಬ್ಬನಿ ರೋಗ / Blight",
            price="₹ 2450",
            district="Davanagere",
            lang="kn"
        )
        plan = res.get("ai_plan", "")
        print("\n--- 1. Planner AI Kannada Strategy Length:", len(plan))
        self.assertTrue(len(plan) > 200, "Plan should be comprehensive")
        self.assertTrue("ಯೋಜನೆ" in plan or "ಮೆಕ್ಕೆಜೋಳ" in plan or "ಕೃಷಿ" in plan)
        self.assertTrue("Davanagere" in plan or "ದಾವಣಗೆರೆ" in plan or "ಜಿಲ್ಲೆ" in plan)

    def test_planner_strategy_hindi(self):
        res = agri_llm.generate_planner_agent_strategy(
            crop="धान",
            disease="झुलसा रोग / Blight",
            price="₹ 3200",
            district="Raichur",
            lang="hi"
        )
        plan = res.get("ai_plan", "")
        print("\n--- 2. Planner AI Hindi Strategy Length:", len(plan))
        self.assertTrue(len(plan) > 200, "Plan should be comprehensive")
        self.assertTrue("कार्य योजना" in plan or "धान" in plan or "कृषि" in plan)
        self.assertTrue("Raichur" in plan or "रायचूर" in plan or "जिला" in plan)

    def test_planner_strategy_english(self):
        res = agri_llm.generate_planner_agent_strategy(
            crop="Cotton",
            disease="None detected",
            price="₹ 6800",
            district="Ballari",
            lang="en"
        )
        plan = res.get("ai_plan", "")
        print("\n--- 3. Planner AI English Strategy Length:", len(plan))
        self.assertTrue(len(plan) > 200, "Plan should be comprehensive")
        self.assertTrue("Plan" in plan or "Cotton" in plan or "Action" in plan)

    def test_api_planner_ai_endpoint(self):
        response = self.app.post(
            "/api/planner_ai",
            json={
                "crop": "Maize",
                "disease": "Leaf Blight",
                "price": "2400",
                "district": "Haveri",
                "lang": "en"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("ai_plan", data)
        self.assertTrue(len(data["ai_plan"]) > 150)
        print("\n--- 4. /api/planner_ai endpoint test passed successfully!")


if __name__ == "__main__":
    unittest.main()
