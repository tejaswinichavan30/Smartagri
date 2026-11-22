import unittest
import json
import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.agri_decision_intelligence import (
    DigitalTwinEngine,
    CounterfactualCausalEngine,
    MultiAgentDebateEngine,
    RegretMinimizationEngine
)
from app import app

class TestDecisionIntelligence(unittest.TestCase):
    
    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_digital_twin_simulation(self):
        result = DigitalTwinEngine.simulate(
            crop='Tomato',
            rainfall_delta_pct=-20.0,
            sowing_shift_days=5,
            fertilizer_pct=110.0,
            irrigation_frequency_days=5
        )
        self.assertIn('projected_yield_q_acre', result)
        self.assertIn('crop_health_score', result)
        self.assertIn('simulated_soil_moisture', result)
        self.assertGreater(result['crop_health_score'], 0)
        self.assertGreater(result['projected_profit_inr'], 0)

    def test_counterfactual_engine(self):
        res = CounterfactualCausalEngine.evaluate_query(
            query="If I had irrigated 3 days earlier, would my blight disease have been reduced?",
            crop="Tomato",
            disease="Early Blight",
            district="Dharwad",
            lang="en"
        )
        self.assertEqual(res['status'], 'success')
        self.assertIn('confidence_pct', res)
        self.assertIn('explanation', res)
        self.assertGreater(res['confidence_pct'], 50)

    def test_multi_agent_debate(self):
        res = MultiAgentDebateEngine.conduct_debate(
            crop="Rice",
            district="Dharwad",
            disease="",
            price_info="Rs 2400/q",
            farmer_budget="moderate",
            lang="en"
        )
        self.assertEqual(res['status'], 'success')
        self.assertIn('debate_turns', res)
        self.assertIn('consensus_summary', res)
        self.assertGreaterEqual(len(res['debate_turns']), 4)

    def test_regret_minimization_plans(self):
        res = RegretMinimizationEngine.get_plans(
            crop="Cotton",
            risk_preference="balanced"
        )
        self.assertEqual(res['status'], 'success')
        self.assertIn('safe_plan', res)
        self.assertIn('balanced_plan', res)
        self.assertIn('aggressive_plan', res)
        self.assertIn('stress_test_matrix', res)

    def test_predict_irrigation_endpoint(self):
        r = self.client.post('/api/predict_irrigation', json={
            'crop': 'Tomato',
            'growth_stage': 'vegetative',
            'soil_type': 'loam',
            'area_acres': 1.5,
            'irrigation_type': 'drip',
            'district': 'Dharwad',
            'lang': 'en'
        })
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('data', data)
        self.assertIn('total_litres_day', data['data'])
        self.assertTrue(data['data'].get('base_total_litres_day', 0) > 0 or data['data'].get('total_litres_day', 0) > 0)

    def test_flask_api_endpoints(self):
        # Digital Twin
        r1 = self.client.post('/api/decision_intelligence/digital_twin', json={
            'crop': 'Maize',
            'rainfall_delta_pct': 10,
            'fertilizer_pct': 100
        })
        self.assertEqual(r1.status_code, 200)
        data1 = json.loads(r1.data)
        self.assertEqual(data1['status'], 'success')

        # Counterfactual
        r2 = self.client.post('/api/decision_intelligence/counterfactual', json={
            'query': 'If I sowed 10 days earlier, what would happen?',
            'crop': 'Wheat',
            'district': 'Dharwad'
        })
        self.assertEqual(r2.status_code, 200)
        data2 = json.loads(r2.data)
        self.assertEqual(data2['status'], 'success')

        # Multi-Agent Debate
        r3 = self.client.post('/api/decision_intelligence/multi_agent_debate', json={
            'crop': 'Tomato',
            'district': 'Dharwad'
        })
        self.assertEqual(r3.status_code, 200)
        data3 = json.loads(r3.data)
        self.assertEqual(data3['status'], 'success')

        # Regret Plans
        r4 = self.client.post('/api/decision_intelligence/regret_plans', json={
            'crop': 'Rice',
            'risk_preference': 'safe'
        })
        self.assertEqual(r4.status_code, 200)
        data4 = json.loads(r4.data)
        self.assertEqual(data4['status'], 'success')


if __name__ == '__main__':
    unittest.main()
