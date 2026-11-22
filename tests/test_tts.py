"""
Test suite for SmartAgri Multilingual Text-to-Speech (TTS) pipeline.
Tests Kannada (kn), Hindi (hi), and English (en) speech synthesis.
"""

import sys
import os
import io

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, sanitize_tts_text
from gtts import gTTS

def test_sanitizer():
    print("\n--- 1. Testing Text Sanitization for TTS ---")
    raw = "🌾 **Rice Crop:** Apply [ICAR Guide] fertilizer • Nitrogen 100 kg/ha! 💡 Check https://icar.gov.in"
    cleaned = sanitize_tts_text(raw)
    print(f"Raw:     '{raw}'")
    print(f"Cleaned: '{cleaned}'")
    assert "🌾" not in cleaned, "Emoji was not removed"
    assert "**" not in cleaned, "Markdown bold not removed"
    assert "http" not in cleaned, "URL was not removed"
    assert "ICAR" not in cleaned, "Bracket citation was not removed"
    print("✓ Sanitizer correctly strips non-speech artifacts.")

def test_direct_gtts_synthesis():
    print("\n--- 2. Testing Direct gTTS Generation (Kannada, Hindi, English) ---")
    samples = {
        'kn': 'ನಮಸ್ಕಾರ ರೈತ ಮಿತ್ರರೇ. ಭತ್ತದ ಬೆಳೆಗೆ ಸಾರಜನಕ ಗೊಬ್ಬರ ಹಾಕಿ.',
        'hi': 'नमस्ते किसान भाई। धान की फसल के लिए सही खाद का प्रयोग करें।',
        'en': 'Hello Farmer. Apply balanced NPK fertilizers for optimal yield.'
    }

    for lang, text in samples.items():
        tts = gTTS(text=text, lang=lang, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_data = fp.read()
        size_kb = len(audio_data) / 1024
        print(f"✓ Lang '{lang}': Synthesized {len(text)} chars -> {size_kb:.1f} KB MP3 audio stream")
        assert len(audio_data) > 1000, f"Generated audio for {lang} is too small"

def test_flask_tts_endpoint():
    print("\n--- 3. Testing Flask /api/tts Endpoint (GET & POST) ---")
    client = app.test_client()

    # GET test for Kannada
    res_kn = client.get('/api/tts?lang=kn&text=ಟೊಮೆಟೊ+ರೋಗ+ನಿಯಂತ್ರಣ+ಮಾಹಿತಿ')
    assert res_kn.status_code == 200, f"Kannada GET failed with {res_kn.status_code}"
    assert res_kn.content_type == "audio/mpeg", f"Wrong content-type: {res_kn.content_type}"
    assert len(res_kn.data) > 1000, "Audio response data is empty"
    print(f"✓ GET /api/tts (Kannada): 200 OK ({len(res_kn.data)} bytes)")

    # POST test for Hindi
    res_hi = client.post('/api/tts', json={
        "lang": "hi",
        "text": "टमाटर के झुलसा रोग के लिए मैंकोजेब का छिड़काव करें।"
    })
    assert res_hi.status_code == 200, f"Hindi POST failed with {res_hi.status_code}"
    assert res_hi.content_type == "audio/mpeg", f"Wrong content-type: {res_hi.content_type}"
    assert len(res_hi.data) > 1000, "Audio response data is empty"
    print(f"✓ POST /api/tts (Hindi): 200 OK ({len(res_hi.data)} bytes)")

    # Cached request test
    res_hi_cached = client.post('/api/tts', json={
        "lang": "hi",
        "text": "टमाटर के झुलसा रोग के लिए मैंकोजेब का छिड़काव करें।"
    })
    assert res_hi_cached.status_code == 200, "Cached request failed"
    assert len(res_hi_cached.data) == len(res_hi.data), "Cached data length mismatch"
    print(f"✓ Cache hit test passed successfully.")

    print("\n✓ ALL MULTILINGUAL TTS TESTS PASSED!")

if __name__ == "__main__":
    test_sanitizer()
    test_direct_gtts_synthesis()
    test_flask_tts_endpoint()
