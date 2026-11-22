import { useState, useRef } from 'react';
import { useLanguage } from '../../context/LanguageContext.jsx';
import { api } from '../../api.js';

const SPEECH_LANG_MAP = { en: 'en-IN', kn: 'kn-IN', hi: 'hi-IN' };

export default function VoiceQuerySection() {
  const { t, lang } = useLanguage();
  const [query, setQuery] = useState('');
  const [resultData, setResultData] = useState(null);
  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [loading, setLoading] = useState(false);
  const recognitionRef = useRef(null);

  function startVoice() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Voice recognition is not supported in this browser. Please use Google Chrome or Microsoft Edge.');
      return;
    }

    if (listening && recognitionRef.current) {
      recognitionRef.current.stop();
      setListening(false);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.lang = SPEECH_LANG_MAP[lang] || 'en-IN';
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => setListening(true);
      recognition.onend = () => setListening(false);
      recognition.onerror = (e) => {
        console.warn('Speech recognition error:', e.error);
        setListening(false);
        if (e.error === 'not-allowed') {
          alert('Microphone permission denied. Please allow microphone access in your browser.');
        }
      };

      recognition.onresult = (event) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          }
        }
        if (finalTranscript) {
          setQuery(finalTranscript.trim());
        } else if (event.results[0]) {
          setQuery(event.results[0][0].transcript);
        }
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err) {
      console.error('Speech recognition exception:', err);
      setListening(false);
    }
  }

  function toggleSpeakAnswer() {
    if (speaking) {
      api.stopSpeech();
      setSpeaking(false);
      return;
    }

    if (!resultData || !resultData.answer) return;

    setSpeaking(true);
    api.playSpeech({
      text: resultData.answer,
      lang: lang,
      onStart: () => setSpeaking(true),
      onEnd: () => setSpeaking(false),
      onError: () => setSpeaking(false)
    });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await api.answerQuery(query, lang);
      setResultData({
        answer: typeof res === 'string' ? res : res.answer || '',
        sources: res.sources || [],
        provider: res.provider || 'SmartAgri AI',
        hasRag: res.has_rag_context
      });
    } catch (err) {
      setResultData({
        answer: 'Sorry, something went wrong getting an answer. Please verify your backend server.',
        sources: []
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="section-box" id="voice">
      <div className="section-header">
        <span className="section-icon" role="img" aria-label="Microphone">🎤</span>
        <div>
          <h2>{t('voiceTitle')}</h2>
          <p className="section-desc">{t('voiceDesc')}</p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t('voicePlaceholder')}
          />
        </div>

        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <button 
            type="button" 
            className="gov-btn" 
            onClick={startVoice}
            style={listening ? { background: '#d32f2f' } : {}}
          >
            {listening ? (lang === 'kn' ? '🔴 ಆಲಿಸುತ್ತಿದೆ... (ಮಾತನಾಡಿ)' : lang === 'hi' ? '🔴 सुन रहा है... (बोलें)' : '🔴 Listening... (Speak now)') : t('startVoice')}
          </button>
          <button
            type="submit"
            className="gov-btn"
            style={{ background: 'linear-gradient(135deg, #1565c0, #1976d2)' }}
            disabled={loading || !query.trim()}
          >
            {loading ? '…' : t('getAnswer')}
          </button>
        </div>
      </form>

      {resultData && resultData.answer && (
        <div className="query-answer-box">
          <div className="query-answer-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span>🤖 SmartAgri AI Agronomist:</span>
              {resultData.provider && (
                <span className="ai-provider-badge">
                  ⚡ {resultData.provider}
                </span>
              )}
            </div>
            <button
              type="button"
              className="gov-btn"
              onClick={toggleSpeakAnswer}
              style={{
                padding: '4px 12px',
                fontSize: '12px',
                background: speaking ? '#d32f2f' : 'linear-gradient(135deg, #2e7d32, #388e3c)',
                margin: 0
              }}
            >
              {speaking 
                ? (lang === 'kn' ? '⏹ ಆಡಿಯೋ ನಿಲ್ಲಿಸಿ' : lang === 'hi' ? '⏹ ऑडियो रोकें' : '⏹ Stop Audio')
                : (lang === 'kn' ? '🔊 ಧ್ವನಿಯಲ್ಲಿ ಕೇಳಿ' : lang === 'hi' ? '🔊 बोलकर सुनाएं' : '🔊 Read Aloud')}
            </button>
          </div>
          <div className="query-answer-body" style={{ whiteSpace: 'pre-line' }}>
            {resultData.answer}
          </div>
          {resultData.sources && resultData.sources.length > 0 && (
            <div className="ai-sources-tag" style={{ marginTop: '12px' }}>
              <span className="source-label">📚 Knowledge Base Citations:</span>
              {resultData.sources.map((src, i) => (
                <span key={i} className="source-pill">{src}</span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
