# -*- coding: utf-8 -*-
"""
Unit tests for "Ask My Farm" Visual Multi-Agent Copilot Engine & API Endpoint.
"""

import os
import sys
import unittest
import json
import io

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from models.agri_visual_copilot import (
    visual_copilot_engine,
    VisionPerceptionAgent,
    SoilAgent,
    WeatherAgent,
    IrrigationAgent,
    CropDiseaseRAGAgent,
    MultimodalReasoningAgent
)
from app import app


class TestAskMyFarmVisualCopilot(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.vision = VisionPerceptionAgent()
        self.soil = SoilAgent()
        self.weather = WeatherAgent()
        self.irrigation = IrrigationAgent()
        self.reasoning = MultimodalReasoningAgent()

    def test_vision_perception_pest(self):
        res = self.vision.analyze_image(
            crop_hint="Maize",
            farmer_query="Is this caterpillar pest destroying my leaves?"
        )
        self.assertEqual(res.get("primary_entity"), "pest")
        self.assertTrue(len(res.get("detected_objects", [])) > 0)
        self.assertIn("caterpillar", res["detected_objects"][0]["label"])

    def test_vision_perception_irrigation_leak(self):
        res = self.vision.analyze_image(
            crop_hint="Tomato",
            farmer_query="Why is there water pooling near the drip pipe joint?"
        )
        self.assertEqual(res.get("primary_entity"), "irrigation_hardware")
        self.assertEqual(res.get("soil_surface_visual"), "waterlogged")

    def test_differential_diagnosis_water_stress_grounding(self):
        """
        Critical Test: Ensure wilting leaves + dry soil telemetry is diagnosed
        as Abiotic Water Stress and NOT mistakenly classified as a fungal pathogen.
        """
        res = visual_copilot_engine.run_ask_my_farm(
            farmer_query="Why are my tomato leaves yellowing and wilting?",
            crop_hint="Tomato",
            district="Davanagere",
            sensor_override={"moisture": 16.5, "days_since_last_irrigation": 4},
            lang="en"
        )
        diag = res.get("diagnosis", {})
        self.assertIn("Water", diag.get("root_cause", ""))
        self.assertTrue("fungicide" not in diag.get("differential_rationale", "").lower() or "not required" in diag.get("differential_rationale", "").lower())
        self.assertTrue(len(diag.get("action_steps", [])) >= 3)

    def test_differential_diagnosis_kannada_synthesis(self):
        res = visual_copilot_engine.run_ask_my_farm(
            farmer_query="ನನ್ನ ಗಿಡದ ಎಲೆಗಳು ಯಾಕೆ ಹಳದಿಯಾಗಿ ಬಾಡುತ್ತಿವೆ?",
            crop_hint="Tomato",
            district="Davanagere",
            sensor_override={"moisture": 17.0, "days_since_last_irrigation": 4},
            lang="kn"
        )
        diag = res.get("diagnosis", {})
        audio_kn = diag.get("audio_summary", "")
        self.assertTrue(len(audio_kn) > 50)
        self.assertTrue("ನೀರಿನ" in audio_kn or "ಗಿಡ" in audio_kn or "ತೇವಾಂಶ" in audio_kn)

    def test_differential_diagnosis_hindi_synthesis(self):
        res = visual_copilot_engine.run_ask_my_farm(
            farmer_query="इस पौधे की पत्तियां पीली क्यों हैं?",
            crop_hint="Tomato",
            district="Davanagere",
            sensor_override={"moisture": 18.0, "days_since_last_irrigation": 4},
            lang="hi"
        )
        diag = res.get("diagnosis", {})
        audio_hi = diag.get("audio_summary", "")
        self.assertTrue(len(audio_hi) > 50)
        self.assertTrue("पानी" in audio_hi or "फसल" in audio_hi or "नमी" in audio_hi)

    def test_api_ask_my_farm_json_endpoint(self):
        response = self.app.post(
            "/api/ask_my_farm",
            json={
                "query": "Why are leaves drooping?",
                "crop": "Tomato",
                "district": "Davanagere",
                "lang": "en",
                "sensor_data": {"moisture": 19.0, "days_since_last_irrigation": 3}
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "success")
        self.assertIn("vision_analysis", data)
        self.assertIn("agent_telemetry", data)
        self.assertIn("diagnosis", data)
        self.assertTrue(len(data["agents_consulted"]) >= 5)

    def test_api_ask_my_farm_multipart_form_endpoint(self):
        dummy_file = (io.BytesIO(b"mock_image_bytes"), "test_leaf.jpg")
        response = self.app.post(
            "/api/ask_my_farm",
            data={
                "query": "Is this caterpillar harmful?",
                "crop": "Maize",
                "district": "Haveri",
                "lang": "en",
                "image": dummy_file
            },
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "success")
        self.assertIn("Pest", data["diagnosis"]["root_cause"])


if __name__ == "__main__":
    unittest.main()
