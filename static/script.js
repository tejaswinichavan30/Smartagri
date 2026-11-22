// ===============================
// LANGUAGE SWITCHER
// ===============================
let currentLang = 'en';
let voiceLang = 'en-IN';

function switchLang(lang, evt) {
    if (!lang) lang = 'en';
    currentLang = lang;
    try {
        localStorage.setItem('smartagri_lang', lang);
    } catch (e) {}

    // Update active button
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.remove('active');
        const text = btn.textContent.toLowerCase();
        if ((lang === 'en' && text.includes('english')) ||
            (lang === 'kn' && text.includes('ಕನ್ನಡ')) ||
            (lang === 'hi' && text.includes('हिंदी'))) {
            btn.classList.add('active');
        }
    });
    if (evt && evt.target) {
        evt.target.classList.add('active');
    }

    // Sync all hidden form inputs
    document.querySelectorAll('.lang-field').forEach(input => {
        input.value = lang;
    });

    // Update all elements with data-en, data-kn, data-hi (skip inputs/textareas)
    document.querySelectorAll('[data-en]').forEach(el => {
        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') return;
        const text = el.getAttribute('data-' + lang);
        if (text) {
            el.textContent = text;
        }
    });

    // Update placeholders
    document.querySelectorAll('[data-placeholder-en]').forEach(el => {
        const ph = el.getAttribute('data-placeholder-' + lang);
        if (ph) el.placeholder = ph;
    });

    // Update marquee text
    const marqueeText = document.getElementById('marqueeText');
    if (marqueeText) {
        const text = marqueeText.getAttribute('data-' + lang);
        if (text) marqueeText.textContent = text;
    }

    // Update page title
    const titles = {
        en: 'SmartAgri AI — Farmer Decision Support System',
        kn: 'ಸ್ಮಾರ್ಟ್‌ಆಗ್ರಿ AI — ರೈತ ನಿರ್ಧಾರ ಬೆಂಬಲ ವ್ಯವಸ್ಥೆ',
        hi: 'स्मार्टएग्री AI — किसान निर्णय समर्थन प्रणाली'
    };
    document.title = titles[lang] || titles.en;

    // Update voice recognition language
    voiceLang = { en: 'en-IN', kn: 'kn-IN', hi: 'hi-IN' }[lang] || 'en-IN';
}

// Auto-initialize language on page load
document.addEventListener('DOMContentLoaded', () => {
    let savedLang = 'en';
    try {
        savedLang = localStorage.getItem('smartagri_lang') || 'en';
    } catch (e) {}

    // Check if server rendered with a specific language field
    const firstLangInput = document.querySelector('.lang-field');
    if (firstLangInput && firstLangInput.value && firstLangInput.value !== 'None') {
        savedLang = firstLangInput.value;
    }

    switchLang(savedLang);
});

// ===============================
// VOICE INPUT & SPEECH SYNTHESIS
// ===============================
let activeRecognition = null;
let isSpeaking = false;

function startVoice() {
    const btn = document.getElementById('voiceBtn');
    const textarea = document.getElementById('voiceText');

    // If already listening, stop it cleanly
    if (activeRecognition) {
        try {
            activeRecognition.stop();
        } catch (e) {}
        activeRecognition = null;
        if (btn) {
            const stopMsgs = { en: '🎤 Start Voice Input', kn: '🎤 ಧ್ವನಿ ಇನ್‌ಪುಟ್ ಪ್ರಾರಂಭಿಸಿ', hi: '🎤 वॉयस इनपुट शुरू करें' };
            btn.textContent = stopMsgs[currentLang] || stopMsgs.en;
            btn.style.background = '';
        }
        return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        const msgs = {
            en: 'Voice recognition is not supported in this browser. Please use Google Chrome or Microsoft Edge.',
            kn: 'ಈ ಬ್ರೌಸರ್‌ನಲ್ಲಿ ಧ್ವನಿ ಗುರುತಿಸುವಿಕೆ ಬೆಂಬಲಿತವಾಗಿಲ್ಲ. ದಯವಿಟ್ಟು Google Chrome ಬಳಸಿ.',
            hi: 'इस ब्राउज़र में वॉयस पहचान समर्थಿತ नहीं है। कृपया Google Chrome का उपयोग करें।'
        };
        alert(msgs[currentLang] || msgs.en);
        return;
    }

    try {
        const recognition = new SpeechRecognition();
        
        // Map language
        const langMap = { en: 'en-IN', kn: 'kn-IN', hi: 'hi-IN' };
        recognition.lang = langMap[currentLang] || 'en-IN';
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.maxAlternatives = 1;

        const startMsgs = { en: '🔴 Listening... (Speak now)', kn: '🔴 ಆಲಿಸುತ್ತಿದೆ... (ಈಗ ಮಾತನಾಡಿ)', hi: '🔴 सुन रहा है... (अब बोलें)' };
        const stopMsgs = { en: '🎤 Start Voice Input', kn: '🎤 ಧ್ವನಿ ಇನ್‌ಪುಟ್ ಪ್ರಾರಂಭಿಸಿ', hi: '🎤 वॉयस इनपुट शुरू करें' };

        if (btn) {
            btn.textContent = startMsgs[currentLang] || startMsgs.en;
            btn.style.background = '#d32f2f';
        }

        recognition.onstart = function () {
            activeRecognition = recognition;
        };

        recognition.onresult = function (event) {
            let finalTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                }
            }
            if (finalTranscript && textarea) {
                textarea.value = finalTranscript.trim();
            } else if (event.results[0] && textarea) {
                textarea.value = event.results[0][0].transcript;
            }
        };

        recognition.onerror = function (event) {
            console.warn('Speech recognition event error:', event.error);
            activeRecognition = null;
            if (btn) {
                btn.textContent = stopMsgs[currentLang] || stopMsgs.en;
                btn.style.background = '';
            }
            if (event.error === 'not-allowed') {
                alert('Microphone access was denied. Please allow microphone permission in your browser address bar.');
            }
        };

        recognition.onend = function () {
            activeRecognition = null;
            if (btn) {
                btn.textContent = stopMsgs[currentLang] || stopMsgs.en;
                btn.style.background = '';
            }
        };

        recognition.start();
    } catch (err) {
        console.error('Error starting recognition:', err);
        activeRecognition = null;
        if (btn) {
            btn.textContent = '🎤 Start Voice Input';
            btn.style.background = '';
        }
    }
}

// ===============================
// MULTILINGUAL TEXT-TO-SPEECH (TTS) - KANNADA, HINDI & ENGLISH
// ===============================
let currentAudio = null;
let currentActiveButton = null;
let isSpeakingActive = false;

const TTS_MESSAGES = {
    read: { en: '🔊 Read Aloud', kn: '🔊 ಧ್ವನಿಯಲ್ಲಿ ಕೇಳಿ', hi: '🔊 बोलकर सुनाएं' },
    loading: { en: '⏳ Loading Audio...', kn: '⏳ ಆಡಿಯೋ ಪ್ರಾರಂಭವಾಗುತ್ತಿದೆ...', hi: '⏳ ऑडियो लोड हो रहा है...' },
    stop: { en: '⏹ Stop Audio', kn: '⏹ ಆಡಿಯೋ ನಿಲ್ಲಿಸಿ', hi: '⏹ ऑडियो रोकें' }
};

function stopAnyPlayingAudio() {
    if (currentAudio) {
        try {
            currentAudio.pause();
            currentAudio.currentTime = 0;
        } catch (e) {}
        currentAudio = null;
    }
    if (window.speechSynthesis && window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
    }
    if (currentActiveButton) {
        const defaultText = currentActiveButton.getAttribute('data-' + currentLang) || 
                            TTS_MESSAGES.read[currentLang] || 
                            TTS_MESSAGES.read.en;
        currentActiveButton.textContent = defaultText;
        currentActiveButton.style.background = '';
        currentActiveButton = null;
    }
    isSpeakingActive = false;
}

function cleanTextForSpeech(rawText) {
    if (!rawText) return '';
    return rawText
        .replace(/https?:\/\/\S+/g, '')
        .replace(/\[ICAR.*?\]|\[.*?\]|\(.*Document.*?\)/gi, ' ')
        .replace(/Document \d+.*?:/gi, ' ')
        .replace(/[•*#→\[\]\(\)\`\_|~]/g, ' ')
        .replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, ' ') // emojis
        .replace(/[🌱🌾🌿🍃🩺💰💧🤖🔬🔴🎤🔊⏹💡🚨⚠✨🛒🇮🇳🇬🇧]/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
}

function playTtsAudio(textToSpeak, langCode, targetButton) {
    const clean = cleanTextForSpeech(textToSpeak);
    if (!clean) {
        alert(currentLang === 'kn' ? 'ಓದಲು ಯಾವುದೇ ಪಠ್ಯ ಲಭ್ಯವಿಲ್ಲ.' : currentLang === 'hi' ? 'बोलने के लिए कोई टेक्स्ट उपलब्ध नहीं है।' : 'No text available to read aloud.');
        return;
    }

    // If clicking the same button while playing, toggle stop
    if (isSpeakingActive && currentActiveButton === targetButton) {
        stopAnyPlayingAudio();
        return;
    }

    stopAnyPlayingAudio();

    const lang = langCode || currentLang || 'en';
    const langNorm = lang.startsWith('kn') ? 'kn' : lang.startsWith('hi') ? 'hi' : 'en';

    isSpeakingActive = true;
    currentActiveButton = targetButton;

    if (targetButton) {
        targetButton.textContent = TTS_MESSAGES.loading[langNorm] || TTS_MESSAGES.loading.en;
        targetButton.style.background = '#e65100';
    }

    // Try backend streaming endpoint /api/tts
    const ttsUrl = `/api/tts?lang=${encodeURIComponent(langNorm)}&text=${encodeURIComponent(clean)}`;
    const audio = new Audio();
    audio.src = ttsUrl;
    audio.preload = 'auto';

    audio.oncanplay = function () {
        if (!isSpeakingActive) return;
        audio.play().then(() => {
            if (targetButton) {
                targetButton.textContent = TTS_MESSAGES.stop[langNorm] || TTS_MESSAGES.stop.en;
                targetButton.style.background = '#d32f2f';
            }
        }).catch(err => {
            console.warn('Audio play error, falling back to browser SpeechSynthesis:', err);
            fallbackBrowserSpeech(clean, langNorm, targetButton);
        });
    };

    audio.onended = function () {
        stopAnyPlayingAudio();
    };

    audio.onerror = function (e) {
        console.warn('Backend TTS failed, using browser Web Speech fallback:', e);
        fallbackBrowserSpeech(clean, langNorm, targetButton);
    };

    currentAudio = audio;
    audio.load();
}

function fallbackBrowserSpeech(cleanText, langCode, targetButton) {
    if (!('speechSynthesis' in window)) {
        stopAnyPlayingAudio();
        return;
    }

    window.speechSynthesis.cancel();
    window.speechSynthesis.resume();

    const langCodeMap = { en: 'en-IN', kn: 'kn-IN', hi: 'hi-IN' };
    const targetLocale = langCodeMap[langCode] || 'en-IN';

    const utterance = new SpeechSynthesisUtterance(cleanText.substring(0, 300));
    utterance.lang = targetLocale;
    utterance.rate = 0.92;

    const voices = window.speechSynthesis.getVoices() || [];
    const matchedVoice = voices.find(v => v.lang === targetLocale || v.lang.startsWith(langCode)) || null;
    if (matchedVoice) utterance.voice = matchedVoice;

    if (targetButton) {
        targetButton.textContent = TTS_MESSAGES.stop[langCode] || TTS_MESSAGES.stop.en;
        targetButton.style.background = '#d32f2f';
    }

    utterance.onend = function () {
        stopAnyPlayingAudio();
    };
    utterance.onerror = function () {
        stopAnyPlayingAudio();
    };

    window.speechSynthesis.speak(utterance);
}

function toggleSpeakAnswer() {
    const speakBtn = document.getElementById('speakBtn');
    const answerEl = document.getElementById('queryAnswerText');
    if (!answerEl) return;
    const text = answerEl.innerText || answerEl.textContent || '';
    playTtsAudio(text, currentLang, speakBtn);
}

function toggleSpeakElement(elementId, btnId) {
    const btn = document.getElementById(btnId);
    const el = document.getElementById(elementId);
    if (!el) return;
    const text = el.innerText || el.textContent || '';
    playTtsAudio(text, currentLang, btn);
}

// ===============================
// District Soil Data Auto-fill
// ===============================
const districtSoilData = {
    'Bagalkot':         { n: 25, p: 130, k: 195, ph: 7.5, rainfall: 65, temp: 28, humidity: 55 },
    'Ballari':          { n: 115, p: 45, k: 20, ph: 7.2, rainfall: 70, temp: 29, humidity: 50 },
    'Belagavi':         { n: 85, p: 46, k: 22, ph: 6.8, rainfall: 85, temp: 24, humidity: 70 },
    'Bengaluru Rural':  { n: 25, p: 25, k: 30, ph: 6.2, rainfall: 95, temp: 24, humidity: 65 },
    'Bengaluru Urban':  { n: 25, p: 25, k: 30, ph: 6.3, rainfall: 95, temp: 25, humidity: 63 },
    'Bidar':            { n: 25, p: 65, k: 22, ph: 7.3, rainfall: 85, temp: 27, humidity: 58 },
    'Chamarajanagara':  { n: 78, p: 48, k: 25, ph: 6.0, rainfall: 80, temp: 26, humidity: 65 },
    'Chikkaballapura':  { n: 25, p: 130, k: 195, ph: 6.5, rainfall: 75, temp: 25, humidity: 62 },
    'Chikkamagaluru':   { n: 100, p: 30, k: 30, ph: 5.8, rainfall: 160, temp: 22, humidity: 80 },
    'Chitradurga':      { n: 80, p: 46, k: 22, ph: 6.8, rainfall: 68, temp: 28, humidity: 55 },
    'Dakshina Kannada': { n: 80, p: 48, k: 40, ph: 5.5, rainfall: 240, temp: 28, humidity: 85 },
    'Davanagere':       { n: 78, p: 48, k: 20, ph: 6.5, rainfall: 85, temp: 27, humidity: 60 },
    'Dharwad':          { n: 115, p: 45, k: 20, ph: 6.8, rainfall: 80, temp: 24, humidity: 75 },
    'Gadag':            { n: 110, p: 45, k: 20, ph: 7.0, rainfall: 70, temp: 28, humidity: 55 },
    'Hassan':           { n: 98, p: 30, k: 30, ph: 6.2, rainfall: 150, temp: 22, humidity: 75 },
    'Haveri':           { n: 85, p: 48, k: 20, ph: 6.8, rainfall: 80, temp: 26, humidity: 60 },
    'Kalaburagi':       { n: 25, p: 65, k: 22, ph: 7.5, rainfall: 80, temp: 29, humidity: 55 },
    'Kodagu':           { n: 100, p: 30, k: 30, ph: 5.5, rainfall: 165, temp: 20, humidity: 90 },
    'Kolar':            { n: 20, p: 25, k: 30, ph: 6.2, rainfall: 90, temp: 25, humidity: 65 },
    'Koppal':           { n: 80, p: 46, k: 22, ph: 7.2, rainfall: 65, temp: 30, humidity: 50 },
    'Mandya':           { n: 80, p: 48, k: 40, ph: 6.2, rainfall: 200, temp: 25, humidity: 68 },
    'Mysuru':           { n: 78, p: 48, k: 25, ph: 6.2, rainfall: 95, temp: 25, humidity: 67 },
    'Raichur':          { n: 115, p: 45, k: 20, ph: 7.2, rainfall: 75, temp: 31, humidity: 50 },
    'Ramanagara':       { n: 25, p: 25, k: 30, ph: 6.3, rainfall: 100, temp: 25, humidity: 64 },
    'Shivamogga':       { n: 80, p: 48, k: 40, ph: 6.0, rainfall: 210, temp: 24, humidity: 78 },
    'Tumakuru':         { n: 22, p: 20, k: 40, ph: 6.3, rainfall: 110, temp: 26, humidity: 62 },
    'Udupi':            { n: 80, p: 48, k: 40, ph: 5.8, rainfall: 245, temp: 27, humidity: 88 },
    'Uttara Kannada':   { n: 80, p: 48, k: 40, ph: 5.8, rainfall: 220, temp: 26, humidity: 82 },
    'Vijayanagara':     { n: 110, p: 45, k: 20, ph: 7.0, rainfall: 68, temp: 29, humidity: 50 },
    'Vijayapura':       { n: 25, p: 130, k: 195, ph: 7.5, rainfall: 68, temp: 29, humidity: 52 },
    'Yadgir':           { n: 25, p: 65, k: 22, ph: 7.4, rainfall: 80, temp: 30, humidity: 52 },
};

function autoFillSoilData(district) {
    if (!district) return;

    const data = districtSoilData[district];
    if (!data) return;

    const setVal = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.value = val;
    };

    // Auto fill all soil fields safely
    setVal('nitrogen', data.n);
    setVal('phosphorus', data.p);
    setVal('potassium', data.k);
    setVal('ph', data.ph);
    setVal('rainfall', data.rainfall);
    setVal('city', district);
    setVal('district', district);

    const distSelect = document.getElementById('districtSelect') || document.getElementById('district');
    if (distSelect && distSelect.value !== district) {
        distSelect.value = district;
    }

    // Show success message
    const lang = currentLang || 'en';
    const msgs = {
        en: `✅ Soil values auto-filled for ${district}! You can modify if needed.`,
        kn: `✅ ${district} ಗಾಗಿ ಮಣ್ಣಿನ ಮೌಲ್ಯಗಳು ತಂತಾನೇ ತುಂಬಲಾಗಿದೆ!`,
        hi: `✅ ${district} के लिए मिट्टी के मान स्वचालित भरे गए!`
    };

    // Show notification
    let notification = document.getElementById('soil-notification');
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'soil-notification';
        notification.className = 'info-note';
        notification.style.marginTop = '8px';
        const targetContainer = document.querySelector('.form-grid') || document.querySelector('.form-group');
        if (targetContainer && targetContainer.parentNode) {
            targetContainer.parentNode.insertBefore(notification, targetContainer);
        }
    }
    if (notification) {
        notification.textContent = msgs[lang] || msgs.en;
        notification.style.display = 'block';
        setTimeout(() => {
            notification.style.display = 'none';
        }, 3500);
    }
}

// ===============================
// Auto-Scroll to Active Result & Agent Chaining
// ===============================
document.addEventListener('DOMContentLoaded', () => {
    // 1. Smooth scroll to latest result if present on page load
    const resultElements = document.querySelectorAll('.crop-result, .price-result, .disease-result, .query-answer-box, .result-card');
    if (resultElements.length > 0) {
        const lastResult = resultElements[resultElements.length - 1];
        setTimeout(() => {
            lastResult.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 150);
    }

    // 2. Chaining: If crop recommendation result exists, auto-fill price, disease, and irrigation forms
    const now = new Date();
    const curMonth = now.getMonth() + 1;
    const curYear = now.getFullYear();

    // Auto-fill present month & year in market price form if empty
    const monthInput = document.querySelector('#price input[name="month"]');
    if (monthInput && (!monthInput.value || monthInput.value === '')) {
        monthInput.value = curMonth;
    }
    const yearInput = document.querySelector('#price input[name="year"]');
    if (yearInput && (!yearInput.value || yearInput.value === '')) {
        yearInput.value = curYear;
    }

    const cropResultEl = document.querySelector('.crop-result');
    if (cropResultEl) {
        const text = cropResultEl.textContent || '';
        // Match English "Recommended Crop: CropName", or Kannada "ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆ: ...", or Hindi "अनुशंसित फसल: ..."
        let matchedCrop = '';
        const enMatch = text.match(/Recommended Crop:\s*([^|\n\r]+)/i);
        const knMatch = text.match(/ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆ:\s*([^|\n\r]+)/i);
        const hiMatch = text.match(/अनुशंसित फसल:\s*([^|\n\r]+)/i);

        if (enMatch && enMatch[1]) matchedCrop = enMatch[1].trim();
        else if (knMatch && knMatch[1]) matchedCrop = knMatch[1].trim();
        else if (hiMatch && hiMatch[1]) matchedCrop = hiMatch[1].trim();

        function cleanStr(s) {
            if (!s) return '';
            return s.toLowerCase().replace(/\(.*?\)/g, '').replace(/[^a-z0-9]/g, '').trim();
        }

        const CROP_ALIASES = {
            'urad': 'blackgram',
            'tur': 'pigeonpeas',
            'arhar': 'pigeonpeas',
            'chana': 'chickpea',
            'corn': 'maize',
            'paddy': 'rice',
            'peanut': 'groundnut',
            'senga': 'groundnut',
            'soyabean': 'soybean',
            'soya': 'soybean',
            'capsicum': 'pepper',
            'matki': 'mothbeans',
            'moong': 'mungbean',
            'rajma': 'kidneybeans'
        };

        const cropDistSelect = document.querySelector('#districtSelect') || document.querySelector('select[name="district"]');
        const activeDistrict = cropDistSelect ? cropDistSelect.value : '';

        if (matchedCrop) {
            const rawTarget = cleanStr(matchedCrop);
            const targetClean = CROP_ALIASES[rawTarget] || rawTarget;
            
            // Auto-select crop in price prediction form
            const priceCropSelect = document.querySelector('#price select[name="crop"]');
            if (priceCropSelect) {
                for (let opt of priceCropSelect.options) {
                    if (!opt.value) continue;
                    const optKey = cleanStr(opt.value);
                    const optMapped = CROP_ALIASES[optKey] || optKey;
                    const optTxtKey = cleanStr(opt.textContent || '');

                    if (optKey === targetClean || optMapped === targetClean || 
                        optKey.includes(targetClean) || targetClean.includes(optKey) ||
                        optTxtKey.includes(targetClean) || targetClean.includes(optTxtKey) ||
                        optTxtKey.includes(rawTarget) || rawTarget.includes(optKey)) {
                        priceCropSelect.value = opt.value;
                        break;
                    }
                }
            }

            // Auto-select district in price prediction form
            if (activeDistrict) {
                const targetDistKey = cleanStr(activeDistrict);
                const priceDistSelect = document.querySelector('#price select[name="district"]');
                if (priceDistSelect) {
                    for (let opt of priceDistSelect.options) {
                        if (!opt.value) continue;
                        const optDistKey = cleanStr(opt.value);
                        if (optDistKey === targetDistKey || optDistKey.includes(targetDistKey) || targetDistKey.includes(optDistKey)) {
                            priceDistSelect.value = opt.value;
                            break;
                        }
                    }
                }
            }

            // Auto-select crop in leaf disease form
            const diseaseCropSelect = document.querySelector('#disease select[name="crop_type"]');
            if (diseaseCropSelect) {
                for (let opt of diseaseCropSelect.options) {
                    if (!opt.value) continue;
                    const optKey = cleanStr(opt.value);
                    const optMapped = CROP_ALIASES[optKey] || optKey;
                    if (optKey === targetClean || optMapped === targetClean || optKey.includes(targetClean) || targetClean.includes(optKey)) {
                        diseaseCropSelect.value = opt.value;
                        handleDiseaseCropChange(opt.value);
                        break;
                    }
                }
            }

            // Auto-select crop & district in precision irrigation form
            const irrCropSelect = document.querySelector('#irrigation select[name="crop"]');
            if (irrCropSelect) {
                for (let opt of irrCropSelect.options) {
                    if (!opt.value) continue;
                    const optKey = cleanStr(opt.value);
                    const optMapped = CROP_ALIASES[optKey] || optKey;
                    const optTxtKey = cleanStr(opt.textContent || '');

                    if (optKey === targetClean || optMapped === targetClean || 
                        optKey.includes(targetClean) || targetClean.includes(optKey) ||
                        optTxtKey.includes(targetClean) || targetClean.includes(optTxtKey) ||
                        optTxtKey.includes(rawTarget) || rawTarget.includes(optKey)) {
                        irrCropSelect.value = opt.value;
                        break;
                    }
                }
            }

            if (activeDistrict) {
                const targetDistKey = cleanStr(activeDistrict);
                const irrDistSelect = document.querySelector('#irrigation select[name="district"]');
                if (irrDistSelect) {
                    for (let opt of irrDistSelect.options) {
                        if (!opt.value) continue;
                        const optDistKey = cleanStr(opt.value);
                        if (optDistKey === targetDistKey || optDistKey.includes(targetDistKey) || targetDistKey.includes(optDistKey)) {
                            irrDistSelect.value = opt.value;
                            break;
                        }
                    }
                }
            }
        }
    }

    // Initialize disease form UI state on load
    const initialDiseaseSelect = document.getElementById('diseaseCropSelect');
    if (initialDiseaseSelect) {
        handleDiseaseCropChange(initialDiseaseSelect.value);
    }
});

function handleDiseaseCropChange(cropValue) {
    const select = document.getElementById('diseaseCropSelect');
    const uploadBox = document.getElementById('leafUploadContainer');
    const imageInput = document.getElementById('leafImageInput');
    const refNotice = document.getElementById('referenceOnlyNotice');
    const submitBtn = document.getElementById('diseaseSubmitBtn');

    if (!select) return;
    const selectedOpt = select.options[select.selectedIndex];
    if (!selectedOpt) return;

    const isDiagnosable = selectedOpt.getAttribute('data-is-diagnosable') === 'true';

    if (isDiagnosable) {
        if (uploadBox) uploadBox.style.display = 'block';
        if (imageInput) imageInput.required = true;
        if (refNotice) refNotice.style.display = 'none';
        if (submitBtn) {
            submitBtn.style.display = 'inline-block';
            submitBtn.disabled = false;
        }
    } else {
        if (uploadBox) uploadBox.style.display = 'none';
        if (imageInput) imageInput.required = false;
        if (refNotice) refNotice.style.display = 'block';
        if (submitBtn) {
            submitBtn.style.display = 'none';
            submitBtn.disabled = true;
        }
    }
}

