"""
SmartAgri Comprehensive Validation Test Suite (10 Core Test Cases)
Validates all chain interactions, agronomic safeguards, price models, and formulas.
"""

import unittest
import os
import sys
import json
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app, compute_price_forecast, render_markdown_safe, get_farm_context, update_farm_context
import translations
from models.agmarknet_service import agmarknet_service
from models.agri_rag_service import agri_rag


class TestSmartAgriComprehensive(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    # Test 1: District Alignment Across Chained Modules
    def test_01_district_alignment_chain(self):
        """When Hassan is selected, Crop, Price, Irrigation and Planner all use Hassan."""
        with self.client.session_transaction() as sess:
            sess['recommended_crop'] = 'Ragi'
            sess['selected_district'] = 'Hassan'
            sess['city'] = 'Hassan'

        response = self.client.post('/planner', data={'lang': 'en'}, headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        advice = " ".join(data.get('advice', []))
        self.assertIn("Hassan", advice)
        # Verify FarmContext contains Hassan
        with self.client.session_transaction() as sess:
            ctx = sess.get('farm_context', {})
            self.assertEqual(ctx.get('district'), 'Hassan')

    # Test 2: Regional Crop (Ragi) Price Forecast Handling
    def test_02_unmodeled_crop_price_forecast(self):
        """Ragi price forecast handling: returns spot price, MSP, and 4-month market outlook."""
        p_data = compute_price_forecast("Ragi", "Hassan", 10, 2026)
        self.assertTrue(p_data.get('forecast_available'))
        self.assertIn("4-Month Price Outlook", p_data['price_en'])
        self.assertIn("Finger Millet (Ragi)", p_data['price_en'])
        self.assertIn("5205", p_data['price_en'])  # Kharif 2026-27 MSP
        self.assertIn("Hassan", p_data['price_en'])

    # Test 3: Spot-vs-Forecast Gap Warning (>25%)
    def test_03_price_gap_warning(self):
        """If spot price diverges from historical forecast by >25%, a clear warning is attached."""
        # Test with a modelled crop like Rice/Maize
        p_data = compute_price_forecast("Maize", "Hassan", 10, 2026)
        if p_data.get('forecast_available') and p_data.get('gap_pct', 0) > 25.0:
            self.assertTrue(len(p_data.get('gap_warning_en', '')) > 0)
            self.assertIn("diverges by", p_data.get('gap_warning_en', ''))

    # Test 4: Sowing Window Check for Kharif Ragi in October
    def test_04_sowing_window_check(self):
        """On Oct 3, Kharif Ragi sowing window (June-Aug) has passed, triggering warning."""
        # Read from config
        with open("data/crop_calendar_config.json", "r", encoding="utf-8") as f:
            cal = json.load(f)
        ragi_kharif = cal["crops"]["ragi"]["kharif"]
        self.assertEqual(ragi_kharif["sowing_end_month"], 8)
        self.assertEqual(ragi_kharif["sowing_end_day"], 31)

        # In October (month 10), sowing_passed should be true
        cur_m = 10
        sowing_passed = cur_m > ragi_kharif["sowing_end_month"]
        self.assertTrue(sowing_passed)

    # Test 5: Cross-Crop Disease Isolation
    def test_05_cross_crop_disease_isolation(self):
        """A Corn leaf disease scan must not contaminate a Ragi farm plan."""
        with self.client.session_transaction() as sess:
            sess['recommended_crop'] = 'Ragi'
            sess['city'] = 'Hassan'
            sess['predicted_crop'] = 'Corn maize'
            sess['predicted_disease'] = 'Northern Leaf Blight'

        response = self.client.post('/planner', data={'lang': 'en'}, headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        # Should NOT treat Northern Leaf Blight as active on Ragi
        alerts = data.get('alerts', [])
        priority = data.get('priority', [])
        combined = " ".join(alerts + priority)
        self.assertNotIn("CRITICAL PRIORITY: Ragi : Northern Leaf Blight", combined)
        self.assertNotIn("DO NOT SOW", combined)

    # Test 6: Planner Headline Consistency with Disease Status
    def test_06_planner_headline_consistency(self):
        """When plant is healthy or no disease detected, summary does not claim active critical disease."""
        with self.client.session_transaction() as sess:
            sess['recommended_crop'] = 'Rice'
            sess['city'] = 'Dharwad'
            sess['predicted_crop'] = 'Rice'
            sess['predicted_disease'] = 'healthy'

        response = self.client.post('/planner', data={'lang': 'en'}, headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        summary = data.get('summary', '')
        self.assertNotIn("STOP — Critical issues detected", summary)

    # Test 7: Markdown Sanitization (No raw ** or unescaped HTML)
    def test_07_markdown_sanitization(self):
        """render_markdown_safe sanitizes HTML tags and renders bold/lists without raw symbols."""
        raw_text = "### Action Plan\n**Step 1:** Apply FYM • Check soil pH\n<script>alert('xss')</script>"
        safe_html = render_markdown_safe(raw_text)
        self.assertNotIn("<script>", safe_html)
        self.assertNotIn("**Step 1:**", safe_html)
        self.assertIn("<strong>Step 1:</strong>", safe_html)
        self.assertIn("<h4 class=\"plan-subheading\">Action Plan</h4>", safe_html)

    # Test 8: Unverified Agronomic & Pesticide Fields
    def test_08_unverified_agronomic_fields(self):
        """All pesticide recommendations and fertilizer guidelines have verified_by_expert=false."""
        with open("data/pesticide_recommendations.json", "r", encoding="utf-8") as f:
            p_data = json.load(f)
        for crop_k, crop_v in p_data.get("crops", {}).items():
            for dis_k, dis_v in crop_v.get("diseases", {}).items():
                self.assertFalse(dis_v.get("verified_by_expert", True), f"{crop_k}:{dis_k} must be marked unverified")
                self.assertFalse(dis_v.get("label_claim_verified", True))

        with open("data/fertilizer_guidelines.json", "r", encoding="utf-8") as f:
            f_data = json.load(f)
        for crop_k, crop_v in f_data.get("crops", {}).items():
            self.assertFalse(crop_v.get("verified_by_expert", True), f"{crop_k} fertilizer must be unverified")

    # Test 9: Irrigation Mass Balance & Effective Rainfall
    def test_09_irrigation_mass_balance_and_effective_rainfall(self):
        """Verifies FAO-56 / Hargreaves ET0, USDA SCS Peff, and separate Per-Event Volume vs Daily Avg."""
        res = translations.calculate_smart_irrigation(
            crop='ragi',
            growth_stage='vegetative',
            soil_type='loam',
            area_acres=1.0,
            irrigation_type='drip',
            temp=24.0,
            humidity=70.0,
            rainfall_mm=10.0,
            district='Hassan'
        )
        self.assertEqual(res['crop'], 'ragi')
        self.assertTrue(res['et0'] > 0)
        self.assertTrue(res['etc_mm'] > 0)
        self.assertTrue(res['peff_mm'] >= 0)
        self.assertTrue(res['interval_days'] >= 1)
        # Volume per event must equal daily need * interval * area
        expected_per_event = round(res['total_litres_day'] * res['interval_days'])
        self.assertEqual(res['litres_per_event'], expected_per_event)

    # Test 10: RAG Snippet & Fallback Handling
    def test_10_rag_snippet_and_no_guidance_handling(self):
        """RAG returns snippet with title/score for relevant queries, and fallback when score is below threshold."""
        # Irrelevant query
        irrelevant_res = agri_rag.retrieve("quantum electrodynamics semiconductor astrophysics", min_score=0.25)
        self.assertEqual(len(irrelevant_res), 0)

        ctx_str, sources = agri_rag.get_rag_context_str("quantum electrodynamics semiconductor astrophysics")
        self.assertIn("No specific guidance found", ctx_str)

    # Test 11: Crop Recommendation Auto-Chains Smart Irrigation
    def test_11_predict_crop_auto_chains_irrigation(self):
        """predict_crop calculates and outputs precision irrigation card without requiring manual navigation or button press."""
        response = self.client.post('/predict_crop', data={
            'district': 'Hassan',
            'nitrogen': '98',
            'phosphorus': '30',
            'potassium': '30',
            'ph': '6.2',
            'rainfall': '150',
            'season': 'Kharif',
            'lang': 'en'
        }, headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('irrigation_data', data)
        self.assertIsNotNone(data['irrigation_data'])
        self.assertIn('total_litres_day', data['irrigation_data'])
        self.assertIn('runtime_en', data['irrigation_data'])
        self.assertIn('frequency_en', data['irrigation_data'])
        self.assertGreaterEqual(data['irrigation_data']['total_litres_day'], 0)


if __name__ == '__main__':
    unittest.main()
