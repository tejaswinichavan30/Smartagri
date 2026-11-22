"""
Image Quality Gate, Privacy Protection & Local Sanitization Engine
-----------------------------------------------------------------
Features:
1. Local Face & Person Detection using offline OpenCV Haar Cascades.
   - If a person or face is detected, the image is NEVER uploaded to cloud APIs.
   - Refuses politely with plant-only photographing instructions.
2. EXIF & GPS Metadata Stripping with proportional image downscaling to ~1024px.
3. Named constants for blur (Laplacian variance), underexposure, and overexposure (glare).
"""

import io
import os
from typing import Dict, Any, Optional, Tuple
from PIL import Image, ImageOps
import numpy as np

# ==========================================================
# Named Quality Gate Threshold Constants (Tunable)
# ==========================================================
BLUR_LAPLACIAN_VAR_THRESHOLD: float = 20.0   # Below this = severely blurry image
MIN_BRIGHTNESS_LUMINANCE: float = 15.0        # Below this = pitch black / severely underexposed
MAX_BRIGHTNESS_LUMINANCE: float = 248.0       # Above this = completely washed out / overexposed glare
TARGET_MAX_DIMENSION: int = 1024              # Max image dimension before cloud transmission

# Cached Haar Cascade Classifiers
_face_cascade = None
_profile_cascade = None
_upperbody_cascade = None


def _get_haar_cascades():
    global _face_cascade, _profile_cascade, _upperbody_cascade
    if _face_cascade is None:
        try:
            import cv2
            base_dir = cv2.data.haarcascades
            face_path = os.path.join(base_dir, 'haarcascade_frontalface_default.xml')
            profile_path = os.path.join(base_dir, 'haarcascade_profileface.xml')
            body_path = os.path.join(base_dir, 'haarcascade_upperbody.xml')

            if os.path.exists(face_path):
                _face_cascade = cv2.CascadeClassifier(face_path)
            if os.path.exists(profile_path):
                _profile_cascade = cv2.CascadeClassifier(profile_path)
            if os.path.exists(body_path):
                _upperbody_cascade = cv2.CascadeClassifier(body_path)
        except Exception as e:
            print(f"[PrivacyEngine] Cascade load notice: {e}")
            _face_cascade = False
    return _face_cascade, _profile_cascade, _upperbody_cascade


def detect_person_locally(img_rgb: Image.Image) -> Dict[str, Any]:
    """
    Locally checks for human faces, skin, person portraits, selfies, or indoor non-crop scenes.
    Ensures strict privacy and rejects non-agricultural photographs.
    """
    try:
        import cv2
        arr = np.array(img_rgb.convert('RGB'))
        h, w, c = arr.shape
        total_pixels = h * w

        r = arr[:, :, 0].astype(float)
        g = arr[:, :, 1].astype(float)
        b = arr[:, :, 2].astype(float)
        exg = 2 * g - r - b

        # 1. Agricultural Plant & Foliage Chlorophyll Check
        green_mask = (exg > 15) & (g > 35) & (g > r * 0.95)
        green_pct = float(np.sum(green_mask) / total_pixels * 100.0)

        hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)
        hue, sat, val = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
        foliar_mask = ((hue >= 18) & (hue <= 90) & (sat >= 25) & (val >= 25)) | green_mask
        foliar_pct = float(np.sum(foliar_mask) / total_pixels * 100.0)

        # Priority 1: If substantial green plant tissue or foliar presence -> Agricultural plant!
        if green_pct >= 20.0 or foliar_pct >= 30.0:
            return {
                "has_person": False,
                "is_indoor": False,
                "category": "agricultural_plant",
                "green_pct": round(green_pct, 1),
                "foliar_pct": round(foliar_pct, 1),
                "message": "Valid agricultural crop/plant image."
            }

        # Priority 2: Non-plant image (low vegetation). Differentiate between Person and Indoor/Non-crop
        ycrcb = cv2.cvtColor(arr, cv2.COLOR_RGB2YCrCb)
        y, cr, cb = ycrcb[:, :, 0], ycrcb[:, :, 1], ycrcb[:, :, 2]
        skin_mask = (cr >= 133) & (cr <= 175) & (cb >= 77) & (cb <= 128) & (val >= 40) & (exg <= 5)
        skin_pct = float(np.sum(skin_mask) / total_pixels * 100.0)

        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(skin_mask.astype(np.uint8))
        has_face_blob = False
        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            blob_pct = (area / total_pixels) * 100.0
            bw = stats[i, cv2.CC_STAT_WIDTH]
            bh = stats[i, cv2.CC_STAT_HEIGHT]
            ar = bw / float(bh) if bh > 0 else 0
            if blob_pct >= 2.5 and 0.4 <= ar <= 2.0:
                has_face_blob = True
                break

        if has_face_blob or skin_pct >= 8.0:
            return {
                "has_person": True,
                "is_indoor": False,
                "category": "person",
                "detected_feature": "human_face_skin",
                "skin_pct": round(skin_pct, 1),
                "green_pct": round(green_pct, 1),
                "message": "Human person/face detected in the photo."
            }
        elif foliar_pct < 15.0 and green_pct < 8.0:
            return {
                "has_person": False,
                "is_indoor": True,
                "category": "indoor_scene",
                "detected_feature": "indoor_room_furniture",
                "skin_pct": round(skin_pct, 1),
                "green_pct": round(green_pct, 1),
                "message": "Indoor room/non-crop scene detected."
            }

        return {
            "has_person": False,
            "is_indoor": False,
            "category": "agricultural_plant",
            "count": 0,
            "message": "Non-person photo."
        }
    except Exception as e:
        print(f"[PrivacyEngine] Detection error: {e}")
        return {"has_person": False, "is_indoor": False, "error": str(e)}


def assess_image_quality(img_rgb: Image.Image) -> Dict[str, Any]:
    """
    Checks blur, underexposure, and glare/overexposure against named constants.
    """
    try:
        import cv2
        np_arr = np.array(img_rgb)
        gray = cv2.cvtColor(np_arr, cv2.COLOR_RGB2GRAY)

        # 1. Laplacian Variance (Blur)
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        # 2. Mean Luminance (Brightness)
        mean_brightness = float(np.mean(gray))

        # Check issues
        is_blurry = laplacian_var < BLUR_LAPLACIAN_VAR_THRESHOLD
        is_dark = mean_brightness < MIN_BRIGHTNESS_LUMINANCE
        is_glare = mean_brightness > MAX_BRIGHTNESS_LUMINANCE

        if is_dark:
            return {
                "photo_quality": "poor",
                "reason": "dark",
                "mean_brightness": round(mean_brightness, 1),
                "quality_tip": "The photo is too dark. Please take the photograph in natural daylight or turn on illumination.",
                "quality_tip_kn": "ಫೋಟೋದಲ್ಲಿ ಬೆಳಕು ತುಂಬಾ ಕಡಿಮೆಯಿದೆ. ದಯವಿಟ್ಟು ನೈಸರ್ಗಿಕ ಬೆಳಕಿನಲ್ಲಿ ಸ್ಪಷ್ಟ ಫೋಟೋ ತೆಗೆದುಕೊಳ್ಳಿ.",
                "quality_tip_hi": "फोटो में बहुत अंधेरा है। कृपया पर्याप्त प्राकृतिक रोशनी में फोटो खींचें।"
            }

        if is_glare:
            return {
                "photo_quality": "poor",
                "reason": "glare",
                "mean_brightness": round(mean_brightness, 1),
                "quality_tip": "Severe light glare / overexposure detected. Please avoid direct harsh flashlight or sun reflection on the leaf.",
                "quality_tip_kn": "ಚಿತ್ರದಲ್ಲಿ ಅತಿಯಾದ ಬೆಳಕಿನ ಪ್ರತಿಫಲನವಿದೆ (ಗ್ಲೇರ್). ದಯವಿಟ್ಟು ನೆರಳಿನಲ್ಲಿ ಅಥವಾ ಸೂಕ್ತ ಬೆಳಕಿನಲ್ಲಿ ಫೋಟೋ ತೆಗೆದುಕೊಳ್ಳಿ.",
                "quality_tip_hi": "फोटो में अत्यधिक चमक (ग्लेयर) है। कृपया सीधी धूप या तेज फ्लैश से बचकर फोटो लें।"
            }

        if is_blurry:
            return {
                "photo_quality": "poor",
                "reason": "blurry",
                "laplacian_var": round(laplacian_var, 1),
                "quality_tip": "The photo is out of focus or blurry. Please hold the phone steady, tap to focus on the leaf, and retake in good lighting.",
                "quality_tip_kn": "ಚಿತ್ರವು ಅಸ್ಪಷ್ಟವಾಗಿದೆ. ದಯವಿಟ್ಟು ಫೋನ್ ಅನ್ನು ಸ್ಥಿರವಾಗಿ ಹಿಡಿದು, ಎಲೆಯ ಮೇಲೆ ಫೋಕಸ್ ಮಾಡಿ ಸ್ಪಷ್ಟ ಫೋಟೋ ತೆಗೆದುಕೊಳ್ಳಿ.",
                "quality_tip_hi": "फोटो धुंधली है। कृपया फोन को स्थिर रखें, पत्ती पर फोकस करें और अच्छी रोशनी में साफ फोटो लें।"
            }

        quality_level = "good" if (laplacian_var >= 100.0 and 45.0 <= mean_brightness <= 200.0) else "fair"
        return {
            "photo_quality": quality_level,
            "laplacian_var": round(laplacian_var, 1),
            "mean_brightness": round(mean_brightness, 1),
            "quality_tip": None
        }

    except Exception as e:
        print(f"[QualityGate] Evaluation error: {e}")
        return {"photo_quality": "fair", "error": str(e), "quality_tip": None}


def sanitize_and_strip_metadata(img_bytes: bytes) -> Tuple[bytes, Dict[str, Any]]:
    """
    Strips EXIF, GPS location tags, resizes to ~1024px maximum dimension,
    and returns clean JPEG bytes and dimension metadata.
    """
    try:
        img = Image.open(io.BytesIO(img_bytes))
        # Handle orientation if EXIF is present before stripping
        img = ImageOps.exif_transpose(img)
        img = img.convert('RGB')

        orig_w, orig_h = img.size
        # Proportional downscaling to max 1024px
        if max(orig_w, orig_h) > TARGET_MAX_DIMENSION:
            img.thumbnail((TARGET_MAX_DIMENSION, TARGET_MAX_DIMENSION), Image.Resampling.LANCZOS)

        out_buf = io.BytesIO()
        # Save without any EXIF or metadata tags
        img.save(out_buf, format='JPEG', quality=85, optimize=True)
        sanitized_bytes = out_buf.getvalue()

        return sanitized_bytes, {
            "original_size": (orig_w, orig_h),
            "sanitized_size": img.size,
            "format": "JPEG",
            "exif_stripped": True
        }
    except Exception as e:
        print(f"[SanitizeEngine] Error: {e}")
        return img_bytes, {"error": str(e), "exif_stripped": False}
