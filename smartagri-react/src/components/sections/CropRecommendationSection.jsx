import { useState } from 'react';
import { useLanguage } from '../../context/LanguageContext.jsx';
import { api } from '../../api.js';
import { DISTRICTS, SOIL_DEFAULTS, getCropName, getDistrictDropdownLabel } from '../../data/districts.js';

const EMPTY_SOIL = { nitrogen: '', phosphorus: '', potassium: '', ph: '', rainfall: '' };

export default function CropRecommendationSection({ onResult }) {
  const { t, lang } = useLanguage();
  const [district, setDistrict] = useState('');
  const [season, setSeason] = useState('auto');
  const [soil, setSoil] = useState(EMPTY_SOIL);
  const [weatherInfo, setWeatherInfo] = useState('');
  const [result, setResult] = useState('');
  const [cropData, setCropData] = useState(null);
  const [seasonContext, setSeasonContext] = useState('');
  const [seasonAdvice, setSeasonAdvice] = useState('');
  const [preferredReason, setPreferredReason] = useState('');
  const [topCrops, setTopCrops] = useState([]);
  const [loading, setLoading] = useState(false);

  function autoFillSoilData(selectedDistrict) {
    setDistrict(selectedDistrict);
    const defaults = SOIL_DEFAULTS[selectedDistrict];
    if (defaults) {
      setSoil({
        nitrogen: defaults.nitrogen,
        phosphorus: defaults.phosphorus,
        potassium: defaults.potassium,
        ph: defaults.ph,
        rainfall: defaults.rainfall
      });
    }
  }

  function updateField(field, value) {
    setSoil((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await api.predictCrop({ ...soil, city: district, district: district, season: season, lang: lang });
      setCropData(data);
      const text = typeof data === 'string' ? data : (lang === 'kn' ? (data.crop_kn || data.crop) : lang === 'hi' ? (data.crop_hi || data.crop) : data.crop || '');
      const weather = typeof data === 'object' ? (lang === 'kn' ? (data.weather_kn || data.weather) : lang === 'hi' ? (data.weather_hi || data.weather) : data.weather) : '';
      const sContext = typeof data === 'object' ? (lang === 'kn' ? (data.season_kn || data.season) : lang === 'hi' ? (data.season_hi || data.season) : data.season) : '';
      const sAdvice = typeof data === 'object' ? (lang === 'kn' ? (data.advice_kn || data.advice) : lang === 'hi' ? (data.advice_hi || data.advice) : data.advice) : '';

      const cropsList = Array.isArray(data?.top_crops) ? data.top_crops : [];
      const prefReason = data?.preferred_crop ? (lang === 'kn' ? (data.preferred_crop.reason_kn || data.preferred_crop.reason) : lang === 'hi' ? (data.preferred_crop.reason_hi || data.preferred_crop.reason) : data.preferred_crop.reason_en || data.preferred_crop.reason) : '';

      const canonicalCrop = (typeof data === 'object' && data?.preferred_crop?.crop_key)
        ? data.preferred_crop.crop_key
        : (typeof data === 'object' && Array.isArray(data?.top_crops) && data.top_crops[0]?.crop_key)
          ? data.top_crops[0].crop_key
          : text;

      setResult(text);
      setTopCrops(cropsList);
      setPreferredReason(prefReason);
      if (weather) setWeatherInfo(weather);
      if (sContext) setSeasonContext(sContext);
      if (sAdvice) setSeasonAdvice(sAdvice);
      onResult?.({ crop: canonicalCrop, displayCrop: text, city: district, season: season, topCrops: cropsList, data: data });

      setTimeout(() => {
        const resEl = document.getElementById('crop-result-card') || document.getElementById('crop');
        if (resEl) {
          resEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
      }, 100);
    } catch (err) {
      console.error('Crop Recommendation Error:', err);
      setResult(err?.message || 'Could not get a crop recommendation. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  const displayCropName = cropData
    ? (getCropName(cropData?.preferred_crop?.crop_key || cropData?.crop, lang) || (lang === 'kn' ? (cropData.crop_kn || cropData.crop) : lang === 'hi' ? (cropData.crop_hi || cropData.crop) : cropData.crop || ''))
    : result;

  const displayWeatherInfo = cropData
    ? (lang === 'kn' ? (cropData.weather_kn || cropData.weather) : lang === 'hi' ? (cropData.weather_hi || cropData.weather) : cropData.weather)
    : weatherInfo;

  const displaySeasonContext = cropData
    ? (lang === 'kn' ? (cropData.season_kn || cropData.season) : lang === 'hi' ? (cropData.season_hi || cropData.season) : cropData.season)
    : seasonContext;

  const displaySeasonAdvice = cropData
    ? (lang === 'kn' ? (cropData.advice_kn || cropData.advice) : lang === 'hi' ? (cropData.advice_hi || cropData.advice) : cropData.advice)
    : seasonAdvice;

  const displayPreferredReason = cropData?.preferred_crop
    ? (lang === 'kn' ? (cropData.preferred_crop.reason_kn || cropData.preferred_crop.reason) : lang === 'hi' ? (cropData.preferred_crop.reason_hi || cropData.preferred_crop.reason) : (cropData.preferred_crop.reason_en || cropData.preferred_crop.reason))
    : preferredReason;

  return (
    <div className="section-box" id="crop">
      <div className="section-header">
        <span className="section-icon">🌱</span>
        <div>
          <h2>{t('cropTitle')}</h2>
          <p className="section-desc">{t('cropDesc')}</p>
        </div>
      </div>

      <div className="info-note" style={{ marginBottom: '16px' }}>
        <strong>{t('cropStep1')}</strong>
        <br />
        <small>{t('cropAutoFillHint')}</small>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group">
            <label className="form-label">{t('cropDistrictAutoFillLabel')}</label>
            <select className="gov-select" onChange={(e) => autoFillSoilData(e.target.value)} value={district} required>
              <option value="">-- {lang === 'kn' ? 'ಜಿಲ್ಲೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ' : lang === 'hi' ? 'जिला चुनें' : 'Select District'} --</option>
              {DISTRICTS.map((d) => (
                <option key={d} value={d}>{getDistrictDropdownLabel(d, lang)}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">{t('farmingSeason')}</label>
            <select className="gov-select" value={season} onChange={(e) => setSeason(e.target.value)}>
              <option value="auto">{t('seasonAuto')}</option>
              <option value="Kharif">{t('seasonKharif')}</option>
              <option value="Rabi">{t('seasonRabi')}</option>
              <option value="Zaid">{t('seasonZaid')}</option>
              <option value="Whole Year">{t('seasonWholeYear')}</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">{t('nitrogen')}</label>
            <input
              type="number" placeholder="0-150" required className="gov-input"
              value={soil.nitrogen} onChange={(e) => updateField('nitrogen', e.target.value)}
            />
          </div>
          <div className="form-group">
            <label className="form-label">{t('phosphorus')}</label>
            <input
              type="number" placeholder="0-150" required className="gov-input"
              value={soil.phosphorus} onChange={(e) => updateField('phosphorus', e.target.value)}
            />
          </div>
          <div className="form-group">
            <label className="form-label">{t('potassium')}</label>
            <input
              type="number" placeholder="0-150" required className="gov-input"
              value={soil.potassium} onChange={(e) => updateField('potassium', e.target.value)}
            />
          </div>
          <div className="form-group">
            <label className="form-label">{t('phValue')}</label>
            <input
              type="number" step="0.1" placeholder="0-14" required className="gov-input"
              value={soil.ph} onChange={(e) => updateField('ph', e.target.value)}
            />
          </div>
          <div className="form-group" style={{ gridColumn: 'span 2' }}>
            <label className="form-label">{t('rainfall')}</label>
            <input
              type="number" step="0.1" placeholder="e.g. 200" required className="gov-input"
              value={soil.rainfall} onChange={(e) => updateField('rainfall', e.target.value)}
            />
          </div>
        </div>
        <button type="submit" className="gov-btn" disabled={loading}>
          {loading ? '…' : t('recommendCrop')}
        </button>
      </form>

      {displayWeatherInfo && <div className="weather-info">🌤 {displayWeatherInfo}</div>}

      {displayCropName && (
        <div className="result-card crop-result" id="crop-result-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '12px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', flexWrap: 'wrap', gap: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '18px' }}>
              <span className="result-icon">{topCrops[0]?.sowing_passed ? '⚠️' : '🌟'}</span>
              <div>
                <span style={{
                  display: 'inline-block',
                  fontSize: '11px',
                  textTransform: 'uppercase',
                  fontWeight: 'bold',
                  letterSpacing: '0.5px',
                  background: topCrops[0]?.sowing_passed ? '#fff3e0' : '#e8f5e9',
                  color: topCrops[0]?.sowing_passed ? '#d84315' : '#1b5e20',
                  padding: '2px 8px',
                  borderRadius: '12px',
                  marginBottom: '4px',
                  border: `1px solid ${topCrops[0]?.sowing_passed ? '#ffcc80' : '#c8e6c9'}`
                }}>
                  {topCrops[0]?.sowing_passed
                    ? (lang === 'kn' ? '⚠️ ಬಿತ್ತನೆ ಅವಧಿ ಮುಗಿದಿರುವ ಸಾಧ್ಯತೆ - KVK ಜೊತೆ ದೃಢೀಕರಿಸಿ' : lang === 'hi' ? '⚠️ बुवाई अवधि समाप्त होने की संभावना - KVK से पुष्टि करें' : '⚠️ Sowing Window Likely Passed - Confirm with KVK')
                    : (lang === 'kn' ? '🌟 #1 ಪ್ರಸ್ತುತ ಹವಾಮಾನಕ್ಕೆ ಅತ್ಯಂತ ಸೂಕ್ತ ಬೆಳೆ' : lang === 'hi' ? '🌟 #1 वर्तमान मौसम के अनुसार सर्वाधिक उपयुक्त फसल' : '🌟 #1 Most Preferred for Current Weather')}
                </span>
                <br />
                <strong>{displayCropName.startsWith('Recommended Crop') || displayCropName.startsWith('ಶಿಫಾರಸು') || displayCropName.startsWith('अनुशंसित') ? displayCropName : `${lang === 'kn' ? 'ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆ' : lang === 'hi' ? 'अनुशंसित फसल' : 'Recommended Crop'}: ${displayCropName}`}</strong>
              </div>
            </div>
          </div>

          {displayPreferredReason && (
            <div style={{
              fontSize: '13.5px',
              fontWeight: 500,
              color: '#1b5e20',
              background: 'rgba(232, 245, 233, 0.85)',
              padding: '10px 14px',
              borderRadius: '8px',
              width: '100%',
              borderLeft: '4px solid #2e7d32',
              lineHeight: 1.45
            }}>
              {displayPreferredReason}
            </div>
          )}

          {displaySeasonContext && (
            <div style={{ fontSize: '14px', fontWeight: 600, color: '#2e7d32' }}>
              {displaySeasonContext}
            </div>
          )}
          {displaySeasonAdvice && (
            <div style={{ fontSize: '13px', fontWeight: 'normal', color: '#33691e', background: 'rgba(255,255,255,0.7)', padding: '8px 12px', borderRadius: '6px', width: '100%', border: '1px dashed #a5d6a7', lineHeight: 1.4 }}>
              💡 {displaySeasonAdvice}
            </div>
          )}
          {cropData?.fertilizer_plan && (
            <div style={{ fontSize: '13px', fontWeight: 'normal', color: '#1b5e20', background: 'rgba(232, 245, 233, 0.9)', padding: '8px 12px', borderRadius: '6px', width: '100%', border: '1px solid #81c784', lineHeight: 1.4 }}>
              {cropData.fertilizer_plan}
            </div>
          )}

          {/* Top 2-3 Regional Crops Grid */}
          {topCrops && topCrops.length > 1 && (
            <div style={{ width: '100%', marginTop: '10px', borderTop: '1px solid #c8e6c9', paddingTop: '12px' }}>
              <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#1b5e20', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                🌾 {lang === 'kn' ? 'ಈ ಜಿಲ್ಲೆಯಲ್ಲಿ ಬೆಳೆಯುವ ಪ್ರಮುಖ 3 ಬೆಳೆಗಳು ಮತ್ತು ಹವಾಮಾನ ಹೊಂದಾಣಿಕೆ:' : lang === 'hi' ? 'इस जिले की शीर्ष 3 फसलें और मौसम अनुकूलता:' : 'Top 3 Crops Grown in This District & Weather Match:'}
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '10px', width: '100%' }}>
                {topCrops.map((c, idx) => {
                  const cropName = getCropName(c.crop_key || c.name, lang) || (lang === 'kn' ? (c.name_kn || c.name) : lang === 'hi' ? (c.name_hi || c.name) : c.name_en || c.name);
                  const reason = lang === 'kn' ? (c.reason_kn || c.reason) : lang === 'hi' ? (c.reason_hi || c.reason) : c.reason_en || c.reason;
                  const sowing = lang === 'kn' ? (c.sowing_kn || c.sowing_en) : lang === 'hi' ? (c.sowing_hi || c.sowing_en) : c.sowing_en;
                  const harvest = lang === 'kn' ? (c.harvest_kn || c.harvest_en) : lang === 'hi' ? (c.harvest_hi || c.harvest_en) : c.harvest_en;
                  const warningText = lang === 'kn' ? (c.sowing_warning_kn || c.sowing_warning) : lang === 'hi' ? (c.sowing_warning_hi || c.sowing_warning) : (c.sowing_warning_en || c.sowing_warning);

                  const isPassed = c.sowing_status === 'passed' || c.sowing_passed;
                  const isClosing = c.sowing_status === 'closing_soon';
                  const matchColor = c.score >= 85 ? '#2e7d32' : c.score >= 70 ? '#f57f17' : '#e65100';
                  const barColor = c.score >= 85 ? '#43a047' : c.score >= 70 ? '#fbc02d' : '#fb8c00';
                  const tierLabel = c.score >= 85
                    ? (lang === 'kn' ? 'ಉನ್ನತ ಹೊಂದಾಣಿಕೆ' : lang === 'hi' ? 'उच्च अनुकूलता' : 'High Match')
                    : c.score >= 70
                      ? (lang === 'kn' ? 'ಮಧ್ಯಮ ಹೊಂದಾಣಿಕೆ' : lang === 'hi' ? 'मध्यम अनुकूलता' : 'Medium Match')
                      : (lang === 'kn' ? 'ಕಡಿಮೆ ಹೊಂದಾಣಿಕೆ' : lang === 'hi' ? 'कम अनुकूलता' : 'Low Match');

                  return (
                    <div
                      key={c.crop_key || idx}
                      style={{
                        background: '#ffffff',
                        border: `1px solid ${isPassed ? '#ffcc80' : c.is_preferred ? '#66bb6a' : '#e0e0e0'}`,
                        borderRadius: '8px',
                        padding: '12px',
                        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '6px'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{
                          fontSize: '11px',
                          fontWeight: 'bold',
                          padding: '2px 8px',
                          borderRadius: '10px',
                          background: isPassed ? '#ffebee' : isClosing ? '#fff8e1' : c.is_preferred ? '#e8f5e9' : '#f5f5f5',
                          color: isPassed ? '#c62828' : isClosing ? '#f57f17' : c.is_preferred ? '#2e7d32' : '#616161',
                          border: `1px solid ${isPassed ? '#ffcdd2' : isClosing ? '#ffe082' : c.is_preferred ? '#a5d6a7' : '#e0e0e0'}`
                        }}>
                          {isPassed
                            ? (lang === 'kn' ? '⚠️ ಬಿತ್ತನೆ ಅವಧಿ ಮೀರಿದೆ' : lang === 'hi' ? '⚠️ बुवाई समाप्त' : '⚠️ Sowing Window Passed')
                            : isClosing
                              ? (lang === 'kn' ? '⏳ ಕೊನೆಗೊಳ್ಳುತ್ತಿದೆ' : lang === 'hi' ? '⏳ बुवाई जल्द समाप्त' : '⏳ Sowing Closing Soon')
                              : c.is_preferred
                                ? (lang === 'kn' ? '🌟 #1 ಅತ್ಯಂತ ಸೂಕ್ತ' : lang === 'hi' ? '🌟 #1 सर्वाधिक उपयुक्त' : '🌟 #1 Most Preferred')
                                : (lang === 'kn' ? `🌱 #${c.rank} ಪರ್ಯಾಯ ಬೆಳೆ` : lang === 'hi' ? `🌱 #${c.rank} वैकल्पिक फसल` : `🌱 #${c.rank} Alternative`)}
                        </span>
                        <span style={{ fontSize: '12px', fontWeight: 'bold', color: matchColor }}>
                          {Math.round(c.score)}% ({tierLabel})
                        </span>
                      </div>

                      <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#2e7d32' }}>
                        {cropName}
                      </div>

                      <div style={{ width: '100%', background: '#eeeeee', height: '6px', borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{ width: `${Math.min(100, Math.round(c.score))}%`, background: barColor, height: '100%' }} />
                      </div>

                      <div style={{ fontSize: '12px', color: '#37474f', lineHeight: 1.35, marginTop: '2px' }}>
                        {reason}
                      </div>

                      {warningText && (
                        <div style={{
                          fontSize: '11px',
                          fontWeight: 500,
                          color: isPassed ? '#b71c1c' : '#e65100',
                          background: isPassed ? '#ffebee' : '#fff3e0',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          border: `1px solid ${isPassed ? '#ffcdd2' : '#ffe0b2'}`,
                          marginTop: '2px'
                        }}>
                          ⚠️ {warningText}
                        </div>
                      )}

                      <div style={{ fontSize: '11px', color: '#616161', display: 'flex', gap: '8px', marginTop: '4px', flexWrap: 'wrap' }}>
                        <span style={{ background: '#f1f8e9', padding: '2px 6px', borderRadius: '4px' }}>
                          {(c.crop_key === 'tomato' || c.name_en === 'Tomato')
                            ? (lang === 'kn' ? '🌱 ನರ್ಸರಿ / ನಾಟಿ' : lang === 'hi' ? '🌱 नर्सरी / रोपाई' : '🌱 Nursery / transplanting')
                            : (lang === 'kn' ? '🗓 ಬಿತ್ತನೆ' : lang === 'hi' ? '🗓 बुवाई' : '🗓 Sowing')}: {sowing}
                        </span>
                        <span style={{ background: '#f1f8e9', padding: '2px 6px', borderRadius: '4px' }}>
                          🌾 {lang === 'kn' ? 'ಕೊಯ್ಲು' : lang === 'hi' ? 'कटाई' : 'Harvest'}: {harvest}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>

              <div style={{ fontSize: '11.5px', color: '#555555', fontStyle: 'italic', marginTop: '12px', background: '#f9fbe7', padding: '8px 12px', borderRadius: '6px', border: '1px solid #e6ee9c' }}>
                📌 {lang === 'kn'
                  ? `ಸೂಚನೆ: ಅಂದಾಜು ಹೊಂದಾಣಿಕೆ ಸ್ಕೋರ್ ಹವಾಮಾನ ಮತ್ತು ಋತುವಿನ ಆಧಾರದ ಮೇಲೆ ನೀಡಲಾಗಿದೆ. ನಿಖರ ತೀರ್ಮಾನಕ್ಕೆ ಸ್ಥಳೀಯ ${topCrops[0]?.kvk || 'ಕೆವಿಕೆ'} / ${topCrops[0]?.university || 'ಕೃಷಿ ವಿಶ್ವವಿದ್ಯಾಲಯ'} ಸಂಪರ್ಕಿಸಿ.`
                  : lang === 'hi'
                    ? `नोट: अनुमानित उपयुक्तता स्कोर मौसम और ऋतु पर आधारित है। अंतिम निर्णय से पूर्व स्थानीय ${topCrops[0]?.kvk || 'केवीके'} / ${topCrops[0]?.university || 'कृषि विश्वविद्यालय'} से पुष्टि करें।`
                    : `Note: Estimated suitability score based on weather and season; confirm with your local ${topCrops[0]?.kvk || 'ICAR-KVK'} / ${topCrops[0]?.university || 'State Agricultural University'}.`}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

