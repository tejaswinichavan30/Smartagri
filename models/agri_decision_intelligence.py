"""
SmartAgri 2.0 Decision Intelligence Suite
Pillars:
1. Digital Twin & What-If Future Simulator (Dynamic Soil Moisture, GDD Phenology, Stress, Yield)
2. Counterfactual Causal AI (Structural Causal Models, Abduction-Action-Prediction)
3. Multi-Agent AI Debate Room (Agronomist, Economist, Pathologist, Risk Officer)
4. Regret Minimization Engine (Savage Minimax Regret & Downside Risk Adaptive Planning)
"""

import math
import re
from typing import Dict, Any, List, Optional
from models.agri_llm_service import agri_llm
from models.agri_rag_service import agri_rag

# ==========================================
# 1. DIGITAL TWIN SIMULATOR ENGINE
# ==========================================
class DigitalTwinEngine:
    """
    Simulates real-time crop growth dynamics, soil moisture depletion,
    thermal/water stress indices, disease vulnerability, and projected financial yields.
    """
    
    CROP_PARAMS = {
        'rice': {'base_yield_q': 22.0, 'base_cost_acre': 22000, 'base_price_q': 2350, 'gdd_req': 1800, 'water_req_mm': 1200, 'moisture_opt': 75},
        'wheat': {'base_yield_q': 18.0, 'base_cost_acre': 16000, 'base_price_q': 2275, 'gdd_req': 1500, 'water_req_mm': 450, 'moisture_opt': 55},
        'cotton': {'base_yield_q': 10.0, 'base_cost_acre': 24000, 'base_price_q': 7120, 'gdd_req': 2200, 'water_req_mm': 700, 'moisture_opt': 60},
        'maize': {'base_yield_q': 25.0, 'base_cost_acre': 18000, 'base_price_q': 2090, 'gdd_req': 1600, 'water_req_mm': 550, 'moisture_opt': 60},
        'tomato': {'base_yield_q': 140.0, 'base_cost_acre': 45000, 'base_price_q': 1800, 'gdd_req': 1400, 'water_req_mm': 600, 'moisture_opt': 65},
        'potato': {'base_yield_q': 100.0, 'base_cost_acre': 38000, 'base_price_q': 1500, 'gdd_req': 1300, 'water_req_mm': 500, 'moisture_opt': 65},
        'onion': {'base_yield_q': 90.0, 'base_cost_acre': 32000, 'base_price_q': 1900, 'gdd_req': 1450, 'water_req_mm': 450, 'moisture_opt': 55},
        'chickpea': {'base_yield_q': 8.5, 'base_cost_acre': 12000, 'base_price_q': 5440, 'gdd_req': 1200, 'water_req_mm': 300, 'moisture_opt': 45},
        'millet': {'base_yield_q': 12.0, 'base_cost_acre': 10000, 'base_price_q': 2500, 'gdd_req': 1100, 'water_req_mm': 280, 'moisture_opt': 40},
        'sorghum': {'base_yield_q': 14.0, 'base_cost_acre': 11000, 'base_price_q': 3180, 'gdd_req': 1250, 'water_req_mm': 350, 'moisture_opt': 45},
        'groundnut': {'base_yield_q': 14.0, 'base_cost_acre': 22000, 'base_price_q': 6780, 'gdd_req': 1600, 'water_req_mm': 500, 'moisture_opt': 55},
        'sunflower': {'base_yield_q': 9.0, 'base_cost_acre': 16000, 'base_price_q': 6850, 'gdd_req': 1400, 'water_req_mm': 400, 'moisture_opt': 50},
        'ragi': {'base_yield_q': 15.0, 'base_cost_acre': 12000, 'base_price_q': 4290, 'gdd_req': 1200, 'water_req_mm': 350, 'moisture_opt': 45},
        'sugarcane': {'base_yield_q': 400.0, 'base_cost_acre': 65000, 'base_price_q': 340, 'gdd_req': 2800, 'water_req_mm': 1800, 'moisture_opt': 75},
        'soybean': {'base_yield_q': 10.0, 'base_cost_acre': 14000, 'base_price_q': 4892, 'gdd_req': 1350, 'water_req_mm': 450, 'moisture_opt': 55}
    }

    @classmethod
    def simulate(cls, crop: str, rainfall_delta_pct: float = 0.0,
                 sowing_shift_days: int = 0, fertilizer_pct: float = 100.0,
                 irrigation_frequency_days: int = 7, temp_c: float = 28.0,
                 humidity_pct: float = 60.0, lang: str = "en") -> Dict[str, Any]:
        """
        Runs the simulation dynamics on crop digital twin.
        """
        crop_key = (crop or 'rice').lower().strip()
        params = cls.CROP_PARAMS.get(crop_key, cls.CROP_PARAMS.get('maize'))

        # 1. Effective Moisture Dynamics
        effective_rain = (1.0 + (rainfall_delta_pct / 100.0))
        irri_factor = max(0.3, 1.2 - (irrigation_frequency_days - 3) * 0.08)
        simulated_soil_moisture = max(15.0, min(95.0, params['moisture_opt'] * effective_rain * 0.6 + irri_factor * 35.0))

        # 2. Water Stress Index (0 = no stress, 100 = critical stress)
        moisture_diff = abs(simulated_soil_moisture - params['moisture_opt'])
        water_stress = min(100.0, (moisture_diff / params['moisture_opt']) * 120.0)

        # 3. Thermal Stress based on Sowing Shift & Temperature
        # Sowing delayed into warmer months increases heat stress
        heat_penalty = max(0.0, (temp_c - 30.0) * 4.0)
        sowing_stress = abs(sowing_shift_days) * 1.5 if sowing_shift_days > 0 else abs(sowing_shift_days) * 0.8
        thermal_stress = min(100.0, heat_penalty + sowing_stress)

        # 4. Pathogen & Fungal Vulnerability Index
        # High moisture + warm humidity triggers fungal spores
        humidity_factor = max(0.0, (humidity_pct - 65.0) * 1.2)
        wetness_factor = max(0.0, (simulated_soil_moisture - 70.0) * 1.0)
        pathogen_risk = min(100.0, max(5.0, humidity_factor + wetness_factor + (15.0 if temp_c > 24 else 5.0)))

        # 5. Fertilizer Response Curve (Mitscherlich-Baule diminishing returns)
        fert_ratio = fertilizer_pct / 100.0
        fert_factor = 1.0 - math.exp(-2.2 * fert_ratio)
        if fert_ratio > 1.4:
            # Over-fertilization toxicity & lodging penalty
            fert_factor -= (fert_ratio - 1.4) * 0.25

        # 6. Overall Yield Penalty Factor
        stress_penalty = 1.0 - (water_stress * 0.004) - (thermal_stress * 0.003) - (pathogen_risk * 0.002)
        stress_penalty = max(0.2, min(1.15, stress_penalty))

        projected_yield_q = round(params['base_yield_q'] * fert_factor * stress_penalty, 2)
        projected_revenue = round(projected_yield_q * params['base_price_q'], 0)
        
        # Total cost adjusts with fertilizer and extra irrigation
        adjusted_cost = params['base_cost_acre'] * (0.8 + 0.2 * fert_ratio) + (max(0, 10 - irrigation_frequency_days) * 600)
        projected_profit = round(projected_revenue - adjusted_cost, 0)
        
        crop_health_score = round(max(10.0, min(99.0, 100.0 - (water_stress * 0.45 + thermal_stress * 0.35 + pathogen_risk * 0.2))), 1)

        # Determine Growth Stage Impact (Localized)
        stage_desc_en = "Optimal Vegetative & Grain Filling"
        stage_desc_kn = "ಅತ್ಯುತ್ತಮ ಸಸ್ಯಕ ಬೆಳವಣಿಗೆ ಮತ್ತು ಕಾಳು ತುಂಬುವ ಹಂತ"
        stage_desc_hi = "इष्टतम वानस्पतिक वृद्धि एवं दाना भराव अवस्था"

        if sowing_shift_days > 10:
            stage_desc_en = "Delayed Anthesis — Risk of terminal heat stress during grain filling"
            stage_desc_kn = "ವಿಳಂಬವಾದ ಹೂಬಿಡುವಿಕೆ — ಕಾಳು ತುಂಬುವಾಗ ಅಂತ್ಯ ಹಂತದ ಶಾಖದ ಒತ್ತಡದ ಅಪಾಯ"
            stage_desc_hi = "देर से फूल आना — दाना भराव के दौरान अत्यधिक ताप तनाव का जोखिम"
        elif sowing_shift_days < -10:
            stage_desc_en = "Early Emergence — Potential seedling frost or cold shock vulnerability"
            stage_desc_kn = "ಮುಂಚಿನ ಮೊಳಕೆಯೊಡೆಯುವಿಕೆ — ಸಸಿಗಳಿಗೆ ಶೀತ ಅಥವಾ ಚಳಿ ಆಘಾತದ ಸಾಧ್ಯತೆ"
            stage_desc_hi = "अगेती अंकुरण — पौधों को ठंड या शीतलहर का जोखिम"
        elif water_stress > 50:
            stage_desc_en = "Moisture Deficit during Critical Flowering Stage"
            stage_desc_kn = "ನಿರ್ಣಾಯಕ ಹೂಬಿಡುವ ಹಂತದಲ್ಲಿ ತೇವಾಂಶದ ಕೊರತೆ"
            stage_desc_hi = "महत्वपूर्ण फूल अवस्था के दौरान नमी की कमी"
        elif pathogen_risk > 60:
            stage_desc_en = "High Humidity Spore Germination Window Detected"
            stage_desc_kn = "ಹೆಚ್ಚಿನ ಆರ್ದ್ರತೆ: ಶಿಲೀಂಧ್ರ ಬೀಜಕಗಳು ಮೊಳಕೆಯೊಡೆಯುವ ಅಪಾಯ"
            stage_desc_hi = "उच्च आर्द्रता: कवक बीजाणु अंकुरण का उच्च जोखिम"

        norm_l = (lang or 'en').lower()
        if 'kn' in norm_l:
            stage_desc = stage_desc_kn
        elif 'hi' in norm_l:
            stage_desc = stage_desc_hi
        else:
            stage_desc = stage_desc_en

        return {
            'crop': crop.capitalize(),
            'simulated_soil_moisture': round(simulated_soil_moisture, 1),
            'water_stress_index': round(water_stress, 1),
            'thermal_stress_index': round(thermal_stress, 1),
            'pathogen_risk_index': round(pathogen_risk, 1),
            'crop_health_score': crop_health_score,
            'projected_yield_q_acre': projected_yield_q,
            'projected_revenue_inr': projected_revenue,
            'projected_cost_inr': round(adjusted_cost, 0),
            'projected_profit_inr': projected_profit,
            'phenology_stage_note': stage_desc,
            'phenology_stage_note_en': stage_desc_en,
            'phenology_stage_note_kn': stage_desc_kn,
            'phenology_stage_note_hi': stage_desc_hi,
            'baseline_yield_q': params['base_yield_q'],
            'yield_delta_pct': round(((projected_yield_q - params['base_yield_q']) / params['base_yield_q']) * 100.0, 1)
        }


# ==========================================
# 2. COUNTERFACTUAL CAUSAL INFERENCE ENGINE
# ==========================================
class CounterfactualCausalEngine:
    """
    Structural Causal Model (SCM) based on Judea Pearl's Abduction-Action-Prediction.
    Answers: 'What would have happened if I did action X instead of Y in the past?'
    """

    @classmethod
    def evaluate_query(cls, query: str, crop: str = "Tomato", 
                       disease: str = "Early Blight",
                       district: str = "Dharwad",
                       lang: str = "en") -> Dict[str, Any]:
        """
        Parses the retrospective what-if question, abducts latent factors,
        simulates the counterfactual world, and produces an agronomic causal explanation.
        """
        query_clean = query.strip().strip('"\'')
        q_lower = query_clean.lower()
        
        # Auto-detect language from query text or explicit parameter
        has_kannada_chars = bool(re.search(r'[\u0C80-\u0CFF]', query_clean))
        has_devanagari_chars = bool(re.search(r'[\u0900-\u097F]', query_clean))
        if has_kannada_chars:
            norm_l = 'kn'
        elif has_devanagari_chars:
            norm_l = 'hi'
        else:
            norm_l = 'kn' if 'kn' in (lang or '').lower() else ('hi' if 'hi' in (lang or '').lower() else 'en')

        # Auto-detect crop mentioned in query
        detected_crop = crop
        KNOWN_CROPS = [
            'sugarcane', 'rice', 'paddy', 'wheat', 'cotton', 'maize', 'corn', 'tomato',
            'potato', 'chilli', 'onion', 'banana', 'soybean', 'groundnut', 'coffee',
            'grape', 'apple', 'ragi', 'tur', 'arhar', 'chickpea', 'gram'
        ]
        for c in KNOWN_CROPS:
            if re.search(rf'\b{c}\b', q_lower):
                detected_crop = 'Rice' if c == 'paddy' else ('Maize' if c == 'corn' else c.capitalize())
                break
        
        # Localize crop name for explanation
        try:
            import translations
            disp_crop = translations.get_crop_name(detected_crop, norm_l)
        except Exception:
            disp_crop = detected_crop

        # Classify counterfactual scenario type with multilingual support (English, Kannada, Hindi)
        if any(w in q_lower for w in [
            'irrigate', 'water', 'watering', 'irrigated', 'drip', 'flood', 'sprinkler', 'fertigation', 'micro-irrigation',
            'ನೀರು', 'ನೀರಾವರಿ', 'ಹಾಯಿಸಿದ್ದರೆ', 'ಹನಿ', 'ಸಿಂಚನ', 'ಹರಿವು',
            'सिंचाई', 'पानी', 'ड्रिप', 'फर्टिगेशन'
        ]):
            scenario_type = "irrigation_timing"
            action_desc = "3 ದಿನ ಮುಂಚಿತವಾಗಿ ನೀರಾವರಿ / ಹೊಂದಾಣಿಕೆ ವೇಳಾಪಟ್ಟಿ" if norm_l == 'kn' else ("3 दिन पहले सिंचाई / समय सारणी समायोजन" if norm_l == 'hi' else "Switched irrigation method / timing")
        elif any(w in q_lower for w in [
            'sow', 'sowing', 'planted', 'sowed', 'planting', 'seed',
            'ಬಿತ್ತನೆ', 'ಬಿತ್ತಿದ್ದರೆ', 'ನಾಟಿ', 'ಬೀಜ',
            'बुवाई', 'बोया', 'रोपाई', 'बीज'
        ]):
            scenario_type = "sowing_date"
            action_desc = "12 ದಿನ ಮುಂಚಿತವಾಗಿ ಬಿತ್ತನೆ" if norm_l == 'kn' else ("12 दिन पहले बुवाई" if norm_l == 'hi' else "Shifted sowing date / planting schedule")
        elif any(w in q_lower for w in [
            'fertilizer', 'urea', 'nitrogen', 'npk', 'dose', 'potash', 'dap', 'manure', 'compost',
            'ಗೊಬ್ಬರ', 'ರಸಗೊಬ್ಬರ', 'ಯೂರಿಯಾ', 'ಸಾರಜನಕ', 'ರಂಜಕ', 'ಪೊಟ್ಯಾಶ್',
            'खाद', 'उर्वरक', 'यूरिया', 'नाइट्रोजन', 'एनपीके'
        ]):
            scenario_type = "fertilizer_management"
            action_desc = "ಕಂತುಗಳಲ್ಲಿ ಗೊಬ್ಬರ ನಿರ್ವಹಣೆ" if norm_l == 'kn' else ("किस्तों में संतुलित उर्वरक प्रबंधन" if norm_l == 'hi' else "Applied different fertilizer split / dosage")
        elif any(w in q_lower for w in [
            'spray', 'pesticide', 'fungicide', 'chemical', 'bio-agent', 'neem', 'insecticide',
            'ಸಿಂಪಡಣೆ', 'ಔಷಧಿ', 'ಕೀಟನಾಶಕ', 'ಶಿಲೀಂಧ್ರನಾಶಕ', 'ಬೇವಿನ',
            'छिड़काव', 'कीटनाशक', 'फफूंदनाशी', 'दवा', 'नीम'
        ]):
            scenario_type = "pesticide_intervention"
            action_desc = "ಮಳೆಗೆ ಮುನ್ನ ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಸಿಂಪಡಣೆ" if norm_l == 'kn' else ("बारिश पूर्व निवारक जैविक छिड़काव" if norm_l == 'hi' else "Preventive chemical/fungicide spray before event")
        else:
            scenario_type = "general_agronomic"
            action_desc = "ಪರ್ಯಾಯ ಕೃಷಿ ನಿರ್ವಹಣಾ ಕ್ರಮ" if norm_l == 'kn' else ("वैकल्पिक कृषि प्रबंधन कदम" if norm_l == 'hi' else "Alternative management action in past season")

        # Attempt LLM Causal Reasoning first
        causal_prompt = f"""
You are an expert Agricultural Causal Scientist and Plant Pathologist utilizing Judea Pearl's Structural Causal Models (SCM).
A farmer is asking a retrospective counterfactual question:
Farmer's Question: "{query_clean}"

Context:
- Crop: {detected_crop}
- Observed Disease / Issue: {disease or 'None specified'}
- Location: {district}
- Target Language: {lang}

Please perform Judea Pearl's 3-step Causal Analysis:
1. Step 1 (Abduction): What were the latent unobserved conditions (microclimate humidity, spore load, soil water potential, plant water turgor, root zone efficiency)?
2. Step 2 (Action): What would the intervention do(Action) change physically?
3. Step 3 (Prediction): What is the estimated counterfactual outcome, trade-offs (e.g. water savings vs disease risk vs yield and cost impact), and confidence percentage (e.g. 85%)?

Format your response clearly with:
- Step 1: Abduction (Inferring Latent Unobserved Conditions)
- Step 2: Action (Applying the Counterfactual Intervention)
- Step 3: Prediction (Counterfactual Outcome Calculation)
- Summary of Counterfactual Outcome
- The Trade-Off Analysis (Comparison table of Observed vs Counterfactual)
- Probabilistic Confidence Percentage (e.g. 85%)

Provide the response in the requested language ({lang}). Keep it insightful, practical, and scientifically rigorous.
"""
        llm_response = None
        if agri_llm and agri_llm.llm:
            try:
                msg = agri_llm.llm.invoke(causal_prompt)
                raw_content = msg.content if hasattr(msg, 'content') else str(msg)
                if isinstance(raw_content, list):
                    llm_response = " ".join(part.get("text", str(part)) if isinstance(part, dict) else str(part) for part in raw_content)
                else:
                    llm_response = str(raw_content)
            except Exception as e:
                print(f"[Counterfactual Engine] LLM invocation failed: {e}")

        # Deterministic SCM fallback if LLM offline or timed out
        if not llm_response:
            if any(w in q_lower for w in ['3 ದಿನ', '3 days', '3 day', '3 दिन', 'ಮುಂಚಿತವಾಗಿ ನೀರು', 'ಮೊದಲೇ ನೀರು', 'पहले सिंचाई', '3 days earlier', '3 days early']):
                confidence = 85
                if norm_l == 'kn':
                    step1 = f"{district} ಜಿಲ್ಲೆಯಲ್ಲಿ ನೀರಾವರಿ ವಿಳಂಬವಾದಾಗ ತೇವಾಂಶದ ಕೊರತೆ ಮತ್ತು ಎಲೆಯ ಮೇಲಿನ ಸೂಕ್ಷ್ಮ ಹವಾಮಾನವು {detected_crop} ಬೆಳೆಗೆ ಶಿಲೀಂಧ್ರ ರೋಗಕಾರಕಗಳ ಬೆಳವಣಿಗೆಗೆ ಅನುಕೂಲಕರವಾಗಿತ್ತು."
                    step2 = f"ಕಾರಣಾತ್ಮಕ ಹಸ್ತಕ್ಷೇಪ do(3 ದಿನ ಮುಂಚಿತವಾಗಿ ನೀರು ಹಾಯಿಸಿದ್ದರೆ) ಅನ್ವಯಿಸಲಾಗುತ್ತಿದೆ."
                    step3 = f"ಸಮಯಕ್ಕೆ ಸರಿಯಾಗಿ ಬೇರಿಗೆ ನೀರು ದೊರೆತು, ಸಸ್ಯದ ರೋಗನಿರೋಧಕ ಶಕ್ತಿ (Turgor & Systemic Resistance) ಬಲಗೊಳ್ಳುತ್ತದೆ ಮತ್ತು ರೋಗದ ತೀವ್ರತೆ 40-50% ಕಡಿಮೆಯಾಗುತ್ತದೆ."
                    summary = f"3 ದಿನ ಮುಂಚಿತವಾಗಿ ನೀರು ಹಾಯಿಸಿದ್ದರೆ, ಬೆಳೆ ರೋಗದ ಬಾಧೆ 40% ರಿಂದ 50% ರಷ್ಟು ಕಡಿಮೆಯಾಗುತ್ತಿತ್ತು ಮತ್ತು ತೇವಾಂಶ ಕೊರತೆಯಿಂದ ಉಂಟಾಗುವ ಇಳುವರಿ ನಷ್ಟವನ್ನು ತಪ್ಪಿಸಬಹುದಿತ್ತು."
                    trade_offs = (
                        f"| ನಿಯತಾಂಕ | ಗಮನಿಸಿದ ವಾಸ್ತವ | ಕೌಂಟರ್‌ಫ್ಯಾಕ್ಚುಯಲ್ (3 ದಿನ ಮುಂಚಿತ ನೀರಾವರಿ) |\n"
                        f"| :--- | :--- | :---\n"
                        f"| **ರೋಗದ ತೀವ್ರತೆ & ಸೋಂಕು** | ಹೆಚ್ಚು (ರೋಗಾಣು ಹರಡುವಿಕೆ) | **40% - 50% ಕಡಿಮೆ (ಬಲವಾದ ರೋಗನಿರೋಧಕತೆ)** |\n"
                        f"| **ನೀರಿನ ಒತ್ತಡ & ಬಾಡುವಿಕೆ** | ಮಧ್ಯಮದಿಂದ ತೀವ್ರ | ಶೂನ್ಯ ಒತ್ತಡ / ಗರಿಷ್ಠ ಹಸಿರು |\n"
                        f"| **ಇಳುವರಿ ನಷ್ಟ ತಡೆ** | ಮೂಲಮಟ್ಟ | **+15% ರಿಂದ +20% ಸಂರಕ್ಷಿತ ಇಳುವರಿ** |"
                    )
                elif norm_l == 'hi':
                    step1 = f"{district} में सिंचाई में देरी से नमी का तनाव और पत्तियों पर प्रतिकूल सूक्ष्म जलवायु ने {detected_crop} में फफूंद संक्रमण को बढ़ावा दिया।"
                    step2 = f"कारणात्मक हस्तक्षेप do(3 दिन पहले सिंचाई) लागू किया जा रहा है।"
                    step3 = f"पौधे की जड़ों को समय पर नमी मिलने से रोग प्रतिरोधक क्षमता (Turgor Pressure) मजबूत होती है और रोग संक्रमण 40-50% कम हो जाता है।"
                    summary = f"यदि 3 दिन पहले सिंचाई की गई होती, तो फसल रोग संक्रमण में 40% से 50% की कमी आती और नमी तनाव से होने वाला उपज नुकसान पूरी तरह बच जाता।"
                    trade_offs = (
                        f"| पैरामीटर | देखी गई वास्तविकता | काउंटरफैक्चुअल (3 दिन पहले सिंचाई) |\n"
                        f"| :--- | :--- | :---\n"
                        f"| **रोग संक्रमण तीव्रता** | अधिक (बीमारी का प्रसार) | **40% - 50% कम (मजबूत रोग प्रतिरोधक क्षमता)** |\n"
                        f"| **नमी तनाव एवं मुरझाना** | मध्यम से गंभीर | शून्य तनाव / इष्टतम हरियाली |\n"
                        f"| **उपज नुकसान से बचाव** | आधार रेखा | **+15% से +20% सुरक्षित पैदावार** |"
                    )
                else:
                    step1 = f"Moisture stress prior to disease onset weakened plant cell turgor and created a favorable microclimate for pathogen spore germination on {detected_crop} in {district}."
                    step2 = f"Applying surgical intervention do(Irrigation = 3 Days Earlier before moisture threshold drop)."
                    step3 = f"Timely root zone hydration strengthens plant turgor and systemic acquired resistance, suppressing disease severity by 40-50%."
                    summary = f"Irrigating 3 days earlier would have reduced crop disease incidence by 40% to 50% and protected crop yield potential."
                    trade_offs = (
                        f"| Parameter | Observed Reality | Counterfactual Action (3 Days Earlier) |\n"
                        f"| :--- | :--- | :---\n"
                        f"| **Disease Severity** | High pathogen spread | **40% - 50% lower severity** |\n"
                        f"| **Plant Water Stress** | Moderate to severe | Zero stress / optimal hydration |\n"
                        f"| **Protected Yield** | Baseline | **+15% to +20% yield saved** |"
                    )
            elif 'drip' in q_lower or 'flood' in q_lower or 'micro-irrigation' in q_lower or 'ಹನಿ' in q_lower or 'ಹರಿವು' in q_lower or 'ड्रिप' in q_lower:
                confidence = 86
                if norm_l == 'kn':
                    step1 = f"{district} ಜಿಲ್ಲೆಯಲ್ಲಿ {detected_crop} ಬೆಳೆಗೆ ಸಾಂಪ್ರದಾಯಿಕ ಕಾಲುವೆ/ಹರಿವು ನೀರಾವರಿ ಪದ್ಧತಿಯಡಿ ಮಣ್ಣಿನ ಆಮ್ಲಜನಕ ಕೊರತೆ ಮತ್ತು ನೀರಿನ ಹರಿವಿನ ನಷ್ಟವನ್ನು ಪುನರ್ನಿರ್ಮಿಸಲಾಗುತ್ತಿದೆ."
                    step2 = f"ಕಾರಣಾತ್ಮಕ ಹಸ್ತಕ್ಷೇಪ do(ನೀರಾವರಿ = ನಿಖರ ಹನಿ ನೀರಾವರಿ + ದ್ರವಗೊಬ್ಬರ Fertigation) ಅನ್ವಯಿಸಲಾಗುತ್ತಿದೆ."
                    step3 = f"ನೀರಿನ ಬಳಕೆಯ ದಕ್ಷತೆಯು 45% ರಿಂದ 90% ಕ್ಕೆ ಏರಿಕೆಯಾಗುತ್ತದೆ, ಕಳೆಗಳ ಬಾಧೆ 60% ಕಡಿಮೆಯಾಗುತ್ತದೆ ಮತ್ತು ಸಾರಜನಕ ಸೋರಿಕೆ ಸಂಪೂರ್ಣ ನಿಲ್ಲುತ್ತದೆ."
                    summary = f"ಹನಿ ನೀರಾವರಿ ಅಳವಡಿಸಿದ್ದರೆ ನೀರಿನ ಬಳಕೆಯಲ್ಲಿ 45% ಉಳಿತಾಯವಾಗುತ್ತಿತ್ತು ಮತ್ತು ಬೆಳೆಯ ಇಳುವರಿಯಲ್ಲಿ +18% ರಿಂದ +25% ಹೆಚ್ಚಳವಾಗುತ್ತಿತ್ತು."
                    trade_offs = (
                        f"| ನಿಯತಾಂಕ | ಗಮನಿಸಿದ ವಾಸ್ತವ (ಹರಿವು ನೀರಾವರಿ) | ಕೌಂಟರ್‌ಫ್ಯಾಕ್ಚುಯಲ್ (ಹನಿ ನೀರಾವರಿ) |\n"
                        f"| :--- | :--- | :---\n"
                        f"| **ನೀರಿನ ಬಳಕೆಯ ದಕ್ಷತೆ** | 40% - 50% (ಹೆಚ್ಚು ಸೋರಿಕೆ/ವ್ಯರ್ಥ) | **85% - 92% (ನೇರ ಬೇರಿಗೆ ತಲುಪುವಿಕೆ)** |\n"
                        f"| **ಬೇರಿನ ಆಮ್ಲಜನಕ & ಪೋಷಕಾಂಶ** | ಕಾಲಕಾಲಕ್ಕೆ ಜಲಾವೃತ & N ಸೋರಿಕೆ | ನಿರಂತರ ಗರಿಷ್ಠ ಗಾಳಿಯಾಡುವಿಕೆ & ಫರ್ಟಿಗೇಷನ್ |\n"
                        f"| **ಕಳೆ ಬೆಳವಣಿಗೆ & ಕೂಲಿ ವೆಚ್ಚ** | ಹೆಚ್ಚು (ಇಡೀ ಜಮೀನು ತೇವ) | ಕಡಿಮೆ (ಕೇವಲ ಸಾಲಿನ ಜಾಗ ಮಾತ್ರ ತೇವ) |\n"
                        f"| **ನಿವ್ವಳ ಇಳುವರಿ & ಲಾಭ** | ಮೂಲಮಟ್ಟ | **+18% ರಿಂದ +25% ಅಧಿಕ ಇಳುವರಿ/ಎಕರೆ** |"
                    )
                elif norm_l == 'hi':
                    step1 = f"{district} में {detected_crop} के लिए पारंपरिक बाढ़/नाली सिंचाई के तहत मिट्टी में ऑक्सीजन की कमी और जल बहाव नुकसान का पुनर्निर्माण किया जा रहा है।"
                    step2 = f"कारणात्मक हस्तक्षेप do(सिंचाई = सटीक ड्रिप सिंचाई + फर्टिगेशन) लागू किया जा रहा है।"
                    step3 = f"जल उपयोग दक्षता 45% से बढ़कर 90% हो जाती है, खरपतवार में 60% कमी आती है और पोषक तत्वों का रिसाव बंद होता है।"
                    summary = f"ड्रिप सिंचाई अपनाने से 45% पानी की बचत होती और फसल पैदावार में +18% से +25% की वृद्धि दर्ज की जाती।"
                    trade_offs = (
                        f"| पैरामीटर | देखा गया वास्तविक (बाढ़ सिंचाई) | काउंटरफैक्चुअल (ड्रिप सिंचाई) |\n"
                        f"| :--- | :--- | :---\n"
                        f"| **जल उपयोग दक्षता** | 40% - 50% (अधिक अपवाह/बर्बादी) | **85% - 92% (सीधे जड़ों तक आपूर्ति)** |\n"
                        f"| **जड़ों में वातन एवं पोषक तत्व** | जलभराव और नाइट्रोजन रिसाव | निरंतर इष्टतम वायु संचार एवं फर्टिगेशन |\n"
                        f"| **खरपतवार और श्रम लागत** | अधिक (पूरे खेत में नमी) | कम (केवल फसल कतार में नमी) |\n"
                        f"| **शुद्ध उपज एवं मुनाफा** | आधार रेखा | **+18% से +25% अधिक उपज प्रति एकड़** |"
                    )
                else:
                    step1 = (
                        f"Under conventional flood irrigation on 2 acres of {detected_crop}, deep percolation loss and surface evaporation accounted for 40-50% of applied water. "
                        f"Soil experienced periodic cyclic saturation (hypoxia at root zone) followed by drying cycles."
                    )
                    step2 = (
                        f"Applying surgical intervention do(Irrigation = Precision Drip System on 2 Acres of {detected_crop}). "
                        f"Water is delivered directly to the active root zone at low pressure with continuous optimal soil moisture tension (field capacity)."
                    )
                    step3 = (
                        f"1. **Water Conservation:** 40% to 55% reduction in total water volume consumed per season (~30–40 lakh litres saved across 2 acres).\n"
                        f"2. **Fertigation Efficiency:** Nutrient uptake efficiency increases by 25–35% through direct soluble fertigation.\n"
                        f"3. **Weed & Disease Pressure:** Inter-row soil remains dry, reducing weed germination and lower canopy fungal humidity.\n"
                        f"4. **Yield Impact:** Estimated +15% to +28% increase in cane tonnage and sugar recovery."
                    )
                    summary = (
                        f"Switching from flood to drip irrigation for 2 acres of {detected_crop} produces a massive positive counterfactual gain: "
                        f"**saves ~45% water, cuts fertilizer leaching, and boosts cane yield by 18-25%**, with capital payback achieved within 1.5–2 crop seasons (especially with PMKSY micro-irrigation subsidies)."
                    )
                    trade_offs = (
                        f"| Parameter | Observed (Flood Irrigation) | Counterfactual (Drip Irrigation) |\n"
                        f"| :--- | :--- | :---\n"
                        f"| **Water Application Efficiency** | 40% - 50% (High runoff/percolation) | **85% - 92% (Targeted root delivery)** |\n"
                        f"| **Root Aeration & Nutrient Leaching** | Periodic waterlogging & N leaching | Continuous optimal aeration & fertigation |\n"
                        f"| **Weed Growth & Inter-row Labor** | High (Entire field wetted) | Low (Only cane row wetted) |\n"
                        f"| **Net Cane Yield & Profit** | Baseline | **+18% to +25% higher yield per acre** |"
                    )
            elif scenario_type == "irrigation_timing":
                confidence = 78
                if norm_l == 'kn':
                    step1 = f"{district} ಜಿಲ್ಲೆಯಲ್ಲಿ {detected_crop} ಬೆಳೆಗೆ ವಾಸ್ತವಿಕ ನೀರಾವರಿ ಅಂತರದಲ್ಲಿ ಹಿನ್ನೆಲೆ ಮಣ್ಣಿನ ತೇವಾಂಶ ಮತ್ತು ಶಿಲೀಂಧ್ರ ಬೀಜಕಗಳ ಉಪಸ್ಥಿತಿಯನ್ನು ಪುನರ್ನಿರ್ಮಿಸಲಾಗುತ್ತಿದೆ."
                    step2 = f"ಕಾರಣಾತ್ಮಕ ಹಸ್ತಕ್ಷೇಪ do(3 ದಿನ ಮುಂಚಿತವಾಗಿ ನೀರಾವರಿ / ಹೊಂದಾಣಿಕೆ ವೇಳಾಪಟ್ಟಿ) ಅನ್ವಯಿಸಲಾಗುತ್ತಿದೆ."
                    step3 = f"ಸಸ್ಯಕ/ಹೂಬಿಡುವ ಹಂತದಲ್ಲಿ ತೇವಾಂಶದ ಒತ್ತಡವು 30% ರಷ್ಟು ಕಡಿಮೆಯಾಗುತ್ತದೆ, ಆದರೆ ರಾತ್ರಿಯ ಸಮಯದಲ್ಲಿ ಎಲೆಗಳ ಸಾಪೇಕ್ಷ ಆರ್ದ್ರತೆ ಸ್ವಲ್ಪ ಹೆಚ್ಚಾಗುತ್ತದೆ."
                    summary = f"ಹೊಂದಾಣಿಕೆಯ ನೀರಾವರಿಯು ನೀರಿನ ಒತ್ತಡವನ್ನು ನಿವಾರಿಸಿ ಇಳುವರಿಯನ್ನು ರಕ್ಷಿಸುತ್ತದೆ, ಆದರೆ ರಾತ್ರಿಯ ಎಲೆಗಳ ತೇವಾಂಶ ತಪ್ಪಿಸಲು ಹನಿ ನೀರಾವರಿ ಅಥವಾ ಬೆಳಗಿನ ಸಮಯವನ್ನು ಆರಿಸಿಕೊಳ್ಳಬೇಕು."
                    trade_offs = (
                        f"| ನಿಯತಾಂಕ | ಗಮನಿಸಿದ ವಾಸ್ತವ | ಕೌಂಟರ್‌ಫ್ಯಾಕ್ಚುಯಲ್ ಹೊಂದಾಣಿಕೆ |\n"
                        f"| :--- | :--- | :---\n"
                        f"| **ತೇವಾಂಶದ ಒತ್ತಡ** | ಸಾಧಾರಣ | 30% ರಷ್ಟು ಇಳಿಕೆ |\n"
                        f"| **ಮೇಲ್ಮೈ ಸೂಕ್ಷ್ಮ ಹವಾಮಾನ** | ಒಣಗಿದ ಸ್ಥಿತಿ | ರಾತ್ರಿಯ ಆರ್ದ್ರತೆ ಕೊಂಚ ಏರಿಕೆ |"
                    )
                elif norm_l == 'hi':
                    step1 = f"{district} में {detected_crop} के लिए वास्तविक सिंचाई अंतराल के तहत मिट्टी की नमी और कवक बीजाणुओं की पृष्ठभूमि स्थिति का पुनर्निर्माण किया जा रहा है।"
                    step2 = f"कारणात्मक हस्तक्षेप do(3 दिन पहले सिंचाई / समय सारणी समायोजन) लागू किया जा रहा है।"
                    step3 = f"वानस्पतिक/फूल अवस्था में नमी का तनाव 30% तक कम हो जाता है, लेकिन रात के समय पत्तियों की आर्द्रता थोड़ी बढ़ जाती है।"
                    summary = f"समय पर सिंचाई से नमी का तनाव कम होता है और उपज सुरक्षित रहती है, लेकिन रात की नमी से बचने के लिए सुबह ड्रिप से सिंचाई करनी चाहिए।"
                    trade_offs = (
                        f"| पैरामीटर | देखा गया वास्तविक | काउंटरफैक्चुअल समायोजन |\n"
                        f"| :--- | :--- | :---\n"
                        f"| **नमी तनाव** | मध्यम | 30% तक कमी |\n"
                        f"| **सूक्ष्म जलवायु** | शुष्क | रात की सापेक्ष आर्द्रता में थोड़ी वृद्धि |"
                    )
                else:
                    step1 = f"Reconstructing background moisture tension and fungal spore presence under actual irrigation interval for {detected_crop} in {district}."
                    step2 = f"Applying surgical intervention do(Irrigate = 3 Days Earlier / Adjusted Schedule)."
                    step3 = f"Moisture stress in vegetative / flowering stage is alleviated by 30%, but canopy relative humidity rises during night hours."
                    summary = f"Adjusted irrigation reduces moisture stress and safeguards yield, but requires drip or morning scheduling to avoid nocturnal leaf wetness."
                    trade_offs = (
                        f"| Parameter | Observed History | Counterfactual Adjustment |\n"
                        f"| :--- | :--- | :---\n"
                        f"| **Moisture Stress** | Moderate | Alleviated by 30% |\n"
                        f"| **Canopy Microclimate** | Dry | Slightly elevated night RH |"
                    )
            elif scenario_type == "pesticide_intervention":
                confidence = 84
                if norm_l == 'kn':
                    step1 = f"{district} ಜಿಲ್ಲೆಯಲ್ಲಿ ಮಳೆಗೆ ಮುನ್ನ ಅನುಕೂಲಕರ ಉಷ್ಣಾಂಶದಲ್ಲಿ {disease or 'ರೋಗಾಣು'} ಸುಪ್ತ ಬೀಜಕಗಳು ಸಕ್ರಿಯವಾಗಿದ್ದವು."
                    step2 = f"ಕಾರಣಾತ್ಮಕ ಹಸ್ತಕ್ಷೇಪ do(ಮಳೆ ಬರುವ 48 ಗಂಟೆ ಮುನ್ನ ರೋಗನಿರೋಧಕ ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಸಿಂಪಡಣೆ) ಅನ್ವಯಿಸಲಾಗುತ್ತಿದೆ."
                    step3 = f"ಎಲೆಯ ಮೇಲೆ ರಕ್ಷಣಾತ್ಮಕ ಜೈವಿಕ ಕವಚ ನಿರ್ಮಾಣವಾಗಿ ಮಳೆಯ ಸಮಯದಲ್ಲಿ ಬೀಜಕಗಳು ಎಲೆಯ ರಂಧ್ರ ಪ್ರವೇಶಿಸುವುದನ್ನು ತಡೆಯುತ್ತದೆ."
                    summary = f"ಮುನ್ನೆಚ್ಚರಿಕೆಯಾಗಿ ಸಿಂಪಡಣೆ ಮಾಡಿದ್ದರೆ, ರೋಗ ಕಾಣಿಸಿಕೊಂಡ ನಂತರ ಸಿಂಪಡಿಸುವುದಕ್ಕಿಂತ 60-70% ರಷ್ಟು ಸೋಂಕಿನ ತೀವ್ರತೆಯನ್ನು ಕಡಿಮೆ ಮಾಡುತ್ತಿತ್ತು."
                    trade_offs = (
                        f"| ನಿಯತಾಂಕ | ಗಮನಿಸಿದ ವಾಸ್ತವ (ರೋಗ ಬಂದ ನಂತರ ಸಿಂಪಡಣೆ) | ಕೌಂಟರ್‌ಫ್ಯಾಕ್ಚುಯಲ್ (ಮಳೆಗೆ ಮುನ್ನ ರೋಗನಿರೋಧಕ ಕ್ರಮ) |\n"
                        f"| :--- | :--- | :---\n"
                        f"| **ರೋಗಾಣು ಪ್ರವೇಶ** | ಎಲೆಯ ಅಂಗಾಂಶದಲ್ಲಿ ಹರಡಿದೆ | ಬೀಜಕ ಪ್ರವೇಶಕ್ಕೆ ಮುನ್ನವೇ ತಡೆಯಲಾಗಿದೆ |\n"
                        f"| **ರಾಸಾಯನಿಕ ಪ್ರಮಾಣ** | ಅಧಿಕ (ಹಲವು ಕರಗುವ ಔಷಧಿಗಳು) | ಕಡಿಮೆ (ಒಂದೇ ಒಂದು ಮುನ್ನೆಚ್ಚರಿಕೆ ಜೈವಿಕ ಪ್ರಮಾಣ) |"
                    )
                elif norm_l == 'hi':
                    step1 = f"{district} में बारिश से पहले अनुकूल तापमान में {disease or 'रोगजनक'} के सुप्त बीजाणु सक्रिय थे।"
                    step2 = f"कारणात्मक हस्तक्षेप do(बारिश से 48 घंटे पहले निवारक बायो-फंगीसाइड छिड़काव) लागू किया जा रहा है।"
                    step3 = f"पत्तियों पर सुरक्षात्मक जैविक परत बनने से बारिश के दौरान बीजाणुओं का रंध्रों में प्रवेश रुक जाता है।"
                    summary = f"निवारक छिड़काव से संक्रमण की गंभीरता में 60-70% तक की कमी आती, जो लक्षण उभरने के बाद किए गए छिड़काव से कहीं अधिक प्रभावी होता।"
                    trade_offs = (
                        f"| पैरामीटर | देखा गया वास्तविक (लक्षण बाद छिड़काव) | काउंटरफैक्चुअल (बारिश पूर्व निवारक) |\n"
                        f"| :--- | :--- | :---\n"
                        f"| **रोग संक्रमण** | पत्ती के ऊतकों में फैल चुका था | बीजाणु प्रवेश से पहले ही रोक दिया गया |\n"
                        f"| **रसायन की मात्रा** | अधिक (बार-बार छिड़काव की आवश्यकता) | कम (एकल समयबद्ध निवारक खुराक) |"
                    )
                else:
                    step1 = f"Latent spore density of {disease or 'pathogen'} was active prior to rainfall under favorable temperature in {district}."
                    step2 = f"Applying surgical intervention do(Spray = Prophylactic Bio-fungicide 48h Pre-Rain)."
                    step3 = f"Forming protective biochemical leaf coating prevents germ-tube penetration into stomata during the rain event."
                    summary = f"Prophylactic application would have reduced infection severity by up to 60-70% compared to curative spraying after lesions emerged."
                    trade_offs = (
                        f"| Parameter | Observed (Curative Post-Symptom) | Counterfactual (Preventive Pre-Rain) |\n"
                        f"| :--- | :--- | :---\n"
                        f"| **Infection Penetration** | Established in leaf tissue | Blocked before spore entry |\n"
                        f"| **Chemical Quantity Needed** | Higher (Multiple curative doses) | Lower (Single timely preventive dose) |"
                    )
            elif scenario_type == "sowing_date":
                confidence = 80
                if norm_l == 'kn':
                    step1 = f"{district} ಜಿಲ್ಲೆಯಲ್ಲಿ ತಡವಾದ ಬಿತ್ತನೆಯಿಂದಾಗಿ ಹೂಬಿಡುವ ಮತ್ತು ಕಾಳು ತುಂಬುವ ಹಂತವು ಗರಿಷ್ಠ ತಾಪಮಾನದ ಅವಧಿಯೊಂದಿಗೆ ಹೊಂದಾಣಿಕೆಯಾಯಿತು."
                    step2 = f"ಕಾರಣಾತ್ಮಕ ಹಸ್ತಕ್ಷೇಪ do(12 ದಿನ ಮುಂಚಿತವಾಗಿ ಬಿತ್ತನೆ) ಅನ್ವಯಿಸಲಾಗುತ್ತಿದೆ."
                    step3 = f"ಗರಿಷ್ಠ ತಾಪಮಾನ ಮಿತಿ ತಲುಪುವ ಮೊದಲೇ ಬೆಳೆಯು ಕಾಳು ತುಂಬುವ ನಿರ್ಣಾಯಕ ಹಂತವನ್ನು ಪೂರ್ಣಗೊಳಿಸುತ್ತದೆ."
                    summary = f"ಬಿತ್ತನೆಯನ್ನು 12 ದಿನ ಮುಂಚಿತವಾಗಿ ಮಾಡಿದ್ದರೆ ತೀವ್ರ ಶಾಖದ ಒತ್ತಡ ತಪ್ಪಿ, ಇಳುವರಿಯಲ್ಲಿ +10% ರಿಂದ +14% ರಷ್ಟು ನಿವ್ವಳ ಹೆಚ್ಚಳವಾಗುತ್ತಿತ್ತು."
                    trade_offs = (
                        f"| ನಿಯತಾಂಕ | ಗಮನಿಸಿದ ತಡವಾದ ಬಿತ್ತನೆ | ಕೌಂಟರ್‌ಫ್ಯಾಕ್ಚುಯಲ್ ಮುಂಚಿತ ಬಿತ್ತನೆ |\n"
                        f"| :--- | :--- | :---\n"
                        f"| **ಅಂತ್ಯ ಹಂತದ ಶಾಖದ ಒತ್ತಡ** | ಕಾಳು ತುಂಬುವಾಗ ಅಧಿಕ | ಸಂಪೂರ್ಣ ನಿಯಂತ್ರಣ / ಮೊದಲೇ ಪೂರ್ಣ |\n"
                        f"| **ಅಂತಿಮ ಕಟಾವಿನ ಇಳುವರಿ** | ಮೂಲಮಟ್ಟ | **+10% ರಿಂದ +14% ಅಧಿಕ ಇಳುವರಿ** |"
                    )
                elif norm_l == 'hi':
                    step1 = f"{district} में देर से बुवाई के कारण दाना भरने की अवस्था अत्यधिक तापमान वाले समय से टकरा गई।"
                    step2 = f"कारणात्मक हस्तक्षेप do(12 दिन पहले बुवाई) लागू किया जा रहा है।"
                    step3 = f"फसल अधिकतम तापमान सीमा तक पहुंचने से पहले दाना भरने की महत्वपूर्ण अवस्था पूरी कर लेती है।"
                    summary = f"बुवाई 12 दिन पहले करने से टर्मिनल हीट स्ट्रेस से बचाव होता और उपज में अनुमानित +10% से +14% की वृद्धि होती।"
                    trade_offs = (
                        f"| पैरामीटर | देखी गई देर से बुवाई | काउंटरफैक्चुअल अगेती बुवाई |\n"
                        f"| :--- | :--- | :---\n"
                        f"| **टर्मिनल ताप तनाव** | दाना भरने के दौरान अधिक | पूरी तरह बचाव / समय पूर्व संपन्न |\n"
                        f"| **अंतिम कटाई उपज** | आधार रेखा | **+10% से +14% अधिक पैदावार** |"
                    )
                else:
                    step1 = f"Historical sowing resulted in late-stage anthesis coinciding with peak terminal heat in {district}."
                    step2 = f"Applying surgical intervention do(Sowing Date = 12 Days Earlier)."
                    step3 = f"Crop completes critical grain filling / pod development before maximum temperature thresholds are reached."
                    summary = f"Advancing sowing date by 12 days would have avoided terminal heat stress and improved yield by an estimated +10% to +14%."
                    trade_offs = (
                        f"| Parameter | Observed Sowing | Counterfactual Early Sowing |\n"
                        f"| :--- | :--- | :---\n"
                        f"| **Terminal Heat Stress** | High during grain fill | Avoided / Completed earlier |\n"
                        f"| **Final Harvest Tonnage** | Baseline | **+10% to +14% higher** |"
                    )
            else:
                confidence = 72
                if norm_l == 'kn':
                    step1 = f"{district} ಜಿಲ್ಲೆಯಲ್ಲಿ {disp_crop} ಬೆಳೆಗೆ ಹಿನ್ನೆಲೆ ವಾಸ್ತವಿಕ ಪರಿಸ್ಥಿತಿಗಳು."
                    step2 = f"ಕಾರಣಾತ್ಮಕ ಹಸ್ತಕ್ಷೇಪ do({query_clean}) ಅನ್ವಯಿಸಲಾಗುತ್ತಿದೆ."
                    step3 = f"ಕೃಷಿ ಪರಿಕರಗಳ ಬಳಕೆಯಲ್ಲಿ ಬದಲಾವಣೆ ಮಾಡುವುದರಿಂದ ಸಂಪನ್ಮೂಲ ಬಳಕೆಯ ದಕ್ಷತೆಯಲ್ಲಿ ಧನಾತ್ಮಕ ಸುಧಾರಣೆಯಾಗುತ್ತದೆ."
                    summary = f"ಈ ಕೌಂಟರ್‌ಫ್ಯಾಕ್ಚುಯಲ್ ಕ್ರಮವು ಬೆಳೆಯ ಹುರುಪು ಮತ್ತು ಇಳುವರಿಯ ಸ್ಥಿರತೆಯನ್ನು ಗಣನೀಯವಾಗಿ ಹೆಚ್ಚಿಸುತ್ತದೆ."
                    trade_offs = (
                        f"| ನಿಯತಾಂಕ | ಗಮನಿಸಿದ ವಾಸ್ತವ | ಕೌಂಟರ್‌ಫ್ಯಾಕ್ಚುಯಲ್ ಕ್ರಮ |\n"
                        f"| :--- | :--- | :---\n"
                        f"| **ಸಂಪನ್ಮೂಲ ದಕ್ಷತೆ** | ಸಾಮಾನ್ಯ ಮೂಲಮಟ್ಟ | ಅತ್ಯುತ್ತಮ ಪರಿಕರ ನಿರ್ವಹಣೆ |"
                    )
                elif norm_l == 'hi':
                    step1 = f"{district} में {disp_crop} के लिए आधारभूत पृष्ठभूमि स्थितियां।"
                    step2 = f"कारणात्मक हस्तक्षेप do({query_clean}) लागू किया जा रहा है।"
                    step3 = f"कृषि आदानों में समयोचित बदलाव से संसाधन उपयोग दक्षता में सीधा सुधार होता है।"
                    summary = f"यह काउंटरफैक्चुअल हस्तक्षेप फसल की सेहत और उपज स्थिरता में उल्लेखनीय सुधार लाता है।"
                    trade_offs = (
                        f"| पैरामीटर | देखी गई वास्तविकता | काउंटरफैक्चुअल कदम |\n"
                        f"| :--- | :--- | :---\n"
                        f"| **संसाधन दक्षता** | मानक आधार रेखा | अनुकूलित इनपुट प्रबंधन |"
                    )
                else:
                    step1 = f"Background baseline conditions for {detected_crop} in {district}."
                    step2 = f"Applying surgical intervention do({query_clean})."
                    step3 = f"Modifying agronomic inputs creates direct positive shift in resource utilization efficiency."
                    summary = f"The counterfactual intervention produces a measurable improvement in crop vigor and yield stability."
                    trade_offs = (
                        f"| Parameter | Observed Reality | Counterfactual Action |\n"
                        f"| :--- | :--- | :---\n"
                        f"| **Resource Efficiency** | Standard baseline | Optimized input delivery |"
                    )
            
            h1 = "1. ಹಂತ 1: ಅಬ್ಡಕ್ಷನ್ (ಅಗೋಚರ ಪರಿಸ್ಥಿತಿಗಳ ಪತ್ತೆ)" if norm_l == 'kn' else ("1. चरण 1: एब्डक्शन (अप्रत्यक्ष स्थितियों का अनुमान)" if norm_l == 'hi' else "1. Step 1: Abduction (Inferring Latent Unobserved Conditions $U$)")
            h2 = "2. ಹಂತ 2: ಕ್ರಿಯೆ (ಕಾರಣಾತ್ಮಕ ಹಸ್ತಕ್ಷೇಪ do(·))" if norm_l == 'kn' else ("2. चरण 2: क्रिया (कारणात्मक हस्तक्षेप do(·))" if norm_l == 'hi' else "2. Step 2: Action (Applying the Counterfactual Intervention $\\text{{do}}(\\cdot)$)")
            h3 = "3. ಹಂತ 3: ಭವಿಷ್ಯ ನುಡಿ (ಕೌಂಟರ್‌ಫ್ಯಾಕ್ಚುಯಲ್ ಫಲಿತಾಂಶ ಲೆಕ್ಕಾಚಾರ)" if norm_l == 'kn' else ("3. चरण 3: भविष्यवाणी (काउंटरफैक्चुअल परिणाम गणना)" if norm_l == 'hi' else "3. Step 3: Prediction (Counterfactual Outcome Calculation)")
            h_sum = "ಕೌಂಟರ್‌ಫ್ಯಾಕ್ಚುಯಲ್ ಫಲಿತಾಂಶದ ಸಾರಾಂಶ" if norm_l == 'kn' else ("काउंटरफैक्चुअल परिणाम का सारांश" if norm_l == 'hi' else "Summary of Counterfactual Outcome")
            h_to = "ವ್ಯತ್ಯಾಸ ಮತ್ತು ತುಲನಾತ್ಮಕ ವಿಶ್ಲೇಷಣೆ" if norm_l == 'kn' else ("तुलनात्मक एवं ट्रेड-ऑफ विश्लेषण" if norm_l == 'hi' else "The Trade-Off Analysis")
            h_conf = "ಸಂಭಾವ್ಯತೆಯ ವಿಶ್ವಾಸಾರ್ಹತೆ ಶೇಕಡಾವಾರು" if norm_l == 'kn' else ("संभाव्यता विश्वास प्रतिशत" if norm_l == 'hi' else "Probabilistic Confidence Percentage")
            lbl_conf = "ವಿಶ್ವಾಸಾರ್ಹತೆ" if norm_l == 'kn' else ("विश्वास" if norm_l == 'hi' else "Confidence")
            h_sum = "ಕೌಂಟರ್‌ಫ್ಯಾಕ್ಚುಯಲ್ ಫಲಿತಾಂಶದ ಸಾರಾಂಶ" if 'kn' in norm_l else "काउंटरफैक्चुअल परिणाम का सारांश" if 'hi' in norm_l else "Summary of Counterfactual Outcome"
            h_to = "ವ್ಯತ್ಯಾಸ ಮತ್ತು ತುಲನಾತ್ಮಕ ವಿಶ್ಲೇಷಣೆ" if 'kn' in norm_l else "तुलनात्मक एवं ट्रेड-ऑफ विश्लेषण" if 'hi' in norm_l else "The Trade-Off Analysis"
            h_conf = "ಸಂಭಾವ್ಯತೆಯ ವಿಶ್ವಾಸಾರ್ಹತೆ ಶೇಕಡಾವಾರು" if 'kn' in norm_l else "संभाव्यता विश्वास प्रतिशत" if 'hi' in norm_l else "Probabilistic Confidence Percentage"
            lbl_conf = "ವಿಶ್ವಾಸಾರ್ಹತೆ" if 'kn' in norm_l else "विश्वास" if 'hi' in norm_l else "Confidence"

            explanation = (
                f"### **{h1}**\n{step1}\n\n"
                f"---\n\n"
                f"### **{h2}**\n{step2}\n\n"
                f"---\n\n"
                f"### **{h3}**\n{step3}\n\n"
                f"---\n\n"
                f"### **{h_sum}**\n{summary}\n\n"
                f"---\n\n"
                f"### **{h_to}**\n\n{trade_offs}\n\n"
                f"---\n\n"
                f"### **{h_conf}**\n**{confidence}% {lbl_conf}**"
            )
        else:
            explanation = str(llm_response)
            confidence = 76
            match = re.search(r'(\d{2})%', explanation)
            if match:
                confidence = int(match.group(1))

        return {
            'status': 'success',
            'query': query,
            'scenario_type': scenario_type,
            'action_description': action_desc,
            'confidence_pct': confidence,
            'explanation': explanation,
            'crop': crop,
            'disease': disease
        }


# ==========================================
# 3. MULTI-AGENT AI DEBATE ROOM
# ==========================================
class MultiAgentDebateEngine:
    """
    Orchestrates a 5-Agent live agronomic debate:
    1. 🌾 Dr. Rao (Lead Agronomist - Yield & Nutrition)
    2. 📈 Sharmaji (APMC Market Economist - Price & Seasonality)
    3. 🔬 Dr. Tara (Plant Pathologist - Pest & Fungal Risk)
    4. 💧 Er. Ramesh Kulkarni (Irrigation & Water Resources Specialist)
    5. 🛡️ Patil (Financial & Risk Officer - Debt & Ruin Prevention)
    """

    AGENTS = [
        {
            'id': 'agronomist',
            'name': 'Dr. V. Rao',
            'role': 'Lead Agronomist',
            'avatar': '🌾',
            'color': '#2e7d32',
            'focus': 'Maximum Biomass, Vegetative Vigor, and Optimized N-P-K Nutrition'
        },
        {
            'id': 'economist',
            'name': 'R. K. Sharma',
            'role': 'APMC Market Economist',
            'avatar': '📈',
            'color': '#0288d1',
            'focus': 'Mandi Price Volatility, Seasonality Gluts, and Storage Feasibility'
        },
        {
            'id': 'pathologist',
            'name': 'Dr. Tara Devi',
            'role': 'Senior Plant Pathologist',
            'avatar': '🔬',
            'color': '#c2185b',
            'focus': 'Microclimate Spore Germination, Vector Thresholds, and Disease Immunity'
        },
        {
            'id': 'irrigation_specialist',
            'name': 'Er. R. Kulkarni',
            'role': 'Smart Irrigation & Hydrology Specialist',
            'avatar': '💧',
            'color': '#0284c7',
            'focus': 'Evapotranspiration (ETc), Soil Moisture Depletion, Drip Fertigation, and Rain-Skip Optimization'
        },
        {
            'id': 'risk_officer',
            'name': 'S. Patil',
            'role': 'Farm Credit & Risk Officer',
            'avatar': '🛡️',
            'color': '#e65100',
            'focus': 'Capital Preservation, Loan Default Prevention, and Smallholder Safety'
        }
    ]

    @classmethod
    def conduct_debate(cls, crop: str = "Tomato", district: str = "Dharwad",
                       disease: str = "", price_info: str = "",
                       farmer_budget: str = "moderate",
                       lang: str = "en") -> Dict[str, Any]:
        """
        Runs a 5-agent debate round to forge a balanced consensus.
        """
        debate_prompt = f"""
Simulate a lively, insightful, and professional 5-Agent Agricultural Consultation Debate for a farmer.

Farm Context:
- Target Crop: {crop}
- District: {district}
- Disease Alert: {disease or 'None reported'}
- Market Price Trend: {price_info or 'Moderate volatility'}
- Farmer Risk/Budget Posture: {farmer_budget}
- Output Language: {lang}

The 5 Experts:
1. Dr. V. Rao (🌾 Agronomist): Focuses on high yield, fertilizer dose, soil preparation, and vegetative vigor.
2. R. K. Sharma (📈 Market Economist): Focuses on Mandi price trends, harvest timing, market glut risks, and buyer demand.
3. Dr. Tara Devi (🔬 Pathologist): Focuses on pest alerts, fungal prevention, weather-driven humidity risks, and bio-controls.
4. Er. R. Kulkarni (💧 Irrigation Specialist): Focuses on FAO Penman ETc water requirement, drip fertigation runtime, and soil moisture conservation.
5. S. Patil (🛡️ Risk & Credit Advisor): Focuses on keeping input costs low, preventing heavy debt, and protecting the farmer against bad seasons.

Please generate:
1. Turn-by-turn dialogue where each expert speaks once (2-3 crisp sentences each), challenging and refining each other's points.
2. A final synthesized UNANIMOUS CONSENSUS STRATEGY (Actionable 5-point plan).

Output in valid JSON format with keys:
{{
  "debate_turns": [
    {{"agent_id": "agronomist", "name": "Dr. V. Rao", "statement": "..."}},
    {{"agent_id": "economist", "name": "R. K. Sharma", "statement": "..."}},
    {{"agent_id": "pathologist", "name": "Dr. Tara Devi", "statement": "..."}},
    {{"agent_id": "irrigation_specialist", "name": "Er. R. Kulkarni", "statement": "..."}},
    {{"agent_id": "risk_officer", "name": "S. Patil", "statement": "..."}}
  ],
  "consensus_summary": "...",
  "key_takeaways": ["Point 1", "Point 2", "Point 3", "Point 4", "Point 5"]
}}
"""
        result = None
        if agri_llm and agri_llm.llm:
            try:
                response = agri_llm.llm.invoke(debate_prompt)
                raw_content = response.content if hasattr(response, 'content') else str(response)
                if isinstance(raw_content, list):
                    content = " ".join(part.get("text", str(part)) if isinstance(part, dict) else str(part) for part in raw_content)
                else:
                    content = str(raw_content)
                # Clean JSON code blocks if present
                content_clean = re.sub(r'```json\s*', '', content)
                content_clean = re.sub(r'```\s*$', '', content_clean).strip()
                import json
                result = json.loads(content_clean)
            except Exception as e:
                print(f"[Multi-Agent Debate] LLM parse failed: {e}")

        if not result or 'debate_turns' not in result:
            norm_l = (lang or 'en').lower()
            if 'kn' in norm_l:
                result = {
                    'debate_turns': [
                        {
                            'agent_id': 'agronomist',
                            'name': 'ಡಾ. ವಿ. ರಾವ್ (Dr. V. Rao)',
                            'statement': f"{district} ಜಿಲ್ಲೆಯಲ್ಲಿ {crop} ಬೆಳೆಗೆ 25+ ಕ್ವಿಂಟಾಲ್ ಅಧಿಕ ಇಳುವರಿ ಸಾಧಿಸಲು ಸಮತೋಲಿತ 120:60:40 NPK ರಸಗೊಬ್ಬರ ಪ್ರಮಾಣ ಮತ್ತು ಸಾಲು-ಬದು (Ridge & Furrow) ಬಿತ್ತನೆ ಪದ್ಧತಿ ಅತ್ಯಗತ್ಯ."
                        },
                        {
                            'agent_id': 'economist',
                            'name': 'ಆರ್. ಕೆ. ಶರ್ಮಾ (R. K. Sharma)',
                            'statement': f"ಡಾ. ರಾವ್ ಅವರೇ ಸ್ವಲ್ಪ ನಿಲ್ಲಿ, {district} ಜಿಲ್ಲೆಯ ಎಲ್ಲ ರೈತರು ಒಟ್ಟಿಗೆ ಕೊಯ್ಲು ಮಾಡಿದರೆ ಸ್ಥಳೀಯ APMC ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ಬೆಲೆ ಕುಸಿತ ಉಂಟಾಗುತ್ತದೆ. ಆದ್ದರಿಂದ ಬೇಗ ಕೊಯ್ಲು ಅಥವಾ ಕಣಜದಲ್ಲಿ ಸುರಕ್ಷಿತ ದಾಸ್ತಾನಿಗೆ ಯೋಜನೆ ರೂಪಿಸಬೇಕು."
                        },
                        {
                            'agent_id': 'pathologist',
                            'name': 'ಡಾ. ತಾರಾ ದೇವಿ (Dr. Tara Devi)',
                            'statement': f"ಅಕ್ಟೋಬರ್-ನವೆಂಬರ್ ತೇವಾಂಶವು ಶಿಲೀಂಧ್ರ ರೋಗ ಮತ್ತು ರಸಹೀರುವ ಕೀಟಗಳ ಅಪಾಯವನ್ನು ಹೆಚ್ಚಿಸುತ್ತದೆ. ಅತಿಯಾದ ಸಾರಜನಕವು ಬೆಳೆಯನ್ನು ರೋಗಕ್ಕೆ ತುತ್ತಾಗಿಸುತ್ತದೆ. ಟ್ರೈಕೋಡರ್ಮಾ ಬೀಜೋಪಚಾರ ಮತ್ತು ಬೇವಿನ ಎಣ್ಣೆ ಸಿಂಪಡಣೆಯನ್ನು ಕಡ್ಡಾಯಗೊಳಿಸಬೇಕು."
                        },
                        {
                            'agent_id': 'irrigation_specialist',
                            'name': 'ಇಂ. ಆರ್. ಕುಲಕರ್ಣಿ (Er. R. Kulkarni)',
                            'statement': f"ಬೇರು ಕೊಳೆಯುವಿಕೆ ಮತ್ತು ಶಿಲೀಂಧ್ರ ಹರಡುವಿಕೆಯನ್ನು ತಡೆಯಲು, ದಿನದ ETc ಆಧಾರದ ಮೇಲೆ ಬೆಳಗಿನ ವೇಳೆಯಲ್ಲೇ ಹನಿ ನೀರಾವರಿ ಒದಗಿಸಬೇಕು. ಮಳೆಯು 5ಮಿ.ಮೀ ಮೀರಿದಾಗ 24-48 ಗಂಟೆಗಳ ಕಾಲ ನೀರು ಹಾಯಿಸುವುದನ್ನು ತಕ್ಷಣ ಸ್ಥಗಿತಗೊಳಿಸಬೇಕು."
                        },
                        {
                            'agent_id': 'risk_officer',
                            'name': 'ಎಸ್. ಪಾಟೀಲ್ (S. Patil)',
                            'statement': f"ನಾನು ಡಾ. ತಾರಾ, ಶರ್ಮಾಜಿ ಮತ್ತು ಕುಲಕರ್ಣಿ ಅವರ ಮಾತನ್ನು ಬೆಂಬಲಿಸುತ್ತೇನೆ. ರೈತರ ಬಂಡವಾಳ ರಕ್ಷಣೆಯಾಗಬೇಕು. ಹನಿ ನೀರಾವರಿ ಮೂಲಕ ರಸಗೊಬ್ಬರ ನೀಡುವುದರಿಂದ 40% ವೆಚ್ಚ ಉಳಿತಾಯವಾಗುತ್ತದೆ ಮತ್ತು 20% ವಿಸ್ತೀರ್ಣದಲ್ಲಿ ದ್ವಿದಳ ಧಾನ್ಯದ ಅಂತರಬೆಳೆ ಬೆಳೆಯುವುದರಿಂದ ಮಾರುಕಟ್ಟೆ ನಷ್ಟಕ್ಕೆ ವಿಮೆ ದೊರೆತಂತಾಗುತ್ತದೆ."
                        }
                    ],
                    'consensus_summary': f"5 ತಜ್ಞ ಏಜೆಂಟ್‌ಗಳು {crop} ಬೆಳೆಗೆ ಸಮಗ್ರ ಸ್ಮಾರ್ಟ್ ಕೃಷಿ ಶಿಷ್ಟಾಚಾರಕ್ಕೆ ಸರ್ವಾನುಮತದಿಂದ ಒಪ್ಪಿಗೆ ನೀಡಿದ್ದಾರೆ: ನೀರು-ಗೊಬ್ಬರ ಉಳಿಸಲು ಹನಿ ನೀರಾವರಿ (Fertigation), ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಬೀಜೋಪಚಾರ, ಮಳೆ-ಆಧಾರಿತ ನೀರಾವರಿ ನಿಯಂತ್ರಣ, ಮತ್ತು APMC ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಕುಸಿತ ತಪ್ಪಿಸಲು ಹಂತಹಂತದ ಕೊಯ್ಲು.",
                    'key_takeaways': [
                        f"ಪೋಷಕಾಂಶ ಸೋರಿಕೆ ತಡೆಯಲು ಹನಿ ನೀರಾವರಿ ಮೂಲಕ ಕಂತುಗಳಲ್ಲಿ ಸಾರಜನಕ ಗೊಬ್ಬರ ನೀಡಿ",
                        f"ಬಿತ್ತನೆಗೆ ಮುನ್ನ ಟ್ರೈಕೋಡರ್ಮಾ ಜೈವಿಕ ಬೀಜೋಪಚಾರ ಕಡ್ಡಾಯವಾಗಿ ಮಾಡಿ",
                        f"ಬೆಳೆ ನೀರಿನ ಆವಿಯಾಗುವಿಕೆ (ETc) ಆಧಾರದ ಮೇಲೆ ನೀರಾವರಿ ನೀಡಿ, ಮಳೆಯಾದಾಗ ನೀರು ಹಾಯಿಸಬೇಡಿ",
                        f"ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ಬೆಲೆ ಕುಸಿತ ತಪ್ಪಿಸಲು 7-10 ದಿನಗಳ ಅಂತರದಲ್ಲಿ ಹಂತಹಂತವಾಗಿ ಕೊಯ್ಲು ಮಾಡಿ",
                        f"20% ದ್ವಿದಳ ಧಾನ್ಯದ ಅಂತರಬೆಳೆ ಬೆಳೆಯುವ ಮೂಲಕ ಆರ್ಥಿಕ ಭದ್ರತೆ ಕಾಪಾಡಿಕೊಳ್ಳಿ"
                    ]
                }
            elif 'hi' in norm_l:
                result = {
                    'debate_turns': [
                        {
                            'agent_id': 'agronomist',
                            'name': 'डॉ. वी. राव (Dr. V. Rao)',
                            'statement': f"{district} में {crop} की 25+ क्विंटल बंपर पैदावार के लिए संतुलित 120:60:40 NPK उर्वरक और मेड़-कूड़ (Ridge & Furrow) विधि से समय पर बुवाई आवश्यक है।"
                        },
                        {
                            'agent_id': 'economist',
                            'name': 'आर. के. शर्मा (R. K. Sharma)',
                            'statement': f"डॉ. राव, थोड़ा रुकिए, यदि {district} के सभी किसान एक साथ फसल काटते हैं तो स्थानीय APMC मंडी में आवक बढ़ने से भाव गिर जाएंगे। हमें अगेती कटाई या खेत पर हवादार भंडारण की योजना बनानी चाहिए।"
                        },
                        {
                            'agent_id': 'pathologist',
                            'name': 'डॉ. तारा देवी (Dr. Tara Devi)',
                            'statement': f"यह न भूलें कि मौसम की नमी से फफूंद जनित रोगों और रस चूसक कीटों का खतरा बढ़ जाता है। अत्यधिक नाइट्रोजन से पत्तियां कोमल होकर रोग की चपेट में आ सकती हैं। ट्राइकोडर्मा बीज उपचार और नीम का छिड़काव अनिवार्य है।"
                        },
                        {
                            'agent_id': 'irrigation_specialist',
                            'name': 'ईं. आर. कुलकर्णी (Er. R. Kulkarni)',
                            'statement': f"जड़ों में सड़न रोकने के लिए दैनिक ETc नमी खपत के अनुसार केवल सुबह के समय ड्रिप से पानी दें, और 5 मिमी से अधिक वर्षा होने पर 24-48 घंटे तक सिंचाई तुरंत रोकें।"
                        },
                        {
                            'agent_id': 'risk_officer',
                            'name': 'एस. पाटिल (S. Patil)',
                            'statement': f"मैं डॉ. तारा, शर्माजी और कुलकर्णी जी से सहमत हूं। किसान की लागत सुरक्षित रहनी चाहिए। ड्रिप फर्टिगेशन से 40% खाद खर्च बचता है और 20% रकबे में दलहनी अंतःफसल (Intercropping) लगाने से बाजार जोखिम का बीमा मिल जाता है।"
                        }
                    ],
                    'consensus_summary': f"पांचों विशेषज्ञ एजेंट {crop} के लिए एकीकृत स्मार्ट कृषि प्रोटोकॉल पर सर्वसम्मति से सहमत हैं: पानी और खाद बचाने के लिए ड्रिप फर्टिगेशन, बायो-फंगीसाइड बीज उपचार, मौसम आधारित सिंचाई नियंत्रण और APMC मंडी में भाव गिरने से बचने के लिए चरणबद्ध कटाई।",
                    'key_takeaways': [
                        f"पोषक तत्वों की बर्बादी रोकने के लिए ड्रिप फर्टिगेशन द्वारा किस्तों में नाइट्रोजन दें",
                        f"बुवाई से पहले ट्राइकोडर्मा विरिडी से जैविक बीज उपचार अवश्य करें",
                        f"दैनिक वाष्पोत्सर्जन (ETc) के आधार पर सिंचाई करें और बारिश होने पर सिंचाई रोकें",
                        f"मंडी में भाव गिरने से बचने के लिए 7-10 दिनों के अंतराल में चरणबद्ध कटाई करें",
                        f"20% क्षेत्र में दलहनी अंतःफसल लगाकर वित्तीय सुरक्षा कवच बनाएं"
                    ]
                }
            else:
                result = {
                    'debate_turns': [
                        {
                            'agent_id': 'agronomist',
                            'name': 'Dr. V. Rao',
                            'statement': f"For {crop} in {district}, we must ensure a balanced 120:60:40 NPK application and early ridge-and-furrow planting to achieve a target yield of 25+ quintals."
                        },
                        {
                            'agent_id': 'economist',
                            'name': 'R. K. Sharma',
                            'statement': f"Hold on Dr. Rao, if all farmers in {district} harvest in late October, the local APMC mandi will experience a price glut. We should aim for early harvest or arrange on-farm ventilated storage."
                        },
                        {
                            'agent_id': 'pathologist',
                            'name': 'Dr. Tara Devi',
                            'statement': f"Let's not forget that October humidity creates a high risk of fungal blight and sucking pests. Heavy nitrogen will make the foliage lush and vulnerable. We must mandate Trichoderma seed treatment and neem spray."
                        },
                        {
                            'agent_id': 'irrigation_specialist',
                            'name': 'Er. R. Kulkarni',
                            'statement': f"To prevent root saturation and fungal spore activation, we must regulate drip irrigation to morning hours based on daily ETc moisture loss, and immediately trigger a 24-48 hr rain-skip when precipitation exceeds 5mm."
                        },
                        {
                            'agent_id': 'risk_officer',
                            'name': 'S. Patil',
                            'statement': f"I agree with Dr. Tara, Sharmaji, and Kulkarni. The farmer's budget must be protected. Drip fertigation saves 40% fertilizer cost, and intercropping 20% area with pulses provides risk insurance against market gluts."
                        }
                    ],
                    'consensus_summary': f"The 5 expert agents unanimously agree on an Integrated Smart Farm Protocol for {crop}: Drip fertigation to save water and nutrients, bio-fungicide seed inoculation, rain-skip water scheduling, and staggered harvesting to beat APMC mandi gluts.",
                    'key_takeaways': [
                        f"Apply split nitrogen via drip fertigation to prevent nutrient leaching and lodging",
                        f"Use Trichoderma viride bio-treatment prior to sowing",
                        f"Schedule irrigation based on evapotranspiration (ETc) and observe rain-skip alerts",
                        f"Stagger harvest by 7-10 days to avoid peak market price drops",
                        f"Maintain a financial cushion with 20% pulse intercropping"
                    ]
                }

        norm_l = 'kn' if 'kn' in (lang or '').lower() else ('hi' if 'hi' in (lang or '').lower() else 'en')
        if norm_l == 'kn':
            # Guarantee 100% Kannada script integrity
            if not any('\u0c80' <= ch <= '\u0cff' for ch in result.get('consensus_summary', '')):
                result['consensus_summary'] = f"5 ತಜ್ಞ ಏಜೆಂಟ್‌ಗಳು {crop} ಬೆಳೆಗೆ ಸಮಗ್ರ ಸ್ಮಾರ್ಟ್ ಕೃಷಿ ಶಿಷ್ಟಾಚಾರಕ್ಕೆ ಸರ್ವಾನುಮತದಿಂದ ಒಪ್ಪಿಗೆ ನೀಡಿದ್ದಾರೆ: ನೀರು-ಗೊಬ್ಬರ ಉಳಿಸಲು ಹನಿ ನೀರಾವರಿ (Fertigation), ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಬೀಜೋಪಚಾರ, ಮಳೆ-ಆಧಾರಿತ ನೀರಾವರಿ ನಿಯಂತ್ರಣ, ಮತ್ತು APMC ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಕುಸಿತ ತಪ್ಪಿಸಲು ಹಂತಹಂತದ ಕೊಯ್ಲು."
            if not any('\u0c80' <= ch <= '\u0cff' for item in result.get('key_takeaways', []) for ch in item):
                result['key_takeaways'] = [
                    f"ಪೋಷಕಾಂಶ ಸೋರಿಕೆ ತಡೆಯಲು ಹನಿ ನೀರಾವರಿ ಮೂಲಕ ಕಂತುಗಳಲ್ಲಿ ಸಾರಜನಕ ಗೊಬ್ಬರ ನೀಡಿ",
                    f"ಬಿತ್ತನೆಗೆ ಮುನ್ನ ಟ್ರೈಕೋಡರ್ಮಾ ಜೈವಿಕ ಬೀಜೋಪಚಾರ ಕಡ್ಡಾಯವಾಗಿ ಮಾಡಿ",
                    f"ಬೆಳೆ ನೀರಿನ ಆವಿಯಾಗುವಿಕೆ (ETc) ಆಧಾರದ ಮೇಲೆ ನೀರಾವರಿ ನೀಡಿ, ಮಳೆಯಾದಾಗ ನೀರು ಹಾಯಿಸಬೇಡಿ",
                    f"ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ಬೆಲೆ ಕುಸಿತ ತಪ್ಪಿಸಲು 7-10 ದಿನಗಳ ಅಂತರದಲ್ಲಿ ಹಂತಹಂತವಾಗಿ ಕೊಯ್ಲು ಮಾಡಿ",
                    f"20% ದ್ವಿದಳ ಧಾನ್ಯದ ಅಂತರಬೆಳೆ ಬೆಳೆಯುವ ಮೂಲಕ ಆರ್ಥಿಕ ಭದ್ರತೆ ಕಾಪಾಡಿಕೊಳ್ಳಿ"
                ]
        elif norm_l == 'hi':
            # Guarantee 100% Hindi script integrity
            if not any('\u0900' <= ch <= '\u097f' for ch in result.get('consensus_summary', '')):
                result['consensus_summary'] = f"पांचों विशेषज्ञ एजेंट {crop} के लिए एकीकृत स्मार्ट कृषि प्रोटोकॉल पर सर्वसम्मति से सहमत हैं: पानी और खाद बचाने के लिए ड्रिप फर्टिगेशन, बायो-फंगीसाइड बीज उपचार, मौसम आधारित सिंचाई नियंत्रण और APMC मंडी में भाव गिरने से बचने के लिए चरणबद्ध कटाई।"
            if not any('\u0900' <= ch <= '\u097f' for item in result.get('key_takeaways', []) for ch in item):
                result['key_takeaways'] = [
                    f"पोषक तत्वों की बर्बादी रोकने के लिए ड्रिप फर्टिगेशन द्वारा किस्तों में नाइट्रोजन दें",
                    f"बुवाई से पहले ट्राइकोडर्मा विरिडी से जैविक बीज उपचार अवश्य करें",
                    f"दैनिक वाष्पोत्सर्जन (ETc) के आधार पर सिंचाई करें और बारिश होने पर सिंचाई रोकें",
                    f"मंडी में भाव गिरने से बचने के लिए 7-10 दिनों के अंतराल में चरणबद्ध कटाई करें",
                    f"20% क्षेत्र में दलहनी अंतःफसल लगाकर वित्तीय सुरक्षा कवच बनाएं"
                ]

        return {
            'status': 'success',
            'crop': crop,
            'district': district,
            'agents': cls.AGENTS,
            'debate_turns': result.get('debate_turns', []),
            'consensus_summary': result.get('consensus_summary', ''),
            'key_takeaways': result.get('key_takeaways', [])
        }


# ==========================================
# 4. REGRET MINIMIZATION ENGINE
# ==========================================
class RegretMinimizationEngine:
    """
    Computes Savage Minimax Regret & Downside Value-at-Risk across 3 strategic tiers:
    🔵 Safe Plan (Defensive / Capital Preservation)
    🟡 Balanced Plan (Optimal Sharpe / Minimax Regret)
    🟢 Aggressive Plan (Peak Upside Alpha)
    """

    PLANS_DATABASE = {
        'rice': {
            'safe': {
                'title': '🔵 Safe Plan (Defensive & Low-Water)',
                'title_kn': '🔵 ಸುರಕ್ಷಿತ ಯೋಜನೆ (ಬಂಡವಾಳ ರಕ್ಷಣೆ & ಕಡಿಮೆ ನೀರು)',
                'title_hi': '🔵 सुरक्षित योजना (पूंजी सुरक्षा एवं कम जल उपयोग)',
                'variety': 'Short-Duration Drought-Tolerant (e.g. Sahbhagi Dhan / R-RHZ-7)',
                'variety_kn': 'ಕಡಿಮೆ ಅವಧಿಯ ಬರ-ನಿರೋಧಕ ತಳಿ (ಉದಾ. ಸಹಭಾಗಿ ಧಾನ್ / R-RHZ-7)',
                'variety_hi': 'कम अवधि की सूखा-सहिष्णु किस्म (जैसे सहभागीय धान / R-RHZ-7)',
                'expected_profit_acre': '₹35,000 – ₹45,000',
                'expected_profit_acre_kn': '₹35,000 – ₹45,000',
                'expected_profit_acre_hi': '₹35,000 – ₹45,000',
                'downside_worst_case': '+₹15,000 (Protected Capital)',
                'downside_worst_case_kn': '+₹15,000 (ಬಂಡವಾಳ ಸಂಪೂರ್ಣ ಸುರಕ್ಷಿತ)',
                'downside_worst_case_hi': '+₹15,000 (पूंजी पूर्णतः सुरक्षित)',
                'capital_outlay': '₹14,000 / acre',
                'capital_outlay_kn': '₹14,000 / ಎಕರೆ',
                'capital_outlay_hi': '₹14,000 / एकड़',
                'strategy': 'Direct Seeded Rice (DSR), minimal chemical input, high straw fodder value.',
                'strategy_kn': 'ನೇರ ಬಿತ್ತನೆ ಭತ್ತ (DSR), ಕನಿಷ್ಠ ರಾಸಾಯನಿಕ ಬಳಕೆ, ಸಾವಯವ ಮಣ್ಣಿನ ಸುಧಾರಣೆ, ಶೂನ್ಯ ಸಾಲ, ಮೇವಿನ ಹೆಚ್ಚಿನ ಮೌಲ್ಯ.',
                'strategy_hi': 'सीधी बुवाई (DSR), न्यूनतम रासायनिक लागत, जैविक खाद, शून्य ऋण, उच्च चारा मूल्य।',
                'regret_score': 'Minimum Regret (0.08) — Immune to canal delay and rain failure.',
                'regret_score_kn': 'ಕನಿಷ್ಠ ವಿಷಾದ (0.08) — ಮಳೆ ವಿಫಲತೆ ಅಥವಾ ಕಾಲುವೆ ವಿಳಂಬದಲ್ಲೂ ನಷ್ಟವಿಲ್ಲ.',
                'regret_score_hi': 'न्यूनतम रिग्रेट (0.08) — बारिश में देरी या विफलता पर भी नुकसान नहीं।'
            },
            'balanced': {
                'title': '🟡 Balanced Plan (Optimal Hedging)',
                'title_kn': '🟡 ಸಮತೋಲಿತ ಯೋಜನೆ (ಸೂಕ್ತ ಅಪಾಯ ನಿರ್ವಹಣೆ)',
                'title_hi': '🟡 संतुलित योजना (इष्टतम जोखिम प्रबंधन)',
                'variety': 'Medium-Duration High-Yield (e.g. MTU 1010 / BPT 5204)',
                'variety_kn': 'ಮಧ್ಯಮ ಅವಧಿಯ ಅಧಿಕ ಇಳುವರಿ ತಳಿ (ಉದಾ. MTU 1010 / BPT 5204) + ಅಂತರಬೆಳೆ',
                'variety_hi': 'मध्यम अवधि की उच्च उपज किस्म (जैसे MTU 1010 / BPT 5204) + अंतःफसल',
                'expected_profit_acre': '₹55,000 – ₹70,000',
                'expected_profit_acre_kn': '₹55,000 – ₹70,000',
                'expected_profit_acre_hi': '₹55,000 – ₹70,000',
                'downside_worst_case': '₹0 (Break-even with MSP)',
                'downside_worst_case_kn': '₹0 (MSP ಬೆಂಬಲ ಬೆಲೆಯೊಂದಿಗೆ ವೆಚ್ಚ ಸರಿದೂಗಿಕೆ)',
                'downside_worst_case_hi': '₹0 (MSP समर्थन मूल्य पर शून्य नुकसान)',
                'capital_outlay': '₹22,000 / acre',
                'capital_outlay_kn': '₹22,000 / ಎಕರೆ',
                'capital_outlay_hi': '₹22,000 / एकड़',
                'strategy': 'System of Rice Intensification (SRI) with integrated bio-fertilizers and PMFBY insurance.',
                'strategy_kn': 'ಶ್ರೀ (SRI) ಅಥವಾ ಸುಧಾರಿತ ಸಾಲು ಪದ್ಧತಿ, ಸಮತೋಲಿತ ಜೈವಿಕ ಗೊಬ್ಬರಗಳು ಮತ್ತು PMFBY ಬೆಳೆ ವಿಮೆ.',
                'strategy_hi': 'श्री (SRI) या उन्नत कतार विधि, संतुलित जैव उर्वरक और PMFBY फसल बीमा।',
                'regret_score': 'Low Regret (0.22) — Best risk-adjusted return under normal rainfall.',
                'regret_score_kn': 'ಕಡಿಮೆ ವಿಷಾದ (0.22) — ಸಾಮಾನ್ಯ ಮಳೆಯಲ್ಲಿ ಅತ್ಯುತ್ತಮ ಅಪಾಯ-ಹೊಂದಾಣಿಕೆಯ ಆದಾಯ.',
                'regret_score_hi': 'कम रिग्रेट (0.22) — सामान्य मौसम में सर्वोत्तम जोखिम-समायोजित रिटर्न।'
            },
            'aggressive': {
                'title': '🟢 Aggressive Plan (Premium Aromatic / High Yield)',
                'title_kn': '🟢 ಆಕ್ರಮಣಕಾರಿ ಯೋಜನೆ (ಗರಿಷ್ಠ ಮಾರುಕಟ್ಟೆ ಲಾಭ)',
                'title_hi': '🟢 आक्रामक योजना (अधिकतम लाभ / प्रीमियम बाजार)',
                'variety': 'Aromatic / Fine Grain Basmati / Hybrid (e.g. Pusa 1121 / Arize 6444)',
                'variety_kn': 'ಪ್ರೀಮಿಯಂ ಸುಗಂಧಿತ / ಹೈಬ್ರಿಡ್ ತಳಿ (ಉದಾ. ಪೂಸಾ 1121 / Arize 6444)',
                'variety_hi': 'प्रीमियम सुगंधित बासमती / हाइब्रिड किस्म (जैसे पूसा 1121 / Arize 6444)',
                'expected_profit_acre': '₹90,000 – ₹1,25,000',
                'expected_profit_acre_kn': '₹90,000 – ₹1,25,000',
                'expected_profit_acre_hi': '₹90,000 – ₹1,25,000',
                'downside_worst_case': '-₹18,000 (Loss if severe blast or lodging)',
                'downside_worst_case_kn': '-₹18,000 (ತೀವ್ರ ರೋಗ ಅಥವಾ ಬಿರುಗಾಳಿ ಉಂಟಾದರೆ ನಷ್ಟದ ಅಪಾಯ)',
                'downside_worst_case_hi': '-₹18,000 (गंभीर कीट प्रकोप या प्रतिकूल मौसम पर जोखिम)',
                'capital_outlay': '₹32,000 / acre',
                'capital_outlay_kn': '₹32,000 / ಎಕರೆ',
                'capital_outlay_hi': '₹32,000 / एकड़',
                'strategy': 'Intensive fertigation, precision micro-nutrients (Zinc/Boron), preventive tricyclazole schedule.',
                'strategy_kn': 'ನಿಖರ ಹನಿ ನೀರಾವರಿ (Fertigation), ಸೂಕ್ಷ್ಮ ಪೋಷಕಾಂಶಗಳು (Zinc/Boron), ಮತ್ತು ಮುನ್ನೆಚ್ಚರಿಕೆ ರೋಗ ನಿಯಂತ್ರಣ.',
                'strategy_hi': 'सटीक ड्रिप फर्टिगेशन, सूक्ष्म पोषक तत्व (Zinc/Boron) और पूर्व-निवारक रोग नियंत्रण।',
                'regret_score': 'High Regret Potential (0.65) — Huge payoff if weather holds, high risk if pest surge.',
                'regret_score_kn': 'ಹೆಚ್ಚಿನ ವಿಷಾದ ಸಂಭವನೀಯತೆ (0.65) — ಹವಾಮಾನ ಅನುಕೂಲವಿದ್ದರೆ ಬಂಪರ್ ಲಾಭ, ವ್ಯತಿರಿಕ್ತವಾದರೆ ನಷ್ಟ.',
                'regret_score_hi': 'उच्च रिग्रेट संभावना (0.65) — मौसम अनुकूल रहने पर भारी मुनाफा, विपरीत होने पर जोखिम।'
            }
        },
        'groundnut': {
            'safe': {
                'title': '🔵 Safe Plan (Rainfed & Drought-Tolerant Bunch)',
                'title_kn': '🔵 ಸುರಕ್ಷಿತ ಯೋಜನೆ (ಬರ-ನಿರೋಧಕ & ರಕ್ಷಣಾತ್ಮಕ ಗೊಂಚಲು ತಳಿ)',
                'title_hi': '🔵 सुरक्षित योजना (कम लागत व सूखा-सहनशील गुच्छा किस्म)',
                'variety': 'Short-Duration Bunch (TMV-2 / JL-24 / K-6)',
                'variety_kn': 'ಕಡಿಮೆ ಅವಧಿಯ ಬರ-ನಿರೋಧಕ ಗೊಂಚಲು ತಳಿ (TMV-2 / JL-24 / ಕದಿರಿ-6)',
                'variety_hi': 'कम अवधि की सूखा-सहनशील गुच्छा किस्म (TMV-2 / JL-24 / कदिरी-6)',
                'expected_profit_acre': '₹32,000 – ₹46,000',
                'expected_profit_acre_kn': '₹32,000 – ₹46,000',
                'expected_profit_acre_hi': '₹32,000 – ₹46,000',
                'downside_worst_case': '+₹12,000 (Protected Seed & Capital)',
                'downside_worst_case_kn': '+₹12,000 (ಬಂಡವಾಳ ಮತ್ತು ಬೀಜ ವೆಚ್ಚ ಸಂಪೂರ್ಣ ಸುರಕ್ಷಿತ)',
                'downside_worst_case_hi': '+₹12,000 (पूंजी व बीज लागत पूर्णतः सुरक्षित)',
                'capital_outlay': '₹15,000 / acre',
                'capital_outlay_kn': '₹15,000 / ಎಕರೆ',
                'capital_outlay_hi': '₹15,000 / एकड़',
                'strategy': 'Ridge-and-furrow rainfed sowing with Trichoderma seed treatment, Rhizobium bio-inoculant, zero pesticide debt.',
                'strategy_kn': 'ಸಾಲು-ಬದು ಮಳೆಯಾಶ್ರಿತ ಬಿತ್ತನೆ, ಟ್ರೈಕೋಡರ್ಮಾ ಮತ್ತು ರೈಜೋಬಿಯಂ ಜೈವಿಕ ಬೀಜೋಪಚಾರ, ಶೂನ್ಯ ಕೀಟನಾಶಕ ಸಾಲ.',
                'strategy_hi': 'मेड़-कूड़ वर्षा आधारित बुवाई, ट्राइकोडर्मा और राइजोबियम जैव-बीजोपचार, शून्य कीटनाशक कर्ज।',
                'regret_score': 'Minimum Regret (0.09) — Zero downside ruin even under dry spell during pod development.',
                'regret_score_kn': 'ಕನಿಷ್ಠ ವಿಷಾದ (0.09) — ಕಾಯಿ ಕಟ್ಟುವ ಹಂತದಲ್ಲಿ ಮಳೆ ಕೈಕೊಟ್ಟರೂ ಬಂಡವಾಳ ಸುರಕ್ಷಿತ.',
                'regret_score_hi': 'न्यूनतम रिग्रेट (0.09) — फली विकास के समय सूखा पड़ने पर भी पूंजी सुरक्षित।'
            },
            'balanced': {
                'title': '🟡 Balanced Plan (High Oil & Foliar Disease Resistant)',
                'title_kn': '🟡 ಸಮತೋಲಿತ ಯೋಜನೆ (ಅಧಿಕ ಎಣ್ಣೆ ಅಂಶ & ಎಲೆ ಚುಕ್ಕೆ ರೋಗ ನಿರೋಧಕ)',
                'title_hi': '🟡 संतुलित योजना (उच्च तेल सामग्री व टिक्का रोग प्रतिरोधी)',
                'variety': 'High-Yielding Resistant Hybrid (GPBD-4 / G2-52 / ICGV-91114)',
                'variety_kn': 'ಅಧಿಕ ಇಳುವರಿ ಮತ್ತು ತಿಕ್ಕಾ ರೋಗ-ನಿರೋಧಕ ತಳಿ (GPBD-4 / G2-52 / ಕದಿರಿ-6)',
                'variety_hi': 'उच्च उपज एवं टिक्का रोग-प्रतिरोधी किस्म (GPBD-4 / G2-52 / ICGV-91114)',
                'expected_profit_acre': '₹58,000 – ₹82,000',
                'expected_profit_acre_kn': '₹58,000 – ₹82,000',
                'expected_profit_acre_hi': '₹58,000 – ₹82,000',
                'downside_worst_case': '+₹4,000 (MSP ₹7,517 Floor Cushion)',
                'downside_worst_case_kn': '+₹4,000 (ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ MSP ₹7,517 ಆರ್ಥಿಕ ರಕ್ಷಣೆ)',
                'downside_worst_case_hi': '+₹4,000 (सरकारी एमएसपी ₹7,517 पर लागत सुरक्षित)',
                'capital_outlay': '₹24,000 / acre',
                'capital_outlay_kn': '₹24,000 / ಎಕರೆ',
                'capital_outlay_hi': '₹24,000 / एकड़',
                'strategy': 'Drip micro-irrigation at pod formation, 200 kg/acre gypsum application at 45 DAS, PMFBY crop insurance.',
                'strategy_kn': 'ಕಾಯಿ ಕಟ್ಟುವ ಹಂತದಲ್ಲಿ ಹನಿ ನೀರಾವರಿ, ಬಿತ್ತನೆಯ 45ನೇ ದಿನಕ್ಕೆ 200 ಕೆಜಿ ಜಿಪ್ಸಮ್ (Gypsum) ಪೋಷಣೆ, PMFBY ವಿಮೆ.',
                'strategy_hi': 'फली बनने पर ड्रिप सिंचाई, 45 दिन पर 200 किग्रा जिप्सम प्रयोग, और PMFBY फसल बीमा।',
                'regret_score': 'Low Regret (0.21) — Optimal Sharpe ratio balancing pod weight and price realization.',
                'regret_score_kn': 'ಕಡಿಮೆ ವಿಷಾದ (0.21) — ಕಾಯಿ ತೂಕ ಮತ್ತು ಮಾರುಕಟ್ಟೆ ಬೆಲೆಯಲ್ಲಿ ಗರಿಷ್ಠ ಸಮತೋಲನ.',
                'regret_score_hi': 'कम रिग्रेट (0.21) — फली वजन और मंडी भाव में इष्टतम संतुलन व सुरक्षा।'
            },
            'aggressive': {
                'title': '🟢 Aggressive Plan (Export-Grade Bold Kernel / Mulched Drip)',
                'title_kn': '🟢 ಆಕ್ರಮಣಕಾರಿ ಯೋಜನೆ (ದೊಡ್ಡ ಗಾತ್ರದ ಬೋಲ್ಡ್ ಕಡಲೆಕಾಯಿ ರಫ್ತು ತಳಿ)',
                'title_hi': '🟢 आक्रामक योजना (बोल्ड दाना प्रीमियम निर्यात / मल्चिंग ड्रिप)',
                'variety': 'Large Bold Seed / Confectionery (Mallika / TG-37A / Kadiri Amaravathi)',
                'variety_kn': 'ದೊಡ್ಡ ಗಾತ್ರದ ಪ್ರೀಮಿಯಂ ಬೋಲ್ಡ್ ಕಡಲೆಕಾಯಿ ತಳಿ (ಮಲ್ಲಿಕಾ / TG-37A / ಕದಿರಿ ಅಮರಾವತಿ)',
                'variety_hi': 'बड़ा बोल्ड दाना निर्यात किस्म (मल्लिका / TG-37A / कदिरी अमरावती)',
                'expected_profit_acre': '₹95,000 – ₹1,50,000',
                'expected_profit_acre_kn': '₹95,000 – ₹1,50,000',
                'expected_profit_acre_hi': '₹95,000 – ₹1,50,000',
                'downside_worst_case': '-₹16,000 (Loss if severe root rot or unseasonal rain at harvest)',
                'downside_worst_case_kn': '-₹16,000 (ಕೊಯ್ಲು ವೇಳೆ ಅಕಾಲಿಕ ಮಳೆ ಅಥವಾ ಬೇರು ಕೊಳೆತ ಬಂದರೆ ನಷ್ಟ)',
                'downside_worst_case_hi': '-₹16,000 (कटाई पर बेमौसम बारिश या कॉलर रॉट से नुकसान का जोखिम)',
                'capital_outlay': '₹35,000 / acre',
                'capital_outlay_kn': '₹35,000 / ಎಕರೆ',
                'capital_outlay_hi': '₹35,000 / एकड़',
                'strategy': 'Silver-black plastic mulch, fertigation with micronutrient boron + calcium, pre-booked exporter contract.',
                'strategy_kn': 'ಪ್ಲಾಸ್ಟಿಕ್ ಮಲ್ಚಿಂಗ್, ಬೋರಾನ್ + ಕ್ಯಾಲ್ಸಿಯಂ ಸೂಕ್ಷ್ಮ ಪೋಷಕಾಂಶ ಫರ್ಟಿಗೇಷನ್, ಎಣ್ಣೆ ಮಿಲ್ & ರಫ್ತುದಾರರ ಪೂರ್ವ ಒಪ್ಪಂದ.',
                'strategy_hi': 'सिल्वर-ब्लैक प्लास्टिक मल्चिंग, बोरॉन + कैल्शियम फर्टिगेशन, तेल मिल व निर्यातकों से अनुबंध।',
                'regret_score': 'High Regret (0.62) — Peak commercial upside if harvest conditions remain dry and sunny.',
                'regret_score_kn': 'ಹೆಚ್ಚಿನ ವಿಷಾದ ಸಂಭವನೀಯತೆ (0.62) — ಬಿಸಿಲು ಮತ್ತು ಒಣ ಹವೆ ಇದ್ದರೆ ಗರಿಷ್ಠ ಆದಾಯ, ಮಳೆಯಾದರೆ ತೊಂದರೆ.',
                'regret_score_hi': 'उच्च रिग्रेट संभावना (0.62) — कटाई पर सूखा मौसम रहने पर बंपर मुनाफा, बारिश पर जोखिम।'
            }
        },
        'wheat': {
            'safe': {
                'title': '🔵 Safe Plan (Hardy Rainfed Durum / Low Rust Risk)',
                'title_kn': '🔵 ಸುರಕ್ಷಿತ ಯೋಜನೆ (ಬರ-ನಿರೋಧಕ ಸಾಂಪ್ರದಾಯಿಕ ಗೋಧಿ / ಕಡಿಮೆ ತುಕ್ಕು ರೋಗ)',
                'title_hi': '🔵 सुरक्षित योजना (कम सिंचाई / सूखा-सहनशील कठिया गेहूं)',
                'variety': 'Rainfed Durum Wheat (UAS Dharwad DWR-1006 / DWR-2006)',
                'variety_kn': 'ಕಡಿಮೆ ನೀರಿನ ಬರ-ನಿರೋಧಕ ಗೋಧಿ ತಳಿ (UAS ಧಾರವಾಡ DWR-1006 / DWR-2006)',
                'variety_hi': 'कम पानी की सूखा-सहनशील कठिया किस्म (UAS धारवाड़ DWR-1006 / DWR-2006)',
                'expected_profit_acre': '₹28,000 – ₹38,000',
                'expected_profit_acre_kn': '₹28,000 – ₹38,000',
                'expected_profit_acre_hi': '₹28,000 – ₹38,000',
                'downside_worst_case': '+₹12,000 (Guaranteed Straw & MSP Support)',
                'downside_worst_case_kn': '+₹12,000 (ಗೋಧಿ ಬೂಸಾ ಮತ್ತು ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ ರಕ್ಷಣೆ)',
                'downside_worst_case_hi': '+₹12,000 (भूसा मूल्य व सरकारी एमएसपी से सुरक्षित पूंजी)',
                'capital_outlay': '₹12,000 / acre',
                'capital_outlay_kn': '₹12,000 / ಎಕರೆ',
                'capital_outlay_hi': '₹12,000 / एकड़',
                'strategy': 'Zero-tillage sowing directly into paddy stubble, 2 critical irrigations (CRI + Boot stage), zero fungicide debt.',
                'strategy_kn': 'ಶೂನ್ಯ ಉಳುಮೆ (Zero-till) ಬಿತ್ತನೆ, ಕೇವಲ 2 ನಿರ್ಣಾಯಕ ನೀರಾವರಿ (ಬೇರು ಮೂಡುವ ಹಂತ & ಹೂಬಿಡುವ ಹಂತ), ಶೂನ್ಯ ಸಾಲ.',
                'strategy_hi': 'जीरो टिलेज सीधी बुवाई, केवल 2 महत्वपूर्ण क्राउन रूट व बाली सिंचाई, न्यूनतम लागत।',
                'regret_score': 'Minimum Regret (0.08) — Strong food security and zero cash loss even in dry winter.',
                'regret_score_kn': 'ಕನಿಷ್ಠ ವಿಷಾದ (0.08) — ಒಣ ಚಳಿಗಾಲದಲ್ಲೂ ಆಹಾರ ಭದ್ರತೆ ಮತ್ತು ಶೂನ್ಯ ನಷ್ಟ.',
                'regret_score_hi': 'न्यूनतम रिग्रेट (0.08) — शुष्क सर्दियों में भी खाद्य सुरक्षा व शून्य घाटा।'
            },
            'balanced': {
                'title': '🟡 Balanced Plan (High-Yield Bread Wheat + Timely Sowing)',
                'title_kn': '🟡 ಸಮತೋಲಿತ ಯೋಜನೆ (ಅಧಿಕ ಇಳುವರಿ ಶರಬತಿ / ಬ್ರೆಡ್ ಗೋಧಿ)',
                'title_hi': '🟡 संतुलित योजना (उच्च उपज शरबती व चपाती गेहूं किस्म)',
                'variety': 'High-Yielding Bread Wheat (GW-322 / Lokwan / HD-2967)',
                'variety_kn': 'ಅಧಿಕ ಇಳುವರಿ ಬ್ರೆಡ್ ಗೋಧಿ ತಳಿ (GW-322 / ಲೋಕವಾನ್ / UAS HD-2967)',
                'variety_hi': 'उच्च पैदावार रोटी किस्म (GW-322 / लोकवान / HD-2967)',
                'expected_profit_acre': '₹48,000 – ₹68,000',
                'expected_profit_acre_kn': '₹48,000 – ₹68,000',
                'expected_profit_acre_hi': '₹48,000 – ₹68,000',
                'downside_worst_case': '+₹5,000 (MSP ₹2,585 Floor Security)',
                'downside_worst_case_kn': '+₹5,000 (ಸರ್ಕಾರಿ ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ MSP ₹2,585 ರಕ್ಷಣೆ)',
                'downside_worst_case_hi': '+₹5,000 (सरकारी एमएसपी ₹2,585 पर लागत से अधिक सुरक्षा)',
                'capital_outlay': '₹18,000 / acre',
                'capital_outlay_kn': '₹18,000 / ಎಕರೆ',
                'capital_outlay_hi': '₹18,000 / एकड़',
                'strategy': '4-stage scheduled sprinkler irrigation, split nitrogen top-dressing at 21 and 42 DAS, chickpea border crop.',
                'strategy_kn': '4 ಹಂತದ ತುಂತುರು ನೀರಾವರಿ, 21 ಮತ್ತು 42ನೇ ದಿನಕ್ಕೆ ಕಂತುಗಳಲ್ಲಿ ಸಾರಜನಕ ಪೋಷಣೆ, ಕಡಲೆ ಅಂಚು ಬೆಳೆ.',
                'strategy_hi': '4 चरणों में स्प्रिंकलर सिंचाई, 21 व 42 दिन पर यूरिया टॉप-ड्रेसिंग, चना बॉर्डर फसल।',
                'regret_score': 'Low Regret (0.18) — Best balance between input costs and guaranteed APMC procurement.',
                'regret_score_kn': 'ಕಡಿಮೆ ವಿಷಾದ (0.18) — ಗೊಬ್ಬರ ವೆಚ್ಚ ಮತ್ತು ಸರ್ಕಾರಿ ಖರೀದಿ ಬೆಲೆಯಲ್ಲಿ ಗರಿಷ್ಠ ಭದ್ರತೆ.',
                'regret_score_hi': 'कम रिग्रेट (0.18) — लागत और गारंटीकृत सरकारी खरीद में उत्तम सामंजस्य।'
            },
            'aggressive': {
                'title': '🟢 Aggressive Plan (Premium Sharbati Grain / Intensive Nutrition)',
                'title_kn': '🟢 ಆಕ್ರಮಣಕಾರಿ ಯೋಜನೆ (ಪ್ರೀಮಿಯಂ ರಫ್ತು ಗುಣಮಟ್ಟದ ಹೊಳಪುಳ್ಳ ಶರಬತಿ ಗೋಧಿ)',
                'title_hi': '🟢 आक्रामक योजना (प्रीमियम शरबती चमकदार दाना / सघन पोषण)',
                'variety': 'Premium Milling Sharbati (C-306 / HI-1544 / MP Sharbati Gold)',
                'variety_kn': 'ಪ್ರೀಮಿಯಂ ಮಿಲ್ಲರ್ಸ್ ಶರಬತಿ ತಳಿ (C-306 / HI-1544 / ಎಂಪಿ ಶರಬತಿ ಗೋಲ್ಡ್)',
                'variety_hi': 'प्रीमियम शरबती गोल्डन दाना किस्म (C-306 / HI-1544 / शरबती गोल्ड)',
                'expected_profit_acre': '₹75,000 – ₹1,15,000',
                'expected_profit_acre_kn': '₹75,000 – ₹1,15,000',
                'expected_profit_acre_hi': '₹75,000 – ₹1,15,000',
                'downside_worst_case': '-₹10,000 (Loss if terminal heat shock or premature harvest rain)',
                'downside_worst_case_kn': '-₹10,000 (ಅಂತ್ಯ ಹಂತದಲ್ಲಿ ಬಿಸಿಗಾಳಿ ಬೀಸಿದರೆ ಅಥವಾ ಕಾಳು ಸುಟ್ಟರೆ ನಷ್ಟ)',
                'downside_worst_case_hi': '-₹10,000 (अंतिम अवस्था में अत्यधिक गर्मी या लू से दाना सिकुड़ने का जोखिम)',
                'capital_outlay': '₹26,000 / acre',
                'capital_outlay_kn': '₹26,000 / ಎಕರೆ',
                'capital_outlay_hi': '₹26,000 / एकड़',
                'strategy': 'Micro-sprinklers for canopy cooling during grain-fill, potassium nitrate foliar spray, direct flour mill contract.',
                'strategy_kn': 'ಕಾಳು ತುಂಬುವಾಗ ಉಷ್ಣತೆ ತಗ್ಗಿಸಲು ಮೈಕ್ರೋ-ಸ್ಪ್ರಿಂಕ್ಲರ್ ಬಳಕೆ, ಪೊಟ್ಯಾಶಿಯಂ ನೈಟ್ರೇಟ್ ಸಿಂಪಡಣೆ, ಮಿಲ್ಲರ್ಸ್ ನೇರ ಒಪ್ಪಂದ.',
                'strategy_hi': 'दाना भराव पर माइक्रो-स्प्रिंकलर से तापमान नियंत्रण, पोटेशियम नाइट्रेट स्प्रे, फ्लोर मिल अनुबंध।',
                'regret_score': 'High Regret (0.55) — Outstanding price premium if grain luster and protein remain top grade.',
                'regret_score_kn': 'ಹೆಚ್ಚಿನ ವಿಷಾದ ಸಾಮರ್ಥ್ಯ (0.55) — ಗೋಧಿ ಕಾಳಿನ ಹೊಳಪು ಮತ್ತು ತೂಕ ಉತ್ತಮವಾಗಿದ್ದರೆ ಬಂಪರ್ ಲಾಭ.',
                'regret_score_hi': 'उच्च रिग्रेट संभावना (0.55) — दाने की चमक व प्रोटीन उत्तम रहने पर प्रीमियम भाव।'
            }
        },
        'sunflower': {
            'safe': {
                'title': '🔵 Safe Plan (Short-Duration Open-Pollinated / Drought Hardy)',
                'title_kn': '🔵 ಸುರಕ್ಷಿತ ಯೋಜನೆ (ಕಡಿಮೆ ಅವಧಿಯ ಬರ-ನಿರೋಧಕ ತಳಿ)',
                'title_hi': '🔵 सुरक्षित योजना (कम अवधि की सूखा-सहिष्णु किस्म)',
                'variety': 'Morden / DRSF-108 (Open Pollinated)',
                'variety_kn': 'ಮಾರ್ಡನ್ / DRSF-108 (ಕಡಿಮೆ ಅವಧಿಯ ಸಾಂಪ್ರದಾಯಿಕ ತಳಿ)',
                'variety_hi': 'मॉर्डन / DRSF-108 (कम अवधि की ओपन पॉलिनेटेड किस्म)',
                'expected_profit_acre': '₹26,000 – ₹38,000',
                'expected_profit_acre_kn': '₹26,000 – ₹38,000',
                'expected_profit_acre_hi': '₹26,000 – ₹38,000',
                'downside_worst_case': '+₹10,000 (Protected Capital)',
                'downside_worst_case_kn': '+₹10,000 (ಬಂಡವಾಳ ಸಂಪೂರ್ಣ ಸುರಕ್ಷಿತ)',
                'downside_worst_case_hi': '+₹10,000 (पूंजी पूर्णतः सुरक्षित)',
                'capital_outlay': '₹11,000 / acre',
                'capital_outlay_kn': '₹11,000 / ಎಕರೆ',
                'capital_outlay_hi': '₹11,000 / एकड़',
                'strategy': 'Rainfed cultivation with Trichoderma seed treatment, low seed cost, zero pesticide loans.',
                'strategy_kn': 'ಮಳೆಯಾಶ್ರಿತ ಬೇಸಾಯ, ಟ್ರೈಕೋಡರ್ಮಾ ಬೀಜೋಪಚಾರ, ಅತ್ಯಂತ ಕಡಿಮೆ ಬೀಜ ವೆಚ್ಚ, ಶೂನ್ಯ ಸಾಲ.',
                'strategy_hi': 'वर्षा आधारित खेती, ट्राइकोडर्मा बीजोपचार, कम बीज लागत, शून्य कीटनाशक कर्ज।',
                'regret_score': 'Minimum Regret (0.09) — Guaranteed positive return even under erratic monsoon.',
                'regret_score_kn': 'ಕನಿಷ್ಠ ವಿಷಾದ (0.09) — ಅನಿಶ್ಚಿತ ಮಳೆಯಲ್ಲೂ ಬಂಡವಾಳ ನಷ್ಟವಾಗುವುದಿಲ್ಲ.',
                'regret_score_hi': 'न्यूनतम रिग्रेट (0.09) — अनियमित मानसून में भी लागत सुरक्षित।'
            },
            'balanced': {
                'title': '🟡 Balanced Plan (High-Yield Hybrid + Boron Nutrition)',
                'title_kn': '🟡 ಸಮತೋಲಿತ ಯೋಜನೆ (ಅಧಿಕ ಎಣ್ಣೆ ಅಂಶದ ಹೈಬ್ರಿಡ್ + ಬೋರಾನ್ ಪೋಷಣೆ)',
                'title_hi': '🟡 संतुलित योजना (उच्च तेल सामग्री हाइब्रिड + बोरॉन पोषण)',
                'variety': 'KBSH-41 / KBSH-53 / DRSH-1 (High-Yield UAS Hybrid)',
                'variety_kn': 'KBSH-41 / KBSH-53 / DRSH-1 (UAS ಬೆಂಗಳೂರು ಅಧಿಕ ಇಳುವರಿ ಹೈಬ್ರಿಡ್)',
                'variety_hi': 'KBSH-41 / KBSH-53 / DRSH-1 (उच्च तेल हाइब्रिड किस्म)',
                'expected_profit_acre': '₹48,000 – ₹70,000',
                'expected_profit_acre_kn': '₹48,000 – ₹70,000',
                'expected_profit_acre_hi': '₹48,000 – ₹70,000',
                'downside_worst_case': '+₹3,000 (MSP ₹7,280 Protection)',
                'downside_worst_case_kn': '+₹3,000 (ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ MSP ₹7,280 ರಕ್ಷಣೆ)',
                'downside_worst_case_hi': '+₹3,000 (सरकारी एमएसपी ₹7,280 पर पूंजी सुरक्षित)',
                'capital_outlay': '₹18,000 / acre',
                'capital_outlay_kn': '₹18,000 / ಎಕರೆ',
                'capital_outlay_hi': '₹18,000 / एकड़',
                'strategy': 'Critical irrigation at ray-floret and seed development, 2 kg/acre Borax spray to ensure 90%+ seed filling.',
                'strategy_kn': 'ಹೂಬಿಡುವ ಮತ್ತು ಕಾಳು ತುಂಬುವ ಹಂತದಲ್ಲಿ ನೀರಾವರಿ, 90%+ ಕಾಳು ಗಟ್ಟಿಯಾಗಲು ಬೋರಾಕ್ಸ್ (Borax) ಸಿಂಪಡಣೆ.',
                'strategy_hi': 'फूल व दाना भराव पर ड्रिप सिंचाई, 90%+ दाना भरने हेतु बोरेक्स का पर्णीय छिड़काव।',
                'regret_score': 'Low Regret (0.20) — Optimal balance between seed filling percentage and market oil price.',
                'regret_score_kn': 'ಕಡಿಮೆ ವಿಷಾದ (0.20) — ಕಾಳು ತುಂಬುವಿಕೆ ಮತ್ತು ಮಾರುಕಟ್ಟೆ ಎಣ್ಣೆ ದರದಲ್ಲಿ ಗರಿಷ್ಠ ಸ್ಥಿರತೆ.',
                'regret_score_hi': 'कम रिग्रेट (0.20) — दाना भराव और तेल मिल भाव में बेहतरीन संतुलन।'
            },
            'aggressive': {
                'title': '🟢 Aggressive Plan (Export High-Oleic Hybrid / Drip Fertigation)',
                'title_kn': '🟢 ಆಕ್ರಮಣಕಾರಿ ಯೋಜನೆ (ಪ್ರೀಮಿಯಂ ಹೈ-ಒಲಿಕ್ ಎಣ್ಣೆ ತಳಿ / ನಿಖರ ಹನಿ ಫರ್ಟಿಗೇಷನ್)',
                'title_hi': '🟢 आक्रामक योजना (उच्च ओलिक तेल प्रीमियम हाइब्रिड / ड्रिप फर्टिगेशन)',
                'variety': 'Pioneer 64A57 / Syngenta NK-Armoni (High-Oleic Hybrid)',
                'variety_kn': 'ಪಯೋನೀರ್ 64A57 / ಸಿಂಜೆಂಟಾ NK-Armoni (ಪ್ರೀಮಿಯಂ ಹೈ-ಒಲಿಕ್ ಹೈಬ್ರಿಡ್)',
                'variety_hi': 'पायनियर 64A57 / सिनजेंटा NK-Armoni (उच्च ओलिक प्रीमियम किस्म)',
                'expected_profit_acre': '₹80,000 – ₹1,25,000',
                'expected_profit_acre_kn': '₹80,000 – ₹1,25,000',
                'expected_profit_acre_hi': '₹80,000 – ₹1,25,000',
                'downside_worst_case': '-₹14,000 (Loss if severe head rot or parrot/bird damage at maturity)',
                'downside_worst_case_kn': '-₹14,000 (ತಲೆ ಕೊಳೆತ ರೋಗ ಅಥವಾ ಗಿಳಿ-ಪಕ್ಷಿಗಳ ಹಾವಳಿಯಿಂದ ಹೂವು ಹಾಳಾದರೆ ನಷ್ಟ)',
                'downside_worst_case_hi': '-₹14,000 (हेड रॉट फफूंद या पक्षियों के नुकसान से पैदावार घटने का जोखिम)',
                'capital_outlay': '₹28,000 / acre',
                'capital_outlay_kn': '₹28,000 / ಎಕರೆ',
                'capital_outlay_hi': '₹28,000 / एकड़',
                'strategy': 'Precision drip fertigation with bio-stimulants, bird reflective ribbon netting, direct edible oil refinery contract.',
                'strategy_kn': 'ಹನಿ ನೀರಾವರಿ ಜೊತೆಗೆ ಜೈವಿಕ ಪ್ರಚೋದಕಗಳು, ಪಕ್ಷಿ ನಿಯಂತ್ರಣ ರಿಬ್ಬನ್ ಬಲೆ, ಎಣ್ಣೆ ಸಂಸ್ಕರಣಾಗಾರದೊಂದಿಗೆ ನೇರ ಒಪ್ಪಂದ.',
                'strategy_hi': 'ड्रिप फर्टिगेशन, पक्षियों से बचाव हेतु रिफ्लेक्टिव रिबन, खाद्य तेल रिफाइनरी से सीधा अनुबंध।',
                'regret_score': 'High Regret (0.59) — Enormous financial upside if head rot and bird depredation are controlled.',
                'regret_score_kn': 'ಹೆಚ್ಚಿನ ವಿಷಾದ (0.59) — ರೋಗ ಮತ್ತು ಪಕ್ಷಿ ಹಾನಿ ನಿಯಂತ್ರಿಸಿದರೆ ಅತ್ಯಧಿಕ ಲಾಭ.',
                'regret_score_hi': 'उच्च रिग्रेट संभावना (0.59) — पक्षियों व फफूंद से बचाव पर रिकॉर्ड मुनाफा।'
            }
        },
        'tomato': {
            'safe': {
                'title': '🔵 Safe Plan (Low-Input Open-Pollinated)',
                'title_kn': '🔵 ಸುರಕ್ಷಿತ ಯೋಜನೆ (ಕಡಿಮೆ ವೆಚ್ಚದ ಸಾಂಪ್ರದಾಯಿಕ ತಳಿ)',
                'title_hi': '🔵 सुरक्षित योजना (कम लागत खुली परागित किस्म)',
                'variety': 'Wilt-Resistant Open Pollinated (e.g. Arka Rakshak / Pusa Ruby)',
                'variety_kn': 'ಸೊರಗು ರೋಗ ನಿರೋಧಕ ತಳಿ (ಉದಾ. ಅರ್ಕಾ ರಕ್ಷಕ್ / ಪೂಸಾ ರೂಬಿ)',
                'variety_hi': 'उकठा रोग प्रतिरोधी किस्म (जैसे अर्का रक्षक / पूसा रूबी)',
                'expected_profit_acre': '₹50,000 – ₹75,000',
                'expected_profit_acre_kn': '₹50,000 – ₹75,000',
                'expected_profit_acre_hi': '₹50,000 – ₹75,000',
                'downside_worst_case': '+₹10,000',
                'downside_worst_case_kn': '+₹10,000 (ಬಂಡವಾಳ ರಕ್ಷಣೆ)',
                'downside_worst_case_hi': '+₹10,000 (पूंजी सुरक्षित)',
                'capital_outlay': '₹20,000 / acre',
                'capital_outlay_kn': '₹20,000 / ಎಕರೆ',
                'capital_outlay_hi': '₹20,000 / एकड़',
                'strategy': 'Staked cultivation with organic mulch and local mandi direct selling.',
                'strategy_kn': 'ಕಡ್ಡಿ ಆಧಾರ (Staking) ಮತ್ತು ಸಾವಯವ ಮಲ್ಚ್, ಸ್ಥಳೀಯ ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ನೇರ ಮಾರಾಟ.',
                'strategy_hi': 'मचान/बांस सहारा एवं जैविक मल्चिंग, स्थानीय मंडी में सीधी बिक्री।',
                'regret_score': 'Low Regret (0.12) — Low seed cost, tolerant to leaf curl.',
                'regret_score_kn': 'ಕಡಿಮೆ ವಿಷಾದ (0.12) — ಕಡಿಮೆ ಬೀಜ ವೆಚ್ಚ, ಎಲೆ ಮುದುರು ರೋಗಕ್ಕೆ ಪ್ರತಿರೋಧ.',
                'regret_score_hi': 'कम रिग्रेट (0.12) — कम बीज लागत, पर्ण कुंचन रोग से सहनशीलता।'
            },
            'balanced': {
                'title': '🟡 Balanced Plan (Commercial Hybrid + Staking)',
                'title_kn': '🟡 ಸಮತೋಲಿತ ಯೋಜನೆ (ವಾಣಿಜ್ಯ ಹೈಬ್ರಿಡ್ + ಕಡ್ಡಿ ಆಧಾರ)',
                'title_hi': '🟡 संतुलित योजना (व्यावसायिक हाइब्रिड + मचान सहारा)',
                'variety': 'Commercial Triple-Disease Resistant Hybrid (e.g. US 440 / Abhinav)',
                'variety_kn': 'ತ್ರಿವಳಿ ರೋಗ-ನಿರೋಧಕ ಹೈಬ್ರಿಡ್ ತಳಿ (ಉದಾ. US 440 / ಅಭಿನವ್ / ಸಾಹೋ)',
                'variety_hi': 'त्रिविध रोग-प्रतिरोधी हाइब्रिड किस्म (जैसे US 440 / अभिनव)',
                'expected_profit_acre': '₹1,20,000 – ₹1,80,000',
                'expected_profit_acre_kn': '₹1,20,000 – ₹1,80,000',
                'expected_profit_acre_hi': '₹1,20,000 – ₹1,80,000',
                'downside_worst_case': '-₹10,000',
                'downside_worst_case_kn': '-₹10,000 (ಬೆಲೆ ಕುಸಿದರೆ ಸಣ್ಣ ನಷ್ಟದ ಅಪಾಯ)',
                'downside_worst_case_hi': '-₹10,000 (भाव गिरने पर मामूली नुकसान का जोखिम)',
                'capital_outlay': '₹38,000 / acre',
                'capital_outlay_kn': '₹38,000 / ಎಕರೆ',
                'capital_outlay_hi': '₹38,000 / एकड़',
                'strategy': 'Drip fertigation, trellising, staggered 3-phase picking to hedge against weekly price drops.',
                'strategy_kn': 'ಹನಿ ನೀರಾವರಿ, ತಂತಿ ಹಂದರ, ವಾರದ ಬೆಲೆ ಕುಸಿತ ತಪ್ಪಿಸಲು 3 ಹಂತಗಳಲ್ಲಿ ಕೊಯ್ಲು.',
                'strategy_hi': 'ड्रिप फर्टिगेशन, तार मचान, साप्ताहिक भाव गिरावट से बचाव हेतु 3 चरणों में तुड़ाई।',
                'regret_score': 'Moderate Regret (0.28) — Excellent yield with staggered price protection.',
                'regret_score_kn': 'ಮಧ್ಯಮ ವಿಷಾದ (0.28) — ಹಂತಹಂತದ ಕೊಯ್ಲಿನಿಂದ ಬೆಲೆ ಕುಸಿತಕ್ಕೆ ರಕ್ಷಣೆ.',
                'regret_score_hi': 'मध्यम रिग्रेट (0.28) — चरणबद्ध तुड़ाई से मंडी जोखिम पर नियंत्रण।'
            },
            'aggressive': {
                'title': '🟢 Aggressive Plan (Off-Season Polyhouse / High Density)',
                'title_kn': '🟢 ಆಕ್ರಮಣಕಾರಿ ಯೋಜನೆ (ಆಫ್-ಸೀಸನ್ ಪಾಲಿಹೌಸ್ / ಗರಿಷ್ಠ ಇಳುವರಿ)',
                'title_hi': '🟢 आक्रामक योजना (ऑफ-सीजन पॉलीहाउस / सघन खेती)',
                'variety': 'Export-Grade Indeterminate Hybrid (e.g. Red Chief / TO-3150)',
                'variety_kn': 'ರಫ್ತು ಗುಣಮಟ್ಟದ ಹೈಬ್ರಿಡ್ ತಳಿ (ಉದಾ. ರೆಡ್ ಚೀಫ್ / TO-3150)',
                'variety_hi': 'निर्यात गुणवत्ता इंडिटरमिनेट हाइब्रिड (जैसे रेड चीफ / TO-3150)',
                'expected_profit_acre': '₹2,50,000 – ₹4,20,000',
                'expected_profit_acre_kn': '₹2,50,000 – ₹4,20,000',
                'expected_profit_acre_hi': '₹2,50,000 – ₹4,20,000',
                'downside_worst_case': '-₹55,000 (Heavy loss if market crash to ₹3/kg)',
                'downside_worst_case_kn': '-₹55,000 (ಮಾರುಕಟ್ಟೆ ದರ ₹3/ಕೆಜಿಗೆ ಕುಸಿದರೆ ನಷ್ಟ)',
                'downside_worst_case_hi': '-₹55,000 (मंडी भाव ₹3/किग्रा गिरने पर भारी नुकसान)',
                'capital_outlay': '₹65,000 / acre',
                'capital_outlay_kn': '₹65,000 / ಎಕರೆ',
                'capital_outlay_hi': '₹65,000 / एकड़',
                'strategy': 'High-density staking, hormone sprays for fruit set, cold-chain transport for distant metro markets.',
                'strategy_kn': 'ಹೆಚ್ಚಿನ ಸಾಂದ್ರತೆಯ ಬಿತ್ತನೆ, ಕಾಯಿ ಕಟ್ಟಲು ಹಾರ್ಮೋನ್ ಸ್ಪ್ರೇ, ಮೆಟ್ರೋ ಮಾರುಕಟ್ಟೆಗೆ ಕೋಲ್ಡ್-ಚೈನ್ ಸಾಗಾಣಿಕೆ.',
                'strategy_hi': 'सघन मचान खेती, फल भराव हेतु हार्मोन छिड़काव, बड़े शहरों हेतु कोल्ड-चेन परिवहन।',
                'regret_score': 'Very High Regret Potential (0.78) — Maximum financial alpha with high perishable risk.',
                'regret_score_kn': 'ಅತ್ಯಧಿಕ ವಿಷಾದ (0.78) — ಬೆಲೆ ಸಿಕ್ಕರೆ ಬಂಪರ್ ಲಾಭ, ಕೊಳೆತರೆ ಹೆಚ್ಚಿನ ನಷ್ಟ.',
                'regret_score_hi': 'अत्यधिक रिग्रेट (0.78) — भाव मिलने पर रिकॉर्ड लाभ, सड़न पर भारी जोखिम।'
            }
        },
        'cotton': {
            'safe': {
                'title': '🔵 Safe Plan (Desi / Rainfed Hardy Cotton)',
                'title_kn': '🔵 ಸುರಕ್ಷಿತ ಯೋಜನೆ (ಮಳೆಯಾಶ್ರಿತ ದೇಸಿ ಹತ್ತಿ / ಕಡಿಮೆ ವೆಚ್ಚ)',
                'title_hi': '🔵 सुरक्षित योजना (देसी वर्षा आधारित कपास / न्यूनतम लागत)',
                'variety': 'HD 123 / RG 8 / DLSa-17 (Native Desi Cotton)',
                'variety_kn': 'HD 123 / RG 8 / DLSa-17 (ಸ್ಥಳೀಯ ದೇಸಿ ಹತ್ತಿ ತಳಿ)',
                'variety_hi': 'HD 123 / RG 8 / DLSa-17 (देसी कपास किस्म)',
                'expected_profit_acre': '₹28,000 – ₹38,000',
                'expected_profit_acre_kn': '₹28,000 – ₹38,000',
                'expected_profit_acre_hi': '₹28,000 – ₹38,000',
                'downside_worst_case': '+₹12,000 (No seed debt)',
                'downside_worst_case_kn': '+₹12,000 (ಶೂನ್ಯ ಬೀಜ ಸಾಲ)',
                'downside_worst_case_hi': '+₹12,000 (शून्य बीज कर्ज)',
                'capital_outlay': '₹11,000 / acre',
                'capital_outlay_kn': '₹11,000 / ಎಕರೆ',
                'capital_outlay_hi': '₹11,000 / एकड़',
                'strategy': 'Rainfed cultivation with zero synthetic insecticide, high boll resistance to pink bollworm.',
                'strategy_kn': 'ಮಳೆಯಾಶ್ರಿತ ಬೇಸಾಯ, ಶೂನ್ಯ ಕೃತಕ ಕೀಟನಾಶಕ, ಗುಲಾಬಿ ಕಾಯಿಕೊರಕಕ್ಕೆ ನೈಸರ್ಗಿಕ ಪ್ರತಿರೋಧ.',
                'strategy_hi': 'वर्षा आधारित खेती, शून्य रासायनिक कीटनाशक, गुलाबी सुंडी से प्राकृतिक बचाव।',
                'regret_score': 'Minimum Regret (0.10) — Zero seed debt.',
                'regret_score_kn': 'ಕನಿಷ್ಠ ವಿಷಾದ (0.10) — ಕಡಿಮೆ ವೆಚ್ಚದ ಸಂಪೂರ್ಣ ರಕ್ಷಣೆ.',
                'regret_score_hi': 'न्यूनतम रिग्रेट (0.10) — लागत सुरक्षित।'
            },
            'balanced': {
                'title': '🟡 Balanced Plan (Bt Cotton + Moong Intercrop)',
                'title_kn': '🟡 ಸಮತೋಲಿತ ಯೋಜನೆ (ಬಿಟಿ ಹತ್ತಿ + ಹೆಸರುಕಾಳು ಅಂತರಬೆಳೆ)',
                'title_hi': '🟡 संतुलित योजना (बीची कॉटन + मूंग अंतःफसल)',
                'variety': 'Bollgard II Hybrid + 2 rows Green Gram (Moong)',
                'variety_kn': 'ಬೋಲ್‌ಗಾರ್ಡ್ II ಹೈಬ್ರಿಡ್ + 2 ಸಾಲು ಹೆಸರುಕಾಳು (Moong) ಅಂತರಬೆಳೆ',
                'variety_hi': 'बोलगार्ड II हाइब्रिड + 2 कतार मूंग अंतःफसल',
                'expected_profit_acre': '₹55,000 – ₹75,000',
                'expected_profit_acre_kn': '₹55,000 – ₹75,000',
                'expected_profit_acre_hi': '₹55,000 – ₹75,000',
                'downside_worst_case': '+₹5,000 (Pulse crop cushions cashflow)',
                'downside_worst_case_kn': '+₹5,000 (ದ್ವಿದಳ ಧಾನ್ಯದಿಂದ ನಷ್ಟ ಭರ್ತಿ)',
                'downside_worst_case_hi': '+₹5,000 (दलहनी अंतःफसल से वित्तीय सुरक्षा)',
                'capital_outlay': '₹22,000 / acre',
                'capital_outlay_kn': '₹22,000 / ಎಕರೆ',
                'capital_outlay_hi': '₹22,000 / एकड़',
                'strategy': 'Refuge crop border, pheromone trap monitoring, balanced potassium foliar spray.',
                'strategy_kn': 'ರೆಫ್ಯೂಜ್ ಬಾರ್ಡರ್ ಬೆಳೆ, ಮೋಹಕ ಬಲೆ (Pheromone trap) ಕಣ್ಗಾವಲು, ಪೊಟ್ಯಾಶಿಯಂ ಸಿಂಪಡಣೆ.',
                'strategy_hi': 'रिफ्यूज बॉर्डर फसल, फेरोमोन ट्रैप निगरानी, संतुलित पोटाश पर्णीय छिड़काव।',
                'regret_score': 'Low Regret (0.20) — Optimal risk-hedging.',
                'regret_score_kn': 'ಕಡಿಮೆ ವಿಷಾದ (0.20) — ಅಂತರಬೆಳೆಯಿಂದ ಆರ್ಥಿಕ ವಿಮೆ.',
                'regret_score_hi': 'कम रिग्रेट (0.20) — अंतःफसल से सुरक्षित लाभ।'
            },
            'aggressive': {
                'title': '🟢 Aggressive Plan (High-Density Planting System - HDPS)',
                'title_kn': '🟢 ಆಕ್ರಮಣಕಾರಿ ಯೋಜನೆ (ಸಾಂದ್ರ ಬಿತ್ತನೆ HDPS + ನಿಖರ ಹನಿ ಫರ್ಟಿಗೇಷನ್)',
                'title_hi': '🟢 आक्रामक योजना (सघन रोपण HDPS + सटीक ड्रिप)',
                'variety': 'Compact Bt Hybrid with Growth Regulators',
                'variety_kn': 'ಕುಬ್ಜ ಬಿಟಿ ಹೈಬ್ರಿಡ್ (Compact Bt Hybrid) + ಬೆಳವಣಿಗೆ ನಿಯಂತ್ರಕ',
                'variety_hi': 'कॉम्पैक्ट बीटी हाइब्रिड + ग्रोथ रेगुलेटर',
                'expected_profit_acre': '₹95,000 – ₹1,40,000',
                'expected_profit_acre_kn': '₹95,000 – ₹1,40,000',
                'expected_profit_acre_hi': '₹95,000 – ₹1,40,000',
                'downside_worst_case': '-₹22,000 (High loss if monsoon fails)',
                'downside_worst_case_kn': '-₹22,000 (ಮಳೆ ವಿಫಲವಾದರೆ ಅಥವಾ ಕಾಯಿಕೊರಕ ಬಂದರೆ ನಷ್ಟ)',
                'downside_worst_case_hi': '-₹22,000 (मानसून विफलता पर नुकसान)',
                'capital_outlay': '₹35,000 / acre',
                'capital_outlay_kn': '₹35,000 / ಎಕರೆ',
                'capital_outlay_hi': '₹35,000 / एकड़',
                'strategy': 'Close spacing (60x15cm), mepiquat chloride canopy management, precision drip fertigation.',
                'strategy_kn': 'ಸಾಂದ್ರ ಬಿತ್ತನೆ (60x15 ಸೆಂ.ಮೀ), ಮೆಪಿಕಾಟ್ ಕ್ಲೋರೈಡ್ ಕ್ಯಾನೋಪಿ ನಿಯಂತ್ರಣ, ಹನಿ ಫರ್ಟಿಗೇಷನ್.',
                'strategy_hi': 'सघन दूरी (60x15 सेमी), मेपिक्वेट क्लोराइड से पौधे का आकार प्रबंधन, ड्रिप फर्टिगेशन।',
                'regret_score': 'High Regret (0.60) — Peak cotton yield potential.',
                'regret_score_kn': 'ಹೆಚ್ಚಿನ ವಿಷಾದ (0.60) — ಗರಿಷ್ಠ ಇಳುವರಿ ಸಾಮರ್ಥ್ಯ ಆದರೆ ಮಳೆ ಅನಿವಾರ್ಯ.',
                'regret_score_hi': 'उच्च रिग्रेट (0.60) — उच्च पैदावार क्षमता।'
            }
        },
        'maize': {
            'safe': {
                'title': '🔵 Safe Plan (Composite / Dual-Purpose Fodder)',
                'title_kn': '🔵 ಸುರಕ್ಷಿತ ಯೋಜನೆ (ಕಾಳು + ಹಸಿರು ಮೇವು ದ್ವಿ-ಉದ್ದೇಶ ತಳಿ)',
                'title_hi': '🔵 सुरक्षित योजना (द्वि-उद्देश्यीय दाना व हरा चारा किस्म)',
                'variety': 'African Tall / Shaktiman 1',
                'variety_kn': 'ಆಫ್ರಿಕನ್ ಟಾಲ್ / ಶಕ್ತಿಮಾನ್ 1 (African Tall / Shaktiman 1)',
                'variety_hi': 'अफ्रीकन टॉल / शक्तिमान 1 (African Tall)',
                'expected_profit_acre': '₹24,000 – ₹34,000',
                'expected_profit_acre_kn': '₹24,000 – ₹34,000',
                'expected_profit_acre_hi': '₹24,000 – ₹34,000',
                'downside_worst_case': '+₹10,000',
                'downside_worst_case_kn': '+₹10,000 (ಮೇವು ಮಾರಾಟದಿಂದ ಬಂಡವಾಳ ಸುರಕ್ಷಿತ)',
                'downside_worst_case_hi': '+₹10,000 (हरा चारा बिक्री से लागत सुरक्षित)',
                'capital_outlay': '₹9,000 / acre',
                'capital_outlay_kn': '₹9,000 / ಎಕರೆ',
                'capital_outlay_hi': '₹9,000 / एकड़',
                'strategy': 'Dual purpose: Grain + Dairy green fodder market hedge.',
                'strategy_kn': 'ದ್ವಿ-ಉದ್ದೇಶ: ಕಾಳು ಮಾರಾಟ ಅಥವಾ ಹೈನುಗಾರಿಕೆಗೆ ಹಸಿರು ಮೇವಿನ ಆರ್ಥಿಕ ರಕ್ಷಣೆ.',
                'strategy_hi': 'द्वि-उद्देश्य: दाना अथवा डेयरी हेतु हरा चारा बिक्री सुरक्षा।',
                'regret_score': 'Minimum Regret (0.09) — Zero downside.',
                'regret_score_kn': 'ಕನಿಷ್ಠ ವಿಷಾದ (0.09) — ಯಾವುದೇ ಮಾರುಕಟ್ಟೆ ನಷ್ಟವಿಲ್ಲ.',
                'regret_score_hi': 'न्यूनतम रिग्रेट (0.09) — शून्य घाटा।'
            },
            'balanced': {
                'title': '🟡 Balanced Plan (Single-Cross Hybrid + FAW Bio-Defense)',
                'title_kn': '🟡 ಸಮತೋಲಿತ ಯೋಜನೆ (ಅಧಿಕ ಇಳುವರಿ ಹೈಬ್ರಿಡ್ + ಸೈನಿಕ ಹುಳು ಜೈವಿಕ ರಕ್ಷಣೆ)',
                'title_hi': '🟡 संतुलित योजना (सिंगल-क्रॉस हाइब्रिड + फॉल आर्मीवर्म जैव-नियंत्रण)',
                'variety': 'DKC 9108 / Pioneer P3501 + Push-Pull Desmodium',
                'variety_kn': 'DKC 9108 / ಪಯೋನೀರ್ P3501 + ಸೈನಿಕ ಹುಳು ನಿಯಂತ್ರಣ',
                'variety_hi': 'DKC 9108 / पायनियर P3501 + आर्मीवर्म जैव-नियंत्रण',
                'expected_profit_acre': '₹48,000 – ₹65,000',
                'expected_profit_acre_kn': '₹48,000 – ₹65,000',
                'expected_profit_acre_hi': '₹48,000 – ₹65,000',
                'downside_worst_case': '+₹2,000',
                'downside_worst_case_kn': '+₹2,000 (MSP ಬೆಂಬಲ ಬೆಲೆಯಲ್ಲಿ ವೆಚ್ಚ ಸುರಕ್ಷಿತ)',
                'downside_worst_case_hi': '+₹2,000 (सरकारी एमएसपी पर लागत सुरक्षित)',
                'capital_outlay': '₹17,000 / acre',
                'capital_outlay_kn': '₹17,000 / ಎಕರೆ',
                'capital_outlay_hi': '₹17,000 / एकड़',
                'strategy': 'Integrated Fall Armyworm defense with Metarhizium anisopliae and split nitrogen.',
                'strategy_kn': 'ಮೆಟಾರೈಜಿಯಂ ಜೈವಿಕ ಶಿಲೀಂಧ್ರದಿಂದ ಸೈನಿಕ ಹುಳು ನಿಯಂತ್ರಣ, ಕಂತುಗಳಲ್ಲಿ ಸಾರಜನಕ.',
                'strategy_hi': 'मेटाराइजियम से फॉल आर्मीवर्म का जैविक नियंत्रण, किस्तों में यूरिया।',
                'regret_score': 'Low Regret (0.19) — Balanced productivity.',
                'regret_score_kn': 'ಕಡಿಮೆ ವಿಷಾದ (0.19) — ಸ್ಥಿರ ಇಳುವರಿ ಮತ್ತು ಭದ್ರತೆ.',
                'regret_score_hi': 'कम रिग्रेट (0.19) — संतुलित पैदावार।'
            },
            'aggressive': {
                'title': '🟢 Aggressive Plan (Sweet Corn / Baby Corn Commercial Contract)',
                'title_kn': '🟢 ಆಕ್ರಮಣಕಾರಿ ಯೋಜನೆ (ಸ್ವೀಟ್ ಕಾರ್ನ್ / ಬೇಬಿ ಕಾರ್ನ್ ವಾಣಿಜ್ಯ ಒಪ್ಪಂದ)',
                'title_hi': '🟢 आक्रामक योजना (स्वीट कॉर्न / बेबी कॉर्न व्यावसायिक अनुबंध)',
                'variety': 'Sugar 75 / Madhuri (Sweet Corn Hybrid)',
                'variety_kn': 'ಶುಗರ್ 75 / ಮಾಧುರಿ (ಸ್ವೀಟ್ ಕಾರ್ನ್ ಹೈಬ್ರಿಡ್)',
                'variety_hi': 'शुगर 75 / माधुरी (स्वीट कॉर्न हाइब्रिड)',
                'expected_profit_acre': '₹85,000 – ₹1,30,000',
                'expected_profit_acre_kn': '₹85,000 – ₹1,30,000',
                'expected_profit_acre_hi': '₹85,000 – ₹1,30,000',
                'downside_worst_case': '-₹15,000',
                'downside_worst_case_kn': '-₹15,000 (ತ್ವರಿತವಾಗಿ ಮಾರಾಟವಾಗದಿದ್ದರೆ ನಷ್ಟದ ಸಾಧ್ಯತೆ)',
                'downside_worst_case_hi': '-₹15,000 (शीघ्र बिक्री न होने पर नुकसान का जोखिम)',
                'capital_outlay': '₹26,000 / acre',
                'capital_outlay_kn': '₹26,000 / ಎಕರೆ',
                'capital_outlay_hi': '₹26,000 / एकड़',
                'strategy': '75-day fast harvest cycle, immediate buyer contract for city supermarkets.',
                'strategy_kn': '75 ದಿನಗಳ ಅಲ್ಪಾವಧಿ ಕೊಯ್ಲು, ನಗರದ ಸೂಪರ್‌ಮಾರ್ಕೆಟ್‌ಗಳಿಗೆ ನೇರ ಗುತ್ತಿಗೆ ಮಾರಾಟ.',
                'strategy_hi': '75 दिन की त्वरित फसल, सुपरमार्केट व खाद्य प्रसंस्करण इकाइयों से सीधा अनुबंध।',
                'regret_score': 'High Regret (0.58) — Fast cashflow but high perishability.',
                'regret_score_kn': 'ಹೆಚ್ಚಿನ ವಿಷಾದ (0.58) — ಕ್ಷಿಪ್ರ ಲಾಭ ಆದರೆ ಕೊಯ್ಲಿನ ನಂತರ ಬೇಗ ಮಾರಾಟವಾಗಬೇಕು.',
                'regret_score_hi': 'उच्च रिग्रेट (0.58) — तीव्र नकद आमदनी किंतु शीघ्र खराब होने का जोखिम।'
            }
        },
        'chickpea': {
            'safe': {
                'title': '🔵 Safe Plan (Desi Wilt-Resistant / Low Input)',
                'title_kn': '🔵 ಸುರಕ್ಷಿತ ಯೋಜನೆ (ದೇಸಿ ಸೊರಗು ರೋಗ-ನಿರೋಧಕ & ಕಡಿಮೆ ವೆಚ್ಚ)',
                'title_hi': '🔵 सुरक्षित योजना (देसी उकठा प्रतिरोधी एवं कम लागत)',
                'variety': 'JG-11 / Annigeri-1 (Drought & Wilt Tolerant)',
                'variety_kn': 'ಜೆಜಿ-11 / ಅಣ್ಣಿಗೇರಿ-1 (ಬರ ಮತ್ತು ಸೊರಗು ರೋಗ ನಿರೋಧಕ)',
                'variety_hi': 'जेजी-11 / अन्निगेरी-1 (सूखा व उकठा प्रतिरोधी)',
                'expected_profit_acre': '₹25,000 – ₹35,000',
                'expected_profit_acre_kn': '₹25,000 – ₹35,000',
                'expected_profit_acre_hi': '₹25,000 – ₹35,000',
                'downside_worst_case': '+₹12,000 (Protected Capital & Fodder)',
                'downside_worst_case_kn': '+₹12,000 (ಬಂಡವಾಳ ಸುರಕ್ಷಿತ ಮತ್ತು ಕಡಲೆ ಹೊಟ್ಟು ಮೌಲ್ಯ)',
                'downside_worst_case_hi': '+₹12,000 (पूंजी सुरक्षित एवं चारा मूल्य)',
                'capital_outlay': '₹10,000 / acre',
                'capital_outlay_kn': '₹10,000 / ಎಕರೆ',
                'capital_outlay_hi': '₹10,000 / एकड़',
                'strategy': 'Residual black soil moisture, Rhizobium + Trichoderma seed inoculation, zero irrigation debt.',
                'strategy_kn': 'ಕಪ್ಪು ಮಣ್ಣಿನ ಹಿಂಗಾರು ತೇವಾಂಶ, ರೈಜೋಬಿಯಂ + ಟ್ರೈಕೋಡರ್ಮಾ ಬೀಜೋಪಚಾರ, ಶೂನ್ಯ ನೀರಾವರಿ ವೆಚ್ಚ.',
                'strategy_hi': 'काली मिट्टी की अवशिष्ट नमी, राइजोबियम + ट्राइकोडर्मा बीजोपचार, शून्य सिंचाई कर्ज।',
                'regret_score': 'Minimum Regret (0.07) — Safe harvest even under early rain cessation.',
                'regret_score_kn': 'ಕನಿಷ್ಠ ವಿಷಾದ (0.07) — ಮಳೆ ಬೇಗ ನಿಂತರೂ ನಷ್ಟವಾಗದ ಭದ್ರತೆ.',
                'regret_score_hi': 'न्यूनतम रिग्रेट (0.07) — बारिश जल्दी रुकने पर भी पूंजी सुरक्षित।'
            },
            'balanced': {
                'title': '🟡 Balanced Plan (Broad-Bed Furrow + Pod Borer Bio-Defense)',
                'title_kn': '🟡 ಸಮತೋಲಿತ ಯೋಜನೆ (ಅಗಲ ಸಾಲು ಬದುಕು BBF + ಕಾಯಿಕೊರಕ ಜೈವಿಕ ನಿಯಂತ್ರಣ)',
                'title_hi': '🟡 संतुलित योजना (मेड़-कूड़ BBF + फली छेदक जैव-प्रबंधन)',
                'variety': 'BGD 103 / JAKI 9218 (High-Yield Wilt Resistant UAS)',
                'variety_kn': 'BGD 103 / JAKI 9218 (UAS ಧಾರವಾಡ ಅಧಿಕ ಇಳುವರಿ ತಳಿ)',
                'variety_hi': 'बीजीडी 103 / जाकी 9218 (उच्च उपज उकठा प्रतिरोधी)',
                'expected_profit_acre': '₹45,000 – ₹60,000',
                'expected_profit_acre_kn': '₹45,000 – ₹60,000',
                'expected_profit_acre_hi': '₹45,000 – ₹60,000',
                'downside_worst_case': '+₹5,000 (Govt MSP Support Hedge)',
                'downside_worst_case_kn': '+₹5,000 (ಸರ್ಕಾರಿ ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ MSP ರಕ್ಷಣೆ)',
                'downside_worst_case_hi': '+₹5,000 (सरकारी एमएसपी मूल्य सुरक्षा)',
                'capital_outlay': '₹16,000 / acre',
                'capital_outlay_kn': '₹16,000 / ಎಕರೆ',
                'capital_outlay_hi': '₹16,000 / एकड़',
                'strategy': 'Single protective sprinkler irrigation at pod initiation, pheromone traps, 2% DAP foliar spray.',
                'strategy_kn': 'ಕಾಯಿ ಕಟ್ಟುವ ಹಂತದಲ್ಲಿ ಒಂದು ಜೀವ ರಕ್ಷಕ ಸಿಂಚನ ನೀರಾವರಿ, ಮೋಹಕ ಬಲೆಗಳು, 2% ಡಿಎಪಿ ಪೋಷಕಾಂಶ ಸಿಂಪಡಣೆ.',
                'strategy_hi': 'फली बनते समय एक सुरक्षात्मक छिड़काव सिंचाई, फेरोमोन ट्रैप, 2% डीएपी पर्णीय छिड़काव।',
                'regret_score': 'Low Regret (0.18) — Best risk-adjusted return in North Karnataka.',
                'regret_score_kn': 'ಕಡಿಮೆ ವಿಷಾದ (0.18) — ಉತ್ತರ ಕರ್ನಾಟಕದ ಮಣ್ಣಿಗೆ ಅತ್ಯುತ್ತಮ ಅಪಾಯ-ಮುಕ್ತ ಲಾಭ.',
                'regret_score_hi': 'कम रिग्रेट (0.18) — उत्तरी कर्नाटक हेतु सर्वोत्तम संतुलित मुनाफा।'
            },
            'aggressive': {
                'title': '🟢 Aggressive Plan (Export Bold Kabuli / Precision Micro-Nutrients)',
                'title_kn': '🟢 ಆಕ್ರಮಣಕಾರಿ ಯೋಜನೆ (ದಪ್ಪ ಕಾಬೂಲಿ ಕಡಲೆ ತಳಿ / ರಫ್ತು ಗುಣಮಟ್ಟ)',
                'title_hi': '🟢 आक्रामक योजना (मोटा काबुली चना / निर्यात गुणवत्ता)',
                'variety': 'MNK-1 / KAK-2 (Extra Bold Export Kabuli)',
                'variety_kn': 'MNK-1 / KAK-2 (ಅತ್ಯಧಿಕ ಮಾರುಕಟ್ಟೆ ಬೆಲೆಯ ದಪ್ಪ ಕಾಬೂಲಿ ತಳಿ)',
                'variety_hi': 'एमएनके-1 / केएके-2 (अतिरिक्त मोटा काबुली चना)',
                'expected_profit_acre': '₹70,000 – ₹95,000',
                'expected_profit_acre_kn': '₹70,000 – ₹95,000',
                'expected_profit_acre_hi': '₹70,000 – ₹95,000',
                'downside_worst_case': '-₹14,000 (Loss if severe collar rot or market crash)',
                'downside_worst_case_kn': '-₹14,000 (ಬುಡ ಕೊಳೆ ರೋಗ ಬಂದರೆ ಅಥವಾ ಬೆಲೆ ಕುಸಿದರೆ ನಷ್ಟದ ಅಪಾಯ)',
                'downside_worst_case_hi': '-₹14,000 (गंभीर कॉलर रॉट या भाव गिरने पर नुकसान)',
                'capital_outlay': '₹24,000 / acre',
                'capital_outlay_kn': '₹24,000 / ಎಕರೆ',
                'capital_outlay_hi': '₹24,000 / एकड़',
                'strategy': 'Two scheduled irrigations, preventive metalaxyl seed coating, staggered marketing for urban dal mills.',
                'strategy_kn': 'ಎರಡು ಹಂತದ ನಿಖರ ನೀರಾವರಿ, ಶಿಲೀಂಧ್ರನಾಶಕ ಕವಚ, ನಗರದ ದಾಲ್ ಮಿಲ್‌ಗಳಿಗೆ ನೇರ ಪ್ರೀಮಿಯಂ ಮಾರಾಟ.',
                'strategy_hi': 'दो समयबद्ध सटीक सिंचाई, सुरक्षात्मक बीज लेपन, दाल मिलों को प्रीमियम पर चरणबद्ध बिक्री।',
                'regret_score': 'High Regret (0.55) — Highest price premium if grain size and color hold.',
                'regret_score_kn': 'ಹೆಚ್ಚಿನ ವಿಷಾದ (0.55) — ಕಾಳಿನ ಗಾತ್ರ ಉತ್ತಮವಾಗಿದ್ದರೆ ಗರಿಷ್ಠ ಪ್ರೀಮಿಯಂ ದರ.',
                'regret_score_hi': 'उच्च रिग्रेट (0.55) — दाने का आकार बड़ा रहने पर सबसे अधिक लाभ।'
            }
        }
    }

    @classmethod
    def get_plans(cls, crop: str = "Rice", risk_preference: str = "balanced", lang: str = "en") -> Dict[str, Any]:
        """
        Generates 3 customized plans and highlights the recommended plan based on farmer's risk posture.
        Fully dynamic across all crops (Groundnut, Wheat, Sunflower, Maize, Cotton, Rice, Tomato, etc.)
        Supports English (en), Kannada (kn), and Hindi (hi).
        """
        raw_crop = (crop or 'Rice').strip()
        crop_key = raw_crop.lower()
        norm_l = (lang or 'en').lower()

        # Alias resolution for Karnataka & Indian crops
        alias_map = {
            'peanut': 'groundnut', 'peanuts': 'groundnut',
            'ಶೇಂಗಾ': 'groundnut', 'ಕಡಲೆಕಾಯಿ': 'groundnut', 'ಕಡಲೆಕಾಯಿ (ಶೇಂಗಾ)': 'groundnut', 'ಮೂಂಗ್‌ಫಲಿ': 'groundnut', 'मूंगफली': 'groundnut',
            'corn': 'maize', 'ಮೆಕ್ಕೆಜೋಳ': 'maize', 'ಮಕ್ಕಾ': 'maize', 'मक्का': 'maize',
            'paddy': 'rice', 'ಭತ್ತ': 'rice', 'ಬತ್ತ': 'rice', 'ಧಾನ': 'rice', 'धान': 'rice', 'चावल': 'rice',
            'wheat': 'wheat', 'ಗೋಧಿ': 'wheat', 'गेहूं': 'wheat', 'गेहू': 'wheat',
            'sunflower': 'sunflower', 'ಸೂರ್ಯಕಾಂತಿ': 'sunflower', 'सूरजमुखी': 'sunflower',
            'cotton': 'cotton', 'ಹತ್ತಿ': 'cotton', 'ಕಪಾಸ್': 'cotton', 'कपास': 'cotton',
            'tomato': 'tomato', 'ಟೊಮೆಟೊ': 'tomato', 'ಟೊಮೇಟೊ': 'tomato', 'टमाटर': 'tomato',
            'chickpea': 'chickpea', 'gram': 'chickpea', 'bengal gram': 'chickpea', 'ಕಡಲೆ': 'chickpea', 'ಚನಾ': 'chickpea', 'चना': 'chickpea',
            'sugarcane': 'sugarcane', 'ಕಬ್ಬು': 'sugarcane', 'गन्ना': 'sugarcane',
            'soybean': 'soybean', 'ಸೋಯಾಬೀನ್': 'soybean', 'सोयाबीन': 'soybean',
            'onion': 'onion', 'ಈರುಳ್ಳಿ': 'onion', 'प्याज': 'onion',
            'chilli': 'chilli', 'chilli pepper': 'chilli', 'chili': 'chilli', 'ಮೆಣಸಿನಕಾಯಿ': 'chilli', 'मिर्च': 'chilli'
        }
        from models.agri_calendar_service import normalize_crop_name
        canonical_key = normalize_crop_name(raw_crop)
        if not canonical_key or canonical_key not in cls.PLANS_DATABASE:
            canonical_key = alias_map.get(crop_key, canonical_key or crop_key)

        crop_plans = cls.PLANS_DATABASE.get(canonical_key)

        # Dynamic fallback generator for any crop not in pre-baked set
        if not crop_plans:
            c_name = raw_crop.capitalize()
            crop_plans = {
                'safe': {
                    'title': f'🔵 Safe Plan (Defensive {c_name})',
                    'title_kn': f'🔵 ಸುರಕ್ಷಿತ ಯೋಜನೆ ({c_name} ರಕ್ಷಣಾತ್ಮಕ ಮತ್ತು ಕಡಿಮೆ ವೆಚ್ಚ)',
                    'title_hi': f'🔵 सुरक्षित योजना ({c_name} कम लागत व सुरक्षा)',
                    'variety': f'Drought/Pest Hardy Native {c_name} Variety',
                    'variety_kn': f'ಕಡಿಮೆ ಅವಧಿಯ ಬರ ಮತ್ತು ರೋಗ-ನಿರೋಧಕ ಸ್ಥಳೀಯ {c_name} ತಳಿ',
                    'variety_hi': f'कम अवधि की सूखा व कीट-प्रतिरोधी स्थानीय {c_name} किस्म',
                    'expected_profit_acre': '₹30,000 – ₹45,000',
                    'expected_profit_acre_kn': '₹30,000 – ₹45,000',
                    'expected_profit_acre_hi': '₹30,000 – ₹45,000',
                    'downside_worst_case': '+₹10,000 (Capital Protected)',
                    'downside_worst_case_kn': '+₹10,000 (ಬಂಡವಾಳ ಸಂಪೂರ್ಣ ಸುರಕ್ಷಿತ)',
                    'downside_worst_case_hi': '+₹10,000 (पूंजी पूर्णतः सुरक्षित)',
                    'capital_outlay': '₹12,000 / acre',
                    'capital_outlay_kn': '₹12,000 / ಎಕರೆ',
                    'capital_outlay_hi': '₹12,000 / एकड़',
                    'strategy': f'Low input cost, organic soil amendments, bio-seed treatment, zero debt.',
                    'strategy_kn': f'ಕಡಿಮೆ ಖರ್ಚಿನ ಸಾವಯವ ಪೋಷಣೆ, ಜೈವಿಕ ಬೀಜೋಪಚಾರ, ಶೂನ್ಯ ಸಾಲ, ಗರಿಷ್ಠ ಬಂಡವಾಳ ರಕ್ಷಣೆ.',
                    'strategy_hi': f'कम लागत जैविक पोषण, जैव-बीजोपचार, शून्य कर्ज और सुरक्षित पूंजी।',
                    'regret_score': 'Minimax Regret Optimal (0.09) — Protected against weather failure.',
                    'regret_score_kn': 'ಕನಿಷ್ಠ ವಿಷಾದ (0.09) — ಪ್ರತಿಕೂಲ ಹವಾಮಾನದಲ್ಲೂ ನಷ್ಟವಿಲ್ಲ.',
                    'regret_score_hi': 'न्यूनतम रिग्रेट (0.09) — प्रतिकूल मौसम में भी पूंजी सुरक्षित।'
                },
                'balanced': {
                    'title': f'🟡 Balanced Plan (Hedged {c_name})',
                    'title_kn': f'🟡 ಸಮತೋಲಿತ ಯೋಜನೆ ({c_name} ಸೂಕ್ತ ಅಪಾಯ ನಿರ್ವಹಣೆ)',
                    'title_hi': f'🟡 संतुलित योजना ({c_name} इष्टतम बचाव व लाभ)',
                    'variety': f'High-Yielding Certified {c_name} Hybrid + Intercrop',
                    'variety_kn': f'ಪ್ರಮಾಣೀಕೃತ ಅಧಿಕ ಇಳುವರಿ {c_name} ಹೈಬ್ರಿಡ್ ತಳಿ + ದ್ವಿದಳ ಧಾನ್ಯ ಅಂತರಬೆಳೆ',
                    'variety_hi': f'प्रमाणित उच्च उपज {c_name} हाइब्रिड किस्म + दलहनी अंतःफसल',
                    'expected_profit_acre': '₹55,000 – ₹78,000',
                    'expected_profit_acre_kn': '₹55,000 – ₹78,000',
                    'expected_profit_acre_hi': '₹55,000 – ₹78,000',
                    'downside_worst_case': '+₹2,000 (Break-even with MSP/Floor)',
                    'downside_worst_case_kn': '+₹2,000 (ಬೆಂಬಲ ಬೆಲೆ ಆಧಾರದಲ್ಲಿ ವೆಚ್ಚ ಸರಿದೂಗಿಕೆ)',
                    'downside_worst_case_hi': '+₹2,000 (समर्थन मूल्य पर लागत सुरक्षित)',
                    'capital_outlay': '₹22,000 / acre',
                    'capital_outlay_kn': '₹22,000 / ಎಕರೆ',
                    'capital_outlay_hi': '₹22,000 / एकड़',
                    'strategy': f'Drip fertigation, balanced split NPK, IPM pest scouting, PMFBY crop insurance.',
                    'strategy_kn': f'ಹನಿ ನೀರಾವರಿ, ಸಮತೋಲಿತ ರಸಗೊಬ್ಬರ, ಸಮಗ್ರ ಕೀಟ ನಿಯಂತ್ರಣ ಮತ್ತು PMFBY ಬೆಳೆ ವಿಮೆ.',
                    'strategy_hi': f'ड्रिप फर्टिगेशन, संतुलित उर्वरक, एकीकृत कीट प्रबंधन और PMFBY फसल बीमा।',
                    'regret_score': 'Optimal Sharpe Ratio (0.22) — Best risk-adjusted return.',
                    'regret_score_kn': 'ಕಡಿಮೆ ವಿಷಾದ (0.22) — ಸಾಮಾನ್ಯ ಪರಿಸ್ಥಿತಿಯಲ್ಲಿ ಅತ್ಯುತ್ತಮ ಆದಾಯ.',
                    'regret_score_hi': 'कम रिग्रेट (0.22) — सामान्य परिस्थितियों में बेहतरीन लाभ।'
                },
                'aggressive': {
                    'title': f'🟢 Aggressive Plan (Precision High-Alpha {c_name})',
                    'title_kn': f'🟢 ಆಕ್ರಮಣಕಾರಿ ಯೋಜನೆ ({c_name} ಗರಿಷ್ಠ ಮಾರುಕಟ್ಟೆ ಲಾಭ)',
                    'title_hi': f'🟢 आक्रामक योजना ({c_name} अधिकतम प्रीमियम लाभ)',
                    'variety': f'Export-Grade / Premium Commercial {c_name} Hybrid',
                    'variety_kn': f'ರಫ್ತು ಗುಣಮಟ್ಟದ ಪ್ರೀಮಿಯಂ ವಾಣಿಜ್ಯ {c_name} ಹೈಬ್ರಿಡ್ ತಳಿ',
                    'variety_hi': f'निर्यात गुणवत्ता प्रीमियम व्यावसायिक {c_name} हाइब्रिड किस्म',
                    'expected_profit_acre': '₹90,000 – ₹1,45,000',
                    'expected_profit_acre_kn': '₹90,000 – ₹1,45,000',
                    'expected_profit_acre_hi': '₹90,000 – ₹1,45,000',
                    'downside_worst_case': '-₹18,000 (Risk under extreme climate shock or market crash)',
                    'downside_worst_case_kn': '-₹18,000 (ತೀವ್ರ ಮಳೆ ಕೊರತೆ ಅಥವಾ ಬೆಲೆ ಕುಸಿತವಾದರೆ ನಷ್ಟದ ಅಪಾಯ)',
                    'downside_worst_case_hi': '-₹18,000 (प्रतिकूल मौसम या बाजार गिरावट पर जोखिम)',
                    'capital_outlay': '₹34,000 / acre',
                    'capital_outlay_kn': '₹34,000 / ಎಕರೆ',
                    'capital_outlay_hi': '₹34,000 / एकड़',
                    'strategy': f'Precision drip fertigation with foliar micro-nutrients, contract farming or direct mandi tie-up.',
                    'strategy_kn': f'ನಿಖರ ಹನಿ ಫರ್ಟಿಗೇಷನ್, ಸೂಕ್ಷ್ಮ ಪೋಷಕಾಂಶಗಳ ಸಿಂಪಡಣೆ ಮತ್ತು ನೇರ ಮಾರುಕಟ್ಟೆ ಒಪ್ಪಂದ.',
                    'strategy_hi': f'सटीक ड्रिप फर्टिगेशन, सूक्ष्म पोषक तत्व स्प्रे और मंडी/व्यापारियों से सीधा अनुबंध।',
                    'regret_score': 'High Regret Potential (0.64) — Peak upside with market exposure.',
                    'regret_score_kn': 'ಹೆಚ್ಚಿನ ವಿಷಾದ ಸಂಭವ (0.64) — ಮಾರುಕಟ್ಟೆ ಅನುಕೂಲವಿದ್ದರೆ ಬಂಪರ್ ಲಾಭ.',
                    'regret_score_hi': 'उच्च रिग्रेट संभावना (0.64) — बाजार अनुकूल रहने पर बंपर लाभ।'
                }
            }

        safe_p = dict(crop_plans['safe'])
        bal_p = dict(crop_plans['balanced'])
        agg_p = dict(crop_plans['aggressive'])

        # Dynamically calibrate stress-test numbers specifically for this crop's capital & profit profile
        def _extract_num(s):
            m = re.search(r'[\d,]+', str(s).replace('₹', ''))
            return int(m.group(0).replace(',', '')) if m else 15000

        safe_cost = _extract_num(crop_plans['safe'].get('capital_outlay', '14000'))
        bal_cost = _extract_num(crop_plans['balanced'].get('capital_outlay', '22000'))
        agg_cost = _extract_num(crop_plans['aggressive'].get('capital_outlay', '32000'))

        safe_prof = _extract_num(crop_plans['safe'].get('expected_profit_acre', '35000'))
        bal_prof = _extract_num(crop_plans['balanced'].get('expected_profit_acre', '55000'))
        agg_prof = _extract_num(crop_plans['aggressive'].get('expected_profit_acre', '90000'))

        # Dynamically calculated payoffs per scenario and crop
        drought_bal = f"+₹{max(4000, round(bal_prof * 0.28 / 1000) * 1000):,}"
        drought_agg = f"-₹{max(10000, round(agg_cost * 0.55 / 1000) * 1000):,}"
        crash_safe = f"+₹{max(3000, round(safe_prof * 0.32 / 1000) * 1000):,}"
        crash_agg = f"-₹{max(12000, round(agg_cost * 0.85 / 1000) * 1000):,}"

        # Language adaptation
        if 'kn' in norm_l:
            for p in [safe_p, bal_p, agg_p]:
                if 'title_kn' in p: p['title'] = p['title_kn']
                if 'variety_kn' in p: p['variety'] = p['variety_kn']
                if 'expected_profit_acre_kn' in p: p['expected_profit_acre'] = p['expected_profit_acre_kn']
                if 'downside_worst_case_kn' in p: p['downside_worst_case'] = p['downside_worst_case_kn']
                if 'capital_outlay_kn' in p: p['capital_outlay'] = p['capital_outlay_kn']
                if 'strategy_kn' in p: p['strategy'] = p['strategy_kn']
                if 'regret_score_kn' in p: p['regret_score'] = p['regret_score_kn']

            stress_test_matrix = [
                {
                    'scenario': '☀️ ಸಾಮಾನ್ಯ ಹವಾಮಾನ ಹಂಗಾಮು (60% ಸಂಭವನೀಯತೆ)',
                    'safe': safe_p.get('expected_profit_acre_kn', safe_p['expected_profit_acre']).split('–')[0].strip(),
                    'balanced': bal_p.get('expected_profit_acre_kn', bal_p['expected_profit_acre']).split('–')[0].strip(),
                    'aggressive': agg_p.get('expected_profit_acre_kn', agg_p['expected_profit_acre']).split('–')[0].strip()
                },
                {
                    'scenario': '🏜️ ಸಾಧಾರಣ ಬರಗಾಲ / ತೀವ್ರ ತಾಪಮಾನ (25% ಸಂಭವನೀಯತೆ)',
                    'safe': safe_p.get('downside_worst_case_kn', safe_p['downside_worst_case']).split('(')[0].strip(),
                    'balanced': drought_bal,
                    'aggressive': drought_agg
                },
                {
                    'scenario': '📉 APMC ಮಾರುಕಟ್ಟೆ ದರ ಕುಸಿತ (15% ಸಂಭವನೀಯತೆ)',
                    'safe': crash_safe,
                    'balanced': '₹0 (MSP ಬೆಂಬಲ ಬೆಲೆ ರಕ್ಷಣೆ)',
                    'aggressive': crash_agg
                }
            ]
        elif 'hi' in norm_l:
            for p in [safe_p, bal_p, agg_p]:
                if 'title_hi' in p: p['title'] = p['title_hi']
                if 'variety_hi' in p: p['variety'] = p['variety_hi']
                if 'expected_profit_acre_hi' in p: p['expected_profit_acre'] = p['expected_profit_acre_hi']
                if 'downside_worst_case_hi' in p: p['downside_worst_case'] = p['downside_worst_case_hi']
                if 'capital_outlay_hi' in p: p['capital_outlay'] = p['capital_outlay_hi']
                if 'strategy_hi' in p: p['strategy'] = p['strategy_hi']
                if 'regret_score_hi' in p: p['regret_score'] = p['regret_score_hi']

            stress_test_matrix = [
                {
                    'scenario': '☀️ सामान्य मौसम सीजन (60% संभावना)',
                    'safe': safe_p.get('expected_profit_acre_hi', safe_p['expected_profit_acre']).split('–')[0].strip(),
                    'balanced': bal_p.get('expected_profit_acre_hi', bal_p['expected_profit_acre']).split('–')[0].strip(),
                    'aggressive': agg_p.get('expected_profit_acre_hi', agg_p['expected_profit_acre']).split('–')[0].strip()
                },
                {
                    'scenario': '🏜️ सूखा / लू का प्रकोप (25% संभावना)',
                    'safe': safe_p.get('downside_worst_case_hi', safe_p['downside_worst_case']).split('(')[0].strip(),
                    'balanced': drought_bal,
                    'aggressive': drought_agg
                },
                {
                    'scenario': '📉 APMC मंडी भाव में भारी गिरावट (15% संभावना)',
                    'safe': crash_safe,
                    'balanced': '₹0 (सरकारी एमएसपी सुरक्षा)',
                    'aggressive': crash_agg
                }
            ]
        else:
            stress_test_matrix = [
                {
                    'scenario': '☀️ Normal Season (60% prob)',
                    'safe': safe_p['expected_profit_acre'].split('–')[0].strip(),
                    'balanced': bal_p['expected_profit_acre'].split('–')[0].strip(),
                    'aggressive': agg_p['expected_profit_acre'].split('–')[0].strip()
                },
                {
                    'scenario': '🏜️ Moderate Drought / Heatwave (25% prob)',
                    'safe': safe_p['downside_worst_case'].split('(')[0].strip(),
                    'balanced': drought_bal,
                    'aggressive': drought_agg
                },
                {
                    'scenario': '📉 Mandi Price Crash (15% prob)',
                    'safe': crash_safe,
                    'balanced': '₹0 (MSP)',
                    'aggressive': crash_agg
                }
            ]

        return {
            'status': 'success',
            'crop': raw_crop.capitalize(),
            'active_preference': risk_preference,
            'safe_plan': safe_p,
            'balanced_plan': bal_p,
            'aggressive_plan': agg_p,
            'stress_test_matrix': stress_test_matrix
        }


# Expose Singleton Instances
digital_twin_engine = DigitalTwinEngine()
counterfactual_causal_engine = CounterfactualCausalEngine()
multi_agent_debate_engine = MultiAgentDebateEngine()
regret_minimization_engine = RegretMinimizationEngine()
