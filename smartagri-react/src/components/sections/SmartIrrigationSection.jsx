import { useState, useEffect } from 'react';
import { useLanguage } from '../../context/LanguageContext.jsx';
import { api } from '../../api.js';
import {
  CROPS,
  DISTRICTS,
  GROWTH_STAGES,
  SOIL_TYPES,
  IRRIGATION_METHODS,
  getCropName,
  getDistrictName,
  getDistrictDropdownLabel,
  matchCropKey,
  matchDistrictKey
} from '../../data/districts.js';

export default function SmartIrrigationSection({
  recommendedCrop = '',
  city = '',
  onResult
}) {
  const { t, lang } = useLanguage();

  const [crop, setCrop] = useState('');
  const [growthStage, setGrowthStage] = useState('vegetative');
  const [soilType, setSoilType] = useState('loam');
  const [areaAcres, setAreaAcres] = useState('1.0');
  const [irrigationType, setIrrigationType] = useState('drip');
  const [district, setDistrict] = useState('');
  const [daysAfterSowing, setDaysAfterSowing] = useState('');
  const [pumpFlowRate, setPumpFlowRate] = useState('10000');
  const [irrigationEfficiency, setIrrigationEfficiency] = useState('90');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [resultData, setResultData] = useState(null);

  // Auto-sync crop if recommended crop changes
  useEffect(() => {
    if (recommendedCrop) {
      const matched = matchCropKey(recommendedCrop);
      if (matched) {
        setCrop(matched);
      } else {
        setCrop(recommendedCrop);
      }
    }
  }, [recommendedCrop]);

  // Auto-sync district if city/district changes
  useEffect(() => {
    if (city) {
      const matched = matchDistrictKey(city);
      if (matched) {
        setDistrict(matched);
      } else {
        setDistrict(city);
      }
    }
  }, [city]);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const payload = {
        crop: crop || 'Tomato',
        growth_stage: growthStage,
        soil_type: soilType,
        area_acres: parseFloat(areaAcres) || 1.0,
        irrigation_type: irrigationType,
        district: district || 'Dharwad',
        days_after_sowing: daysAfterSowing !== '' ? parseInt(daysAfterSowing, 10) : undefined,
        pump_flow_rate: parseFloat(pumpFlowRate) || 10000.0,
        irrigation_efficiency: parseFloat(irrigationEfficiency) || 90.0,
        lang: lang || 'en'
      };

      const res = await api.predictIrrigation(payload);
      if (res && res.status === 'success' && res.data) {
        setResultData(res.data);
        if (onResult) {
          onResult(res.data);
        }
      } else if (res && res.data) {
        setResultData(res.data);
        if (onResult) onResult(res.data);
      } else {
        setError(res?.message || 'Could not calculate irrigation requirements.');
      }
    } catch (err) {
      setError(err.message || 'Error communicating with Precision Irrigation Agent.');
    } finally {
      setLoading(false);
    }
  }

  const adviceText = resultData
    ? lang === 'kn'
      ? resultData.advice_kn || resultData.advice_en
      : lang === 'hi'
      ? resultData.advice_hi || resultData.advice_en
      : resultData.advice_en
    : '';

  const runtimeText = resultData
    ? lang === 'kn'
      ? resultData.runtime_kn || resultData.runtime_en
      : lang === 'hi'
      ? resultData.runtime_hi || resultData.runtime_en
      : resultData.runtime_en
    : '';

  const freqText = resultData
    ? lang === 'kn'
      ? resultData.frequency_kn || resultData.frequency_en
      : lang === 'hi'
      ? resultData.frequency_hi || resultData.frequency_en
      : resultData.frequency_en
    : '';

  const rainAlertText = resultData?.rain_alert
    ? lang === 'kn'
      ? resultData.rain_alert_kn || resultData.rain_alert_en
      : lang === 'hi'
      ? resultData.rain_alert_hi || resultData.rain_alert_en
      : resultData.rain_alert_en
    : '';

  const allCrops = crop && !CROPS.includes(crop) ? [crop, ...CROPS] : CROPS;
  const allDistricts = district && !DISTRICTS.includes(district) ? [district, ...DISTRICTS] : DISTRICTS;

  return (
    <div className="section-box" id="irrigation">
      <span id="smart-irrigation" style={{ display: 'block', position: 'relative', top: '-20px', visibility: 'hidden' }} />
      <div className="section-header">
        <span className="section-icon" role="img" aria-label="Water droplet">
          💧
        </span>
        <div>
          <h2>{t('irrigationTitle')}</h2>
          <p className="section-desc">{t('irrigationDesc')}</p>
        </div>
      </div>

      {recommendedCrop && (
        <div className="info-note" style={{ background: '#e0f2fe', borderColor: '#7dd3fc', marginBottom: '16px' }}>
          🔗 <strong>Agent Chaining Active:</strong> Auto-fetched <strong>{getCropName(crop || recommendedCrop, lang)}</strong> in <strong>{getDistrictName(district || city, lang) || 'your district'}</strong> from the Crop Recommendation Agent!
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          {/* Select Crop */}
          <div className="form-group">
            <label className="form-label">{t('selectCropLabel')}</label>
            <select
              value={crop}
              onChange={(e) => setCrop(e.target.value)}
              required
              className="gov-select"
            >
              <option value="">{t('selectCrop')}</option>
              {allCrops.map((c) => (
                <option key={c} value={c}>
                  {getCropName(c, lang)}
                </option>
              ))}
            </select>
          </div>

          {/* Growth Stage */}
          <div className="form-group">
            <label className="form-label">{t('growthStage')}</label>
            <select
              value={growthStage}
              onChange={(e) => setGrowthStage(e.target.value)}
              required
              className="gov-select"
            >
              {Object.entries(GROWTH_STAGES).map(([key, dict]) => (
                <option key={key} value={key}>
                  {dict[lang] || dict.en}
                </option>
              ))}
            </select>
          </div>

          {/* Soil Texture */}
          <div className="form-group">
            <label className="form-label">{t('soilTexture')}</label>
            <select
              value={soilType}
              onChange={(e) => setSoilType(e.target.value)}
              required
              className="gov-select"
            >
              {Object.entries(SOIL_TYPES).map(([key, dict]) => (
                <option key={key} value={key}>
                  {dict[lang] || dict.en}
                </option>
              ))}
            </select>
          </div>

          {/* Land Area (Acres) */}
          <div className="form-group">
            <label className="form-label">{t('landArea')}</label>
            <input
              type="number"
              step="0.1"
              min="0.1"
              max="100.0"
              value={areaAcres}
              onChange={(e) => setAreaAcres(e.target.value)}
              placeholder="1.0"
              required
              className="gov-input"
            />
          </div>

          {/* Irrigation System */}
          <div className="form-group">
            <label className="form-label">{t('irrigationSystem')}</label>
            <select
              value={irrigationType}
              onChange={(e) => setIrrigationType(e.target.value)}
              required
              className="gov-select"
            >
              {Object.entries(IRRIGATION_METHODS).map(([key, dict]) => (
                <option key={key} value={key}>
                  {dict[lang] || dict.en}
                </option>
              ))}
            </select>
          </div>

          {/* Location District */}
          <div className="form-group">
            <label className="form-label">{t('locationDistrict')}</label>
            <select
              value={district}
              onChange={(e) => setDistrict(e.target.value)}
              required
              className="gov-select"
            >
              <option value="">{t('selectDistrictLabel')}</option>
              {allDistricts.map((d) => (
                <option key={d} value={d}>
                  {getDistrictDropdownLabel(d, lang)}
                </option>
              ))}
            </select>
          </div>

          {/* Days After Sowing (DAS) */}
          <div className="form-group">
            <label className="form-label">
              {lang === 'kn' ? 'ಬಿತ್ತನೆಯ ನಂತರದ ದಿನಗಳು (DAS)' : lang === 'hi' ? 'बुवाई के बाद के दिन (DAS)' : 'Days After Sowing (DAS)'}
            </label>
            <input
              type="number"
              min="0"
              max="180"
              value={daysAfterSowing}
              onChange={(e) => setDaysAfterSowing(e.target.value)}
              placeholder="e.g. 0 (sowing), 21 (CRI), 60 (jointing)"
              className="gov-input"
            />
          </div>

          {/* Pump Flow Rate */}
          <div className="form-group">
            <label className="form-label">
              {lang === 'kn' ? 'ಪಂಪ್ ಹರಿವು (ಲೀಟರ್/ಗಂಟೆ)' : lang === 'hi' ? 'पंप प्रवाह दर (लीटर/घंटा)' : 'Pump Flow Rate (L/hr)'}
            </label>
            <input
              type="number"
              min="1000"
              step="500"
              value={pumpFlowRate}
              onChange={(e) => setPumpFlowRate(e.target.value)}
              placeholder="10000"
              className="gov-input"
            />
          </div>

          {/* Irrigation System Efficiency (%) */}
          <div className="form-group">
            <label className="form-label">
              {lang === 'kn' ? 'ನೀರಾವರಿ ದಕ್ಷತೆ (%)' : lang === 'hi' ? 'सिंचाई दक्षता (%)' : 'System Efficiency (%)'}
            </label>
            <input
              type="number"
              min="30"
              max="100"
              value={irrigationEfficiency}
              onChange={(e) => setIrrigationEfficiency(e.target.value)}
              placeholder="90"
              className="gov-input"
            />
          </div>
        </div>

        <div style={{ marginTop: '16px' }}>
          <button type="submit" className="gov-btn" disabled={loading}>
            {loading ? '⏳ Calculating Water Requirements...' : t('calculateIrrigation')}
          </button>
        </div>
      </form>

      {error && (
        <div style={{ marginTop: '14px', color: '#b91c1c', fontWeight: 'bold' }}>
          ⚠ {error}
        </div>
      )}

      {resultData && (
        <div
          className="result-card"
          style={{
            marginTop: '18px',
            borderLeft: '4px solid #0284c7',
            background: 'linear-gradient(180deg, #f0f9ff 0%, #ffffff 100%)',
            boxShadow: '0 4px 12px rgba(2, 132, 199, 0.08)'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
            <span style={{ fontSize: '30px' }} role="img" aria-label="water">
              💧
            </span>
            <div style={{ flex: 1 }}>
              <div style={{ marginBottom: '8px' }}>
                <h4 style={{ margin: 0, color: '#0369a1', fontSize: '17px' }}>
                  {t('waterReqSchedule')}
                </h4>
              </div>

              <p
                style={{
                  margin: '6px 0 12px 0',
                  fontSize: '15px',
                  fontWeight: '600',
                  color: '#0f172a',
                  lineHeight: '1.5'
                }}
              >
                {adviceText}
              </p>

              {/* 4 Metric Tiles */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                  gap: '10px',
                  marginTop: '10px',
                  padding: '12px',
                  background: '#ffffff',
                  borderRadius: '8px',
                  border: '1px solid #e0f2fe'
                }}
              >
                <div>
                  <small style={{ color: '#64748b', display: 'block', marginBottom: '2px' }}>
                    {t('totalDailyWater')}
                  </small>
                  <div style={{ fontWeight: '700', color: resultData.is_rain_paused || resultData.total_litres_day === 0 ? '#059669' : '#0284c7', fontSize: '16px' }}>
                    {resultData.is_rain_paused || resultData.total_litres_day === 0
                      ? `0 Litres/day (Rain-Met)`
                      : `${resultData.total_litres_day?.toLocaleString()} Litres/day`}
                  </div>
                  {(resultData.is_rain_paused || resultData.total_litres_day === 0) && resultData.base_total_litres_day > 0 && (
                    <small style={{ color: '#0369a1', display: 'block', marginTop: '2px', fontSize: '11.5px', fontWeight: '500' }}>
                      Normal: {resultData.base_total_litres_day?.toLocaleString()} L/day
                    </small>
                  )}
                </div>

                <div>
                  <small style={{ color: '#64748b', display: 'block', marginBottom: '2px' }}>
                    {t('pumpRuntime')}
                  </small>
                  <div style={{ fontWeight: '700', color: resultData.is_rain_paused || resultData.run_mins === 0 ? '#059669' : '#0369a1', fontSize: '16px' }}>
                    {runtimeText}
                  </div>
                  {(resultData.is_rain_paused || resultData.run_mins === 0) && resultData.base_runtime_en && (
                    <small style={{ color: '#0369a1', display: 'block', marginTop: '2px', fontSize: '11.5px', fontWeight: '500' }}>
                      Normal: {lang === 'kn' ? resultData.base_runtime_kn : lang === 'hi' ? resultData.base_runtime_hi : resultData.base_runtime_en}
                    </small>
                  )}
                </div>

                <div>
                  <small style={{ color: '#64748b', display: 'block', marginBottom: '2px' }}>
                    {t('frequency')}
                  </small>
                  <div style={{ fontWeight: '700', color: '#0f766e', fontSize: '15px' }}>
                    {freqText}
                  </div>
                </div>

                <div>
                  <small style={{ color: '#64748b', display: 'block', marginBottom: '2px' }}>
                    {t('liveWeatherIndex')}
                  </small>
                  <div style={{ fontWeight: '600', color: '#475569', fontSize: '14px' }}>
                    {resultData.temp}°C | {resultData.humidity}% RH | ET₀: {resultData.et0} mm{resultData.rainfall_mm > 0 ? ` | Rain: ${resultData.rainfall_mm}mm` : ''}
                  </div>
                </div>
              </div>

              {/* Rain Alert Warning Banner if rain forecast or detected */}
              {resultData.rain_alert && (
                <div
                  style={{
                    marginTop: '12px',
                    padding: '10px 14px',
                    background: '#fef2f2',
                    border: '1px solid #fecaca',
                    borderRadius: '6px',
                    color: '#991b1b',
                    fontWeight: '600',
                    fontSize: '14px',
                    lineHeight: '1.4'
                  }}
                >
                  {rainAlertText}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
