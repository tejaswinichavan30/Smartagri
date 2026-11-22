# 🌱 SmartAgri AI: Agent-Based Decision Support System for Precision Agriculture

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Backend-Flask-green.svg)](https://flask.palletsprojects.com/)
[![Frontend](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite-61dafb.svg)](https://react.dev/)
[![Deep Learning](https://img.shields.io/badge/ML-TensorFlow%20%2F%20Keras-orange.svg)](https://www.tensorflow.org/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

An intelligent, multi-agent agricultural decision support platform designed to empower farmers with localized, data-driven agronomic insights. Tailored specifically for agricultural zones in Karnataka (including Dharwad, Kolar, Kalaburagi, and Mysuru), SmartAgri integrates real-time agrometeorology, deep learning vision models, dynamic market price forecasting, and FAO-56 precision hydro-modeling into a unified multilingual copilot.

---

## 🚀 Key Modules & Autonomous Agents

```
                        ┌────────────────────────────────────────┐
                        │   Farmer Web / Voice / Mobile UI       │
                        │    (English, Kannada, Hindi UI)        │
                        └───────────────────┬────────────────────┘
                                            │
                        ┌───────────────────▼────────────────────┐
                        │   Multi-Agent Coordination Engine      │
                        └─┬──────────────┬──────────────┬──────┬─┘
                          │              │              │      │
            ┌─────────────▼──┐ ┌─────────▼────┐ ┌───────▼──┐ ┌─▼──────────────┐
            │   Crop Reco    │ │ Disease CNN  │ │  Market  │ │  FAO-56 Water  │
            │   Agent        │ │ Vision Agent │ │  Agent   │ │  Planner Agent │
            └────────────────┘ └──────────────┘ └──────────┘ └────────────────┘
```

### 1. 🌾 Crop Recommendation Agent
- **Agrometeorological Matching:** Integrates live weather telemetry (temperature, humidity, rainfall) via Open-Meteo & OpenWeather APIs.
- **District-Specific Agronomic Calendars:** Formulated against **UAS Dharwad** and **ICAR-KVK** package of practices.
- **Sowing Window Validator:** Dynamic detection of `open`, `closing_soon`, and `passed` sowing windows with penalty scoring for late-season risk prevention.

### 2. 🔬 Plant Disease Diagnostic Agent
- **Convolutional Neural Network (CNN):** Automated leaf pathology classification and vision grounding across 20+ crops (Rice, Wheat, Tomato, Maize, Potato, Soybean, Cotton, Ragi, Sugarcane, Pepper, etc.).
- **Reference Symptom Guide:** Visual diagnosis fallback for regional pulses (Chickpea, Jowar, Cowpea, Horse Gram) complete with symptom profiles.
- **Integrated Pest Management (IPM):** KVK-verified biological (Trichoderma, neem extracts) and chemical fungicide interventions with safety disclaimers.

### 3. 📈 Market Price & MSP Intelligence Agent
- **APMC Mandi Spot Feeds & Benchmarks:** Live benchmark spot rates with local district APMC yard attribution (Bidar, Hubballi-Dharwad, Kalaburagi, Davanagere, etc.) and transparent `₹/kg wholesale` conversion.
- **4-Month Trend Horizon:** Seasonality-anchored price projections for harvest timing decisions (reporting "Insufficient data" responsibly when multi-year historical data is unavailable to prevent hallucinations).
- **Statutory MSP Verification:** Real-time compliance check against official Cabinet Committee on Economic Affairs (CCEA) Minimum Support Prices, with immediate warning alerts if mandi forecasts dip below MSP to protect farmers from distress sales.

### 4. 💧 Precision Irrigation Scheduling Agent
- **FAO-56 Dynamic Penman-Monteith:** Computes actual crop evapotranspiration:
  $$ET_c = ET_0 \times K_c(\text{stage})$$
- **Growth Stage $K_c$ Scaling:** Derived from Days After Sowing (DAS) across initial, mid-season, and late-season stages.
- **Field Calibration:** Accounts for soil texture moisture retention, effective rainfall deduction ($P_{\text{eff}}$), irrigation efficiency (drip/sprinkler), and pump flow delivery rates (L/hr).

### 5. 🤖 Multilingual Agri-Copilot (RAG)
- **Generative AI Assistant:** Powered by Google Gemini API & LangChain vector search grounded in verified UAS Dharwad agronomy documents.
- **Audio Voice Synthesis:** Native text-to-speech (gTTS) enabling accessible advisory delivery in **English**, **Kannada (ಕನ್ನಡ)**, and **Hindi (हिन्दी)**.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, Vite, React Router, Tailwind CSS, Heroicons |
| **Backend API** | Python 3.12, Flask, Gunicorn, RESTful architecture |
| **Machine Learning** | TensorFlow / Keras (CNN), Scikit-learn (RandomForest), Joblib |
| **Generative AI** | Google Gemini API, LangChain, FAISS Vector Store |
| **Data & Feeds** | Agmarknet, Open-Meteo API, CCEA MSP Gazette Records |
| **Containerization** | Docker, multi-stage build |

---

## 💻 Local Setup & Installation

### Prerequisites
- Python 3.12+
- Node.js 18+ and npm
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/tejaswinichavan30/Smartagri.git
cd Smartagri
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate      # On Windows
# source venv/bin/activate  # On Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd smartagri-react
npm install
npm run build
cd ..
```

### 4. Environment Variables
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
FLASK_ENV=development
PORT=5000
```

### 5. Run Application
```bash
python app.py
```
Open your browser and navigate to `http://localhost:5000`.

---

## 🧪 Testing

Run the automated agronomy and validation test suite:
```bash
pytest tests/test_audit_fixes.py tests/test_district_crops.py -v
```

---

## 📜 Citation & Credits
- **Agronomic Rules & Sowing Windows:** University of Agricultural Sciences (UAS), Dharwad & ICAR Krishi Vigyan Kendra (KVK).
- **MSP Data:** Cabinet Committee on Economic Affairs (CCEA), Ministry of Agriculture & Farmers Welfare, Govt. of India.
- **Disease Dataset:** PlantVillage Leaf Pathology Callset & Indian Agronomic Datasets.

---

## 📄 License
This project is licensed under the MIT License.
