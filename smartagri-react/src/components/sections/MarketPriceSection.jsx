import { useState, useEffect } from 'react';
import { useLanguage } from '../../context/LanguageContext.jsx';
import { api } from '../../api.js';
import { CROPS, DISTRICTS, getCropName, getDistrictName, getDistrictDropdownLabel } from '../../data/districts.js';

export default function MarketPriceSection({ onResult, recommendedCrop, city }) {
  const { t, lang } = useLanguage();
  const currentMonth = new Date().getMonth() + 1;
  const currentYear = new Date().getFullYear();

  const [crop, setCrop] = useState('');
  const [district, setDistrict] = useState('');
  const [month, setMonth] = useState(String(currentMonth));
  const [year, setYear] = useState(String(currentYear));
  const [result, setResult] = useState('');
  const [priceData, setPriceData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [autoFetched, setAutoFetched] = useState(false);

  // Auto-chain input from Crop Recommendation Agent
  useEffect(() => {
    let matchedCrop = '';
    if (recommendedCrop) {
      const recClean = recommendedCrop.toLowerCase().replace(/[^a-z0-9]/g, '');
      const found = CROPS.find((c) => {
        const cClean = c.toLowerCase().replace(/[^a-z0-9]/g, '');
        return cClean === recClean || recClean.includes(cClean) || cClean.includes(recClean);
      });
      matchedCrop = found || (recommendedCrop.charAt(0).toUpperCase() + recommendedCrop.slice(1));
    }

    let matchedDist = '';
    if (city) {
      const cityClean = city.toLowerCase().replace(/[^a-z0-9]/g, '');
      const foundDist = DISTRICTS.find((d) => {
        const dClean = d.toLowerCase().replace(/[^a-z0-9]/g, '');
        return dClean === cityClean || cityClean.includes(dClean) || dClean.includes(cityClean);
      });
      matchedDist = foundDist || city;
    }

    if (matchedCrop) {
      setCrop(matchedCrop);
    }
    if (matchedDist) {
      setDistrict(matchedDist);
    }

    // Auto-predict price if both crop and district are chained from previous agent
    if (matchedCrop && matchedDist) {
      fetchPricePrediction(matchedCrop, matchedDist, String(currentMonth), String(currentYear), true);
    }
  }, [recommendedCrop, city]);

  async function fetchPricePrediction(c, d, m, y, isAuto = false) {
    if (!c || !d || !m || !y) return;
    setLoading(true);
    try {
      const data = await api.predictPrice(c, d, m, y, lang);
      setPriceData(data);
      const text = typeof data === 'string' 
        ? data 
        : (lang === 'kn' ? (data.result_kn || data.result) : lang === 'hi' ? (data.result_hi || data.result) : (data.result_en || data.result || data.forecast_text || `₹ ${data.prediction}`));
      setResult(text);
      setAutoFetched(isAuto);
      onResult?.({ crop: c, priceText: text, data: data });
    } catch (err) {
      setResult('Could not fetch a price prediction. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    await fetchPricePrediction(crop, district, month, year, false);
  }

  const activeResult = priceData
    ? (lang === 'kn' ? (priceData.result_kn || priceData.result) : lang === 'hi' ? (priceData.result_hi || priceData.result) : (priceData.result_en || priceData.result || priceData.forecast_text))
    : result;

  // Ensure selected crop and district are in the option list even if custom/fallback
  const allCrops = crop && !CROPS.includes(crop) ? [crop, ...CROPS] : CROPS;
  const allDistricts = district && !DISTRICTS.includes(district) ? [district, ...DISTRICTS] : DISTRICTS;

  return (
    <div className="section-box" id="price">
      <span id="market-price" style={{ display: 'block', position: 'relative', top: '-20px', visibility: 'hidden' }} />
      <div className="section-header">
        <span className="section-icon">💰</span>
        <div>
          <h2>{t('priceTitle')}</h2>
          <p className="section-desc">{t('priceDesc')}</p>
        </div>
      </div>

      {recommendedCrop && (
        <div className="info-note" style={{ background: '#e8f5e9', borderColor: '#81c784', marginBottom: '16px' }}>
          🔗 <strong>Agent Chaining Active:</strong> Auto-fetched <strong>{getCropName(crop || recommendedCrop, lang)}</strong> in <strong>{getDistrictName(district || city, lang) || 'your district'}</strong> from the Crop Recommendation Agent!
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group">
            <label className="form-label">{t('selectCropLabel')}</label>
            <select className="gov-select" value={crop} onChange={(e) => setCrop(e.target.value)} required>
              <option value="">{t('selectCrop')}</option>
              {allCrops.map((c) => (
                <option key={c} value={c}>{getCropName(c, lang)}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">{t('selectDistrictLabel')}</label>
            <select className="gov-select" value={district} onChange={(e) => setDistrict(e.target.value)} required>
              <option value="">{lang === 'kn' ? '-- ಜಿಲ್ಲೆ ಆಯ್ಕೆ ಮಾಡಿ --' : (lang === 'hi' ? '-- जिला चुनें --' : '-- Select District --')}</option>
              {allDistricts.map((d) => (
                <option key={d} value={d}>{getDistrictDropdownLabel(d, lang)}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">{t('month')}</label>
            <input
              type="number" min="1" max="12" placeholder="1-12" required
              className="gov-input" value={month} onChange={(e) => setMonth(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label className="form-label">{t('year')}</label>
            <input
              type="number" min="2020" max="2035" placeholder="2024" required
              className="gov-input" value={year} onChange={(e) => setYear(e.target.value)}
            />
          </div>
        </div>

        <button type="submit" className="gov-btn" disabled={loading}>
          {loading ? 'Predicting Market Mandi Price…' : t('predictPrice')}
        </button>
      </form>

      {activeResult && (
        <div className="result-card price-result" style={{ marginTop: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
            <span className="result-icon" style={{ fontSize: '1.35rem', marginTop: '2px' }}>💹</span>
            <div style={{ fontSize: '0.95rem', fontWeight: '500', lineHeight: '1.6', color: '#1b4d3e', display: 'flex', flexDirection: 'column', gap: '8px', width: '100%' }}>
              {typeof activeResult === 'string' ? (
                activeResult.split('\n').filter(Boolean).map((line, idx, arr) => {
                  const isWarn = line.includes('⚠️') || line.includes('Warning') || line.includes('Alert') || line.includes('BELOW');
                  return (
                    <div
                      key={idx}
                      style={{
                        padding: isWarn ? '8px 12px' : '4px 0',
                        background: isWarn ? '#fff3e0' : 'transparent',
                        color: isWarn ? '#b71c1c' : '#1b4d3e',
                        borderRadius: isWarn ? '6px' : '0',
                        border: isWarn ? '1px solid #ffcc80' : 'none',
                        fontWeight: isWarn ? '600' : '500',
                        paddingBottom: (!isWarn && idx < arr.length - 1) ? '6px' : isWarn ? '8px' : '0',
                        borderBottom: (!isWarn && idx < arr.length - 1) ? '1px dashed rgba(27, 77, 62, 0.15)' : 'none'
                      }}
                    >
                      {line}
                    </div>
                  );
                })
              ) : (
                <span>{result}</span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
