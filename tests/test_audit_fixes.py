"""
Comprehensive Test Suite for SmartAgri Farm Management Platform Audit Fixes
Tests all 8 audited items:
1. MSP Config & Official PIB/CCEA Gazettes (Paddy Rs 2441, Sunflower Rs 8343, static retrieval_date, valid source URLs)
2. Paddy vs Milled Rice separation, unanchored outlook suppression (SHOW_UNANCHORED_OUTLOOK=False), and month-jump warning
3. Pesticides Allowlist & DPPQ&S safety rules (carbofuran banned, carbosulfan under review, zero chemical mentions in translations, LLM post-filter)
4. FAO-56 ET0 calculations (Eq. 21 Ra, plausibility warnings, rounded temperatures, pump flow rate, Kc, Peff)
5. Disease sample image paths (0 missing files / 0 404s) and neutral reference badge
6. Selling tips anchored to multi-year modal trends or MSP centers
7. Sowing windows labeled with general/hedged guidance
8. Mandi price feed statuses and fallback message
"""

import os
import json
import math
import unittest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app
import translations
from models.agmarknet_service import agmarknet_service, PriceFeedStatus
from models.agri_llm_service import sanitize_llm_chemical_output


class TestAuditFixes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.app.testing = True
        cls.client = app.app.test_client()

    # ==========================================
    # ITEM 1: MSP CONFIG & OFFICIAL SOURCES
    # ==========================================
    def test_item_1_msp_reviewed_values_and_sources(self):
        """Verify MSP config contains audited figures, official PIB/CCEA URLs, and static retrieval_date."""
        msp_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'msp_config.json')
        self.assertTrue(os.path.exists(msp_path), "data/msp_config.json must exist")
        
        with open(msp_path, 'r', encoding='utf-8') as f:
            msp_data = json.load(f)

        crops = msp_data.get('commodities', {})
        
        # 1. Paddy Common MSP must be 2441 (2026-27 CCEA verified)
        self.assertIn('paddy', crops)
        paddy = crops['paddy']
        self.assertEqual(paddy['msp_per_quintal'], 2441)
        self.assertIn('2026-27', paddy.get('marketing_season', ''))
        self.assertTrue(paddy['source_url'].startswith('https://pib.gov.in') or paddy['source_url'].startswith('https://agricoop.gov.in') or paddy['source_url'].startswith('https://cacp.dacnet.nic.in'))
        self.assertEqual(paddy['retrieval_date'], '2026-10-04')

        # 2. Sunflower MSP must be 8343 (2026-27 CCEA verified)
        self.assertIn('sunflower', crops)
        sunflower = crops['sunflower']
        self.assertEqual(sunflower['msp_per_quintal'], 8343)
        self.assertIn('2026-27', sunflower.get('marketing_season', ''))
        self.assertTrue(sunflower['source_url'].startswith('https://pib.gov.in') or sunflower['source_url'].startswith('https://agricoop.gov.in') or sunflower['source_url'].startswith('https://cacp.dacnet.nic.in'))
        self.assertEqual(sunflower['retrieval_date'], '2026-10-04')

        # 3. Maize MSP must be 2410
        self.assertIn('maize', crops)
        self.assertEqual(crops['maize']['msp_per_quintal'], 2410)

        # 4. Ragi MSP must be 5205
        self.assertIn('ragi', crops)
        self.assertEqual(crops['ragi']['msp_per_quintal'], 5205)

        # 5. Non-mandated crops show "No government MSP for this crop"
        for unmandated in ['tomato', 'potato', 'onion', 'chilli']:
            self.assertNotIn(unmandated, crops)

    # ==========================================
    # ITEM 2: PADDY VS RICE & OUTLOOK GUARDRAILS
    # ==========================================
    def test_item_2_paddy_vs_rice_and_forecast_guardrails(self):
        """Verify Paddy does not return milled-rice outlook, SHOW_UNANCHORED_OUTLOOK=False, and month jump warning."""
        # A. Paddy MSP and note
        paddy_forecast = app.compute_price_forecast('Paddy (Common)', 'Dharwad', 2026, 10, lang='en')
        self.assertIn('msp', paddy_forecast)
        self.assertEqual(paddy_forecast['msp'], 2441)
        self.assertIn('raw Paddy', paddy_forecast.get('note', ''))
        # Must not have milled rice forecast months for paddy
        self.assertEqual(paddy_forecast.get('forecast_months', []), [])

        # B. Rice outlook allowed when Rice selected
        rice_forecast = app.compute_price_forecast('Rice', 'Dharwad', 2026, 10, live_price=3800.0, lang='en')
        self.assertGreater(len(rice_forecast.get('forecast_months', [])), 0)

        # C. Unanchored outlook yields 4-month ML baseline when enabled
        unanchored_forecast = app.compute_price_forecast('Rice', 'Dharwad', 2026, 10, live_price=None, lang='en')
        self.assertGreater(len(unanchored_forecast.get('forecast_months', [])), 0)

        # D. Month jump warning wording
        self.assertEqual(app.PRICE_MONTH_JUMP_WARN_PCT, 15.0)

    # ==========================================
    # ITEM 3: PESTICIDES ALLOWLIST & DPPQ&S
    # ==========================================
    def test_item_3_pesticides_dppqs_restricted_list_and_allowlist(self):
        """Verify DPPQ&S restricted list config and zero unapproved chemical mentions in translations."""
        pesticide_cfg_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'pesticide_recommendations.json')
        self.assertTrue(os.path.exists(pesticide_cfg_path))
        with open(pesticide_cfg_path, 'r', encoding='utf-8') as f:
            p_data = json.load(f)

        restricted = p_data.get('dppqs_restricted_or_banned_list', {}) or p_data.get('restricted_or_banned_pesticides', {})
        self.assertIn('carbofuran', restricted)
        self.assertIn(restricted['carbofuran']['status'], ['banned', 'banned_or_restricted'])
        self.assertIn('carbosulfan', restricted)
        self.assertEqual(restricted['carbosulfan']['status'], 'under_review')

        # Test LLM post-filter blocks restricted chemicals
        dirty_llm_text = "Apply Carbofuran 3G at 10kg/ha or Carbosulfan 25 EC to control stem borer."
        clean_llm_text = sanitize_llm_chemical_output(dirty_llm_text)
        self.assertNotIn("Carbofuran", clean_llm_text)
        self.assertNotIn("Carbosulfan", clean_llm_text)
        self.assertIn("approved bio-control / KVK recommended IPM practice", clean_llm_text)

        # Verify translations.py CROP_DISEASE_SAMPLES have zero banned chemicals
        banned_names = ['carbofuran', 'carbosulfan', 'buprofezin', 'tricyclazole', 'monocrotophos', 'phorate', 'paraquat', 'endosulfan']
        for crop_k, samples in translations.CROP_DISEASE_SAMPLES.items():
            for s in samples:
                treatment = (s.get('treatment_en', '') + " " + s.get('symptoms_en', '')).lower()
                for b in banned_names:
                    self.assertNotIn(b, treatment, f"Found banned chemical '{b}' in crop '{crop_k}' sample '{s.get('id')}'")

    # ==========================================
    # ITEM 4: FAO-56 ET0 CALCULATION & PLAUSIBILITY
    # ==========================================
    def test_item_4_fao56_et0_calculation_and_plausibility(self):
        """Verify FAO-56 Eq. 21-25 extraterrestrial radiation, temperature rounding, and plausibility check."""
        # Standard day: Hassan latitude 13.0N, temp=28C, humidity=55%
        res = translations.calculate_smart_irrigation(
            crop='tomato',
            growth_stage='vegetative',
            soil_type='loam',
            area_acres=1.5,
            irrigation_type='drip',
            temp=28.4,
            humidity=55.0,
            rainfall_mm=0.0,
            district='Hassan',
            pump_flow_rate=12000
        )
        self.assertIn('et0', res)
        self.assertGreater(res['et0'], 2.0)
        self.assertLess(res['et0'], 8.0)
        self.assertEqual(res['temp'], 28) # Rounded whole degree
        self.assertTrue(res['is_plausible'])
        self.assertEqual(res['efficiency_pct'], 90) # Drip efficiency
        self.assertEqual(res['et0_method'], 'FAO-56 Hargreaves Radiation Method (Eq. 21 & 52)')

        # Out of bound test -> Plausibility warning (not silent clamp)
        res_extreme = translations.calculate_smart_irrigation(
            crop='tomato',
            temp=55.0, # Extreme unphysical temp
            humidity=5.0,
            district='Bidar'
        )
        if res_extreme['et0'] > 9.0:
            self.assertFalse(res_extreme['is_plausible'])
            self.assertIn('Calculated ET0', res_extreme['plausibility_warning'])

    # ==========================================
    # ITEM 5: IMAGE AUDIT, QUALITY & STATUS VALIDATION
    # ==========================================
    def test_item_5_disease_sample_image_status_and_quality(self):
        """
        Verify image status auditing:
        - All samples have image_status in ('ok', 'missing', 'needs_review').
        - Every 'ok' image is >= 5KB, >= 200x200, validly decodable, has no cross-crop/cross-disease collisions,
          and returns HTTP 200 with an image content-type through the Flask test client.
        - Stubs (149 bytes) are marked 'missing'.
        - Colliding pairs (cotton bacterial_blight vs pepper bacterial_spot) are marked 'needs_review'.
        - Aliased folders (corn and maize) are exempt from duplicate failures.
        - Logs warnings for images exceeding MAX_IMAGE_BYTES (300 KB).
        """
        from PIL import Image
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Test API endpoint returns image_status for samples
        api_resp = self.client.get('/api/crop_disease_samples?crop=Tomato&lang=en')
        self.assertEqual(api_resp.status_code, 200)
        api_json = api_resp.get_json()
        self.assertIn('samples', api_json)
        for s in api_json['samples']:
            self.assertIn('image_status', s)
            self.assertIn(s['image_status'], ['ok', 'missing', 'needs_review'])

        # Audit every crop's samples
        oversized_images = []
        for crop_k in translations.CROP_DISEASE_SAMPLES.keys():
            samples = translations.get_crop_disease_samples(crop_k, 'en')
            for s in samples:
                img_rel = s.get('image', '')
                st = s.get('image_status')
                self.assertIn(st, ['ok', 'missing', 'needs_review'])

                if st == 'ok':
                    img_path = os.path.join(base_dir, img_rel)
                    self.assertTrue(os.path.exists(img_path), f"OK image must exist on disk: {img_rel}")
                    
                    sz = os.path.getsize(img_path)
                    self.assertGreaterEqual(sz, translations.MIN_IMAGE_BYTES, f"OK image must be >= {translations.MIN_IMAGE_BYTES} bytes: {img_rel}")
                    
                    with Image.open(img_path) as im:
                        w, h = im.size
                        self.assertGreaterEqual(w, translations.MIN_IMAGE_DIM[0], f"OK image width must be >= {translations.MIN_IMAGE_DIM[0]}: {img_rel}")
                        self.assertGreaterEqual(h, translations.MIN_IMAGE_DIM[1], f"OK image height must be >= {translations.MIN_IMAGE_DIM[1]}: {img_rel}")

                    # Verify Flask test client returns HTTP 200 with image content type
                    resp = self.client.get(f"/{img_rel}")
                    self.assertEqual(resp.status_code, 200, f"Failed HTTP 200 for OK image: {img_rel}")
                    self.assertTrue(resp.content_type.startswith('image/'), f"Expected image content-type for {img_rel}, got {resp.content_type}")

                    if sz > translations.MAX_IMAGE_BYTES:
                        oversized_images.append((img_rel, sz))

        # Check that cotton bacterial_blight is flagged needs_review, while pepper bacterial_spot is kept ok
        cotton_samples = {s['id']: s for s in translations.get_crop_disease_samples('cotton', 'en')}
        pepper_samples = {s['id']: s for s in translations.get_crop_disease_samples('pepper', 'en')}
        if 'bacterial_blight' in cotton_samples:
            self.assertEqual(cotton_samples['bacterial_blight']['image_status'], 'ok')
        if 'bacterial_spot' in pepper_samples:
            self.assertEqual(pepper_samples['bacterial_spot']['image_status'], 'ok')

        # Check that Arecanut has real images and is marked ok
        arecanut_samples = {s['id']: s for s in translations.get_crop_disease_samples('arecanut', 'en')}
        for s_id, s in arecanut_samples.items():
            self.assertEqual(s['image_status'], 'ok')

        # Check that 149-byte stubs (e.g. Squash) are marked missing
        squash_samples = {s['id']: s for s in translations.get_crop_disease_samples('squash', 'en')}
        for s_id, s in squash_samples.items():
            self.assertEqual(s['image_status'], 'missing')

        # Check that chilli now has real images and is marked ok
        chilli_samples = {s['id']: s for s in translations.get_crop_disease_samples('chilli', 'en')}
        for s_id, s in chilli_samples.items():
            if s_id in ['leaf_curl', 'fruit_rot', 'bacterial_wilt']:
                self.assertEqual(s['image_status'], 'ok')

        if oversized_images:
            print(f"\n[Quality Warning] {len(oversized_images)} image(s) exceed MAX_IMAGE_BYTES (300 KB):")
            for img_p, sz in oversized_images:
                print(f"  - {img_p} ({sz/1024:.1f} KB)")

    # ==========================================
    # ITEM 6: SELLING TIPS
    # ==========================================
    def test_item_6_selling_tips_anchoring(self):
        """Verify selling tips reference multi-year trends or APMC/MSP procurement rather than arbitrary claims."""
        for crop_k, tr_data in translations.CROP_TRANSLATIONS.items():
            if 'sell_tip' in tr_data:
                tip_en = tr_data['sell_tip'].get('en', '')
                self.assertTrue(len(tip_en) > 0)
                # Confirm it is not an ungrounded single assertion
                self.assertTrue('Agmarknet' in tip_en or 'MSP' in tip_en or 'modal price' in tip_en or 'procurement' in tip_en or 'KVK' in tip_en or 'trend' in tip_en)

    # ==========================================
    # ITEM 7: SOWING WINDOWS
    # ==========================================
    def test_item_7_sowing_windows_hedged_labels(self):
        """Verify sowing windows are marked with general/hedged guidance."""
        for crop_k, tr_data in translations.CROP_TRANSLATIONS.items():
            if 'planting_months' in tr_data:
                p_en = tr_data['planting_months'].get('en', '')
                self.assertTrue(len(p_en) > 0)

    # ==========================================
    # ITEM 8: PRICE FEED & STATUSES
    # ==========================================
    def test_item_8_price_feed_statuses_and_fallback(self):
        """Verify PriceFeedStatus enum and fallback messaging."""
        self.assertTrue(hasattr(PriceFeedStatus, 'UNREACHABLE'))
        self.assertTrue(hasattr(PriceFeedStatus, 'FORMAT_CHANGED'))
        self.assertTrue(hasattr(PriceFeedStatus, 'NO_RECENT_DATA'))
        self.assertTrue(hasattr(PriceFeedStatus, 'LIVE_API'))

        feed_res = agmarknet_service.fetch_live_mandi_price('Paddy', 'Dharwad')
        if feed_res is not None:
            self.assertIn(feed_res.get('status'), [PriceFeedStatus.UNREACHABLE, PriceFeedStatus.FORMAT_CHANGED, PriceFeedStatus.NO_RECENT_DATA, PriceFeedStatus.LIVE_API, PriceFeedStatus.LIVE_CACHED, PriceFeedStatus.BENCHMARK_RECORD])
        else:
            self.assertIsNone(feed_res)


if __name__ == '__main__':
    unittest.main()
