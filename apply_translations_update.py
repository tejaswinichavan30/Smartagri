# -*- coding: utf-8 -*-
import sys
import update_translations_data

with open('translations.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update DISEASE_PANEL_TEXTS with additional messages
panel_texts_patch = '''    'crop_mismatch_message': {
        'en': "This photo doesn't look like a {crop} leaf. Please upload a clearer photo.",
        'kn': "ಈ ಫೋಟೋ {crop} ಎಲೆಯಂತೆ ಕಾಣುತ್ತಿಲ್ಲ. ದಯವಿಟ್ಟು ಹೆಚ್ಚು ಸ್ಪಷ್ಟವಾದ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ.",
        'hi': "यह फोटो {crop} की पत्ती जैसी नहीं लग रही है। कृपया अधिक स्पष्ट फोटो अपलोड करें।"
    },
    'orange_detected_message': {
        'en': "Possible Citrus Greening (Huanglongbing) suspected, confirm with the horticulture department.",
        'kn': "ಸಿಟ್ರಸ್ ಗ್ರೀನಿಂಗ್ ರೋಗದ ಶಂಕೆ ಇದೆ, ದಯವಿಟ್ಟು ತೋಟಗಾರಿಕೆ ಇಲಾಖೆಯೊಂದಿಗೆ ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ.",
        'hi': "सिट्रस ग्रीनिंग रोग की संभावना है, कृपया बागवानी विभाग से पुष्टि करें।"
    },
    'orange_not_detected_message': {
        'en': "Citrus Greening (Huanglongbing) not detected. This does not mean the plant is healthy. Please consult the horticulture department.",
        'kn': "ಸಿಟ್ರಸ್ ಗ್ರೀನಿಂಗ್ ರೋಗ ಪತ್ತೆಯಾಗಿಲ್ಲ. ಇದರರ್ಥ ಸಸ್ಯವು ಸಂಪೂರ್ಣ ಆರೋಗ್ಯಕರವಾಗಿದೆ ಎಂದಲ್ಲ. ದಯವಿಟ್ಟು ತೋಟಗಾರಿಕೆ ಇಲಾಖೆಯನ್ನು ಸಂಪರ್ಕಿಸಿ.",
        'hi': "सिट्रस ग्रीनिंग (हॉन्गलोंगबिंग) रोग नहीं पाया गया। इसका अर्थ यह नहीं है कि पौधा स्वस्थ है। कृपया बागवानी विभाग से संपर्क करें।"
    },
    'squash_detected_message': {
        'en': "Possible Powdery Mildew, confirm with an expert.",
        'kn': "ಬೂದಿ ರೋಗದ ಶಂಕೆ ಇದೆ, ದಯವಿಟ್ಟು ಕೃಷಿ ತಜ್ಞರೊಂದಿಗೆ ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ.",
        'hi': "चूर्णिल फफूंद (पाउडरी मिल्ड्यू) की संभावना है, कृपया विशेषज्ञ से पुष्टि करें।"
    },
    'squash_not_detected_message': {
        'en': "Powdery Mildew not detected. This does not mean the plant is healthy. Please consult an expert.",
        'kn': "ಬೂದಿ ರೋಗ ಪತ್ತೆಯಾಗಿಲ್ಲ. ಇದರರ್ಥ ಸಸ್ಯವು ಸಂಪೂರ್ಣ ಆರೋಗ್ಯಕರವಾಗಿದೆ ಎಂದಲ್ಲ. ದಯವಿಟ್ಟು ಕೃಷಿ ತಜ್ಞರನ್ನು ಸಂಪರ್ಕಿಸಿ.",
        'hi': "चूर्णिल फफूंद (पाउडरी मिल्ड्यू) नहीं पाया गया। इसका अर्थ यह नहीं है कि पौधा स्वस्थ है। कृपया किसी विशेषज्ञ से सलाह लें।"
    },'''

if "'crop_mismatch_message'" not in content:
    content = content.replace("'uncertain_diagnosis_message': {", panel_texts_patch + "\n    'uncertain_diagnosis_message': {")

# 2. Insert EXTRA_CROP_SAMPLES before closing of CROP_DISEASE_SAMPLES
target_close = "        }\n    ]\n}\n\n\ndef get_crop_disease_samples"
replacement_close = "        },\n" + update_translations_data.EXTRA_CROP_SAMPLES + "}\n\n\ndef get_crop_disease_samples"
if "'orange': [" not in content:
    content = content.replace(target_close, replacement_close)

# 3. Update get_crop_disease_samples to use exact normalize_disease_crop
old_func_start = content.find("def get_crop_disease_samples")
new_func = '''def get_crop_disease_samples(crop_name: str, lang: str = 'en') -> list:
    """
    Returns 3-4 sample disease reference objects with localized names,
    sample illustrations/images, and field management tips for the requested crop.
    Reference-only crops are clearly identified, with verified_by_expert flag.
    Confidence scores are NOT included on reference cards.
    """
    crop_k = normalize_disease_crop(crop_name)
    if not crop_k:
        crop_k = 'tomato'

    raw_samples = CROP_DISEASE_SAMPLES.get(crop_k)
    if not raw_samples:
        raw_samples = CROP_DISEASE_SAMPLES.get('tomato', [])
        
    is_supported = is_disease_diagnosis_supported(crop_k)
    info = get_crop_support(crop_k)
    status = info.get('status', 'reference_only')
    
    localized_samples = []
    for item in raw_samples:
        d_name = item.get(f'disease_name_{lang}', item.get('disease_name_en'))
        symptoms = item.get(f'symptoms_{lang}', item.get('symptoms_en'))
        treatment = item.get(f'treatment_{lang}', item.get('treatment_en'))
        is_healthy = (item.get('id') == 'healthy' or 'healthy' in item.get('id', ''))
        
        # If crop is disease_only (e.g. Orange, Squash), never flag a sample as healthy
        if status == 'disease_only':
            is_healthy = False
            
        localized_samples.append({
            'id': item['id'],
            'name': d_name,
            'name_en': item.get('disease_name_en'),
            'name_kn': item.get('disease_name_kn'),
            'name_hi': item.get('disease_name_hi'),
            'image': item['image'],
            'symptoms': symptoms,
            'treatment': treatment,
            'verified_by_expert': item.get('verified_by_expert', False),
            'is_healthy': is_healthy,
            'is_diagnosis_supported': is_supported
        })

    return localized_samples
'''
if old_func_start != -1:
    content = content[:old_func_start] + new_func

with open('translations.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Applied updates to translations.py successfully.")
