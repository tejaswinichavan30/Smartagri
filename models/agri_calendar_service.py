"""
Agri Calendar & Sowing Window Engine (Karnataka Package of Practices Aligned)
Handles seasonal status (open, closing_soon, late_sowing, passed, not_started) and dynamic harvest date computation.
"""

import os
import json
import re
from datetime import date, timedelta
from typing import Dict, Any, Tuple, Optional

MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

MONTH_NAMES_KN = [
    "", "ಜನವರಿ", "ಫೆಬ್ರವರಿ", "ಮಾರ್ಚ್", "ಏಪ್ರಿಲ್", "ಮೇ", "ಜೂನ್",
    "ಜುಲೈ", "ಆಗಸ್ಟ್", "ಸೆಪ್ಟೆಂಬರ್", "ಅಕ್ಟೋಬರ್", "ನವೆಂಬರ್", "ಡಿಸೆಂಬರ್"
]

MONTH_NAMES_HI = [
    "", "जनवरी", "फरवरी", "मार्च", "अप्रैल", "मई", "जून",
    "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"
]

# District to University and ICAR-KVK Authority Mapping (All 31 Karnataka Districts)
DISTRICT_INSTITUTIONS: Dict[str, Tuple[str, str]] = {
    # UAS Bangalore (GKVK) - 10 Districts
    "Kolar": ("UAS Bangalore (GKVK)", "ICAR-KVK Kolar"),
    "Bengaluru Urban": ("UAS Bangalore (GKVK)", "ICAR-KVK Bengaluru Urban"),
    "Bengaluru Rural": ("UAS Bangalore (GKVK)", "ICAR-KVK Bengaluru Rural"),
    "Chikkaballapura": ("UAS Bangalore (GKVK)", "ICAR-KVK Chikkaballapura"),
    "Ramanagara": ("UAS Bangalore (GKVK)", "ICAR-KVK Ramanagara"),
    "Mandya": ("UAS Bangalore (GKVK)", "ICAR-KVK Mandya"),
    "Mysuru": ("UAS Bangalore (GKVK)", "ICAR-KVK Mysuru"),
    "Tumakuru": ("UAS Bangalore (GKVK)", "ICAR-KVK Tumakuru"),
    "Hassan": ("UAS Bangalore (GKVK)", "ICAR-KVK Hassan"),
    "Chamarajanagara": ("UAS Bangalore (GKVK)", "ICAR-KVK Chamarajanagara"),

    # UAS Dharwad - 7 Districts
    "Dharwad": ("UAS Dharwad", "ICAR-KVK Dharwad"),
    "Belagavi": ("UAS Dharwad", "ICAR-KVK Belagavi"),
    "Bagalkot": ("UAS Dharwad", "ICAR-KVK Bagalkot"),
    "Gadag": ("UAS Dharwad", "ICAR-KVK Gadag"),
    "Haveri": ("UAS Dharwad", "ICAR-KVK Haveri"),
    "Uttara Kannada": ("UAS Dharwad", "ICAR-KVK Uttara Kannada"),
    "Vijayapura": ("UAS Dharwad", "ICAR-KVK Vijayapura"),

    # UAS Raichur - 7 Districts
    "Raichur": ("UAS Raichur", "ICAR-KVK Raichur"),
    "Kalaburagi": ("UAS Raichur", "ICAR-KVK Kalaburagi"),
    "Yadgir": ("UAS Raichur", "ICAR-KVK Yadgir"),
    "Bidar": ("UAS Raichur", "ICAR-KVK Bidar"),
    "Ballari": ("UAS Raichur", "ICAR-KVK Ballari"),
    "Koppal": ("UAS Raichur", "ICAR-KVK Koppal"),
    "Vijayanagara": ("UAS Raichur", "ICAR-KVK Vijayanagara"),

    # KSNUAHS Shivamogga - 7 Districts
    "Shivamogga": ("KSNUAHS Shivamogga", "ICAR-KVK Shivamogga"),
    "Chikkamagaluru": ("KSNUAHS Shivamogga", "ICAR-KVK Chikkamagaluru"),
    "Chitradurga": ("KSNUAHS Shivamogga", "ICAR-KVK Chitradurga"),
    "Davanagere": ("KSNUAHS Shivamogga", "ICAR-KVK Davanagere"),
    "Dakshina Kannada": ("KSNUAHS Shivamogga", "ICAR-KVK Dakshina Kannada"),
    "Udupi": ("KSNUAHS Shivamogga", "ICAR-KVK Udupi"),
    "Kodagu": ("KSNUAHS Shivamogga", "ICAR-KVK Kodagu"),
}

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sowing_windows_config.json")


def get_district_institution(district: str) -> Tuple[str, str]:
    """Retrieve designated University and ICAR-KVK for any Karnataka district."""
    if not district:
        return ("State Agricultural University", "ICAR-KVK")
    d_clean = district.strip()
    for d_name, inst in DISTRICT_INSTITUTIONS.items():
        if d_name.lower() in d_clean.lower() or d_clean.lower() in d_name.lower():
            # Return ICAR-KVK [District] without village names
            return (inst[0], f"ICAR-KVK {d_name}")
    return ("State Agricultural University", f"ICAR-KVK {d_clean}")


def get_current_date(override: Optional[date] = None) -> date:
    """
    Returns the reference date.
    Date override is permitted ONLY during automated tests (via explicit parameter
    or SMARTAGRI_TEST_MODE environment variable). In production, strictly date.today().
    """
    if override is not None:
        return override
    if os.environ.get("SMARTAGRI_TEST_MODE") == "1" and os.environ.get("SMARTAGRI_TEST_DATE"):
        try:
            return date.fromisoformat(os.environ["SMARTAGRI_TEST_DATE"])
        except Exception:
            pass
    return date.today()


def load_sowing_config() -> Dict[str, Any]:
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Notice: Failed to load sowing_windows_config.json: {e}")
    return {}


# Perennial and plantation crops excluded from annual sowing recommendations
PERENNIAL_CROPS = {
    "arecanut", "coconut", "cashew", "mango", "mulberry", "coffee",
    "sugarcane", "flowers", "fodder"
}

# Crop name alias normalization (English, Kannada, Hindi, and compounds)
CROP_ALIASES = {
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
}

def normalize_crop_name(crop: str) -> str:
    """Map variants/aliases to canonical crop keys across languages and compounds."""
    if not crop:
        return ""
    c_raw = str(crop).strip()
    c_clean = c_raw.lower().replace(" ", "").replace("-", "").replace("_", "")
    # Check exact clean alias
    if c_clean in CROP_ALIASES:
        return CROP_ALIASES[c_clean]
    for alias, canonical in CROP_ALIASES.items():
        if alias.replace("_", "").replace(" ", "") == c_clean:
            return canonical

    # Strip parenthetical annotations like "(ಶೇಂಗಾ)", "(peanut)", "(rice)" and re-check
    c_no_paren = re.sub(r'\(.*?\)', '', c_raw).strip().lower().replace(" ", "").replace("-", "").replace("_", "")
    if c_no_paren and c_no_paren in CROP_ALIASES:
        return CROP_ALIASES[c_no_paren]
    for alias, canonical in CROP_ALIASES.items():
        if alias.replace("_", "").replace(" ", "") == c_no_paren:
            return canonical

    # Substring check for Kannada/Hindi script names (non-ASCII only)
    for alias, canonical in CROP_ALIASES.items():
        if not alias.isascii() and alias in c_raw:
            return canonical

    return c_raw.lower().strip()

def get_district_zone(district: str) -> Optional[str]:
    """Identify the agro-climatic zone for a given Karnataka district."""
    if not district:
        return None
    d_clean = district.strip().lower()
    zd = load_sowing_config().get("zone_definitions", {})
    for z_name, dists in zd.items():
        for d in dists:
            if d.lower() == d_clean or d.lower() in d_clean or d_clean in d.lower():
                return z_name
    return None

def format_window_label(sm: int, sd: int, em: int, ed: int, late_em: Optional[int] = None, late_ed: Optional[int] = None, lang: str = "en") -> str:
    """Generate window labels strictly from numeric month/day fields, never hand-typed strings."""
    m_names = MONTH_NAMES_KN if lang == "kn" else (MONTH_NAMES_HI if lang == "hi" else MONTH_NAMES)
    base = f"{sd:02d} {m_names[sm]} - {ed:02d} {m_names[em]}"
    if late_em and late_ed:
        if lang == "kn":
            return f"{base} (ತಡವಾದ ಬಿತ್ತನೆ {late_ed:02d} {m_names[late_em]} ವರೆಗೆ)"
        elif lang == "hi":
            return f"{base} (देर से बुवाई {late_ed:02d} {m_names[late_em]} तक)"
        else:
            return f"{base} (Late sowing up to {late_ed:02d} {m_names[late_em]})"
    return base

def get_sowing_window_data(crop: str, season: str = "rabi", district: str = "Dharwad") -> Dict[str, Any]:
    """Retrieve calibrated sowing window and duration data for a crop and district zone."""
    c_canon = normalize_crop_name(crop)
    if c_canon in PERENNIAL_CROPS:
        return {}

    cfg = load_sowing_config().get("crops", {})
    crop_entry = cfg.get(c_canon)
    if not crop_entry:
        for k, v in cfg.items():
            if k == c_canon or normalize_crop_name(k) == c_canon:
                crop_entry = v
                break

    if not crop_entry:
        return {}

    s_req = (season or "rabi").lower().strip()
    # Map zaid entries to summer
    if s_req == "zaid":
        season_key = "summer" if "summer" in crop_entry else "zaid"
    else:
        season_key = s_req

    if season_key not in crop_entry:
        return {}

    s_data = dict(crop_entry.get(season_key, {}))

    # Validate agro-climatic zone applicability if configured
    app_zones = s_data.get("applicable_zones")
    if app_zones is not None:
        dist_zone = get_district_zone(district)
        if dist_zone and dist_zone not in app_zones:
            # Crop not suitable / not configured for this district's zone
            return {}

    # Apply district override if available and valid
    dist_clean = (district or "").strip()
    overrides = s_data.get("district_overrides", {})
    for d_name, d_override in overrides.items():
        if d_name.lower() in dist_clean.lower() or dist_clean.lower() in d_name.lower():
            s_data.update(d_override)
            break

    return s_data


def get_sowing_status(crop: str, season: str = "rabi", today: Optional[date] = None, district: str = "Dharwad") -> Dict[str, Any]:
    """
    Computes sowing status against the agricultural calendar.
    Returns:
      status: 'open' | 'closing_soon' | 'late_sowing' | 'passed' | 'not_started' | 'no_window'
      days_difference: int (positive if closing in N days, negative if passed N days ago)
      window_label: str
      urgency_7d: bool
      warning_en / warning_kn / warning_hi: str
    """
    today = get_current_date(today)
    univ_name, kvk_name = get_district_institution(district)

    w_data = get_sowing_window_data(crop, season, district)
    if not w_data:
        return {
            "status": "no_window",
            "days_difference": 0,
            "window_label": "No sowing window for district zone",
            "window_label_en": "No sowing window for district zone",
            "window_label_kn": "ಜಿಲ್ಲೆಯ ವಲಯಕ್ಕೆ ಬಿತ್ತನೆ ಸಮಯ ನಿಗದಿಯಾಗಿಲ್ಲ",
            "window_label_hi": "जिले के क्षेत्र हेतु बुवाई समय निर्धारित नहीं",
            "sowing_start": None,
            "sowing_end": None,
            "warning": "",
            "warning_en": "",
            "warning_kn": "",
            "warning_hi": "",
            "urgency_7d": False,
            "needs_verification": True,
            "university": univ_name,
            "kvk": kvk_name,
            "is_transplanted": False
        }

    is_transplanted = w_data.get("is_transplanted", False)
    nursery_days = w_data.get("nursery_duration_days", 28 if is_transplanted else 0)

    sm = w_data.get("start_month", 10)
    sd = w_data.get("start_day", 1)
    em = w_data.get("end_month", 11)
    ed = w_data.get("end_day", 15)
    late_em = w_data.get("late_sowing_end_month")
    late_ed = w_data.get("late_sowing_end_day")

    window_label_en = format_window_label(sm, sd, em, ed, late_em, late_ed, "en")
    window_label_kn = format_window_label(sm, sd, em, ed, late_em, late_ed, "kn")
    window_label_hi = format_window_label(sm, sd, em, ed, late_em, late_ed, "hi")

    cur_year = today.year
    is_wrap = (em < sm) or (em == sm and ed < sd)

    if not is_wrap:
        start_date = date(cur_year, sm, sd)
        end_date = date(cur_year, em, ed)
        late_end_date = date(cur_year, late_em, late_ed) if (late_em and late_ed) else end_date
    else:
        # Cross-year window (e.g. 15 Dec to 15 Jan)
        if today.month >= sm:
            start_date = date(cur_year, sm, sd)
            end_date = date(cur_year + 1, em, ed)
            late_end_date = date(cur_year + 1, late_em, late_ed) if (late_em and late_ed) else end_date
        elif today.month <= em:
            start_date = date(cur_year - 1, sm, sd)
            end_date = date(cur_year, em, ed)
            late_end_date = date(cur_year, late_em, late_ed) if (late_em and late_ed) else end_date
        else:
            mid_month = (em + sm) / 2.0
            if today.month >= mid_month:
                start_date = date(cur_year, sm, sd)
                end_date = date(cur_year + 1, em, ed)
                late_end_date = date(cur_year + 1, late_em, late_ed) if (late_em and late_ed) else end_date
            else:
                start_date = date(cur_year - 1, sm, sd)
                end_date = date(cur_year, em, ed)
                late_end_date = date(cur_year, late_em, late_ed) if (late_em and late_ed) else end_date

    # Nursery sowing deadline for transplanted crops
    if is_transplanted:
        sow_deadline = end_date - timedelta(days=nursery_days)
    else:
        sow_deadline = end_date

    status = "open"
    days_diff = 0
    warn_en = ""
    warn_kn = ""
    warn_hi = ""

    if is_transplanted:
        if today > sow_deadline:
            status = "passed"
            days_diff = (today - sow_deadline).days
            dl_str = sow_deadline.strftime("%d %b")
            tp_str = end_date.strftime("%d %b")
            warn_en = f"⚠️ Nursery sowing deadline passed (ended {dl_str}, {days_diff} days ago). Starting nursery today cannot meet transplanting cutoff of {tp_str}; consult {kvk_name} / {univ_name}."
            warn_kn = f"⚠️ ನರ್ಸರಿ ಬಿತ್ತನೆ ಗಡುವು ಮೀರಿದೆ ({dl_str} ರಂದು ಮುಗಿದಿದೆ, {days_diff} ದಿನಗಳ ಹಿಂದೆ). ಇಂದು ನರ್ಸರಿ ಪ್ರಾರಂಭಿಸಿದರೆ {tp_str} ರೊಳಗೆ ನಾಟಿ ಅಸಾಧ್ಯ; {kvk_name} / {univ_name} ಯಲ್ಲಿ ಸಮಾಲೋಚಿಸಿ."
            warn_hi = f"⚠️ नर्सरी बुवाई की समय सीमा समाप्त ({dl_str} को समाप्त, {days_diff} दिन पहले)। आज नर्सरी शुरू करने पर {tp_str} तक रोपाई संभव नहीं; {kvk_name} / {univ_name} से परामर्श करें।"
        elif (sow_deadline - today).days <= 14 and today >= start_date - timedelta(days=nursery_days):
            status = "closing_soon"
            days_diff = (sow_deadline - today).days
            dl_str = sow_deadline.strftime("%d %b")
            tp_str = end_date.strftime("%d %b")
            warn_en = f"⏳ Nursery sowing window closing soon ({days_diff} days left until {dl_str}). Sow nursery now for timely transplanting by {tp_str}."
            warn_kn = f"⏳ ನರ್ಸರಿ ಬಿತ್ತನೆ ಸಮಯ ಶೀಘ್ರದಲ್ಲೇ ಮುಕ್ತಾಯವಾಗಲಿದೆ ({dl_str} ವರೆಗೆ {days_diff} ದಿನಗಳು ಬಾಕಿ). {tp_str} ರೊಳಗೆ ನಾಟಿ ಮಾಡಲು ತಕ್ಷಣ ನರ್ಸರಿ ಬಿತ್ತನೆ ಮಾಡಿ."
            warn_hi = f"⏳ नर्सरी बुवाई का समय जल्द समाप्त होगा ({dl_str} तक {days_diff} दिन शेष)। {tp_str} तक समय पर रोपाई हेतु तुरंत नर्सरी डालें।"
        elif today < start_date - timedelta(days=nursery_days):
            status = "not_started"
            n_start = start_date - timedelta(days=nursery_days)
            days_diff = (n_start - today).days
            st_str = n_start.strftime("%d %b")
            warn_en = f"📅 Nursery preparation begins on {st_str}. Prepare raised beds and seeds."
            warn_kn = f"📅 ನರ್ಸರಿ ಸಿದ್ಧತೆ {st_str} ರಂದು ಪ್ರಾರಂಭವಾಗುತ್ತದೆ. ಬೀಜ ಹಾಗೂ ಭೂಮಿ ಸಿದ್ಧತೆ ಮಾಡಿಕೊಳ್ಳಿ."
            warn_hi = f"📅 नर्सरी तैयारी {st_str} से शुरू होगी। बीज एवं क्यारी तैयार करें।"
        else:
            status = "open"
            days_diff = (sow_deadline - today).days
    else:
        # Direct-seeded crops (Wheat, Jowar, Chickpea, Ragi, etc.)
        if today > late_end_date:
            status = "passed"
            days_diff = (today - end_date).days
            end_str = end_date.strftime("%d %b")
            warn_en = f"⚠️ Sowing window passed (ended {end_str}). Sowing now carries high yield loss risk; consult {kvk_name} / {univ_name}."
            warn_kn = f"⚠️ ಬಿತ್ತನೆ ಸಮಯ ಮೀರಿದೆ ({end_str} ರಂದು ಮುಗಿದಿದೆ). ಈಗ ಬಿತ್ತನೆ ಮಾಡುವುದರಿಂದ ಇಳುವರಿ ಕುಂಠಿತ ಸಾಧ್ಯತೆ; {kvk_name} / {univ_name} ನಲ್ಲಿ ಸಮಾಲೋಚಿಸಿ."
            warn_hi = f"⚠️ बुवाई का समय समाप्त हो चुका है ({end_str} को समाप्त)। अब बुवाई करने से उपज हानि का जोखिम है; {kvk_name} / {univ_name} से परामर्श करें।"
        elif end_date < today <= late_end_date:
            status = "late_sowing"
            days_diff = (late_end_date - today).days
            late_str = late_end_date.strftime("%d %b")
            warn_en = f"⏳ Late sowing window active (until {late_str}, {days_diff} days left). Use recommended late-sown varieties. Consult {kvk_name}."
            warn_kn = f"⏳ ತಡವಾದ ಬಿತ್ತನೆ ಸಮಯ ಸಕ್ರಿಯವಾಗಿದೆ ({late_str} ವರೆಗೆ {days_diff} ದಿನಗಳು ಬಾಕಿ). ಶಿಫಾರಸು ಮಾಡಿದ ತಳಿಗಳನ್ನು ಬಳಸಿ. {kvk_name} ಸಂಪರ್ಕಿಸಿ."
            warn_hi = f"⏳ देर से बुवाई का समय सक्रिय ({late_str} तक {days_diff} दिन शेष)। अनुशंसित किस्मों का प्रयोग करें। {kvk_name} से परामर्श लें।"
        elif (end_date - today).days <= 14 and today >= start_date:
            status = "closing_soon"
            days_diff = (end_date - today).days
            end_str = end_date.strftime("%d %b")
            warn_en = f"⏳ Sowing window closing soon ({days_diff} days left until {end_str}). Complete sowing immediately."
            warn_kn = f"⏳ ಬಿತ್ತನೆ ಸಮಯ ಶೀಘ್ರದಲ್ಲೇ ಮುಕ್ತಾಯವಾಗಲಿದೆ ({end_str} ವರೆಗೆ {days_diff} ದಿನಗಳು ಬಾಕಿ). ತಕ್ಷಣ ಬಿತ್ತನೆ ಪೂರ್ಣಗೊಳಿಸಿ."
            warn_hi = f"⏳ बुवाई का समय जल्द समाप्त होने वाला है ({end_str} तक {days_diff} दिन शेष)। शीघ्र बुवाई पूर्ण करें।"
        elif today < start_date:
            status = "not_started"
            days_diff = (start_date - today).days
            start_str = start_date.strftime("%d %b")
            warn_en = f"📅 Sowing window begins on {start_str}. Prepare seedbed and inputs."
            warn_kn = f"📅 ಬಿತ್ತನೆ ಸಮಯ {start_str} ರಂದು ಪ್ರಾರಂಭವಾಗುತ್ತದೆ. ಬೀಜ ಹಾಗೂ ಭೂಮಿ ಸಿದ್ಧತೆ ಮಾಡಿಕೊಳ್ಳಿ."
            warn_hi = f"📅 बुवाई का समय {start_str} से शुरू होगा। खेत की तैयारी करें।"
        else:
            status = "open"
            days_diff = (end_date - today).days

    urgency_7d = (status in ["closing_soon", "late_sowing"]) and (0 <= days_diff <= 7)

    return {
        "status": status,
        "days_difference": days_diff,
        "window_label": window_label_en,
        "window_label_en": window_label_en,
        "window_label_kn": window_label_kn,
        "window_label_hi": window_label_hi,
        "sowing_start": start_date.isoformat(),
        "sowing_end": end_date.isoformat(),
        "warning": warn_en,
        "warning_en": warn_en,
        "warning_kn": warn_kn,
        "warning_hi": warn_hi,
        "urgency_7d": urgency_7d,
        "needs_verification": True,
        "university": univ_name,
        "kvk": kvk_name,
        "is_transplanted": is_transplanted
    }


def compute_harvest_range(
    crop: str,
    season: str = "rabi",
    district: str = "Dharwad",
    today: Optional[date] = None,
    planned_sowing_date: Optional[date] = None
) -> Dict[str, str]:
    """
    Computes realistic harvest range dynamically:
    (planned sowing date or today, whichever is later) + crop duration range.
    Uses unified logic for top cards and small cards.
    """
    w_data = get_sowing_window_data(crop, season, district)
    is_transplanted = w_data.get("is_transplanted", False) or ("tomato" in crop.lower())

    if not w_data or "duration_days_min" not in w_data:
        d_min, d_max = (90, 115) if is_transplanted else (105, 120)
    else:
        d_min = w_data.get("duration_days_min", 105)
        d_max = w_data.get("duration_days_max", 120)

    sm = w_data.get("start_month", 10)
    sd = w_data.get("start_day", 15)

    ref_today = get_current_date(today)
    ref_year = ref_today.year

    if planned_sowing_date:
        planned_sow = planned_sowing_date
    else:
        planned_sow = date(ref_year, sm, sd)
        if season.lower() == "rabi" and sm < 6 and ref_today.month >= 6:
            planned_sow = date(ref_year + 1, sm, sd)

    effective_sow = max(planned_sow, ref_today)

    earliest_harvest = effective_sow + timedelta(days=d_min)
    latest_harvest = effective_sow + timedelta(days=d_max)

    h_sm = earliest_harvest.month
    h_em = latest_harvest.month

    name_sm_en = MONTH_NAMES[h_sm]
    name_em_en = MONTH_NAMES[h_em]
    name_sm_kn = MONTH_NAMES_KN[h_sm]
    name_em_kn = MONTH_NAMES_KN[h_em]
    name_sm_hi = MONTH_NAMES_HI[h_sm]
    name_em_hi = MONTH_NAMES_HI[h_em]

    if name_sm_en == name_em_en:
        label_en = name_sm_en
        label_kn = name_sm_kn
        label_hi = name_sm_hi
    else:
        label_en = f"{name_sm_en} - {name_em_en}"
        label_kn = f"{name_sm_kn} - {name_em_kn}"
        label_hi = f"{name_sm_hi} - {name_em_hi}"

    if is_transplanted:
        dur_str_en = f"~{d_min}-{d_max} days after transplanting"
        dur_str_kn = f"ನಾಟಿ ಮಾಡಿದ ನಂತರ ~{d_min}-{d_max} ದಿನಗಳು"
        dur_str_hi = f"रोपाई के ~{d_min}-{d_max} दिन बाद"
    else:
        dur_str_en = f"~{d_min}-{d_max} days after sowing"
        dur_str_kn = f"ಬಿತ್ತನೆಯ ನಂತರ ~{d_min}-{d_max} ದಿನಗಳು"
        dur_str_hi = f"बुवाई के ~{d_min}-{d_max} दिन बाद"

    return {
        "harvest_en": f"{label_en} ({dur_str_en})",
        "harvest_kn": f"{label_kn} ({dur_str_kn})",
        "harvest_hi": f"{label_hi} ({dur_str_hi})",
        "harvest_months_en": label_en,
        "harvest_months_kn": label_kn,
        "harvest_months_hi": label_hi,
        "duration_days": f"{d_min}-{d_max} days",
        "effective_sowing_date": effective_sow.isoformat(),
        "earliest_harvest_date": earliest_harvest.isoformat(),
        "latest_harvest_date": latest_harvest.isoformat()
    }


MSP_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "msp_config.json")


def load_msp_config() -> Dict[str, Any]:
    """Load canonical Government Minimum Support Price (MSP) configuration."""
    try:
        if os.path.exists(MSP_CONFIG_PATH):
            with open(MSP_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Notice: Failed to load msp_config.json: {e}")
    return {}


def get_msp_for_crop(crop_name: str) -> Optional[Dict[str, Any]]:
    """Lookup MSP entry for a given crop name."""
    cfg = load_msp_config().get("commodities", {})
    query = crop_name.lower().strip().replace(" ", "_")
    
    if query in cfg:
        return cfg[query]
    
    for k, v in cfg.items():
        if k in query or query in k:
            return v
        for alias in v.get("aliases", []):
            if alias.lower() in query or query in alias.lower():
                return v
    return None
