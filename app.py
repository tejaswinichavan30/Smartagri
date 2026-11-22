import os
import sys

# Ensure KERAS_HOME points to local project directory to prevent Windows [Errno 13] PermissionError
_project_dir = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('KERAS_HOME', os.path.join(_project_dir, '.keras'))
os.environ.setdefault('TF_ENABLE_ONEDNN_OPTS', '0')

# Safe global InputLayer patch for Keras 3 compatibility (strips legacy 'optional' arg from kwargs & config)
for _pkg in ['keras.layers', 'tf_keras.layers', 'tensorflow.keras.layers']:
    try:
        _mod = __import__(_pkg, fromlist=['InputLayer'])
        _lyr = getattr(_mod, 'InputLayer', None)
        if _lyr:
            _orig_init = _lyr.__init__
            def _make_safe_init(orig_fn):
                def _safe_init(self, *args, **kwargs):
                    kwargs.pop('optional', None)
                    orig_fn(self, *args, **kwargs)
                return _safe_init
            _lyr.__init__ = _make_safe_init(_orig_init)

            if hasattr(_lyr, 'from_config'):
                _orig_fc = _lyr.from_config
                def _make_safe_fc(orig_fn):
                    def _safe_fc(cls, config):
                        cfg = dict(config)
                        cfg.pop('optional', None)
                        return orig_fn(cfg)
                    return _safe_fc
                _lyr.from_config = classmethod(_make_safe_fc(_orig_fc))
    except Exception:
        pass

from flask import Flask, render_template, request, redirect, session, jsonify, send_file, send_from_directory, Response
import numpy as np
import pandas as pd
import joblib
import requests
import json
import os
import io
import re
import hashlib
import difflib
import pickle
import tensorflow as tf
import tf_keras
from tf_keras.preprocessing import image
from gtts import gTTS
from datetime import datetime, date
from typing import Optional, Dict, Any, Tuple, List
import translations

try:
    from models.agri_llm_service import agri_llm
    from models.agri_rag_service import agri_rag
    from models.agmarknet_service import agmarknet_service
    from models.agri_decision_intelligence import (
        digital_twin_engine,
        counterfactual_causal_engine,
        multi_agent_debate_engine,
        regret_minimization_engine
    )
    from models.agri_visual_copilot import visual_copilot_engine
    from models.plant_image_validator import validate_plant_image
except Exception as _llm_e:
    print(f"Warning: Could not load Agri LLM/RAG/Agmarknet/Decision Intelligence/Visual Copilot service: {_llm_e}")
    agri_llm = None
    agri_rag = None
    agmarknet_service = None
    digital_twin_engine = None
    counterfactual_causal_engine = None
    multi_agent_debate_engine = None
    regret_minimization_engine = None
    visual_copilot_engine = None
    validate_plant_image = None


from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict
import uuid

class ServerSideSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.modified = False

class FileSystemSessionInterface(SessionInterface):
    def __init__(self, session_dir="flask_sessions"):
        self.session_dir = session_dir
        os.makedirs(self.session_dir, exist_ok=True)

    def open_session(self, app, request):
        sid = request.cookies.get(app.config.get("SESSION_COOKIE_NAME", "session"))
        if not sid:
            sid = str(uuid.uuid4())
            return ServerSideSession(sid=sid)
        filepath = os.path.join(self.session_dir, f"{sid}.sess")
        if os.path.exists(filepath):
            try:
                with open(filepath, "rb") as f:
                    val = pickle.load(f)
                return ServerSideSession(val, sid=sid)
            except Exception:
                pass
        return ServerSideSession(sid=sid)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        if not session:
            if session.modified:
                filepath = os.path.join(self.session_dir, f"{session.sid}.sess")
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except Exception:
                        pass
                response.delete_cookie(app.config.get("SESSION_COOKIE_NAME", "session"),
                                       domain=domain, path=path)
            return

        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)
        samesite = self.get_cookie_samesite(app)

        filepath = os.path.join(self.session_dir, f"{session.sid}.sess")
        try:
            with open(filepath, "wb") as f:
                pickle.dump(dict(session), f)
        except Exception as e:
            print(f"Session save error: {e}")

        response.set_cookie(app.config.get("SESSION_COOKIE_NAME", "session"),
                            session.sid,
                            httponly=httponly,
                            domain=domain,
                            path=path,
                            secure=secure,
                            samesite=samesite)

app = Flask(__name__)
app.secret_key = "smartagri@123"
app.session_interface = FileSystemSessionInterface()

REACT_DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'smartagri-react', 'dist')

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({"status": "ok"})

# ===============================
# Crop Knowledge Base & Seasonal Calendar
# ===============================
crop_knowledge = {
    'rice': {
        'season': 'Kharif (Monsoon)',
        'season_type': 'Kharif',
        'planting_months': 'June - July (general, confirm locally with KVK)',
        'harvest_months': 'October - November',
        'season_desc': 'Requires high rainfall & warm humid climate. Ideal for monsoon cultivation.',
        'fertilizer': {
            'Nitrogen': '100 kg/hectare',
            'Phosphorus': '50 kg/hectare',
            'Potassium': '50 kg/hectare'
        },
        'pests': [
            'Brown planthopper → Alternate wetting & drying, avoid excess N, use light traps',
            'Stem borer → Install pheromone traps (5/ha), release Trichogramma egg parasitoids',
            'Blast disease → Seed treatment with Trichoderma viride (10g/kg) and balanced N-K nutrition'
        ],
        'best_sell_months': 'December - January',
        'sell_tip': 'Avail official Govt MSP procurement centers for assured returns on Grade-A/Common paddy.'
    },
    'maize': {
        'season': 'Kharif / Zaid',
        'season_type': 'Kharif',
        'planting_months': 'June - July & February - March (general, confirm locally with KVK)',
        'harvest_months': 'September - October & May - June',
        'season_desc': 'Adaptable cereal crop grown in both monsoon and spring-summer.',
        'fertilizer': {
            'Nitrogen': '120 kg/hectare',
            'Phosphorus': '60 kg/hectare',
            'Potassium': '40 kg/hectare'
        },
        'pests': [
            'Fall armyworm → Pheromone traps, intercropping with pulses, apply neem seed kernel extract (NSKE 5%)',
            'Stem borer → Release Trichogramma chilonis and apply push-pull trap crops',
            'Aphids → Conserve predatory ladybird beetles and spray 5% neem oil'
        ],
        'best_sell_months': 'October - November',
        'sell_tip': 'Monitor multi-year APMC price trends; check mandi arrivals post-harvest.'
    },
    'chickpea': {
        'season': 'Rabi (Winter)',
        'season_type': 'Rabi',
        'planting_months': 'October - November (general, confirm locally with KVK)',
        'harvest_months': 'February - March',
        'season_desc': 'Cool-season legume requiring moderate cold and dry weather at maturity.',
        'fertilizer': {
            'Nitrogen': '20 kg/hectare',
            'Phosphorus': '60 kg/hectare',
            'Potassium': '20 kg/hectare'
        },
        'pests': [
            'Pod borer → Install pheromone traps (4-5/ha), erect bird perches, spray HaNPV (250 LE/ha)',
            'Wilt → Seed treatment with Trichoderma harzianum (4g/kg seed) and crop rotation',
            'Aphids → Yellow sticky traps and 5% neem seed kernel extract'
        ],
        'best_sell_months': 'March - May',
        'sell_tip': 'Benchmark against Govt MSP of ₹5,875/q before open market selling.'
    },
    'kidneybeans': {
        'season': 'Kharif',
        'season_type': 'Kharif',
        'planting_months': 'June - July (general, confirm locally with KVK)',
        'harvest_months': 'September - October',
        'season_desc': 'Warm-season pulse requiring moderate rain and fertile well-drained soil.',
        'fertilizer': {
            'Nitrogen': '30 kg/hectare',
            'Phosphorus': '60 kg/hectare',
            'Potassium': '40 kg/hectare'
        },
        'pests': [
            'Bean fly → Soil solarization and seed treatment with bio-agents',
            'Aphids → 5% neem oil spray and yellow sticky traps',
            'Rust → Crop hygiene, wider spacing, and bio-fungicide preventive spray'
        ],
        'best_sell_months': 'October - December',
        'sell_tip': 'Monitor local APMC arrivals to identify seasonal peak price windows.'
    },
    'pigeonpeas': {
        'season': 'Kharif',
        'season_type': 'Kharif',
        'planting_months': 'June - July (general, confirm locally with KVK)',
        'harvest_months': 'December - January',
        'season_desc': 'Long-duration pulse crop thriving under rainfed monsoon conditions.',
        'fertilizer': {
            'Nitrogen': '25 kg/hectare',
            'Phosphorus': '50 kg/hectare',
            'Potassium': '25 kg/hectare'
        },
        'pests': [
            'Pod borer → Install pheromone traps, erect bird perches (50/ha), apply HaNPV spray',
            'Pod fly → Early sowing, intercropping with sorghum/bajra, light traps',
            'Sterility mosaic → Rogue out vector-infested diseased plants early'
        ],
        'best_sell_months': 'January - March',
        'sell_tip': 'Benchmark against official Tur MSP of ₹8,450/q at designated APMC yards.'
    },
    'mothbeans': {
        'season': 'Kharif (Drought Tolerant)',
        'season_type': 'Kharif',
        'planting_months': 'June - July (general, confirm locally with KVK)',
        'harvest_months': 'September - October',
        'season_desc': 'Extremely drought-hardy legume suitable for dry and arid tracts.',
        'fertilizer': {
            'Nitrogen': '20 kg/hectare',
            'Phosphorus': '40 kg/hectare',
            'Potassium': '20 kg/hectare'
        },
        'pests': [
            'Jassids → Yellow sticky traps and 5% neem seed extract spray',
            'Whitefly → Yellow sticky traps and border crop of pearl millet',
            'Pod borer → Bird perches and bio-pesticide spray'
        ],
        'best_sell_months': 'October - November',
        'sell_tip': 'Check local mandi prices post-harvest.'
    },
    'mungbean': {
        'season': 'Kharif / Zaid',
        'season_type': 'Kharif',
        'planting_months': 'June - July (Kharif) & March - April (Summer) (general, confirm locally with KVK)',
        'harvest_months': 'August - September & May - June',
        'season_desc': 'Short duration 65-day crop suitable for multi-cropping.',
        'fertilizer': {
            'Nitrogen': '20 kg/hectare',
            'Phosphorus': '40 kg/hectare',
            'Potassium': '20 kg/hectare'
        },
        'pests': [
            'Whitefly → Yellow sticky traps and border cropping with maize/sorghum',
            'Yellow mosaic → Grow MYMV resistant varieties and control whitefly vectors with neem spray',
            'Thrips → Blue sticky traps and 5% neem oil'
        ],
        'best_sell_months': 'September - October',
        'sell_tip': 'Benchmark against official Moong MSP of ₹8,780/q.'
    },
    'blackgram': {
        'season': 'Kharif / Zaid',
        'season_type': 'Kharif',
        'planting_months': 'June - July (Kharif) & February - March (Summer) (general, confirm locally with KVK)',
        'harvest_months': 'September - October & April - May',
        'season_desc': 'Fast-maturing pulse that enriches soil nitrogen.',
        'fertilizer': {
            'Nitrogen': '20 kg/hectare',
            'Phosphorus': '40 kg/hectare',
            'Potassium': '20 kg/hectare'
        },
        'pests': [
            'Aphids → Yellow sticky traps and 5% neem seed kernel extract',
            'Pod borer → Pheromone traps and bio-agent application',
            'Leaf crinkle virus → Rogue out infected plants and manage insect vectors with neem oil'
        ],
        'best_sell_months': 'October - November',
        'sell_tip': 'Benchmark against official Urad MSP of ₹8,200/q.'
    },
    'lentil': {
        'season': 'Rabi (Winter)',
        'season_type': 'Rabi',
        'planting_months': 'October - November (general, confirm locally with KVK)',
        'harvest_months': 'February - March',
        'season_desc': 'Cold-tolerant winter legume requiring low to medium moisture.',
        'fertilizer': {
            'Nitrogen': '20 kg/hectare',
            'Phosphorus': '40 kg/hectare',
            'Potassium': '20 kg/hectare'
        },
        'pests': [
            'Aphids → Yellow sticky traps and bio-control predators',
            'Rust → Crop hygiene, balanced nutrition, and bio-fungicides',
            'Wilt → Seed treatment with Trichoderma harzianum (4g/kg seed)'
        ],
        'best_sell_months': 'March - May',
        'sell_tip': 'Check local APMC price trends during Rabi harvest.'
    },
    'pomegranate': {
        'season': 'Whole Year (Perennial)',
        'season_type': 'Whole Year',
        'planting_months': 'June - July (Mrig Bahar) & Dec - Jan (Ambe Bahar) (general, confirm locally with KVK)',
        'harvest_months': 'November - December & June - August',
        'season_desc': 'Commercial horticultural fruit crop performing well in semi-arid zones.',
        'fertilizer': {
            'Nitrogen': '200 kg/hectare',
            'Phosphorus': '100 kg/hectare',
            'Potassium': '200 kg/hectare'
        },
        'pests': [
            'Fruit borer → Individual fruit bagging with butter paper bags and light traps',
            'Bacterial blight (Telya) → Clean orchard sanitation, prune infected twigs, spray Bordeaux mixture 1%',
            'Thrips → Blue sticky traps and neem-based formulation'
        ],
        'best_sell_months': 'November - February',
        'sell_tip': 'Sort by grade and fruit weight for premium mandi rates.'
    },
    'banana': {
        'season': 'Whole Year (Perennial)',
        'season_type': 'Whole Year',
        'planting_months': 'February - March & June - July (general, confirm locally with KVK)',
        'harvest_months': 'Year round (12-15 months after planting)',
        'season_desc': 'Perennial crop requiring abundant moisture and warm humid climate.',
        'fertilizer': {
            'Nitrogen': '200 kg/hectare',
            'Phosphorus': '60 kg/hectare',
            'Potassium': '300 kg/hectare'
        },
        'pests': [
            'Banana weevil → Pseudostem trap management and clean planting suckers',
            'Sigatoka leaf spot → De-leafing infected leaves and spraying 1% Bordeaux mixture',
            'Aphids → Yellow sticky traps and bio-pesticide spray'
        ],
        'best_sell_months': 'October - January',
        'sell_tip': 'Monitor local festival and market demand.'
    },
    'mango': {
        'season': 'Summer / Annual',
        'season_type': 'Zaid',
        'planting_months': 'June - July (general, confirm locally with KVK)',
        'harvest_months': 'April - June',
        'season_desc': 'Tropical perennial fruit yielding during peak summer months.',
        'fertilizer': {
            'Nitrogen': '100 kg/hectare',
            'Phosphorus': '50 kg/hectare',
            'Potassium': '100 kg/hectare'
        },
        'pests': [
            'Mango hopper → Pruning dense canopy for sunlight and neem oil spray (3000 ppm)',
            'Fruit fly → Methyl eugenol pheromone traps (10/ha) and field sanitation',
            'Powdery mildew → Wettable sulfur spray (2g/L) at panicle emergence'
        ],
        'best_sell_months': 'April - June',
        'sell_tip': 'Early season harvests in April fetch top mandi rates.'
    },
    'grapes': {
        'season': 'Rabi / Summer',
        'season_type': 'Rabi',
        'planting_months': 'July - August (general, confirm locally with KVK)',
        'harvest_months': 'February - April',
        'season_desc': 'Subtropical/temperate vine requiring warm dry weather during fruit ripening.',
        'fertilizer': {
            'Nitrogen': '90 kg/hectare',
            'Phosphorus': '60 kg/hectare',
            'Potassium': '90 kg/hectare'
        },
        'pests': [
            'Downy mildew → Canopy management for air flow and preventive Bordeaux mixture',
            'Thrips → Blue sticky traps and bio-rational extracts',
            'Mealybug → Release Cryptolaemus montrouzieri predatory beetles'
        ],
        'best_sell_months': 'February - April',
        'sell_tip': 'Grape prices depend on Brix sugar levels and cold-storage availability.'
    },
    'watermelon': {
        'season': 'Zaid (Summer)',
        'season_type': 'Zaid',
        'planting_months': 'January - March (general, confirm locally with KVK)',
        'harvest_months': 'March - May',
        'season_desc': 'Fast-growing summer vine requiring warm sunny days and sandy loam soil.',
        'fertilizer': {
            'Nitrogen': '80 kg/hectare',
            'Phosphorus': '50 kg/hectare',
            'Potassium': '50 kg/hectare'
        },
        'pests': [
            'Fruit fly → Cue-lure pheromone traps and collection of fallen fruits',
            'Red pumpkin beetle → Ash dusting on seedlings and hand-picking in morning',
            'Anthracnose → Seed treatment with Trichoderma and crop hygiene'
        ],
        'best_sell_months': 'April - May',
        'sell_tip': 'Demand peaks during peak summer temperatures.'
    },
    'muskmelon': {
        'season': 'Zaid (Summer)',
        'season_type': 'Zaid',
        'planting_months': 'February - March (general, confirm locally with KVK)',
        'harvest_months': 'April - May',
        'season_desc': 'Warm-season cucurbit requiring high temperatures and dry air at ripening.',
        'fertilizer': {
            'Nitrogen': '60 kg/hectare',
            'Phosphorus': '40 kg/hectare',
            'Potassium': '40 kg/hectare'
        },
        'pests': [
            'Fruit fly → Cue-lure traps and field sanitation',
            'Aphids → Yellow sticky traps and neem oil spray',
            'Downy mildew → Drip irrigation and adequate plant spacing'
        ],
        'best_sell_months': 'April - May',
        'sell_tip': 'Sweet fragrant melons sell rapidly in urban markets in summer.'
    },
    'apple': {
        'season': 'Temperate / Autumn',
        'season_type': 'Rabi',
        'planting_months': 'January - February (general, confirm locally with KVK)',
        'harvest_months': 'August - October',
        'season_desc': 'Temperate fruit crop requiring winter chilling and mild summer.',
        'fertilizer': {
            'Nitrogen': '70 kg/hectare',
            'Phosphorus': '35 kg/hectare',
            'Potassium': '70 kg/hectare'
        },
        'pests': [
            'Codling moth → Pheromone mating disruption and trunk banding',
            'Apple scab → Orchard sanitation, pruning, and bio-fungicides',
            'Woolly aphid → Release Aphelinus mali parasitoids'
        ],
        'best_sell_months': 'September - October',
        'sell_tip': 'Graded and cold-stored apples fetch premium returns.'
    },
    'orange': {
        'season': 'Whole Year / Winter',
        'season_type': 'Rabi',
        'planting_months': 'June - August (general, confirm locally with KVK)',
        'harvest_months': 'November - January',
        'season_desc': 'Subtropical citrus crop performing well in well-drained loams.',
        'fertilizer': {
            'Nitrogen': '120 kg/hectare',
            'Phosphorus': '60 kg/hectare',
            'Potassium': '80 kg/hectare'
        },
        'pests': [
            'Citrus psylla → Yellow sticky traps and neem formulation',
            'Citrus canker → Pruning canker-affected branches and spraying 1% Bordeaux mixture',
            'Leaf miner → Spraying 5% neem seed kernel extract on tender flushes'
        ],
        'best_sell_months': 'December - February',
        'sell_tip': 'Citrus winter harvest commands strong consumer demand.'
    },
    'papaya': {
        'season': 'Whole Year (Tropical)',
        'season_type': 'Whole Year',
        'planting_months': 'February - March & June - July (general, confirm locally with KVK)',
        'harvest_months': 'Year round (starts 9-10 months after planting)',
        'season_desc': 'Fast growing fruit crop providing continuous year-round yields.',
        'fertilizer': {
            'Nitrogen': '150 kg/hectare',
            'Phosphorus': '150 kg/hectare',
            'Potassium': '200 kg/hectare'
        },
        'pests': [
            'Ring spot virus → Vector control with barrier crops (maize/sorghum) and neem oil',
            'Mealybugs → Release Cryptolaemus predatory beetles',
            'Mites → Wettable sulfur spray (2g/L)'
        ],
        'best_sell_months': 'October - December',
        'sell_tip': 'Consistent cash crop with steady local market demand.'
    },
    'coconut': {
        'season': 'Whole Year (Perennial)',
        'season_type': 'Whole Year',
        'planting_months': 'June - September (general, confirm locally with KVK)',
        'harvest_months': 'Year round (every 45-60 days)',
        'season_desc': 'Perennial coastal & tropical tree requiring warm humid climate.',
        'fertilizer': {
            'Nitrogen': '100 kg/hectare',
            'Phosphorus': '40 kg/hectare',
            'Potassium': '200 kg/hectare'
        },
        'pests': [
            'Rhinoceros beetle → Install rhinoceros beetle pheromone traps and treat manure pits with Metarhizium anisopliae',
            'Red palm weevil → Pheromone traps (Ferrolure+) and crown cleaning',
            'Leaf blight → Apply 1% Bordeaux mixture on lower fronds'
        ],
        'best_sell_months': 'April - June',
        'sell_tip': 'Tender coconut demand peaks in summer months.'
    },
    'cotton': {
        'season': 'Kharif (Monsoon)',
        'season_type': 'Kharif',
        'planting_months': 'May - June (general, confirm locally with KVK)',
        'harvest_months': 'November - January',
        'season_desc': 'Commercial cash crop requiring warm days, long sunshine and black cotton soil.',
        'fertilizer': {
            'Nitrogen': '100 kg/hectare',
            'Phosphorus': '50 kg/hectare',
            'Potassium': '50 kg/hectare'
        },
        'pests': [
            'Bollworm → Pheromone traps (5/ha), light traps, and intercropping with maize/cowpea',
            'Whitefly → Yellow sticky traps (15-20/ha) and 5% neem oil spray',
            'Aphids → Conserve ladybird beetles and spray 5% NSKE'
        ],
        'best_sell_months': 'December - February',
        'sell_tip': 'Benchmark against Govt MSP of ₹8,267/q (Medium Staple) / ₹8,667/q (Long Staple).'
    },
    'jute': {
        'season': 'Kharif (Monsoon)',
        'season_type': 'Kharif',
        'planting_months': 'March - May (general, confirm locally with KVK)',
        'harvest_months': 'July - September',
        'season_desc': 'Natural fiber crop requiring warm humid climate and standing water for retting.',
        'fertilizer': {
            'Nitrogen': '60 kg/hectare',
            'Phosphorus': '30 kg/hectare',
            'Potassium': '30 kg/hectare'
        },
        'pests': [
            'Hairy caterpillar → Light traps and collection of egg masses',
            'Stem rot → Seed treatment with Trichoderma viride',
            'Aphids → Neem formulation spray'
        ],
        'best_sell_months': 'September - November',
        'sell_tip': 'Monitor JCI (Jute Corporation of India) procurement centers for minimum support.'
    },
    'coffee': {
        'season': 'Whole Year (Plantation)',
        'season_type': 'Whole Year',
        'planting_months': 'June - August (general, confirm locally with KVK)',
        'harvest_months': 'November - January',
        'season_desc': 'Shade-grown plantation crop thriving in Western Ghats soils.',
        'fertilizer': {
            'Nitrogen': '80 kg/hectare',
            'Phosphorus': '40 kg/hectare',
            'Potassium': '80 kg/hectare'
        },
        'pests': [
            'Coffee berry borer → Beauveria bassiana bio-fungal spray and broca traps',
            'Leaf rust → Canopy shade management and Bordeaux mixture 0.5%',
            'Mealybug → Release of Cryptolaemus predator beetles'
        ],
        'best_sell_months': 'January - March',
        'sell_tip': 'Coffee Board auction prices determine seasonal benchmarks.'
    },
    'tomato': {
        'season': 'Kharif & Rabi',
        'season_type': 'Kharif',
        'planting_months': 'June - August & November - January (general, confirm locally with KVK)',
        'harvest_months': 'October - December & March - May',
        'season_desc': 'High-value vegetable cultivated across monsoon and winter cycles.',
        'fertilizer': {
            'Nitrogen': '80 kg/hectare',
            'Phosphorus': '60 kg/hectare',
            'Potassium': '180 kg/hectare'
        },
        'pests': [
            'Whitefly → Yellow sticky traps (20/ha) and 5% neem oil spray',
            'Aphids → Conserve predators and spray neem seed extract',
            'Fruit borer → Install Helicoverpa pheromone traps (5/ha) and Trichogramma release'
        ],
        'best_sell_months': 'October - December',
        'sell_tip': 'Daily spot prices fluctuate widely; check local APMC rates before transport.'
    },
    'potato': {
        'season': 'Rabi (Winter)',
        'season_type': 'Rabi',
        'planting_months': 'October - December (general, confirm locally with KVK)',
        'harvest_months': 'February - March',
        'season_desc': 'Cool-weather tuber crop requiring 15-20°C temperatures for tuber formation.',
        'fertilizer': {
            'Nitrogen': '120 kg/hectare',
            'Phosphorus': '60 kg/hectare',
            'Potassium': '150 kg/hectare'
        },
        'pests': [
            'Aphids → Yellow sticky traps and border crop of barley/wheat',
            'Tuber moth → Clean storage, earthing up, and covering with sand/dry leaves',
            'Late blight → Certified disease-free seed tubers and preventive copper hydroxide / Bordeaux spray'
        ],
        'best_sell_months': 'March - April',
        'sell_tip': 'Cold storage allows phased market release for improved margins.'
    },
    'onion': {
        'season': 'Kharif & Rabi',
        'season_type': 'Rabi',
        'planting_months': 'June - July (Kharif) & October - December (Rabi) (general, confirm locally with KVK)',
        'harvest_months': 'October - November & March - May',
        'season_desc': 'Essential bulb crop grown across monsoon and winter cycles.',
        'fertilizer': {
            'Nitrogen': '100 kg/hectare',
            'Phosphorus': '50 kg/hectare',
            'Potassium': '50 kg/hectare'
        },
        'pests': [
            'Thrips → Blue sticky traps (20/ha) and 5% neem oil spray',
            'Onion maggot → Crop rotation and soil solarization',
            'Purple blotch → Wider plant spacing, proper drainage, and Trichoderma seed treatment'
        ],
        'best_sell_months': 'April - June',
        'sell_tip': 'Proper post-harvest curing and ventilated storage prevents storage rot.'
    },
    'wheat': {
        'season': 'Rabi (Winter)',
        'season_type': 'Rabi',
        'planting_months': 'November - December (general, confirm locally with KVK)',
        'harvest_months': 'March - April',
        'season_desc': 'Major winter staple cereal requiring cool growing season and dry harvest period.',
        'fertilizer': {
            'Nitrogen': '120 kg/hectare',
            'Phosphorus': '60 kg/hectare',
            'Potassium': '40 kg/hectare'
        },
        'pests': [
            'Aphids → Yellow sticky traps and conservation of coccinellid predators',
            'Rust → Grow rust-resistant varieties and maintain balanced N-K nutrition',
            'Termites → Decomposed organic manure and neem cake soil application'
        ],
        'best_sell_months': 'April - May',
        'sell_tip': 'Benchmark against official Govt MSP of ₹2,585/q.'
    },
    'soybean': {
        'season': 'Kharif (Monsoon)',
        'season_type': 'Kharif',
        'planting_months': 'June - July (general, confirm locally with KVK)',
        'harvest_months': 'September - October',
        'season_desc': 'Major Kharif oilseed in North Karnataka requiring warm humid weather.',
        'fertilizer': {
            'Nitrogen': '30 kg/hectare',
            'Phosphorus': '60 kg/hectare',
            'Potassium': '40 kg/hectare'
        },
        'pests': [
            'Stem fly → Seed treatment with Trichoderma and timely early planting',
            'Girdle beetle → Destruction of alternate host weeds and light traps',
            'Rust → Grow resistant varieties and apply bio-fungicide preventives'
        ],
        'best_sell_months': 'October - December',
        'sell_tip': 'Benchmark against official Govt MSP of ₹5,708/q.'
    },
    'groundnut': {
        'season': 'Kharif & Rabi / Summer',
        'season_type': 'Kharif',
        'planting_months': 'June - July & December - January (general, confirm locally with KVK)',
        'harvest_months': 'October - November & April - May',
        'season_desc': 'Major commercial oilseed performing well in sandy loam soils.',
        'fertilizer': {
            'Nitrogen': '25 kg/hectare',
            'Phosphorus': '50 kg/hectare',
            'Potassium': '40 kg/hectare'
        },
        'pests': [
            'Tikka leaf spot → Seed treatment with Trichoderma viride (10g/kg) and neem oil spray',
            'Leaf miner → Light traps and 5% neem seed kernel extract',
            'White grub → Deep summer ploughing and application of Metarhizium anisopliae'
        ],
        'best_sell_months': 'November - January',
        'sell_tip': 'Benchmark against official Govt MSP of ₹7,517/q.'
    },
    'ragi': {
        'season': 'Kharif (Monsoon)',
        'season_type': 'Kharif',
        'planting_months': 'July - August (general, confirm locally with KVK)',
        'harvest_months': 'November - December',
        'season_desc': 'Climate-smart staple grain with high nutritional value and drought resilience.',
        'fertilizer': {
            'Nitrogen': '60 kg/hectare',
            'Phosphorus': '30 kg/hectare',
            'Potassium': '30 kg/hectare'
        },
        'pests': [
            'Blast disease → Seed treatment with Trichoderma harzianum (4g/kg seed) and balanced fertilizer use',
            'Stem borer → Release Trichogramma parasitoids and use light traps',
            'Aphids → 5% neem oil spray'
        ],
        'best_sell_months': 'December - February',
        'sell_tip': 'Benchmark against official Govt MSP of ₹5,205/q at state procurement centers.'
    },
    'default': {
        'season': 'General All-Season',
        'season_type': 'Whole Year',
        'planting_months': 'Consult local Krishi Vigyan Kendra (KVK)',
        'harvest_months': 'Consult local Krishi Vigyan Kendra (KVK)',
        'season_desc': 'Consult local Krishi Vigyan Kendra (KVK) for specific seasonal schedule.',
        'fertilizer': {
            'Nitrogen': 'As per soil test',
            'Phosphorus': 'As per soil test',
            'Potassium': 'As per soil test'
        },
        'pests': [
            'Follow Integrated Pest Management (IPM) guidelines from your local KVK / ICAR station'
        ],
        'best_sell_months': 'Monitor local market prices',
        'sell_tip': 'Check local mandi prices and official MSP announcements.'
    }
}
# ===============================
# Helper Function
# ===============================
def find_crop_in_text(text):
    return translations.find_crop_in_text(text)
# ===============================
# Load Crop Models
# ===============================
crop_model   = joblib.load("models/saved_models/crop_model.pkl")
crop_scaler  = joblib.load("models/saved_models/scaler.pkl")
crop_encoder = joblib.load("models/saved_models/crop_encoder.pkl")

price_model  = joblib.load("models/saved_models/market_price_model.pkl")
le_commodity = joblib.load("models/saved_models/commodity_encoder.pkl")
le_state     = joblib.load("models/saved_models/state_encoder.pkl")
PRICE_MONTH_JUMP_WARN_PCT = 15.0

KARNATAKA_DISTRICTS = [
    'Bagalkot', 'Ballari', 'Belagavi', 'Bengaluru Rural', 'Bengaluru Urban',
    'Bidar', 'Chamarajanagara', 'Chikkaballapura', 'Chikkamagaluru', 'Chitradurga',
    'Dakshina Kannada', 'Davanagere', 'Dharwad', 'Gadag', 'Hassan',
    'Haveri', 'Kalaburagi', 'Kodagu', 'Kolar', 'Koppal',
    'Mandya', 'Mysuru', 'Raichur', 'Ramanagara', 'Shivamogga',
    'Tumakuru', 'Udupi', 'Uttara Kannada', 'Vijayanagara', 'Vijayapura', 'Yadgir'
]

KARNATAKA_CROPS = [
    'Rice', 'Maize', 'Wheat', 'Cotton', 'Sugarcane', 'Tomato', 'Potato', 'Onion',
    'Chickpea', 'Pigeonpeas', 'Blackgram', 'Mungbean', 'Banana',
    'Mango', 'Grapes', 'Pomegranate', 'Coconut', 'Coffee', 'Papaya',
    'Watermelon', 'Muskmelon', 'Orange', 'Lentil', 'Kidneybeans', 'Mothbeans', 'Pepper',
    'Soybean', 'Groundnut', 'Ragi', 'Arecanut', 'Cashew', 'Sunflower', 'Mulberry', 'Jowar'
]

KARNATAKA_DISTRICT_SEASON_CROPS = {
    'Bagalkot': {
        'kharif': ['maize', 'pigeonpeas', 'groundnut', 'bajra', 'sunflower', 'onion', 'cotton', 'horsegram', 'cowpea'],
        'rabi': ['jowar', 'chickpea', 'sunflower', 'wheat', 'groundnut', 'maize', 'onion', 'watermelon'],
        'zaid': ['groundnut', 'sunflower', 'maize', 'watermelon', 'cowpea', 'tomato', 'bajra']
    },
    'Ballari': {
        'kharif': ['cotton', 'maize', 'rice', 'pigeonpeas', 'groundnut', 'sunflower', 'chilli', 'horsegram', 'cowpea'],
        'rabi': ['rice', 'jowar', 'sunflower', 'chickpea', 'maize', 'groundnut', 'watermelon'],
        'zaid': ['groundnut', 'maize', 'rice', 'sunflower', 'watermelon', 'cowpea', 'tomato']
    },
    'Belagavi': {
        'kharif': ['soybean', 'maize', 'rice', 'cotton', 'groundnut', 'jowar', 'chilli', 'potato', 'horsegram', 'sunflower', 'cowpea'],
        'rabi': ['jowar', 'chickpea', 'wheat', 'sunflower', 'maize', 'groundnut', 'tomato', 'watermelon'],
        'zaid': ['groundnut', 'maize', 'sunflower', 'cowpea', 'watermelon', 'tomato']
    },
    'Bengaluru Rural': {
        'kharif': ['ragi', 'maize', 'groundnut', 'pigeonpeas', 'cowpea', 'tomato', 'chilli', 'horsegram', 'sunflower'],
        'rabi': ['tomato', 'fieldbeans', 'horsegram', 'chickpea', 'ragi', 'cowpea', 'onion', 'groundnut', 'watermelon'],
        'zaid': ['tomato', 'groundnut', 'ragi', 'maize', 'watermelon', 'cowpea', 'vegetables']
    },
    'Bengaluru Urban': {
        'kharif': ['ragi', 'maize', 'groundnut', 'pigeonpeas', 'cowpea', 'tomato', 'chilli', 'horsegram', 'sunflower'],
        'rabi': ['tomato', 'fieldbeans', 'horsegram', 'chickpea', 'ragi', 'cowpea', 'onion', 'groundnut', 'watermelon'],
        'zaid': ['tomato', 'groundnut', 'ragi', 'maize', 'watermelon', 'cowpea', 'vegetables']
    },
    'Bidar': {
        'kharif': ['soybean', 'pigeonpeas', 'mungbean', 'blackgram', 'jowar', 'maize', 'sunflower', 'horsegram', 'cowpea'],
        'rabi': ['chickpea', 'jowar', 'sunflower', 'wheat', 'groundnut', 'tomato', 'watermelon'],
        'zaid': ['groundnut', 'sunflower', 'mungbean', 'blackgram', 'watermelon', 'tomato', 'cowpea']
    },
    'Chamarajanagar': {
        'kharif': ['maize', 'cotton', 'turmeric', 'ragi', 'rice', 'cowpea', 'groundnut', 'sunflower', 'horsegram'],
        'rabi': ['sunflower', 'chickpea', 'tomato', 'horsegram', 'ragi', 'rice', 'cowpea', 'groundnut', 'watermelon'],
        'zaid': ['maize', 'tomato', 'groundnut', 'cowpea', 'watermelon', 'rice', 'ragi']
    },
    'Chamarajanagara': {
        'kharif': ['maize', 'cotton', 'turmeric', 'ragi', 'rice', 'cowpea', 'groundnut', 'sunflower', 'horsegram'],
        'rabi': ['sunflower', 'chickpea', 'tomato', 'horsegram', 'ragi', 'rice', 'cowpea', 'groundnut', 'watermelon'],
        'zaid': ['maize', 'tomato', 'groundnut', 'cowpea', 'watermelon', 'rice', 'ragi']
    },
    'Chikkaballapura': {
        'kharif': ['ragi', 'groundnut', 'maize', 'pigeonpeas', 'cowpea', 'tomato', 'chilli', 'horsegram', 'sunflower'],
        'rabi': ['tomato', 'horsegram', 'fieldbeans', 'chickpea', 'ragi', 'cowpea', 'onion', 'groundnut', 'watermelon'],
        'zaid': ['tomato', 'groundnut', 'ragi', 'maize', 'watermelon', 'cowpea', 'vegetables']
    },
    'Chikkamagaluru': {
        'kharif': ['rice', 'maize', 'ragi', 'ginger', 'turmeric', 'cowpea', 'tomato', 'chilli', 'horsegram', 'sunflower'],
        'rabi': ['rice', 'horsegram', 'cowpea', 'blackgram', 'tomato', 'maize', 'vegetables', 'watermelon', 'groundnut'],
        'zaid': ['cowpea', 'tomato', 'blackgram', 'watermelon', 'vegetables', 'maize', 'groundnut', 'rice']
    },
    'Chitradurga': {
        'kharif': ['maize', 'groundnut', 'cotton', 'ragi', 'pigeonpeas', 'onion', 'sunflower', 'horsegram', 'cowpea'],
        'rabi': ['sunflower', 'chickpea', 'onion', 'horsegram', 'maize', 'jowar', 'tomato', 'fieldbeans', 'groundnut', 'watermelon'],
        'zaid': ['groundnut', 'sunflower', 'tomato', 'maize', 'watermelon', 'cowpea', 'ragi']
    },
    'Dakshina Kannada': {
        'kharif': ['rice', 'ragi', 'cowpea', 'ginger', 'turmeric', 'blackgram', 'chilli', 'horsegram', 'sunflower'],
        'rabi': ['rice', 'blackgram', 'mungbean', 'cowpea', 'horsegram', 'groundnut', 'watermelon', 'vegetables'],
        'zaid': ['rice', 'cowpea', 'blackgram', 'watermelon', 'groundnut', 'vegetables', 'mungbean']
    },
    'Davanagere': {
        'kharif': ['maize', 'rice', 'cotton', 'groundnut', 'ragi', 'pigeonpeas', 'sunflower', 'horsegram', 'cowpea'],
        'rabi': ['jowar', 'sunflower', 'chickpea', 'maize', 'rice', 'horsegram', 'tomato', 'onion', 'groundnut', 'watermelon'],
        'zaid': ['rice', 'maize', 'tomato', 'groundnut', 'sunflower', 'watermelon', 'cowpea']
    },
    'Dharwad': {
        'kharif': ['jowar', 'cotton', 'soybean', 'maize', 'groundnut', 'chilli', 'pigeonpeas', 'horsegram', 'sunflower', 'cowpea'],
        'rabi': ['jowar', 'chickpea', 'wheat', 'sunflower', 'maize', 'onion', 'groundnut', 'tomato', 'watermelon'],
        'zaid': ['groundnut', 'sunflower', 'maize', 'mungbean', 'cowpea', 'watermelon', 'tomato']
    },
    'Gadag': {
        'kharif': ['maize', 'cotton', 'onion', 'groundnut', 'pigeonpeas', 'bajra', 'sunflower', 'chilli', 'horsegram', 'cowpea'],
        'rabi': ['chickpea', 'jowar', 'sunflower', 'wheat', 'onion', 'groundnut', 'maize', 'watermelon'],
        'zaid': ['groundnut', 'maize', 'tomato', 'sunflower', 'watermelon', 'cowpea']
    },
    'Hassan': {
        'kharif': ['ragi', 'maize', 'potato', 'rice', 'ginger', 'turmeric', 'cowpea', 'soybean', 'horsegram', 'sunflower'],
        'rabi': ['tomato', 'horsegram', 'cowpea', 'rice', 'blackgram', 'maize', 'sunflower', 'chickpea', 'groundnut', 'watermelon'],
        'zaid': ['rice', 'tomato', 'maize', 'groundnut', 'cowpea', 'watermelon', 'blackgram']
    },
    'Haveri': {
        'kharif': ['maize', 'cotton', 'chilli', 'soybean', 'groundnut', 'jowar', 'pigeonpeas', 'rice', 'horsegram', 'sunflower', 'cowpea'],
        'rabi': ['chickpea', 'jowar', 'sunflower', 'wheat', 'maize', 'groundnut', 'tomato', 'watermelon'],
        'zaid': ['tomato', 'groundnut', 'maize', 'sunflower', 'cowpea', 'watermelon']
    },
    'Kalaburagi': {
        'kharif': ['pigeonpeas', 'mungbean', 'blackgram', 'cotton', 'sunflower', 'soybean', 'bajra', 'horsegram', 'cowpea'],
        'rabi': ['chickpea', 'jowar', 'sunflower', 'wheat', 'groundnut', 'tomato', 'watermelon'],
        'zaid': ['sunflower', 'groundnut', 'tomato', 'watermelon', 'mungbean', 'blackgram', 'cowpea']
    },
    'Kodagu': {
        'kharif': ['rice', 'ginger', 'turmeric', 'maize', 'ragi', 'cowpea', 'tomato', 'chilli', 'horsegram', 'sunflower'],
        'rabi': ['rice', 'horsegram', 'cowpea', 'blackgram', 'tomato', 'maize', 'vegetables', 'watermelon', 'groundnut'],
        'zaid': ['tomato', 'cowpea', 'blackgram', 'maize', 'watermelon', 'vegetables', 'groundnut', 'rice']
    },
    'Kolar': {
        'kharif': ['ragi', 'groundnut', 'tomato', 'maize', 'pigeonpeas', 'cowpea', 'chilli', 'horsegram', 'sunflower'],
        'rabi': ['tomato', 'horsegram', 'fieldbeans', 'chickpea', 'ragi', 'cowpea', 'onion', 'groundnut', 'watermelon'],
        'zaid': ['tomato', 'groundnut', 'ragi', 'maize', 'watermelon', 'cowpea', 'vegetables']
    },
    'Koppal': {
        'kharif': ['rice', 'maize', 'pigeonpeas', 'groundnut', 'cotton', 'bajra', 'sunflower', 'chilli', 'horsegram', 'cowpea'],
        'rabi': ['jowar', 'chickpea', 'rice', 'sunflower', 'wheat', 'maize', 'groundnut', 'watermelon'],
        'zaid': ['rice', 'groundnut', 'tomato', 'maize', 'sunflower', 'watermelon', 'cowpea']
    },
    'Mandya': {
        'kharif': ['rice', 'ragi', 'maize', 'cowpea', 'turmeric', 'groundnut', 'blackgram', 'horsegram', 'sunflower'],
        'rabi': ['rice', 'ragi', 'blackgram', 'horsegram', 'cowpea', 'chickpea', 'tomato', 'groundnut', 'watermelon'],
        'zaid': ['rice', 'ragi', 'tomato', 'groundnut', 'cowpea', 'blackgram', 'watermelon', 'maize']
    },
    'Mysuru': {
        'kharif': ['rice', 'ragi', 'maize', 'cotton', 'cowpea', 'turmeric', 'groundnut', 'blackgram', 'horsegram', 'sunflower'],
        'rabi': ['rice', 'ragi', 'horsegram', 'blackgram', 'cowpea', 'chickpea', 'tomato', 'groundnut', 'watermelon'],
        'zaid': ['rice', 'ragi', 'tomato', 'groundnut', 'cowpea', 'blackgram', 'watermelon', 'maize']
    },
    'Raichur': {
        'kharif': ['cotton', 'rice', 'jowar', 'pigeonpeas', 'groundnut', 'bajra', 'sunflower', 'horsegram', 'cowpea'],
        'rabi': ['rice', 'jowar', 'chickpea', 'sunflower', 'groundnut', 'wheat', 'watermelon'],
        'zaid': ['rice', 'groundnut', 'sunflower', 'watermelon', 'cowpea', 'tomato', 'bajra']
    },
    'Ramanagara': {
        'kharif': ['ragi', 'maize', 'groundnut', 'pigeonpeas', 'cowpea', 'tomato', 'chilli', 'horsegram', 'sunflower'],
        'rabi': ['tomato', 'ragi', 'horsegram', 'fieldbeans', 'chickpea', 'cowpea', 'groundnut', 'watermelon'],
        'zaid': ['tomato', 'groundnut', 'ragi', 'maize', 'watermelon', 'cowpea', 'vegetables']
    },
    'Shivamogga': {
        'kharif': ['rice', 'maize', 'ginger', 'ragi', 'turmeric', 'cowpea', 'soybean', 'chilli', 'horsegram', 'sunflower'],
        'rabi': ['rice', 'blackgram', 'tomato', 'horsegram', 'cowpea', 'maize', 'sunflower', 'groundnut', 'watermelon'],
        'zaid': ['rice', 'groundnut', 'tomato', 'maize', 'cowpea', 'watermelon', 'blackgram']
    },
    'Tumakuru': {
        'kharif': ['ragi', 'groundnut', 'pigeonpeas', 'maize', 'cotton', 'onion', 'sunflower', 'cowpea', 'horsegram'],
        'rabi': ['horsegram', 'sunflower', 'tomato', 'chickpea', 'fieldbeans', 'onion', 'ragi', 'groundnut', 'watermelon'],
        'zaid': ['groundnut', 'tomato', 'maize', 'sunflower', 'watermelon', 'cowpea', 'ragi']
    },
    'Udupi': {
        'kharif': ['rice', 'ragi', 'cowpea', 'ginger', 'turmeric', 'blackgram', 'chilli', 'horsegram', 'sunflower'],
        'rabi': ['rice', 'blackgram', 'mungbean', 'cowpea', 'horsegram', 'groundnut', 'watermelon', 'vegetables'],
        'zaid': ['rice', 'cowpea', 'blackgram', 'watermelon', 'groundnut', 'vegetables', 'mungbean']
    },
    'Uttara Kannada': {
        'kharif': ['rice', 'ragi', 'cowpea', 'ginger', 'turmeric', 'blackgram', 'chilli', 'groundnut', 'horsegram', 'sunflower'],
        'rabi': ['rice', 'blackgram', 'mungbean', 'cowpea', 'horsegram', 'groundnut', 'watermelon', 'vegetables'],
        'zaid': ['rice', 'cowpea', 'blackgram', 'watermelon', 'groundnut', 'vegetables', 'mungbean']
    },
    'Vijayanagara': {
        'kharif': ['rice', 'maize', 'cotton', 'pigeonpeas', 'groundnut', 'bajra', 'sunflower', 'chilli', 'horsegram', 'cowpea'],
        'rabi': ['rice', 'jowar', 'sunflower', 'chickpea', 'wheat', 'maize', 'groundnut', 'watermelon'],
        'zaid': ['rice', 'groundnut', 'maize', 'sunflower', 'watermelon', 'cowpea', 'tomato']
    },
    'Vijayapura': {
        'kharif': ['pigeonpeas', 'bajra', 'maize', 'groundnut', 'sunflower', 'onion', 'cotton', 'horsegram', 'cowpea'],
        'rabi': ['jowar', 'chickpea', 'sunflower', 'wheat', 'onion', 'groundnut', 'maize', 'watermelon'],
        'zaid': ['sunflower', 'groundnut', 'tomato', 'maize', 'watermelon', 'cowpea', 'bajra']
    },
    'Yadgir': {
        'kharif': ['cotton', 'pigeonpeas', 'rice', 'groundnut', 'bajra', 'sunflower', 'mungbean', 'blackgram', 'horsegram', 'cowpea'],
        'rabi': ['jowar', 'chickpea', 'sunflower', 'rice', 'groundnut', 'wheat', 'watermelon'],
        'zaid': ['rice', 'sunflower', 'groundnut', 'watermelon', 'cowpea', 'mungbean', 'blackgram', 'tomato']
    }
}

KARNATAKA_DISTRICT_CROPS = {
    d: list(dict.fromkeys(crops['kharif'] + crops['rabi'] + crops['zaid']))
    for d, crops in KARNATAKA_DISTRICT_SEASON_CROPS.items()
}

DISTRICT_WEATHER_CITY = {
    'Bagalkot': 'Bagalkot',
    'Ballari': 'Bellary',
    'Belagavi': 'Belgaum',
    'Bengaluru Rural': 'Bengaluru',
    'Bengaluru Urban': 'Bengaluru',
    'Bidar': 'Bidar',
    'Chamarajanagara': 'Chamrajnagar',
    'Chikkaballapura': 'Chik Ballapur',
    'Chikkamagaluru': 'Chikmagalur',
    'Chitradurga': 'Chitradurga',
    'Dakshina Kannada': 'Mangalore',
    'Davanagere': 'Davangere',
    'Dharwad': 'Dharwad',
    'Gadag': 'Gadag',
    'Hassan': 'Hassan',
    'Haveri': 'Haveri',
    'Kalaburagi': 'Gulbarga',
    'Kodagu': 'Madikeri',
    'Kolar': 'Kolar',
    'Koppal': 'Koppal',
    'Mandya': 'Mandya',
    'Mysuru': 'Mysore',
    'Raichur': 'Raichur',
    'Ramanagara': 'Ramanagara',
    'Shivamogga': 'Shimoga',
    'Tumakuru': 'Tumkur',
    'Udupi': 'Udupi',
    'Uttara Kannada': 'Karwar',
    'Vijayanagara': 'Hospet',
    'Vijayapura': 'Bijapur',
    'Yadgir': 'Yadgir'
}

DISTRICT_RAINFALL_NORMALS_PATH = os.path.join(os.path.dirname(__file__), "data", "district_rainfall_normals.json")

def get_district_monthly_rainfall(district: str, month: int) -> Optional[float]:
    """Retrieve IMD monthly rainfall normal for a district. Returns None if unverified/null."""
    try:
        if os.path.exists(DISTRICT_RAINFALL_NORMALS_PATH):
            with open(DISTRICT_RAINFALL_NORMALS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                dists = data.get("districts", {})
                for d_name, m_data in dists.items():
                    if d_name.lower() in district.lower() or district.lower() in d_name.lower():
                        val = m_data.get(str(month))
                        if val is not None:
                            return float(val)
    except Exception as e:
        print(f"Notice: Failed loading rainfall normals: {e}")
    return None

def get_weather(city):
    try:
        api_key = os.getenv("OWM_API_KEY", "b9592880d7ec9f2a8e4de876eaa84c09")
        query_city = DISTRICT_WEATHER_CITY.get(city, city)
        url = f"http://api.openweathermap.org/data/2.5/weather?q={query_city},IN&appid={api_key}&units=metric"
        response = requests.get(url, timeout=3.0)
        data = response.json()
        if data.get("cod") == 200:
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            desc = data["weather"][0]["description"].title()
            return temp, humidity, desc
    except Exception:
        pass
    return 28.0, 55.0, "clear sky"

# ===============================
# ===============================
# Leaf Disease Models (Lazy-loaded for cloud memory efficiency)
# ===============================
general_disease_model = None
wheat_disease_model = None
rice_disease_model = None

def get_general_disease_model():
    global general_disease_model
    if general_disease_model is None:
        print("[Model] Loading general_disease_model into memory...")
        model_path = "models/saved_models/disease_model.h5"

        # 1. Try tf_keras first with native tf_keras InputLayer wrapper
        try:
            from tf_keras.layers import InputLayer as LegacyInputLayer
            class SafeTfKerasInputLayer(LegacyInputLayer):
                def __init__(self, *args, **kwargs):
                    kwargs.pop('optional', None)
                    super().__init__(*args, **kwargs)
                @classmethod
                def from_config(cls, config):
                    cfg = dict(config)
                    cfg.pop('optional', None)
                    return cls(**cfg)
            general_disease_model = tf_keras.models.load_model(
                model_path, compile=False, custom_objects={'InputLayer': SafeTfKerasInputLayer}
            )
        except Exception as e1:
            print(f"[Model] tf_keras load_model failed ({e1}). Trying keras...")
            # 2. Try native keras (Keras 3)
            try:
                import keras
                class SafeKerasInputLayer(keras.layers.InputLayer):
                    def __init__(self, *args, **kwargs):
                        kwargs.pop('optional', None)
                        super().__init__(*args, **kwargs)
                    @classmethod
                    def from_config(cls, config):
                        cfg = dict(config)
                        cfg.pop('optional', None)
                        return cls(**cfg)
                general_disease_model = keras.models.load_model(
                    model_path, compile=False, custom_objects={'InputLayer': SafeKerasInputLayer}
                )
            except Exception as e2:
                print(f"[Model] keras load_model failed ({e2}). Trying tf.keras...")
                # 3. Try tf.keras safely
                try:
                    import tensorflow as tf
                    class SafeTfInputLayer(tf.keras.layers.InputLayer):
                        def __init__(self, *args, **kwargs):
                            kwargs.pop('optional', None)
                            super().__init__(*args, **kwargs)
                        @classmethod
                        def from_config(cls, config):
                            cfg = dict(config)
                            cfg.pop('optional', None)
                            return cls(**cfg)
                    general_disease_model = tf.keras.models.load_model(
                        model_path, compile=False, custom_objects={'InputLayer': SafeTfInputLayer}
                    )
                except Exception as e3:
                    print(f"[Model] All load_model attempts failed for general_disease_model ({e3}). Model unavailable.")
                    general_disease_model = None
    return general_disease_model

def get_wheat_disease_model():
    global wheat_disease_model
    if wheat_disease_model is None:
        model_path = "models/saved_models/wheat_model_final.keras"
        if not os.path.exists(model_path):
            model_path = "Datasets/wheat_model_final.keras"
        print(f"[Model] Loading wheat_disease_model from {model_path}...")
        try:
            import tf_keras
            wheat_disease_model = tf_keras.models.load_model(model_path, compile=False)
        except Exception as e1:
            try:
                import keras
                wheat_disease_model = keras.models.load_model(model_path, compile=False)
            except Exception as e2:
                try:
                    import tensorflow as tf
                    wheat_disease_model = tf.keras.models.load_model(model_path, compile=False)
                except Exception as e3:
                    print(f"[Model] All load attempts failed for wheat model ({e3}).")
                    wheat_disease_model = None
    return wheat_disease_model

def get_rice_disease_model():
    global rice_disease_model
    if rice_disease_model is None:
        model_path = "models/saved_models/rice_model_final.keras"
        if not os.path.exists(model_path):
            model_path = "Datasets/rice_model_final.keras"
        if not os.path.exists(model_path):
            model_path = "models/saved_models/rice_model.keras"
        print(f"[Model] Loading rice_disease_model from {model_path}...")
        try:
            import tf_keras
            rice_disease_model = tf_keras.models.load_model(model_path, compile=False)
        except Exception as e1:
            try:
                import keras
                rice_disease_model = keras.models.load_model(model_path, compile=False)
            except Exception as e2:
                try:
                    import tensorflow as tf
                    rice_disease_model = tf.keras.models.load_model(model_path, compile=False)
                except Exception as e3:
                    print(f"[Model] All load attempts failed for rice model ({e3}).")
                    rice_disease_model = None
    return rice_disease_model

rice_classes = ['bacterial_leaf_blight', 'brown_spot', 'healthy', 'leaf_blast', 'leaf_scald', 'narrow_brown_spot']
for r_path in ["models/saved_models/rice_model_classes.txt", "Datasets/rice_model_classes.txt"]:
    if os.path.exists(r_path):
        with open(r_path) as f:
            lines = [line.strip() for line in f if line.strip()]
            if lines:
                rice_classes = lines
                break

wheat_classes = ['BlackPoint', 'FusariumFootRot', 'HealthyLeaf', 'LeafBlight', 'WheatBlast']
for w_path in ["models/saved_models/wheat_model_classes.txt", "Datasets/wheat_model_classes.txt"]:
    if os.path.exists(w_path):
        with open(w_path) as f:
            lines = [line.strip() for line in f if line.strip()]
            if lines:
                wheat_classes = lines
                break

# 40 classes matching general_disease_model (disease_model.h5)
GENERAL_40_DISEASE_CLASSES = [
    'Apple - Apple scab',
    'Apple - Black rot',
    'Apple - Cedar apple rust',
    'Apple - healthy',
    'Blueberry - healthy',
    'Cherry including sour - Powdery mildew',
    'Cherry including sour - healthy',
    'Corn maize - Cercospora leaf spot Gray leaf spot',
    'Corn maize - Common rust',
    'Corn maize - Northern Leaf Blight',
    'Corn maize - healthy',
    'Grape - Black rot',
    'Grape - Esca (Black Measles)',
    'Grape - Leaf blight (Isariopsis Leaf Spot)',
    'Grape - healthy',
    'Orange - Haunglongbing (Citrus greening)',
    'Peach - Bacterial spot',
    'Peach - healthy',
    'Pepper, bell - Bacterial spot',
    'Pepper, bell - healthy',
    'Potato - Early blight',
    'Potato - Late blight',
    'Potato - healthy',
    'Raspberry - healthy',
    'Rice - general',
    'Soybean - healthy',
    'Squash - Powdery mildew',
    'Strawberry - Leaf scorch',
    'Strawberry - healthy',
    'Tomato - Bacterial spot',
    'Tomato - Early blight',
    'Tomato - Late blight',
    'Tomato - Leaf Mold',
    'Tomato - Septoria leaf spot',
    'Tomato - Spider mites Two-spotted spider mite',
    'Tomato - Target Spot',
    'Tomato - Tomato Yellow Leaf Curl Virus',
    'Tomato - Tomato mosaic virus',
    'Tomato - healthy',
    'Wheat - general'
]

general_disease_classes = GENERAL_40_DISEASE_CLASSES

# ===============================
# Disease Prediction Function
# ===============================
WHEAT_DISEASE_NAME_CLEAN = {
    'LeafBlight': 'Leaf Blight',
    'FusariumFootRot': 'Fusarium Foot Rot',
    'BlackPoint': 'Black Point',
    'WheatBlast': 'Wheat Blast',
    'HealthyLeaf': 'Healthy Leaf'
}

RICE_DISEASE_NAME_CLEAN = {
    'bacterial_leaf_blight': 'Bacterial Leaf Blight',
    'brown_spot': 'Brown Spot',
    'healthy': 'Healthy',
    'leaf_blast': 'Leaf Blast',
    'leaf_scald': 'Leaf Scald',
    'narrow_brown_spot': 'Narrow Brown Spot'
}

def predict_leaf_disease(image_path, crop_type='tomato'):
    # Pre-validate if image contains an actual plant leaf
    if validate_plant_image:
        val_res = validate_plant_image(image_path)
        if not val_res.get('is_plant', True):
            reason = val_res.get('reason', 'No plant leaf detected in the photo.')
            print(f"[predict_leaf_disease] Invalid non-plant image rejected: {reason}")
            return ("Invalid", reason, 0.0)

    crop_key = translations.normalize_disease_crop(crop_type)
    if not crop_key or not translations.is_disease_diagnosis_supported(crop_key):
        print(f"[predict_leaf_disease] Refused unsupported/reference crop: '{crop_type}'")
        return ("Unsupported", crop_type, 0.0)

    crop_info = translations.get_crop_support(crop_key)
    crop_status = crop_info.get('status', 'reference_only')

    # Dedicated Wheat Model
    if crop_key == 'wheat':
        img = image.load_img(image_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)

        model = get_wheat_disease_model()
        prediction = model.predict(img_array)[0]

        sorted_indices = sorted(range(len(prediction)), key=lambda i: prediction[i], reverse=True)
        idx1 = sorted_indices[0]
        p1 = float(prediction[idx1])
        conf_pct = round(p1 * 100, 2)

        if p1 < translations.DISEASE_CONFIDENCE_THRESHOLD:
            print(f"[predict_leaf_disease] Uncertain diagnosis for wheat (p1={p1:.4f})")
            return ("Uncertain", "wheat", conf_pct)

        raw_disease = wheat_classes[idx1] if idx1 < len(wheat_classes) else "HealthyLeaf"
        clean_disease = WHEAT_DISEASE_NAME_CLEAN.get(raw_disease, raw_disease)
        print(f"[predict_leaf_disease] Wheat predicted: {clean_disease} ({conf_pct}%)")
        return ("Wheat", clean_disease, conf_pct)

    # Dedicated Rice Model
    if crop_key == 'rice':
        img = image.load_img(image_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)

        model = get_rice_disease_model()
        prediction = model.predict(img_array)[0]

        sorted_indices = sorted(range(len(prediction)), key=lambda i: prediction[i], reverse=True)
        idx1 = sorted_indices[0]
        p1 = float(prediction[idx1])
        conf_pct = round(p1 * 100, 2)

        if p1 < translations.DISEASE_CONFIDENCE_THRESHOLD:
            print(f"[predict_leaf_disease] Uncertain diagnosis for rice (p1={p1:.4f})")
            return ("Uncertain", "rice", conf_pct)

        raw_disease = rice_classes[idx1] if idx1 < len(rice_classes) else "healthy"
        clean_disease = RICE_DISEASE_NAME_CLEAN.get(raw_disease, raw_disease.replace('_', ' ').title())
        print(f"[predict_leaf_disease] Rice predicted: {clean_disease} ({conf_pct}%)")
        return ("Rice", clean_disease, conf_pct)

    # General PlantVillage CNN (40 classes)
    img = image.load_img(image_path, target_size=(128, 128))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    model = get_general_disease_model()
    prediction = model.predict(img_array)[0]

    # Map normalized crop_key to exact matching prefix in general_disease_classes
    CROP_CLASS_PREFIXES = {
        'apple': 'Apple - ',
        'blueberry': 'Blueberry - ',
        'cherry': 'Cherry including sour - ',
        'corn': 'Corn maize - ',
        'grape': 'Grape - ',
        'orange': 'Orange - ',
        'peach': 'Peach - ',
        'pepper': 'Pepper, bell - ',
        'potato': 'Potato - ',
        'raspberry': 'Raspberry - ',
        'soybean': 'Soybean - ',
        'squash': 'Squash - ',
        'strawberry': 'Strawberry - ',
        'tomato': 'Tomato - '
    }
    prefix = CROP_CLASS_PREFIXES.get(crop_key)
    if not prefix:
        matching_indices = [
            i for i, c in enumerate(general_disease_classes)
            if c.lower().startswith(crop_key) and i < len(prediction)
        ]
    else:
        matching_indices = [
            i for i, c in enumerate(general_disease_classes)
            if c.startswith(prefix) and i < len(prediction)
        ]

    if not matching_indices:
        return ("Unsupported", crop_key, 0.0)

    # 1. Compute total softmax probability on selected crop's classes
    crop_total_prob = float(sum(prediction[i] for i in matching_indices))
    print(f"[predict_leaf_disease] Crop '{crop_key}' total probability: {crop_total_prob:.4f}")

    if crop_total_prob < translations.CROP_MATCH_THRESHOLD:
        print(f"[predict_leaf_disease] Photo doesn't match crop '{crop_key}' (prob {crop_total_prob:.4f} < {translations.CROP_MATCH_THRESHOLD})")
        return ("CropMismatch", crop_key, round(crop_total_prob * 100, 2))

    # 2. Handle disease_only crops (Orange and Squash)
    if crop_status == 'disease_only':
        disease_idx = matching_indices[0]
        prob = float(prediction[disease_idx])
        conf_pct = round(prob * 100, 2)
        if crop_key == 'orange':
            if prob >= translations.DISEASE_CONFIDENCE_THRESHOLD:
                print(f"[predict_leaf_disease] Orange - Citrus greening suspected ({conf_pct}%)")
                return ("Orange", "Huanglongbing (Citrus Greening)", conf_pct)
            else:
                print(f"[predict_leaf_disease] Orange - Citrus greening not detected (prob {conf_pct}%)")
                return ("Orange", "DiseaseNotDetected", conf_pct)
        elif crop_key == 'squash':
            if prob >= translations.DISEASE_CONFIDENCE_THRESHOLD:
                print(f"[predict_leaf_disease] Squash - Powdery mildew suspected ({conf_pct}%)")
                return ("Squash", "Powdery Mildew", conf_pct)
            else:
                print(f"[predict_leaf_disease] Squash - Powdery mildew not detected (prob {conf_pct}%)")
                return ("Squash", "DiseaseNotDetected", conf_pct)

    # 3. Handle full and healthy_only crops
    # Sort matching indices by prediction probability descending
    sorted_indices = sorted(matching_indices, key=lambda i: prediction[i], reverse=True)
    idx1 = sorted_indices[0]
    p1 = float(prediction[idx1])
    p2 = float(prediction[sorted_indices[1]]) if len(sorted_indices) > 1 else 0.0
    conf_pct = round(p1 * 100, 2)

    # Check confidence threshold and margin
    has_confidence = p1 >= translations.DISEASE_CONFIDENCE_THRESHOLD
    has_margin = (p1 - p2) >= translations.MIN_CONFIDENCE_MARGIN if len(sorted_indices) > 1 else True

    if not has_confidence or not has_margin:
        print(f"[predict_leaf_disease] Uncertain diagnosis for '{crop_key}' (p1={p1:.4f}, p2={p2:.4f}, margin={p1-p2:.4f})")
        return ("Uncertain", crop_key, conf_pct)

    predicted_class = general_disease_classes[idx1]
    print(f"Predicted Disease: {predicted_class} with absolute confidence {conf_pct}%")

    if " - " in predicted_class:
        pred_crop, pred_disease = predicted_class.split(" - ", 1)
    else:
        pred_crop, pred_disease = crop_key, predicted_class

    return (
        pred_crop.strip().title(),
        pred_disease.strip(),
        conf_pct
    )

# ===============================
# Price Forecasting Engine Helper
# ===============================
def compute_price_forecast(crop, district, month=None, year=None, live_price=None, mandi_trend=None, lang='en'):
    if not crop:
        crop = 'Rice'
    if not district:
        district = 'Dharwad'
        
    now = datetime.now()
    if month is None or str(month).strip() == '':
        month = now.month
    if year is None or str(year).strip() == '':
        year = now.year
    try:
        month = int(month)
    except Exception:
        month = now.month
    try:
        year = int(year)
    except Exception:
        year = now.year

    crop_clean = crop.strip()
    crop_lower = crop_clean.lower()
    crop_aliases = {
        'finger millet (ragi)': 'ragi',
        'finger millet': 'ragi',
        'ragi (finger millet)': 'ragi',
        'paddy (rice)': 'paddy',
        'rice (paddy)': 'rice',
        'paddy (common)': 'paddy',
        'corn (maize)': 'maize',
        'corn': 'maize',
        'groundnut (peanut)': 'groundnut',
        'peanut': 'groundnut',
        'redgram': 'pigeonpea',
        'tur': 'pigeonpea',
        'arhar': 'pigeonpea',
        'pigeonpeas': 'pigeonpea',
        'cowpea (alasande)': 'cowpea',
        'cowpea (alsandi)': 'cowpea',
        'alasande': 'cowpea',
        'alsandi': 'cowpea',
        'lobia': 'cowpea',
        'horse gram (huruli)': 'horsegram',
        'horse gram': 'horsegram',
        'huruli': 'horsegram',
        'field bean (avarekai)': 'fieldbeans',
        'field beans': 'fieldbeans',
        'fieldbean': 'fieldbeans',
        'avarekai': 'fieldbeans'
    }
    canonical_crop = crop_aliases.get(crop_lower, crop_lower)
    
    # Load official MSP config
    msp_config = {}
    try:
        with open("data/msp_config.json", "r", encoding="utf-8") as mspf:
            msp_config = json.load(mspf)
    except Exception as _mspe:
        pass

    # For MSP lookup, raw Paddy (Dhan) is the mandated MSP commodity for rice/paddy
    msp_crop_key = 'paddy' if canonical_crop in ['rice', 'paddy', 'dhan'] else canonical_crop
    crop_msp_data = msp_config.get("commodities", {}).get(msp_crop_key, None) or msp_config.get("commodities", {}).get(canonical_crop, None) or msp_config.get("commodities", {}).get(crop_lower, None)
    msp_val = crop_msp_data.get("msp_per_quintal") if crop_msp_data else None
    msp_season = crop_msp_data.get("marketing_season", "Kharif 2026-27") if crop_msp_data else ""
    msp_source = msp_config.get("source", "CCEA / CACP, Govt of India")
    msp_source_url = crop_msp_data.get("source_url") if crop_msp_data else msp_config.get("source_url", "https://cacp.dacnet.nic.in")
    msp_retrieval_date = crop_msp_data.get("retrieval_date") if crop_msp_data else msp_config.get("retrieval_date", "2026-10-04")
    msp_disclaimer_en = msp_config.get("disclaimer_en", "MSP procurement depends on farmer registration and APMC procurement quotas.")
    msp_disclaimer_kn = msp_config.get("disclaimer_kn", "ಬೆಂಬಲ ಬೆಲೆ (MSP) ಖರೀದಿ ಕೇಂದ್ರಗಳ ನೋಂದಣಿ ಮತ್ತು ಸರ್ಕಾರದ ಮಿತಿಗೆ ಒಳಪಟ್ಟಿರುತ್ತದೆ.")
    msp_disclaimer_hi = msp_config.get("disclaimer_hi", "न्यूनतम समर्थन मूल्य (MSP) खरीद किसान पंजीकरण और सरकारी कोटा के अधीन है।")

    crop_en = translations.get_crop_name(crop, 'en')
    crop_kn = translations.get_crop_name(crop, 'kn')
    crop_hi = translations.get_crop_name(crop, 'hi')
    dist_kn = translations.get_district_translation(district, 'kn')
    dist_hi = translations.get_district_translation(district, 'hi')

    # Fetch live spot mandi price from Agmarknet or use live_price if explicitly provided
    live_mandi = None
    if live_price is not None:
        try:
            p_flt = float(live_price)
            if p_flt > 0:
                live_mandi = {
                    'mandi': f"{district} APMC Yard",
                    'modal_price': p_flt,
                    'min_price': p_flt,
                    'max_price': p_flt,
                    'source': 'Agmarknet / Data.gov.in',
                    'price_field': 'Modal Price'
                }
        except Exception:
            pass

    if not live_mandi:
        try:
            if agmarknet_service:
                live_mandi = agmarknet_service.fetch_live_mandi_price(canonical_crop, district) or agmarknet_service.fetch_live_mandi_price(crop_clean, district)
        except Exception as _ag_err:
            print(f"Agmarknet fetch notice: {_ag_err}")

    # Global Config Flags: When True, ML model forecasts 4-month horizon even if live APMC feed is offline
    SHOW_UNANCHORED_OUTLOOK = True

    comp_en = ""
    comp_kn = ""
    comp_hi = ""

    if live_mandi and live_mandi.get('modal_price'):
        m_name = live_mandi.get('mandi', f"{district} APMC Yard")
        m_spot = live_mandi.get('modal_price', 0.0)
        m_min = live_mandi.get('min_price', m_spot)
        m_max = live_mandi.get('max_price', m_spot)
        m_date = live_mandi.get('date', '')
        m_source = live_mandi.get('source', 'Agmarknet / Data.gov.in')
        m_field = live_mandi.get('price_field', 'Modal Price')
        is_live_feed = live_mandi.get('is_live', False) and m_date and m_date != 'Benchmark Dataset'
        
        # Jowar specific variety pricing disclosure
        variety_suffix = ""
        variety_suffix_kn = ""
        variety_suffix_hi = ""
        if 'jowar' in crop_lower or 'sorghum' in crop_lower:
            variety_suffix = " | Varieties: White Jowar (Maldandi): ~₹3,000 - ₹4,300/qtl, Hybrid Jowar: ~₹2,000 - ₹2,600/qtl in Karnataka APMCs"
            variety_suffix_kn = " | ತಳಿಗಳು: ಬಿಳಿ ಜೋಳ (ಮಾಲ್ದಂಡಿ): ~₹3,000 - ₹4,300/ಕ್ವಿಂಟಾಲ್, ಹೈಬ್ರಿಡ್ ಜೋಳ: ~₹2,000 - ₹2,600/ಕ್ವಿಂಟಾಲ್"
            variety_suffix_hi = " | किस्में: सफेद ज्वार (मालदांडी): ~₹3,000 - ₹4,300/क्विंटल, हाइब्रिड ज्वार: ~₹2,000 - ₹2,600/क्विंटल"
        elif 'wheat' in crop_lower:
            variety_suffix = " | Varieties: Sharbati / Bread Wheat (Lokwan, GW-322): ~₹2,600 - ₹3,150/qtl, Durum Wheat (UAS Dharwad DWR series): ~₹2,400 - ₹2,850/qtl in Karnataka APMCs"
            variety_suffix_kn = " | ತಳಿಗಳು: ಶರಬತಿ / ಬ್ರೆಡ್ ಗೋಧಿ (ಲೋಕವನ್, GW-322): ~₹2,600 - ₹3,150/ಕ್ವಿಂಟಾಲ್, ಡ್ಯುರಮ್ ಗೋಧಿ (ಕೃವಿವಿ ಧಾರವಾಡ DWR ತಳಿಗಳು): ~₹2,400 - ₹2,850/ಕ್ವಿಂಟಾಲ್"
            variety_suffix_hi = " | किस्में: शरबती / रोटी गेहूं (लोकवन, GW-322): ~₹2,600 - ₹3,150/क्विंटल, ड्यूरम गेहूं (यूएएस धारवाड़ DWR श्रृंखला): ~₹2,400 - ₹2,850/क्विंटल"

        date_suffix = f" | Date: {m_date}" if m_date else ""
        if is_live_feed:
            prefix_en = "⚡ Live Mandi Spot Price"
            prefix_kn = "⚡ ನೇರ ಮಂಡಿ ದರ"
            prefix_hi = "⚡ लाइव मंडी भाव"
            stale_notice_en = ""
            stale_notice_kn = ""
            stale_notice_hi = ""
        else:
            prefix_en = "📊 Reference price (not live)"
            prefix_kn = "📊 ಉಲ್ಲೇಖ ಮಂಡಿ ದರ (ಲೈವ್ ಅಲ್ಲ)"
            prefix_hi = "📊 संदर्भ मंडी भाव (लाइव नहीं)"
            stale_notice_en = "\nℹ️ Benchmark Reference Notice: Sourced from verified Karnataka APMC benchmark records (not today's live feed). Verify today's spot auction rates at your local APMC."
            stale_notice_kn = "\nℹ️ ಉಲ್ಲೇಖ ದರ ಮಾಹಿತಿ: ಇದು ಕರ್ನಾಟಕ ಎಪಿಎಂಸಿ ಐತಿಹಾಸಿಕ ಮಾನದಂಡ ದರವಾಗಿದೆ (ಇಂದಿನ ಲೈವ್ ಹರಾಜು ದರವಲ್ಲ). ಸ್ಥಳೀಯ ಎಪಿಎಂಸಿಯಲ್ಲಿ ಇಂದಿನ ದರ ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ."
            stale_notice_hi = "\nℹ️ संदर्भ भाव सूचना: यह कर्नाटक एपीएमसी ऐतिहासिक संदर्भ दर है (आज का लाइव भाव नहीं)। अपनी स्थानीय मंडी में आज का दर सत्यापित करें।"

        m_spot_kg = m_spot / 100.0
        kg_str_en = f" (≈ ₹{m_spot_kg:.2f}/kg wholesale)"
        kg_str_kn = f" (≈ ₹{m_spot_kg:.2f}/ಕೆಜಿ ಸಗಟು ದರ)"
        kg_str_hi = f" (≈ ₹{m_spot_kg:.2f}/किग्रा थोक भाव)"

        spot_clean_en = f"{prefix_en}: ₹{m_spot:.2f}/Quintal{kg_str_en} (Mandi: {m_name} | Range: ₹{m_min:.2f} - ₹{m_max:.2f}{date_suffix} | Source: {m_source}){variety_suffix}{stale_notice_en}"
        spot_clean_kn = f"{prefix_kn}: ₹{m_spot:.2f}/ಕ್ವಿಂಟಾಲ್{kg_str_kn} (ಮಂಡಿ: {m_name} | ವ್ಯಾಪ್ತಿ: ₹{m_min:.2f} - ₹{m_max:.2f}{date_suffix} | ಮೂಲ: {m_source}){variety_suffix_kn}{stale_notice_kn}"
        spot_clean_hi = f"{prefix_hi}: ₹{m_spot:.2f}/क्विंटल{kg_str_hi} (मंडी: {m_name} | दायरा: ₹{m_min:.2f} - ₹{m_max:.2f}{date_suffix} | स्रोत: {m_source}){variety_suffix_hi}{stale_notice_hi}"
    else:
        spot_clean_en = "📊 Live price is unavailable: Live price feed currently unavailable. Check your local APMC."
        spot_clean_kn = "📊 ಲೈವ್ ದರ ಲಭ್ಯವಿಲ್ಲ: ಲೈವ್ ದರ ಪ್ರಸ್ತುತ ಲಭ್ಯವಿಲ್ಲ. ನಿಮ್ಮ ಸ್ಥಳೀಯ ಎಪಿಎಂಸಿ ಮಾರುಕಟ್ಟೆಯನ್ನು ಸಂಪರ್ಕಿಸಿ."
        spot_clean_hi = "📊 लाइव भाव उपलब्ध नहीं है: लाइव भाव वर्तमान में उपलब्ध नहीं है। अपने स्थानीय एपीएमसी से संपर्क करें।"

    # Official MSP Line with provenance URL and verification status
    if msp_val:
        is_msp_live = crop_msp_data.get('is_live_fetched', False)
        last_ver_date = crop_msp_data.get('last_verified', msp_retrieval_date)
        date_provenance_en = f"Retrieved: {msp_retrieval_date}" if is_msp_live else f"Static reference data, last verified {last_ver_date}"
        date_provenance_kn = f"ಪಡೆದ ದಿನಾಂಕ: {msp_retrieval_date}" if is_msp_live else f"ಸ್ಥಿರ ಉಲ್ಲೇಖ ಮಾಹಿತಿ, ಕೊನೆಯ ಪರಿಶೀಲನೆ {last_ver_date}"
        date_provenance_hi = f"प्राप्त: {msp_retrieval_date}" if is_msp_live else f"स्थैतिक संदर्भ डेटा, अंतिम सत्यापन {last_ver_date}"

        # Jowar specific variety MSP breakdown
        jowar_msp_note_en = ""
        jowar_msp_note_kn = ""
        jowar_msp_note_hi = ""
        if 'jowar' in crop_lower or 'sorghum' in crop_lower:
            jowar_msp_note_en = " | CCEA Approved Rates: Jowar (Hybrid): ₹4,023/qtl, Jowar (Maldandi): ₹4,073/qtl (Prev Year 2025-26: ₹3,699 / ₹3,749)"
            jowar_msp_note_kn = " | ಸಿಸಿಇಎ ದರಗಳು: ಹೈಬ್ರಿಡ್ ಜೋಳ: ₹4,023/ಕ್ವಿಂಟಾಲ್, ಮಾಲ್ದಂಡಿ ಬಿಳಿ ಜೋಳ: ₹4,073/ಕ್ವಿಂಟಾಲ್ (ಹಿಂದಿನ ವರ್ಷ: ₹3,699 / ₹3,749)"
            jowar_msp_note_hi = " | सीसीईए स्वीकृत दरें: हाइब्रिड ज्वार: ₹4,023/क्विंटल, मालदांडी ज्वार: ₹4,073/क्विंटल (गत वर्ष: ₹3,699 / ₹3,749)"

        msp_str_en = f"🏛️ Govt Minimum Support Price (MSP {msp_season}): ₹{msp_val:.2f}/Quintal [Source: {msp_source} ({msp_source_url}) | {date_provenance_en}]{jowar_msp_note_en}"
        msp_str_kn = f"🏛️ ಸರ್ಕಾರಿ ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ (MSP {msp_season}): ₹{msp_val:.2f}/ಕ್ವಿಂಟಾಲ್ [ಮೂಲ: {msp_source} ({msp_source_url}) | {date_provenance_kn}]{jowar_msp_note_kn}"
        msp_str_hi = f"🏛️ सरकारी न्यूनतम समर्थन मूल्य (MSP {msp_season}): ₹{msp_val:.2f}/क्विंटल [स्रोत: {msp_source} ({msp_source_url}) | {date_provenance_hi}]{jowar_msp_note_hi}"

        # Compare Mandi Spot vs MSP if spot price available
        m_spot_val = live_mandi.get('modal_price', 0.0) if live_mandi else 0.0
        if m_spot_val > 0:
            if m_spot_val < msp_val:
                diff = msp_val - m_spot_val
                comp_en = f"\n⚠️ Mandi Spot vs MSP Comparison: Current mandi price (₹{m_spot_val:.0f}) is ₹{diff:.0f} BELOW Govt MSP (₹{msp_val:.0f}). Eligible registered farmers are strongly advised to sell at APMC Government MSP procurement centres."
                comp_kn = f"\n⚠️ ಮಂಡಿ ದರ vs ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ: ಪ್ರಸ್ತುತ ಮಂಡಿ ದರ (₹{m_spot_val:.0f}) ಸರ್ಕಾರಿ ಬೆಂಬಲ ಬೆಲೆಗಿಂತ (₹{msp_val:.0f}) ₹{diff:.0f} ಕಡಿಮೆಯಿದೆ. ರೈತರು ಎಪಿಎಂಸಿ ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ (MSP) ಖರೀದಿ ಕೇಂದ್ರಗಳಲ್ಲಿ ಮಾರಾಟ ಮಾಡಲು ಸಲಹೆ ನೀಡಲಾಗಿದೆ."
                comp_hi = f"\n⚠️ मंडी भाव बनाम एमएसपी तुलना: वर्तमान मंडी भाव (₹{m_spot_val:.0f}) सरकारी एमएसपी (₹{msp_val:.0f}) से ₹{diff:.0f} कम है। किसान सरकारी एमएसपी खरीद केंद्र पर बिक्री का लाभ उठाएं।"
            else:
                comp_en = f"\n✅ Mandi Spot vs MSP Comparison: Current mandi spot price (₹{m_spot_val:.0f}) is ABOVE Govt MSP (₹{msp_val:.0f})."
                comp_kn = f"\n✅ ಮಂಡಿ ದರ vs ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ: ಪ್ರಸ್ತುತ ಮಂಡಿ ದರ (₹{m_spot_val:.0f}) ಸರ್ಕಾರಿ ಬೆಂಬಲ ಬೆಲೆಗಿಂತ (₹{msp_val:.0f}) ಹೆಚ್ಚಾಗಿದೆ."
                comp_hi = f"\n✅ मंडी भाव बनाम एमएसपी तुलना: वर्तमान मंडी भाव (₹{m_spot_val:.0f}) सरकारी एमएसपी (₹{msp_val:.0f}) से अधिक है।"
    else:
        msp_str_en = "🏛️ Govt Minimum Support Price: No government MSP for this crop"
        msp_str_kn = "🏛️ ಸರ್ಕಾರಿ ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ: ಈ ಬೆಳೆಗೆ ಸರ್ಕಾರಿ ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ (MSP) ನಿಗದಿಯಾಗಿಲ್ಲ"
        msp_str_hi = "🏛️ सरकारी न्यूनतम समर्थन मूल्य: इस फसल के लिए कोई सरकारी न्यूनतम समर्थन मूल्य (MSP) निर्धारित नहीं है"

    # Strict Paddy vs Rice Handling: Paddy is unhusked raw Dhan (MSP mandated), whereas regression model is trained on milled Rice.
    is_paddy = crop_lower in ['paddy', 'dhan', 'paddy (common)']
    
    # Check whether a dedicated trained ML model exists for this exact commodity
    TRAINED_PRICE_COMMODITIES = {'Wheat', 'Tomato', 'Potato', 'Onion', 'Rice', 'Maize', 'Grapes', 'Apple', 'Mango', 'Banana', 'Cotton', 'Coconut'}
    
    matched_commodity = None
    if not is_paddy:
        for tc in TRAINED_PRICE_COMMODITIES:
            if crop_lower == tc.lower():
                matched_commodity = tc
                break

    # If crop is Paddy: do not show milled-rice forecast
    if is_paddy:
        paddy_note_en = "ℹ️ Note: This is the official MSP for raw Paddy (Dhan). Mandi prices for milled Rice operate under a separate commercial price structure."
        paddy_note_kn = "ℹ️ ಗಮನಿಸಿ: ಇದು ಭತ್ತದ (Dhan) ಅಧಿಕೃತ ಬೆಂಬಲ ಬೆಲೆಯಾಗಿದೆ. ಅಕ್ಕಿಯ ಮಂಡಿ ದರಗಳು ಪ್ರತ್ಯೇಕ ಮಾರುಕಟ್ಟೆ ರಚನೆಗೆ ಒಳಪಟ್ಟಿರುತ್ತವೆ."
        paddy_note_hi = "ℹ️ सूचना: यह कच्चे धान (Paddy) का आधिकारिक न्यूनतम समर्थन मूल्य है। चावल (Rice) के मंडी भाव अलग व्यावसायिक ढांचे के अधीन होते हैं।"
        
        price_en = f"{spot_clean_en}\n{msp_str_en}\n{paddy_note_en}".strip()
        price_kn = f"{spot_clean_kn}\n{msp_str_kn}\n{paddy_note_kn}".strip()
        price_hi = f"{spot_clean_hi}\n{msp_str_hi}\n{paddy_note_hi}".strip()
        
        return {
            'crop': crop,
            'district': district,
            'month': month,
            'year': year,
            'prediction': msp_val or 0.0,
            'avg_price': msp_val or 0.0,
            'min_price': msp_val or 0.0,
            'max_price': msp_val or 0.0,
            'msp': msp_val,
            'note': paddy_note_en,
            'forecast_months': [],
            'forecast_available': False,
            'live_mandi': live_mandi,
            'msp_per_quintal': msp_val,
            'msp_season': msp_season,
            'msp_source': msp_source,
            'msp_source_url': msp_source_url,
            'msp_retrieval_date': msp_retrieval_date,
            'msp_disclaimer_en': msp_disclaimer_en,
            'msp_disclaimer_kn': msp_disclaimer_kn,
            'msp_disclaimer_hi': msp_disclaimer_hi,
            'price_en': price_en,
            'price_kn': price_kn,
            'price_hi': price_hi,
            'spot_clean_en': spot_clean_en,
            'spot_clean_kn': spot_clean_kn,
            'spot_clean_hi': spot_clean_hi,
            'forecast_clean_en': paddy_note_en,
            'forecast_clean_kn': paddy_note_kn,
            'forecast_clean_hi': paddy_note_hi,
            'months_str_en': '',
            'months_str_kn': '',
            'months_str_hi': ''
        }

    MONTH_NAMES = {
        'en': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        'kn': ['ಜನ', 'ಫೆಬ್ರ', 'ಮಾರ್ಚ್', 'ಏಪ್ರಿಲ್', 'ಮೇ', 'ಜೂನ್', 'ಜುಲೈ', 'ಆಗ', 'ಸೆಪ್ಟೆಂ', 'ಅಕ್ಟೋ', 'ನವೆಂ', 'ಡಿಸೆಂ'],
        'hi': ['जन', 'फर', 'मार्च', 'अप्रैल', 'मई', 'जून', 'जुलाई', 'अग', 'सितं', 'अक्टू', 'नव', 'दिस']
    }

    forecast_prices = []
    month_labels_en = []
    month_labels_kn = []
    month_labels_hi = []

    if matched_commodity and price_model is not None:
        crop_encoded = le_commodity.transform([matched_commodity])[0]
        dist_clean = district.strip()
        if dist_clean in le_state.classes_:
            district_encoded = le_state.transform([dist_clean])[0]
        else:
            close_matches = difflib.get_close_matches(dist_clean, le_state.classes_, n=1, cutoff=0.5)
            if close_matches:
                district_encoded = le_state.transform([close_matches[0]])[0]
            else:
                district_encoded = 0

        # Start from next month and run through harvest month + 1
        start_m = (month % 12) + 1
        start_y = year if month < 12 else year + 1

        try:
            from models.agri_calendar_service import compute_harvest_range
            h_info = compute_harvest_range(crop, district=district, today=date(year, month, 1))
            latest_h_str = h_info.get('latest_harvest_date')
            if latest_h_str:
                h_d = date.fromisoformat(latest_h_str)
                end_m = (h_d.month % 12) + 1
                end_y = h_d.year if h_d.month < 12 else h_d.year + 1
            else:
                end_m = ((start_m + 3 - 1) % 12) + 1
                end_y = start_y + ((start_m + 3 - 1) // 12)
        except Exception:
            end_m = ((start_m + 3 - 1) % 12) + 1
            end_y = start_y + ((start_m + 3 - 1) // 12)

        target_seq = []
        cur_y, cur_m = start_y, start_m
        for _ in range(12):  # safeguard at most 12 months
            target_seq.append((cur_y, cur_m))
            if cur_y == end_y and cur_m == end_m:
                break
            if cur_m == 12:
                cur_y += 1
                cur_m = 1
            else:
                cur_m += 1

        for y_target, m_target in target_seq:
            feat = pd.DataFrame([[crop_encoded, district_encoded, m_target, y_target]], columns=['Commodity_Enc', 'District_Enc', 'Month', 'Year'])
            p_raw = float(price_model.predict(feat)[0])
            p_val = int(round(p_raw / 10.0) * 10)
            forecast_prices.append(p_val)

            m_name_en = MONTH_NAMES['en'][m_target - 1]
            m_name_kn = MONTH_NAMES['kn'][m_target - 1]
            m_name_hi = MONTH_NAMES['hi'][m_target - 1]

            month_labels_en.append(f"{m_name_en}: ₹{p_val}")
            month_labels_kn.append(f"{m_name_kn}: ₹{p_val}")
            month_labels_hi.append(f"{m_name_hi}: ₹{p_val}")

        avg_price = int(round(float(np.mean(forecast_prices)) / 10.0) * 10) if forecast_prices else 0
        min_price = int(round(float(np.min(forecast_prices)) / 10.0) * 10) if forecast_prices else 0
        max_price = int(round(float(np.max(forecast_prices)) / 10.0) * 10) if forecast_prices else 0
        first_month_pred = forecast_prices[0] if forecast_prices else 0
        forecast_available = True

        # Month-to-Month Jump Warning: Check sequential month transitions
        jump_warning_en = ""
        jump_warning_kn = ""
        jump_warning_hi = ""
        for idx_j in range(len(forecast_prices) - 1):
            p_curr = forecast_prices[idx_j]
            p_next = forecast_prices[idx_j + 1]
            if p_curr > 0:
                pct_change = ((p_next - p_curr) / p_curr) * 100.0
                if abs(pct_change) > PRICE_MONTH_JUMP_WARN_PCT:
                    sign = "+" if pct_change > 0 else ""
                    jump_warning_en = f"⚠️ Notice: Unusually large projected change ({sign}{pct_change:.1f}%). Treat with caution."
                    jump_warning_kn = f"⚠️ ಗಮನಿಸಿ: ಅನಿರೀಕ್ಷಿತ ದೊಡ್ಡ ಬೆಲೆ ಬದಲಾವಣೆ ({sign}{pct_change:.1f}%). ಎಚ್ಚರಿಕೆಯಿಂದ ಪರಿಗಣಿಸಿ."
                    jump_warning_hi = f"⚠️ सूचना: असामान्य रूप से बड़ा अनुमानित बदलाव ({sign}{pct_change:.1f}%)। सावधानी बरतें।"
                    break

        # Check if projected price falls below MSP in ANY month
        below_msp_warning_en = ""
        below_msp_warning_kn = ""
        below_msp_warning_hi = ""
        if msp_val and forecast_prices:
            below_months_en = []
            below_months_kn = []
            below_months_hi = []
            for idx_m, p_val in enumerate(forecast_prices):
                if p_val < msp_val:
                    diff_val = msp_val - p_val
                    y_t, m_t = target_seq[idx_m]
                    m_name_en = MONTH_NAMES['en'][m_t - 1]
                    m_name_kn = MONTH_NAMES['kn'][m_t - 1]
                    m_name_hi = MONTH_NAMES['hi'][m_t - 1]
                    below_months_en.append(f"{m_name_en} (₹{p_val} — ₹{diff_val:.0f} below MSP)")
                    below_months_kn.append(f"{m_name_kn} (₹{p_val})")
                    below_months_hi.append(f"{m_name_hi} (₹{p_val})")
            if below_months_en:
                below_msp_warning_en = f"⚠️ Price Trend Warning: Projected price falls BELOW Govt MSP (₹{msp_val:.0f}/qtl) in: {', '.join(below_months_en)}. Eligible farmers are advised to register for APMC Government MSP procurement to avoid market loss."
                below_msp_warning_kn = f"⚠️ ಬೆಲೆ ಪ್ರವೃತ್ತಿ ಎಚ್ಚರಿಕೆ: ಮುನ್ಸೂಚನೆಯ ದರವು ಸರ್ಕಾರಿ ಬೆಂಬಲ ಬೆಲೆಗಿಂತ (₹{msp_val:.0f}) ಕಡಿಮೆಯಾಗುವ ಸಾಧ್ಯತೆಯಿದೆ ({', '.join(below_months_kn)}). ರೈತರು ಎಪಿಎಂಸಿ ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ (MSP) ಖರೀದಿ ಕೇಂದ್ರಗಳಲ್ಲಿ ನೋಂದಾಯಿಸಿ ಮಾರಾಟ ಮಾಡಲು ಸಲಹೆ ನೀಡಲಾಗಿದೆ."
                below_msp_warning_hi = f"⚠️ मूल्य रुझान चेतावनी: अनुमानित मंडी भाव सरकारी एमएसपी (₹{msp_val:.0f}/क्विंटल) से नीचे जा सकता है ({', '.join(below_months_hi)})। किसान संकटपूर्ण बिक्री से बचें और सरकारी खरीद केंद्रों पर बिक्री करें।"

        months_str_en = " | ".join(month_labels_en)
        months_str_kn = " | ".join(month_labels_kn)
        months_str_hi = " | ".join(month_labels_hi)

        crop_display_label = "Rice (milled)" if matched_commodity == "Rice" else crop_en
        horizon_label_en = f"📈 Estimated Price Trend (Estimated trend, not a guarantee — historical seasonal projection): Avg ₹{avg_price} (Range: ₹{min_price} - ₹{max_price}) [{months_str_en}]"
        horizon_label_kn = f"📈 ಅಂದಾಜು ಬೆಲೆ ಪ್ರವೃತ್ತಿ (ಅಂದಾಜು ಪ್ರವೃತ್ತಿ, ಗ್ಯಾರಂಟಿ ಅಲ್ಲ — ಐತಿಹಾಸಿಕ ಋತುಮಾನ ಪ್ರಕ್ಷೇಪಣೆ): ಸರಾಸರಿ ₹{avg_price} (ವ್ಯಾಪ್ತಿ: ₹{min_price} - ₹{max_price}) [{months_str_kn}]"
        horizon_label_hi = f"📈 अनुमानित मूल्य रुझान (अनुमानित रुझान, कोई गारंटी नहीं — ऐतिहासिक मौसमी अनुमान): औसत ₹{avg_price} (दायरा: ₹{min_price} - ₹{max_price}) [{months_str_hi}]"

        forecast_clean_en = f"{horizon_label_en}\n{below_msp_warning_en}\n{jump_warning_en}".strip()
        forecast_clean_kn = f"{horizon_label_kn}\n{below_msp_warning_kn}\n{jump_warning_kn}".strip()
        forecast_clean_hi = f"{horizon_label_hi}\n{below_msp_warning_hi}\n{jump_warning_hi}".strip()

    else:
        # Show price trend ONLY when real multi-year history exists; otherwise "Insufficient data"
        avg_price = 0
        min_price = 0
        max_price = 0
        first_month_pred = 0
        forecast_prices = []
        forecast_available = False
        jump_warning_en = ""
        jump_warning_kn = ""
        jump_warning_hi = ""
        below_msp_warning_en = ""
        below_msp_warning_kn = ""
        below_msp_warning_hi = ""
        months_str_en = ""
        months_str_kn = ""
        months_str_hi = ""

        horizon_label_en = "📈 Estimated Price Trend: Insufficient data"
        horizon_label_kn = "📈 ಅಂದಾಜು ಬೆಲೆ ಪ್ರವೃತ್ತಿ: ಸಾಕಷ್ಟು ಐತಿಹಾಸಿಕ ದತ್ತಾಂಶ ಲಭ್ಯವಿಲ್ಲ"
        horizon_label_hi = "📈 अनुमानित मूल्य रुझान: अपर्याप्त ऐतिहासिक डेटा"

        forecast_clean_en = horizon_label_en
        forecast_clean_kn = horizon_label_kn
        forecast_clean_hi = horizon_label_hi

    price_en = f"{spot_clean_en}\n{msp_str_en}{comp_en}\n{forecast_clean_en}".strip()
    price_kn = f"{spot_clean_kn}\n{msp_str_kn}{comp_kn}\n{forecast_clean_kn}".strip()
    price_hi = f"{spot_clean_hi}\n{msp_str_hi}{comp_hi}\n{forecast_clean_hi}".strip()

    return {
        'crop': crop,
        'district': district,
        'month': month,
        'year': year,
        'prediction': first_month_pred,
        'avg_price': avg_price,
        'min_price': min_price,
        'max_price': max_price,
        'msp': msp_val,
        'forecast_months': forecast_prices,
        'forecast_available': forecast_available,
        'jump_warning_en': jump_warning_en,
        'below_msp_warning_en': below_msp_warning_en,
        'below_msp_warning_kn': below_msp_warning_kn,
        'below_msp_warning_hi': below_msp_warning_hi,
        'live_mandi': live_mandi,
        'msp_per_quintal': msp_val,
        'msp_season': msp_season,
        'msp_source': msp_source,
        'msp_source_url': msp_source_url,
        'msp_retrieval_date': msp_retrieval_date,
        'msp_disclaimer_en': msp_disclaimer_en,
        'msp_disclaimer_kn': msp_disclaimer_kn,
        'msp_disclaimer_hi': msp_disclaimer_hi,
        'price_en': price_en,
        'price_kn': price_kn,
        'price_hi': price_hi,
        'spot_clean_en': spot_clean_en,
        'spot_clean_kn': spot_clean_kn,
        'spot_clean_hi': spot_clean_hi,
        'forecast_clean_en': forecast_clean_en,
        'forecast_clean_kn': forecast_clean_kn,
        'forecast_clean_hi': forecast_clean_hi,
        'months_str_en': months_str_en,
        'months_str_kn': months_str_kn,
        'months_str_hi': months_str_hi
    }


# ===============================
# FarmContext Lifecycle Engine
# ===============================
def get_farm_context():
    """Retrieves or initializes the active FarmContext object for the session with 2-hour inactivity expiry."""
    ctx = session.get('farm_context')
    now = datetime.now()
    if ctx and isinstance(ctx, dict):
        last_updated_str = ctx.get('last_updated')
        if last_updated_str:
            try:
                last_updated = datetime.fromisoformat(last_updated_str)
                if (now - last_updated).total_seconds() > 7200:  # 2 hours expiry
                    ctx = None
            except Exception:
                pass

    if not ctx or not isinstance(ctx, dict):
        ctx = {
            'session_id': session.get('_id', str(now.timestamp())),
            'created_at': now.isoformat(),
            'last_updated': now.isoformat(),
            'crop': session.get('recommended_crop', ''),
            'crop_key': session.get('recommended_crop', '').lower(),
            'district': session.get('selected_district', '') or session.get('city', ''),
            'season': session.get('selected_season', 'auto'),
            'current_date': now.strftime("%Y-%m-%d"),
            'sowing_date': session.get('sowing_date', ''),
            'days_after_sowing': session.get('days_after_sowing', None),
            'sowing_status': session.get('sowing_status', 'open'),
            'soil': session.get('crop_form_data', {}),
            'irrigation': session.get('irrigation_data', {}),
            'latest_disease': {
                'crop_key': session.get('predicted_crop', '').lower(),
                'disease_name': session.get('predicted_disease', ''),
                'timestamp': session.get('disease_timestamp', '')
            }
        }
        session['farm_context'] = ctx
    return ctx

def update_farm_context(**kwargs):
    """Updates fields in the unified FarmContext and auto-syncs session keys."""
    ctx = get_farm_context()
    for k, v in kwargs.items():
        ctx[k] = v
    ctx['last_updated'] = datetime.now().isoformat()
    session['farm_context'] = ctx
    return ctx

def invalidate_dependent_farm_context(new_crop=None, new_district=None):
    """Clears cross-crop and cross-district stale state when primary crop or district changes."""
    ctx = get_farm_context()
    curr_crop = ctx.get('crop_key', '')
    curr_dist = ctx.get('district', '')
    
    if new_crop and new_crop.lower() != curr_crop.lower():
        session.pop('predicted_disease', None)
        session.pop('disease_result', None)
        session.pop('disease_result_en', None)
        session.pop('disease_result_kn', None)
        session.pop('disease_result_hi', None)
        session.pop('planner_ai_plan', None)
        ctx['latest_disease'] = {'crop_key': '', 'disease_name': '', 'timestamp': ''}
        ctx['crop'] = new_crop
        ctx['crop_key'] = new_crop.lower()

    if new_district and new_district.lower() != curr_dist.lower():
        session.pop('price_result_en', None)
        session.pop('price_result_kn', None)
        session.pop('price_result_hi', None)
        session.pop('planner_ai_plan', None)
        ctx['district'] = new_district
        
    session['farm_context'] = ctx

def render_markdown_safe(text):
    """Sanitizes text and converts markdown bold/lists to clean HTML without raw markdown display."""
    if not text:
        return ""
    import html
    escaped = html.escape(str(text))
    escaped = re.sub(r'###\s*(.*?)(?:\n|$)', r'<h4 class="plan-subheading">\1</h4>', escaped)
    escaped = re.sub(r'##\s*(.*?)(?:\n|$)', r'<h3 class="plan-heading">\1</h3>', escaped)
    escaped = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', escaped)
    escaped = re.sub(r'(?m)^[\s]*[•\-]\s*(.*?)$', r'<li>\1</li>', escaped)
    escaped = re.sub(r'(<li>.*?</li>\s*)+', r'<ul class="plan-list">\g<0></ul>', escaped, flags=re.DOTALL)
    escaped = escaped.replace('\n\n', '<br/><br/>').replace('\n', '<br/>')
    return escaped

def get_session_data():
    lang = session.get('lang', 'en')
    rec_crop = session.get('recommended_crop', '')
    rec_crop_l = rec_crop.lower().strip() if rec_crop else ''
    c_meta = translations.CROP_TRANSLATIONS.get(rec_crop_l, translations.CROP_TRANSLATIONS['default'])
    
    crop_tr_en = translations.get_crop_name(rec_crop, 'en') if rec_crop else ''
    crop_tr_kn = translations.get_crop_name(rec_crop, 'kn') if rec_crop else ''
    crop_tr_hi = translations.get_crop_name(rec_crop, 'hi') if rec_crop else ''

    price = session.get('predicted_price', 0)

    # Schedules & Plans derived dynamically
    if rec_crop:
        plant_en = f"🌱 Best planting months for {crop_tr_en.upper()}: {c_meta['planting_months']['en']}"
        plant_kn = f"🌱 {crop_tr_kn.upper()} ಬಿತ್ತನೆಗೆ ಉತ್ತಮ ಸಮಯ: {c_meta['planting_months']['kn']}"
        plant_hi = f"🌱 {crop_tr_hi.upper()} की बुवाई का सर्वोत्तम समय: {c_meta['planting_months']['hi']}"

        harv_en = f"🌾 Expected harvest months: {c_meta['harvest_months']['en']}"
        harv_kn = f"🌾 ನಿರೀಕ್ಷಿತ ಕೊಯ್ಲು ತಿಂಗಳುಗಳು: {c_meta['harvest_months']['kn']}"
        harv_hi = f"🌾 कटाई के अनुमानित महीने: {c_meta['harvest_months']['hi']}"

        fert_en = f"🌿 Fertilizer plan for {crop_tr_en.upper()}: {c_meta['fertilizer']['en']}"
        fert_kn = f"🌿 {crop_tr_kn.upper()} ಗೊಬ್ಬರದ ಪ್ರಮಾಣ: {c_meta['fertilizer']['kn']}"
        fert_hi = f"🌿 {crop_tr_hi.upper()} उर्वरक योजना: {c_meta['fertilizer']['hi']}"

        pests_en = c_meta['pests']['en']
        pests_kn = c_meta['pests']['kn']
        pests_hi = c_meta['pests']['hi']

        price_res_en = session.get('price_result_en', '')
        price_res_kn = session.get('price_result_kn', '')
        price_res_hi = session.get('price_result_hi', '')

        spot_clean_en = session.get('price_spot_clean_en', '')
        forecast_clean_en = session.get('price_forecast_clean_en', '')
        spot_clean_kn = session.get('price_spot_clean_kn', '')
        forecast_clean_kn = session.get('price_forecast_clean_kn', '')
        spot_clean_hi = session.get('price_spot_clean_hi', '')
        forecast_clean_hi = session.get('price_forecast_clean_hi', '')

        if spot_clean_en:
            sell_en = f"{spot_clean_en}\n\n{forecast_clean_en}\n\n💡 Peak Selling Months: {c_meta['best_sell_months']['en']}. {c_meta['sell_tip']['en']}"
            sell_kn = f"{spot_clean_kn or spot_clean_en}\n\n{forecast_clean_kn or forecast_clean_en}\n\n💡 ಮಾರಾಟಕ್ಕೆ ಸೂಕ್ತ ತಿಂಗಳುಗಳು: {c_meta['best_sell_months']['kn']}. {c_meta['sell_tip']['kn']}"
            sell_hi = f"{spot_clean_hi or spot_clean_en}\n\n{forecast_clean_hi or forecast_clean_en}\n\n💡 बेचने के सर्वोत्तम महीने: {c_meta['best_sell_months']['hi']}। {c_meta['sell_tip']['hi']}"
        elif price_res_en:
            sell_en = f"💰 {price_res_en}\n\n💡 Peak Selling Months: {c_meta['best_sell_months']['en']}. {c_meta['sell_tip']['en']}"
            sell_kn = f"💰 {price_res_kn or price_res_en}\n\n💡 ಮಾರಾಟಕ್ಕೆ ಸೂಕ್ತ ತಿಂಗಳುಗಳು: {c_meta['best_sell_months']['kn']}. {c_meta['sell_tip']['kn']}"
            sell_hi = f"💰 {price_res_hi or price_res_en}\n\n💡 बेचने के सर्वोत्तम महीने: {c_meta['best_sell_months']['hi']}। {c_meta['sell_tip']['hi']}"
        else:
            sell_en = f"💰 Best selling months for {crop_tr_en.upper()}: {c_meta['best_sell_months']['en']}.\n💡 Strategy: {c_meta['sell_tip']['en']}"
            sell_kn = f"💰 {crop_tr_kn.upper()} ಮಾರಾಟಕ್ಕೆ ಸೂಕ್ತ ತಿಂಗಳುಗಳು: {c_meta['best_sell_months']['kn']}.\n💡 ಸಲಹೆ: {c_meta['sell_tip']['kn']}"
            sell_hi = f"💰 {crop_tr_hi.upper()} बेचने के सर्वोत्तम महीने: {c_meta['best_sell_months']['hi']}।\n💡 रणनीति: {c_meta['sell_tip']['hi']}"
    else:
        plant_en, plant_kn, plant_hi = '', '', ''
        harv_en, harv_kn, harv_hi = '', '', ''
        fert_en, fert_kn, fert_hi = '', '', ''
        pests_en, pests_kn, pests_hi = [], [], []
        sell_en, sell_kn, sell_hi = '', '', ''

    now_dt = datetime.now()
    cur_m_str = str(now_dt.month)
    cur_y_str = str(now_dt.year)

    effective_price_form = dict(session.get('price_form_data', {}))
    if not effective_price_form.get('month'):
        effective_price_form['month'] = cur_m_str
    if not effective_price_form.get('year'):
        effective_price_form['year'] = cur_y_str
    if not effective_price_form.get('crop') and rec_crop:
        effective_price_form['crop'] = rec_crop
    if not effective_price_form.get('district') and (session.get('selected_district') or session.get('city')):
        effective_price_form['district'] = session.get('selected_district') or session.get('city')

    effective_irrigation_form = dict(session.get('irrigation_form_data', {}))
    if not effective_irrigation_form.get('crop') and rec_crop:
        effective_irrigation_form['crop'] = rec_crop
    if not effective_irrigation_form.get('district') and (session.get('selected_district') or session.get('city')):
        effective_irrigation_form['district'] = session.get('selected_district') or session.get('city')

    return dict(
        lang=lang,
        crop_result=session.get(f'crop_result_{lang}') or session.get('crop_result'),
        crop_result_en=session.get('crop_result_en') or session.get('crop_result'),
        crop_result_kn=session.get('crop_result_kn') or session.get('crop_result'),
        crop_result_hi=session.get('crop_result_hi') or session.get('crop_result'),

        weather_info=session.get(f'weather_info_{lang}') or session.get('weather_info'),
        weather_info_en=session.get('weather_info_en') or session.get('weather_info'),
        weather_info_kn=session.get('weather_info_kn') or session.get('weather_info'),
        weather_info_hi=session.get('weather_info_hi') or session.get('weather_info'),

        price_result=session.get(f'price_result_{lang}') or session.get('price_result'),
        price_result_en=session.get('price_result_en') or session.get('price_result'),
        price_result_kn=session.get('price_result_kn') or session.get('price_result'),
        price_result_hi=session.get('price_result_hi') or session.get('price_result'),

        disease_result=session.get(f'disease_result_{lang}') or session.get('disease_result'),
        disease_result_en=session.get('disease_result_en') or session.get('disease_result'),
        disease_result_kn=session.get('disease_result_kn') or session.get('disease_result'),
        disease_result_hi=session.get('disease_result_hi') or session.get('disease_result'),

        uploaded_image=session.get('uploaded_image'),

        # New session values
        recommended_crop=rec_crop,
        recommended_crop_tr=crop_tr_kn if lang == 'kn' else (crop_tr_hi if lang == 'hi' else crop_tr_en),
        recommended_crop_en=crop_tr_en,
        recommended_crop_kn=crop_tr_kn,
        recommended_crop_hi=crop_tr_hi,

        recommended_crop_season=session.get(f'recommended_crop_season_{lang}') or session.get('recommended_crop_season'),
        recommended_crop_season_en=session.get('recommended_crop_season_en') or session.get('recommended_crop_season'),
        recommended_crop_season_kn=session.get('recommended_crop_season_kn') or session.get('recommended_crop_season'),
        recommended_crop_season_hi=session.get('recommended_crop_season_hi') or session.get('recommended_crop_season'),

        season_advice=session.get(f'season_advice_{lang}') or session.get('season_advice'),
        season_advice_en=session.get('season_advice_en') or session.get('season_advice'),
        season_advice_kn=session.get('season_advice_kn') or session.get('season_advice'),
        season_advice_hi=session.get('season_advice_hi') or session.get('season_advice'),

        selected_district=session.get('selected_district', ''),
        selected_season=session.get('selected_season', 'auto'),
        predicted_crop=session.get('predicted_crop'),
        price_crop=session.get("price_crop"),
        price_crop_kn=translations.get_crop_name(session.get("price_crop", ""), 'kn') if session.get("price_crop") else '',
        price_crop_hi=translations.get_crop_name(session.get("price_crop", ""), 'hi') if session.get("price_crop") else '',
        predicted_price=session.get('predicted_price'),
        predicted_disease=session.get('predicted_disease'),
        predicted_disease_en=translations.get_disease_translation(session.get('predicted_crop', 'Crop'), session.get('predicted_disease', ''), 'en') if session.get('predicted_disease') else '',
        predicted_disease_kn=translations.get_disease_translation(session.get('predicted_crop', 'Crop'), session.get('predicted_disease', ''), 'kn') if session.get('predicted_disease') else '',
        predicted_disease_hi=translations.get_disease_translation(session.get('predicted_crop', 'Crop'), session.get('predicted_disease', ''), 'hi') if session.get('predicted_disease') else '',
        city=session.get('city'),
        city_kn=translations.get_district_translation(session.get('city', ''), 'kn') if session.get('city') else '',
        city_hi=translations.get_district_translation(session.get('city', ''), 'hi') if session.get('city') else '',

        planner_summary=session.get(f'planner_summary_{lang}') or session.get('planner_summary'),
        planner_summary_en=session.get('planner_summary_en') or session.get('planner_summary'),
        planner_summary_kn=session.get('planner_summary_kn') or session.get('planner_summary'),
        planner_summary_hi=session.get('planner_summary_hi') or session.get('planner_summary'),

        planner_advice=session.get(f'planner_advice_{lang}') or session.get('planner_advice'),
        planner_advice_en=session.get('planner_advice_en') or session.get('planner_advice'),
        planner_advice_kn=session.get('planner_advice_kn') or session.get('planner_advice'),
        planner_advice_hi=session.get('planner_advice_hi') or session.get('planner_advice'),

        planner_alerts=session.get(f'planner_alerts_{lang}') or session.get('planner_alerts'),
        planner_alerts_en=session.get('planner_alerts_en') or session.get('planner_alerts'),
        planner_alerts_kn=session.get('planner_alerts_kn') or session.get('planner_alerts'),
        planner_alerts_hi=session.get('planner_alerts_hi') or session.get('planner_alerts'),

        planner_priority=session.get(f'planner_priority_{lang}') or session.get('planner_priority'),
        planner_priority_en=session.get('planner_priority_en') or session.get('planner_priority'),
        planner_priority_kn=session.get('planner_priority_kn') or session.get('planner_priority'),
        planner_priority_hi=session.get('planner_priority_hi') or session.get('planner_priority'),

        planner_ai_plan=session.get(f'planner_ai_plan_{lang}') or session.get('planner_ai_plan'),
        planner_ai_plan_en=session.get('planner_ai_plan_en') or session.get('planner_ai_plan'),
        planner_ai_plan_kn=session.get('planner_ai_plan_kn') or session.get('planner_ai_plan'),
        planner_ai_plan_hi=session.get('planner_ai_plan_hi') or session.get('planner_ai_plan'),
        planner_ai_provider=session.get('planner_ai_provider', 'SmartAgri AI Engine'),

        top_crops=session.get('top_crops', []),
        preferred_crop_reason=session.get(f'preferred_crop_reason_{lang}') or session.get('preferred_crop_reason'),
        preferred_crop_reason_en=session.get('preferred_crop_reason_en'),
        preferred_crop_reason_kn=session.get('preferred_crop_reason_kn'),
        preferred_crop_reason_hi=session.get('preferred_crop_reason_hi'),

        planting_schedule=plant_kn if lang == 'kn' else (plant_hi if lang == 'hi' else plant_en),
        planting_schedule_en=plant_en,
        planting_schedule_kn=plant_kn,
        planting_schedule_hi=plant_hi,

        harvest_schedule=harv_kn if lang == 'kn' else (harv_hi if lang == 'hi' else harv_en),
        harvest_schedule_en=harv_en,
        harvest_schedule_kn=harv_kn,
        harvest_schedule_hi=harv_hi,

        fertilizer_plan=fert_kn if lang == 'kn' else (fert_hi if lang == 'hi' else fert_en),
        fertilizer_plan_en=fert_en,
        fertilizer_plan_kn=fert_kn,
        fertilizer_plan_hi=fert_hi,

        pest_guide=pests_kn if lang == 'kn' else (pests_hi if lang == 'hi' else pests_en),
        pest_guide_en=pests_en,
        pest_guide_kn=pests_kn,
        pest_guide_hi=pests_hi,

        sell_recommendation=sell_kn if lang == 'kn' else (sell_hi if lang == 'hi' else sell_en),
        sell_recommendation_en=sell_en,
        sell_recommendation_kn=sell_kn,
        sell_recommendation_hi=sell_hi,

        # Irrigation Agent Session Data
        irrigation_data=session.get('irrigation_data'),
        irrigation_result=session.get(f'irrigation_result_{lang}') or session.get('irrigation_result'),
        irrigation_result_en=session.get('irrigation_result_en'),
        irrigation_result_kn=session.get('irrigation_result_kn'),
        irrigation_result_hi=session.get('irrigation_result_hi'),
        irrigation_crop=session.get('irrigation_crop') or session.get('recommended_crop') or '',
        irrigation_stage=session.get('irrigation_stage', 'vegetative'),
        irrigation_soil=session.get('irrigation_soil', 'loam'),
        irrigation_area=session.get('irrigation_area', '1.0'),
        irrigation_method=session.get('irrigation_method', 'drip'),
        irrigation_district=session.get('irrigation_district') or session.get('selected_district') or session.get('city') or '',
        growth_stages_tr=translations.GROWTH_STAGES_TR,
        soil_types_tr=translations.SOIL_TYPES_TR,
        irrigation_methods_tr=translations.IRRIGATION_METHODS_TR,

        query_answer=session.get(f'query_answer_{lang}') or session.get('query_answer'),
        query_answer_en=session.get('query_answer_en') or session.get('query_answer'),
        query_answer_kn=session.get('query_answer_kn') or session.get('query_answer'),
        query_answer_hi=session.get('query_answer_hi') or session.get('query_answer'),

        crop_form_data=session.get('crop_form_data', {}),
        price_form_data=effective_price_form,
        current_month=cur_m_str,
        current_year=cur_y_str,
        disease_form_data=session.get('disease_form_data', {}),
        irrigation_form_data=effective_irrigation_form,
        crop_disease_samples=translations.get_crop_disease_samples(rec_crop, lang) if rec_crop else [],
        is_disease_supported=translations.is_disease_diagnosis_supported(rec_crop) if rec_crop else False,
        disease_notice=translations.get_crop_support_notice(rec_crop, lang) if rec_crop else translations.get_crop_support_notice('soybean', lang),
        disease_notice_en=translations.get_crop_support_notice(rec_crop, 'en') if rec_crop else translations.get_crop_support_notice('soybean', 'en'),
        disease_notice_kn=translations.get_crop_support_notice(rec_crop, 'kn') if rec_crop else translations.get_crop_support_notice('soybean', 'kn'),
        disease_notice_hi=translations.get_crop_support_notice(rec_crop, 'hi') if rec_crop else translations.get_crop_support_notice('soybean', 'hi'),
        disease_coverage_line=translations.get_disease_coverage_line(lang),
        disease_coverage_line_en=translations.get_disease_coverage_line('en'),
        disease_coverage_line_kn=translations.get_disease_coverage_line('kn'),
        disease_coverage_line_hi=translations.get_disease_coverage_line('hi'),
        disease_crops_grouped=translations.get_disease_crops_grouped(lang),
        disease_panel_texts=translations.DISEASE_PANEL_TEXTS,
        disease_confidence_threshold=translations.DISEASE_CONFIDENCE_THRESHOLD,
        query_text=session.get('query_text', ''),
        district_translations=translations.DISTRICT_TRANSLATIONS,
        commodity_translations=translations.COMMODITY_TRANSLATIONS,
        crops=KARNATAKA_CROPS,
        karnataka_crops=KARNATAKA_CROPS,
        districts=KARNATAKA_DISTRICTS,
        states=KARNATAKA_DISTRICTS
    )
# ── Simple user database ──────────────────────────────────────────────────────
# In real project use a proper database
users = {
    'farmer1':  {'password': 'farmer123',  'type': 'farmer',  'name': 'Raju'},
    'officer1': {'password': 'officer123', 'type': 'officer', 'name': 'Mr. Sharma'},
    'admin':    {'password': 'admin123',   'type': 'admin',   'name': 'Admin'}
}

# ===============================
# Login Route
# ===============================
# ── Persistent user storage ───────────────────────────────────────────────────
USERS_FILE = 'users.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

# ===============================
# Login Route
# ===============================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users     = load_users()
        username  = request.form.get('username', '').strip()
        password  = request.form.get('password', '').strip()
        is_api = request.headers.get('Accept') == 'application/json' or request.is_json or 'fetch' in request.headers.get('Sec-Fetch-Mode', '')

        if username in users and users[username]['password'] == password:
            session['logged_in']  = True
            session['username']   = username
            session['user_type']  = users[username]['type']
            session['user_name']  = users[username]['name']
            if is_api:
                return jsonify({
                    "status": "success",
                    "username": username,
                    "user_name": users[username]['name'],
                    "user_type": users[username]['type']
                })
            return redirect('/')
        else:
            if is_api:
                return jsonify({"error": "Invalid username or password. Please try again."}), 401
            return render_template(
                'login.html',
                error='Invalid username or password. Please try again.'
            )

    if os.path.exists(os.path.join(REACT_DIST_DIR, 'index.html')):
        return send_from_directory(REACT_DIST_DIR, 'index.html')
    return render_template('login.html')

# ===============================
# Register Route
# ===============================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users     = load_users()
        username  = request.form.get('username', '').strip()
        password  = request.form.get('password', '').strip()
        confirm   = request.form.get('confirm_password', '').strip()
        full_name = request.form.get('full_name', '').strip()
        user_type = request.form.get('user_type', 'farmer')
        is_api = request.headers.get('Accept') == 'application/json' or request.is_json or 'fetch' in request.headers.get('Sec-Fetch-Mode', '')

        if not username or not password or not full_name:
            if is_api:
                return jsonify({"error": "All fields are required."}), 400
            return render_template('register.html', error='All fields are required.')

        if username in users:
            if is_api:
                return jsonify({"error": "Username already exists. Please choose another."}), 400
            return render_template('register.html', error='Username already exists. Please choose another.')

        if password != confirm:
            if is_api:
                return jsonify({"error": "Passwords do not match."}), 400
            return render_template('register.html', error='Passwords do not match.')

        if len(password) < 6:
            if is_api:
                return jsonify({"error": "Password must be at least 6 characters."}), 400
            return render_template('register.html', error='Password must be at least 6 characters.')

        users[username] = {
            'password': password,
            'type': user_type,
            'name': full_name
        }
        save_users(users)

        if is_api:
            return jsonify({"status": "success", "message": "Account created successfully! Please log in."})
        return render_template('login.html', success='Account created successfully! Please log in.')

    if os.path.exists(os.path.join(REACT_DIST_DIR, 'index.html')):
        return send_from_directory(REACT_DIST_DIR, 'index.html')
    return render_template('register.html')

# ===============================
# Logout Route
# ===============================
@app.route('/logout')
def logout():
    session.clear()
    if request.headers.get('Accept') == 'application/json' or 'fetch' in request.headers.get('Sec-Fetch-Mode', ''):
        return jsonify({"status": "logged_out"})
    return redirect('/login')

# ===============================
# Home & SPA Assets Routes
# ===============================
@app.route('/')
def home():
    if os.path.exists(os.path.join(REACT_DIST_DIR, 'index.html')):
        return send_from_directory(REACT_DIST_DIR, 'index.html')

    # Fallback to server-rendered template if React dist not built
    if not session.get('logged_in'):
        return redirect('/login')

    return render_template(
        "index.html",
        user_name=session.get('user_name', 'Farmer'),
        user_type=session.get('user_type', 'farmer'),
        **get_session_data()
    )

@app.route('/price-result')
def price_result():
    if os.path.exists(os.path.join(REACT_DIST_DIR, 'index.html')):
        return send_from_directory(REACT_DIST_DIR, 'index.html')
    return redirect('/')

@app.route('/assets/<path:path>')
def serve_react_assets(path):
    assets_dir = os.path.join(REACT_DIST_DIR, 'assets')
    if os.path.exists(assets_dir):
        return send_from_directory(assets_dir, path)
    return jsonify({"error": "Asset not found"}), 404

@app.route('/vite.svg')
def serve_vite_svg():
    if os.path.exists(os.path.join(REACT_DIST_DIR, 'vite.svg')):
        return send_from_directory(REACT_DIST_DIR, 'vite.svg')
    return '', 404
# ===============================
# Crop Recommendation
# ===============================
@app.route('/predict_crop', methods=['POST'])
def predict_crop():
    try:
        req_json = request.get_json(silent=True) or {}
        lang = request.form.get('lang') or req_json.get('lang') or request.args.get('lang') or session.get('lang', 'en')
        session['lang'] = lang

        district = request.form.get('district', '').strip() or request.form.get('city', '').strip() or 'Bengaluru Urban'
        season = request.form.get('season', 'auto').strip()

        crop_form_data = {
            'nitrogen': request.form.get('nitrogen', ''),
            'phosphorus': request.form.get('phosphorus', ''),
            'potassium': request.form.get('potassium', ''),
            'ph': request.form.get('ph', ''),
            'rainfall': request.form.get('rainfall', ''),
            'city': district,
            'district': district,
            'season': season
        }
        session['crop_form_data'] = crop_form_data
        session['selected_district'] = district
        session['selected_season'] = season

        from models.agri_calendar_service import get_current_date
        eval_today = get_current_date()

        # Wire IMD 30-year normal rainfall for selected district and current month
        norm_rain = get_district_monthly_rainfall(district, eval_today.month)
        if norm_rain is not None:
            rainfall = norm_rain

        def safe_float(val, default):
            try:
                v = float(val)
                return v if v > 0 else default
            except (ValueError, TypeError):
                return default

        N        = safe_float(request.form.get('nitrogen'), 55.0)
        P        = safe_float(request.form.get('phosphorus'), 42.0)
        K        = safe_float(request.form.get('potassium'), 35.0)
        ph       = safe_float(request.form.get('ph'), 6.8)
        if norm_rain is None:
            rainfall = safe_float(request.form.get('rainfall'), 75.0)

        query_city = DISTRICT_WEATHER_CITY.get(district, district)

        API_KEY = "b9592880d7ec9f2a8e4de876eaa84c09"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={query_city},IN&appid={API_KEY}&units=metric"
        try:
            response = requests.get(url, timeout=3.0)
            data     = response.json()
        except Exception:
            data     = {}

        if data.get("cod") != 200:
            fallback_weather = district_weather_fallback.get(district, {'temp': 25, 'humidity': 60})
            weather_temp     = fallback_weather['temp']
            weather_humidity = fallback_weather['humidity']
            weather_desc     = 'Clear Sky'
        else:
            weather_temp     = data["main"]["temp"]
            weather_humidity = data["main"]["humidity"]
            weather_desc     = data["weather"][0]["description"]

        weather_info_en = translations.format_weather_status(district, weather_temp, weather_humidity, weather_desc, 'en')
        weather_info_kn = translations.format_weather_status(district, weather_temp, weather_humidity, weather_desc, 'kn')
        weather_info_hi = translations.format_weather_status(district, weather_temp, weather_humidity, weather_desc, 'hi')

        input_features = np.array([[N, P, K, weather_temp, weather_humidity, ph, rainfall]])
        input_scaled   = crop_scaler.transform(input_features)
        
        # Ensure only crops grown in Karnataka and suited to the selected district and season are recommended
        NON_KARNATAKA_CROPS = {'jute'}
        district_key = district.strip()

        # Determine active season
        active_season = season
        if not active_season or active_season == 'auto':
            current_m = datetime.now().month
            if 6 <= current_m <= 10:
                active_season = 'Kharif'
            elif current_m in [11, 12, 1, 2]:
                active_season = 'Rabi'
            else:
                active_season = 'Zaid'

        active_season_l = active_season.lower()
        district_profile = KARNATAKA_DISTRICT_SEASON_CROPS.get(
            district_key,
            KARNATAKA_DISTRICT_SEASON_CROPS.get('Dharwad', {
                'kharif': ['cotton', 'soybean', 'maize'],
                'rabi': ['chickpea', 'jowar', 'wheat'],
                'zaid': ['tomato', 'groundnut', 'maize']
            })
        )

        from models.agri_calendar_service import (
            normalize_crop_name, get_sowing_status, get_district_institution,
            compute_harvest_range, PERENNIAL_CROPS
        )

        # Candidates strictly from KARNATAKA_DISTRICT_SEASON_CROPS for the selected district and season
        # Normalized with crop alias mapping to merge duplicates
        raw_season_crops = district_profile.get(active_season_l, [])
        candidate_crops = []
        seen_candidates = set()
        for c in raw_season_crops:
            c_canon = normalize_crop_name(c)
            if c_canon not in seen_candidates and c_canon not in NON_KARNATAKA_CROPS and c_canon not in PERENNIAL_CROPS:
                seen_candidates.add(c_canon)
                candidate_crops.append(c_canon)

        # 1. Gather Candidate Crops and score dynamically using live weather & calibrated sowing status
        scored_candidates = []
        try:
            for crop_name in candidate_crops:
                sow_st = get_sowing_status(crop_name, active_season, today=eval_today, district=district)
                st = sow_st.get('status')

                # Strictly keep only open, closing_soon, or late_sowing; drop passed and not_started / no_window
                if st not in ['open', 'closing_soon', 'late_sowing']:
                    continue

                # Weather preferability evaluation against live weather (omits rainfall sentence if norm_rain is None)
                w_eval = translations.evaluate_crop_weather_suitability(
                    crop_name=crop_name,
                    temp=weather_temp,
                    humidity=weather_humidity,
                    rainfall=norm_rain,
                    season=active_season,
                    lang=lang,
                    weather_desc=weather_desc
                )

                base_weather_score = w_eval['score']
                # Window multiplier per Requirement 2d:
                # Open: 1.00x, Closing soon: 0.95x, Late sowing: 0.85x
                if st == 'open':
                    multiplier = 1.00
                elif st == 'closing_soon':
                    multiplier = 0.95
                elif st == 'late_sowing':
                    multiplier = 0.85
                else:
                    multiplier = 0.0

                raw_final = base_weather_score * multiplier
                final_score = round(raw_final, 1)

                scored_candidates.append({
                    'crop_key': crop_name,
                    'weather_eval': w_eval,
                    'base_weather_score': base_weather_score,
                    'multiplier': multiplier,
                    'raw_final': raw_final,
                    'final_score': final_score,
                    'ranking_score': final_score,
                    'composite_match': final_score,
                    'sowing_status': sow_st,
                    'needs_verification': True
                })

            # Tier 2: only if Tier 1 gives fewer than 3, crops listed for OTHER districts in the SAME agro-climatic zone that are sowable now
            ZONE_FALLBACK_ENABLED = True
            if len(scored_candidates) < 3 and ZONE_FALLBACK_ENABLED:
                from models.agri_calendar_service import get_district_zone
                dist_zone = get_district_zone(district)
                same_zone_districts = [
                    d for d in KARNATAKA_DISTRICT_SEASON_CROPS.keys()
                    if get_district_zone(d) == dist_zone and d.strip().lower() != district.strip().lower()
                ]
                tier2_crops = []
                for oz_dist in same_zone_districts:
                    oz_crops = KARNATAKA_DISTRICT_SEASON_CROPS.get(oz_dist, {}).get(active_season_l, [])
                    for oz_c in oz_crops:
                        c_canon = normalize_crop_name(oz_c)
                        if (c_canon not in seen_candidates and 
                            c_canon not in NON_KARNATAKA_CROPS and 
                            c_canon not in PERENNIAL_CROPS and 
                            c_canon not in tier2_crops):
                            tier2_crops.append(c_canon)

                for crop_name in tier2_crops:
                    sow_st = get_sowing_status(crop_name, active_season, today=eval_today, district=district)
                    st = sow_st.get('status')
                    if st not in ['open', 'closing_soon', 'late_sowing']:
                        continue

                    w_eval = translations.evaluate_crop_weather_suitability(
                        crop_name=crop_name,
                        temp=weather_temp,
                        humidity=weather_humidity,
                        rainfall=norm_rain,
                        season=active_season,
                        lang=lang,
                        weather_desc=weather_desc
                    )
                    base_weather_score = w_eval['score']
                    multiplier = 1.00 if st == 'open' else (0.95 if st == 'closing_soon' else 0.85)
                    raw_final = base_weather_score * multiplier
                    final_score = round(raw_final, 1)

                    scored_candidates.append({
                        'crop_key': crop_name,
                        'weather_eval': w_eval,
                        'base_weather_score': base_weather_score,
                        'multiplier': multiplier,
                        'raw_final': raw_final,
                        'final_score': final_score,
                        'ranking_score': final_score,
                        'composite_match': final_score,
                        'sowing_status': sow_st,
                        'is_tier2': True,
                        'needs_verification': True
                    })

            # Sort strictly: Tier 1 crops rank above Tier 2 at equal scores, then by unrounded raw_final, break ties by more days left
            scored_candidates.sort(
                key=lambda x: (
                    not x.get('is_tier2', False),
                    x['raw_final'],
                    x['sowing_status'].get('days_difference', 0)
                ),
                reverse=True
            )

            # Top 3 candidates (strictly district-grown sowable crops only, never padded)
            top_selected = scored_candidates[:3]

            if len(top_selected) < 3:
                print(f"[Agronomy Shortage Log] District: {district} | Date: {eval_today.isoformat()} | Season: {active_season} | Found {len(top_selected)} sowable candidates.")

        except Exception as e:
            print(f"Candidate crop scoring notice: {e}")
            top_selected = []

        # Build structured 1 to 3 crops list
        from models.agri_calendar_service import get_sowing_status, compute_harvest_range, get_district_institution
        univ_name, kvk_name = get_district_institution(district)
        top_crops = []
        for idx, item in enumerate(top_selected):
            c_key = item['crop_key']
            w_info = item['weather_eval']
            c_meta = translations.CROP_TRANSLATIONS.get(c_key, translations.CROP_TRANSLATIONS['default'])

            c_en = translations.get_crop_name(c_key, 'en')
            c_kn = translations.get_crop_name(c_key, 'kn')
            c_hi = translations.get_crop_name(c_key, 'hi')

            is_top = (idx == 0)
            base_weather_score = item.get('base_weather_score', w_info['score'])
            mult = item.get('multiplier', 1.0)
            final_match = item.get('final_score', w_info['score'])
            display_match_pct = int(round(final_match))

            sow_st = item.get('sowing_status') or get_sowing_status(c_key, active_season, today=eval_today, district=district)
            harvest_info = compute_harvest_range(c_key, active_season, district=district, today=eval_today)

            st = sow_st.get('status', 'open')
            is_passed = (st == 'passed')
            is_closing = (st == 'closing_soon')
            is_late = (st == 'late_sowing')
            days_diff = sow_st.get('days_difference', 0)

            # Headline & urgency badges (Bug 3 fix)
            if is_top:
                if is_late:
                    rank_label_en = f"⏳ Late Sowing Window Active ({days_diff} day{'s' if days_diff > 1 else ''} left) — Use Late-Sown Varieties"
                    rank_label_kn = f"⏳ ತಡವಾದ ಬಿತ್ತನೆ ಸಮಯ ಸಕ್ರಿಯವಾಗಿದೆ ({days_diff} ದಿನ ಬಾಕಿ) — ತಡವಾದ ತಳಿಗಳನ್ನು ಬಳಸಿ"
                    rank_label_hi = f"⏳ देर से बुवाई सक्रिय ({days_diff} दिन शेष) — उपयुक्त किस्में अपनाएं"
                    status_en, status_kn, status_hi = f"Late Sowing ({days_diff}d left)", f"ತಡವಾದ ಬಿತ್ತನೆ ({days_diff} ದಿನ)", f"देर से बुवाई ({days_diff} दिन)"
                    icon = '⏳'
                elif is_closing and days_diff <= 7:
                    day_unit_en = "day" if days_diff == 1 else "days"
                    rank_label_en = f"⏳ Sowing Window Closing Soon ({days_diff} {day_unit_en} left) — Prioritize Sowing"
                    rank_label_kn = f"⏳ ಬಿತ್ತನೆ ಸಮಯ ಶೀಘ್ರದಲ್ಲೇ ಮುಕ್ತಾಯವಾಗಲಿದೆ ({days_diff} ದಿನ ಬಾಕಿ) — ತಕ್ಷಣ ಬಿತ್ತನೆ ಮಾಡಿ"
                    rank_label_hi = f"⏳ बुवाई का समय जल्द समाप्त होगा ({days_diff} दिन शेष) — तुरंत बुवाई करें"
                    status_en, status_kn, status_hi = f"Closing Soon ({days_diff}d left)", f"ಶೀಘ್ರ ಮುಕ್ತಾಯ ({days_diff} ದಿನ)", f"जल्द समाप्त ({days_diff} दिन)"
                    icon = '⏳'
                elif is_closing:
                    rank_label_en = f"⏳ Sowing Window Closing Soon ({days_diff} days left) — Plan Sowing"
                    rank_label_kn = f"⏳ ಬಿತ್ತನೆ ಸಮಯ ಕೊನೆಗೊಳ್ಳಲಿದೆ ({days_diff} ದಿನಗಳು ಬಾಕಿ) — ಬಿತ್ತನೆಗೆ ಯೋಜಿಸಿ"
                    rank_label_hi = f"⏳ बुवाई जल्द समाप्त होगी ({days_diff} दिन शेष) — बुवाई की योजना बनाएं"
                    status_en, status_kn, status_hi = 'Closing Soon', 'ಶೀಘ್ರ ಮುಕ್ತಾಯ', 'जल्द समाप्त'
                    icon = '⏳'
                else:
                    rank_label_en = "🌟 Most Preferred for Current Weather"
                    rank_label_kn = "🌟 ಪ್ರಸ್ತುತ ಹವಾಮಾನಕ್ಕೆ ಅತ್ಯಂತ ಸೂಕ್ತ"
                    rank_label_hi = "🌟 वर्तमान मौसम के अनुसार सर्वाधिक उपयुक्त"
                    if final_match >= 85.0:
                        status_en, status_kn, status_hi = 'High Match', 'ಉನ್ನತ ಹೊಂದಾಣಿಕೆ', 'उच्च अनुकूलता'
                        icon = '🌟'
                    elif final_match >= 70.0:
                        status_en, status_kn, status_hi = 'Medium Match', 'ಮಧ್ಯಮ ಹೊಂದಾಣಿಕೆ', 'मध्यम अनुकूलता'
                        icon = '👍'
                    else:
                        status_en, status_kn, status_hi = 'Low Match', 'ಕಡಿಮೆ ಹೊಂದಾಣಿಕೆ', 'कम अनुकूलता'
                        icon = '🌤'
            else:
                if is_late:
                    rank_label_en = f"⏳ Late Sowing (#{idx + 1})"
                    rank_label_kn = f"⏳ ತಡವಾದ ಬಿತ್ತನೆ (#{idx + 1})"
                    rank_label_hi = f"⏳ देर से बुवाई (#{idx + 1})"
                    status_en, status_kn, status_hi = f"Late Sowing ({days_diff}d left)", f"ತಡವಾದ ಬಿತ್ತನೆ ({days_diff} ದಿನ)", f"देर से बुवाई ({days_diff} दिन)"
                    icon = '⏳'
                elif is_closing:
                    rank_label_en = f"⏳ Sowing Closing Soon (#{idx + 1})"
                    rank_label_kn = f"⏳ ಬಿತ್ತನೆ ಕೊನೆಗೊಳ್ಳಲಿದೆ (#{idx + 1})"
                    rank_label_hi = f"⏳ बुवाई जल्द समाप्त (#{idx + 1})"
                    status_en, status_kn, status_hi = f"Closing Soon ({days_diff}d left)", f"ಶೀಘ್ರ ಮುಕ್ತಾಯ ({days_diff} ದಿನ)", f"जल्द समाप्त ({days_diff} दिन)"
                    icon = '⏳'
                else:
                    rank_label_en = f"🌱 Recommended Option #{idx + 1}"
                    rank_label_kn = f"🌱 ಶಿಫಾರಸು ಮಾಡಿದ ಆಯ್ಕೆ #{idx + 1}"
                    rank_label_hi = f"🌱 अनुशंसित विकल्प #{idx + 1}"
                    if final_match >= 85.0:
                        status_en, status_kn, status_hi = 'High Match', 'ಉನ್ನತ ಹೊಂದಾಣಿಕೆ', 'उच्च अनुकूलता'
                        icon = '🌟'
                    elif final_match >= 70.0:
                        status_en, status_kn, status_hi = 'Medium Match', 'ಮಧ್ಯಮ ಹೊಂದಾಣಿಕೆ', 'मध्यम अनुकूलता'
                        icon = '👍'
                    else:
                        status_en, status_kn, status_hi = 'Low Match', 'ಕಡಿಮೆ ಹೊಂದಾಣಿಕೆ', 'कम अनुकूलता'
                        icon = '🌤'

            level = 'optimal' if final_match >= 85.0 else ('good' if final_match >= 70.0 else 'moderate')
            suitability_disclaimer = f" (Estimated suitability score based on weather and season; confirm with your local {kvk_name} / {univ_name})."

            round_temp = int(round(weather_temp))
            crop_explanation_en = w_info.get('crop_weather_explanation_en') or f"Live {round_temp}°C temperature and {weather_humidity:.0f}% humidity align with {c_en}."
            crop_explanation_kn = w_info.get('crop_weather_explanation_kn') or f"ಪ್ರಸ್ತುತ {round_temp}°C ತಾಪಮಾನ ಮತ್ತು {weather_humidity:.0f}% ತೇವಾಂಶ {c_kn} ಬೆಳೆಗೆ ಹೊಂದಿಕೆಯಾಗುತ್ತದೆ."
            crop_explanation_hi = w_info.get('crop_weather_explanation_hi') or f"वर्तमान {round_temp}°C तापमान और {weather_humidity:.0f}% आर्द्रता {c_hi} के अनुकूल है।"

            score_breakdown_en = f"(Suitability Score: {display_match_pct}%)"
            score_breakdown_kn = f"(ಹೊಂದಾಣಿಕೆ ಸ್ಕೋರ್: {display_match_pct}%)"
            score_breakdown_hi = f"(अनुकूलता स्कोर: {display_match_pct}%)"

            dyn_reason_en = f"{icon} {status_en} {score_breakdown_en}: {crop_explanation_en} {w_info['base_reason_en']}{suitability_disclaimer}"
            dyn_reason_kn = f"{icon} {status_kn} {score_breakdown_kn}: {crop_explanation_kn} {w_info['base_reason_kn']}"
            dyn_reason_hi = f"{icon} {status_hi} {score_breakdown_hi}: {crop_explanation_hi} {w_info['base_reason_hi']}"

            if item.get('is_tier2'):
                dyn_reason_en += f" Grown in neighbouring districts of your zone; confirm suitability with ICAR-KVK {district}."
                dyn_reason_kn += f" ನಿಮ್ಮ ವಲಯದ ನೆರೆಯ ಜಿಲ್ಲೆಗಳಲ್ಲಿ ಬೆಳೆಯಲಾಗುತ್ತದೆ; ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರ (ICAR-KVK) {district} ನೊಂದಿಗೆ ಸೂಕ್ತತೆ ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ."
                dyn_reason_hi += f" आपके क्षेत्र के पड़ोसी जिलों में उगाई जाती है; ICAR-KVK {district} से उपयुक्तता की पुष्टि करें।"

            is_transplanted_c = sow_st.get('is_transplanted', False) or (c_key in ['tomato', 'chilli', 'onion'])
            sow_lbl_en = "🌱 Nursery / transplanting" if is_transplanted_c else "🗓 Sowing"
            sow_lbl_kn = "🌱 ನರ್ಸರಿ / ನಾಟಿ" if is_transplanted_c else "🗓 ಬಿತ್ತನೆ"
            sow_lbl_hi = "🌱 नर्सरी / रोपाई" if is_transplanted_c else "🗓 बुवाई"

            top_crops.append({
                'rank': idx + 1,
                'is_preferred': is_top and not is_passed,
                'crop_key': c_key,
                'name': c_en,
                'name_en': c_en,
                'name_kn': c_kn,
                'name_hi': c_hi,
                'rank_label_en': rank_label_en,
                'rank_label_kn': rank_label_kn,
                'rank_label_hi': rank_label_hi,
                'rank_label': rank_label_kn if lang == 'kn' else (rank_label_hi if lang == 'hi' else rank_label_en),
                'score': display_match_pct,
                'base_weather_score': base_weather_score,
                'multiplier': mult,
                'final_score': final_match,
                'needs_verification': sow_st.get('needs_verification', True),
                'level': level,
                'status_en': status_en,
                'status_kn': status_kn,
                'status_hi': status_hi,
                'reason_en': dyn_reason_en,
                'reason_kn': dyn_reason_kn,
                'reason_hi': dyn_reason_hi,
                'reason': dyn_reason_kn if lang == 'kn' else (dyn_reason_hi if lang == 'hi' else dyn_reason_en),
                'base_reason_en': w_info['base_reason_en'],
                'base_reason_kn': w_info['base_reason_kn'],
                'base_reason_hi': w_info['base_reason_hi'],
                'season_en': c_meta['season']['en'],
                'season_kn': c_meta['season']['kn'],
                'season_hi': c_meta['season']['hi'],
                'sowing_op_en': sow_lbl_en,
                'sowing_op_kn': sow_lbl_kn,
                'sowing_op_hi': sow_lbl_hi,
                'sowing_en': sow_st.get('window_label_en', sow_st.get('window_label', c_meta['planting_months']['en'])),
                'sowing_kn': sow_st.get('window_label_kn', sow_st.get('window_label', c_meta['planting_months']['kn'])),
                'sowing_hi': sow_st.get('window_label_hi', sow_st.get('window_label', c_meta['planting_months']['hi'])),
                'harvest_en': harvest_info.get('harvest_en', c_meta['harvest_months']['en']),
                'harvest_kn': harvest_info.get('harvest_kn', c_meta['harvest_months']['kn']),
                'harvest_hi': harvest_info.get('harvest_hi', c_meta['harvest_months']['hi']),
                'desc_en': c_meta['season_desc']['en'],
                'desc_kn': c_meta['season_desc']['kn'],
                'desc_hi': c_meta['season_desc']['hi'],
                'sowing_status': sow_st.get('status', 'open'),
                'sowing_passed': is_passed,
                'sowing_closing': is_closing,
                'sowing_warning': sow_st.get('warning_kn', '') if lang == 'kn' else (sow_st.get('warning_hi', '') if lang == 'hi' else sow_st.get('warning_en', '')),
                'sowing_warning_en': sow_st.get('warning_en', ''),
                'sowing_warning_kn': sow_st.get('warning_kn', ''),
                'sowing_warning_hi': sow_st.get('warning_hi', ''),
                'university': univ_name,
                'kvk': kvk_name
            })

        # Hard cap: guarantee exactly at most 3 crops
        top_crops = top_crops[:3]

        # Primary recommended crop is the #1 Most Preferred Crop (if any qualify)
        if top_crops:
            primary_crop = top_crops[0]
            result = primary_crop['crop_key']
            crop_lower = result.lower()
            c_meta = translations.CROP_TRANSLATIONS.get(crop_lower, translations.CROP_TRANSLATIONS['default'])
            crop_tr_en = primary_crop['name_en']
            crop_tr_kn = primary_crop['name_kn']
            crop_tr_hi = primary_crop['name_hi']
            crop_result_en = f"Recommended Crop: {crop_tr_en}"
            crop_result_kn = f"ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆ: {crop_tr_kn}"
            crop_result_hi = f"अनुशंसित फसल: {crop_tr_hi}"
        else:
            primary_crop = {
                'crop_key': '',
                'name_en': 'None currently open',
                'name_kn': 'ಪ್ರಸ್ತುತ ಬಿತ್ತನೆ ಅವಧಿ ಮುಕ್ತಾಯಗೊಂಡಿದೆ',
                'name_hi': 'वर्तमान में बुवाई समय उपलब्ध नहीं',
                'sowing_en': 'N/A', 'sowing_kn': 'ಲಭ್ಯವಿಲ್ಲ', 'sowing_hi': 'उपलब्ध नहीं',
                'harvest_en': 'N/A', 'harvest_kn': 'ಲಭ್ಯವಿಲ್ಲ', 'harvest_hi': 'उपलब्ध नहीं',
                'reason_en': 'No sowable crops currently open for this district and season.',
                'reason_kn': 'ಈ ಜಿಲ್ಲೆ ಮತ್ತು ಋತುವಿನಲ್ಲಿ ಪ್ರಸ್ತುತ ಯಾವುದೇ ಬೆಳೆಯ ಬಿತ್ತನೆ ಅವಧಿ ಮುಕ್ತವಾಗಿಲ್ಲ.',
                'reason_hi': 'इस जिले और मौसम के लिए वर्तमान में कोई बुवाई सत्र खुला नहीं है।',
                'reason': 'No sowable crops currently open.'
            }
            result = ""
            crop_lower = ""
            c_meta = translations.CROP_TRANSLATIONS['default']
            crop_tr_en = primary_crop['name_en']
            crop_tr_kn = primary_crop['name_kn']
            crop_tr_hi = primary_crop['name_hi']
            crop_result_en = "Recommended Crop: No sowable crops open today"
            crop_result_kn = "ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆ: ಇಂದು ಯಾವುದೇ ಬಿತ್ತನೆ ಕಾಲ ಮುಕ್ತವಾಗಿಲ್ಲ"
            crop_result_hi = "अनुशंसित फसल: आज कोई बुवाई सत्र खुला नहीं है"

        # Sowing vs Nursery/Transplanting operation label
        is_transplanted_op = crop_lower in ['tomato', 'chilli', 'onion', 'brinjal', 'cabbage', 'cauliflower']
        sow_op_en = "🌱 Nursery / transplanting" if is_transplanted_op else "🗓 Sowing"
        sow_op_kn = "🌱 ನರ್ಸರಿ / ನಾಟಿ" if is_transplanted_op else "🗓 ಬಿತ್ತನೆ"
        sow_op_hi = "🌱 नर्सरी / रोपाई" if is_transplanted_op else "🗓 बुवाई"

        primary_sowing_en = primary_crop.get('sowing_en', c_meta['planting_months']['en'])
        primary_sowing_kn = primary_crop.get('sowing_kn', c_meta['planting_months']['kn'])
        primary_sowing_hi = primary_crop.get('sowing_hi', c_meta['planting_months']['hi'])
        primary_harvest_en = primary_crop.get('harvest_en', c_meta['harvest_months']['en'])
        primary_harvest_kn = primary_crop.get('harvest_kn', c_meta['harvest_months']['kn'])
        primary_harvest_hi = primary_crop.get('harvest_hi', c_meta['harvest_months']['hi'])

        # Unified Season badge using the identical computed harvest range
        if season == 'auto' or not season:
            season_badge_en = f"🌾 Suitable Season: {c_meta['season']['en']} | {sow_op_en}: {primary_sowing_en} | 🌾 Harvest: {primary_harvest_en}"
            season_badge_kn = f"🌾 ಸೂಕ್ತ ಋತು: {c_meta['season']['kn']} | {sow_op_kn}: {primary_sowing_kn} | 🌾 ಕೊಯ್ಲು: {primary_harvest_kn}"
            season_badge_hi = f"🌾 उपयुक्त मौसम: {c_meta['season']['hi']} | {sow_op_hi}: {primary_sowing_hi} | 🌾 कटाई: {primary_harvest_hi}"
        else:
            season_badge_en = f"🌾 Selected Season: {season} (Crop Primary: {c_meta['season']['en']}) | {sow_op_en}: {primary_sowing_en} | 🌾 Harvest: {primary_harvest_en}"
            season_badge_kn = f"🌾 ಆಯ್ಕೆ ಮಾಡಿದ ಋತು: {season} (ಬೆಳೆಯ ಪ್ರಮುಖ ಋತು: {c_meta['season']['kn']}) | {sow_op_kn}: {primary_sowing_kn} | 🌾 ಕೊಯ್ಲು: {primary_harvest_kn}"
            season_badge_hi = f"🌾 चयनित मौसम: {season} (फसल का मुख्य मौसम: {c_meta['season']['hi']}) | {sow_op_hi}: {primary_sowing_hi} | 🌾 कटाई: {primary_harvest_hi}"

        season_advice_en = f"Seasonal Guide for {crop_tr_en}: {c_meta['season_desc']['en']}"
        season_advice_kn = f"{crop_tr_kn} ಬೆಳೆ ಮಾರ್ಗದರ್ಶಿ: {c_meta['season_desc']['kn']}"
        season_advice_hi = f"{crop_tr_hi} मौसमी गाइड: {c_meta['season_desc']['hi']}"

        # Invalidate stale cross-crop and cross-district artifacts
        invalidate_dependent_farm_context(new_crop=result, new_district=district)
        sowing_passed = primary_crop.get('sowing_passed', False)
        update_farm_context(
            crop=result,
            crop_key=crop_lower,
            district=district,
            season=active_season,
            sowing_status="passed" if sowing_passed else "open",
            days_after_sowing=0
        )
        session['recommended_crop'] = result
        session['recommended_crop_en'] = crop_tr_en
        session['recommended_crop_kn'] = crop_tr_kn
        session['recommended_crop_hi'] = crop_tr_hi

        session['top_crops'] = top_crops
        session['preferred_crop_reason_en'] = primary_crop.get('reason_en', '')
        session['preferred_crop_reason_kn'] = primary_crop.get('reason_kn', '')
        session['preferred_crop_reason_hi'] = primary_crop.get('reason_hi', '')
        session['preferred_crop_reason'] = primary_crop.get('reason', '')

        session['crop_result_en'] = crop_result_en
        session['crop_result_kn'] = crop_result_kn
        session['crop_result_hi'] = crop_result_hi
        session['crop_result'] = crop_result_kn if lang == 'kn' else (crop_result_hi if lang == 'hi' else crop_result_en)

        session['weather_info_en'] = weather_info_en
        session['weather_info_kn'] = weather_info_kn
        session['weather_info_hi'] = weather_info_hi
        session['weather_info'] = weather_info_kn if lang == 'kn' else (weather_info_hi if lang == 'hi' else weather_info_en)

        session['recommended_crop_season_en'] = season_badge_en
        session['recommended_crop_season_kn'] = season_badge_kn
        session['recommended_crop_season_hi'] = season_badge_hi
        session['recommended_crop_season'] = season_badge_kn if lang == 'kn' else (season_badge_hi if lang == 'hi' else season_badge_en)

        session['season_advice_en'] = season_advice_en
        session['season_advice_kn'] = season_advice_kn
        session['season_advice_hi'] = season_advice_hi
        session['season_advice'] = season_advice_kn if lang == 'kn' else (season_advice_hi if lang == 'hi' else season_advice_en)

        session['city'] = district
        session['selected_district'] = district

        # Auto-chain Market Price Agent to the newly recommended crop, district, and present month/year
        now = datetime.now()
        cur_month_str = str(now.month)
        cur_year_str = str(now.year)
        session['price_crop'] = result
        session['price_district'] = district
        session['price_form_data'] = {
            'crop': result,
            'district': district,
            'month': cur_month_str,
            'year': cur_year_str
        }
        # Compute and sync market price forecast immediately for recommended crop + district
        p_data = compute_price_forecast(result, district, now.month, now.year)
        session['predicted_price'] = p_data['prediction']
        session['price_result_en'] = p_data['price_en']
        session['price_result_kn'] = p_data['price_kn']
        session['price_result_hi'] = p_data['price_hi']
        session['price_result'] = p_data['price_kn'] if lang == 'kn' else (p_data['price_hi'] if lang == 'hi' else p_data['price_en'])
        session['price_spot_clean_en'] = p_data['spot_clean_en']
        session['price_forecast_clean_en'] = p_data['forecast_clean_en']
        session['price_spot_clean_kn'] = p_data['spot_clean_kn']
        session['price_forecast_clean_kn'] = p_data['forecast_clean_kn']
        session['price_spot_clean_hi'] = p_data['spot_clean_hi']
        session['price_forecast_clean_hi'] = p_data['forecast_clean_hi']

        # Auto-chain Precision Irrigation Agent to recommended crop & district
        session['irrigation_crop'] = result
        session['irrigation_district'] = district
        growth_st = session.get('irrigation_stage', 'vegetative')
        soil_t = session.get('irrigation_soil', 'loam')
        area_ac = session.get('irrigation_area', '1.0')
        irri_t = session.get('irrigation_method', 'drip')

        irri_rain = 8.0 if (weather_desc and 'rain' in str(weather_desc).lower()) else 0.0

        irri_data = translations.calculate_smart_irrigation(
            crop=result,
            growth_stage=growth_st,
            soil_type=soil_t,
            area_acres=area_ac,
            irrigation_type=irri_t,
            temp=float(weather_temp) if weather_temp is not None else 28.0,
            humidity=float(weather_humidity) if weather_humidity is not None else 55.0,
            rainfall_mm=irri_rain,
            weather_desc=weather_desc or "clear sky",
            district=district,
            lang=lang
        )

        session['irrigation_data'] = irri_data
        session['irrigation_crop'] = result
        session['irrigation_district'] = district
        session['irrigation_stage'] = growth_st
        session['irrigation_soil'] = soil_t
        session['irrigation_area'] = area_ac
        session['irrigation_method'] = irri_t

        session['irrigation_result_en'] = irri_data['advice_en']
        session['irrigation_result_kn'] = irri_data['advice_kn']
        session['irrigation_result_hi'] = irri_data['advice_hi']
        session['irrigation_result'] = irri_data.get(f'advice_{lang}', irri_data['advice_en'])

        session['irrigation_form_data'] = {
            'crop': result,
            'district': district,
            'growth_stage': growth_st,
            'soil_type': soil_t,
            'area_acres': area_ac,
            'irrigation_type': irri_t
        }

        if request.headers.get('Accept') == 'application/json' or request.is_json:
            return jsonify({
                'crop': crop_tr_en,
                'crop_kn': crop_tr_kn,
                'crop_hi': crop_tr_hi,
                'preferred_crop': primary_crop,
                'top_crops': top_crops,
                'season': season_badge_kn if lang == 'kn' else (season_badge_hi if lang == 'hi' else season_badge_en),
                'season_en': season_badge_en,
                'season_kn': season_badge_kn,
                'season_hi': season_badge_hi,
                'weather': weather_info_kn if lang == 'kn' else (weather_info_hi if lang == 'hi' else weather_info_en),
                'weather_en': weather_info_en,
                'weather_kn': weather_info_kn,
                'weather_hi': weather_info_hi,
                'advice': season_advice_kn if lang == 'kn' else (season_advice_hi if lang == 'hi' else season_advice_en),
                'advice_en': season_advice_en,
                'advice_kn': season_advice_kn,
                'advice_hi': season_advice_hi,
                'disease_samples': translations.get_crop_disease_samples(result, lang),
                'district': district,
                'current_month': cur_month_str,
                'current_year': cur_year_str,
                'price_data': p_data,
                'predicted_price': p_data['prediction'],
                'price_result_en': p_data['price_en'],
                'price_result_kn': p_data['price_kn'],
                'price_result_hi': p_data['price_hi'],
                'irrigation_data': irri_data,
                'irrigation_result': irri_data.get(f'advice_{lang}', irri_data['advice_en']),
                'irrigation_result_en': irri_data['advice_en'],
                'irrigation_result_kn': irri_data['advice_kn'],
                'irrigation_result_hi': irri_data['advice_hi']
            })

        return render_template(
            "index.html",
            **get_session_data()
        )

    except Exception as e:
        if request.headers.get('Accept') == 'application/json' or request.is_json:
            return jsonify({'status': 'error', 'message': str(e)}), 500
        session['crop_result'] = f"Error: {str(e)}"
        session['crop_form_data'] = {
            'nitrogen': request.form.get('nitrogen', ''),
            'phosphorus': request.form.get('phosphorus', ''),
            'potassium': request.form.get('potassium', ''),
            'ph': request.form.get('ph', ''),
            'rainfall': request.form.get('rainfall', ''),
            'city': request.form.get('city', ''),
            'district': request.form.get('district', ''),
            'season': request.form.get('season', 'auto')
        }
        return render_template(
            "index.html",
            **get_session_data()
        )
# District Soil Data Auto-fill (Calibrated to Karnataka Agro-climatic Zones & Crop Requirements)
# ===============================
district_soil_data = {
    'Bagalkot':         {'N': 75, 'P': 45, 'K': 22, 'ph': 7.2, 'rainfall': 65},
    'Ballari':          {'N': 115, 'P': 45, 'K': 20, 'ph': 7.2, 'rainfall': 70},
    'Belagavi':         {'N': 85, 'P': 46, 'K': 22, 'ph': 6.8, 'rainfall': 85},
    'Bengaluru Rural':  {'N': 75, 'P': 45, 'K': 25, 'ph': 6.2, 'rainfall': 95},
    'Bengaluru Urban':  {'N': 75, 'P': 45, 'K': 25, 'ph': 6.3, 'rainfall': 95},
    'Bidar':            {'N': 25, 'P': 65, 'K': 22, 'ph': 7.3, 'rainfall': 85},
    'Chamarajanagara':  {'N': 78, 'P': 48, 'K': 25, 'ph': 6.0, 'rainfall': 80},
    'Chikkaballapura':  {'N': 78, 'P': 46, 'K': 28, 'ph': 6.5, 'rainfall': 85},
    'Chikkamagaluru':   {'N': 100, 'P': 30, 'K': 30, 'ph': 5.8, 'rainfall': 160},
    'Chitradurga':      {'N': 80, 'P': 46, 'K': 22, 'ph': 6.8, 'rainfall': 68},
    'Dakshina Kannada': {'N': 40, 'P': 30, 'K': 60, 'ph': 5.8, 'rainfall': 250},
    'Davanagere':       {'N': 78, 'P': 48, 'K': 20, 'ph': 6.5, 'rainfall': 85},
    'Dharwad':          {'N': 70, 'P': 35, 'K': 30, 'ph': 7.2, 'rainfall': 75},
    'Gadag':            {'N': 110, 'P': 45, 'K': 20, 'ph': 7.0, 'rainfall': 70},
    'Hassan':           {'N': 98, 'P': 30, 'K': 30, 'ph': 6.2, 'rainfall': 150},
    'Haveri':           {'N': 85, 'P': 48, 'K': 20, 'ph': 6.8, 'rainfall': 80},
    'Kalaburagi':       {'N': 25, 'P': 65, 'K': 22, 'ph': 7.5, 'rainfall': 80},
    'Kodagu':           {'N': 100, 'P': 30, 'K': 30, 'ph': 5.5, 'rainfall': 165},
    'Kolar':            {'N': 78, 'P': 48, 'K': 25, 'ph': 6.2, 'rainfall': 85},
    'Koppal':           {'N': 80, 'P': 46, 'K': 22, 'ph': 7.2, 'rainfall': 65},
    'Mandya':           {'N': 80, 'P': 48, 'K': 40, 'ph': 6.2, 'rainfall': 200},
    'Mysuru':           {'N': 80, 'P': 40, 'K': 40, 'ph': 6.5, 'rainfall': 140},
    'Raichur':          {'N': 120, 'P': 48, 'K': 20, 'ph': 7.0, 'rainfall': 80},
    'Ramanagara':       {'N': 60, 'P': 30, 'K': 40, 'ph': 6.5, 'rainfall': 90},
    'Shivamogga':       {'N': 80, 'P': 48, 'K': 40, 'ph': 6.0, 'rainfall': 210},
    'Tumakuru':         {'N': 25, 'P': 20, 'K': 32, 'ph': 6.3, 'rainfall': 130},
    'Udupi':            {'N': 40, 'P': 30, 'K': 60, 'ph': 5.8, 'rainfall': 260},
    'Uttara Kannada':   {'N': 85, 'P': 45, 'K': 40, 'ph': 6.0, 'rainfall': 220},
    'Vijayanagara':     {'N': 110, 'P': 45, 'K': 20, 'ph': 7.0, 'rainfall': 68},
    'Vijayapura':       {'N': 25, 'P': 130, 'K': 195, 'ph': 7.5, 'rainfall': 68},
    'Yadgir':           {'N': 25, 'P': 65, 'K': 22, 'ph': 7.4, 'rainfall': 80},
}

# District typical weather fallback (when API fails)
district_weather_fallback = {
    'Bagalkot': {'temp': 28, 'humidity': 55},
    'Ballari': {'temp': 29, 'humidity': 50},
    'Belagavi': {'temp': 25, 'humidity': 65},
    'Bengaluru Rural': {'temp': 24, 'humidity': 65},
    'Bengaluru Urban': {'temp': 25, 'humidity': 63},
    'Bidar': {'temp': 27, 'humidity': 58},
    'Chamarajanagara': {'temp': 26, 'humidity': 62},
    'Chikkaballapura': {'temp': 26, 'humidity': 60},
    'Chikkamagaluru': {'temp': 22, 'humidity': 75},
    'Chitradurga': {'temp': 27, 'humidity': 56},
    'Dakshina Kannada': {'temp': 28, 'humidity': 80},
    'Davanagere': {'temp': 28, 'humidity': 62},
    'Dharwad': {'temp': 27, 'humidity': 60},
    'Gadag': {'temp': 28, 'humidity': 55},
    'Hassan': {'temp': 23, 'humidity': 70},
    'Haveri': {'temp': 27, 'humidity': 58},
    'Kalaburagi': {'temp': 28, 'humidity': 52},
    'Kodagu': {'temp': 20, 'humidity': 80},
    'Mandya': {'temp': 27, 'humidity': 61},
    'Mysuru': {'temp': 26, 'humidity': 60},
    'Raichur': {'temp': 29, 'humidity': 51},
    'Ramanagara': {'temp': 26, 'humidity': 62},
    'Shivamogga': {'temp': 25, 'humidity': 70},
    'Tumakuru': {'temp': 26, 'humidity': 61},
    'Udupi': {'temp': 28, 'humidity': 78},
    'Uttara Kannada': {'temp': 26, 'humidity': 75},
    'Vijayanagara': {'temp': 29, 'humidity': 50},
    'Vijayapura': {'temp': 28, 'humidity': 52},
    'Yadgir': {'temp': 29, 'humidity': 48},
}

@app.route('/get_district_data', methods=['POST'])
def get_district_data():
    district = request.form.get('district', '')
    data = district_soil_data.get(district, {})
    return jsonify(data)

@app.route('/predict_price', methods=['POST'])
def predict_price():
    try:
        req_json = request.get_json(silent=True) or {}
        lang = request.form.get('lang') or req_json.get('lang') or request.args.get('lang') or session.get('lang', 'en')
        session['lang'] = lang

        crop = request.form['crop']
        district = request.form.get('district') or request.form.get('state', '')
        month = request.form.get('month')
        year = request.form.get('year')

        p_data = compute_price_forecast(crop, district, month, year)

        # Save selected crop and predicted price
        session['price_crop'] = crop
        session['price_district'] = district
        session['predicted_price'] = p_data['prediction']
        session['price_form_data'] = {
            'crop': crop,
            'district': district,
            'state': district,
            'month': p_data['month'],
            'year': p_data['year']
        }

        session['price_result_en'] = p_data['price_en']
        session['price_result_kn'] = p_data['price_kn']
        session['price_result_hi'] = p_data['price_hi']
        session['price_result'] = p_data['price_kn'] if lang == 'kn' else (p_data['price_hi'] if lang == 'hi' else p_data['price_en'])
        session['price_spot_clean_en'] = p_data['spot_clean_en']
        session['price_forecast_clean_en'] = p_data['forecast_clean_en']
        session['price_spot_clean_kn'] = p_data['spot_clean_kn']
        session['price_forecast_clean_kn'] = p_data['forecast_clean_kn']
        session['price_spot_clean_hi'] = p_data['spot_clean_hi']
        session['price_forecast_clean_hi'] = p_data['forecast_clean_hi']

        if request.headers.get('Accept') == 'application/json' or request.is_json:
            chosen_price_result = p_data['price_kn'] if lang == 'kn' else (p_data['price_hi'] if lang == 'hi' else p_data['price_en'])
            return jsonify({
                'crop': crop,
                'district': district,
                'prediction': p_data['prediction'],
                'avg_price': p_data['avg_price'],
                'min_price': p_data['min_price'],
                'max_price': p_data['max_price'],
                'live_mandi': p_data['live_mandi'],
                'forecast_text': chosen_price_result,
                'result': chosen_price_result,
                'result_en': p_data['price_en'],
                'result_kn': p_data['price_kn'],
                'result_hi': p_data['price_hi'],
                'spot_clean_en': p_data.get('spot_clean_en', ''),
                'spot_clean_kn': p_data.get('spot_clean_kn', ''),
                'spot_clean_hi': p_data.get('spot_clean_hi', ''),
                'forecast_clean_en': p_data.get('forecast_clean_en', ''),
                'forecast_clean_kn': p_data.get('forecast_clean_kn', ''),
                'forecast_clean_hi': p_data.get('forecast_clean_hi', '')
            })

        return render_template(
            "index.html",
            **get_session_data()
        )

    except Exception as e:
        session['price_result'] = f"Error: {str(e)}"
        session['price_form_data'] = {
            'crop': request.form.get('crop', ''),
            'district': request.form.get('district', '') or request.form.get('state', ''),
            'state': request.form.get('district', '') or request.form.get('state', ''),
            'month': request.form.get('month', ''),
            'year': request.form.get('year', '')
        }
        return render_template(
            "index.html",
            **get_session_data()
        )

@app.route('/api/live_mandi_price', methods=['GET', 'POST'])
def api_live_mandi_price():
    crop = request.args.get('crop') or request.form.get('crop', 'Rice')
    district = request.args.get('district') or request.form.get('district', 'Dharwad')
    try:
        if agmarknet_service:
            data = agmarknet_service.fetch_live_mandi_price(crop, district)
        else:
            data = {"status": "unavailable", "message": "Agmarknet service not active"}
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ===============================
# Leaf Disease Prediction
# ===============================
@app.route('/predict_disease', methods=['POST'])
def predict_disease():
    try:
        req_json = request.get_json(silent=True) or {}
        lang = request.form.get('lang') or req_json.get('lang') or request.args.get('lang') or session.get('lang', 'en')
        session['lang'] = lang

        if 'image' not in request.files:
            return redirect('/')

        file = request.files['image']
        if file.filename == '':
            return redirect('/')

        crop_type = request.form.get('crop_type', 'tomato')
        session['disease_form_data'] = {'crop_type': crop_type}

        upload_folder = "static/uploads"
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, file.filename)
        file.save(filepath)

        predicted_crop, predicted_disease, confidence = predict_leaf_disease(filepath, crop_type)
        print(f"Prediction: {predicted_crop} : {predicted_disease} (Confidence: {confidence}%)")

        if predicted_crop == "Unsupported" or not translations.is_disease_diagnosis_supported(crop_type):
            unsupp_msg = translations.get_crop_support_notice(crop_type, lang)
            unsupp_en = translations.get_crop_support_notice(crop_type, 'en')
            unsupp_kn = translations.get_crop_support_notice(crop_type, 'kn')
            unsupp_hi = translations.get_crop_support_notice(crop_type, 'hi')

            session["predicted_crop"] = "Unsupported"
            session["predicted_disease"] = "Diagnosis Not Available"
            session["disease_confidence"] = 0.0
            session["disease_result_en"] = unsupp_en
            session["disease_result_kn"] = unsupp_kn
            session["disease_result_hi"] = unsupp_hi
            session["disease_result"] = unsupp_msg
            session['uploaded_image'] = filepath

            if request.headers.get('Accept') == 'application/json' or request.is_json:
                return jsonify({
                    'status': 'unsupported',
                    'is_supported': False,
                    'is_valid_leaf': True,
                    'crop': crop_type,
                    'disease': 'Diagnosis Not Available',
                    'confidence': 0.0,
                    'error': unsupp_en,
                    'result': unsupp_en,
                    'result_kn': unsupp_kn,
                    'result_hi': unsupp_hi,
                    'image_path': filepath
                })

            return render_template(
                "index.html",
                **get_session_data()
            )

        if predicted_crop == "Invalid":
            err_en = f"❌ Invalid Image: {predicted_disease}"
            err_kn = f"❌ ಅಮಾನ್ಯ ಫೋಟೋ: ಬೆಳೆ ಅಥವಾ ಎಲೆ ಪತ್ತೆಯಾಗಿಲ್ಲ. ದಯವಿಟ್ಟು ಗಿಡದ ಎಲೆಯ ಸ್ಪಷ್ಟ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ."
            err_hi = f"❌ अमान्य फोटो: फसल या पत्ती नहीं मिली। कृपया पौधे की पत्ती की स्पष्ट फोटो अपलोड करें।"

            session["predicted_crop"] = "Invalid"
            session["predicted_disease"] = predicted_disease
            session["disease_confidence"] = 0.0
            session["disease_result_en"] = err_en
            session["disease_result_kn"] = err_kn
            session["disease_result_hi"] = err_hi
            session["disease_result"] = err_kn if lang == 'kn' else (err_hi if lang == 'hi' else err_en)
            session['uploaded_image'] = filepath

            if request.headers.get('Accept') == 'application/json' or request.is_json:
                return jsonify({
                    'status': 'error',
                    'is_valid_leaf': False,
                    'crop': 'Invalid',
                    'disease': predicted_disease,
                    'confidence': 0.0,
                    'error': err_en,
                    'result': err_en,
                    'result_kn': err_kn,
                    'result_hi': err_hi,
                    'image_path': filepath
                }), 400

            return render_template(
                "index.html",
                **get_session_data()
            )

        if predicted_crop == "CropMismatch":
            c_name_en = translations.get_crop_name(crop_type, 'en')
            c_name_kn = translations.get_crop_name(crop_type, 'kn')
            c_name_hi = translations.get_crop_name(crop_type, 'hi')

            mismatch_en = translations.DISEASE_PANEL_TEXTS['crop_mismatch_message']['en'].format(crop=c_name_en)
            mismatch_kn = translations.DISEASE_PANEL_TEXTS['crop_mismatch_message']['kn'].format(crop=c_name_kn)
            mismatch_hi = translations.DISEASE_PANEL_TEXTS['crop_mismatch_message']['hi'].format(crop=c_name_hi)

            session["predicted_crop"] = "CropMismatch"
            session["predicted_disease"] = "Crop Mismatch"
            session["disease_confidence"] = 0.0
            session["disease_result_en"] = mismatch_en
            session["disease_result_kn"] = mismatch_kn
            session["disease_result_hi"] = mismatch_hi
            session["disease_result"] = mismatch_kn if lang == 'kn' else (mismatch_hi if lang == 'hi' else mismatch_en)
            session['uploaded_image'] = filepath

            if request.headers.get('Accept') == 'application/json' or request.is_json:
                return jsonify({
                    'status': 'crop_mismatch',
                    'is_valid_leaf': False,
                    'is_crop_match': False,
                    'crop': crop_type,
                    'disease': 'Crop Mismatch',
                    'confidence': 0.0,
                    'error': mismatch_en,
                    'result': mismatch_en,
                    'result_kn': mismatch_kn,
                    'result_hi': mismatch_hi,
                    'image_path': filepath
                }), 400

            return render_template(
                "index.html",
                **get_session_data()
            )

        if predicted_crop == "Uncertain":
            uncert_en = translations.DISEASE_PANEL_TEXTS['uncertain_diagnosis_message']['en']
            uncert_kn = translations.DISEASE_PANEL_TEXTS['uncertain_diagnosis_message']['kn']
            uncert_hi = translations.DISEASE_PANEL_TEXTS['uncertain_diagnosis_message']['hi']

            session["predicted_crop"] = crop_type
            session["predicted_disease"] = "Uncertain"
            session["disease_confidence"] = confidence
            session["disease_result_en"] = uncert_en
            session["disease_result_kn"] = uncert_kn
            session["disease_result_hi"] = uncert_hi
            session["disease_result"] = uncert_kn if lang == 'kn' else (uncert_hi if lang == 'hi' else uncert_en)
            session['uploaded_image'] = filepath

            if request.headers.get('Accept') == 'application/json' or request.is_json:
                return jsonify({
                    'status': 'uncertain',
                    'is_valid_leaf': True,
                    'is_confident': False,
                    'crop': crop_type,
                    'disease': 'Uncertain',
                    'confidence': confidence,
                    'error': uncert_en,
                    'result': uncert_en,
                    'result_kn': uncert_kn,
                    'result_hi': uncert_hi,
                    'image_path': filepath
                })

            return render_template(
                "index.html",
                **get_session_data()
            )

        # Handle Orange (Citrus Greening only)
        if predicted_crop.lower() == "orange":
            session["predicted_crop"] = "Orange"
            session["predicted_disease"] = predicted_disease
            session["disease_confidence"] = confidence

            if predicted_disease == "DiseaseNotDetected":
                o_msg_en = translations.DISEASE_PANEL_TEXTS['orange_not_detected_message']['en']
                o_msg_kn = translations.DISEASE_PANEL_TEXTS['orange_not_detected_message']['kn']
                o_msg_hi = translations.DISEASE_PANEL_TEXTS['orange_not_detected_message']['hi']
            else:
                conf_lbl_en = translations.get_confidence_level(confidence, 'en')
                conf_lbl_kn = translations.get_confidence_level(confidence, 'kn')
                conf_lbl_hi = translations.get_confidence_level(confidence, 'hi')
                o_msg_en = f"{translations.DISEASE_PANEL_TEXTS['orange_detected_message']['en']} ({conf_lbl_en})"
                o_msg_kn = f"{translations.DISEASE_PANEL_TEXTS['orange_detected_message']['kn']} ({conf_lbl_kn})"
                o_msg_hi = f"{translations.DISEASE_PANEL_TEXTS['orange_detected_message']['hi']} ({conf_lbl_hi})"

            session["disease_result_en"] = o_msg_en
            session["disease_result_kn"] = o_msg_kn
            session["disease_result_hi"] = o_msg_hi
            session["disease_result"] = o_msg_kn if lang == 'kn' else (o_msg_hi if lang == 'hi' else o_msg_en)
            session['uploaded_image'] = filepath

            if request.headers.get('Accept') == 'application/json' or request.is_json:
                return jsonify({
                    'status': 'success',
                    'is_valid_leaf': True,
                    'is_confident': True,
                    'crop': 'Orange',
                    'disease': predicted_disease,
                    'confidence': confidence,
                    'result': o_msg_kn if lang == 'kn' else (o_msg_hi if lang == 'hi' else o_msg_en),
                    'result_en': o_msg_en,
                    'result_kn': o_msg_kn,
                    'result_hi': o_msg_hi,
                    'image_path': filepath
                })

            return render_template("index.html", **get_session_data())

        # Handle Squash (Powdery Mildew only)
        elif predicted_crop.lower() == "squash":
            session["predicted_crop"] = "Squash"
            session["predicted_disease"] = predicted_disease
            session["disease_confidence"] = confidence

            if predicted_disease == "DiseaseNotDetected":
                s_msg_en = translations.DISEASE_PANEL_TEXTS['squash_not_detected_message']['en']
                s_msg_kn = translations.DISEASE_PANEL_TEXTS['squash_not_detected_message']['kn']
                s_msg_hi = translations.DISEASE_PANEL_TEXTS['squash_not_detected_message']['hi']
            else:
                conf_lbl_en = translations.get_confidence_level(confidence, 'en')
                conf_lbl_kn = translations.get_confidence_level(confidence, 'kn')
                conf_lbl_hi = translations.get_confidence_level(confidence, 'hi')
                s_msg_en = f"{translations.DISEASE_PANEL_TEXTS['squash_detected_message']['en']} ({conf_lbl_en})"
                s_msg_kn = f"{translations.DISEASE_PANEL_TEXTS['squash_detected_message']['kn']} ({conf_lbl_kn})"
                s_msg_hi = f"{translations.DISEASE_PANEL_TEXTS['squash_detected_message']['hi']} ({conf_lbl_hi})"

            session["disease_result_en"] = s_msg_en
            session["disease_result_kn"] = s_msg_kn
            session["disease_result_hi"] = s_msg_hi
            session["disease_result"] = s_msg_kn if lang == 'kn' else (s_msg_hi if lang == 'hi' else s_msg_en)
            session['uploaded_image'] = filepath

            if request.headers.get('Accept') == 'application/json' or request.is_json:
                return jsonify({
                    'status': 'success',
                    'is_valid_leaf': True,
                    'is_confident': True,
                    'crop': 'Squash',
                    'disease': predicted_disease,
                    'confidence': confidence,
                    'result': s_msg_kn if lang == 'kn' else (s_msg_hi if lang == 'hi' else s_msg_en),
                    'result_en': s_msg_en,
                    'result_kn': s_msg_kn,
                    'result_hi': s_msg_hi,
                    'image_path': filepath
                })

            return render_template("index.html", **get_session_data())

        # Standard Diagnosis Success
        session["predicted_crop"] = predicted_crop
        session["predicted_disease"] = predicted_disease
        session["disease_confidence"] = confidence

        dis_en = translations.get_disease_translation(predicted_crop, predicted_disease, 'en')
        dis_kn = translations.get_disease_translation(predicted_crop, predicted_disease, 'kn')
        dis_hi = translations.get_disease_translation(predicted_crop, predicted_disease, 'hi')

        conf_lbl_en = translations.get_confidence_level(confidence, 'en')
        conf_lbl_kn = translations.get_confidence_level(confidence, 'kn')
        conf_lbl_hi = translations.get_confidence_level(confidence, 'hi')

        dis_result_en = f"{dis_en} ({conf_lbl_en})"
        dis_result_kn = f"{dis_kn} ({conf_lbl_kn})"
        dis_result_hi = f"{dis_hi} ({conf_lbl_hi})"

        session["disease_result_en"] = dis_result_en
        session["disease_result_kn"] = dis_result_kn
        session["disease_result_hi"] = dis_result_hi
        session["disease_result"] = dis_result_kn if lang == 'kn' else (dis_result_hi if lang == 'hi' else dis_result_en)

        session['uploaded_image'] = filepath

        if request.headers.get('Accept') == 'application/json' or request.is_json:
            return jsonify({
                'status': 'success',
                'is_valid_leaf': True,
                'is_confident': True,
                'crop': predicted_crop,
                'disease': predicted_disease,
                'confidence': confidence,
                'result': dis_result_kn if lang == 'kn' else (dis_result_hi if lang == 'hi' else dis_result_en),
                'result_en': dis_result_en,
                'result_kn': dis_result_kn,
                'result_hi': dis_result_hi,
                'image_path': filepath
            })

        return render_template(
            "index.html",
            **get_session_data()
        )

    except Exception as e:
        print(f"[predict_disease] Error during diagnosis: {e}")
        import traceback
        traceback.print_exc()

        err_msg = f"Diagnosis error: {str(e)}"
        session["predicted_crop"] = "Error"
        session["predicted_disease"] = str(e)
        session["disease_confidence"] = 0.0
        session["disease_result_en"] = f"❌ {err_msg}"
        session["disease_result_kn"] = "❌ ಫೋಟೋ ವಿಶ್ಲೇಷಣೆ ವಿಫಲವಾಗಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೊಮ್ಮೆ ಪ್ರಯತ್ನಿಸಿ."
        session["disease_result_hi"] = "❌ फोटो का विश्लेषण विफल रहा। कृपया पुनः प्रयास करें।"
        session["disease_result"] = session["disease_result_kn"] if lang == 'kn' else (session["disease_result_hi"] if lang == 'hi' else session["disease_result_en"])

        if request.headers.get('Accept') == 'application/json' or request.is_json:
            return jsonify({
                'status': 'error',
                'is_valid_leaf': False,
                'is_confident': False,
                'crop': crop_type,
                'disease': 'Error',
                'confidence': 0.0,
                'error': err_msg,
                'result': err_msg,
                'result_kn': session["disease_result_kn"],
                'result_hi': session["disease_result_hi"]
            }), 500

        return render_template(
            "index.html",
            **get_session_data()
        )

@app.route('/api/disease_crops', methods=['GET'])
def api_disease_crops():
    lang = request.args.get('lang') or session.get('lang', 'en')
    grouped = translations.get_disease_crops_grouped(lang)
    coverage_line = translations.get_disease_coverage_line(lang)
    panel_texts = {}
    for k, v in translations.DISEASE_PANEL_TEXTS.items():
        if isinstance(v, dict):
            panel_texts[k] = v.get(lang, v.get('en', ''))
        else:
            panel_texts[k] = str(v)
    return jsonify({
        'status': 'success',
        'groups': grouped,
        'coverage_line': coverage_line,
        'panel_texts': panel_texts
    })

@app.route('/api/crop_disease_samples', methods=['GET', 'POST'])
def api_crop_disease_samples():
    crop = request.args.get('crop') or request.form.get('crop') or session.get('recommended_crop') or 'Soybean'
    lang = request.args.get('lang') or request.form.get('lang') or session.get('lang', 'en')
    samples = translations.get_crop_disease_samples(crop, lang)
    is_supp = translations.is_disease_diagnosis_supported(crop)
    notice = translations.get_crop_support_notice(crop, lang)
    coverage_line = translations.get_disease_coverage_line(lang)
    return jsonify({
        'status': 'success',
        'crop': crop,
        'is_diagnosis_supported': is_supp,
        'samples': samples,
        'notice': notice,
        'coverage_line': coverage_line
    })

# ===============================

# # Smart Irrigation Agent Route
# ===============================
@app.route('/predict_irrigation', methods=['POST'])
def predict_irrigation():
    try:
        req_json = request.get_json(silent=True) or {}
        lang = request.form.get('lang') or req_json.get('lang') or request.args.get('lang') or session.get('lang', 'en')
        session['lang'] = lang

        crop = request.form.get('crop', '') or session.get('recommended_crop') or 'Tomato'
        growth_stage = request.form.get('growth_stage', 'vegetative')
        soil_type = request.form.get('soil_type', 'loam')
        area_acres = request.form.get('area_acres', '1.0')
        irrigation_type = request.form.get('irrigation_type', 'drip')
        district = request.form.get('district', '') or session.get('selected_district') or session.get('city') or 'Dharwad'
        pump_flow_rate = request.form.get('pump_flow_rate')
        days_after_sowing = request.form.get('days_after_sowing') or request.form.get('das')
        irrigation_efficiency = request.form.get('irrigation_efficiency') or request.form.get('efficiency')

        if request.is_json:
            j_body = request.get_json(silent=True) or {}
            crop = j_body.get('crop') or crop
            growth_stage = j_body.get('growth_stage') or growth_stage
            soil_type = j_body.get('soil_type') or soil_type
            area_acres = j_body.get('area_acres') or area_acres
            irrigation_type = j_body.get('irrigation_type') or irrigation_type
            district = j_body.get('district') or district
            pump_flow_rate = j_body.get('pump_flow_rate') or pump_flow_rate
            days_after_sowing = j_body.get('days_after_sowing') or days_after_sowing
            irrigation_efficiency = j_body.get('irrigation_efficiency') or irrigation_efficiency

        # Fetch live district weather
        temp, humidity, weather_desc = 28.0, 55.0, "clear sky"
        rainfall_mm = 0.0
        try:
            temp_f, hum_f, w_desc = get_weather(district)
            temp = float(temp_f) if temp_f is not None else 28.0
            humidity = float(hum_f) if hum_f is not None else 55.0
            weather_desc = w_desc or "clear sky"
            if 'rain' in weather_desc.lower():
                rainfall_mm = 8.0
        except Exception:
            pass

        irri_data = translations.calculate_smart_irrigation(
            crop=crop,
            growth_stage=growth_stage,
            soil_type=soil_type,
            area_acres=area_acres,
            irrigation_type=irrigation_type,
            temp=temp,
            humidity=humidity,
            rainfall_mm=rainfall_mm,
            weather_desc=weather_desc,
            district=district,
            pump_flow_rate=pump_flow_rate,
            irrigation_efficiency=irrigation_efficiency,
            days_after_sowing=days_after_sowing,
            lang=lang
        )

        session['irrigation_data'] = irri_data
        session['irrigation_crop'] = crop
        session['irrigation_stage'] = growth_stage
        session['irrigation_soil'] = soil_type
        session['irrigation_area'] = area_acres
        session['irrigation_method'] = irrigation_type
        session['irrigation_district'] = district
        session['irrigation_pump_flow_rate'] = pump_flow_rate
        session['irrigation_days_after_sowing'] = days_after_sowing
        session['irrigation_efficiency'] = irrigation_efficiency

        session['irrigation_result_en'] = irri_data['advice_en']
        session['irrigation_result_kn'] = irri_data['advice_kn']
        session['irrigation_result_hi'] = irri_data['advice_hi']
        session['irrigation_result'] = irri_data[f'advice_{lang}']

        session['irrigation_form_data'] = {
            'crop': crop,
            'growth_stage': growth_stage,
            'soil_type': soil_type,
            'area_acres': area_acres,
            'irrigation_type': irrigation_type,
            'district': district,
            'pump_flow_rate': pump_flow_rate
        }

        if request.headers.get('Accept') == 'application/json' or request.is_json:
            return jsonify({
                'data': irri_data,
                'result_en': irri_data['advice_en'],
                'result_kn': irri_data['advice_kn'],
                'result_hi': irri_data['advice_hi'],
                'result': irri_data.get(f'advice_{lang}', irri_data['advice_en'])
            })

        return render_template(
            "index.html",
            **get_session_data()
        )

    except Exception as e:
        session['irrigation_result'] = f"Error: {str(e)}"
        if request.headers.get('Accept') == 'application/json' or request.is_json:
            return jsonify({"error": str(e)}), 500
        return render_template(
            "index.html",
            **get_session_data()
        )

# ===============================
# Session Reset Route
# ===============================
@app.route('/reset', methods=['GET', 'POST'])
def reset_session():
    lang = session.get('lang', 'en')
    logged_in = session.get('logged_in', False)
    username = session.get('username')
    user_type = session.get('user_type')
    user_name = session.get('user_name')

    session.clear()

    session['lang'] = lang
    session['logged_in'] = logged_in
    if username:
        session['username'] = username
    if user_type:
        session['user_type'] = user_type
    if user_name:
        session['user_name'] = user_name

    if request.headers.get('Accept') == 'application/json' or request.is_json:
        return jsonify({"status": "reset"})
    return redirect('/')

# ===============================
# Planner Agent with Priority Rules
# ===============================
@app.route('/planner', methods=['POST'])
def planner():
    try:
        req_json = request.get_json(silent=True) or {}
        lang = request.form.get('lang') or req_json.get('lang') or request.args.get('lang') or session.get('lang', 'en')
        session['lang'] = lang

        crop_input = request.form.get('crop') or req_json.get('crop') or session.get('recommended_crop', '')
        from models.agri_calendar_service import normalize_crop_name
        crop_name = normalize_crop_name(crop_input) if crop_input else session.get('recommended_crop', '')
        crop_tr_en = translations.get_crop_name(crop_name, 'en') if crop_name else 'Crop'
        crop_tr_kn = translations.get_crop_name(crop_name, 'kn') if crop_name else 'ಬೆಳೆ'
        crop_tr_hi = translations.get_crop_name(crop_name, 'hi') if crop_name else 'फसल'

        city = session.get('city', '') or session.get('selected_district', '') or 'Dharwad'
        predicted_crop = session.get('predicted_crop', '')
        predicted_disease = session.get('predicted_disease', '')

        # Synchronize active FarmContext
        update_farm_context(
            crop=crop_name,
            crop_key=crop_name.lower() if crop_name else '',
            district=city
        )

        # ── Cross-Crop Disease Diagnostic Validation ──────────────────
        rec_norm = translations.normalize_disease_crop(crop_name)
        diag_norm = translations.normalize_disease_crop(predicted_crop)

        is_same_crop = bool(rec_norm and diag_norm and rec_norm == diag_norm)
        is_invalid_disease = (
            not predicted_disease
            or predicted_disease in ['DiseaseNotDetected', 'CropMismatch', 'Unsupported', 'Uncertain', 'Invalid']
            or predicted_crop in ['CropMismatch', 'Unsupported', 'Uncertain', 'Invalid']
        )

        advice_en, advice_kn, advice_hi = [], [], []
        alert_en, alert_kn, alert_hi = [], [], []
        priority_en, priority_kn, priority_hi = [], [], []

        # ── Priority 1: Disease ───────────────────────────────────────
        critical_diseases = ['blight', 'virus', 'rot', 'mildew', 'blast']
        moderate_diseases = ['spot', 'rust', 'scorch', 'cercospora', 'mite']
        disease_priority = "none"

        if is_invalid_disease:
            disease_priority = "none"
            advice_en.append(f"🌿 Crop Health: No active leaf disease reported for {crop_tr_en} (Preventive IPM active).")
            advice_kn.append(f"🌿 ಬೆಳೆ ಆರೋಗ್ಯ: {crop_tr_kn} ಬೆಳೆಗೆ ಯಾವುದೇ ರೋಗ ದಾಖಲಾಗಿಲ್ಲ (ಮುನ್ನೆಚ್ಚರಿಕೆ IPM ಸಕ್ರಿಯ).")
            advice_hi.append(f"🌿 फसल स्वास्थ्य: {crop_tr_hi} के लिए कोई सक्रिय रोग नहीं (निवारक IPM सक्रिय)।")
        elif is_same_crop:
            disease_lower = predicted_disease.lower()
            dis_tr_kn = translations.get_disease_translation(predicted_crop or crop_name, predicted_disease, 'kn')
            dis_tr_hi = translations.get_disease_translation(predicted_crop or crop_name, predicted_disease, 'hi')

            if "healthy" in disease_lower:
                advice_en.append(f"✅ {crop_tr_en} plant is HEALTHY — safe to proceed with farming.")
                advice_kn.append(f"✅ {crop_tr_kn} ಸಸ್ಯವು ಆರೋಗ್ಯಕರವಾಗಿದೆ — ಕೃಷಿ ಕಾರ್ಯವನ್ನು ಮುಂದುವರಿಸಬಹುದು.")
                advice_hi.append(f"✅ {crop_tr_hi} पौधा स्वस्थ है — खेती कार्य जारी रखना सुरक्षित है।")
                disease_priority = "healthy"
            elif any(d in disease_lower for d in critical_diseases):
                priority_en.append(
                    f"🚨 CRITICAL PRIORITY: {crop_tr_en} : {predicted_disease} detected — DO NOT SOW until disease is fully treated. Apply fungicide immediately."
                )
                priority_kn.append(
                    f"🚨 ತುರ್ತು ಎಚ್ಚರಿಕೆ: {crop_tr_kn} : {dis_tr_kn} ಪತ್ತೆಯಾಗಿದೆ — ರೋಗ ನಿವಾರಣೆಯಾಗುವವರೆಗೆ ಬಿತ್ತನೆ ಮಾಡಬೇಡಿ. ಸೂಕ್ತ ಶಿಲೀಂಧ್ರನಾಶಕ ಸಿಂಪಡಿಸಿ."
                )
                priority_hi.append(
                    f"🚨 अति महत्वपूर्ण चेतावनी: {crop_tr_hi} : {dis_tr_hi} पाया गया — बीमारी ठीक होने तक बुवाई न करें। तुरंत कवकनाशी छिड़कें।"
                )
                disease_priority = "critical"
            elif any(d in disease_lower for d in moderate_diseases):
                alert_en.append(f"⚠ MODERATE ALERT: {crop_tr_en} : {predicted_disease} detected — Treat affected plants before proceeding.")
                alert_kn.append(f"⚠ ಮಧ್ಯಮ ಎಚ್ಚರಿಕೆ: {crop_tr_kn} : {dis_tr_kn} ಪತ್ತೆಯಾಗಿದೆ — ಕೃಷಿ ಮುಂದುವರಿಸುವ ಮೊದಲು ಚಿಕಿತ್ಸೆ ನೀಡಿ.")
                alert_hi.append(f"⚠ मध्यम चेतावनी: {crop_tr_hi} : {dis_tr_hi} पाया गया — आगे बढ़ने से पहले प्रभावित पौधों का उपचार करें।")
                disease_priority = "moderate"
            else:
                alert_en.append(f"⚠ Disease Detected: {crop_tr_en} : {predicted_disease} — Consult local agricultural officer.")
                alert_kn.append(f"⚠ ರೋಗ ಪತ್ತೆಯಾಗಿದೆ: {crop_tr_kn} : {dis_tr_kn} — ಸ್ಥಳೀಯ ಕೃಷಿ ಅಧಿಕಾರಿಯನ್ನು ಸಂಪರ್ಕಿಸಿ.")
                alert_hi.append(f"⚠ रोग पहचाना गया: {crop_tr_hi} : {dis_tr_hi} — स्थानीय कृषि अधिकारी से परामर्श लें।")
                disease_priority = "unknown"
        else:
            # Diagnosis was for a different crop -> emit informative note, not a blocking alert
            dis_tr_kn = translations.get_disease_translation(predicted_crop or 'Crop', predicted_disease, 'kn')
            dis_tr_hi = translations.get_disease_translation(predicted_crop or 'Crop', predicted_disease, 'hi')
            advice_en.append(f"🌿 Crop Health: No active leaf disease reported for {crop_tr_en}. (Note: Previous diagnostic scan was for {predicted_crop} — {predicted_disease}).")
            advice_kn.append(f"🌿 ಬೆಳೆ ಆರೋಗ್ಯ: {crop_tr_kn} ಬೆಳೆಗೆ ಯಾವುದೇ ರೋಗ ದಾಖಲಾಗಿಲ್ಲ. (ಗಮನಿಸಿ: ಹಿಂದಿನ ಪರೀಕ್ಷೆ {predicted_crop} — {dis_tr_kn}).")
            advice_hi.append(f"🌿 फसल स्वास्थ्य: {crop_tr_hi} के लिए कोई सक्रिय रोग दर्ज नहीं है। (पिछली जांच: {predicted_crop} — {dis_tr_hi})।")
            disease_priority = "none"

        # ── Priority 2: Weather ───────────────────────────────────────
        weather_priority = "normal"
        temp, humidity, weather_desc = get_weather(city)
        if city:
            if temp > 40:
                priority_en.append(f"🌡 CRITICAL: Extreme heat ({temp}°C) in {city} — Farming not recommended.")
                priority_kn.append(f"🌡 ತೀವ್ರ ಎಚ್ಚರಿಕೆ: {city}ನಲ್ಲಿ ವಿಪರೀತ ಬಿಸಿಲು ({temp}°C) — ಕೃಷಿ ಸೂಕ್ತವಲ್ಲ.")
                priority_hi.append(f"🌡 गंभीर चेतावनी: {city} में अत्यधिक गर्मी ({temp}°C) — खेती की सलाह नहीं।")
                weather_priority = "critical"
            elif temp > 35:
                alert_en.append(f"🌡 HIGH TEMP WARNING: {temp}°C in {city} — Increase irrigation frequency.")
                alert_kn.append(f"🌡 ಹೆಚ್ಚಿನ ತಾಪಮಾನ ಎಚ್ಚರಿಕೆ: {city}ನಲ್ಲಿ {temp}°C — ನೀರಾವರಿಯನ್ನು ಹೆಚ್ಚಿಸಿ.")
                alert_hi.append(f"🌡 उच्च तापमान चेतावनी: {city} में {temp}°C — सिंचाई की आवृत्ति बढ़ाएं।")
                weather_priority = "warning"
            elif temp < 5:
                priority_en.append(f"❄ CRITICAL: Frost risk ({temp}°C) in {city} — Protect crops immediately.")
                priority_kn.append(f"❄ ತೀವ್ರ ಎಚ್ಚರಿಕೆ: {city}ನಲ್ಲಿ ಹಿಮಗಡ್ಡೆ ಅಪಾಯ ({temp}°C) — ಬೆಳೆಗಳನ್ನು ರಕ್ಷಿಸಿ.")
                priority_hi.append(f"❄ गंभीर चेतावनी: {city} में पाले का खतरा ({temp}°C) — फसलों की तुरंत रक्षा करें।")
                weather_priority = "critical"
            else:
                w_kn = translations.format_weather_status(city, temp, humidity, weather_desc, 'kn')
                w_hi = translations.format_weather_status(city, temp, humidity, weather_desc, 'hi')
                advice_en.append(f"✅ Weather in {city}: {temp}°C, {humidity}% humidity — {weather_desc}. Suitable for farming.")
                advice_kn.append(f"✅ {w_kn}. ಕೃಷಿಗೆ ಸೂಕ್ತವಾಗಿದೆ.")
                advice_hi.append(f"✅ {w_hi}। खेती के लिए अनुकूल मौसम।")
                weather_priority = "normal"

        # ── Priority 3: Market Price (Strict District & Crop Auto-Sync) ──
        price_priority = "normal"
        target_crop = crop_name or session.get('price_crop') or 'Rice'
        target_dist = city

        price_crop_match = (session.get('price_crop', '').lower() == target_crop.lower())
        price_dist_match = (session.get('price_district', '').lower() == target_dist.lower())
        has_price_res = bool(session.get('price_result_en'))

        if not (price_crop_match and price_dist_match and has_price_res):
            now_dt = datetime.now()
            p_data = compute_price_forecast(target_crop, target_dist, now_dt.month, now_dt.year)
            session['price_crop'] = target_crop
            session['price_district'] = target_dist
            session['predicted_price'] = p_data['prediction']
            session['price_result_en'] = p_data['price_en']
            session['price_result_kn'] = p_data['price_kn']
            session['price_result_hi'] = p_data['price_hi']
            session['price_result'] = p_data['price_kn'] if lang == 'kn' else (p_data['price_hi'] if lang == 'hi' else p_data['price_en'])
            session['price_spot_clean_en'] = p_data['spot_clean_en']
            session['price_forecast_clean_en'] = p_data['forecast_clean_en']
            session['price_spot_clean_kn'] = p_data['spot_clean_kn']
            session['price_forecast_clean_kn'] = p_data['forecast_clean_kn']
            session['price_spot_clean_hi'] = p_data['spot_clean_hi']
            session['price_forecast_clean_hi'] = p_data['forecast_clean_hi']

        price = session.get('predicted_price', 0)
        price_res_en = session.get('price_result_en', '')
        price_res_kn = session.get('price_result_kn', '')
        price_res_hi = session.get('price_result_hi', '')

        if price_res_en:
            advice_en.append(f"💹 {price_res_en}")
            advice_kn.append(f"💹 {price_res_kn or price_res_en}")
            advice_hi.append(f"💹 {price_res_hi or price_res_en}")
            if price >= 3000:
                price_priority = "high"
            elif price >= 1500:
                price_priority = "moderate"
            else:
                price_priority = "low"
        elif price > 0:
            if price >= 3000:
                advice_en.append(f"✅ Market price is HIGH (₹{price}) — Excellent time to sell {crop_tr_en}.")
                advice_kn.append(f"✅ ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಹೆಚ್ಚಾಗಿದೆ (₹{price}) — {crop_tr_kn} ಮಾರಾಟ ಮಾಡಲು ಅತ್ಯುತ್ತಮ ಸಮಯ.")
                advice_hi.append(f"✅ बाजार भाव बहुत अच्छा है (₹{price}) — {crop_tr_hi} बेचने का सही समय।")
                price_priority = "high"
            elif price >= 1500:
                advice_en.append(f"✅ Market price is MODERATE (₹{price}) — Good time to grow and sell {crop_tr_en}.")
                advice_kn.append(f"✅ ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಮಧ್ಯಮವಾಗಿದೆ (₹{price}) — {crop_tr_kn} ಬೆಳೆದು ಮಾರಲು ಸೂಕ್ತ ಸಮಯ.")
                advice_hi.append(f"✅ बाजार भाव सामान्य है (₹{price}) — {crop_tr_hi} उगाने और बेचने का अच्छा समय।")
                price_priority = "moderate"
            else:
                alert_en.append(f"⚠ Market price is LOW (₹{price}) — Consider storing crop or alternative.")
                alert_kn.append(f"⚠ ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಕಡಿಮೆಯಾಗಿದೆ (₹{price}) — ಬೆಳೆಯನ್ನು ದಾಸ್ತಾನು ಮಾಡಲು ಅಥವಾ ಪರ್ಯಾಯ ಬೆಳೆ ಆಲೋಚಿಸಿ.")
                alert_hi.append(f"⚠ बाजार भाव कम है (₹{price}) — फसल का भंडारण करें या अन्य विकल्प देखें।")
                price_priority = "low"
        else:
            alert_en.append("⚠ No market price data provided.")
            alert_kn.append("⚠ ಯಾವುದೇ ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ.")
            alert_hi.append("⚠ कोई बाजार मूल्य डेटा उपलब्ध नहीं है।")

        # ── Priority 4: Crop ──────────────────────────────────────────
        if crop_name:
            advice_en.append(f"✅ Recommended crop for your soil and climate: {crop_tr_en.upper()}")
            advice_kn.append(f"✅ ನಿಮ್ಮ ಮಣ್ಣು ಮತ್ತು ಹವಾಮಾನಕ್ಕೆ ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆ: {crop_tr_kn.upper()}")
            advice_hi.append(f"✅ आपकी मिट्टी और जलवायु के लिए अनुशंसित फसल: {crop_tr_hi.upper()}")

        # ── Priority 5: Smart Irrigation Integration ───────────────────
        irri_info = session.get('irrigation_data')
        if irri_info:
            advice_en.append(f"💧 Smart Irrigation Plan: {irri_info['advice_en']}")
            advice_kn.append(f"💧 ಸ್ಮಾರ್ಟ್ ನೀರಾವರಿ ಯೋಜನೆ: {irri_info['advice_kn']}")
            advice_hi.append(f"💧 स्मार्ट सिंचाई योजना: {irri_info['advice_hi']}")
            if irri_info.get('rain_alert'):
                alert_en.append(irri_info['rain_alert_en'])
                alert_kn.append(irri_info['rain_alert_kn'])
                alert_hi.append(irri_info['rain_alert_hi'])

        # ── Conflict Resolution / Summary ─────────────────────────────
        if disease_priority == "critical" or weather_priority == "critical":
            sum_en = "🚨 STOP — Critical issues detected! Address all critical alerts before any farming activity."
            sum_kn = "🚨 ನಿಲ್ಲಿ — ತುರ್ತು ಸಮಸ್ಯೆಗಳು ಕಂಡುಬಂದಿವೆ! ಕೃಷಿ ಕಾರ್ಯದ ಮೊದಲು ಎಲ್ಲಾ ತುರ್ತು ಎಚ್ಚರಿಕೆಗಳನ್ನು ಪರಿಹರಿಸಿ."
            sum_hi = "🚨 रुकें — गंभीर समस्याएं पाई गईं! खेती से पहले सभी महत्वपूर्ण चेतावनियों का समाधान करें।"
        elif disease_priority == "moderate" or weather_priority == "warning":
            if price_priority == "low":
                sum_en = f"⚠ HIGH RISK — Disease present AND market price is low. Consider alternative crop instead of {crop_tr_en}."
                sum_kn = f"⚠ ಹೆಚ್ಚಿನ ಅಪಾಯ — ರೋಗವಿದೆ ಮತ್ತು ಮಾರುಕಟ್ಟೆ ಬೆಲೆಯೂ ಕಡಿಮೆಯಿದೆ. {crop_tr_kn} ಬದಲಿಗೆ ಪರ್ಯಾಯ ಬೆಳೆ ಪರಿಗಣಿಸಿ."
                sum_hi = f"⚠ उच्च जोखिम — बीमारी भी है और बाजार भाव भी कम है। {crop_tr_hi} के स्थान पर अन्य फसल पर विचार करें।"
            else:
                sum_en = f"🌾 Proceed with CAUTION — Treat disease first, then sow {crop_tr_en}."
                sum_kn = f"🌾 ಎಚ್ಚರಿಕೆಯಿಂದ ಮುಂದುವರಿಯಿರಿ — ಮೊದಲು ರೋಗ ನಿವಾರಣೆ ಮಾಡಿ, ನಂತರ {crop_tr_kn} ಬಿತ್ತನೆ ಮಾಡಿ."
                sum_hi = f"🌾 सावधानी से आगे बढ़ें — पहले बीमारी का इलाज करें, फिर {crop_tr_hi} बोएं।"
        elif disease_priority == "healthy" and weather_priority == "normal":
            if price_priority == "high":
                sum_en = f"🌾 EXCELLENT CONDITIONS — Grow {crop_tr_en} now! High market price and good weather."
                sum_kn = f"🌾 ಅತ್ಯುತ್ತಮ ಪರಿಸ್ಥಿತಿಗಳು — ಈಗಲೇ {crop_tr_kn} ಬೆಳೆಯಿರಿ! ಉತ್ತಮ ಮಾರುಕಟ್ಟೆ ದರ ಮತ್ತು ಹವಾಮಾನವಿದೆ."
                sum_hi = f"🌾 उत्तम परिस्थितियां — अभी {crop_tr_hi} उगाएं! बेहतरीन बाजार भाव और अनुकूल मौसम।"
            elif price_priority == "low":
                sum_en = f"🌾 Good farming conditions but market price is LOW. Consider storing {crop_tr_en} and selling later."
                sum_kn = f"🌾 ಉತ್ತಮ ಕೃಷಿ ಪರಿಸ್ಥಿತಿ ಆದರೆ ಬೆಲೆ ಕಡಿಮೆಯಿದೆ. {crop_tr_kn} ದಾಸ್ತಾನು ಮಾಡಿ ನಂತರ ಮಾರಾಟ ಮಾಡಲು ಯೋಚಿಸಿ."
                sum_hi = f"🌾 खेती के लिए अच्छी स्थिति है पर भाव कम है। {crop_tr_hi} का भंडारण करके बाद में बेचने पर विचार करें।"
            else:
                sum_en = f"🌾 All conditions are FAVORABLE — Proceed with growing {crop_tr_en}."
                sum_kn = f"🌾 ಎಲ್ಲಾ ಪರಿಸ್ಥಿತಿಗಳು ಅನುಕೂಲಕರವಾಗಿವೆ — {crop_tr_kn} ಬೆಳೆಯಲು ಮುಂದುವರಿಯಿರಿ."
                sum_hi = f"🌾 सभी स्थितियां अनुकूल हैं — {crop_tr_hi} की खेती के साथ आगे बढ़ें।"
        else:
            sum_en = f"🌾 Proceed with caution. Address alerts before sowing {crop_tr_en}."
            sum_kn = f"🌾 ಎಚ್ಚರಿಕೆಯಿಂದ ಮುಂದುವರಿಯಿರಿ. {crop_tr_kn} ಬಿತ್ತನೆ ಮಾಡುವ ಮುನ್ನ ಎಚ್ಚರಿಕೆಗಳನ್ನು ಗಮನಿಸಿ."
            sum_hi = f"🌾 सावधानी से आगे बढ़ें। {crop_tr_hi} बोने से पहले चेतावनियों पर ध्यान दें।"

        # ── Layer 5: Decision & Recommendation ───────────────────────
        crop_lower = crop_name.lower() if crop_name else 'default'
        c_meta = translations.CROP_TRANSLATIONS.get(crop_lower)
        if not c_meta:
            c_meta = translations.CROP_TRANSLATIONS.get(normalize_crop_name(crop_lower), translations.CROP_TRANSLATIONS['default'])

        plant_en = f"🌱 Best planting months for {crop_tr_en.upper()}: {c_meta['planting_months']['en']}"
        plant_kn = f"🌱 {crop_tr_kn.upper()} ಬಿತ್ತನೆಗೆ ಉತ್ತಮ ಸಮಯ: {c_meta['planting_months']['kn']}"
        plant_hi = f"🌱 {crop_tr_hi.upper()} की बुवाई का सर्वोत्तम समय: {c_meta['planting_months']['hi']}"

        harv_en = f"🌾 Expected harvest months: {c_meta['harvest_months']['en']}"
        harv_kn = f"🌾 ನಿರೀಕ್ಷಿತ ಕೊಯ್ಲು ತಿಂಗಳುಗಳು: {c_meta['harvest_months']['kn']}"
        harv_hi = f"🌾 कटाई के अनुमानित महीने: {c_meta['harvest_months']['hi']}"

        fert_en = f"🌿 Fertilizer plan for {crop_tr_en.upper()}: {c_meta['fertilizer']['en']}"
        fert_kn = f"🌿 {crop_tr_kn.upper()} ಗೊಬ್ಬರದ ಪ್ರಮಾಣ: {c_meta['fertilizer']['kn']}"
        fert_hi = f"🌿 {crop_tr_hi.upper()} उर्वरक योजना: {c_meta['fertilizer']['hi']}"

        pests_en = c_meta['pests']['en']
        pests_kn = c_meta['pests']['kn']
        pests_hi = c_meta['pests']['hi']

        spot_clean_en = session.get('price_spot_clean_en', '')
        forecast_clean_en = session.get('price_forecast_clean_en', '')
        spot_clean_kn = session.get('price_spot_clean_kn', '')
        forecast_clean_kn = session.get('price_forecast_clean_kn', '')
        spot_clean_hi = session.get('price_spot_clean_hi', '')
        forecast_clean_hi = session.get('price_forecast_clean_hi', '')

        if spot_clean_en:
            sell_en = f"{spot_clean_en}\n\n{forecast_clean_en}\n\n💡 Peak Selling Months: {c_meta['best_sell_months']['en']}. {c_meta['sell_tip']['en']}"
            sell_kn = f"{spot_clean_kn or spot_clean_en}\n\n{forecast_clean_kn or forecast_clean_en}\n\n💡 ಮಾರಾಟಕ್ಕೆ ಸೂಕ್ತ ತಿಂಗಳುಗಳು: {c_meta['best_sell_months']['kn']}. {c_meta['sell_tip']['kn']}"
            sell_hi = f"{spot_clean_hi or spot_clean_en}\n\n{forecast_clean_hi or forecast_clean_en}\n\n💡 बेचने के सर्वोत्तम महीने: {c_meta['best_sell_months']['hi']}। {c_meta['sell_tip']['hi']}"
        elif price_res_en:
            sell_en = f"💰 {price_res_en}\n\n💡 Peak Selling Months: {c_meta['best_sell_months']['en']}. {c_meta['sell_tip']['en']}"
            sell_kn = f"💰 {price_res_kn or price_res_en}\n\n💡 ಮಾರಾಟಕ್ಕೆ ಸೂಕ್ತ ತಿಂಗಳುಗಳು: {c_meta['best_sell_months']['kn']}. {c_meta['sell_tip']['kn']}"
            sell_hi = f"💰 {price_res_hi or price_res_en}\n\n💡 बेचने के सर्वोत्तम महीने: {c_meta['best_sell_months']['hi']}। {c_meta['sell_tip']['hi']}"
        else:
            sell_en = f"💰 Best selling months for {crop_tr_en.upper()}: {c_meta['best_sell_months']['en']}.\n💡 Strategy: {c_meta['sell_tip']['en']}"
            sell_kn = f"💰 {crop_tr_kn.upper()} ಮಾರಾಟಕ್ಕೆ ಸೂಕ್ತ ತಿಂಗಳುಗಳು: {c_meta['best_sell_months']['kn']}.\n💡 ಸಲಹೆ: {c_meta['sell_tip']['kn']}"
            sell_hi = f"💰 {crop_tr_hi.upper()} बेचने के सर्वोत्तम महीने: {c_meta['best_sell_months']['hi']}।\n💡 रणनीति: {c_meta['sell_tip']['hi']}"

        # ── Layer 6: AI Agronomist 360° Strategic Farm Plan (LLM + RAG) ──
        ai_plan_result = ""
        ai_provider = "SmartAgri AI Engine"
        ai_sources = []
        if agri_llm:
            try:
                price_str = f"₹ {price}" if price > 0 else (price_res_en or "Standard Market Rate")
                weather_dict = {'temp': temp, 'humidity': humidity, 'desc': weather_desc} if (temp or humidity) else None
                disease_for_llm = f"{predicted_crop} : {predicted_disease}" if (is_same_crop and not is_invalid_disease) else "None detected"

                soil_val = session.get('irrigation_soil') or (irri_info.get('soil_type') if irri_info else 'loam')
                ai_res = agri_llm.generate_planner_agent_strategy(
                    crop=crop_name or 'Rice',
                    disease=disease_for_llm,
                    price=price_str,
                    district=city or 'Dharwad',
                    irrigation_data=irri_info,
                    weather_data=weather_dict,
                    soil_type=soil_val,
                    lang=lang
                )
                ai_plan_result = ai_res.get('ai_plan', '')
                ai_provider = ai_res.get('provider', 'SmartAgri AI Engine')
                ai_sources = ai_res.get('sources', [])
                session['planner_ai_plan'] = ai_plan_result
                session['planner_ai_plan_en'] = ai_res.get('ai_plan_en', ai_plan_result)
                session['planner_ai_plan_kn'] = ai_res.get('ai_plan_kn', ai_plan_result)
                session['planner_ai_plan_hi'] = ai_res.get('ai_plan_hi', ai_plan_result)
                session['planner_ai_provider'] = ai_provider
            except Exception as _ai_e:
                print(f"[Planner AI] Generation notice: {_ai_e}")

        # ── Save to session ───────────────────────────────────────────
        session['planner_summary_en'] = sum_en
        session['planner_summary_kn'] = sum_kn
        session['planner_summary_hi'] = sum_hi
        session['planner_summary'] = sum_kn if lang == 'kn' else (sum_hi if lang == 'hi' else sum_en)

        session['planner_advice_en'] = advice_en
        session['planner_advice_kn'] = advice_kn
        session['planner_advice_hi'] = advice_hi
        session['planner_advice'] = advice_kn if lang == 'kn' else (advice_hi if lang == 'hi' else advice_en)

        session['planner_alerts_en'] = alert_en
        session['planner_alerts_kn'] = alert_kn
        session['planner_alerts_hi'] = alert_hi
        session['planner_alerts'] = alert_kn if lang == 'kn' else (alert_hi if lang == 'hi' else alert_en)

        session['planner_priority_en'] = priority_en
        session['planner_priority_kn'] = priority_kn
        session['planner_priority_hi'] = priority_hi
        session['planner_priority'] = priority_kn if lang == 'kn' else (priority_hi if lang == 'hi' else priority_en)

        if request.headers.get('Accept') == 'application/json' or request.is_json:
            return jsonify({
                'summary': sum_kn if lang == 'kn' else (sum_hi if lang == 'hi' else sum_en),
                'summary_en': sum_en,
                'summary_kn': sum_kn,
                'summary_hi': sum_hi,
                'planting_schedule': plant_kn if lang == 'kn' else (plant_hi if lang == 'hi' else plant_en),
                'planting_schedule_en': plant_en,
                'planting_schedule_kn': plant_kn,
                'planting_schedule_hi': plant_hi,
                'harvest_schedule': harv_kn if lang == 'kn' else (harv_hi if lang == 'hi' else harv_en),
                'harvest_schedule_en': harv_en,
                'harvest_schedule_kn': harv_kn,
                'harvest_schedule_hi': harv_hi,
                'fertilizer_plan': fert_kn if lang == 'kn' else (fert_hi if lang == 'hi' else fert_en),
                'fertilizer_plan_en': fert_en,
                'fertilizer_plan_kn': fert_kn,
                'fertilizer_plan_hi': fert_hi,
                'sell_recommendation': sell_kn if lang == 'kn' else (sell_hi if lang == 'hi' else sell_en),
                'sell_recommendation_en': sell_en,
                'sell_recommendation_kn': sell_kn,
                'sell_recommendation_hi': sell_hi,
                'pest_guide': pests_kn if lang == 'kn' else (pests_hi if lang == 'hi' else pests_en),
                'pest_guide_en': pests_en,
                'pest_guide_kn': pests_kn,
                'pest_guide_hi': pests_hi,
                'advice': advice_kn if lang == 'kn' else (advice_hi if lang == 'hi' else advice_en),
                'advice_en': advice_en,
                'advice_kn': advice_kn,
                'advice_hi': advice_hi,
                'alerts': alert_kn if lang == 'kn' else (alert_hi if lang == 'hi' else alert_en),
                'alerts_en': alert_en,
                'alerts_kn': alert_kn,
                'alerts_hi': alert_hi,
                'priority': priority_kn if lang == 'kn' else (priority_hi if lang == 'hi' else priority_en),
                'priority_en': priority_en,
                'priority_kn': priority_kn,
                'priority_hi': priority_hi,
                'ai_plan': ai_plan_result or session.get('planner_ai_plan', ''),
                'ai_plan_en': session.get('planner_ai_plan_en') or ai_plan_result,
                'ai_plan_kn': session.get('planner_ai_plan_kn') or ai_plan_result,
                'ai_plan_hi': session.get('planner_ai_plan_hi') or ai_plan_result,
                'provider': ai_provider,
                'sources': ai_sources
            })

        return render_template(
            "index.html",
            **get_session_data()
        )

    except Exception as e:
        if request.headers.get('Accept') == 'application/json' or request.is_json:
            return jsonify({"error": str(e)}), 500
        return render_template(
            "index.html",
            planner_summary=f"Error: {str(e)}",
            **get_session_data()
        )

# ===============================
# Voice/Text Query Answer
# ===============================
def build_query_answer(query, lang='en'):
    return translations.build_multilingual_voice_answer(query, lang)

@app.route('/answer_query', methods=['POST'])
def answer_query():
    try:
        query = request.form.get('query', '').strip()
        lang = request.form.get('lang', session.get('lang', 'en'))
        session['lang'] = lang
        session['query_text'] = query

        if agri_llm and query:
            if lang == 'kn':
                res = agri_llm.ask_agronomist_rag(query, lang='kn')
                ans_kn = res.get('answer', '')
                ans_en = ans_kn
                ans_hi = ans_kn
            elif lang == 'hi':
                res = agri_llm.ask_agronomist_rag(query, lang='hi')
                ans_hi = res.get('answer', '')
                ans_en = ans_hi
                ans_kn = ans_hi
            else:
                res = agri_llm.ask_agronomist_rag(query, lang='en')
                ans_en = res.get('answer', '')
                ans_kn = ans_en
                ans_hi = ans_en
        else:
            ans_en = translations.build_multilingual_voice_answer(query, 'en')
            ans_kn = translations.build_multilingual_voice_answer(query, 'kn')
            ans_hi = translations.build_multilingual_voice_answer(query, 'hi')

        session['query_answer_en'] = ans_en
        session['query_answer_kn'] = ans_kn
        session['query_answer_hi'] = ans_hi
        session['query_answer'] = ans_kn if lang == 'kn' else (ans_hi if lang == 'hi' else ans_en)

        return render_template(
            "index.html",
            **get_session_data()
        )
    except Exception as e:
        session['query_answer'] = f"Error: {str(e)}"
        return render_template(
            "index.html",
            **get_session_data()
        )

@app.route('/api/answer_query', methods=['POST'])
def api_answer_query():
    try:
        data = request.get_json(silent=True) or request.form
        query = (data.get('query') or '').strip()
        lang = data.get('lang', 'en')
        
        if not query:
            return jsonify({"answer": "Please ask a question about crops, fertilizers, or diseases."})

        if agri_llm:
            result = agri_llm.ask_agronomist_rag(query, lang=lang)
            return jsonify({
                "answer": result.get("answer", ""),
                "sources": result.get("sources", []),
                "provider": result.get("provider", "SmartAgri"),
                "has_rag_context": result.get("has_rag_context", False)
            })
        else:
            answer = translations.build_multilingual_voice_answer(query, lang)
            return jsonify({
                "answer": answer,
                "sources": ["[SmartAgri Translations]"],
                "provider": "Fallback"
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """
    Conversational AI Agronomist endpoint with LangChain RAG & multi-turn history.
    """
    try:
        data = request.get_json(silent=True) or request.form
        query = (data.get('message') or data.get('query') or '').strip()
        history = data.get('history') or []
        lang = data.get('lang', 'en')

        dashboard_context = data.get('dashboard_context')
        if not dashboard_context:
            # Reconstruct from server session
            dashboard_context = {
                'crop': {
                    'name': session.get('recommended_crop') or session.get('crop_result'),
                    'district': session.get('selected_district'),
                    'season': session.get('selected_season'),
                    'weather': session.get('crop_weather'),
                    'advice': session.get('crop_advice')
                },
                'price': {
                    'crop': session.get('price_crop'),
                    'district': session.get('price_district'),
                    'price': session.get('predicted_price') or session.get('price_result'),
                    'forecastText': session.get('price_forecast')
                },
                'disease': {
                    'disease': session.get('predicted_disease') or session.get('disease_result'),
                    'confidence': session.get('disease_confidence'),
                    'crop': session.get('disease_crop')
                },
                'irrigation': {
                    'crop': session.get('irrigation_crop'),
                    'advice': session.get('irrigation_result') or session.get('irrigation_result_en'),
                    'stage': session.get('irrigation_stage'),
                    'method': session.get('irrigation_method')
                },
                'planner': {
                    'summary': session.get('planner_summary'),
                    'alerts': session.get('planner_alerts'),
                    'priority': session.get('planner_priority')
                }
            }

        if agri_llm:
            res = agri_llm.ask_agronomist_rag(
                query=query,
                chat_history=history,
                lang=lang,
                dashboard_context=dashboard_context
            )
            return jsonify({
                "status": "success",
                "reply": res.get("answer", ""),
                "sources": res.get("sources", []),
                "provider": res.get("provider", "SmartAgri LLM"),
                "has_rag": res.get("has_rag_context", False)
            })
        else:
            return jsonify({
                "status": "success",
                "reply": "Agri LLM service is loading. Please try again in a moment.",
                "sources": [],
                "provider": "Loading"
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/explain_prediction', methods=['POST'])
def api_explain_prediction():
    """
    Generates tailored agronomist LLM explanations for ML model outputs.
    """
    try:
        data = request.get_json(silent=True) or request.form
        exp_type = data.get('type', 'crop') # 'crop', 'disease', 'price'
        lang = data.get('lang', 'en')

        if not agri_llm:
            return jsonify({"explanation": "LLM Service unavailable."})

        if exp_type == 'crop':
            crop = data.get('crop', 'Rice')
            n = float(data.get('N', 80))
            p = float(data.get('P', 40))
            k = float(data.get('K', 40))
            temp = float(data.get('temperature', 26))
            humidity = float(data.get('humidity', 70))
            ph = float(data.get('ph', 6.5))
            rainfall = float(data.get('rainfall', 150))
            
            explanation = agri_llm.explain_crop_recommendation(
                crop=crop, n=n, p=p, k=k, temp=temp, humidity=humidity, ph=ph, rainfall=rainfall, lang=lang
            )
            return jsonify({"status": "success", "explanation": explanation})

        elif exp_type == 'disease':
            disease_name = data.get('disease', 'Tomato Early Blight')
            confidence = float(data.get('confidence', 0.95))
            
            explanation = agri_llm.explain_disease_diagnosis(
                disease_name=disease_name, confidence=confidence, lang=lang
            )
            return jsonify({"status": "success", "explanation": explanation})

        return jsonify({"status": "error", "message": "Unknown explanation type"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/planner_ai', methods=['POST'])
def api_planner_ai():
    """
    AI-powered holistic Farm Planning synthesizing Weather, ML models, and RAG.
    """
    try:
        data = request.get_json(silent=True) or request.form
        crop = data.get('crop') or session.get('recommended_crop') or 'Rice'
        disease = data.get('disease') or session.get('predicted_disease')
        price = data.get('price') or session.get('predicted_price')
        district = data.get('district') or session.get('city') or 'Dharwad'
        lang = data.get('lang', 'en')
        irri_info = session.get('irrigation_data')

        temp, humidity, weather_desc = 28.0, 55.0, "clear sky"
        try:
            temp_f, hum_f, w_desc = get_weather(district)
            temp = float(temp_f) if temp_f is not None else 28.0
            humidity = float(hum_f) if hum_f is not None else 55.0
            weather_desc = w_desc or "clear sky"
        except Exception:
            pass

        if agri_llm:
            soil_val = data.get('soil_type') or session.get('irrigation_soil') or (irri_info.get('soil_type') if irri_info else 'loam')
            res = agri_llm.generate_planner_agent_strategy(
                crop=crop,
                disease=disease,
                price=str(price) if price else None,
                district=district,
                irrigation_data=irri_info,
                weather_data={'temp': temp, 'humidity': humidity, 'desc': weather_desc},
                soil_type=soil_val,
                lang=lang
            )
            return jsonify({
                "status": "success",
                "ai_plan": res.get("ai_plan", ""),
                "ai_plan_en": res.get("ai_plan_en", res.get("ai_plan", "")),
                "ai_plan_kn": res.get("ai_plan_kn", res.get("ai_plan", "")),
                "ai_plan_hi": res.get("ai_plan_hi", res.get("ai_plan", "")),
                "sources": res.get("sources", []),
                "provider": res.get("provider", "SmartAgri AI Engine")
            })
        else:
            return jsonify({"status": "error", "message": "LLM Service offline"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/predict_irrigation', methods=['POST'])
def api_predict_irrigation():
    try:
        data = request.get_json(silent=True) or request.form
        crop = data.get('crop', '') or session.get('recommended_crop') or 'Tomato'
        growth_stage = data.get('growth_stage', 'vegetative')
        soil_type = data.get('soil_type', 'loam')
        area_acres = data.get('area_acres', '1.0')
        irrigation_type = data.get('irrigation_type', 'drip')
        district = data.get('district', '') or session.get('selected_district') or session.get('city') or 'Dharwad'
        lang = data.get('lang', 'en')

        pump_flow_rate = data.get('pump_flow_rate')

        temp, humidity, weather_desc = 28.0, 55.0, "clear sky"
        rainfall_mm = 0.0
        try:
            temp_f, hum_f, w_desc = get_weather(district)
            temp = float(temp_f) if temp_f is not None else 28.0
            humidity = float(hum_f) if hum_f is not None else 55.0
            weather_desc = w_desc or "clear sky"
            if 'rain' in weather_desc.lower():
                rainfall_mm = 8.0
        except Exception:
            pass

        irri_data = translations.calculate_smart_irrigation(
            crop=crop,
            growth_stage=growth_stage,
            soil_type=soil_type,
            area_acres=area_acres,
            irrigation_type=irrigation_type,
            temp=temp,
            humidity=humidity,
            rainfall_mm=rainfall_mm,
            weather_desc=weather_desc,
            district=district,
            pump_flow_rate=pump_flow_rate,
            lang=lang
        )
        return jsonify({"status": "success", "data": irri_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ==========================================
# Decision Intelligence & Simulation Endpoints
# ==========================================

@app.route('/api/decision_intelligence/digital_twin', methods=['POST'])
def api_digital_twin():
    """
    Real-time dynamic Digital Twin simulator for crops: soil moisture balance,
    thermal/water stress indices, disease risk, and yield/profit impact.
    """
    try:
        data = request.get_json(silent=True) or request.form
        crop = data.get('crop') or session.get('recommended_crop') or 'Rice'
        rainfall_delta = float(data.get('rainfall_delta_pct', 0.0))
        sowing_shift = int(data.get('sowing_shift_days', 0))
        fertilizer_pct = float(data.get('fertilizer_pct', 100.0))
        irrigation_freq = int(data.get('irrigation_frequency_days', 7))
        district = data.get('district') or session.get('city') or 'Dharwad'

        temp, humidity = 28.0, 60.0
        try:
            temp_f, hum_f, _ = get_weather(district)
            temp = float(temp_f) if temp_f is not None else 28.0
            humidity = float(hum_f) if hum_f is not None else 60.0
        except Exception:
            pass

        if digital_twin_engine:
            result = digital_twin_engine.simulate(
                crop=crop,
                rainfall_delta_pct=rainfall_delta,
                sowing_shift_days=sowing_shift,
                fertilizer_pct=fertilizer_pct,
                irrigation_frequency_days=irrigation_freq,
                temp_c=temp,
                humidity_pct=humidity
            )
            return jsonify({'status': 'success', 'data': result})
        else:
            return jsonify({'status': 'error', 'message': 'Digital Twin engine offline'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/decision_intelligence/counterfactual', methods=['POST'])
def api_counterfactual():
    """
    Retrospective Causal AI: evaluates Pearl's Structural Causal Models for 'What if I had done X?' queries.
    """
    try:
        data = request.get_json(silent=True) or request.form
        query = (data.get('query') or '').strip()
        raw_crop = data.get('crop') or session.get('recommended_crop') or 'Tomato'
        from models.agri_calendar_service import normalize_crop_name
        crop = normalize_crop_name(raw_crop) or raw_crop
        disease = data.get('disease') or session.get('predicted_disease') or ''
        district = data.get('district') or session.get('city') or 'Dharwad'
        lang = data.get('lang') or session.get('lang', 'en')

        if not query:
            return jsonify({'status': 'error', 'message': 'No counterfactual query provided'}), 400

        if counterfactual_causal_engine:
            result = counterfactual_causal_engine.evaluate_query(
                query=query,
                crop=crop,
                disease=disease,
                district=district,
                lang=lang
            )
            return jsonify(result)
        else:
            return jsonify({'status': 'error', 'message': 'Counterfactual Causal engine offline'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/decision_intelligence/multi_agent_debate', methods=['POST'])
def api_multi_agent_debate():
    """
    4-Agent Consultation Debate: Agronomist, Market Economist, Pathologist, and Risk Officer.
    """
    try:
        data = request.get_json(silent=True) or request.form
        raw_crop = data.get('crop') or session.get('recommended_crop') or 'Tomato'
        from models.agri_calendar_service import normalize_crop_name
        crop = normalize_crop_name(raw_crop) or raw_crop
        district = data.get('district') or session.get('city') or 'Dharwad'
        disease = data.get('disease') or session.get('predicted_disease') or ''
        price_info = data.get('price_info') or str(session.get('predicted_price') or '')
        farmer_budget = data.get('farmer_budget', 'moderate')
        lang = data.get('lang') or session.get('lang', 'en')

        if multi_agent_debate_engine:
            result = multi_agent_debate_engine.conduct_debate(
                crop=crop,
                district=district,
                disease=disease,
                price_info=price_info,
                farmer_budget=farmer_budget,
                lang=lang
            )
            return jsonify(result)
        else:
            return jsonify({'status': 'error', 'message': 'Multi-Agent Debate engine offline'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/decision_intelligence/regret_plans', methods=['POST'])
def api_regret_plans():
    """
    Savage Minimax Regret & Downside Risk Adaptive Planning (Safe, Balanced, Aggressive).
    """
    try:
        data = request.get_json(silent=True) or request.form
        raw_crop = data.get('crop') or session.get('recommended_crop') or 'Rice'
        from models.agri_calendar_service import normalize_crop_name
        crop = normalize_crop_name(raw_crop) or raw_crop
        risk_preference = data.get('risk_preference', 'balanced')
        lang = data.get('lang') or session.get('lang', 'en')

        if regret_minimization_engine:
            result = regret_minimization_engine.get_plans(
                crop=crop,
                risk_preference=risk_preference,
                lang=lang
            )
            return jsonify(result)
        else:
            return jsonify({'status': 'error', 'message': 'Regret Minimization engine offline'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/ask_my_farm', methods=['POST'])
def api_ask_my_farm():
    """
    "Ask My Farm" Visual Multi-Agent Copilot Endpoint.
    Orchestrates Perception, Soil, Weather, Irrigation, RAG, Market, and Reasoning agents.
    """
    try:
        # Check if form data or JSON
        data = request.form or {}
        json_data = request.get_json(silent=True) or {}

        query = data.get('query') or json_data.get('query') or "Identify this plant and answer my query"
        crop_hint = data.get('crop') if data.get('crop') is not None else (json_data.get('crop') or '')
        raw_dist = data.get('district') or json_data.get('district') or session.get('selected_district') or session.get('city') or ''
        district = raw_dist.strip() if raw_dist else None
        lang = data.get('lang') or json_data.get('lang') or 'en'
        
        # Sensor data overrides
        sensor_override = {}
        if 'sensor_data' in data:
            try:
                sensor_override = json.loads(data['sensor_data'])
            except Exception:
                pass
        elif 'sensor_data' in json_data:
            sensor_override = json_data['sensor_data']

        # Extract image bytes if uploaded
        image_bytes = None
        image_b64 = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                image_bytes = file.read()
        elif 'image_b64' in json_data:
            image_b64 = json_data['image_b64']
        elif 'image' in json_data:
            image_b64 = json_data['image']
        elif 'image_b64' in data:
            image_b64 = data['image_b64']
        elif 'image' in data:
            image_b64 = data['image']

        if visual_copilot_engine:
            result = visual_copilot_engine.run_ask_my_farm(
                farmer_query=query,
                image_bytes=image_bytes,
                image_b64=image_b64,
                crop_hint=crop_hint,
                district=district,
                sensor_override=sensor_override,
                lang=lang
            )
            # Store in session for persistence
            session['ask_my_farm_last_result'] = result
            return jsonify(result)
        else:
            return jsonify({'status': 'error', 'message': 'Visual Copilot Engine offline'}), 500
    except Exception as e:
        print(f"Error in /api/ask_my_farm: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ===============================
# Text-to-Speech (TTS) Multilingual Engine (Kannada, Hindi, English)
# ===============================
_tts_cache = {}
_MAX_TTS_CACHE_ENTRIES = 200

def sanitize_tts_text(text: str) -> str:
    if not text:
        return ""
    # Strip URLs, bracket citations, markdown headers, bolding, bullet icons, emojis
    t = re.sub(r'https?://\S+', '', str(text))
    t = re.sub(r'\[ICAR.*?\]|\[.*?\]|\(.*?Document.*?\)', '', t, flags=re.IGNORECASE)
    t = re.sub(r'Document \d+.*?:', '', t, flags=re.IGNORECASE)
    t = re.sub(r'[*#_`~>•→|]', ' ', t)
    # Strip emojis and supplementary symbol characters
    t = re.sub(r'[\U00010000-\U0010ffff]', ' ', t)
    t = re.sub(r'[🌱🌾🌿🍃🩺💰💧🤖🔬🔴🎤🔊⏹💡🚨⚠✨🛒🇮🇳🇬🇧]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

@app.route('/api/tts', methods=['GET', 'POST'])
def api_tts():
    """
    Multilingual Text-to-Speech endpoint supporting Kannada (kn), Hindi (hi), and English (en).
    Generates high-clarity voice audio (MP3) for farmers with in-memory caching.
    """
    try:
        if request.method == 'POST':
            data = request.get_json(silent=True) or request.form
            raw_text = (data.get('text') or data.get('query') or '').strip()
            lang = data.get('lang', 'en')
        else:
            raw_text = (request.args.get('text') or request.args.get('query') or '').strip()
            lang = request.args.get('lang', 'en')

        lang = (lang or 'en').lower().strip()
        if 'kn' in lang:
            target_lang = 'kn'
        elif 'hi' in lang:
            target_lang = 'hi'
        else:
            target_lang = 'en'

        clean_text = sanitize_tts_text(raw_text)
        if not clean_text:
            return jsonify({"error": "No text provided for speech synthesis"}), 400

        # Limit text length to prevent heavy compute overhead (1500 chars is ~2-3 minutes of speech)
        if len(clean_text) > 1500:
            clean_text = clean_text[:1500]

        cache_key = hashlib.md5(f"{target_lang}:{clean_text}".encode('utf-8')).hexdigest()
        if cache_key in _tts_cache:
            audio_bytes = _tts_cache[cache_key]
        else:
            tts = gTTS(text=clean_text, lang=target_lang, slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            audio_bytes = fp.read()

            if len(_tts_cache) >= _MAX_TTS_CACHE_ENTRIES:
                _tts_cache.pop(next(iter(_tts_cache)))
            _tts_cache[cache_key] = audio_bytes

        from flask import Response
        return send_file(
            io.BytesIO(audio_bytes),
            mimetype="audio/mpeg",
            as_attachment=False,
            download_name="speech.mp3"
        )
    except Exception as e:
        print(f"TTS generation error: {e}")
        return jsonify({"error": str(e)}), 500

# ===============================
# Run Application
# ===============================
if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode)

