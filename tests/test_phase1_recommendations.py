import os
import sys
import json
import py_compile
from datetime import date

sys.path.insert(0, os.path.abspath("."))

# Set test environment
os.environ["SMARTAGRI_TEST_MODE"] = "1"

print("--- 1. Checking py_compile on all python files ---")
py_files = []
for root, dirs, files in os.walk("."):
    if any(ign in root for ign in ["node_modules", ".git", "__pycache__", "_backup", "dist", ".venv", "scratch"]):
        continue
    for f in files:
        if f.endswith(".py"):
            py_path = os.path.join(root, f)
            py_files.append(py_path)
            py_compile.compile(py_path, doraise=True)
print(f"Verified {len(py_files)} Python files compiled with zero syntax errors.")

print("\n--- 2. Checking all JSON files load properly ---")
json_files = []
for root, dirs, files in os.walk("data"):
    for f in files:
        if f.endswith(".json"):
            j_path = os.path.join(root, f)
            json_files.append(j_path)
            with open(j_path, "r", encoding="utf-8") as fp:
                json.load(fp)
print(f"Verified {len(json_files)} project data JSON files loaded successfully.")

print("\n--- 3. Running multi-district temporal recommendation tests via Flask test client ---")
from app import app, KARNATAKA_DISTRICT_SEASON_CROPS
from models.agri_calendar_service import (
    normalize_crop_name, get_district_institution, get_sowing_status,
    load_sowing_config, PERENNIAL_CROPS
)

client = app.test_client()

# 25 dates: 1st and 15th of every month, plus 10 Jan
test_dates = [date(2026, 1, 10)]
for m in range(1, 13):
    test_dates.append(date(2026, m, 1))
    test_dates.append(date(2026, m, 15))
test_dates.sort()

# All 31 Karnataka districts
districts = sorted([d for d in KARNATAKA_DISTRICT_SEASON_CROPS.keys() if d != "Chamarajanagar"])
assert len(districts) == 31, f"Expected 31 districts, got {len(districts)}"

shortage_records = []
sample_printouts = []
total_runs = 0
passed_runs = 0

for test_date in test_dates:
    os.environ["SMARTAGRI_TEST_DATE"] = test_date.isoformat()
    
    # Season resolution matching app
    current_m = test_date.month
    if 6 <= current_m <= 10:
        season = "Kharif"
    elif current_m in [11, 12, 1, 2]:
        season = "Rabi"
    else:
        season = "Zaid"
    
    season_l = season.lower()

    for district in districts:
        total_runs += 1
        univ_name, kvk_name = get_district_institution(district)
        
        # Valid candidate crops from KARNATAKA_DISTRICT_SEASON_CROPS
        dist_raw_crops = KARNATAKA_DISTRICT_SEASON_CROPS.get(district, {}).get(season_l, [])
        dist_canonical_crops = set()
        for c in dist_raw_crops:
            canon = normalize_crop_name(c)
            if canon not in PERENNIAL_CROPS:
                dist_canonical_crops.add(canon)

        resp = client.post("/predict_crop", data={
            "district": district,
            "season": season,
            "nitrogen": "60",
            "phosphorus": "40",
            "potassium": "30",
            "ph": "6.8"
        })
        
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code} for {district} on {test_date}"

        # Test session output
        with client.session_transaction() as sess:
            top_crops = sess.get("top_crops", [])
            pref_reason = sess.get("preferred_crop_reason_en", "")

        # Assert exactly 3 cards (never more, never fewer)
        assert len(top_crops) == 3, f"Expected exactly 3 crops, got {len(top_crops)} for {district} on {test_date}"
        
        # Assert no duplicates
        crop_keys = [c["crop_key"] for c in top_crops]
        assert len(crop_keys) == len(set(crop_keys)), f"Duplicate crops in recommendation: {crop_keys}"

        # Assert no crop outside district list
        for c in top_crops:
            ck = c["crop_key"]
            assert ck in dist_canonical_crops, (
                f"Crop {ck} for {district} on {test_date} ({season}) is outside district list {dist_canonical_crops}"
            )
            
            # Assert no passed or not_yet_open crop
            c_status = c.get("sowing_status")
            assert c_status in ["open", "closing_soon", "late_sowing"], (
                f"Crop {ck} in {district} on {test_date} has non-sowable status: {c_status}"
            )
            
            # Assert note shows correct university and KVK
            assert c.get("university") == univ_name, f"Expected univ {univ_name}, got {c.get('university')}"
            assert c.get("kvk") == kvk_name, f"Expected kvk {kvk_name}, got {c.get('kvk')}"

        # Assert rainfall sentence omitted when null
        from app import get_district_monthly_rainfall
        rain_val = get_district_monthly_rainfall(district, test_date.month)
        if rain_val is None:
            assert "Monthly normal:" not in pref_reason, f"Rainfall sentence present for null normal in {district} on {test_date}: {pref_reason}"

        if len(top_crops) < 3:
            shortage_records.append((district, test_date.isoformat(), season, len(top_crops), crop_keys))

        if test_date in [date(2026, 1, 10), date(2026, 7, 10), date(2026, 9, 15), date(2026, 11, 21), date(2026, 12, 15)] and district in ["Dharwad", "Bidar", "Kolar", "Mandya", "Bagalkot", "Kodagu"]:
            crops_str = ", ".join([f"{c['crop_key']} ({c.get('final_score', c.get('composite_match'))}% - {c.get('sowing_status')} - {c.get('sowing_days_left', 0)}d left)" for c in top_crops]) or "None"
            sample_printouts.append((district, test_date.isoformat(), crops_str))

        passed_runs += 1

print(f"\nAll {passed_runs}/{total_runs} district-date simulation points PASSED successfully!")
print(f"Total (district, date) combinations with < 3 sowable crops: {len(shortage_records)}")

print("\n--- Sample District | Date | Crops | Scores | Status Table ---")
for p in sample_printouts:
    print(f"{p[0]:<15} | {p[1]} | {p[2]}")

print("\n--- Sample Pairs with Fewer Than 3 Crops ---")
for s in shortage_records[:15]:
    print(f"District: {s[0]:<15} | Date: {s[1]} | Season: {s[2]:<6} | Count: {s[3]} | Crops: {s[4]}")
