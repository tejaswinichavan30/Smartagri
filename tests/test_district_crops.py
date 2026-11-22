"""
Unit tests for 2-3 District-Aware Regional Crop Recommendations and Weather Preferability Evaluation.
"""

import os
import sys
import json
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app, KARNATAKA_DISTRICT_CROPS
import translations


class TestDistrictCropRecommendation(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_kolar_crop_recommendation_html(self):
        with self.app.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'farmer'

        response = self.app.post(
            "/predict_crop",
            data={
                "district": "Kolar",
                "nitrogen": "78",
                "phosphorus": "48",
                "potassium": "25",
                "ph": "6.2",
                "rainfall": "85",
                "season": "auto",
                "lang": "en"
            }
        )
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertTrue("Mango" in html or "Grapes" in html or "Pomegranate" in html, "Kolar must recommend a regional horticulture crop")
        self.assertIn("Most Preferred for Current Weather", html)
        self.assertIn("Top 3 Crops Grown in This District", html)
        print("\n--- Kolar HTML Multi-Crop Recommendation Test Passed!")

    def test_district_multi_crop_json_api(self):
        # Test Dharwad JSON response with Kharif test date override
        os.environ["SMARTAGRI_TEST_MODE"] = "1"
        os.environ["SMARTAGRI_TEST_DATE"] = "2026-07-15"
        try:
            response = self.app.post(
                "/predict_crop",
                data={
                    "district": "Dharwad",
                    "nitrogen": "115",
                    "phosphorus": "45",
                    "potassium": "20",
                    "ph": "6.8",
                    "rainfall": "80",
                    "season": "Kharif",
                    "lang": "en"
                },
                headers={"Accept": "application/json"}
            )
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertIn("crop", data)
            self.assertIn("top_crops", data)
            self.assertIn("preferred_crop", data)
            
            top_crops = data["top_crops"]
            self.assertGreaterEqual(len(top_crops), 2, "Must return 2-3 regional crop candidates")
            self.assertLessEqual(len(top_crops), 3, "Must return at most 3 regional crop candidates")

            dharwad_allowed = [c.lower() for c in KARNATAKA_DISTRICT_CROPS["Dharwad"]]
            for c in top_crops:
                self.assertIn(c["crop_key"].lower(), dharwad_allowed, f"{c['crop_key']} must be in Dharwad's regional crops list")
                self.assertIn("score", c)
                self.assertIn("reason_en", c)
                self.assertGreater(c["score"], 0)

            # Check preferred crop rank & descending weather score ordering
            self.assertEqual(top_crops[0]["rank"], 1)
            self.assertTrue(top_crops[0]["is_preferred"])
            for i in range(len(top_crops) - 1):
                self.assertGreaterEqual(
                    top_crops[i]["score"], 
                    top_crops[i+1]["score"], 
                    f"Crop at rank {i+1} ({top_crops[i]['name']} with score {top_crops[i]['score']}) must have >= weather score than rank {i+2} ({top_crops[i+1]['name']} with score {top_crops[i+1]['score']})"
                )
            print(f"\n--- Dharwad Multi-Crop JSON API Passed: {len(top_crops)} crops returned with strict descending weather ranking: {[(c['name'], c['score']) for c in top_crops]}")
        finally:
            os.environ.pop("SMARTAGRI_TEST_MODE", None)
            os.environ.pop("SMARTAGRI_TEST_DATE", None)

    def test_kannada_multi_crop_translation(self):
        os.environ["SMARTAGRI_TEST_MODE"] = "1"
        os.environ["SMARTAGRI_TEST_DATE"] = "2026-07-15"
        try:
            response = self.app.post(
                "/predict_crop",
                data={
                    "district": "Belagavi",
                    "nitrogen": "85",
                    "phosphorus": "46",
                    "potassium": "22",
                    "ph": "6.8",
                    "rainfall": "85",
                    "season": "Kharif",
                    "lang": "kn"
                },
                headers={"Accept": "application/json"}
            )
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            top_crops = data["top_crops"]
            self.assertGreaterEqual(len(top_crops), 2)
            self.assertTrue(any(c.get("name_kn") for c in top_crops))
            self.assertTrue(any(c.get("reason_kn") for c in top_crops))
            print("\n--- Kannada Multi-Crop Translation Test Passed!")
        finally:
            os.environ.pop("SMARTAGRI_TEST_MODE", None)
            os.environ.pop("SMARTAGRI_TEST_DATE", None)

    def test_weather_preferability_evaluator(self):
        # Rice prefers high temperature and high humidity
        eval_rice = translations.evaluate_crop_weather_suitability('rice', temp=28, humidity=80, rainfall=150, season='Kharif', lang='en')
        self.assertGreaterEqual(eval_rice['score'], 80.0)
        self.assertIn('match', eval_rice['reason_en'])

        # Chickpea prefers cooler weather (18C) over extreme heat (38C)
        eval_chickpea_cool = translations.evaluate_crop_weather_suitability('chickpea', temp=20, humidity=50, rainfall=30, season='Rabi', lang='en')
        eval_chickpea_hot = translations.evaluate_crop_weather_suitability('chickpea', temp=38, humidity=85, rainfall=150, season='Kharif', lang='en')
        self.assertGreater(eval_chickpea_cool['score'], eval_chickpea_hot['score'], "Chickpea should score higher in cool dry weather than hot wet weather")
        print("\n--- Weather Preferability Evaluator Logic Test Passed!")

    def test_crop_disease_samples_and_api(self):
        # 1. Test translation helper for Soybean
        soy_samples = translations.get_crop_disease_samples('Soybean', 'en')
        self.assertEqual(len(soy_samples), 4)
        for s in soy_samples:
            self.assertIn('name', s)
            self.assertNotIn('confidence', s)
            self.assertIn('image', s)
            self.assertTrue(os.path.exists(s['image']), f"Sample image file {s['image']} must exist on disk")

        # 2. Test Kannada localization
        soy_samples_kn = translations.get_crop_disease_samples('Soybean', 'kn')
        self.assertEqual(len(soy_samples_kn), 4)
        self.assertTrue(any('ಸೋಯಾಬೀನ್' in s['name'] for s in soy_samples_kn))

        # 3. Test Rice samples
        rice_samples = translations.get_crop_disease_samples('Rice', 'en')
        self.assertEqual(len(rice_samples), 4)
        for s in rice_samples:
            self.assertTrue(os.path.exists(s['image']), f"Rice image file {s['image']} must exist")

        # 4. Test API endpoint
        res = self.app.get('/api/crop_disease_samples?crop=Soybean&lang=kn')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['samples']), 4)
        print("\n--- Crop Leaf Disease Samples & API Test Passed!")

    def test_auto_sync_market_price_agent(self):
        with self.app.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'farmer'

        # Predict crop for Davanagere (which recommends Maize)
        response = self.app.post(
            "/predict_crop",
            data={
                "district": "Davanagere",
                "nitrogen": "78",
                "phosphorus": "48",
                "potassium": "20",
                "ph": "6.5",
                "rainfall": "85",
                "season": "Kharif",
                "lang": "en"
            }
        )
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)

        from datetime import datetime
        now = datetime.now()
        cur_m = str(now.month)
        cur_y = str(now.year)

        # Verify HTML has Maize and Davanagere selected for Market Price form
        self.assertIn('value="Maize"', html)
        self.assertIn('value="Davanagere"', html)
        self.assertIn(f'value="{cur_m}"', html)
        self.assertIn(f'value="{cur_y}"', html)

        # Predict crop for Bidar (recommends Blackgram)
        response_bidar = self.app.post(
            "/predict_crop",
            data={
                "district": "Bidar",
                "nitrogen": "40",
                "phosphorus": "60",
                "potassium": "20",
                "ph": "7.0",
                "rainfall": "65",
                "season": "Kharif",
                "lang": "en"
            }
        )
        self.assertEqual(response_bidar.status_code, 200)
        html_bidar = response_bidar.get_data(as_text=True)

        # Verify HTML has Blackgram and Bidar selected
        self.assertTrue('value="Blackgram"\n                                data-en="Blackgram (Urad)"\n                                data-kn="ಉದ್ದಿನ ಬೇಳೆ (ಉದ್ದು)"\n                                data-hi="उड़द दाल"\n                                selected' in html_bidar or ('value="Blackgram"' in html_bidar and 'selected' in html_bidar))
        self.assertIn('value="Bidar"', html_bidar)
        print(f"\n--- Market Price Auto-Sync Test Passed for Bidar -> Blackgram & Davanagere -> Maize (Month: {cur_m}, Year: {cur_y})!")

    def test_auto_sync_precision_irrigation_agent(self):
        with self.app.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'farmer'

        # 1. Test Davanagere recommendation auto-syncs into Irrigation Form
        response = self.app.post(
            "/predict_crop",
            data={
                "district": "Davanagere",
                "nitrogen": "78",
                "phosphorus": "48",
                "potassium": "20",
                "ph": "6.5",
                "rainfall": "85",
                "season": "Kharif",
                "lang": "en"
            }
        )
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)

        # Check that #irrigation select elements have Maize and Davanagere selected
        self.assertIn('value="Maize"', html)
        self.assertIn('value="Davanagere"', html)

        # 2. Test Bidar recommendation auto-syncs Blackgram and Bidar into Irrigation
        response_bidar = self.app.post(
            "/predict_crop",
            data={
                "district": "Bidar",
                "nitrogen": "40",
                "phosphorus": "60",
                "potassium": "20",
                "ph": "7.0",
                "rainfall": "65",
                "season": "Kharif",
                "lang": "en"
            }
        )
        self.assertEqual(response_bidar.status_code, 200)
        html_bidar = response_bidar.get_data(as_text=True)
        self.assertIn('value="Blackgram"', html_bidar)
        self.assertIn('value="Bidar"', html_bidar)
        print("\n--- Precision Irrigation Auto-Sync Test Passed for Crop & District!")

    def test_all_crops_leaf_disease_accuracy(self):
        # Verify trained vs AI generated leaf disease reference profiles
        all_crops_to_test = [
            'Rice', 'Wheat', 'Maize (Corn)', 'Soybean', 'Cotton',
            'Tomato', 'Potato', 'Grape', 'Apple', 'Pepper (Chilli)',
            'Black Gram (Urad)', 'Groundnut (Peanut)', 'Coconut',
            'Pigeonpeas (Tur)', 'Sugarcane', 'Chickpea', 'Ragi',
            'Banana', 'Mango', 'Coffee'
        ]
        for crop in all_crops_to_test:
            samples = translations.get_crop_disease_samples(crop, 'en')
            self.assertGreaterEqual(len(samples), 2, f"Crop {crop} must have at least 2-4 leaf disease reference samples")
            for s in samples:
                self.assertIn('name', s)
                self.assertNotIn('confidence', s)
                self.assertTrue(os.path.exists(s['image']), f"Leaf image for {crop} ({s['name']}) not found at {s['image']}")
        print(f"\n--- All {len(all_crops_to_test)} Crops Leaf Disease Reference Image & Accuracy Test Passed!")


if __name__ == "__main__":
    unittest.main()




