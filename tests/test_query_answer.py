"""
Unit tests for SmartAgri Multilingual Agronomist Voice & Query Answers (Kannada, Hindi, English).
"""

import os
import sys
import unittest

# Ensure root project path is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from models.agri_llm_service import agri_llm
import translations
from app import app


class TestQueryAnswer(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_kannada_june_sowing_query(self):
        query = "ಕರ್ನಾಟಕದಲ್ಲಿ ಜೂನ್ ತಿಂಗ್ಳಲ್ಲಿ ಬಿತ್ತನೆ ಮಾಡಲು ಸೂಕ್ತವಾದ ಬೆಳೆಗಳು ಯಾವುವು"
        res = agri_llm.ask_agronomist_rag(query, lang="kn")
        answer = res.get("answer", "")
        print("\n--- 1. Kannada June Sowing Answer Length:", len(answer))
        self.assertTrue(len(answer) > 100, "Answer should be detailed")
        self.assertTrue("ಭತ್ತ" in answer or "ಮೆಕ್ಕೆಜೋಳ" in answer or "ರಾಗಿ" in answer, "Must recommend Karnataka crops")
        self.assertTrue("ಜೂನ್" in answer or "ಮುಂಗಾರು" in answer or "ಖಾರಿಫ್" in answer, "Must address June / Kharif season")

    def test_kannada_fertilizer_query(self):
        query = "ಮೆಕ್ಕೆಜೋಳಕ್ಕೆ ಯಾವ ಗೊಬ್ಬರ ಹಾಕಬೇಕು"
        res = agri_llm.ask_agronomist_rag(query, lang="kn")
        answer = res.get("answer", "")
        print("\n--- 2. Kannada Fertilizer Answer Length:", len(answer))
        self.assertTrue(len(answer) > 100)
        self.assertTrue("ಸಾರಜನಕ" in answer or "NPK" in answer or "ಗೊಬ್ಬರ" in answer)

    def test_hindi_disease_query(self):
        query = "धान के रोग और दवा बताएं"
        res = agri_llm.ask_agronomist_rag(query, lang="hi")
        answer = res.get("answer", "")
        print("\n--- 3. Hindi Disease Answer Length:", len(answer))
        self.assertTrue(len(answer) > 100)
        self.assertTrue("रोग" in answer or "कीट" in answer or "उपचार" in answer)

    def test_english_june_sowing_query(self):
        query = "Which crops are suitable for June sowing in Karnataka?"
        res = agri_llm.ask_agronomist_rag(query, lang="en")
        answer = res.get("answer", "")
        print("\n--- 4. English June Sowing Answer Length:", len(answer))
        self.assertTrue(len(answer) > 100)
        self.assertTrue("Paddy" in answer or "Rice" in answer or "Maize" in answer)

    def test_hindi_maize_irrigation_query(self):
        query = "मक्के की फसल को कितने दिन के अंतराल पर पानी देना चाहिए"
        res = agri_llm.ask_agronomist_rag(query, lang="hi")
        answer = res.get("answer", "")
        print("\n--- 5. Hindi Maize Irrigation Answer Length:", len(answer))
        self.assertTrue(len(answer) > 150, "Answer should be complete and detailed")
        self.assertTrue("सिंचाई" in answer or "पानी" in answer, "Must provide irrigation guidelines")
        self.assertTrue("मक्का" in answer or "मक्के" in answer or "दिन" in answer, "Must mention intervals")

    def test_translations_voice_builder(self):
        query = "ಕರ್ನಾಟಕದಲ್ಲಿ ಜೂನ್ ತಿಂಗ್ಳಲ್ಲಿ ಬಿತ್ತನೆ ಮಾಡಲು ಸೂಕ್ತವಾದ ಬೆಳೆಗಳು ಯಾವುವು"
        ans = translations.build_multilingual_voice_answer(query, "kn")
        self.assertTrue(len(ans) > 100)

    def test_kannada_maize_fall_armyworm_query(self):
        query = "ಮೆಕ್ಕೆಜೋಳದ ಸೈನಿಕ ಹುಳ ನಿಯಂತ್ರಣಕ್ಕೆ ಪರಿಹಾರವೇನು"
        res = agri_llm.ask_agronomist_rag(query, lang="kn")
        answer = res.get("answer", "")
        self.assertTrue(len(answer) > 200, "Answer should be detailed and complete")
        self.assertTrue("ಸೈನಿಕ ಹುಳು" in answer or "ನಿಯಂತ್ರಣ" in answer or "ಎಮಾಮೆಕ್ಟಿನ್" in answer or "ಬೇವಿನ ಎಣ್ಣೆ" in answer, "Must provide Kannada FAW recommendations")
        self.assertNotIn("Document 1 ([Karnataka", answer, "Must not leak raw English RAG text")


if __name__ == "__main__":
    unittest.main()

