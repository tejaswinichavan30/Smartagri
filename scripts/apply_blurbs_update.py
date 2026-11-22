import re
import sys
sys.path.insert(0, '.')

from scripts.audit_all_facts import facts

with open('translations.py', 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = "CROP_WEATHER_PROFILES = {"
end_marker = "def evaluate_crop_weather_suitability"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx)

if start_idx == -1 or end_idx == -1:
    raise ValueError("Could not find CROP_WEATHER_PROFILES block bounds")

header = content[:start_idx]
block = content[start_idx:end_idx]
footer = content[end_idx:]

for crop, dict_facts in facts.items():
    # Search for crop inside block
    # Pattern: '{crop}': { ... 'weather_reason': { ... } ... }
    crop_pattern = re.compile(
        rf"('{crop}':\s*\{{[^}}]*?'weather_reason':\s*\{{)[^}}]*(\}})",
        re.DOTALL
    )
    en_val = dict_facts['en'].replace("'", "\\'")
    kn_val = dict_facts['kn'].replace("'", "\\'")
    hi_val = dict_facts['hi'].replace("'", "\\'")
    
    new_reason = (
        f"\n            'en': '{en_val}',"
        f"\n            'kn': '{kn_val}',"
        f"\n            'hi': '{hi_val}'\n        "
    )
    
    block, count = crop_pattern.subn(rf"\g<1>{new_reason}\g<2>", block, count=1)
    if count == 0:
        print(f"FAILED inside block for: {crop}")
    else:
        print(f"Successfully updated {crop} inside block")

# Also update fallback weather_reason inside footer
fallback_pattern = re.compile(
    r"('weather_reason':\s*\{\s*'en':\s*'[^']*?',\s*'kn':\s*'[^']*?',\s*'hi':\s*'[^']*?'\s*\})",
    re.DOTALL
)
fallback_replacement = (
    "'weather_reason': {\n"
    "            'en': 'Versatile agricultural crop cultivated for regional food security and farm income.',\n"
    "            'kn': 'ಪ್ರಾದೇಶಿಕ ಆಹಾರ ಭದ್ರತೆ ಮತ್ತು ರೈತರ ಆದಾಯಕ್ಕಾಗಿ ಬೆಳೆಯಲಾಗುವ ಪ್ರಮುಖ ಕೃಷಿ ಬೆಳೆ.',\n"
    "            'hi': 'क्षेत्रीय खाद्य सुरक्षा और कृषि आय के लिए उगाई जाने वाली उपयोगी कृषि फसल।'\n"
    "        }"
)
footer, fb_count = fallback_pattern.subn(fallback_replacement, footer, count=1)
print(f"Fallback updated count: {fb_count}")

new_content = header + block + footer
with open('translations.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("translations.py written successfully!")
