// Thin wrapper around fetch for the Flask backend. Every original <form
// action="..."> becomes one of these calls. `credentials: 'include'` keeps
// session cookies working the same way the server-rendered forms did.

async function postForm(url, formData) {
  let res;
  try {
    res = await fetch(url, {
      method: 'POST',
      headers: {
        'Accept': 'application/json'
      },
      body: formData,
      credentials: 'include'
    });
  } catch (networkErr) {
    // fetch itself threw: server unreachable, CORS blocked, DNS failure, etc.
    // This is NOT a validation error from Flask - surface it distinctly.
    throw new Error(
      `Could not reach ${url}. Is the Flask backend running and is the ` +
      `Vite proxy pointing at the right host/port? (${networkErr.message})`
    );
  }

  const contentType = res.headers.get('content-type') || '';
  const body = contentType.includes('application/json') ? await res.json() : await res.text();

  if (!res.ok) {
    // Surface whatever Flask actually sent back instead of a generic message,
    // so real validation errors (e.g. "username taken") are distinguishable
    // from server errors (500s) or misconfigured routes (404s returning HTML).
    const detail =
      typeof body === 'object' && (body?.message || body?.error)
        ? (body.message || body.error)
        : typeof body === 'string'
          ? body.slice(0, 300)
          : `HTTP ${res.status}`;
    const err = new Error(detail);
    err.status = res.status;
    err.body = body;
    throw err;
  }

  return body;
}

async function postJson(url, payload) {
  let res;
  try {
    res = await fetch(url, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(payload),
      credentials: 'include'
    });
  } catch (networkErr) {
    throw new Error(
      `Could not reach ${url}. Is the Flask backend running? (${networkErr.message})`
    );
  }

  const contentType = res.headers.get('content-type') || '';
  const body = contentType.includes('application/json') ? await res.json() : await res.text();

  if (!res.ok) {
    const detail =
      typeof body === 'object' && body?.message
        ? body.message
        : typeof body === 'object' && body?.error
          ? body.error
          : typeof body === 'string'
            ? body.slice(0, 300)
            : `HTTP ${res.status}`;
    const err = new Error(detail);
    err.status = res.status;
    err.body = body;
    throw err;
  }

  return body;
}

function toFormData(fields) {
  const fd = new FormData();
  Object.entries(fields).forEach(([key, value]) => {
    if (value !== undefined && value !== null) fd.append(key, value);
  });
  return fd;
}

let currentAudio = null;

export function stopSpeech() {
  if (currentAudio) {
    try {
      currentAudio.pause();
      currentAudio.currentTime = 0;
    } catch (e) {}
    currentAudio = null;
  }
  if (typeof window !== 'undefined' && window.speechSynthesis) {
    try {
      window.speechSynthesis.cancel();
    } catch (e) {}
  }
}

export function playSpeech({ text, lang = 'en', onStart, onEnd, onError }) {
  stopSpeech();

  if (!text || !text.trim()) {
    if (onEnd) onEnd();
    return;
  }

  const clean = text
    .replace(/https?:\/\/\S+/g, '')
    .replace(/\[ICAR.*?\]|\[.*?\]|\(.*Document.*?\)/gi, ' ')
    .replace(/Document \d+.*?:/gi, ' ')
    .replace(/[•*#→\[\]\(\)\`\_|~]/g, ' ')
    .replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, ' ')
    .replace(/[🌱🌾🌿🍃🩺💰💧🤖🔬🔴🎤🔊⏹💡🚨⚠✨🛒🇮🇳🇬🇧]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  if (!clean) {
    if (onEnd) onEnd();
    return;
  }

  const normLang = (lang || 'en').startsWith('kn') ? 'kn' : (lang || 'en').startsWith('hi') ? 'hi' : 'en';

  if (onStart) onStart();

  const runBrowserFallback = () => {
    currentAudio = null;
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      if (onError) onError();
      if (onEnd) onEnd();
      return;
    }

    try {
      window.speechSynthesis.cancel();
      if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume();
      }

      const speakText = (voices) => {
        const speechLang = normLang === 'kn' ? 'kn-IN' : normLang === 'hi' ? 'hi-IN' : 'en-IN';
        const utterance = new SpeechSynthesisUtterance(clean.slice(0, 400));
        utterance.lang = speechLang;
        utterance.rate = 0.92;
        utterance.volume = 1.0;

        const available = voices || window.speechSynthesis.getVoices() || [];
        // Try exact language match, then language prefix, then Indian subcontinent voices
        let voice = available.find(v => (v.lang || '').toLowerCase().replace('_', '-').includes(normLang));
        if (!voice && normLang === 'kn') {
          voice = available.find(v => (v.lang || '').toLowerCase().includes('hi-in') || (v.lang || '').toLowerCase().includes('en-in') || (v.lang || '').toLowerCase().includes('in'));
        } else if (!voice && normLang === 'hi') {
          voice = available.find(v => (v.lang || '').toLowerCase().includes('hi') || (v.lang || '').toLowerCase().includes('en-in'));
        }
        if (voice) {
          utterance.voice = voice;
          utterance.lang = voice.lang || speechLang;
        }

        utterance.onstart = () => {
          if (onStart) onStart();
        };
        utterance.onend = () => {
          if (onEnd) onEnd();
        };
        utterance.onerror = (e) => {
          console.warn('SpeechSynthesis event error:', e);
          if (onError) onError();
          if (onEnd) onEnd();
        };

        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utterance);
      };

      const currentVoices = window.speechSynthesis.getVoices();
      if (!currentVoices || currentVoices.length === 0) {
        window.speechSynthesis.onvoiceschanged = () => {
          speakText(window.speechSynthesis.getVoices());
        };
        // Safety timeout if voiceschanged doesn't fire
        setTimeout(() => speakText([]), 300);
      } else {
        speakText(currentVoices);
      }
    } catch (e) {
      console.warn('SpeechSynthesis error:', e);
      if (onError) onError();
      if (onEnd) onEnd();
    }
  };

  // Fetch audio from /api/tts via POST with JSON body (avoids URL length limits for Indic scripts)
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 9000);

  fetch('/api/tts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      lang: normLang,
      text: clean.slice(0, 450)
    }),
    credentials: 'include',
    signal: controller.signal
  })
    .then(async (res) => {
      clearTimeout(timer);
      if (!res.ok) {
        throw new Error(`TTS server responded with ${res.status}`);
      }
      const blob = await res.blob();
      if (blob.size < 50) {
        throw new Error('TTS audio blob too small');
      }
      const audioUrl = URL.createObjectURL(blob);
      const audio = new Audio(audioUrl);
      currentAudio = audio;

      audio.onended = () => {
        currentAudio = null;
        URL.revokeObjectURL(audioUrl);
        if (onEnd) onEnd();
      };

      audio.onerror = () => {
        currentAudio = null;
        URL.revokeObjectURL(audioUrl);
        runBrowserFallback();
      };

      const playPromise = audio.play();
      if (playPromise !== undefined) {
        playPromise.catch((playErr) => {
          console.warn('Audio play() promise rejected (browser policy), switching to Web Speech fallback:', playErr);
          runBrowserFallback();
        });
      }
      return playPromise;
    })
    .catch((err) => {
      clearTimeout(timer);
      console.warn('TTS streaming failed or aborted, using Web Speech API fallback:', err);
      runBrowserFallback();
    });
}

export const api = {
  login: (username, password, userType, remember) =>
    postForm('/login', toFormData({ username, password, user_type: userType, remember: remember ? 'on' : undefined })),

  register: (fullName, username, userType, password, confirmPassword) =>
    postForm('/register', toFormData({
      full_name: fullName,
      username,
      user_type: userType,
      password,
      confirm_password: confirmPassword
    })),

  logout: () => fetch('/logout', { credentials: 'include' }),

  resetSession: () => fetch('/reset', { method: 'POST', credentials: 'include' }),

  answerQuery: (query, lang = 'en') => postJson('/api/answer_query', { query, lang }),

  chat: (message, history = [], lang = 'en', dashboardContext = null) =>
    postJson('/api/chat', { message, history, lang, dashboard_context: dashboardContext }),

  explainPrediction: (params) => postJson('/api/explain_prediction', params),

  plannerAi: (params) => postJson('/api/planner_ai', params),

  predictDisease: (imageFile, cropType = 'general', lang = 'en') =>
    postForm('/predict_disease', toFormData({ image: imageFile, crop_type: cropType, lang })),

  predictPrice: (crop, district, month, year, lang = 'en') =>
    postForm('/predict_price', toFormData({ crop, district, month, year, lang })),

  predictCrop: (fields) => postForm('/predict_crop', toFormData(fields)),

  predictIrrigation: (fields) => postJson('/api/predict_irrigation', fields),

  getCropDiseaseSamples: (crop, lang = 'en') =>
    fetch(`/api/crop_disease_samples?crop=${encodeURIComponent(crop)}&lang=${encodeURIComponent(lang)}`, { credentials: 'include' }).then(r => r.json()),

  getDiseaseCrops: (lang = 'en') =>
    fetch(`/api/disease_crops?lang=${encodeURIComponent(lang)}`, { credentials: 'include' }).then(r => r.json()),

  planner: (params = 'en') => {
    const payload = typeof params === 'string' ? { lang: params } : (params || { lang: 'en' });
    return postForm('/planner', toFormData(payload));
  },

  simulateDigitalTwin: (params) => postJson('/api/decision_intelligence/digital_twin', params),

  simulateCounterfactual: (params) => postJson('/api/decision_intelligence/counterfactual', params),

  runMultiAgentDebate: (params) => postJson('/api/decision_intelligence/multi_agent_debate', params),

  getRegretPlans: (params) => postJson('/api/decision_intelligence/regret_plans', params),

  askMyFarm: (payload) => {
    if (payload instanceof FormData) {
      return postForm('/api/ask_my_farm', payload);
    }
    return postJson('/api/ask_my_farm', payload);
  },

  getTtsUrl: (text, lang = 'en') => {
    const clean = (text || '')
      .replace(/https?:\/\/\S+/g, '')
      .replace(/\[ICAR.*?\]|\[.*?\]|\(.*Document.*?\)/gi, ' ')
      .replace(/Document \d+.*?:/gi, ' ')
      .replace(/[•*#→\[\]\(\)\`\_|~]/g, ' ')
      .replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, ' ')
      .replace(/[🌱🌾🌿🍃🩺💰💧🤖🔬🔴🎤🔊⏹💡🚨⚠✨🛒🇮🇳🇬🇧]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
    const normLang = (lang || 'en').startsWith('kn') ? 'kn' : (lang || 'en').startsWith('hi') ? 'hi' : 'en';
    return `/api/tts?lang=${encodeURIComponent(normLang)}&text=${encodeURIComponent(clean)}`;
  },

  playSpeech,
  stopSpeech
};


