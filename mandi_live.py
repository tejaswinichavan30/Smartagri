import os, json, time, logging, requests
from datetime import datetime
from statistics import mean
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()
API_KEY = os.getenv("DATA_GOV_IN_API_KEY")
URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mandi_cache.json")
log = logging.getLogger("mandi")

_session = requests.Session()
_session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
    "Accept": "application/json",
})
_session.mount("https://", HTTPAdapter(max_retries=Retry(
    total=1, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])))


# ---------- app crop name -> exact commodity name used by data.gov.in ----------
CROP_MAP = {
    "onion": "Onion",
    "sunflower": "Sunflower/Sunflower Seed",
    "horse gram": "Kulthi(Horse Gram)",
    "horsegram": "Kulthi(Horse Gram)",
    "kulthi": "Kulthi(Horse Gram)",
    "chickpea": "Bengal Gram(Gram)(Whole)",
    "chickpea (bengal gram)": "Bengal Gram(Gram)(Whole)",
    "bengal gram": "Bengal Gram(Gram)(Whole)",
    "gram": "Bengal Gram(Gram)(Whole)",
    "groundnut": "Groundnut",
    "groundnut (peanut)": "Groundnut",
    "peanut": "Groundnut",
    "wheat": "Wheat",
    "jowar": "Jowar(Sorghum)",
    "sorghum": "Jowar(Sorghum)",
    "rabi jowar": "Jowar(Sorghum)",
    "safflower": "Safflower",
    "kusube": "Safflower",
    "maize": "Maize",
    "ragi": "Ragi(Finger Millet)",
    "bajra": "Bajra(Pearl Millet/Cumbu)",
    "tur": "Red gram/Arhar/Tur(whole)",
    "red gram": "Red gram/Arhar/Tur(whole)",
    "pigeonpea": "Red gram/Arhar/Tur(whole)",
    "pigeonpeas": "Red gram/Arhar/Tur(whole)",
    "arhar": "Red gram/Arhar/Tur(whole)",
    "green gram": "Green Gram(Moong)(Whole)",
    "moong": "Green Gram(Moong)(Whole)",
    "black gram": "Black Gram(Urd Beans)(Whole)",
    "urad": "Black Gram(Urd Beans)(Whole)",
    "soybean": "Soyabean",
    "soyabean": "Soyabean",
    "cotton": "Cotton",
    "paddy": "Paddy(Common)",
    "rice": "Rice",
    "sesame": "Sesamum(Sesame,Gingelly,Til)",
    "sesamum": "Sesamum(Sesame,Gingelly,Til)",
    "tomato": "Tomato",
    "potato": "Potato",
    "turmeric": "Turmeric",
    "garlic": "Garlic",
    "cowpea": "Cowpea(Lobia/Karamani)",
    "coriander": "Corriander seed",
    "dry chilli": "Dry Chillies",
    "green chilli": "Green Chilli",
    "arecanut": "Arecanut(Betelnut/Supari)",
    "coconut": "Coconut",
    "banana": "Banana",
    "grapes": "Grapes",
    "mango": "Mango",
    "apple": "Apple",
    "watermelon": "Water Melon",
    "muskmelon": "Karbuja(Musk Melon)",
    "pomegranate": "Pomegranate",
    "fieldbeans": "Field Pea",
    "field bean": "Field Pea",
    "avarekai": "Field Pea",
}

# ---------- app district name -> spellings used by the dataset ----------
ALIASES = {
    "davanagere": ["Davangere"], "davangere": ["Davangere"],
    "shimoga": ["Shivamogga"], "shivamogga": ["Shivamogga"],
    "chikmagalur": ["Chikkamagaluru"], "chikkamagaluru": ["Chikkamagaluru"],
    "bijapur": ["Vijayapura"], "vijayapura": ["Vijayapura"],
    "bellary": ["Ballari", "Vijayanagara"], "ballari": ["Ballari"],
    "belgaum": ["Belagavi"], "belagavi": ["Belagavi"],
    "gulbarga": ["Kalaburagi"], "kalaburagi": ["Kalaburagi"],
    "tumkur": ["Tumakuru"], "tumakuru": ["Tumakuru"],
    "mysore": ["Mysuru"], "mysuru": ["Mysuru"],
    "bangalore": ["Bengaluru", "Bengaluru Urban"], "bengaluru": ["Bengaluru"],
    "hubballi-dharwad": ["Dharwad"], "hubli": ["Dharwad"], "dharwad": ["Dharwad"],
    "mangalore": ["Dakshina Kannada"],
    "chamarajanagar": ["Chamarajanagar", "Chamrajnagar"],
}


def fetch_mandi_price(state, commodity, district=None, market=None):
    """Latest real record from data.gov.in, or None. Never returns made-up data."""
    if not API_KEY:
        log.error("DATA_GOV_IN_API_KEY is not set")
        return None

    params = {"api-key": API_KEY, "format": "json", "limit": 100,
              "filters[state]": state, "filters[commodity]": commodity}
    if district:
        params["filters[district]"] = district
    if market:
        params["filters[market]"] = market

    try:
        r = _session.get(URL, params=params, timeout=(4.0, 10.0))
        r.raise_for_status()
        records = r.json().get("records", [])
    except Exception as e:
        log.error("data.gov.in call failed: %s", e)
        return None

    rows = []
    for rec in records:
        try:
            rows.append({
                "market": rec["market"],
                "date": datetime.strptime(rec["arrival_date"], "%d/%m/%Y"),
                "min": float(rec["min_price"]),
                "max": float(rec["max_price"]),
                "modal": float(rec["modal_price"]),
            })
        except (KeyError, ValueError):
            continue

    if not rows:
        log.warning("No records for %s / %s / %s", state, district, commodity)
        return None

    latest = max(r["date"] for r in rows)
    newest = [r for r in rows if r["date"] == latest]
    return {
        "as_of": latest.strftime("%d %b %Y"),
        "modal": round(mean(r["modal"] for r in newest)),
        "min": min(r["min"] for r in newest),
        "max": max(r["max"] for r in newest),
        "markets": sorted({r["market"] for r in newest}),
        "unit": "\u20b9/quintal",
        "source": "data.gov.in (AGMARKNET)",
    }


def _load():
    try:
        with open(CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception as e:
        log.error("could not write cache: %s", e)


def get_price(state, commodity, district=None, market=None, fresh_for=3600):
    """status: 'live' | 'cached' (under 1h old) | 'stale' (API down, last real record) | None"""
    key = f"{state}|{district}|{commodity}|{market}"
    cache = _load()
    hit = cache.get(key)

    if hit and time.time() - hit["fetched_at"] < fresh_for:
        return {**hit["data"], "status": "cached"}

    data = fetch_mandi_price(state, commodity, district, market)
    if data:
        cache[key] = {"fetched_at": time.time(), "data": data}
        _save(cache)
        return {**data, "status": "live"}

    if hit:
        return {**hit["data"], "status": "stale"}
    return None


def get_price_smart(crop, district=None, state="Karnataka"):
    """District price if available, otherwise statewide. Check result['scope']."""
    crop_name = CROP_MAP.get(crop.strip().lower(), crop.strip())

    candidates = []
    if district and district.strip().lower() not in ("", "karnataka"):
        d = district.strip()
        for c in [d] + ALIASES.get(d.lower(), []):
            if c not in candidates:
                candidates.append(c)

    for c in candidates:
        res = get_price(state, crop_name, c)
        if res:
            res["scope"] = "district"
            res["district_used"] = c
            return res
        log.info("no data for district spelling %r", c)

    res = get_price(state, crop_name)
    if res:
        res["scope"] = "state"
        res["district_used"] = None
    return res


# ---------- v2: verifies commodity, uses median, pages through results ----------
from statistics import median

def fetch_mandi_price(state, commodity, district=None, market=None):
    """Latest real records for exactly this commodity, or None."""
    if not API_KEY:
        log.error("DATA_GOV_IN_API_KEY is not set")
        return None

    base = {"api-key": API_KEY, "format": "json", "limit": 1000, "filters[state]": state}
    if district:
        base["filters[district]"] = district
    if market:
        base["filters[market]"] = market

    def run(extra):
        out, offset = [], 0
        for _ in range(6):                       # up to 6,000 rows
            params = {**base, **extra, "offset": offset}
            r = _session.get(URL, params=params, timeout=(4.0, 10.0))
            r.raise_for_status()
            batch = r.json().get("records", [])
            out += batch
            if len(batch) < 1000:
                break
            offset += 1000
        return out

    want = commodity.strip().lower()

    def exact(recs):
        return [x for x in recs if str(x.get("commodity", "")).strip().lower() == want]

    try:
        records = run({"filters[commodity]": commodity})
        rows_raw = exact(records)
        if records and len(rows_raw) != len(records):
            log.warning("API ignored the commodity filter (got %s); filtering locally",
                        sorted({str(x.get("commodity")) for x in records})[:5])
            rows_raw = exact(run({}))
    except Exception as e:
        log.error("data.gov.in call failed: %s", e)
        return None

    rows = []
    for rec in rows_raw:
        try:
            rows.append({
                "market": rec["market"],
                "variety": rec.get("variety", ""),
                "date": datetime.strptime(rec["arrival_date"], "%d/%m/%Y"),
                "min": float(rec["min_price"]),
                "max": float(rec["max_price"]),
                "modal": float(rec["modal_price"]),
            })
        except (KeyError, ValueError):
            continue

    if not rows:
        log.warning("No exact records for %s / %s / %s", state, district, commodity)
        return None

    latest = max(r["date"] for r in rows)
    newest = [r for r in rows if r["date"] == latest]
    modals = [r["modal"] for r in newest]

    by_market = {}
    for r in newest:
        by_market.setdefault(r["market"], []).append(r["modal"])
    by_market = {m: round(median(v)) for m, v in sorted(by_market.items())}

    low, high = min(modals), max(modals)
    return {
        "as_of": latest.strftime("%d %b %Y"),
        "modal": round(median(modals)),
        "min": min(r["min"] for r in newest),
        "max": max(r["max"] for r in newest),
        "modal_low": low,
        "modal_high": high,
        "wide_spread": (high / low > 2.5) if low > 0 else True,
        "n_records": len(newest),
        "by_market": by_market,
        "markets": sorted(by_market),
        "varieties": sorted({r["variety"] for r in newest if r["variety"]}),
        "unit": "\u20b9/quintal",
        "source": "data.gov.in (AGMARKNET)",
    }


# ---------- display text for the price card ----------
# Only Kharif 2026-27 MSPs verified from the CCEA announcement (13 May 2026).
# Rabi crops (wheat, chickpea, safflower) are intentionally absent until verified.
MSP_KHARIF_2026_27 = {
    "Sunflower/Sunflower Seed": 8343, "Groundnut": 7517, "Soyabean": 5708,
    "Sesamum(Sesame,Gingelly,Til)": 10346, "Red gram/Arhar/Tur(whole)": 8450,
    "Black Gram(Urd Beans)(Whole)": 8200, "Green Gram(Moong)(Whole)": 8780,
    "Paddy(Common)": 2441, "Maize": 2410, "Ragi(Finger Millet)": 5205,
    "Bajra(Pearl Millet/Cumbu)": 2900, "Cotton": 8267,
}
NO_MSP = {"Onion", "Kulthi(Horse Gram)", "Tomato", "Potato", "Garlic"}


def format_price_card(result, crop, district=None):
    """Returns a list of display lines. Never invents a number."""
    if not result:
        return ["Live price unavailable right now. Check your local APMC or agmarknet.gov.in."]

    commodity = CROP_MAP.get(crop.strip().lower(), crop.strip())
    unit = result["unit"]
    lines = []

    if result.get("scope") == "district":
        where = ", ".join(result["markets"])
    else:
        where = f"{result['n_records']} record(s) across {len(result['markets'])} Karnataka market(s)"
        if district and district.strip().lower() != "karnataka":
            lines.append(f"No market in {district} reported {crop} today. "
                         f"Showing the Karnataka-wide median instead.")
        else:
            lines.append(f"Showing the Karnataka-wide median for {crop}.")

    lines.append(f"Live mandi price (median): \u20b9{result['modal']:,}/{unit.split('/')[-1]} "
                 f"(\u2248 \u20b9{result['modal']/100:.2f}/kg) | Range of reported prices: "
                 f"\u20b9{result['min']:,.0f} - \u20b9{result['max']:,.0f}")
    lines.append(f"Source: {result['source']} | Markets: {where} | Date: {result['as_of']}")

    if result.get("status") == "stale":
        lines.append("Live service is down. Showing the last fetched data.")
    if result["n_records"] < 3:
        lines.append(f"Based on only {result['n_records']} record(s), so treat this as a rough guide.")
    if result.get("wide_spread"):
        lines.append("Prices vary widely between markets today. Check your nearest mandi before selling.")

    msp = MSP_KHARIF_2026_27.get(commodity)
    if commodity in NO_MSP:
        lines.append("Govt MSP: No central MSP for this crop.")
    elif msp:
        gap = msp - result["modal"]
        lines.append(f"Govt MSP (2026-27 announcement): \u20b9{msp:,}/quintal")
        if gap > 0:
            lines.append(f"Today's market price is \u20b9{gap:,.0f} below MSP. MSP procurement happens only "
                         f"if the state opens it for your district and you are registered; ask your APMC/RSK.")
        else:
            lines.append(f"Today's market price is \u20b9{-gap:,.0f} above MSP.")
    else:
        lines.append("Govt MSP: not checked for this crop. Confirm with the Department of Agriculture.")

    lines.append("Price trend: Insufficient data (live feed has only the latest day).")
    return lines
