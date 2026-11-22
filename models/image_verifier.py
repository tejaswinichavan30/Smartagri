# -*- coding: utf-8 -*-
"""
SmartAgri AI - Image Audit & Verification Module
Computes image status (ok, missing, needs_review), hashes, dimensions,
and manages review overrides from data/image_review.json.
"""

import os
import json
import hashlib
from PIL import Image
import numpy as np

# Named Constants as mandated by Audit Specifications
MIN_IMAGE_BYTES = 5120          # 5 KB
MIN_IMAGE_DIM = (200, 200)      # 200x200 pixels minimum
MAX_IMAGE_BYTES = 300 * 1024    # 300 KB max threshold for warnings/optimization
PHASH_MAX_DISTANCE = 10         # Near-duplicate threshold for human review listing
PHASH_FAIL_DISTANCE = 2         # Strict threshold for build failure unless whitelisted
JPEG_QUALITY = 85               # Standard JPEG compression quality for optimized copies
MAX_RESIZED_WIDTH = 800         # Max width for resized image copies

PROVENANCE_BADGE = {
    'en': 'Reference image (source not yet verified)',
    'kn': 'ಉಲ್ಲೇಖ ಚಿತ್ರ (ಮೂಲ ಪರಿಶೀಲಿಸಬೇಕಿದೆ)',
    'hi': 'संदर्भ छवि (स्रोत अभी सत्यापित नहीं है)'
}

CROP_ALIASES = {
    'corn': 'maize',
    'corn_(maize)': 'maize',
    'maize (corn)': 'maize'
}

_CONFIG_CACHE = None

def load_image_review_config():
    """Load manual overrides, embedded text flags, and whitelists from data/image_review.json."""
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'image_review.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                _CONFIG_CACHE = json.load(f)
                return _CONFIG_CACHE
        except Exception as e:
            print(f"[ImageVerifier] Warning: failed to load image_review.json: {e}")
    
    _CONFIG_CACHE = {
        'overrides': {},
        'embedded_text_flags': {},
        'whitelisted_near_duplicate_pairs': []
    }
    return _CONFIG_CACHE

def compute_ahash_from_image(img, hash_size=8):
    """Compute 64-bit Average Hash (aHash) for an open PIL Image."""
    try:
        img_gray = img.convert('L').resize((hash_size, hash_size), Image.Resampling.LANCZOS)
        pixels = np.asarray(img_gray)
        avg = pixels.mean()
        diff = pixels > avg
        return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])
    except Exception:
        return None

def compute_dhash_from_image(img, hash_size=8):
    """Compute 64-bit Difference Hash (dHash) for an open PIL Image."""
    try:
        img_gray = img.convert('L').resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
        pixels = np.asarray(img_gray)
        diff = pixels[:, 1:] > pixels[:, :-1]
        return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])
    except Exception:
        return None

def hamming_distance(h1, h2):
    """Compute Hamming distance between two integer hashes."""
    if h1 is None or h2 is None:
        return 999
    return bin(h1 ^ h2).count('1')

def resolve_optimized_image_path(image_rel_path):
    """
    If an optimized copy exists in static/disease_samples_optimized/, return it.
    Otherwise return the original image path.
    """
    if not image_rel_path:
        return image_rel_path

    norm_rel = image_rel_path.replace('\\', '/')
    if 'static/disease_samples/' in norm_rel:
        opt_rel = norm_rel.replace('static/disease_samples/', 'static/disease_samples_optimized/')
        if os.path.exists(opt_rel):
            return opt_rel
    return image_rel_path

def evaluate_image_status(crop, disease_id, image_rel_path):
    """
    Evaluate an image against all validation rules.
    Returns dict with:
      - status: 'ok', 'missing', or 'needs_review'
      - reason: string explanation
      - has_embedded_text: bool
      - resolved_path: path to optimized or original image
      - width, height, size_bytes
    """
    config = load_image_review_config()
    overrides = config.get('overrides', {})
    embedded_flags = config.get('embedded_text_flags', {})

    # Normalize crop name for aliasing
    norm_crop = crop.lower().strip()
    aliased_crop = CROP_ALIASES.get(norm_crop, norm_crop)
    key = f"{aliased_crop}/{disease_id}"
    orig_key = f"{norm_crop}/{disease_id}"

    # Embedded text flag (report only)
    has_text = False
    if key in embedded_flags:
        has_text = embedded_flags[key].get('has_embedded_text', False)
    elif orig_key in embedded_flags:
        has_text = embedded_flags[orig_key].get('has_embedded_text', False)
    elif (key in overrides and overrides[key].get('has_embedded_text')):
        has_text = overrides[key].get('has_embedded_text')

    # Resolve physical image path
    target_path = resolve_optimized_image_path(image_rel_path)
    full_path = os.path.normpath(os.path.join('.', target_path)) if target_path else ''

    # 1. Physical presence & size check
    if not target_path or not os.path.exists(full_path):
        return {
            'status': 'missing',
            'reason': 'file_absent',
            'has_embedded_text': has_text,
            'resolved_path': target_path,
            'width': 0,
            'height': 0,
            'size_bytes': 0
        }

    size_bytes = os.path.getsize(full_path)
    if size_bytes < MIN_IMAGE_BYTES:
        return {
            'status': 'missing',
            'reason': f'under_min_bytes ({size_bytes} B < {MIN_IMAGE_BYTES} B, placeholder file)',
            'has_embedded_text': has_text,
            'resolved_path': target_path,
            'width': 0,
            'height': 0,
            'size_bytes': size_bytes
        }

    # 2. Decodability & dimensions check
    try:
        with Image.open(full_path) as img:
            img.verify()
        with Image.open(full_path) as img:
            width, height = img.size
    except Exception as e:
        return {
            'status': 'missing',
            'reason': f'undecodable_corrupt_image ({str(e)})',
            'has_embedded_text': has_text,
            'resolved_path': target_path,
            'width': 0,
            'height': 0,
            'size_bytes': size_bytes
        }

    if width < MIN_IMAGE_DIM[0] or height < MIN_IMAGE_DIM[1]:
        return {
            'status': 'missing',
            'reason': f'smaller_than_min_dim ({width}x{height} < {MIN_IMAGE_DIM[0]}x{MIN_IMAGE_DIM[1]})',
            'has_embedded_text': has_text,
            'resolved_path': target_path,
            'width': width,
            'height': height,
            'size_bytes': size_bytes
        }

    # 3. Manual override check (missing status can NEVER be overridden)
    matched_override = overrides.get(key) or overrides.get(orig_key)
    if matched_override:
        ov_status = matched_override.get('status_override', 'ok')
        ov_reason = matched_override.get('reason', 'manual_override')
        return {
            'status': ov_status,
            'reason': ov_reason,
            'has_embedded_text': has_text,
            'resolved_path': target_path,
            'width': width,
            'height': height,
            'size_bytes': size_bytes
        }

    return {
        'status': 'ok',
        'reason': 'valid_image_passed_checks',
        'has_embedded_text': has_text,
        'resolved_path': target_path,
        'width': width,
        'height': height,
        'size_bytes': size_bytes
    }
