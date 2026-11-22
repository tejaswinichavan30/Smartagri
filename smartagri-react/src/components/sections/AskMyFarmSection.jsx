import { useState, useRef } from 'react';
import { useLanguage } from '../../context/LanguageContext.jsx';
import { api } from '../../api.js';
import { DISTRICTS, DISTRICT_TRANSLATIONS, getDistrictDropdownLabel } from '../../data/districts.js';

const SPEECH_LANG_MAP = { en: 'en-IN', kn: 'kn-IN', hi: 'hi-IN' };

function localizeCopilotText(text, lang) {
  if (!text || lang === 'en') return text;
  let s = String(text).trim();
  const lower = s.toLowerCase();

  // Confidence suffixes replacement
  s = s.replace(/\(high confidence\)/gi, lang === 'kn' ? '(ಹೆಚ್ಚಿನ ವಿಶ್ವಾಸಾರ್ಹತೆ)' : '(उच्च विश्वसनीयता)');
  s = s.replace(/\(medium confidence\)/gi, lang === 'kn' ? '(ಮಧ್ಯಮ ವಿಶ್ವಾಸಾರ್ಹತೆ)' : '(मध्यम विश्वसनीयता)');
  s = s.replace(/\(low confidence\)/gi, lang === 'kn' ? '(ಕಡಿಮೆ ವಿಶ್ವಾಸಾರ್ಹತೆ)' : '(कम विश्वसनीयता)');

  // Structured Badge Prefixes
  if (s.startsWith('Identified Crop:')) {
    const val = s.replace('Identified Crop:', '').trim();
    return lang === 'kn' ? `ಗುರುತಿಸಲಾದ ಬೆಳೆ: ${val}` : lang === 'hi' ? `पहचानी गई फसल: ${val}` : s;
  }
  if (s.startsWith('Identified Disease:')) {
    const val = s.replace('Identified Disease:', '').trim();
    return lang === 'kn' ? `ಗುರುತಿಸಲಾದ ರೋಗ: ${val}` : lang === 'hi' ? `पहचाना गया रोग: ${val}` : s;
  }
  if (s.startsWith('Health Status:') || s.startsWith('Health Assessment:')) {
    const val = s.replace(/^(Health Status:|Health Assessment:)/, '').trim();
    return lang === 'kn' ? `ಆರೋಗ್ಯ ಸ್ಥಿತಿ: ${val}` : lang === 'hi' ? `स्वास्थ्य स्थिति: ${val}` : s;
  }

  // Observations
  if (lower.includes('close-up view of a green leaf') || lower.includes('prominent white central midrib')) {
    return lang === 'kn' ? 'ಎಲೆಯ ಮಧ್ಯದಲ್ಲಿ ಬಿಳಿ ನಾಳವನ್ನು ತೋರಿಸುವ ಹಸಿರು ಎಲೆಯ ನಿಕಟ ನೋಟ.' : 'सफेद केंद्रीय शिरा दर्शाती हरी पत्ती का निकट दृश्य।';
  }
  if (lower.includes('distinct parallel leaf venation') || lower.includes('monocot')) {
    return lang === 'kn' ? 'ಏಕದಳ ಧಾನ್ಯದ ಎಲೆಗಳಿಗೆ ವಿಶಿಷ್ಟವಾದ ಸಮಾನಾಂತರ ನಾಳ ವಿನ್ಯಾಸ.' : 'एकबीजपत्री पत्तियों की विशिष्ट समानांतर शिरा विन्यास।';
  }
  if (lower.includes('uniform green coloration') || lower.includes('without distinct necrotic lesions')) {
    return lang === 'kn' ? 'ಕಾಣುವ ಎಲೆಯ ಮೇಲ್ಮೈಯಲ್ಲಿ ಕೀಟ ಅಥವಾ ರೋಗದ ಲಕ್ಷಣಗಳಿಲ್ಲದ ಏಕರೂಪದ ಹಸಿರು ಬಣ್ಣ.' : 'दिखने वाली पत्ती की सतह पर बिना किसी रोग या कीट क्षति के एकसमान हरा रंग।';
  }
  if (lower.includes('rust') && (lower.includes('pustule') || lower.includes('spots') || lower.includes('lesions'))) {
    return lang === 'kn' ? 'ಎಲೆಯ ಮೇಲ್ಮೈಯಲ್ಲಿ ಕಂದು-ಕೆಂಪು ಬಣ್ಣದ ತುಕ್ಕು ರೋಗದ ಮಚ್ಚೆಗಳು ಮತ್ತು ಸ್ಪೋರ್‌ಗಳು ಕಂಡುಬರುತ್ತಿವೆ.' : 'पत्ती की सतह पर लाल-भूरे रंग के रतुआ (रस्ट) रोग के धब्बे व बीजाणु दिखाई दे रहे हैं।';
  }

  // Limitations / What cannot be determined from this photo
  if (lower.includes('leaf underside') || lower.includes('underside') || lower.includes('presence of pests on the leaf') || lower.includes('presence of pests or diseases on lower') || lower.includes('ಎಲೆಯ ಹಿಂಭಾಗ') || lower.includes('ನಿಚಲಿ') || lower.includes('निचली')) {
    return lang === 'kn' ? 'ಎಲೆಯ ಹಿಂಭಾಗ ಅಥವಾ ಕೆಳಭಾಗದಲ್ಲಿ ಕೀಟಗಳ ಇರುವಿಕೆ.' : (lang === 'hi' ? 'पत्ती की निचली या छिपी सतह पर कीटों की उपस्थिति।' : 'Presence of pests on the leaf underside.');
  }
  if (lower.includes('condition of the rest of the plant') || lower.includes('rest of the plant or field') || lower.includes('overall health of the complete plant') || lower.includes('ಸಂಪೂರ್ಣ ಸಸ್ಯ') || lower.includes('ಉಳಿದ ಭಾಗದ') || lower.includes('शेष भाग')) {
    return lang === 'kn' ? 'ಸಂಪೂರ್ಣ ಸಸ್ಯ ಅಥವಾ ಹೊಲದ ಉಳಿದ ಭಾಗದ ಸ್ಥಿತಿ.' : (lang === 'hi' ? 'संपूर्ण पौधे या खेत के शेष भाग की स्थिति।' : 'Condition of the rest of the plant or field.');
  }
  if (lower.includes('viral or nutrient cause') || lower.includes('leaf distortion') || lower.includes('distortion without lab') || lower.includes('ಪ್ರಯೋಗಾಲಯದ ವಿಶ್ಲೇಷಣೆ') || lower.includes('ಎಲೆ ವಿರೂಪ') || lower.includes('विकृति') || lower.includes('प्रयोगशाला जांच')) {
    return lang === 'kn' ? 'ಪ್ರಯೋಗಾಲಯದ ವಿಶ್ಲೇಷಣೆಯಿಲ್ಲದೆ ಎಲೆ ವಿರೂಪಕ್ಕೆ ನಿಖರವಾದ ವೈರಸ್ ಅಥವಾ ಪೋಷಕಾಂಶದ ಕೊರತೆಯ ಕಾರಣ.' : (lang === 'hi' ? 'प्रयोगशाला जांच के बिना पत्ती के मुड़ने/विकृति का सटीक वायरल अथवा पोषक तत्व कारण।' : 'Exact viral or nutrient cause of leaf distortion without lab analysis.');
  }
  if (lower.includes('exact rust fungal species') || lower.includes('laboratory spore')) {
    return lang === 'kn' ? 'ಪ್ರಯೋಗಾಲಯದ ಸ್ಪೋರ್ ಪರೀಕ್ಷೆಯಿಲ್ಲದೆ ನಿಖರವಾದ ತುಕ್ಕು ಶಿಲೀಂಧ್ರ ತಳಿ ಗುರುತಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ.' : 'प्रयोगशाला बीजाणु परीक्षण के बिना सटीक रतुआ कवक प्रजाति की पहचान संभव नहीं है।';
  }
  if (lower.includes('overall infection severity')) {
    return lang === 'kn' ? 'ಸಂಪೂರ್ಣ ಹೊಲ ಅಥವಾ ಬೆಳೆ ವ್ಯಾಪ್ತಿಯ ಒಟ್ಟಾರೆ ಸೋಂಕಿನ ತೀವ್ರತೆ.' : 'संपूर्ण खेत या फसल क्षेत्र में समग्र संक्रमण की तीव्रता।';
  }
  if (lower.includes('exact crop species differentiation') || lower.includes('maize vs. sorghum')) {
    return lang === 'kn' ? 'ಕೇವಲ ಎಲೆಯ ತುಣುಕಿನಿಂದ ನಿಖರವಾದ ಬೆಳೆ ಪ್ರಭೇದದ ವ್ಯತ್ಯಾಸ (ಉದಾ. ಮೆಕ್ಕೆಜೋಳ vs ಜೋಳ).' : 'केवल पत्ती के भाग से सटीक फसल प्रजाति का अंतर (उदा. मक्का बनाम ज्वार)।';
  }
  if (lower.includes('nutritional deficiency status') || lower.includes('nutrient deficiencies')) {
    return lang === 'kn' ? 'ಸಮಗ್ರ ಸಸ್ಯದ ಪೋಷಕಾಂಶಗಳ ಕೊರತೆಯ ಸ್ಥಿತಿ.' : 'संपूर्ण पौधे की पोषक तत्वों की कमी की स्थिति।';
  }
  if (lower.includes('connected iot hardware sensor') || lower.includes('root-zone check')) {
    return lang === 'kn' ? 'ಮಣ್ಣಿನ ತೇವಾಂಶ ಮಟ್ಟ ತಿಳಿಯಲು ಐಒಟಿ ಹಾರ್ಡ್‌ವೇರ್ ಸೆನ್ಸರ್ ಅಥವಾ ಬೇರಿನ ವಲಯದ ಪರೀಕ್ಷೆ ಅಗತ್ಯ.' : 'मिट्टी की नमी का स्तर जानने के लिए IoT हार्डवेयर सेंसर या जड़ क्षेत्र की जांच आवश्यक है।';
  }
  if (lower.includes('soil nutrients or moisture') || lower.includes('soil nutrients')) {
    return lang === 'kn' ? 'ಮಣ್ಣಿನ ಪೋಷಕಾಂಶ ಅಥವಾ ತೇವಾಂಶದ ಮಟ್ಟ.' : 'मिट्टी के पोषक तत्व या नमी का स्तर।';
  }
  if (lower.includes('district not specified')) {
    return lang === 'kn' ? 'ಜಿಲ್ಲೆಯನ್ನು ಆಯ್ಕೆ ಮಾಡಿಲ್ಲ (ಎಪಿಎಂಸಿ ಮಂಡಿ ದರ ತಿಳಿಯಲು ಮೇಲಿನ ಪಟ್ಟಿಯಿಂದ ನಿಮ್ಮ ಜಿಲ್ಲೆ ಆಯ್ಕೆಮಾಡಿ).' : 'जिला निर्दिष्ट नहीं है (मंडी भाव देखने के लिए ऊपर ड्रॉपडाउन से अपना जिला चुनें)।';
  }
  if (lower.includes('internal rot') || lower.includes('sugar content') || lower.includes('soil chemistry')) {
    return lang === 'kn' ? 'ಆಂತರಿಕ ಕೊಳೆತ, ಸಕ್ಕರೆ ಪ್ರಮಾಣ ಅಥವಾ ಮಣ್ಣಿನ ರಾಸಾಯನಿಕತೆ.' : 'आंतरिक सड़न, शर्करा की मात्रा अथवा मिट्टी की रासायनिक स्थिति।';
  }

  // Management steps
  if (lower.includes('monitor field incidence') || lower.includes('rust typically spreads')) {
    return lang === 'kn'
      ? '1. ಹೊಲದ ತಪಾಸಣೆ ನಡೆಸಿ: ತುಕ್ಕು ರೋಗವು ತೇವಾಂಶ ಮತ್ತು ಮಧ್ಯಮ ತಾಪಮಾನದಲ್ಲಿ ಹರಡುತ್ತದೆ; ಹೊಲದಲ್ಲಿ ಮೇಲಿನ ಮತ್ತು ಕೆಳಗಿನ ಎಲೆಗಳನ್ನು ಸೂಕ್ಷ್ಮವಾಗಿ ಗಮನಿಸಿ.'
      : '1. खेत की निगरानी करें: रतुआ आमतौर पर आर्द्र मौसम और मध्यम तापमान में फैलता है; पूरे खेत में ऊपरी और निचली पत्तियों का निरीक्षण करें।';
  }
  if (lower.includes('cultural control') || lower.includes('row spacing')) {
    return lang === 'kn'
      ? '2. ಕೃಷಿ ನಿರ್ವಹಣೆ: ಗಾಳಿಯಾಡಲು ಸರಿಯಾದ ಸಾಲಿನ ಅಂತರ (60 x 20 ಸೆಂ.ಮೀ) ಕಾಪಾಡಿ, ತಡವಾಗಿ ಅತಿಯಾದ ಸಾರಜನಕ ನೀಡುವುದನ್ನು ತಪ್ಪಿಸಿ, ಕೊಯ್ಲಿನ ನಂತರ ರೋಗಪೀಡಿತ ಅವಶೇಷಗಳನ್ನು ನಾಶಮಾಡಿ.'
      : '2. सस्य प्रबंधन: वायु संचार के लिए उचित कतार दूरी (60 x 20 सेमी) बनाए रखें, देर से अत्यधिक नाइट्रोजन प्रयोग से बचें और कटाई बाद संक्रमित अवशेषों को नष्ट करें।';
  }
  if (lower.includes('fungicidal spray') || lower.includes('mancozeb') || lower.includes('tebuconazole') || lower.includes('tasseling')) {
    return lang === 'kn'
      ? '3. ಶಿಲೀಂಧ್ರನಾಶಕ ಸಿಂಪಡಣೆ: ತೆನೆ ಮೂಡುವ ಮುನ್ನ ಸೋಂಕು ತೀವ್ರವಾಗಿದ್ದರೆ, ಅಧಿಕೃತ ಶಿಫಾರಸಿನಂತೆ ಜೈವಿಕ ನಿಯಂತ್ರಕ (ಸ್ಯೂಡೋಮೊನಾಸ್ ಫ್ಲೋರೊಸೆನ್ಸ್) ಅಥವಾ ಮ್ಯಾಂಕೋಜೆಬ್ / ಟೆಬುಕೊನಜೋಲ್ ಸಿಂಪಡಣೆಗೆ ಸ್ಥಳೀಯ ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರ (KVK) ಸಂಪರ್ಕಿಸಿ.'
      : '3. कवकनाशी छिड़काव: यदि भुट्टा आने से पहले संक्रमण गंभीर हो, तो आधिकारिक पैकेज ऑफ प्रैक्टिसेज के अनुसार जैव-एजेंट (जैसे स्यूडोमोनास फ्लोरोसेंस) या मैंकोजेब अथवा टेबुकोनाज़ोल जैसे कवकनाशी हेतु स्थानीय कृषि विज्ञान केंद्र (KVK) से संपर्क करें।';
  }

  // When to consult KVK
  if (lower.includes('rust spots rapidly spread') || lower.includes('silking') || lower.includes('tasseling and silking')) {
    return lang === 'kn'
      ? 'ತೆನೆ ಮತ್ತು ಕದಿರು ಮೂಡುವ ಹಂತಕ್ಕೆ ಮುನ್ನ ತುಕ್ಕು ಮಚ್ಚೆಗಳು ಮೇಲಿನ ಎಲೆಗಳಿಗೆ ವೇಗವಾಗಿ ಹರಡಿದರೆ ಸ್ಥಳೀಯ ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರ (KVK) ಸಂಪರ್ಕಿಸಿ.'
      : 'यदि भुट्टे और फूल आने की अवस्था से पहले रतुआ के धब्बे तेजी से ऊपरी पत्तियों तक फैलें तो स्थानीय कृषि विज्ञान केंद्र (KVK) से संपर्क करें।';
  }

  return s;
}

function localizeMetricLabel(lbl, lang) {
  if (!lbl || lang === 'en') return lbl;
  const lower = String(lbl).toLowerCase();
  if (lower.includes('mandi modal price') || lower.includes('mandi')) {
    return lang === 'kn' ? 'ಮಂಡಿ ಮಾದರಿ ದರ' : 'मंडी मॉडल भाव';
  }
  if (lower.includes('soil moisture')) {
    return lang === 'kn' ? 'ಮಣ್ಣಿನ ತೇವಾಂಶ' : 'मिट्टी की नमी';
  }
  if (lower.includes('temperature') || lower.includes('temp')) {
    return lang === 'kn' ? 'ತಾಪಮಾನ' : 'तापमान';
  }
  if (lower.includes('humidity')) {
    return lang === 'kn' ? 'ಗಾಳಿಯ ತೇವಾಂಶ' : 'हवा में नमी';
  }
  return lbl;
}

function localizeSource(src, lang) {
  if (!src || lang === 'en') return src;
  const lower = String(src).toLowerCase();
  if (lower.includes('apmc') || lower.includes('agmarknet')) {
    return lang === 'kn' ? 'ಕರ್ನಾಟಕ ಎಪಿಎಂಸಿ / ಅಗ್ರ್‌ಮಾರ್ಕ್‌ನೆಟ್ ಬುಲೆಟಿನ್' : 'कर्नाटक एपीएमसी / एगमार्कनेट बुलेटिन';
  }
  if (lower.includes('openweathermap') || lower.includes('weather')) {
    return lang === 'kn' ? 'ಲೈವ್ ಹವಾಮಾನ ಉಪಗ್ರಹ ಡೇಟಾ' : 'लाइव मौसम उपग्रह डेटा';
  }
  if (lower.includes('kvk') || lower.includes('icar') || lower.includes('uas')) {
    return lang === 'kn' ? 'ಸ್ಥಳೀಯ ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರ (KVK)' : 'स्थानीय कृषि विज्ञान केंद्र (KVK)';
  }
  return src;
}

// Map internal scene and entity keys to clean localized names
const SCENE_TYPE_MAP = {
  leaf: { en: 'Crop Leaf', kn: 'ಬೆಳೆಯ ಎಲೆ', hi: 'फसल की पत्ती' },
  crop_leaf: { en: 'Crop Leaf', kn: 'ಬೆಳೆಯ ಎಲೆ', hi: 'फसल की पत्ती' },
  whole_plant: { en: 'Whole Plant', kn: 'ಸಂಪೂರ್ಣ ಗಿಡ', hi: 'संपूर्ण पौधा' },
  fruit_grain: { en: 'Fruit / Grain', kn: 'ಹಣ್ಣು / ಧಾನ್ಯ', hi: 'फल / अनाज' },
  pest_insect: { en: 'Pest / Insect', kn: 'ಕೀಟ / ಹುಳು', hi: 'कीट / इल्ली' },
  soil: { en: 'Soil Bed / Root Zone', kn: 'ಮಣ್ಣು / ಬೇರು ತಾಕು', hi: 'मिट्टी / जड़ क्षेत्र' },
  irrigation_equipment: { en: 'Irrigation Setup / Pipe', kn: 'ನೀರಾವರಿ ಉಪಕರಣ / ಪೈಪ್', hi: 'सिंचाई पाइप / उपकरण' },
  field_stand: { en: 'Crop Field / Stand', kn: 'ಬೆಳೆ ಜಮೀನು', hi: 'फसल का खेत' },
  farm_structure: { en: 'Farm Structure', kn: 'ಕೃಷಿ ರಚನೆ', hi: 'कृषि संरचना' },
  not_farm_related: { en: 'Non-Agricultural Subject', kn: 'ಕೃಷಿಯೇತರ ವಸ್ತು / ಚಿತ್ರ', hi: 'गैर-कृषि विषय' },
  not_sure: { en: 'Uncertain Subject', kn: 'ಅಸ್ಪಷ್ಟ ವಸ್ತು', hi: 'अस्पष्ट विषय' }
};

export default function AskMyFarmSection({ moduleState = {}, onResult }) {
  const { lang } = useLanguage();

  const [imageFile, setImageFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [district, setDistrict] = useState(moduleState.city || moduleState.district || '');
  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [loading, setLoading] = useState(false);
  const [resultData, setResultData] = useState(null);

  const fileInputRef = useRef(null);
  const recognitionRef = useRef(null);
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  // Quick sample prompts
  const samplePrompts = {
    en: [
      "How many liters of water per day for coconut?",
      "Why are these tomato leaves yellowing and wilting?",
      "What is the recommended spacing and fertilizer for maize?",
      "Why is water pooling near the drip pipe joint?"
    ],
    kn: [
      "ತೆಂಗಿನ ಮರಕ್ಕೆ ದಿನಕ್ಕೆ ಎಷ್ಟು ಲೀಟರ್ ನೀರು ಬೇಕು?",
      "ಟೊಮ್ಯಾಟೊ ಎಲೆಗಳು ಯಾಕೆ ಹಳದಿಯಾಗಿ ಬಾಡುತ್ತಿವೆ?",
      "ಮೆಕ್ಕೆಜೋಳಕ್ಕೆ ಶಿಫಾರಸು ಮಾಡಿದ ಅಂತರ ಮತ್ತು ಗೊಬ್ಬರ ಎಷ್ಟು?",
      "ಹನಿ ನೀರಾವರಿ ಪೈಪ್ ಬಳಿ ನೀರು ಯಾಕೆ ನಿಲ್ಲುತ್ತಿದೆ?"
    ],
    hi: [
      "नारियल के पेड़ को प्रतिदिन कितने लीटर पानी चाहिए?",
      "टमाटर की पत्तियां पीली होकर क्यों मुरझा रही हैं?",
      "मक्का के लिए अनुशंसित दूरी और खाद की मात्रा क्या है?",
      "ड्रिप पाइप के पास पानी क्यों जमा हो रहा है?"
    ]
  };

  const currentPrompts = samplePrompts[lang] || samplePrompts.en;

  async function startLiveCamera() {
    try {
      handleClearImage();
      setIsCameraOpen(true);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: 'environment' }, width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
    } catch (err) {
      console.error('Camera access error:', err);
      setIsCameraOpen(false);
      alert(lang === 'kn'
        ? 'ಕ್ಯಾಮೆರಾ ಪ್ರವೇಶಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಬ್ರೌಸರ್‌ನಲ್ಲಿ ಕ್ಯಾಮೆರಾ ಅನುಮತಿ ನೀಡಿ.'
        : lang === 'hi'
          ? 'कैमरा शुरू नहीं हो सका। कृपया ब्राउज़र में कैमरा अनुमति दें।'
          : 'Could not access camera. Please allow camera permissions in your browser.');
    }
  }

  function stopLiveCamera() {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setIsCameraOpen(false);
  }

  function snapPhoto() {
    if (!videoRef.current) return;
    const video = videoRef.current;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], `farm_snap_${Date.now()}.jpg`, { type: 'image/jpeg' });
        setImageFile(file);
        const url = URL.createObjectURL(blob);
        setPreviewUrl(url);
        stopLiveCamera();
      }
    }, 'image/jpeg', 0.90);
  }

  function handleImageChange(e) {
    const file = e.target.files?.[0];
    if (file) {
      stopLiveCamera();
      setImageFile(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    }
  }

  function handleClearImage() {
    stopLiveCamera();
    setImageFile(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }

  function startVoice() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert(lang === 'kn'
        ? 'ನಿಮ್ಮ ಬ್ರೌಸರ್‌ನಲ್ಲಿ ಧ್ವನಿ ಗುರುತಿಸುವಿಕೆ ಬೆಂಬಲಿತವಾಗಿಲ್ಲ. ದಯವಿಟ್ಟು Google Chrome ಬಳಸಿ.'
        : lang === 'hi'
          ? 'आपके ब्राउज़र में वॉइस इनपुट समर्थित नहीं है। कृपया Google Chrome का उपयोग करें।'
          : 'Voice recognition is not supported in this browser. Please use Google Chrome or Edge.');
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
      };

      recognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          transcript += event.results[i][0].transcript;
        }
        if (transcript) {
          setQuery(transcript.trim());
        }
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err) {
      console.error('Speech recognition exception:', err);
      setListening(false);
    }
  }

  async function handleConsultCopilot(e) {
    if (e) e.preventDefault();
    if (!query.trim() && !imageFile) {
      alert(lang === 'kn' ? 'ದಯವಿಟ್ಟು ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಅಥವಾ ಪ್ರಶ್ನೆ ಕೇಳಿ.' : lang === 'hi' ? 'कृपया फोटो अपलोड करें या सवाल पूछें।' : 'Please upload a farm photo or enter a query.');
      return;
    }

    setLoading(true);
    if (speaking) {
      api.stopSpeech();
      setSpeaking(false);
    }

    try {
      const fd = new FormData();
      if (imageFile) {
        fd.append('image', imageFile);
      }
      fd.append('query', query.trim() || 'Provide agronomic diagnosis and guidance');
      fd.append('crop', '');
      fd.append('district', district || '');
      fd.append('lang', lang);

      // Only pass real sensor data if explicitly present in module state
      if (moduleState.soilMoisture) {
        const sensorData = { moisture: moduleState.soilMoisture };
        fd.append('sensor_data', JSON.stringify(sensorData));
      }

      const res = await api.askMyFarm(fd);
      setResultData(res);
      if (onResult) onResult(res);

      // Speak answer automatically
      const speechText = buildSpeechText(res);
      if (speechText) {
        setTimeout(() => {
          togglePlayAudio(speechText);
        }, 400);
      }
    } catch (err) {
      console.error('Visual Copilot Error:', err);
      const errMsg = err?.message || '';
      if (errMsg.includes('502') || errMsg.includes('Failed to fetch') || errMsg.includes('NetworkError')) {
        alert('The server is currently waking up or completing an analysis. Please wait a few seconds and tap Get Farm Advice again.');
      } else {
        alert(errMsg || 'Error consulting Visual Copilot. Please verify backend connection.');
      }
    } finally {
      setLoading(false);
    }
  }

  function buildSpeechText(data) {
    if (!data) return '';
    const parts = [];
    if (data.answer_title) parts.push(data.answer_title);
    if (data.answer_summary) parts.push(data.answer_summary);
    if (Array.isArray(data.action_steps) && data.action_steps.length > 0) {
      parts.push(data.action_steps.join('. '));
    }
    return parts.join('. ');
  }

  function togglePlayAudio(customText = null) {
    if (speaking) {
      api.stopSpeech();
      setSpeaking(false);
      return;
    }

    const textToSpeak = customText || buildSpeechText(resultData);
    if (!textToSpeak) return;

    setSpeaking(true);
    api.playSpeech({
      text: textToSpeak,
      lang: lang,
      onStart: () => setSpeaking(true),
      onEnd: () => setSpeaking(false),
      onError: () => setSpeaking(false)
    });
  }

  // Sanitizes text to remove raw markdown syntax (*, #, `) and repetitive prefixes
  function renderCleanText(txt) {
    if (!txt) return '';
    return String(txt)
      .replace(/\[Not based on your photo\]\s*/gi, '')
      .replace(/\*\*(.*?)\*\*/g, '$1')
      .replace(/\*(.*?)\*/g, '$1')
      .replace(/`(.*?)`/g, '$1')
      .replace(/#{1,6}\s?/g, '')
      .trim();
  }

  function handleNavigateToModule(e, targetUrl) {
    if (e) e.preventDefault();
    if (!targetUrl) return;
    const rawId = String(targetUrl).replace('#', '').trim();
    // Resolve aliases to actual DOM section IDs
    let targetEl = document.getElementById(rawId);
    if (!targetEl) {
      if (rawId === 'market-price' || rawId === 'market_price' || rawId === 'price') {
        targetEl = document.getElementById('price') || document.getElementById('market-price');
      } else if (rawId === 'smart-irrigation' || rawId === 'smart_irrigation' || rawId === 'irrigation') {
        targetEl = document.getElementById('irrigation') || document.getElementById('smart-irrigation');
      } else if (rawId === 'crop-planner' || rawId === 'crop_planner' || rawId === 'planner') {
        targetEl = document.getElementById('planner');
      }
    }
    if (targetEl) {
      targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
      targetEl.style.transition = 'box-shadow 0.3s ease-in-out';
      targetEl.style.boxShadow = '0 0 20px rgba(34, 197, 94, 0.7)';
      setTimeout(() => {
        targetEl.style.boxShadow = '';
      }, 1500);
    } else {
      window.location.hash = targetUrl;
    }
  }

  const confidenceColor = {
    high: '#15803d',
    medium: '#d97706',
    low: '#dc2626'
  };

  return (
    <div className="section-card ask-my-farm-card" style={{
      background: 'linear-gradient(145deg, #f0fdf4 0%, #ffffff 100%)',
      border: '2px solid #86efac',
      borderRadius: '14px',
      padding: '16px 20px',
      marginBottom: '20px',
      boxShadow: '0 6px 20px rgba(22, 101, 52, 0.07)'
    }}>
      {/* Header Banner */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px', borderBottom: '1px solid #bbf7d0', paddingBottom: '10px', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '26px' }}>👁️‍🗨️</span>
          <div>
            <h2 style={{ margin: 0, color: '#14532d', fontSize: '1.2rem', fontWeight: '700' }}>
              {lang === 'kn' ? '"ಆಸ್ಕ್ ಮೈ ಫಾರ್ಮ್" - ದೃಶ್ಯ ಮತ್ತು ಧ್ವನಿ ಕೃಷಿ ಸಲಹೆಗಾರ' : lang === 'hi' ? '"आस्क माई फार्म" - विजुअल और वॉइस कृषि सहायक' : '"Ask My Farm" Visual Multi-Agent Copilot'}
            </h2>
            <p style={{ margin: '2px 0 0', color: '#15803d', fontSize: '0.78rem' }}>
              {lang === 'kn' ? 'ನಿಖರವಾದ ಫೋಟೋ ಮತ್ತು ಧ್ವನಿ ಆಧಾರಿತ ನೈಜ ಕೃಷಿ ಪರಿಹಾರ' : lang === 'hi' ? 'सटीक फोटो और आवाज आधारित वास्तविक कृषि परामर्श' : 'Strictly Grounded Visual Perception & Region-Attributed Agronomy'}
            </p>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <span style={{
            background: '#dcfce7',
            color: '#166534',
            padding: '4px 10px',
            borderRadius: '16px',
            fontSize: '0.74rem',
            fontWeight: '600',
            border: '1px solid #86efac'
          }}>
            🔒 Privacy Safe & Zero-Hallucination
          </span>
        </div>
      </div>

      {/* Input Grid: Camera & Voice */}
      <form onSubmit={handleConsultCopilot}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px', marginBottom: '14px' }}>

          {/* Left: Image Uploader / Camera */}
          <div style={{
            border: '2px dashed #86efac',
            borderRadius: '10px',
            padding: '12px',
            background: '#f9fdfa',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '110px',
            position: 'relative'
          }}>
            {isCameraOpen ? (
              <div style={{ width: '100%', textAlign: 'center' }}>
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  style={{
                    width: '100%',
                    maxHeight: '200px',
                    borderRadius: '8px',
                    objectFit: 'cover',
                    border: '2px solid #22c55e',
                    background: '#000'
                  }}
                />
                <div style={{ marginTop: '10px', display: 'flex', gap: '8px', justifyContent: 'center' }}>
                  <button
                    type="button"
                    onClick={snapPhoto}
                    style={{
                      background: 'linear-gradient(135deg, #15803d 0%, #22c55e 100%)',
                      color: '#ffffff',
                      border: 'none',
                      borderRadius: '8px',
                      padding: '8px 16px',
                      fontSize: '0.85rem',
                      fontWeight: '700',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      boxShadow: '0 2px 8px rgba(34, 197, 94, 0.4)'
                    }}
                  >
                    📸 {lang === 'kn' ? 'ಫೋಟೋ ಕ್ಲಿಕ್ ಮಾಡಿ' : lang === 'hi' ? 'फोटो खींचें' : 'Snap Photo'}
                  </button>
                  <button
                    type="button"
                    onClick={stopLiveCamera}
                    style={{
                      background: '#fee2e2',
                      color: '#991b1b',
                      border: '1px solid #f87171',
                      borderRadius: '8px',
                      padding: '8px 12px',
                      fontSize: '0.82rem',
                      cursor: 'pointer'
                    }}
                  >
                    ✕ {lang === 'kn' ? 'ಮುಚ್ಚಿ' : lang === 'hi' ? 'बंद करें' : 'Close'}
                  </button>
                </div>
              </div>
            ) : previewUrl ? (
              <div style={{ width: '100%', textAlign: 'center' }}>
                <img
                  src={previewUrl}
                  alt="Farm preview"
                  style={{ maxHeight: '110px', maxWidth: '100%', borderRadius: '8px', objectFit: 'contain', border: '1px solid #86efac' }}
                />
                <div style={{ marginTop: '4px' }}>
                  <button
                    type="button"
                    onClick={handleClearImage}
                    style={{
                      background: '#fee2e2',
                      color: '#991b1b',
                      border: '1px solid #f87171',
                      borderRadius: '6px',
                      padding: '3px 8px',
                      fontSize: '0.72rem',
                      cursor: 'pointer'
                    }}
                  >
                    ✕ {lang === 'kn' ? 'ಫೋಟೋ ತೆಗೆಯಿರಿ' : lang === 'hi' ? 'फोटो हटाएं' : 'Remove Photo'}
                  </button>
                </div>
              </div>
            ) : (
              <>
                <span style={{ fontSize: '24px', marginBottom: '4px' }}>📷</span>
                <p style={{ margin: '0 0 6px', fontSize: '0.8rem', color: '#166534', fontWeight: '500', textAlign: 'center' }}>
                  {lang === 'kn' ? 'ಬೆಳೆ, ಎಲೆ ಅಥವಾ ಜಮೀನಿನ ಫೋಟೋ ತೆಗೆದುಕೊಳ್ಳಿ' : lang === 'hi' ? 'फसल, पत्ती या खेत की फोटो लें' : 'Snap Camera or Upload Photo'}
                </p>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', justifyContent: 'center' }}>
                  <button
                    type="button"
                    onClick={startLiveCamera}
                    style={{
                      background: 'linear-gradient(135deg, #15803d 0%, #16a34a 100%)',
                      color: '#ffffff',
                      border: 'none',
                      borderRadius: '8px',
                      padding: '6px 12px',
                      fontSize: '0.78rem',
                      cursor: 'pointer',
                      fontWeight: '600',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                  >
                    📸 {lang === 'kn' ? 'ಲೈವ್ ಕ್ಯಾಮೆರಾ' : lang === 'hi' ? 'लाइव कैमरा' : 'Open Camera'}
                  </button>
                  <input
                    type="file"
                    accept="image/*"
                    capture="environment"
                    ref={fileInputRef}
                    onChange={handleImageChange}
                    style={{ display: 'none' }}
                    id="copilot-file-input"
                  />
                  <label
                    htmlFor="copilot-file-input"
                    style={{
                      background: '#e0f2fe',
                      color: '#0369a1',
                      border: '1px solid #bae6fd',
                      padding: '8px 14px',
                      borderRadius: '8px',
                      fontSize: '0.82rem',
                      cursor: 'pointer',
                      fontWeight: '600',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                  >
                    📁 {lang === 'kn' ? 'ಗ್ಯಾಲರಿ / ಫೈಲ್' : lang === 'hi' ? 'गैलरी / फाइल' : 'Upload File'}
                  </label>
                </div>
              </>
            )}
          </div>

          {/* Right: Farmer Voice / Text Query & District Selection */}
          <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              {/* District Dropdown Selector */}
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.84rem', fontWeight: '600', color: '#14532d', marginBottom: '4px' }}>
                  <span>📍 {lang === 'kn' ? 'ಜಿಲ್ಲೆ (ಮಾರುಕಟ್ಟೆ & ಹವಾಮಾನಕ್ಕಾಗಿ):' : lang === 'hi' ? 'ज़िला (मंडी भाव एवं मौसम हेतु):' : 'District (For Live Market & Weather):'}</span>
                  {!district && (
                    <span style={{ fontSize: '0.72rem', color: '#b45309', fontWeight: 'normal' }}>
                      {lang === 'kn' ? '(ಆಯ್ಕೆಮಾಡಿಲ್ಲ)' : lang === 'hi' ? '(चयनित नहीं)' : '(Not selected)'}
                    </span>
                  )}
                </label>
                <select
                  value={district}
                  onChange={(e) => setDistrict(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    borderRadius: '8px',
                    border: '1px solid #86efac',
                    background: '#ffffff',
                    fontSize: '0.85rem',
                    color: district ? '#14532d' : '#64748b',
                    outline: 'none'
                  }}
                >
                  <option value="">
                    {lang === 'kn' ? '-- ಜಿಲ್ಲೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ --' : lang === 'hi' ? '-- अपना जिला चुनें --' : '-- Select Your District --'}
                  </option>
                  {DISTRICTS.map((d) => (
                    <option key={d} value={d}>
                      {getDistrictDropdownLabel(d, lang)}
                    </option>
                  ))}
                </select>
                {!district && (
                  <p style={{ margin: '4px 0 0', fontSize: '0.72rem', color: '#b45309' }}>
                    ⚠️ {lang === 'kn' ? 'ಲೈವ್ ಬೆಲೆ ಮತ್ತು ಸ್ಥಳೀಯ ಹವಾಮಾನಕ್ಕಾಗಿ ಜಿಲ್ಲೆ ಆಯ್ಕೆಮಾಡಿ.' : lang === 'hi' ? 'लाइव मंडी भाव एवं स्थानीय मौसम के लिए जिला चुनें।' : 'Select district for localized APMC market rates and weather.'}
                  </p>
                )}
              </div>

              <label style={{ display: 'block', fontSize: '0.88rem', fontWeight: '600', color: '#14532d', marginBottom: '8px' }}>
                {lang === 'kn' ? '🎤 ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಹೇಳಿ / ಬರೆಯಿರಿ:' : lang === 'hi' ? '🎤 अपना सवाल बोलें / लिखें:' : '🎤 Speak or type your question:'}
              </label>
              <div style={{ display: 'flex', gap: '8px', marginBottom: '10px' }}>
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder={lang === 'kn' ? 'ಉದಾ: ತೆಂಗಿನ ಮರಕ್ಕೆ ದಿನಕ್ಕೆ ಎಷ್ಟು ಲೀಟರ್ ನೀರು ಬೇಕು?' : lang === 'hi' ? 'उदा: नारियल के पेड़ को प्रतिदिन कितने लीटर पानी चाहिए?' : 'e.g. How many liters of water per day for coconut?'}
                  style={{
                    flex: 1,
                    padding: '10px 14px',
                    borderRadius: '8px',
                    border: '1px solid #86efac',
                    fontSize: '0.9rem',
                    outline: 'none'
                  }}
                />
                <button
                  type="button"
                  onClick={startVoice}
                  style={{
                    background: listening ? '#ef4444' : '#22c55e',
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '8px',
                    padding: '0 16px',
                    cursor: 'pointer',
                    fontSize: '1rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    transition: 'all 0.2s',
                    boxShadow: listening ? '0 0 12px rgba(239, 68, 68, 0.5)' : 'none'
                  }}
                  title={listening ? 'Listening...' : 'Click to Speak'}
                >
                  {listening ? '🔴' : '🎤'}
                </button>
              </div>

              {/* Quick sample chips */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {currentPrompts.map((p, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => setQuery(p)}
                    style={{
                      background: '#e0f2fe',
                      color: '#0369a1',
                      border: '1px solid #bae6fd',
                      borderRadius: '12px',
                      padding: '4px 8px',
                      fontSize: '0.72rem',
                      cursor: 'pointer',
                      textAlign: 'left'
                    }}
                  >
                    💡 {p}
                  </button>
                ))}
              </div>
            </div>

            {/* Submit Button & Privacy Note */}
            <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
              <span style={{ fontSize: '0.72rem', color: '#64748b' }}>
                🛡️ {lang === 'kn' ? 'ಫೋಟೋಗಳನ್ನು ಕೃಷಿ ರೋಗನಿರ್ಣಯಕ್ಕೆ ಮಾತ್ರ ಬಳಸಲಾಗುತ್ತದೆ.' : lang === 'hi' ? 'फोटो केवल कृषि निदान हेतु उपयोग की जाती है।' : 'Photos are processed securely for farm diagnostics.'}
              </span>
              <button
                type="submit"
                disabled={loading}
                style={{
                  background: 'linear-gradient(135deg, #15803d 0%, #16a34a 100%)',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '10px',
                  padding: '10px 20px',
                  fontSize: '0.92rem',
                  fontWeight: '700',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  boxShadow: '0 4px 12px rgba(22, 101, 52, 0.2)'
                }}
              >
                {loading ? (
                  <>
                    <span className="spinner" style={{ display: 'inline-block', width: '14px', height: '14px', border: '2px solid #fff', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
                    {lang === 'kn' ? 'ಪರಿಶೀಲಿಸಲಾಗುತ್ತಿದೆ...' : lang === 'hi' ? 'विश्लेषण जारी है...' : 'Analyzing...'}
                  </>
                ) : (
                  <>
                    <span>🚀</span> {lang === 'kn' ? 'ಸಲಹೆ ಪಡೆಯಿರಿ' : lang === 'hi' ? 'सलाह प्राप्त करें' : 'Get Farm Advice'}
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </form>

      {/* Results View */}
      {resultData && (
        <div style={{ marginTop: '24px', borderTop: '2px solid #86efac', paddingTop: '20px' }}>

          {/* Header with Title & Audio */}
          <div style={{
            background: '#ecfdf5',
            border: '1px solid #6ee7b7',
            borderRadius: '12px',
            padding: '14px 18px',
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '12px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '24px' }}>📢</span>
              <div>
                <h3 style={{ margin: 0, color: '#065f46', fontSize: '1.05rem', fontWeight: '700' }}>
                  {renderCleanText(resultData.answer_title || 'Farm Advisory')}
                </h3>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginTop: '4px' }}>
                  <span style={{
                    fontSize: '0.72rem',
                    background: '#ffffff',
                    color: confidenceColor[resultData.overall_confidence] || '#15803d',
                    padding: '2px 8px',
                    borderRadius: '10px',
                    fontWeight: '700',
                    border: '1px solid #cbd5e1'
                  }}>
                    ● Confidence: {(resultData.overall_confidence || 'Medium').toUpperCase()}
                  </span>
                  {resultData.answered_from && (
                    <span style={{ fontSize: '0.72rem', color: '#047857' }}>
                      ({resultData.answered_from === 'photo' ? 'From Photo' : resultData.answered_from === 'text_only' ? 'General Guidance - Not based on photo' : 'Photo + Telemetry Grounded'})
                    </span>
                  )}
                </div>
              </div>
            </div>

            <button
              type="button"
              onClick={() => togglePlayAudio()}
              style={{
                background: speaking ? '#ef4444' : '#059669',
                color: '#ffffff',
                border: 'none',
                borderRadius: '8px',
                padding: '8px 18px',
                fontWeight: '600',
                fontSize: '0.85rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <span>{speaking ? '⏹️' : '🔊'}</span>
              {speaking ? (lang === 'kn' ? 'ನಿಲ್ಲಿಸಿ' : lang === 'hi' ? 'रोकें' : 'Stop Audio') : (lang === 'kn' ? 'ಧ್ವನಿ ಪ್ಲೇ ಮಾಡಿ' : lang === 'hi' ? 'आवाज सुनें' : 'Speak Answer')}
            </button>
          </div>

          {/* Main Content Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px', marginBottom: '16px' }}>

            {/* Block 1: What I Can See (Strictly grounded in photo) */}
            {Array.isArray(resultData.observations) && resultData.observations.length > 0 && (
              <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '16px' }}>
                <h4 style={{ margin: '0 0 10px', color: '#334155', fontSize: '0.92rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span>👁️</span> {lang === 'kn' ? 'ಚಿತ್ರದಲ್ಲಿ ಕಂಡುಬಂದ ಅಂಶಗಳು' : lang === 'hi' ? 'फोटो में स्पष्ट रूप से दिखा' : 'What I Can See in this Photo'}
                </h4>
                <div style={{ fontSize: '0.82rem', color: '#475569', lineHeight: '1.6' }}>
                  {resultData.scene_type && (
                    <div style={{ marginBottom: '8px' }}>
                      <strong>{lang === 'kn' ? 'ಗುರುತಿಸಲಾದ ಭಾಗ:' : lang === 'hi' ? 'पहचाना गया तत्व:' : 'Subject:'}</strong>{' '}
                      <span style={{ color: '#0f766e', fontWeight: '600' }}>
                        {SCENE_TYPE_MAP[resultData.scene_type]?.[lang] || SCENE_TYPE_MAP[resultData.scene_type]?.en || resultData.scene_type}
                      </span>
                    </div>
                  )}
                  {(resultData.identified_crop_display || resultData.identified_crop) && (
                    <div style={{ marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <strong>{lang === 'kn' ? 'ಗುರುತಿಸಲಾದ ಬೆಳೆ:' : lang === 'hi' ? 'पहचानी गई फसल:' : 'Identified Crop:'}</strong>{' '}
                      <span style={{
                        background: '#ecfdf5',
                        color: '#065f46',
                        padding: '3px 10px',
                        borderRadius: '6px',
                        fontWeight: '700',
                        fontSize: '0.85rem',
                        border: '1px solid #a7f3d0'
                      }}>
                        🌿 {resultData.identified_crop_display || resultData.identified_crop}
                      </span>
                    </div>
                  )}
                  {(resultData.identified_disease_display || resultData.apparent_disorder || resultData.identified_disease) && (
                    <div style={{ marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <strong>{lang === 'kn' ? 'ಗುರುತಿಸಲಾದ ರೋಗ:' : lang === 'hi' ? 'पहचाना गया रोग:' : 'Identified Disease:'}</strong>{' '}
                      <span style={{
                        background: '#fef2f2',
                        color: '#b91c1c',
                        padding: '3px 10px',
                        borderRadius: '6px',
                        fontWeight: '700',
                        fontSize: '0.85rem',
                        border: '1px solid #fecaca'
                      }}>
                        🦠 {resultData.identified_disease_display || resultData.apparent_disorder || resultData.identified_disease}
                      </span>
                    </div>
                  )}
                  {resultData.is_healthy === true && !resultData.identified_disease && (
                    <div style={{ marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <strong>{lang === 'kn' ? 'ಆರೋಗ್ಯ ಸ್ಥಿತಿ:' : lang === 'hi' ? 'स्वास्थ्य स्थिति:' : 'Health Status:'}</strong>{' '}
                      <span style={{
                        background: '#ecfdf5',
                        color: '#065f46',
                        padding: '3px 10px',
                        borderRadius: '6px',
                        fontWeight: '700',
                        fontSize: '0.85rem',
                        border: '1px solid #a7f3d0'
                      }}>
                        ✅ {lang === 'kn' ? 'ಆರೋಗ್ಯಕರ (ರೋಗಮುಕ್ತ)' : lang === 'hi' ? 'स्वस्थ (रोगमुक्त)' : 'Healthy (No Disease)'}
                      </span>
                    </div>
                  )}
                  <ul style={{ margin: 0, paddingLeft: '18px' }}>
                    {resultData.observations.map((obs, idx) => {
                      const rawText = typeof obs === 'object' ? obs.text : obs;
                      const localizedText = localizeCopilotText(rawText, lang);
                      const confLabel = typeof obs === 'object' && obs.confidence
                        ? (lang === 'kn' ? (obs.confidence === 'high' ? 'ಹೆಚ್ಚಿನ ವಿಶ್ವಾಸಾರ್ಹತೆ' : 'ಮಧ್ಯಮ ವಿಶ್ವಾಸಾರ್ಹತೆ') : lang === 'hi' ? (obs.confidence === 'high' ? 'उच्च विश्वसनीयता' : 'मध्यम विश्वसनीयता') : `${obs.confidence} confidence`)
                        : null;
                      return (
                        <li key={idx} style={{ marginBottom: '4px' }}>
                          {localizedText}
                          {confLabel && (
                            <span style={{ fontSize: '0.7rem', color: '#94a3b8', marginLeft: '6px' }}>
                              ({confLabel})
                            </span>
                          )}
                        </li>
                      );
                    })}
                  </ul>
                </div>
              </div>
            )}

            {/* Block 2: Grounded Answer & Details */}
            <div style={{ background: '#ffffff', border: '1px solid #bbf7d0', borderRadius: '10px', padding: '16px' }}>
              <h4 style={{ margin: '0 0 8px', color: '#166534', fontSize: '0.92rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span>💡</span> {lang === 'kn' ? 'ಕೃಷಿ ಸಲಹೆ & ವಿವರಣೆ' : lang === 'hi' ? 'कृषि सलाह एवं समाधान' : 'Practical Agronomic Answer'}
              </h4>
              <p style={{ fontSize: '0.88rem', color: '#14532d', fontWeight: '600', margin: '0 0 10px', lineHeight: '1.5' }}>
                {renderCleanText(resultData.answer_summary)}
              </p>
              {Array.isArray(resultData.details) && resultData.details.length > 0 && (
                <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '0.82rem', color: '#334155', lineHeight: '1.5' }}>
                  {resultData.details.map((d, idx) => (
                    <li key={idx} style={{ marginBottom: '4px' }}>{renderCleanText(localizeCopilotText(d, lang))}</li>
                  ))}
                </ul>
              )}
            </div>

          </div>

          {/* Block 3: Quantities & Data Telemetry Table with Real Sources */}
          {((Array.isArray(resultData.numbers) && resultData.numbers.length > 0) || (Array.isArray(resultData.module_links) && resultData.module_links.length > 0)) && (
            <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '16px', marginBottom: '16px' }}>
              <h4 style={{ margin: '0 0 10px', color: '#334155', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span>📊</span> {lang === 'kn' ? 'ಉತ್ತರಕ್ಕೆ ಸಂಬಂಧಿಸಿದ ಅಂಕಿಅಂಶಗಳು' : lang === 'hi' ? 'उत्तर से संबंधित मात्रा एवं माप' : 'Quantities & Telemetry (Intent Answer)'}
              </h4>

              {Array.isArray(resultData.numbers) && resultData.numbers.length > 0 && (
                <>
                  <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem', textAlign: 'left' }}>
                      <thead>
                        <tr style={{ background: '#e2e8f0', color: '#334155' }}>
                          <th style={{ padding: '6px 10px', border: '1px solid #cbd5e1' }}>
                            {lang === 'kn' ? 'ಪ್ಯಾರಾಮೀಟರ್ / ವಿವರ' : lang === 'hi' ? 'मापदंड / विवरण' : 'Metric / Parameter'}
                          </th>
                          <th style={{ padding: '6px 10px', border: '1px solid #cbd5e1' }}>
                            {lang === 'kn' ? 'ಮೌಲ್ಯ ಮತ್ತು ಘಟಕ' : lang === 'hi' ? 'मान एवं इकाई' : 'Value & Unit'}
                          </th>
                          <th style={{ padding: '6px 10px', border: '1px solid #cbd5e1' }}>
                            {lang === 'kn' ? 'ಮೂಲ / ದೃಢೀಕರಣ' : lang === 'hi' ? 'स्रोत / सत्यापन' : 'Source / Attribution'}
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {resultData.numbers.map((num, i) => (
                          <tr key={i} style={{ background: i % 2 === 0 ? '#ffffff' : '#f1f5f9' }}>
                            <td style={{ padding: '6px 10px', border: '1px solid #cbd5e1', fontWeight: '600' }}>
                              {localizeMetricLabel(num.label, lang)}
                            </td>
                            <td style={{ padding: '6px 10px', border: '1px solid #cbd5e1', color: '#0f766e', fontWeight: '700' }}>
                              {num.value} {num.unit}
                            </td>
                            <td style={{ padding: '6px 10px', border: '1px solid #cbd5e1', color: '#64748b' }}>
                              {localizeSource(num.source, lang)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Collapsible Data and Sources details */}
                  <details style={{ marginTop: '12px', background: '#f1f5f9', padding: '8px 12px', borderRadius: '8px', border: '1px solid #cbd5e1' }}>
                    <summary style={{ cursor: 'pointer', fontWeight: '600', color: '#334155', fontSize: '0.78rem' }}>
                      ℹ️ {lang === 'kn' ? 'ಡೇಟಾ ಮತ್ತು ಮೂಲಗಳ ವಿವರಗಳು' : lang === 'hi' ? 'डेटा एवं स्रोत विवरण' : 'Data and Sources / Assumptions'}
                    </summary>
                    <div style={{ marginTop: '8px', fontSize: '0.75rem', color: '#475569', lineHeight: '1.5' }}>
                      {resultData.numbers.map((num, idx) => (
                        <div key={idx} style={{ marginBottom: '6px' }}>
                          <strong>{num.label}:</strong> {num.source} {num.assumptions ? `— (${num.assumptions})` : ''}
                        </div>
                      ))}
                    </div>
                  </details>
                </>
              )}

              {/* Module Link Shortcuts for Other Agricultural Information */}
              {Array.isArray(resultData.module_links) && resultData.module_links.length > 0 && (
                <div style={{ marginTop: '14px', paddingTop: '12px', borderTop: '1px dashed #cbd5e1' }}>
                  <span style={{ fontSize: '0.78rem', fontWeight: '600', color: '#475569', display: 'block', marginBottom: '8px' }}>
                    🔗 {lang === 'kn' ? 'ಇತರ ಕೃಷಿ ಮಾಡ್ಯೂಲ್‌ಗಳನ್ನು ತೆರೆಯಿರಿ:' : lang === 'hi' ? 'अन्य कृषि मॉड्यूल देखें:' : 'Explore Related Tools for Other Info:'}
                  </span>
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                    {resultData.module_links.map((link, idx) => (
                      <a
                        key={idx}
                        href={link.url}
                        onClick={(e) => handleNavigateToModule(e, link.url)}
                        style={{
                          textDecoration: 'none',
                          background: '#e0f2fe',
                          color: '#0369a1',
                          border: '1px solid #bae6fd',
                          padding: '6px 12px',
                          borderRadius: '6px',
                          fontSize: '0.78rem',
                          fontWeight: '600',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px',
                          cursor: 'pointer',
                          transition: 'all 0.15s ease-in-out'
                        }}
                      >
                        <span>📌</span> {link.label}
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Block 4: Recommended Action Steps & Safety */}
          {Array.isArray(resultData.action_steps) && resultData.action_steps.length > 0 && (
            <div style={{ background: '#f0fdf4', border: '1px solid #86efac', borderRadius: '10px', padding: '16px', marginBottom: '16px' }}>
              <h4 style={{ margin: '0 0 8px', color: '#166534', fontSize: '0.9rem' }}>
                📋 {lang === 'kn' ? 'ಕ್ರಮಬದ್ಧ ನಿರ್ವಹಣಾ ಹಂತಗಳು:' : lang === 'hi' ? 'अनुशंसित प्रबंधन कदम:' : 'Recommended Action Steps:'}
              </h4>
              <ol style={{ margin: 0, paddingLeft: '20px', fontSize: '0.82rem', color: '#14532d', lineHeight: '1.6' }}>
                {resultData.action_steps.map((step, idx) => (
                  <li key={idx} style={{ marginBottom: '4px' }}>{renderCleanText(localizeCopilotText(step, lang))}</li>
                ))}
              </ol>
              <div style={{ marginTop: '10px', padding: '8px 12px', background: '#fef3c7', borderRadius: '6px', border: '1px solid #fde68a', fontSize: '0.78rem', color: '#92400e' }}>
                ⚠️ <strong>{lang === 'kn' ? 'ಗಮನಿಸಿ:' : lang === 'hi' ? 'सूचना:' : 'Note:'}</strong> {lang === 'kn' ? 'ಉತ್ಪನ್ನದ ಲೇಬಲ್‌ನಲ್ಲಿರುವ ಪ್ರಮಾಣವನ್ನು ಪರಿಶೀಲಿಸಿ ಮತ್ತು ನಿಮ್ಮ ಕೆವಿಕೆಯೊಂದಿಗೆ ಖಚಿತಪಡಿಸಿ. ಸುರಕ್ಷತಾ ನಿಯಮಗಳನ್ನು ಪಾಲಿಸಿ.' : lang === 'hi' ? 'उत्पाद लेबल पर दी गई मात्रा की जांच करें और अपने केवीके से पुष्टि करें। सुरक्षा निर्देशों का पालन करें।' : 'Check the dose on the product label and confirm with your KVK. Follow safety instructions.'}
              </div>
            </div>
          )}

          {/* Block 5: What I Cannot Tell & When to Contact KVK */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px' }}>
            {Array.isArray(resultData.what_i_cannot_tell) && resultData.what_i_cannot_tell.length > 0 && (
              <div style={{ background: '#fffbeb', border: '1px solid #fde68a', borderRadius: '8px', padding: '12px' }}>
                <h5 style={{ margin: '0 0 6px', color: '#92400e', fontSize: '0.82rem' }}>
                  ❓ {resultData.answered_from === 'text_only' ? (
                    lang === 'kn'
                      ? 'ಮಾಹಿತಿ ಮಿತಿಗಳು ಮತ್ತು ಅಗತ್ಯ ವಿವರಗಳು:'
                      : lang === 'hi'
                        ? 'सूचना की सीमाएं एवं आवश्यक विवरण:'
                        : 'Information Limitations & Unprovided Inputs:'
                  ) : (
                    lang === 'kn'
                      ? 'ಈ ಫೋಟೋದಿಂದ ತಿಳಿಯಲಾಗದ ಅಂಶಗಳು:'
                      : lang === 'hi'
                        ? 'इस फोटो से जो नहीं बताया जा सकता:'
                        : 'What I Cannot Tell From This Photo:'
                  )}
                </h5>
                <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '0.78rem', color: '#78350f', lineHeight: '1.4' }}>
                  {resultData.what_i_cannot_tell.map((item, idx) => (
                    <li key={idx}>{renderCleanText(localizeCopilotText(item, lang))}</li>
                  ))}
                </ul>
              </div>
            )}

            {resultData.see_expert_if && (
              <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '8px', padding: '12px' }}>
                <h5 style={{ margin: '0 0 6px', color: '#991b1b', fontSize: '0.82rem' }}>
                  🏥 {lang === 'kn' ? 'ತಜ್ಞರನ್ನು / KVK ಸಂಪರ್ಕಿಸುವ ಸಂದರ್ಭ:' : lang === 'hi' ? 'कृषि विशेषज्ञ / KVK से कब संपर्क करें:' : 'When to Contact Local KVK:'}
                </h5>
                <p style={{ margin: 0, fontSize: '0.78rem', color: '#7f1d1d', lineHeight: '1.4' }}>
                  {renderCleanText(localizeCopilotText(resultData.see_expert_if, lang))}
                </p>
              </div>
            )}
          </div>

        </div>
      )}
    </div>
  );
}
