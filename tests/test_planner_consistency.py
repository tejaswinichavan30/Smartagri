"""
Unit tests for Planner Agent cross-module consistency:
1. District & Crop synchronization (no split like Hassan weather with Chikkamagaluru prices).
2. Cross-crop leaf disease alert isolation (Corn leaf scan does not alert Finger Millet).
3. Structured selling recommendation formatting.
"""

import unittest
import os
import sys
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app, compute_price_forecast


class TestPlannerConsistency(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_compute_price_forecast_sync(self):
        p_data = compute_price_forecast("Finger Millet (Ragi)", "Hassan", 10, 2026)
        self.assertIn("Hassan", p_data['price_en'])
        self.assertIn("Finger Millet", p_data['price_en'])
        self.assertTrue(p_data['prediction'] > 0)
        self.assertTrue(len(p_data['spot_clean_en']) > 0 or "Agmarknet" in p_data['price_en'])

    def test_planner_cross_crop_disease_isolation(self):
        with self.client.session_transaction() as sess:
            sess['recommended_crop'] = 'Ragi'
            sess['city'] = 'Hassan'
            sess['selected_district'] = 'Hassan'
            # Previous scan was for Corn Maize
            sess['predicted_crop'] = 'Corn maize'
            sess['predicted_disease'] = 'Common rust'

        response = self.client.post('/planner', data={'lang': 'en'}, headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        # Moderate alert for Corn Common rust should NOT be in alerts or priority for Ragi
        alerts = data.get('alerts', [])
        priority = data.get('priority', [])
        all_warnings = " ".join(alerts + priority)
        
        self.assertNotIn("MODERATE ALERT", all_warnings, "Corn rust should not block Ragi farming")
        self.assertNotIn("CRITICAL PRIORITY", all_warnings)

        # Informational note in advice
        advice = " ".join(data.get('advice', []))
        self.assertIn("Ragi", advice)
        self.assertIn("Corn maize", advice)

    def test_planner_same_crop_disease_alert(self):
        with self.client.session_transaction() as sess:
            sess['recommended_crop'] = 'Tomato'
            sess['city'] = 'Kolar'
            sess['selected_district'] = 'Kolar'
            sess['predicted_crop'] = 'Tomato'
            sess['predicted_disease'] = 'Early blight'

        response = self.client.post('/planner', data={'lang': 'en'}, headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        priority = " ".join(data.get('priority', []))
        self.assertIn("CRITICAL PRIORITY", priority)
        self.assertIn("Tomato", priority)

    def test_planner_district_price_synchronization(self):
        with self.client.session_transaction() as sess:
            sess['recommended_crop'] = 'Ragi'
            sess['city'] = 'Hassan'
            sess['selected_district'] = 'Hassan'
            # Stale price result from another district
            sess['price_crop'] = 'Finger Millet'
            sess['price_district'] = 'Chikkamagaluru'
            sess['price_result_en'] = 'Old Chikkamagaluru forecast'

        response = self.client.post('/planner', data={'lang': 'en'}, headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        advice = " ".join(data.get('advice', []))
        self.assertIn("Hassan", advice)
        self.assertNotIn("Old Chikkamagaluru forecast", advice)


if __name__ == '__main__':
    unittest.main()
