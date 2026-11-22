import React, { useEffect, useState } from 'react';

const API_BASE = 'http://127.0.0.1:5000';

const districtSoilData = {
  Bagalkot: { n: 70, p: 35, k: 38, ph: 7.2, rainfall: 550, temp: 28, humidity: 55 },
  Ballari: { n: 65, p: 30, k: 35, ph: 7.0, rainfall: 500, temp: 30, humidity: 50 },
  Belagavi: { n: 85, p: 45, k: 42, ph: 6.8, rainfall: 800, temp: 24, humidity: 70 },
  'Bengaluru Rural': { n: 75, p: 40, k: 40, ph: 6.2, rainfall: 900, temp: 24, humidity: 65 },
  'Bengaluru Urban': { n: 72, p: 38, k: 38, ph: 6.3, rainfall: 870, temp: 25, humidity: 63 },
  Bidar: { n: 68, p: 33, k: 36, ph: 7.3, rainfall: 750, temp: 27, humidity: 58 },
  Chamarajanagara: { n: 78, p: 42, k: 40, ph: 6.0, rainfall: 750, temp: 26, humidity: 65 },
  Chikkaballapura: { n: 70, p: 36, k: 38, ph: 6.5, rainfall: 820, temp: 25, humidity: 62 },
  Chikkamagaluru: { n: 92, p: 52, k: 48, ph: 5.8, rainfall: 1800, temp: 22, humidity: 80 },
  Chitradurga: { n: 68, p: 34, k: 36, ph: 6.8, rainfall: 600, temp: 28, humidity: 55 },
  'Dakshina Kannada': { n: 90, p: 50, k: 46, ph: 5.5, rainfall: 3000, temp: 28, humidity: 85 },
  Davanagere: { n: 78, p: 42, k: 40, ph: 6.5, rainfall: 650, temp: 27, humidity: 60 },
  Dharwad: { n: 80, p: 40, k: 38, ph: 6.5, rainfall: 700, temp: 25, humidity: 62 },
  Gadag: { n: 70, p: 35, k: 37, ph: 7.0, rainfall: 550, temp: 28, humidity: 55 },
  Hassan: { n: 90, p: 50, k: 45, ph: 6.5, rainfall: 1100, temp: 22, humidity: 75 },
  Haveri: { n: 75, p: 38, k: 38, ph: 6.8, rainfall: 650, temp: 26, humidity: 60 },
  Kalaburagi: { n: 65, p: 32, k: 35, ph: 7.5, rainfall: 700, temp: 29, humidity: 55 },
  Kodagu: { n: 95, p: 55, k: 50, ph: 5.5, rainfall: 2800, temp: 20, humidity: 90 },
  Kolar: { n: 70, p: 35, k: 38, ph: 6.0, rainfall: 850, temp: 25, humidity: 65 },
  Koppal: { n: 65, p: 30, k: 35, ph: 7.2, rainfall: 500, temp: 30, humidity: 50 },
  Mandya: { n: 88, p: 48, k: 44, ph: 6.2, rainfall: 700, temp: 25, humidity: 68 },
  Mysuru: { n: 75, p: 38, k: 40, ph: 6.2, rainfall: 750, temp: 25, humidity: 67 },
  Raichur: { n: 65, p: 32, k: 35, ph: 7.2, rainfall: 550, temp: 31, humidity: 50 },
  Ramanagara: { n: 73, p: 37, k: 39, ph: 6.3, rainfall: 820, temp: 25, humidity: 64 },
  Shivamogga: { n: 85, p: 45, k: 42, ph: 6.0, rainfall: 1500, temp: 24, humidity: 78 },
  Tumakuru: { n: 72, p: 36, k: 38, ph: 6.3, rainfall: 800, temp: 26, humidity: 62 },
  Udupi: { n: 88, p: 48, k: 44, ph: 5.8, rainfall: 3500, temp: 27, humidity: 88 },
  'Uttara Kannada': { n: 85, p: 45, k: 42, ph: 5.8, rainfall: 2500, temp: 26, humidity: 82 },
  Vijayapura: { n: 70, p: 38, k: 40, ph: 7.5, rainfall: 500, temp: 29, humidity: 52 },
  Yadgir: { n: 63, p: 30, k: 33, ph: 7.4, rainfall: 600, temp: 30, humidity: 52 },
};

const cropOptions = [
  'Wheat',
  'Tomato',
  'Potato',
  'Onion',
  'Rice',
  'Maize',
  'Grapes',
  'Apple',
  'Mango',
  'Banana',
  'Cotton',
  'Coconut',
];

const districtOptions = Object.keys(districtSoilData);

const titles = {
  en: 'SmartAgri AI — Farmer Decision Support System',
  kn: 'ಸ್ಮಾರ್ಟ್‌ಆಗ್ರಿ AI — ರೈತ ನಿರ್ಧಾರ ಬೆಂಬಲ ವ್ಯವಸ್ಥೆ',
  hi: 'स्मार्टएग्री AI — किसान निर्णय समर्थन प्रणाली',
};

function App() {
  const [lang, setLang] = useState('en');
  const [voiceText, setVoiceText] = useState('');
  const [soilForm, setSoilForm] = useState({
    nitrogen: '',
    phosphorus: '',
    potassium: '',
    ph: '',
    rainfall: '',
    city: '',
  });
  const [soilNotice, setSoilNotice] = useState('');
  const [selectedCrop, setSelectedCrop] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState('');
  const [month, setMonth] = useState('');
  const [year, setYear] = useState('');
  const [queryAnswer, setQueryAnswer] = useState('');
  const [diseaseResult, setDiseaseResult] = useState('');
  const [priceResult, setPriceResult] = useState('');
  const [weatherInfo, setWeatherInfo] = useState('');
  const [cropResult, setCropResult] = useState('');
  const [plannerPriority, setPlannerPriority] = useState([
    'Water irrigation should be scheduled before the next 48-hour dry spell.',
    'Use nitrogen-balanced nutrition to improve crop stress resistance.',
  ]);
  const [plannerSummary, setPlannerSummary] = useState('');
  const [plannerAdvice, setPlannerAdvice] = useState([
    'Maintain soil moisture in the top 20 cm layer to improve root health.',
    'Follow local market timing to maximize sale value before peak demand.',
  ]);
  const [plannerAlerts, setPlannerAlerts] = useState([
    'Watch for early signs of nutrient deficiency in the next 7 days.',
  ]);
  const [plantingSchedule, setPlantingSchedule] = useState('');
  const [harvestSchedule, setHarvestSchedule] = useState('');
  const [fertilizerPlan, setFertilizerPlan] = useState('');
  const [sellRecommendation, setSellRecommendation] = useState('');
  const [pestGuide, setPestGuide] = useState([
    'Apply neem oil for mild pest pressure.',
    'Inspect the field twice a week for visible leaf damage.',
  ]);

  useEffect(() => {
    document.title = titles[lang] || titles.en;
  }, [lang]);

  function updateSoilField(name, value) {
    setSoilForm((prev) => ({ ...prev, [name]: value }));
  }

  function switchLang(nextLang) {
    setLang(nextLang);
  }

  function autoFillSoilData(district) {
    if (!district) return;

    const data = districtSoilData[district];
    if (!data) return;

    setSoilForm({
      nitrogen: data.n,
      phosphorus: data.p,
      potassium: data.k,
      ph: data.ph,
      rainfall: data.rainfall,
      city: district,
    });

    const message = {
      en: `✅ Soil values auto-filled for ${district}! You can modify if needed.`,
      kn: `✅ ${district} ಗಾಗಿ ಮಣ್ಣಿನ ಮೌಲ್ಯಗಳು ತಂತಾನೇ ತುಂಬಿವೆ! ನೀವು ಬದಲಾಯಿಸಬಹುದು.`,
      hi: `✅ ${district} के लिए मिट्टी के मान अपने आप भर गए! आप आवश्यकता अनुसार बदल सकते हैं।`,
    };

    setSoilNotice(message[lang] || message.en);
    window.setTimeout(() => setSoilNotice(''), 3000);
  }

  function startVoice() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert(
        lang === 'kn'
          ? 'ಈ ಬ್ರೌಸರ್‌ನಲ್ಲಿ ಧ್ವನಿ ಗುರುತಿಸುವಿಕೆ ಬೆಂಬಲಿತವಾಗಿಲ್ಲ. Chrome ಬಳಸಿ.'
          : lang === 'hi'
            ? 'इस ब्राउज़र में वॉयस पहचान समर्थित नहीं है। Chrome का उपयोग करें।'
            : 'Voice recognition not supported in this browser. Please use Chrome.',
      );
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = { en: 'en-IN', kn: 'kn-IN', hi: 'hi-IN' }[lang] || 'en-IN';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setVoiceText(transcript);
    };

    recognition.onerror = (event) => {
      const errorMessage = {
        en: 'Voice recognition failed. Please try again.',
        kn: 'ಧ್ವನಿ ಗುರುತಿಸುವಿಕೆ ವಿಫಲವಾಗಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.',
        hi: 'वॉयस पहचान विफल रही। कृपया पुनः प्रयास करें।',
      };
      alert(errorMessage[lang] || errorMessage.en);
    };

    try {
      recognition.start();
    } catch (error) {
      console.error('Voice recognition could not start:', error);
    }
  }

  async function handleQuerySubmit(event) {
    event.preventDefault();

    try {
      const formData = new FormData();
      formData.append('query', voiceText);

      const response = await fetch(`${API_BASE}/api/answer_query`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Failed to get answer');
      const data = await response.json();
      setQueryAnswer(data.answer || 'No answer returned');
    } catch (error) {
      console.error(error);
      setQueryAnswer('SmartAgri AI is temporarily unavailable. Please try again.');
    }
  }

  async function handleDiseaseSubmit(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    formData.append('crop_type', 'general');

    try {
      const response = await fetch(`${API_BASE}/predict_disease`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Disease prediction failed');
      const html = await response.text();
      if (html.includes('Error:')) {
        throw new Error('Backend disease prediction error');
      }
      setDiseaseResult('Disease prediction submitted successfully. Please refresh or wait for backend processing results.');
    } catch (error) {
      console.error(error);
      setDiseaseResult('Unable to complete disease prediction right now.');
    }
  }

  async function handlePriceSubmit(event) {
    event.preventDefault();

    const formData = new FormData();
    formData.append('crop', selectedCrop);
    formData.append('district', selectedDistrict);
    formData.append('month', month);
    formData.append('year', year);

    try {
      const response = await fetch(`${API_BASE}/predict_price`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Price prediction failed');
      const html = await response.text();
      if (html.includes('Error:')) {
        throw new Error('Backend price prediction error');
      }
      setPriceResult(`Price prediction submitted for ${selectedCrop} in ${selectedDistrict}. Please refresh to see the backend result.`);
    } catch (error) {
      console.error(error);
      setPriceResult('Unable to get a live price prediction right now.');
    }
  }

  async function handleCropSubmit(event) {
    event.preventDefault();

    const formData = new FormData();
    Object.entries(soilForm).forEach(([key, value]) => formData.append(key, value));

    try {
      const response = await fetch(`${API_BASE}/predict_crop`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Crop prediction failed');
      const html = await response.text();
      if (html.includes('Error:')) {
        throw new Error('Backend crop prediction error');
      }
      setWeatherInfo(`Weather data request sent for ${soilForm.city || 'your district'}. Please refresh to view the backend recommendation.`);
      setCropResult('Crop recommendation submitted successfully.');
    } catch (error) {
      console.error(error);
      setCropResult('Unable to complete crop recommendation right now.');
    }
  }

  async function handlePlannerSubmit(event) {
    event.preventDefault();

    try {
      const response = await fetch(`${API_BASE}/planner`, {
        method: 'POST',
      });

      if (!response.ok) throw new Error('Planner request failed');
      const html = await response.text();
      if (html.includes('Error:')) {
        throw new Error('Planner backend error');
      }

      setPlannerSummary('Farm plan generated successfully. Refresh the page to display the latest backend session data.');
      setPlannerAdvice(['Planner data has been submitted to the backend successfully.']);
      setPlannerAlerts(['Check the page after refresh for the generated plan.']);
      setPlantingSchedule('Backend planner data is pending display.');
      setHarvestSchedule('Backend planner data is pending display.');
      setFertilizerPlan('Backend planner data is pending display.');
      setSellRecommendation('Backend planner data is pending display.');
    } catch (error) {
      console.error(error);
      setPlannerSummary('Unable to generate a full farm plan right now.');
    }
  }

  return (
    <>
      <header className="gov-header">
        <div className="header-top">
          <div className="header-logo" role="img" aria-label="Wheat sheaf icon">🌾</div>
          <div className="header-text">
            <h1>SmartAgri AI</h1>
            <p>Agent-Based Intelligent System for Farmer Decision Support</p>
          </div>
          <div className="header-emblem" role="img" aria-label="Indian flag">🇮🇳</div>
        </div>

        <div className="header-user">
          <span>👤 Welcome, Farmer!</span>
          <a href="#" className="logout-btn">🚪 Logout</a>
        </div>

        <nav className="gov-nav">
          <a href="#crop">🌱 Crop Recommendation</a>
          <a href="#price">💰 Market Price</a>
          <a href="#disease">🍃 Disease Detection</a>
          <a href="#planner">🤖 Planner Agent</a>
        </nav>
      </header>

      <div className="marquee-bar" aria-label="Announcements">
        <div className="marquee-track">
          <span>
            🌾 Welcome to SmartAgri AI — Empowering Farmers with Artificial Intelligence | 🌱 Get Crop Recommendations | 💰 Check Market Prices | 🍃 Detect Leaf Diseases | 🤖 Get AI Farm Planning
          </span>
        </div>
      </div>

      <div className="lang-switcher">
        <span className="lang-note">
          Note: AI-generated results are currently shown in English only.
        </span>
        <button
          type="button"
          className={`lang-btn ${lang === 'en' ? 'active' : ''}`}
          onClick={() => switchLang('en')}
        >
          🇬🇧 English
        </button>
        <button
          type="button"
          className={`lang-btn ${lang === 'kn' ? 'active' : ''}`}
          onClick={() => switchLang('kn')}
        >
          🇮🇳 ಕನ್ನಡ
        </button>
        <button
          type="button"
          className={`lang-btn ${lang === 'hi' ? 'active' : ''}`}
          onClick={() => switchLang('hi')}
        >
          🇮🇳 हिंदी
        </button>
      </div>

      <div className="main-container">
        <div style={{ textAlign: 'right', marginBottom: '8px' }}>
          <button type="button" className="gov-btn reset-btn" onClick={() => window.location.reload()}>
            🔄 Start New Session
          </button>
        </div>

        <div className="section-box" id="voice">
          <div className="section-header">
            <span className="section-icon" role="img" aria-label="Microphone">🎤</span>
            <div>
              <h2>Voice Query Assistant</h2>
              <p className="section-desc">Ask any farming question in English, Kannada or Hindi</p>
            </div>
          </div>

          <form onSubmit={handleQuerySubmit}>
            <div className="form-group">
              <textarea
                id="voiceText"
                value={voiceText}
                onChange={(event) => setVoiceText(event.target.value)}
                placeholder="e.g. Which crop should I grow? / What fertilizer for tomato?"
              />
            </div>

            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
              <button type="button" id="voiceBtn" className="gov-btn" onClick={startVoice}>
                🎤 Start Voice Input
              </button>
              <button type="submit" className="gov-btn" style={{ background: 'linear-gradient(135deg, #1565c0, #1976d2)' }}>
                🔍 Get Answer
              </button>
            </div>
          </form>

          {queryAnswer && (
            <div className="query-answer-box">
              <div className="query-answer-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
                <span>🤖 SmartAgri AI Answer:</span>
                <button
                  type="button"
                  className="gov-btn"
                  onClick={() => {
                    const clean = queryAnswer.replace(/[*#_`~>•→]/g, ' ').replace(/\s+/g, ' ').trim();
                    const audio = new Audio(`${API_BASE}/api/tts?lang=${lang}&text=${encodeURIComponent(clean)}`);
                    audio.play().catch(() => {
                      if ('speechSynthesis' in window) {
                        const ut = new SpeechSynthesisUtterance(clean.substring(0, 300));
                        ut.lang = lang === 'kn' ? 'kn-IN' : lang === 'hi' ? 'hi-IN' : 'en-IN';
                        window.speechSynthesis.speak(ut);
                      }
                    });
                  }}
                  style={{
                    padding: '4px 12px',
                    fontSize: '12px',
                    background: 'linear-gradient(135deg, #2e7d32, #388e3c)',
                    margin: 0
                  }}
                >
                  {lang === 'kn' ? '🔊 ಧ್ವನಿಯಲ್ಲಿ ಕೇಳಿ' : lang === 'hi' ? '🔊 बोलकर सुनाएं' : '🔊 Read Aloud'}
                </button>
              </div>
              <div className="query-answer-body">{queryAnswer}</div>
            </div>
          )}
        </div>

        <div className="section-box" id="crop">
          <div className="section-header">
            <span className="section-icon">🌱</span>
            <div>
              <h2>Crop Recommendation</h2>
              <p className="section-desc">Get AI-powered crop suggestions based on soil and live weather data</p>
            </div>
          </div>

          <div className="info-note" style={{ marginBottom: '16px' }}>
            <strong>📋 Step 1: Select your district to auto-fill typical soil values</strong>
            <br />
            <small>Fields will auto-fill once you select a district — you can still edit any value.</small>
          </div>

          <div className="form-group" style={{ marginBottom: '16px' }}>
            <label className="form-label">Select District (Auto-fill soil values)</label>
            <select className="gov-select" value={soilForm.city} onChange={(event) => autoFillSoilData(event.target.value)}>
              <option value="">-- Select District --</option>
              {districtOptions.map((district) => (
                <option key={district} value={district}>{district}</option>
              ))}
            </select>
          </div>

          {soilNotice && <div className="info-note" style={{ marginTop: '8px' }}>{soilNotice}</div>}

          <form onSubmit={handleCropSubmit}>
            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">Nitrogen (N)</label>
                <input type="number" name="nitrogen" value={soilForm.nitrogen} onChange={(event) => updateSoilField('nitrogen', event.target.value)} placeholder="0-150" required className="gov-input" />
              </div>
              <div className="form-group">
                <label className="form-label">Phosphorus (P)</label>
                <input type="number" name="phosphorus" value={soilForm.phosphorus} onChange={(event) => updateSoilField('phosphorus', event.target.value)} placeholder="0-150" required className="gov-input" />
              </div>
              <div className="form-group">
                <label className="form-label">Potassium (K)</label>
                <input type="number" name="potassium" value={soilForm.potassium} onChange={(event) => updateSoilField('potassium', event.target.value)} placeholder="0-150" required className="gov-input" />
              </div>
              <div className="form-group">
                <label className="form-label">pH Value</label>
                <input type="number" step="0.1" name="ph" value={soilForm.ph} onChange={(event) => updateSoilField('ph', event.target.value)} placeholder="0-14" required className="gov-input" />
              </div>
              <div className="form-group">
                <label className="form-label">Rainfall (mm)</label>
                <input type="number" step="0.1" name="rainfall" value={soilForm.rainfall} onChange={(event) => updateSoilField('rainfall', event.target.value)} placeholder="e.g. 200" required className="gov-input" />
              </div>
              <input type="hidden" name="city" value={soilForm.city} />
            </div>
            <button type="submit" className="gov-btn">🌾 Recommend Crop</button>
          </form>

          {weatherInfo && <div className="weather-info">🌤 {weatherInfo}</div>}
          {cropResult && <div className="result-card crop-result"><span className="result-icon">🌱</span><span>{cropResult}</span></div>}
        </div>

        <div className="section-box" id="price">
          <div className="section-header">
            <span className="section-icon">💰</span>
            <div>
              <h2>Market Price Prediction</h2>
              <p className="section-desc">Predict mandi prices before selling your crop</p>
            </div>
          </div>

          <p className="info-note">📌 Price prediction available for: Wheat, Tomato, Potato, Onion, Rice, Maize, Grapes, Apple, Mango, Banana, Cotton, Coconut</p>

          <form onSubmit={handlePriceSubmit}>
            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">Select Crop</label>
                <select value={selectedCrop} onChange={(event) => setSelectedCrop(event.target.value)} required className="gov-select">
                  <option value="">-- Select Crop --</option>
                  {cropOptions.map((crop) => (
                    <option key={crop} value={crop}>{crop}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Select District</label>
                <select value={selectedDistrict} onChange={(event) => setSelectedDistrict(event.target.value)} required className="gov-select">
                  <option value="">-- Select District --</option>
                  {districtOptions.map((district) => (
                    <option key={district} value={district}>{district}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Month</label>
                <input type="number" value={month} onChange={(event) => setMonth(event.target.value)} min="1" max="12" placeholder="1-12" required className="gov-input" />
              </div>

              <div className="form-group">
                <label className="form-label">Year</label>
                <input type="number" value={year} onChange={(event) => setYear(event.target.value)} min="2020" max="2035" placeholder="2024" required className="gov-input" />
              </div>
            </div>

            <button type="submit" className="gov-btn">📊 Predict Price</button>
          </form>

          {priceResult && <div className="result-card price-result"><span className="result-icon">💹</span><span>{priceResult}</span></div>}
        </div>

        <div className="section-box" id="disease">
          <div className="section-header">
            <span className="section-icon" role="img" aria-label="Leaf">🍃</span>
            <div>
              <h2>Leaf Disease Detection</h2>
              <p className="section-desc">Upload a leaf image to detect plant diseases using AI</p>
            </div>
          </div>

          <p className="info-note">📌 Accepted file types: JPG, JPEG, PNG</p>

          <form onSubmit={handleDiseaseSubmit}>
            <div className="form-group">
              <label className="form-label">Select Leaf Image</label>
              <input type="file" name="image" accept=".jpg,.jpeg,.png,image/jpeg,image/png" required className="file-input" />
            </div>
            <button type="submit" className="gov-btn">🔍 Detect Disease</button>
          </form>

          {diseaseResult && <div className="result-card disease-result"><span className="result-icon">🔬</span><span>{diseaseResult}</span></div>}
        </div>

        <div className="section-box" id="planner">
          <div className="section-header">
            <span className="section-icon" role="img" aria-label="Robot">🤖</span>
            <div>
              <h2>Planner Agent — Final Farm Decision</h2>
              <p className="section-desc">AI orchestration combining all module outputs for final farming advice</p>
            </div>
          </div>

          <div className="plan-card green-card">
            <p><strong>🌱 Recommended Crop:</strong> Rice</p>
            <p><strong>💰 Market Price:</strong> Rice : ₹ 2,450</p>
            <p><strong>🍃 Disease Detected:</strong> Wheat : Leaf Blight</p>
            <p><strong>📍 City:</strong> {soilForm.city || 'Bengaluru'}</p>
          </div>

          <form onSubmit={handlePlannerSubmit}>
            <button type="submit" className="gov-btn">🤖 Get Complete Farm Plan</button>
          </form>

          {plannerPriority.length > 0 && (
            <div style={{ marginTop: '20px' }}>
              <div className="result-section-title critical-title">🚨 Critical Priority Actions</div>
              {plannerPriority.map((item) => (
                <div key={item} className="result-card critical-result">{item}</div>
              ))}
            </div>
          )}

          {plannerSummary && (
            <div className="result-card summary-result" style={{ marginTop: '15px' }}>
              <strong>{plannerSummary}</strong>
            </div>
          )}

          {plannerAdvice.length > 0 && (
            <div style={{ marginTop: '15px' }}>
              <div className="result-section-title advice-title">✅ Agent Advice</div>
              {plannerAdvice.map((advice) => (
                <div key={advice} className="result-card crop-result" style={{ marginBottom: '8px' }}>{advice}</div>
              ))}
            </div>
          )}

          {plannerAlerts.length > 0 && (
            <div style={{ marginTop: '15px' }}>
              <div className="result-section-title alert-title">⚠ Alerts</div>
              {plannerAlerts.map((alert) => (
                <div key={alert} className="result-card alert-result" style={{ marginBottom: '8px' }}>{alert}</div>
              ))}
            </div>
          )}

          {(plantingSchedule || harvestSchedule || fertilizerPlan || sellRecommendation) && (
            <div style={{ marginTop: '20px' }}>
              <div className="result-section-title plan-title">📋 Complete Farm Decision Plan</div>
              <div className="plan-grid">
                <div className="plan-card green-card">
                  <div className="plan-card-title">🌱 Planting Schedule</div>
                  <div className="plan-card-body">{plantingSchedule || 'Plant in the current suitable window.'}</div>
                </div>
                <div className="plan-card green-card">
                  <div className="plan-card-title">🌾 Harvest Schedule</div>
                  <div className="plan-card-body">{harvestSchedule || 'Harvest near maturity and before heavy rainfall risk.'}</div>
                </div>
                <div className="plan-card blue-card">
                  <div className="plan-card-title">🌿 Fertilizer Plan</div>
                  <div className="plan-card-body">{fertilizerPlan || 'Apply split nitrogen dosing and balance K levels.'}</div>
                </div>
                <div className="plan-card purple-card">
                  <div className="plan-card-title">💰 Selling Recommendation</div>
                  <div className="plan-card-body">{sellRecommendation || 'Sell in the nearest mandi during the peak demand window.'}</div>
                </div>
              </div>
              <div className="plan-card orange-card" style={{ marginTop: '12px' }}>
                <div className="plan-card-title">🐛 Pest Treatment Guide</div>
                {pestGuide.map((pest) => (
                  <div key={pest} className="pest-item">• {pest}</div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <footer className="gov-footer">
        <div className="footer-content">
          <div className="footer-left">
            <strong>🌾 SmartAgri AI</strong><br />
            Agent-Based AI System for Farmer Decision Support
          </div>
          <div className="footer-center">
            Developed for Agricultural Decision Making<br />
            Powered by Machine Learning & Deep Learning
          </div>
          <div className="footer-right">
            Models: Random Forest | CNN<br />
            API: OpenWeatherMap
          </div>
        </div>
        <div className="footer-bottom">© 2025 SmartAgri AI — All Rights Reserved</div>
      </footer>
    </>
  );
}

export default App;
