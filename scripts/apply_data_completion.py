import json
import csv
import os
import re

# Load base crops config from scratch/tune_windows
import sys
sys.path.insert(0, os.path.abspath("."))
from scratch.tune_windows import crops_config, district_season_crops, zone_definitions

# 1. Write data/sowing_windows_config.json
sowing_config = {
    "_comment": "Karnataka Regional Sowing Windows, Crop Durations and Seasonal Boundaries. All entries flagged with needs_verification: true pending user/expert sign-off.",
    "reference_authority": "Package of Practices - UAS Bangalore, UAS Dharwad, UAS Raichur, KSNUAHS Shivamogga",
    "zone_definitions": zone_definitions,
    "crops": crops_config
}

with open("data/sowing_windows_config.json", "w", encoding="utf-8") as f:
    json.dump(sowing_config, f, indent=2)
print("Updated data/sowing_windows_config.json")

# 2. Write data/added_for_review.csv
csv_path = "data/added_for_review.csv"
fieldnames = [
    "crop", "season", "start_month", "start_day", "end_month", "end_day",
    "late_sowing_end_month", "late_sowing_end_day", "duration_days_min", "duration_days_max",
    "is_transplanted", "nursery_duration_days", "ideal_temp_min", "ideal_temp_max",
    "ideal_humidity_min", "ideal_humidity_max", "applicable_zones",
    "needs_verification", "confidence", "source_authority"
]

rows = []
for crop_key, seasons in sorted(crops_config.items()):
    for season_name, data in sorted(seasons.items()):
        zones_str = "; ".join(data.get("applicable_zones", [])) if data.get("applicable_zones") else "ALL"
        row = {
            "crop": crop_key,
            "season": season_name,
            "start_month": data.get("start_month", ""),
            "start_day": data.get("start_day", ""),
            "end_month": data.get("end_month", ""),
            "end_day": data.get("end_day", ""),
            "late_sowing_end_month": data.get("late_sowing_end_month", ""),
            "late_sowing_end_day": data.get("late_sowing_end_day", ""),
            "duration_days_min": data.get("duration_days_min", ""),
            "duration_days_max": data.get("duration_days_max", ""),
            "is_transplanted": data.get("is_transplanted", False),
            "nursery_duration_days": data.get("nursery_duration_days", 0),
            "ideal_temp_min": data.get("ideal_temp_min", ""),
            "ideal_temp_max": data.get("ideal_temp_max", ""),
            "ideal_humidity_min": data.get("ideal_humidity_min", ""),
            "ideal_humidity_max": data.get("ideal_humidity_max", ""),
            "applicable_zones": zones_str,
            "needs_verification": True,
            "confidence": data.get("confidence", "high"),
            "source_authority": "Package of Practices - UAS Bangalore, UAS Dharwad, UAS Raichur, KSNUAHS Shivamogga"
        }
        rows.append(row)

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
print(f"Generated {csv_path} with {len(rows)} entries.")

# 3. Update models/agri_calendar_service.py
with open("models/agri_calendar_service.py", "r", encoding="utf-8") as f:
    cal_code = f.read()

# Update PERENNIAL_CROPS: remove ginger, turmeric
new_perennials = '''PERENNIAL_CROPS = {
    "arecanut", "coconut", "cashew", "mango", "mulberry", "coffee",
    "sugarcane", "flowers", "fodder"
}'''
cal_code = re.sub(r'PERENNIAL_CROPS\s*=\s*\{[^}]*\}', new_perennials, cal_code)

# Update CROP_ALIASES to include all aliases and zaid/summer
new_aliases = '''CROP_ALIASES = {
    # Pulses
    "fieldbean": "fieldbeans",
    "fieldbeans": "fieldbeans",
    "avare": "fieldbeans",
    "avarekalu": "fieldbeans",
    "bengalgram": "chickpea",
    "bengal_gram": "chickpea",
    "bengal gram": "chickpea",
    "chickpea": "chickpea",
    "chickpeas": "chickpea",
    "gram": "chickpea",
    "chana": "chickpea",
    "pigeonpea": "pigeonpeas",
    "pigeonpeas": "pigeonpeas",
    "redgram": "pigeonpeas",
    "red_gram": "pigeonpeas",
    "red gram": "pigeonpeas",
    "tur": "pigeonpeas",
    "arhar": "pigeonpeas",
    "green_gram": "mungbean",
    "greengram": "mungbean",
    "mungbean": "mungbean",
    "mung": "mungbean",
    "moong": "mungbean",
    "black_gram": "blackgram",
    "blackgram": "blackgram",
    "urad": "blackgram",
    "horse_gram": "horsegram",
    "horsegram": "horsegram",
    "kulthi": "horsegram",
    "huruli": "horsegram",
    "cowpea": "cowpea",
    "cowpeas": "cowpea",
    "lobia": "cowpea",
    "alasande": "cowpea",

    # Cereals & Millets
    "paddy": "rice",
    "rice": "rice",
    "dhan": "rice",
    "corn": "maize",
    "corn(maize)": "maize",
    "maize": "maize",
    "makka": "maize",
    "wheat": "wheat",
    "gehun": "wheat",
    "ragi": "ragi",
    "fingermillet": "ragi",
    "finger_millet": "ragi",
    "finger millet": "ragi",
    "jowar": "jowar",
    "sorghum": "jowar",
    "bajra": "bajra",
    "pearlmillet": "bajra",
    "pearl millet": "bajra",

    # Oilseeds & Cash crops
    "groundnut": "groundnut",
    "groundnuts": "groundnut",
    "peanut": "groundnut",
    "peanuts": "groundnut",
    "groundnut(peanut)": "groundnut",
    "sunflower": "sunflower",
    "cotton": "cotton",
    "soybean": "soybean",
    "soybeans": "soybean",
    "sugarcane": "sugarcane",
    "sesame": "sesamum",
    "sesamum": "sesamum",
    "til": "sesamum",
    "castor": "castor",
    "mustard": "mustard",

    # Spices & Cash
    "turmeric": "turmeric",
    "arisina": "turmeric",
    "haldi": "turmeric",
    "ginger": "ginger",
    "shunti": "ginger",
    "adrak": "ginger",

    # Vegetables & Fruits
    "tomato": "tomato",
    "potato": "potato",
    "onion": "onion",
    "chilli": "chilli",
    "chili": "chilli",
    "chillies": "chilli",
    "capsicum": "capsicum",
    "watermelon": "watermelon",
    "muskmelon": "muskmelon",
    "vegetables": "vegetables",

    # Seasons
    "zaid": "summer",
    "summer": "summer",

    # Kannada Script Aliases
    "ಕಡಲೆಕಾಯಿ": "groundnut",
    "ಶೇಂಗಾ": "groundnut",
    "ಕಡಲೆಕಾಯಿ(ಶೇಂಗಾ)": "groundnut",
    "ಭತ್ತ": "rice",
    "ಬತ್ತ": "rice",
    "ಮೆಕ್ಕೆಜೋಳ": "maize",
    "ಮಕ್ಕಾ": "maize",
    "ಗೋಧಿ": "wheat",
    "ರಾಗಿ": "ragi",
    "ಜೋಳ": "jowar",
    "ಸಜ್ಜೆ": "bajra",
    "ಸೂರ್ಯಕಾಂತಿ": "sunflower",
    "ಹತ್ತಿ": "cotton",
    "ಕಪಾಸ್": "cotton",
    "ಸೋಯಾಬೀನ್": "soybean",
    "ಕಡಲೆ": "chickpea",
    "ತೊಗರಿ": "pigeonpeas",
    "ತೊಗರಿಬೇಳೆ": "pigeonpeas",
    "ಹೆಸರು": "mungbean",
    "ಹೆಸರುಕಾಳು": "mungbean",
    "ಉದ್ದು": "blackgram",
    "ಉದ್ದಿನಕಾಳು": "blackgram",
    "ಹುರುಳಿ": "horsegram",
    "ಅಲಸಂದಿ": "cowpea",
    "ಅಲಸಂದೆ": "cowpea",
    "ಕಬ್ಬು": "sugarcane",
    "ಟೊಮೆಟೊ": "tomato",
    "ಟೊಮೇಟೊ": "tomato",
    "ಆಲೂಗಡ್ಡೆ": "potato",
    "ಈರುಳ್ಳಿ": "onion",
    "ಮೆಣಸಿನಕಾಯಿ": "chilli",
    "ಶುಂಠಿ": "ginger",
    "ಅರಿಶಿನ": "turmeric",
    "ಕಲ್ಲಂಗಡಿ": "watermelon",
    "ತರಕಾರಿಗಳು": "vegetables",

    # Hindi Script Aliases
    "मूंगफली": "groundnut",
    "धान": "rice",
    "चावल": "rice",
    "मक्का": "maize",
    "गेहूं": "wheat",
    "गेहू": "wheat",
    "रागी": "ragi",
    "ज्वार": "jowar",
    "बाजरा": "bajra",
    "सूरजमुखी": "sunflower",
    "कपास": "cotton",
    "सोयाबीन": "soybean",
    "चना": "chickpea",
    "अरहर": "pigeonpeas",
    "तुअर": "pigeonpeas",
    "मूंग": "mungbean",
    "उड़द": "blackgram",
    "कुलथी": "horsegram",
    "लोबिया": "cowpea",
    "गन्ना": "sugarcane",
    "टमाटर": "tomato",
    "आलू": "potato",
    "प्याज": "onion",
    "मिर्च": "chilli",
    "अदरक": "ginger",
    "हल्दी": "turmeric",
    "तरबूज": "watermelon",
    "सब्जियां": "vegetables"
}'''

cal_code = re.sub(r'CROP_ALIASES\s*=\s*\{.*?\n\}', new_aliases, cal_code, flags=re.DOTALL)

# Update normalize_crop_name to avoid false positive substring matches on short English aliases
old_norm = '''    # Substring check for Kannada/Hindi names
    for alias, canonical in CROP_ALIASES.items():
        if alias in c_raw:
            return canonical'''

new_norm = '''    # Substring check for Kannada/Hindi script names (non-ASCII only)
    for alias, canonical in CROP_ALIASES.items():
        if not alias.isascii() and alias in c_raw:
            return canonical'''

cal_code = cal_code.replace(old_norm, new_norm)

with open("models/agri_calendar_service.py", "w", encoding="utf-8") as f:
    f.write(cal_code)
print("Updated models/agri_calendar_service.py")

# 4. Update templates/index.html
with open("templates/index.html", "r", encoding="utf-8") as f:
    html_code = f.read()

html_code = html_code.replace("<!-- Top 2-3 Regionally Suited Crops", "<!-- Top 3 Regionally Suited Crops")
html_code = html_code.replace('data-en="🌾 Top 2-3 Crops Grown in This District & Weather Match:"', 'data-en="🌾 Top 3 Crops Grown in This District & Weather Match:"')
html_code = html_code.replace('🌾 Top 2-3 Crops Grown in This District & Weather Match:', '🌾 Top 3 Crops Grown in This District & Weather Match:')

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(html_code)
print("Updated templates/index.html")

# 5. Update app.py KARNATAKA_DISTRICT_SEASON_CROPS and ensure hard cap slicing
with open("app.py", "r", encoding="utf-8") as f:
    app_code = f.read()

# Build serialized KARNATAKA_DISTRICT_SEASON_CROPS code
dist_lines = ["KARNATAKA_DISTRICT_SEASON_CROPS = {"]
for d, s in sorted(district_season_crops.items()):
    dist_lines.append(f"    '{d}': {{")
    for s_name in ['kharif', 'rabi', 'zaid']:
        crops_arr = s.get(s_name, [])
        crops_str = ", ".join([f"'{c}'" for c in crops_arr])
        dist_lines.append(f"        '{s_name}': [{crops_str}],")
    dist_lines[-1] = dist_lines[-1].rstrip(',')  # strip last comma of season
    dist_lines.append("    },")
dist_lines[-1] = dist_lines[-1].rstrip(',')
dist_lines.append("}")
new_dist_crops_code = "\n".join(dist_lines)

# Replace KARNATAKA_DISTRICT_SEASON_CROPS in app.py
pattern = r'KARNATAKA_DISTRICT_SEASON_CROPS\s*=\s*\{.*?\n\}'
app_code = re.sub(pattern, new_dist_crops_code, app_code, flags=re.DOTALL)

# Ensure top_crops = top_crops[:3] before rendering
if "top_crops = top_crops[:3]" not in app_code:
    app_code = app_code.replace("top_crops.append({", "top_crops.append({")
    app_code = app_code.replace("        # Primary recommended crop is the #1 Most Preferred Crop",
                                "        # Hard cap: guarantee exactly at most 3 crops\n        top_crops = top_crops[:3]\n\n        # Primary recommended crop is the #1 Most Preferred Crop")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)
print("Updated app.py")
