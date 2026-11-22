"""
Unit tests to verify Server-Side Session persistence across all SmartAgri Agents:
Crop Recommendation, Price Prediction, Leaf Disease Detection, Smart Irrigation, and Planner.
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app


class TestServerSideSession(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_multi_agent_session_persistence(self):
        # 1. Simulate setting all agents' data in session
        with self.app.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'farmer'
            sess['recommended_crop'] = 'Cotton'
            sess['predicted_price'] = 7150.0
            sess['city'] = 'Chamarajanagara'
            sess['predicted_crop'] = 'Cotton'
            sess['predicted_disease'] = 'Bacterial spot'
            sess['disease_confidence'] = 98.5
            sess['disease_result_en'] = 'Disease Prediction: Cotton : Bacterial spot (Confidence: 98.50%)'
            sess['disease_result_kn'] = 'ರೋಗ ಪತ್ತೆ ಫಲಿತಾಂಶ: ಹತ್ತಿ : ಬ್ಯಾಕ್ಟೀರಿಯಲ್ ಸ್ಪಾಟ್ (ವಿಶ್ವಾಸಾರ್ಹತೆ: 98.50%)'
            sess['irrigation_data'] = {
                'crop': 'Cotton',
                'water_liters_per_day': 18500,
                'irrigation_runtime_str': '2 hours 15 mins',
                'interval_days': 4
            }
            sess['irrigation_result_en'] = 'Irrigation: 18,500 L/day (Runtime: 2 hrs 15 mins every 4 days)'
            sess['irrigation_result_kn'] = 'ನೀರಾವರಿ: 18,500 ಲೀಟರ್/ದಿನ (ಪ್ರತಿ 4 ದಿನಗಳಿಗೊಮ್ಮೆ 2 ಗಂಟೆ 15 ನಿಮಿಷ)'

        # 2. Verify session persistence in get_session_data helper
        from app import get_session_data
        with self.app as client:
            client.get('/')
            session_data = get_session_data()
            self.assertEqual(session_data.get('recommended_crop'), 'Cotton')
            self.assertEqual(session_data.get('predicted_disease'), 'Bacterial spot')
            self.assertEqual(session_data.get('city'), 'Chamarajanagara')
            self.assertIn('18,500', session_data.get('irrigation_result_en', ''))
            print("\n--- Server-Side Session Test: All 4 agents retained perfectly in session data!")


if __name__ == "__main__":
    unittest.main()
