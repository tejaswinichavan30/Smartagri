import { useState, useEffect } from 'react';
import { useLanguage } from '../../context/LanguageContext.jsx';
import { api } from '../../api.js';
import { matchCropKey, getCropName } from '../../data/districts.js';

export default function DiseaseDetectionSection({ onResult, recommendedCrop }) {
  const { t, lang } = useLanguage();
  const [cropType, setCropType] = useState('tomato');
  const [groupedCrops, setGroupedCrops] = useState({ photo_diagnosis: null, reference_only: null });
  const [isDiagnosable, setIsDiagnosable] = useState(true);

  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [result, setResult] = useState('');
  const [diseaseData, setDiseaseData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isError, setIsError] = useState(false);

  const [diseaseSamples, setDiseaseSamples] = useState([]);
  const [cropNotice, setCropNotice] = useState('');
  const [coverageLine, setCoverageLine] = useState('');
  const [panelTexts, setPanelTexts] = useState({});

  // 1. Fetch grouped crops list from backend config
  useEffect(() => {
    api.getDiseaseCrops(lang)
      .then((res) => {
        if (res && res.groups) {
          setGroupedCrops(res.groups);
          if (res.coverage_line) setCoverageLine(res.coverage_line);
          if (res.panel_texts) setPanelTexts(res.panel_texts);
        }
      })
      .catch((err) => {
        console.warn('Failed to fetch /api/disease_crops:', err);
      });
  }, [lang]);

  // 2. Fetch samples and notices whenever cropType or lang changes
  useEffect(() => {
    if (!cropType) return;
    
    // Check if current crop is diagnosable
    let diagnosable = true;
    if (groupedCrops.reference_only?.crops?.some(c => c.key === cropType)) {
      diagnosable = false;
    }
    setIsDiagnosable(diagnosable);

    api.getCropDiseaseSamples(cropType, lang)
      .then((res) => {
        if (res && res.samples) {
          setDiseaseSamples(res.samples);
          if (res.notice) setCropNotice(res.notice);
          if (res.coverage_line) setCoverageLine(res.coverage_line);
        }
      })
      .catch((err) => {
        console.warn('Failed to fetch /api/crop_disease_samples:', err);
      });
  }, [cropType, lang, groupedCrops]);

  // 3. Auto-sync with recommendedCrop if provided
  useEffect(() => {
    if (!recommendedCrop) return;
    const rawCrop = recommendedCrop;
    const canonical = matchCropKey(rawCrop);
    const targetCrop = (canonical || rawCrop).toLowerCase().trim();
    const cleanTarget = targetCrop.replace(/[^a-z0-9]/g, '');

    const allCrops = [
      ...(groupedCrops.photo_diagnosis?.crops || []),
      ...(groupedCrops.reference_only?.crops || [])
    ];
    const found = allCrops.find(c => {
      const cClean = c.key.toLowerCase().replace(/[^a-z0-9]/g, '');
      return cClean === cleanTarget || c.key.toLowerCase() === targetCrop;
    });

    if (found) {
      setCropType(found.key);
    } else {
      setCropType(targetCrop);
    }
  }, [recommendedCrop, groupedCrops]);

  function handleCropChange(e) {
    const selected = e.target.value;
    setCropType(selected);
    setFile(null);
    setPreviewUrl('');
    setResult('');
    setIsError(false);
  }

  function handleFileChange(e) {
    const selected = e.target.files[0];
    setFile(selected);
    setPreviewUrl(selected ? URL.createObjectURL(selected) : '');
    setResult('');
    setIsError(false);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setIsError(false);
    try {
      const data = await api.predictDisease(file, cropType, lang);
      setDiseaseData(data);
      if (data && (data.status === 'error' || data.status === 'crop_mismatch' || data.is_valid_leaf === false)) {
        const errMsg = (lang === 'kn' ? data.result_kn : (lang === 'hi' ? data.result_hi : data.result)) || data.error || 'Invalid leaf image.';
        setResult(errMsg);
        setIsError(true);
      } else {
        const text = typeof data === 'string' ? data : (lang === 'kn' ? data.result_kn : (lang === 'hi' ? data.result_hi : data.result)) || '';
        setResult(text);
        setIsError(false);
        onResult?.(text);
      }
    } catch (err) {
      const errDetail = err?.body || err?.response?.data || {};
      let fallbackMsg = '';
      if (errDetail && (errDetail.error || errDetail.result)) {
        fallbackMsg = (lang === 'kn' ? errDetail.result_kn : (lang === 'hi' ? errDetail.result_hi : errDetail.result)) || errDetail.error;
      } else {
        fallbackMsg = lang === 'kn'
          ? '❌ ಸರ್ವರ್ ಪ್ರಕ್ರಿಯೆ ವಿಫಲವಾಗಿದೆ. ದಯವಿಟ್ಟು 1 ನಿಮಿಷದ ನಂತರ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.'
          : lang === 'hi'
          ? '❌ सर्वर व्यस्त है या प्रक्रिया विफल रही। कृपया 1 मिनट बाद पुनः प्रयास करें।'
          : '❌ Diagnosis request failed. The cloud server may be spinning up or busy. Please try again in 30 seconds.';
      }
      setResult(fallbackMsg);
      setIsError(true);
    } finally {
      setLoading(false);
    }
  }

  const activeResult = diseaseData
    ? (lang === 'kn' ? (diseaseData.result_kn || diseaseData.result) : lang === 'hi' ? (diseaseData.result_hi || diseaseData.result) : (diseaseData.result_en || diseaseData.result))
    : result;

  return (
    <div className="section-box" id="disease">
      <div className="section-header">
        <span className="section-icon" role="img" aria-label="Leaf">🍃</span>
        <div>
          <h2>{t('diseaseTitle') || 'Leaf Disease Diagnosis & Reference Guide'}</h2>
          <p className="section-desc">{t('diseaseDesc') || 'Instant photo diagnosis for supported crops and symptom reference guide for all other crops.'}</p>
        </div>
      </div>

      <p className="info-note">
        {t('diseaseFileTypes') || '📌 Accepted file types: JPG, JPEG, PNG'}
      </p>

      <form onSubmit={handleSubmit}>
        <div className="form-grid" style={{ marginBottom: '16px' }}>
          <div className="form-group">
            <label className="form-label">
              🌱 {lang === 'kn' ? 'ಬೆಳೆ ಆಯ್ಕೆ ಮಾಡಿ:' : lang === 'hi' ? 'फसल चुनें:' : 'Select Crop:'}
            </label>
            <select
              value={cropType}
              onChange={handleCropChange}
              className="gov-select"
            >
              {groupedCrops.photo_diagnosis && (
                <optgroup label={groupedCrops.photo_diagnosis.label}>
                  {groupedCrops.photo_diagnosis.crops.map((c) => (
                    <option key={c.key} value={c.key}>
                      {c.name} {c.karnataka ? '⭐' : ''}
                    </option>
                  ))}
                </optgroup>
              )}

              {groupedCrops.reference_only && (
                <optgroup label={groupedCrops.reference_only.label}>
                  {groupedCrops.reference_only.crops.map((c) => (
                    <option key={c.key} value={c.key}>
                      {c.name} {c.karnataka ? '⭐' : ''}
                    </option>
                  ))}
                </optgroup>
              )}

              {/* Fallback if groups haven't loaded yet */}
              {!groupedCrops.photo_diagnosis && (
                <>
                  <option value="tomato">Tomato (ಟೊಮೆಟೊ)</option>
                  <option value="potato">Potato (ಆಲೂಗಡ್ಡೆ)</option>
                  <option value="rice">Rice / Paddy (ಭತ್ತ)</option>
                  <option value="wheat">Wheat (ಗೋಧಿ)</option>
                  <option value="corn">Corn / Maize (ಮೆಕ್ಕೆಜೋಳ)</option>
                  <option value="soybean">Soybean (ಸೋಯಾಬೀನ್)</option>
                  <option value="chilli">Chilli (ಮೆಣಸಿನಕಾಯಿ)</option>
                </>
              )}
            </select>
          </div>

          {isDiagnosable ? (
            <div className="form-group">
              <label className="form-label">{t('selectLeafImage') || 'Select Leaf Image'}</label>
              <input
                type="file"
                accept=".jpg,.jpeg,.png,image/jpeg,image/png"
                required
                className="file-input"
                onChange={handleFileChange}
              />
            </div>
          ) : (
            <div className="form-group" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <div style={{
                background: '#f8fafc',
                border: '1px dashed #cbd5e1',
                padding: '12px 14px',
                borderRadius: '8px',
                fontSize: '0.85rem',
                color: '#64748b'
              }}>
                📖 <strong>{lang === 'kn' ? 'ಉಲ್ಲೇಖ ಮಾರ್ಗದರ್ಶಿ ಮಾತ್ರ' : lang === 'hi' ? 'केवल संदर्भ मार्गदर्शिका' : 'Reference Guide Mode'}</strong>: {lang === 'kn' ? 'ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಅಗತ್ಯವಿಲ್ಲ. ಕೆಳಗಿನ ರೋಗ ಲಕ್ಷಣಗಳನ್ನು ವೀಕ್ಷಿಸಿ.' : lang === 'hi' ? 'फोटो अपलोड की आवश्यकता नहीं है। नीचे लक्षण गाइड देखें।' : 'No photo upload needed. View the typical symptoms guide below.'}
              </div>
            </div>
          )}
        </div>

        {isDiagnosable && (
          <button type="submit" className="gov-btn" disabled={loading || !file}>
            {loading ? (lang === 'kn' ? 'ರೋಗ ಪತ್ತೆ ಮಾಡಲಾಗುತ್ತಿದೆ...' : lang === 'hi' ? 'रोग की जांच की जा रही है...' : 'Diagnosing Leaf Disease…') : (t('detectDisease') || '🔍 Detect Disease')}
          </button>
        )}
      </form>

      {activeResult && (
        <div
          className="result-card disease-result"
          style={{
            marginTop: '20px',
            background: isError ? '#fef2f2' : undefined,
            border: isError ? '2px solid #f87171' : undefined
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <span className="result-icon">{isError ? '⚠️' : '🔬'}</span>
            <span
              className="ai-provider-badge"
              style={{
                background: isError ? '#fee2e2' : undefined,
                color: isError ? '#991b1b' : undefined,
                borderColor: isError ? '#fca5a5' : undefined
              }}
            >
              {isError ? '🛡️ Image Verification Guard' : '🔬 Photo Disease Diagnosis'}
            </span>
          </div>
          <span style={{ fontSize: '1.05rem', fontWeight: '600', whiteSpace: 'pre-line', color: isError ? '#991b1b' : undefined }}>{activeResult}</span>
        </div>
      )}

      {previewUrl && (
        <div className="image-preview" style={{ marginTop: '16px' }}>
          <p className="preview-label">{t('uploadedImage') || 'Uploaded Image:'}</p>
          <img src={previewUrl} width="280" alt="Uploaded leaf" style={{ borderRadius: '10px', boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }} />
        </div>
      )}

      {/* 🍃 Common Diseases Reference Gallery for Selected Crop */}
      {diseaseSamples.length > 0 && (
        <div className="disease-samples-section" style={{ marginTop: '28px', paddingTop: '20px', borderTop: '1px solid #e0e6ed' }}>
          <div style={{ marginBottom: '14px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#1b5e20', margin: '0 0 6px 0' }}>
              {lang === 'kn' 
                ? `🍃 ${getCropName(cropType, 'kn')} ಬೆಳೆಯ ಸಾಮಾನ್ಯ ರೋಗಗಳು (ಉಲ್ಲೇಖ ಮಾರ್ಗದರ್ಶಿ)` 
                : lang === 'hi' 
                ? `🍃 ${getCropName(cropType, 'hi')} के सामान्य रोग (संदर्भ मार्गदर्शिका)` 
                : `🍃 Common diseases of ${getCropName(cropType, 'en')} (reference guide)`}
            </h3>
            
            <p style={{
              fontSize: '0.88rem',
              color: '#475569',
              margin: '0 0 8px 0',
              lineHeight: 1.5,
              background: '#fffbeb',
              padding: '10px 14px',
              borderRadius: '8px',
              borderLeft: '4px solid #f59e0b'
            }}>
              {cropNotice}
            </p>

            <div style={{
              fontSize: '0.78rem',
              color: '#0f766e',
              background: '#f0fdfa',
              padding: '8px 12px',
              borderRadius: '6px',
              border: '1px solid #ccfbf1',
              fontWeight: 500
            }}>
              {coverageLine}
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px', alignItems: 'start' }}>
            {diseaseSamples.map((sample) => (
              <div 
                key={sample.id} 
                className="disease-sample-card"
                style={{
                  background: '#ffffff',
                  borderRadius: '10px',
                  border: '1px solid #e2e8f0',
                  overflow: 'hidden',
                  boxShadow: '0 3px 10px rgba(0,0,0,0.06)',
                  display: 'flex',
                  flexDirection: 'column',
                  transition: 'transform 0.2s ease, box-shadow 0.2s ease'
                }}
              >
                {sample.image && (sample.verified || sample.source) ? (
                  <div style={{ position: 'relative', width: '100%', height: '150px', background: '#f8fafc', overflow: 'hidden' }}>
                    <img 
                      src={`/${sample.image}`} 
                      alt={sample.name} 
                      loading="lazy"
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                      onError={(e) => { if (e.target.parentElement) e.target.parentElement.style.display = 'none'; }}
                    />
                    <span style={{
                      position: 'absolute',
                      top: '8px',
                      right: '8px',
                      background: sample.verified ? 'rgba(22, 101, 52, 0.9)' : 'rgba(15, 23, 42, 0.85)',
                      color: sample.verified ? '#f0fdf4' : '#fef08a',
                      fontSize: '0.72rem',
                      fontWeight: 700,
                      padding: '4px 9px',
                      borderRadius: '6px',
                      backdropFilter: 'blur(4px)',
                      border: sample.verified ? '1px solid #86efac' : '1px solid rgba(254, 240, 138, 0.4)'
                    }}>
                      {sample.verified ? `🏛️ ${sample.source || 'UAS Dharwad Verified'}` : `🖼️ ${sample.provenance_badge || 'Reference Image'}`}
                    </span>
                  </div>
                ) : (
                  <div style={{ height: '90px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: '#f1f5f9', color: '#64748b', fontSize: '0.75rem', padding: '10px', textAlign: 'center' }}>
                    <span style={{ fontSize: '1.3rem' }}>📷</span>
                    <span>{lang === 'kn' ? 'ಚಿತ್ರ ಪರಿಶೀಲನೆಯಲ್ಲಿದೆ' : lang === 'hi' ? 'छवि सत्यापन प्रक्रिया में है' : 'Image under scientific review'}</span>
                  </div>
                )}

                <div style={{ padding: '14px', display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
                  <h4 style={{ margin: '0 0 4px 0', fontSize: '0.95rem', fontWeight: 700, color: '#1e293b' }}>
                    {sample.name}
                  </h4>

                  {sample.last_reviewed_by && (
                    <div style={{ fontSize: '0.7rem', color: '#64748b', marginBottom: '4px' }}>
                      👨‍🔬 <strong>{lang === 'kn' ? 'ಪರಿಶೀಲಿಸಿದವರು' : lang === 'hi' ? 'समीक्षक' : 'Reviewed by'}:</strong> {sample.last_reviewed_by} ({sample.last_reviewed_date || '2026-10-15'})
                      {sample.confidence_level && <span> • <strong>{sample.confidence_level}</strong></span>}
                    </div>
                  )}

                  {sample.source_license && (
                    <div style={{ fontSize: '0.67rem', color: '#94a3b8', marginBottom: '6px' }}>
                      📜 <strong>License:</strong> {sample.source_license}
                    </div>
                  )}

                  {!sample.verified && !sample.verified_by_expert && (
                    <div style={{ marginBottom: '8px' }}>
                      <span style={{
                        display: 'inline-block',
                        fontSize: '0.7rem',
                        background: '#fef3c7',
                        color: '#92400e',
                        fontWeight: 600,
                        padding: '2px 7px',
                        borderRadius: '4px',
                        border: '1px solid #fde68a'
                      }}>
                        ⚠️ {lang === 'kn' ? 'ತಜ್ಞರ ಪರಿಶೀಲನೆ ಬಾಕಿಯಿದೆ' : lang === 'hi' ? 'विशेषज्ञ समीक्षा लंबित' : 'Pending expert review'}
                      </span>
                    </div>
                  )}

                  <p style={{ fontSize: '0.82rem', color: '#475569', margin: '0 0 12px 0', lineHeight: 1.5 }}>
                    <strong style={{ color: '#334155' }}>🔍 {lang === 'kn' ? 'ಲಕ್ಷಣಗಳು:' : lang === 'hi' ? 'लक्षण:' : 'Symptoms:'}</strong> {sample.symptoms}
                  </p>
                  
                  <div style={{
                    marginTop: 'auto',
                    fontSize: '0.78rem',
                    background: '#f0fdf4',
                    color: '#166534',
                    padding: '8px 10px',
                    borderRadius: '6px',
                    borderLeft: '3px solid #22c55e',
                    lineHeight: 1.4
                  }}>
                    <strong>💊 {lang === 'kn' ? 'ಪರಿಹಾರ:' : lang === 'hi' ? 'उपचार:' : 'Remedy:'}</strong> {sample.treatment}
                    
                    {!sample.is_healthy && (
                      <div style={{
                        fontSize: '0.7rem',
                        color: '#64748b',
                        marginTop: '6px',
                        borderTop: '1px dashed #bbf7d0',
                        paddingTop: '5px',
                        fontStyle: 'italic'
                      }}>
                        ⚠️ {lang === 'kn'
                          ? 'ಉತ್ಪನ್ನದ ಲೇಬಲ್‌ನಲ್ಲಿರುವ ಪ್ರಮಾಣವನ್ನು ಪರಿಶೀಲಿಸಿ ಮತ್ತು ನಿಮ್ಮ ಕೆವಿಕೆಯೊಂದಿಗೆ ಖಚಿತಪಡಿಸಿ. ಸುರಕ್ಷತಾ ನಿಯಮಗಳನ್ನು ಪಾಲಿಸಿ.'
                          : lang === 'hi'
                          ? 'उत्पाद लेबल पर दी गई मात्रा की जांच करें और अपने केवीके से पुष्टि करें। सुरक्षा निर्देशों का पालन करें।'
                          : 'Check the dose on the product label and confirm with your KVK. Follow safety instructions.'}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
