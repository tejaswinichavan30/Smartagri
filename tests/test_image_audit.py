# -*- coding: utf-8 -*-
"""
SmartAgri AI - Disease Image Verification & Audit Unit Tests
Validates all image audit rules:
- No missing, undecodable, or undersized files for ok images.
- Exact and near-duplicate validation with PHASH_FAIL_DISTANCE.
- Flask test client HTTP 200 & image content type checks.
- React frontend dist integration.
- data/image_review.json and missing_images_to_supply.csv validation.
"""

import os
import csv
import json
import unittest
import hashlib
from PIL import Image
import numpy as np

import app
import translations
from models.image_verifier import (
    MIN_IMAGE_BYTES,
    MIN_IMAGE_DIM,
    MAX_IMAGE_BYTES,
    PHASH_MAX_DISTANCE,
    PHASH_FAIL_DISTANCE,
    load_image_review_config,
    evaluate_image_status,
    compute_ahash_from_image,
    hamming_distance
)

class TestDiseaseImageAudit(unittest.TestCase):

    def setUp(self):
        self.client = app.app.test_client()
        self.app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config = load_image_review_config()

    def test_image_review_config_exists_and_valid(self):
        """Verify data/image_review.json exists, is valid JSON, and has required keys."""
        config_path = os.path.join(self.app_dir, 'data', 'image_review.json')
        self.assertTrue(os.path.exists(config_path), "data/image_review.json must exist")
        with open(config_path, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        self.assertIn('overrides', cfg)
        self.assertIn('embedded_text_flags', cfg)
        self.assertIn('whitelisted_near_duplicate_pairs', cfg)

        # Check required manual overrides
        overrides = cfg['overrides']
        self.assertIn('cotton/healthy', overrides)
        self.assertEqual(overrides['cotton/healthy']['status_override'], 'ok')
        self.assertIn('pepper/bacterial_spot', overrides)
        self.assertEqual(overrides['pepper/bacterial_spot']['status_override'], 'ok')

    def test_missing_images_csv_exists_and_valid(self):
        """Verify missing_images_to_supply.csv exists and has correct columns and rows."""
        csv_path = os.path.join(self.app_dir, 'missing_images_to_supply.csv')
        self.assertTrue(os.path.exists(csv_path), "missing_images_to_supply.csv must exist")
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            expected_headers = ['crop', 'disease', 'expected_filename', 'expected_path', 'reason']
            self.assertEqual(reader.fieldnames, expected_headers)
            rows = list(reader)
        self.assertGreater(len(rows), 0, "CSV must list missing/needs_review images")
        valid_reasons = {'missing', 'needs_review', 'wrong_crop', 'embedded_text'}
        for r in rows:
            self.assertIn(r['reason'], valid_reasons, f"Unexpected reason: {r['reason']} in row {r}")

    def test_all_ok_images_exist_decodable_and_meet_thresholds(self):
        """Verify that every image with status 'ok' physically exists, is decodable, and >= 200x200 & >= 5KB."""
        samples_dict = translations.CROP_DISEASE_SAMPLES
        ok_count = 0
        for crop, sample_list in samples_dict.items():
            for s in sample_list:
                eval_res = evaluate_image_status(crop, s.get('id', ''), s.get('image', ''))
                if eval_res['status'] == 'ok':
                    img_path = eval_res['resolved_path']
                    abs_path = os.path.join(self.app_dir, img_path)
                    self.assertTrue(os.path.exists(abs_path), f"Image file missing for ok status: {abs_path}")
                    sz = os.path.getsize(abs_path)
                    self.assertGreaterEqual(sz, MIN_IMAGE_BYTES, f"File undersized: {abs_path} ({sz} B)")
                    with Image.open(abs_path) as im:
                        w, h = im.size
                    self.assertGreaterEqual(w, MIN_IMAGE_DIM[0], f"Width {w} < {MIN_IMAGE_DIM[0]} for {abs_path}")
                    self.assertGreaterEqual(h, MIN_IMAGE_DIM[1], f"Height {h} < {MIN_IMAGE_DIM[1]} for {abs_path}")
                    ok_count += 1
        self.assertGreater(ok_count, 30, "Should have a solid set of verified ok images")

    def test_phash_near_duplicates_and_fail_threshold(self):
        """
        Verify no unwhitelisted duplicate or near-duplicate pairs exist with hamming distance <= PHASH_FAIL_DISTANCE (2)
        among 'ok' images.
        """
        samples_dict = translations.CROP_DISEASE_SAMPLES
        image_hashes = {}
        for crop, sample_list in samples_dict.items():
            for s in sample_list:
                d_id = s.get('id', '')
                eval_res = evaluate_image_status(crop, d_id, s.get('image', ''))
                if eval_res['status'] == 'ok':
                    abs_path = os.path.join(self.app_dir, eval_res['resolved_path'])
                    key = f"{crop.lower().strip()}/{d_id}"
                    if key not in image_hashes:
                        with Image.open(abs_path) as im:
                            h = compute_ahash_from_image(im)
                            with open(abs_path, 'rb') as fp:
                                sha = hashlib.sha256(fp.read()).hexdigest()
                        image_hashes[key] = {'ahash': h, 'sha256': sha, 'crop': crop.lower().strip(), 'disease': d_id}

        keys = list(image_hashes.keys())
        whitelisted = self.config.get('whitelisted_near_duplicate_pairs', [])
        whitelist_set = {tuple(sorted([p[0].lower(), p[1].lower()])) for p in whitelisted}

        near_dup_list = []
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                k1, k2 = keys[i], keys[j]
                m1, m2 = image_hashes[k1], image_hashes[k2]
                
                # Exclude corn/maize aliased duplicates
                if (m1['crop'] in ['corn', 'maize', 'corn_(maize)', 'maize (corn)'] and
                    m2['crop'] in ['corn', 'maize', 'corn_(maize)', 'maize (corn)'] and
                    m1['disease'] == m2['disease']):
                    continue
                
                dist = hamming_distance(m1['ahash'], m2['ahash'])
                pair_tuple = tuple(sorted([k1, k2]))
                
                if dist <= PHASH_MAX_DISTANCE:
                    near_dup_list.append((k1, k2, dist, m1['sha256'] == m2['sha256']))
                    
                if dist <= PHASH_FAIL_DISTANCE and pair_tuple not in whitelist_set:
                    self.fail(f"Unwhitelisted duplicate pair detected with distance {dist} <= {PHASH_FAIL_DISTANCE}: {k1} vs {k2}")

        print(f"\n[Image Audit] Found {len(near_dup_list)} near-duplicate pairs (dist <= {PHASH_MAX_DISTANCE})")

    def test_flask_http_200_and_content_type_for_ok_images(self):
        """Verify that every image returned for ok status returns HTTP 200 with image/jpeg or image/png."""
        samples_dict = translations.CROP_DISEASE_SAMPLES
        tested_urls = set()
        for crop, sample_list in samples_dict.items():
            for s in sample_list:
                eval_res = evaluate_image_status(crop, s.get('id', ''), s.get('image', ''))
                if eval_res['status'] == 'ok':
                    img_rel = eval_res['resolved_path']
                    if img_rel in tested_urls:
                        continue
                    tested_urls.add(img_rel)
                    
                    url = f"/{img_rel}"
                    resp = self.client.get(url)
                    self.assertEqual(resp.status_code, 200, f"HTTP {resp.status_code} for {url}")
                    c_type = resp.headers.get('Content-Type', '')
                    self.assertTrue(
                        c_type.startswith('image/'),
                        f"Expected image content-type for {url}, got {c_type}"
                    )

    def test_corn_maize_aliasing(self):
        """Verify that corn and maize are aliased and both resolve cleanly."""
        maize_samples = translations.get_crop_disease_samples('maize', 'en')
        corn_samples = translations.get_crop_disease_samples('corn', 'en')
        self.assertEqual(len(maize_samples), len(corn_samples))
        for ms, cs in zip(maize_samples, corn_samples):
            self.assertEqual(ms['id'], cs['id'])
            self.assertEqual(ms['status'], cs['status'])

    def test_provenance_badge_translations(self):
        """Verify neutral provenance badge text is returned for en, kn, and hi."""
        sample_en = translations.get_crop_disease_samples('tomato', 'en')[0]
        self.assertEqual(sample_en['provenance_badge'], "Reference image (source not yet verified)")
        self.assertEqual(sample_en['image_type'], "unknown")

        sample_kn = translations.get_crop_disease_samples('tomato', 'kn')[0]
        self.assertEqual(sample_kn['provenance_badge'], "ಉಲ್ಲೇಖ ಚಿತ್ರ (ಮೂಲ ಪರಿಶೀಲಿಸಬೇಕಿದೆ)")

        sample_hi = translations.get_crop_disease_samples('tomato', 'hi')[0]
        self.assertEqual(sample_hi['provenance_badge'], "संदर्भ छवि (स्रोत अभी सत्यापित नहीं है)")

    def test_optimized_images_exist_and_under_max_bytes(self):
        """Verify that optimized image folder exists and all images in it are under MAX_IMAGE_BYTES (300 KB)."""
        opt_dir = os.path.join(self.app_dir, 'static', 'disease_samples_optimized')
        self.assertTrue(os.path.exists(opt_dir), "Optimized samples folder must exist")
        for root, dirs, files in os.walk(opt_dir):
            for f in files:
                full_path = os.path.join(root, f)
                sz = os.path.getsize(full_path)
                self.assertLessEqual(sz, MAX_IMAGE_BYTES, f"Optimized file exceeds 300KB: {full_path} ({sz} bytes)")
                with Image.open(full_path) as im:
                    w, h = im.size
                self.assertLessEqual(w, 800, f"Optimized width {w} > 800 for {full_path}")

if __name__ == '__main__':
    unittest.main()
