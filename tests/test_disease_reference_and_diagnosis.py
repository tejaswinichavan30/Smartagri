"""
Tests for SmartAgri Common Diseases Reference Panel and Leaf Disease Detection
Covers the 5 core requirements specified in the user prompt:
1. chilli and black pepper never resolve to bell pepper
2. Orange and Squash never return "Healthy" (disease_only status)
3. A photo of another crop (e.g. potato with Tomato selected) is refused due to crop mismatch
4. An unknown crop name falls back to reference-only without errors
5. The notice and coverage line never contradict each other for every crop in config
"""

import os
import unittest
import numpy as np
from PIL import Image

import translations
import app


class TestDiseaseReferenceAndDiagnosis(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.app.testing = True
        cls.client = app.app.test_client()
        app.get_general_disease_model()

        # Create dummy test image in static/uploads
        os.makedirs("static/uploads", exist_ok=True)
        cls.test_img_path = "static/uploads/test_leaf_sample.jpg"
        img = Image.new("RGB", (224, 224), color=(34, 139, 34))
        img.save(cls.test_img_path)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_img_path):
            try:
                os.remove(cls.test_img_path)
            except Exception:
                pass

    def test_1_chilli_and_black_pepper_never_resolve_to_bell_pepper(self):
        """Test that chilli and black pepper are strictly reference_only and never alias to bell pepper."""
        # Check alias normalization
        self.assertNotEqual(translations.normalize_disease_crop('chilli'), 'pepper')
        self.assertNotEqual(translations.normalize_disease_crop('chilli'), 'pepper bell')
        self.assertEqual(translations.normalize_disease_crop('chilli'), 'chilli')

        self.assertNotEqual(translations.normalize_disease_crop('black pepper'), 'pepper')
        self.assertEqual(translations.normalize_disease_crop('black pepper'), 'black pepper')

        # Check bell pepper aliases
        self.assertEqual(translations.normalize_disease_crop('pepper bell'), 'pepper')
        self.assertEqual(translations.normalize_disease_crop('bell pepper'), 'pepper')
        self.assertEqual(translations.normalize_disease_crop('capsicum'), 'pepper')

        # Check support status
        support_chilli = translations.get_crop_support('chilli')
        self.assertEqual(support_chilli['status'], 'reference_only')
        self.assertFalse(translations.is_disease_diagnosis_supported('chilli'))

        support_black_pepper = translations.get_crop_support('black pepper')
        self.assertEqual(support_black_pepper['status'], 'reference_only')
        self.assertFalse(translations.is_disease_diagnosis_supported('black pepper'))

        support_pepper = translations.get_crop_support('pepper')
        self.assertEqual(support_pepper['status'], 'full')
        self.assertTrue(translations.is_disease_diagnosis_supported('pepper'))

    def test_2_orange_and_squash_never_return_healthy(self):
        """Test that Orange and Squash have 'disease_only' status and never return 'Healthy'."""
        support_orange = translations.get_crop_support('orange')
        self.assertEqual(support_orange['status'], 'disease_only')
        self.assertTrue(support_orange['karnataka'], "Orange (Coorg mandarin) must have karnataka=True")

        support_squash = translations.get_crop_support('squash')
        self.assertEqual(support_squash['status'], 'disease_only')

        # Test prediction logic for Orange
        # Case A: High probability of Huanglongbing -> Suspected
        dummy_high_orange_preds = np.zeros((1, len(app.general_disease_classes)), dtype=np.float32)
        orange_hlb_idx = app.general_disease_classes.index('Orange - Haunglongbing (Citrus greening)')
        dummy_high_orange_preds[0, orange_hlb_idx] = 0.95
        
        orig_predict = app.general_disease_model.predict
        try:
            app.general_disease_model.predict = lambda x, **kwargs: dummy_high_orange_preds
            res_crop, res_disease, conf = app.predict_leaf_disease(self.test_img_path, 'orange')
            self.assertEqual(res_crop, 'Orange')
            self.assertEqual(res_disease, 'Huanglongbing (Citrus Greening)')
            self.assertGreaterEqual(conf, 70.0)

            # Route test
            with open(self.test_img_path, 'rb') as f:
                resp = self.client.post('/predict_disease', data={
                    'image': (f, 'test.jpg'),
                    'crop_type': 'orange',
                    'lang': 'en'
                }, headers={'Accept': 'application/json'})
                data = resp.get_json()
                self.assertEqual(data['status'], 'success')
                self.assertIn("horticulture department", data['result'])
                self.assertNotIn("Healthy", data['result'])

            # Case B: Low probability on Orange disease (< 0.70) but crop match >= 0.60 -> Disease Not Detected
            dummy_low_orange_preds = np.zeros((1, len(app.general_disease_classes)), dtype=np.float32)
            dummy_low_orange_preds[0, orange_hlb_idx] = 0.62  # >= 0.60 crop total, but < 0.70 threshold
            app.general_disease_model.predict = lambda x, **kwargs: dummy_low_orange_preds

            res_crop, res_disease, conf = app.predict_leaf_disease(self.test_img_path, 'orange')
            self.assertEqual(res_crop, 'Orange')
            self.assertEqual(res_disease, 'DiseaseNotDetected')

            with open(self.test_img_path, 'rb') as f:
                resp = self.client.post('/predict_disease', data={
                    'image': (f, 'test.jpg'),
                    'crop_type': 'orange',
                    'lang': 'en'
                }, headers={'Accept': 'application/json'})
                data = resp.get_json()
                self.assertEqual(data['status'], 'success')
                self.assertIn("not detected. This does not mean the plant is healthy", data['result'])
                self.assertIn("horticulture department", data['result'])
                self.assertNotIn("Healthy", data['result'])

            # Case C: Squash Powdery mildew
            dummy_high_squash = np.zeros((1, len(app.general_disease_classes)), dtype=np.float32)
            squash_idx = app.general_disease_classes.index('Squash - Powdery mildew')
            dummy_high_squash[0, squash_idx] = 0.90
            app.disease_model = app.general_disease_model
            app.general_disease_model.predict = lambda x, **kwargs: dummy_high_squash

            with open(self.test_img_path, 'rb') as f:
                resp = self.client.post('/predict_disease', data={
                    'image': (f, 'test.jpg'),
                    'crop_type': 'squash',
                    'lang': 'en'
                }, headers={'Accept': 'application/json'})
                data = resp.get_json()
                self.assertEqual(data['status'], 'success')
                self.assertIn("confirm with an expert", data['result'])
                self.assertNotIn("Healthy", data['result'])

        finally:
            app.general_disease_model.predict = orig_predict

    def test_3_potato_photo_with_tomato_selected_refused(self):
        """Test that a photo of potato with tomato selected is refused due to crop mismatch."""
        # Simulated prediction: high probability on Potato - Early blight (0.95), 0.05 on Tomato
        dummy_potato_preds = np.zeros((1, len(app.general_disease_classes)), dtype=np.float32)
        potato_idx = app.general_disease_classes.index('Potato - Early blight')
        dummy_potato_preds[0, potato_idx] = 0.95
        # 0.05 split elsewhere

        orig_predict = app.general_disease_model.predict
        try:
            app.general_disease_model.predict = lambda x, **kwargs: dummy_potato_preds
            # Select Tomato as crop_type
            res_crop, res_disease, conf = app.predict_leaf_disease(self.test_img_path, 'tomato')
            self.assertEqual(res_crop, 'CropMismatch')
            self.assertEqual(conf, 0.0)

            # Test route response
            with open(self.test_img_path, 'rb') as f:
                resp = self.client.post('/predict_disease', data={
                    'image': (f, 'test.jpg'),
                    'crop_type': 'tomato',
                    'lang': 'en'
                }, headers={'Accept': 'application/json'})
                data = resp.get_json()
                self.assertEqual(data['status'], 'crop_mismatch')
                self.assertIn("doesn't look like a Tomato leaf", data['result'])
                self.assertIn("Please upload a clearer photo", data['result'])
        finally:
            app.general_disease_model.predict = orig_predict

    def test_4_unknown_crop_name_fallback_to_reference_only(self):
        """Test that unknown crops fall back safely to reference_only without throwing errors."""
        unknown_crops = [
            'dragonfruit', 'quinoa', 'avocado', 'unknown_random_crop_123',
            'jowar', 'sunflower', 'arecanut', 'turmeric', 'cashew',
            'mulberry', 'green gram', 'horse gram', 'tobacco', 'ginger'
        ]
        for crop in unknown_crops:
            support = translations.get_crop_support(crop)
            self.assertIsNotNone(support, f"Failed for {crop}")
            self.assertEqual(support['status'], 'reference_only', f"Expected reference_only for {crop}")
            self.assertFalse(translations.is_disease_diagnosis_supported(crop))
            
            notice = translations.get_crop_support_notice(crop, 'en')
            self.assertIn("not available", notice)

            # Test API endpoint
            resp = self.client.get(f'/api/crop_disease_samples?crop={crop}&lang=en')
            self.assertEqual(resp.status_code, 200, f"API error for crop {crop}")
            data = resp.get_json()
            self.assertIn('samples', data)
            self.assertIn('notice', data)

    def test_5_notice_and_coverage_line_never_contradict(self):
        """Test that for every crop in DISEASE_COVERAGE, the notice and the coverage line never contradict each other."""
        cov_line_en = translations.get_disease_coverage_line('en')
        cov_line_kn = translations.get_disease_coverage_line('kn')
        cov_line_hi = translations.get_disease_coverage_line('hi')

        for key, info in translations.DISEASE_COVERAGE.items():
            status = info['status']
            name_en = info['name']['en']
            
            notice_en = translations.get_crop_support_notice(key, 'en')
            notice_kn = translations.get_crop_support_notice(key, 'kn')
            notice_hi = translations.get_crop_support_notice(key, 'hi')

            # Plain farmer language check: No forbidden jargon
            for text in [notice_en, notice_kn, notice_hi, cov_line_en, cov_line_kn, cov_line_hi]:
                self.assertNotIn("model", text.lower())
                self.assertNotIn("training data", text.lower())
                self.assertNotIn("classifier", text.lower())

            if status in ['full', 'disease_only']:
                # Supported crop: notice MUST state photo diagnosis / check covers or is available
                self.assertTrue(notice_en.startswith("Photo"), f"Contradiction for supported crop: {key} (got: '{notice_en}')")
                self.assertNotIn("photo diagnosis is not available", notice_en.lower(), f"Contradiction for supported crop: {key}")
                self.assertTrue(translations.is_disease_diagnosis_supported(key))
            elif status == 'healthy_only':
                self.assertTrue(notice_en.startswith("Photo"), f"Contradiction for healthy-only crop: {key} (got: '{notice_en}')")
                self.assertFalse(translations.is_disease_diagnosis_supported(key))
            else:
                # Reference only: notice MUST state photo diagnosis is not available
                self.assertIn("photo diagnosis is not available", notice_en.lower(), f"Contradiction for reference-only crop: {key}")
                self.assertFalse(translations.is_disease_diagnosis_supported(key))

    def test_6_named_constants(self):
        """Verify all confidence and match thresholds are defined as named constants."""
        self.assertEqual(translations.CROP_MATCH_THRESHOLD, 0.60)
        self.assertEqual(translations.DISEASE_CONFIDENCE_THRESHOLD, 0.70)
        self.assertEqual(translations.MIN_CONFIDENCE_MARGIN, 0.15)


if __name__ == '__main__':
    unittest.main()
