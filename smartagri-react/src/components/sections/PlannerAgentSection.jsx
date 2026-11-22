import { useState, useEffect, useRef } from 'react';
import { useLanguage } from '../../context/LanguageContext.jsx';
import { api } from '../../api.js';
import { getCropName, getDistrictName, getCropDropdownLabel, getDistrictDropdownLabel } from '../../data/districts.js';
import { CROP_AGRONOMY } from '../../data/crop_agronomy.js';

function isWrongScript(text, targetLang) {
  if (!text) return true;
  const s = String(text);
  const hasKannada = /[\u0C80-\u0CFF]/.test(s);
  const hasDevanagari = /[\u0900-\u097F]/.test(s);

  if (targetLang === 'hi') {
    if (hasKannada) return true;
  } else if (targetLang === 'kn') {
    if (hasDevanagari) return true;
  } else if (targetLang === 'en') {
    if (hasKannada || hasDevanagari) return true;
  }
  return false;
}

function getCanonicalCropKey(crop) {
  if (!crop) return 'groundnut';
  const c = String(crop).toLowerCase().trim();
  const map = {
    'peanuts': 'groundnut', 'peanut': 'groundnut', 'ಕಡಲೆಕಾಯಿ': 'groundnut', 'ಶೇಂಗಾ': 'groundnut', 'मूंगफली': 'groundnut',
    'paddy': 'rice', 'ಭತ್ತ': 'rice', 'ಬತ್ತ': 'rice', 'धान': 'rice', 'चावल': 'rice',
    'corn': 'maize', 'ಮೆಕ್ಕೆಜೋಳ': 'maize', 'ಮಕ್ಕಾ': 'maize', 'मक्का': 'maize',
    'wheat': 'wheat', 'ಗೋಧಿ': 'wheat', 'गेहूं': 'wheat',
    'sunflower': 'sunflower', 'ಸೂರ್ಯಕಾಂತಿ': 'sunflower', 'सूरजमुखी': 'sunflower',
    'cotton': 'cotton', 'ಹತ್ತಿ': 'cotton', 'कपास': 'cotton',
    'chickpea': 'chickpea', 'gram': 'chickpea', 'bengal gram': 'chickpea', 'ಕಡಲೆ': 'chickpea', 'चना': 'chickpea',
    'tomato': 'tomato', 'ಟೊಮೆಟೊ': 'tomato', 'ಟೊಮೇಟೊ': 'tomato', 'टमाटर': 'tomato',
    'potato': 'potato', 'ಆಲೂಗಡ್ಡೆ': 'potato', 'आलू': 'potato',
    'onion': 'onion', 'ಈರುಳ್ಳಿ': 'onion', 'प्याज': 'onion',
    'chilli': 'chilli', 'chili': 'chilli', 'ಮೆಣಸಿನಕಾಯಿ': 'chilli', 'मिर्च': 'chilli'
  };
  return map[c] || c;
}

function localizeExecutiveSummary(summary, l, crop) {
  if (!summary || l === 'en') return summary;
  const s = String(summary);
  if (l === 'hi') {
    if (s.includes('ಎಚ್ಚರಿಕೆಯಿಂದ ಮುಂದುವರಿಯಿರಿ') || s.includes('Proceed with CAUTION') || s.includes('Proceed with caution') || s.includes('ಎಚ್ಚರಿಕೆಗಳನ್ನು ಗಮನಿಸಿ')) {
      const c = crop ? getCropDropdownLabel(crop, 'hi') : 'फसल';
      return `🌾 सावधानी से आगे बढ़ें। ${c} बोने से पहले चेतावनियों पर ध्यान दें।`;
    }
    if (s.includes('ನಿಲ್ಲಿ — ತುರ್ತು ಸಮಸ್ಯೆಗಳು') || s.includes('Critical issues detected') || s.includes('ನಿಲ್ಲಿ')) {
      return '🚨 रुकें — गंभीर समस्याएं पाई गईं! खेती से पहले सभी महत्वपूर्ण चेतावनियों का समाधान करें।';
    }
    if (s.includes('ಹೆಚ್ಚಿನ ಅಪಾಯ') || s.includes('HIGH RISK')) {
      const c = crop ? getCropDropdownLabel(crop, 'hi') : 'फसल';
      return `⚠ उच्च जोखिम — बीमारी भी है और बाजार भाव भी कम है। ${c} के स्थान पर अन्य फसल पर विचार करें।`;
    }
    if (s.includes('ಅತ್ಯುತ್ತಮ ಪರಿಸ್ಥಿತಿಗಳು') || s.includes('EXCELLENT CONDITIONS')) {
      const c = crop ? getCropDropdownLabel(crop, 'hi') : 'फसल';
      return `🌾 उत्तम परिस्थितियां — अभी ${c} उगाएं! बेहतरीन बाजार भाव और अनुकूल मौसम।`;
    }
    if (s.includes('ಎಲ್ಲಾ ಪರಿಸ್ಥಿತಿಗಳು ಅನುಕೂಲಕರವಾಗಿವೆ') || s.includes('FAVORABLE')) {
      const c = crop ? getCropDropdownLabel(crop, 'hi') : 'फसल';
      return `🌾 सभी स्थितियां अनुकूल हैं — ${c} की खेती के साथ आगे बढ़ें।`;
    }
  } else if (l === 'kn') {
    if (s.includes('सावधानी से आगे बढ़ें') || s.includes('Proceed with CAUTION') || s.includes('Proceed with caution') || s.includes('चेतावनियों पर ध्यान दें')) {
      const c = crop ? getCropDropdownLabel(crop, 'kn') : 'ಬೆಳೆ';
      return `🌾 ಎಚ್ಚರಿಕೆಯಿಂದ ಮುಂದುವರಿಯಿರಿ. ${c} ಬಿತ್ತನೆ ಮಾಡುವ ಮುನ್ನ ಎಚ್ಚರಿಕೆಗಳನ್ನು ಗಮನಿಸಿ.`;
    }
    if (s.includes('रुकें — गंभीर समस्याएं') || s.includes('Critical issues detected') || s.includes('रुकें')) {
      return '🚨 ನಿಲ್ಲಿ — ತುರ್ತು ಸಮಸ್ಯೆಗಳು ಕಂಡುಬಂದಿವೆ! ಕೃಷಿ ಕಾರ್ಯದ ಮೊದಲು ಎಲ್ಲಾ ತುರ್ತು ಎಚ್ಚರಿಕೆಗಳನ್ನು ಪರಿಹರಿಸಿ.';
    }
    if (s.includes('उच्च जोखिम') || s.includes('HIGH RISK')) {
      const c = crop ? getCropDropdownLabel(crop, 'kn') : 'ಬೆಳೆ';
      return `⚠ ಹೆಚ್ಚಿನ ಅಪಾಯ — ರೋಗವಿದೆ ಮತ್ತು ಮಾರುಕಟ್ಟೆ ಬೆಲೆಯೂ ಕಡಿಮೆಯಿದೆ. ${c} ಬದಲಿಗೆ ಪರ್ಯಾಯ ಬೆಳೆ ಪರಿಗಣಿಸಿ.`;
    }
    if (s.includes('उत्तम परिस्थितियां') || s.includes('EXCELLENT CONDITIONS')) {
      const c = crop ? getCropDropdownLabel(crop, 'kn') : 'ಬೆಳೆ';
      return `🌾 ಅತ್ಯುತ್ತಮ ಪರಿಸ್ಥಿತಿಗಳು — ಈಗಲೇ ${c} ಬೆಳೆಯಿರಿ! ಉತ್ತಮ ಮಾರುಕಟ್ಟೆ ದರ ಮತ್ತು ಹವಾಮಾನವಿದೆ.`;
    }
    if (s.includes('सभी स्थितियां अनुकूल') || s.includes('FAVORABLE')) {
      const c = crop ? getCropDropdownLabel(crop, 'kn') : 'ಬೆಳೆ';
      return `🌾 ಎಲ್ಲಾ ಪರಿಸ್ಥಿತಿಗಳು ಅನುಕೂಲಕರವಾಗಿವೆ — ${c} ಬೆಳೆಯಲು ಮುಂದುವರಿಯಿರಿ.`;
    }
  }
  return s;
}

export default function PlannerAgentSection({ moduleState = {} }) {
  const { t, lang } = useLanguage();
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [speaking, setSpeaking] = useState(false);

  const { recommendedCrop, city, predictedDisease, priceCrop, predictedPrice } = moduleState;
  const hasAnyInput = Boolean(recommendedCrop || predictedDisease || predictedPrice);

  function localizePlannerPriceText(text, l) {
    if (!text || l === 'en') return text;
    let s = String(text);
    if (l === 'kn') {
      return s
        .replace(/Live price is unavailable/gi, 'ಲೈವ್ ದರ ಲಭ್ಯವಿಲ್ಲ')
        .replace(/लाइव भाव उपलब्ध नहीं है/gi, 'ಲೈವ್ ದರ ಲಭ್ಯವಿಲ್ಲ')
        .replace(/Estimated Price Trend: Insufficient data/gi, 'ಅಂದಾಜು ಬೆಲೆ ಪ್ರವೃತ್ತಿ: ಸಾಕಷ್ಟು ಐತಿಹಾಸಿಕ ದತ್ತಾಂಶ ಲಭ್ಯವಿಲ್ಲ')
        .replace(/Estimated Price Trend/gi, 'ಅಂದಾಜು ಬೆಲೆ ಪ್ರವೃತ್ತಿ')
        .replace(/Reference price \(not live\)/gi, 'ಉಲ್ಲೇಖ ಮಂಡಿ ದರ (ಲೈವ್ ಅಲ್ಲ)')
        .replace(/संदर्भ मंडी भाव \(लाइव नहीं\)/gi, 'ಉಲ್ಲೇಖ ಮಂಡಿ ದರ (ಲೈವ್ ಅಲ್ಲ)')
        .replace(/Live Mandi Spot Price/gi, 'ನೇರ ಮಂಡಿ ದರ')
        .replace(/लाइव मंडी भाव/gi, 'ನೇರ ಮಂಡಿ ದರ')
        .replace(/Quintal/gi, 'ಕ್ವಿಂಟಾಲ್')
        .replace(/क्विंटल/gi, 'ಕ್ವಿಂಟಾಲ್')
        .replace(/Mandi:/gi, 'ಮಾರುಕಟ್ಟೆ:')
        .replace(/मंडी:/gi, 'ಮಾರುಕಟ್ಟೆ:')
        .replace(/Range:/gi, 'ವ್ಯಾಪ್ತಿ:')
        .replace(/दायरा:/gi, 'ವ್ಯಾಪ್ತಿ:')
        .replace(/स्रोत:/gi, 'ಮೂಲ:')
        .replace(/Date: Benchmark Dataset/gi, 'ದಿನಾಂಕ: ಐತಿಹಾಸಿಕ ಮಾನದಂಡ ಮಾಹಿತಿ')
        .replace(/दिनांक: ऐतिहासिक संदर्भ डेटा/gi, 'ದಿನಾಂಕ: ಐತಿಹಾಸಿಕ ಮಾನದಂಡ ಮಾಹಿತಿ')
        .replace(/Source: APMC Dharwad \/ KSAMB Mandi Feed/gi, 'ಮೂಲ: APMC ಧಾರವಾಡ / KSAMB ಮಂಡಿ ಮಾಹಿತಿ')
        .replace(/Benchmark Reference Notice: Sourced from verified Karnataka APMC benchmark records \(not today's live feed\)\. Verify today's spot auction rates at your local APMC\./gi, 'ಉಲ್ಲೇಖ ದರ ಮಾಹಿತಿ: ಇದು ಕರ್ನಾಟಕ ಎಪಿಎಂಸಿ ಐತಿಹಾಸಿಕ ಮಾನದಂಡ ದರವಾಗಿದೆ. ಸ್ಥಳೀಯ ಎಪಿಎಂಸಿಯಲ್ಲಿ ಇಂದಿನ ದರ ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ.')
        .replace(/संदर्भ भाव सूचना: यह कर्नाटक एपीएमसी ऐतिहासिक संदर्भ दर है.*?सत्यापित करें।/gi, 'ಉಲ್ಲೇಖ ದರ ಮಾಹಿತಿ: ಇದು ಕರ್ನಾಟಕ ಎಪಿಎಂಸಿ ಐತಿಹಾಸಿಕ ಮಾನದಂಡ ದರವಾಗಿದೆ. ಸ್ಥಳೀಯ ಎಪಿಎಂಸಿಯಲ್ಲಿ ಇಂದಿನ ದರ ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ.')
        .replace(/Govt Minimum Support Price/gi, 'ಸರ್ಕಾರಿ ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ')
        .replace(/सरकारी न्यूनतम समर्थन मूल्य/gi, 'ಸರ್ಕಾರಿ ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ')
        .replace(/स्थिर संदर्भ सूचना, अंतिम सत्यापन/gi, 'ಸ್ಥಿರ ಉಲ್ಲೇಖ ಮಾಹಿತಿ, ಕೊನೆಯ ಪರಿಶೀಲನೆ')
        .replace(/मंडी भाव बनाम न्यूनतम समर्थन मूल्य: वर्तमान मंडी भाव/gi, 'ಮಂಡಿ ದರ vs ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ: ಪ್ರಸ್ತುತ ಮಂಡಿ ದರ')
        .replace(/सरकारी समर्थन मूल्य से/gi, 'ಸರ್ಕಾರಿ ಬೆಂಬಲ ಬೆಲೆಗಿಂತ')
        .replace(/कम है/gi, 'ಕಡಿಮೆಯಾಗಿದೆ')
        .replace(/अधिक है/gi, 'ಹೆಚ್ಚಾಗಿದೆ')
        .replace(/अनुमानित 4 महीने का मूल्य रुझान/gi, 'ಅಂದಾಜು 4 ತಿಂಗಳ ಬೆಲೆ ಪ್ರವೃತ್ತಿ')
        .replace(/औसत/gi, 'ಸರಾಸರಿ')
        .replace(/Mandi Spot vs MSP Comparison: Current mandi spot price \((.*?)\) is ABOVE Govt MSP \((.*?)\)\./gi, 'ಮಂಡಿ ದರ vs ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ: ಪ್ರಸ್ತುತ ಮಂಡಿ ದರ ($1) ಸರ್ಕಾರಿ ಬೆಂಬಲ ಬೆಲೆಗಿಂತ ($2) ಹೆಚ್ಚಾಗಿದೆ.')
        .replace(/Estimated 4-Month Price Trend \(Estimated trend, not a guarantee — historical seasonal projection\):/gi, 'ಅಂದಾಜು 4 ತಿಂಗಳ ಬೆಲೆ ಪ್ರವೃತ್ತಿ (ಐತಿಹಾಸಿಕ ಋತುವಿನ ಪ್ರಕ್ಷೇಪಣ):')
        .replace(/Varieties:/gi, 'ತಳಿಗಳು:')
        .replace(/किस्में:/gi, 'ತಳಿಗಳು:')
        .replace(/wholesale/gi, 'ಸಗಟು ದರ');
    } else if (l === 'hi') {
      return s
        .replace(/wholesale/gi, 'थोक भाव')
        .replace(/Live price is unavailable/gi, 'लाइव भाव उपलब्ध नहीं है')
        .replace(/ಲೈವ್ ದರ ಲಭ್ಯವಿಲ್ಲ/gi, 'लाइव भाव उपलब्ध नहीं है')
        .replace(/Estimated Price Trend: Insufficient data/gi, 'अनुमानित मूल्य रुझान: अपर्याप्त ऐतिहासिक डेटा')
        .replace(/Estimated Price Trend/gi, 'अनुमानित मूल्य रुझान')
        .replace(/Reference price \(not live\)/gi, 'संदर्भ मंडी भाव (लाइव नहीं)')
        .replace(/ಉಲ್ಲೇಖ ಮಂಡಿ ದರ \(ಲೈವ್ ಅಲ್ಲ\)/gi, 'संदर्भ मंडी भाव (लाइव नहीं)')
        .replace(/Live Mandi Spot Price/gi, 'लाइव मंडी भाव')
        .replace(/ನೇರ ಮಂಡಿ ದರ/gi, 'लाइव मंडी भाव')
        .replace(/Quintal/gi, 'क्विंटल')
        .replace(/ಕ್ವಿಂಟಾಲ್/gi, 'क्विंटल')
        .replace(/Mandi:/gi, 'मंडी:')
        .replace(/ಮಂಡಿ:/gi, 'मंडी:')
        .replace(/ಮಾರುಕಟ್ಟೆ:/gi, 'मंडी:')
        .replace(/Range:/gi, 'दायरा:')
        .replace(/ವ್ಯಾಪ್ತಿ:/gi, 'दायरा:')
        .replace(/ಮೂಲ:/gi, 'स्रोत:')
        .replace(/Date: Benchmark Dataset/gi, 'दिनांक: ऐतिहासिक संदर्भ डेटा')
        .replace(/ದಿನಾಂಕ: ಐತಿಹಾಸಿಕ ಮಾನದಂಡ ಮಾಹಿತಿ/gi, 'दिनांक: ऐतिहासिक संदर्भ डेटा')
        .replace(/Source: APMC Dharwad \/ KSAMB Mandi Feed/gi, 'स्रोत: APMC धारवाड़ / KSAMB मंडी फीड')
        .replace(/ಉಲ್ಲೇಖ ದರ ಮಾಹಿತಿ: ಇದು ಕರ್ನಾಟಕ ಎಪಿಎಂಸಿ ಐತಿಹಾಸಿಕ ಮಾನದಂಡ ದರವಾಗಿದೆ.*?ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ\./gi, 'संदर्भ भाव सूचना: यह कर्नाटक एपीएमसी ऐतिहासिक संदर्भ दर है (आज का लाइव नीलामी दर नहीं)। अपनी स्थानीय मंडी में आज का दर सत्यापित करें।')
        .replace(/Benchmark Reference Notice: Sourced from verified Karnataka APMC benchmark records \(not today's live feed\)\. Verify today's spot auction rates at your local APMC\./gi, 'संदर्भ भाव सूचना: यह कर्नाटक एपीएमसी ऐतिहासिक संदर्भ दर है। अपनी स्थानीय मंडी में आज का दर सत्यापित करें।')
        .replace(/Govt Minimum Support Price/gi, 'सरकारी न्यूनतम समर्थन मूल्य')
        .replace(/ಸರ್ಕಾರಿ ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ/gi, 'सरकारी न्यूनतम समर्थन मूल्य')
        .replace(/ಸ್ಥಿರ ಉಲ್ಲೇಖ ಮಾಹಿತಿ, ಕೊನೆಯ ಪರಿಶೀಲನೆ/gi, 'स्थिर संदर्भ सूचना, अंतिम सत्यापन')
        .replace(/ಮಂಡಿ ದರ vs ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ: ಪ್ರಸ್ತುತ ಮಂಡಿ ದರ/gi, 'मंडी भाव बनाम न्यूनतम समर्थन मूल्य: वर्तमान मंडी भाव')
        .replace(/ಸರ್ಕಾರಿ ಬೆಂಬಲ ಬೆಲೆಗಿಂತ/gi, 'सरकारी समर्थन मूल्य से')
        .replace(/ಕಡಿಮೆಯಾಗಿದೆ/gi, 'कम है')
        .replace(/ಹೆಚ್ಚಾಗಿದೆ/gi, 'अधिक है')
        .replace(/ರೈತರು ಎಪಿಎಂಸಿ ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ \(MSP\) ಖರೀದಿ ಕೇಂದ್ರಗಳಲ್ಲಿ ಮಾರಾಟ ಮಾಡಲು ಸಲಹೆ ನೀಡಲಾಗಿದೆ\./gi, 'किसानों को एपीएमसी न्यूनतम समर्थन मूल्य (MSP) खरीद केंद्रों पर बेचने की सलाह दी जाती है।')
        .replace(/ಅಂದಾಜು 4 ತಿಂಗಳ ಬೆಲೆ ಪ್ರವೃತ್ತಿ \(ಅಂದಾಜು ಪ್ರವೃತ್ತಿ, ಗ್ಯಾರಂಟಿ ಅಲ್ಲ — ಐತಿಹಾಸಿಕ ಋತುವಿನ ಪ್ರಕ್ಷೇಪಣೆ\):/gi, 'अनुमानित 4 महीने का मूल्य रुझान (अनुमानित रुझान, गारंटी नहीं — ऐतिहासिक मौसमी अनुमान):')
        .replace(/ಅಂದಾಜು 4 ತಿಂಗಳ ಬೆಲೆ ಪ್ರವೃತ್ತಿ/gi, 'अनुमानित 4 महीने का मूल्य रुझान')
        .replace(/ಸರಾಸರಿ/gi, 'औसत')
        .replace(/ಬೆಲೆ ಪ್ರವೃತ್ತಿ ಎಚ್ಚರಿಕೆ: ಮುನ್ಸೂಚನೆಯ ದರವು ಸರ್ಕಾರಿ ಬೆಂಬಲ ಬೆಲೆಗಿಂತ/gi, 'मूल्य रुझान चेतावनी: पूर्वानुमानित दर सरकारी समर्थन मूल्य से')
        .replace(/ಕಡಿಮೆಯಾಗುವ ಸಾಧ್ಯತೆಯಿದೆ/gi, 'कम होने की संभावना है')
        .replace(/ರೈತರು ಎಪಿಎಂಸಿ ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ \(MSP\) ಖರೀದಿ ಕೇಂದ್ರಗಳಲ್ಲಿ ನೋಂದಾಯಿಸಿ ಮಾರಾಟ ಮಾಡಲು ಸಲಹೆ ನೀಡಲಾಗಿದೆ\./gi, 'किसानों को एपीएमसी न्यूनतम समर्थन मूल्य (MSP) खरीद केंद्रों में पंजीकरण कराकर बेचने की सलाह दी जाती है।')
        .replace(/ಮಾರಾಟಕ್ಕೆ ಸೂಕ್ತ ತಿಂಗಳುಗಳು:/gi, 'बेचने के सर्वोत्तम महीने:')
        .replace(/ಅಗ್ಮಾರ್ಕ್‌ನೆಟ್ ಮಂಡಿ ದರ ವಿಶ್ಲೇಷಣೆ:/gi, 'एगमार्कनेट मंडी भाव विश्लेषण:')
        .replace(/ಕ್ಕಿಂತ ಕಡಿಮೆ ತೇವಾಂಶವಿರುವಂತೆ ಒಣಗಿಸಿದ/gi, 'से कम नमी वाली सुखाई गई')
        .replace(/ಕಡಲೆಕಾಯಿಗೆ ಗರಿಷ್ಠ ದರ ಸಿಗುತ್ತದೆ; ಸರ್ಕಾರಿ ಬೆಂಬಲ ಬೆಲೆ \(MSP\) ಪರಿಶೀಲಿಸಿ\./gi, 'मूंगफली के लिए अधिकतम मूल्य मिलता है; सरकारी समर्थन मूल्य (MSP) की जांच करें।')
        .replace(/ನವೆಂ/gi, 'नवंबर')
        .replace(/ಡಿಸೆಂ/gi, 'दिसंबर')
        .replace(/ಜನ:/gi, 'जनवरी:')
        .replace(/ಫೆಬ್ರು:/gi, 'फरवरी:')
        .replace(/Mandi Spot vs MSP Comparison: Current mandi spot price \((.*?)\) is ABOVE Govt MSP \((.*?)\)\./gi, 'मंडी भाव बनाम एमएसपी तुलना: वर्तमान मंडी भाव ($1) सरकारी एमएसपी ($2) से अधिक है।')
        .replace(/Estimated 4-Month Price Trend \(Estimated trend, not a guarantee — historical seasonal projection\):/gi, 'अनुमानित 4 महीने का मूल्य रुझान (ऐतिहासिक मौसमी अनुमान):')
        .replace(/Varieties:/gi, 'किस्में:')
        .replace(/ತಳಿಗಳು:/gi, 'किस्में:');
    }
    return s;
  }

  function localizePlannerIrrigationText(text, l) {
    if (!text || l === 'en') return text;
    let s = String(text);
    if (l === 'kn') {
      return s
        .replace(/Stage-Based Irrigation/gi, 'ಹಂತ-ಆಧಾರಿತ ನೀರಾವರಿ')
        .replace(/चरण-आधारित.*?सिंचाई/gi, 'ಹಂತ-ಆಧಾರಿತ ನಿಖರ ನೀರಾವರಿ')
        .replace(/Vegetative \/ Tillering Stage/gi, 'ಸಸ್ಯಕ / ಕವಲೊಡೆಯುವ ಹಂತ')
        .replace(/Irrigate (\d+) hr (\d+) min/gi, 'ನೀರಾವರಿ ಸಮಯ: $1 ಗಂಟೆ $2 ನಿಮಿಷ')
        .replace(/Loamy Soil: Moderate intervals \(every 4-5 days \/ at critical physiological stage\)/gi, 'ಮರಳುಮಿಶ್ರಿತ ಗೋಡು ಮಣ್ಣು: ಮಧ್ಯಮ ಅಂತರ (ಪ್ರತಿ 4-5 ದಿನಕ್ಕೊಮ್ಮೆ / ನಿರ್ಣಾಯಕ ಹಂತದಲ್ಲಿ)')
        .replace(/दोमट मिट्टी/gi, 'ಗೋಡು ಮಣ್ಣು')
        .replace(/प्रति बार/gi, 'ಪ್ರತಿ ಬಾರಿಗೆ')
        .replace(/लीटर पानी/gi, 'ಲೀಟರ್ ನೀರು')
        .replace(/दैनिक आवश्यकता:/gi, 'ದೈನಂದಿನ ಅಗತ್ಯ:')
        .replace(/ड्रिप सिंचाई/gi, 'ಹನಿ ನೀರಾವರಿ')
        .replace(/पंप प्रवाह/gi, 'ಪಂಪ್ ಹರಿವು')
        .replace(/delivering ([\d,]+) Litres per event/gi, 'ಪ್ರತಿ ಬಾರಿಗೆ $1 ಲೀಟರ್ ನೀರು')
        .replace(/Net requirement: ([\d.]+) mm\/day after ([\d.]+)mm effective rainfall/gi, 'ನಿವ್ವಳ ಅಗತ್ಯ: $2ಮಿ.ಮೀ ಮಳೆಯ ನಂತರ ದಿನಕ್ಕೆ $1 ಮಿ.ಮೀ')
        .replace(/Daily water: ([\d,]+) L\/day for ([\d.]+) acre\(s\)/gi, 'ದೈನಂದಿನ ನೀರು: $2 ಎಕರೆಗೆ ದಿನಕ್ಕೆ $1 ಲೀಟರ್')
        .replace(/efficiency/gi, 'ದಕ್ಷತೆ')
        .replace(/pump flow/gi, 'ಪಂಪ್ ಸಾಮರ್ಥ್ಯ')
        .replace(/UAS Raichur \/ ICAR-KVK Bidar Advisory: Tillering stage irrigation promotes active tillers\./gi, 'UAS ರಾಯಚೂರು / ICAR-KVK ಬೀದರ್ ಸಲಹೆ: ಕವಲೊಡೆಯುವ ಹಂತದಲ್ಲಿ ನೀರಾವರಿ ಮಾಡುವುದರಿಂದ ಆರೋಗ್ಯಕರ ಕವಲುಗಳು ಹೆಚ್ಚುತ್ತವೆ.');
    } else if (l === 'hi') {
      return s
        .replace(/Stage-Based Irrigation/gi, 'चरण-आधारित सिंचाई')
        .replace(/ಹಂತ-ಆಧಾರಿತ ನಿಖರ ನೀರಾವರಿ:/gi, 'चरण-आधारित सटीक सिंचाई:')
        .replace(/ಹಂತ-ಆಧಾರಿತ ನೀರಾವರಿ/gi, 'चरण-आधारित सिंचाई')
        .replace(/Vegetative \/ Tillering Stage/gi, 'वानस्पतिक / कल्ले फूटने की अवस्था')
        .replace(/Irrigate (\d+) hr (\d+) min/gi, 'सिंचाई अवधि: $1 घंटे $2 मिनट')
        .replace(/ಪ್ರತಿ ನೀರಾವರಿ ಅವಧಿ: (\d+) ಗಂಟೆಗಳು/gi, 'प्रत्येक सिंचाई अवधि: $1 घंटे')
        .replace(/ಗೋಡು ಮಣ್ಣು:/gi, 'दोमट मिट्टी:')
        .replace(/ಪ್ರತಿ 4-5 ದಿನಕ್ಕೊಮ್ಮೆ \/ ಬೆಳೆಯ ಪ್ರಮುಖ ಹಂತದಲ್ಲಿ/gi, 'प्रत्येक 4-5 दिन में / फसल की मुख्य अवस्था में')
        .replace(/Loamy Soil: Moderate intervals \(every 4-5 days \/ at critical physiological stage\)/gi, 'दोमट मिट्टी: मध्यम अंतराल (प्रत्येक 4-5 दिन में / क्रांतिक अवस्था पर)')
        .replace(/ಪ್ರತಿ ಬಾರಿಗೆ/gi, 'प्रति बार')
        .replace(/ಲೀಟರ್ ನೀರು\./gi, 'लीटर पानी।')
        .replace(/ಲೀಟರ್ ನೀರು/gi, 'लीटर पानी')
        .replace(/ದಿನಕ್ಕೆ/gi, 'दिन')
        .replace(/ದೈನಂದಿನ ಅಗತ್ಯ:/gi, 'दैनिक आवश्यकता:')
        .replace(/ಎಕರೆಗೆ/gi, 'एकड़ के लिए')
        .replace(/ಹನಿ ನೀರಾವರಿ/gi, 'ड्रिप सिंचाई')
        .replace(/ನೀರಿನ ದಕ್ಷತೆ/gi, 'जल दक्षता')
        .replace(/ಮೂಲಕ/gi, 'के माध्यम से')
        .replace(/ಪಂಪ್ ಹರಿವು/gi, 'पंप प्रवाह')
        .replace(/ಲೀ\/ಗಂಟೆ/gi, 'ली/घंटा')
        .replace(/delivering ([\d,]+) Litres per event/gi, 'प्रति बार $1 लीटर पानी की आपूर्ति')
        .replace(/Net requirement: ([\d.]+) mm\/day after ([\d.]+)mm effective rainfall/gi, 'शुद्ध आवश्यकता: $2मिमी बारिश के बाद $1 मिमी/दिन')
        .replace(/Daily water: ([\d,]+) L\/day for ([\d.]+) acre\(s\)/gi, 'दैनिक पानी: $2 एकड़ के लिए $1 लीटर/दिन')
        .replace(/efficiency/gi, 'दक्षता')
        .replace(/pump flow/gi, 'पंप प्रवाह')
        .replace(/UAS Raichur \/ ICAR-KVK Bidar Advisory: Tillering stage irrigation promotes active tillers\./gi, 'UAS रायचूर / ICAR-KVK बीदर परामर्श: कल्ले फूटने की अवस्था में सिंचाई से स्वस्थ कल्ले बढ़ते हैं।');
    }
    return s;
  }

  function localizePlannerAdviceItem(item, l, crop, dist) {
    if (!item) return '';
    let s = String(item).trim();
    if (l === 'en') return s;
    const cName = crop ? getCropDropdownLabel(crop, l) : (l === 'kn' ? 'ಬೆಳೆ' : 'फसल');
    const dName = dist ? getDistrictDropdownLabel(dist, l) : (l === 'kn' ? 'ಜಿಲ್ಲೆ' : 'जिला');

    // 1. Crop Health
    if (s.includes('Crop Health') || s.includes('ಬೆಳೆ ಆರೋಗ್ಯ') || s.includes('ಫಸಲ್ ಸ್ವಾಸ್ಥ್ಯ') || s.includes('फसल स्वास्थ्य')) {
      if (l === 'hi') {
        return `🌿 फसल स्वास्थ्य: ${cName} के लिए कोई सक्रिय रोग नहीं (निवारक IPM सक्रिय)।`;
      } else if (l === 'kn') {
        return `🌿 ಬೆಳೆ ಆರೋಗ್ಯ: ${cName} ಬೆಳೆಗೆ ಯಾವುದೇ ರೋಗ ದಾಖಲಾಗಿಲ್ಲ (ಮುನ್ನೆಚ್ಚರಿಕೆ IPM ಸಕ್ರಿಯ).`;
      }
    }

    // 2. Weather
    if (s.includes('Weather') || s.includes('ಹವಾಮಾನ') || s.includes('मौसम') || s.includes('°C')) {
      if (l === 'hi') {
        return s
          .replace(/ನೇರ ಹವಾಮಾನ:/gi, 'लाइव मौसम:')
          .replace(/Live Weather:/gi, 'लाइव मौसम:')
          .replace(/ತೇವಾಂಶ/gi, 'आर्द्रता')
          .replace(/humidity/gi, 'आर्द्रता')
          .replace(/ಸ್ವಚ್ಛ ಆಕಾಶ/gi, 'साफ आसमान')
          .replace(/clear sky/gi, 'साफ आसमान')
          .replace(/ಕೃಷಿಗೆ ಸೂಕ್ತವಾಗಿದೆ\./gi, 'कृषि के लिए उपयुक्त है।')
          .replace(/Suitable for farming\./gi, 'कृषि के लिए उपयुक्त है।');
      } else if (l === 'kn') {
        return s
          .replace(/लाइव मौसम:/gi, 'ನೇರ ಹವಾಮಾನ:')
          .replace(/Live Weather:/gi, 'ನೇರ ಹವಾಮಾನ:')
          .replace(/आर्द्रता/gi, 'ತೇವಾಂಶ')
          .replace(/humidity/gi, 'ತೇವಾಂಶ')
          .replace(/साफ आसमान/gi, 'ಸ್ವಚ್ಛ ಆಕಾಶ')
          .replace(/clear sky/gi, 'ಸ್ವಚ್ಛ ಆಕಾಶ')
          .replace(/कृषि के लिए अनुकूल है\./gi, 'ಕೃಷಿಗೆ ಸೂಕ್ತವಾಗಿದೆ.')
          .replace(/Suitable for farming\./gi, 'ಕೃಷಿಗೆ ಸೂಕ್ತವಾಗಿದೆ.');
      }
    }

    // 3. Recommended Crop
    if (s.includes('Recommended crop') || s.includes('ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆ') || s.includes('अनुशंसित फसल')) {
      if (l === 'hi') {
        return `✅ आपकी मिट्टी और जलवायु के लिए अनुशंसित फसल: ${cName}`;
      } else if (l === 'kn') {
        return `✅ ನಿಮ್ಮ ಮಣ್ಣು ಮತ್ತು ಹವಾಮಾನಕ್ಕೆ ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆ: ${cName}`;
      }
    }

    // 4. Mandi Price
    if (s.includes('Mandi') || s.includes('ಮಂಡಿ') || s.includes('मंडी') || s.includes('MSP') || s.includes('ಬೆಂಬಲ ಬೆಲೆ')) {
      return localizePlannerPriceText(s, l);
    }

    // 5. Smart Irrigation
    if (s.includes('Irrigation') || s.includes('ನೀರಾವರಿ') || s.includes('सिंचाई') || s.includes('ETc') || s.includes('ಲೀಟರ್') || s.includes('लीटर')) {
      return localizePlannerIrrigationText(s, l);
    }

    return s;
  }

  const rawPrice = moduleState.priceData
    ? (lang === 'kn' ? (moduleState.priceData.result_kn || moduleState.priceData.result) : lang === 'hi' ? (moduleState.priceData.result_hi || moduleState.priceData.result) : (moduleState.priceData.result_en || moduleState.priceData.result || moduleState.priceData.forecast_text))
    : (priceCrop && predictedPrice ? `${getCropDropdownLabel(priceCrop, lang)} : ${predictedPrice}` : predictedPrice || t('notAvailable'));
  const displayPrice = localizePlannerPriceText(rawPrice, lang);

  const rawIrrigation = moduleState.irrigationData
    ? (lang === 'kn' ? (moduleState.irrigationData.advice_kn || moduleState.irrigationData.advice_en) : lang === 'hi' ? (moduleState.irrigationData.advice_hi || moduleState.irrigationData.advice_en) : moduleState.irrigationData.advice_en)
    : (moduleState.irrigationAdvice || t('notAvailable'));
  const displayIrrigation = localizePlannerIrrigationText(rawIrrigation, lang);

  async function handleGeneratePlan() {
    setLoading(true);
    setPlan(null);
    if (speaking && window._planAudio) {
      window._planAudio.pause();
      window._planAudio = null;
      setSpeaking(false);
    }

    try {
      // 1. Fetch structured farm plan + AI plan from backend
      const res = await api.planner({
        lang,
        crop: recommendedCrop || 'Groundnut',
        district: city || 'Kalaburagi'
      });
      const planObj = typeof res === 'string' ? { summary: res } : res;

      // 2. If AI plan was not embedded or is empty, fetch planner_ai directly
      if (!planObj.ai_plan) {
        try {
          const aiRes = await api.plannerAi({
            crop: recommendedCrop || 'Rice',
            disease: predictedDisease || '',
            price: predictedPrice || '',
            district: city || 'Dharwad',
            soil_type: moduleState.irrigationData?.soil_type || 'loam',
            lang: lang
          });
          if (aiRes?.ai_plan) {
            planObj.ai_plan = aiRes.ai_plan;
            planObj.ai_plan_en = aiRes.ai_plan_en || aiRes.ai_plan;
            planObj.ai_plan_kn = aiRes.ai_plan_kn || aiRes.ai_plan;
            planObj.ai_plan_hi = aiRes.ai_plan_hi || aiRes.ai_plan;
            planObj.provider = aiRes.provider || planObj.provider;
            planObj.sources = aiRes.sources || planObj.sources;
          }
        } catch (aiErr) {
          console.warn('AI planner sub-call notice:', aiErr);
        }
      }

      setPlan(planObj);
    } catch (err) {
      console.error('Plan generation error:', err);
      // Try direct fallback AI plan call if /planner failed
      try {
        const aiRes = await api.plannerAi({
          crop: recommendedCrop || 'Rice',
          disease: predictedDisease || '',
          price: predictedPrice || '',
          district: city || 'Dharwad',
          soil_type: moduleState.irrigationData?.soil_type || 'loam',
          lang: lang
        });
        if (aiRes && aiRes.ai_plan) {
          setPlan(aiRes);
          return;
        }
      } catch (_) { }

      setPlan({
        summary: lang === 'kn'
          ? 'ಯೋಜನೆ ರಚಿಸಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೊಮ್ಮೆ ಪ್ರಯತ್ನಿಸಿ.'
          : lang === 'hi'
            ? 'योजना नहीं बनाई जा सकी। कृपया पुनः प्रयास करें।'
            : 'Could not generate farm plan right now. Please try again.'
      });
    } finally {
      setLoading(false);
    }
  }

  // Auto-refresh plan in new language when user switches language
  const prevLangRef = useRef(lang);
  useEffect(() => {
    if (plan && prevLangRef.current !== lang) {
      prevLangRef.current = lang;
      handleGeneratePlan();
    } else {
      prevLangRef.current = lang;
    }
  }, [lang]);

  const rawSummary = plan
    ? (lang === 'kn' ? (plan.summary_kn || plan.summary) : lang === 'hi' ? (plan.summary_hi || plan.summary) : (plan.summary_en || plan.summary))
    : '';
  const activeSummary = localizeExecutiveSummary(rawSummary, lang, recommendedCrop);

  const canonCrop = getCanonicalCropKey(recommendedCrop);
  const cropMeta = CROP_AGRONOMY[canonCrop] || CROP_AGRONOMY['groundnut'] || {};

  // 1. Planting Schedule
  let activePlanting = plan
    ? (lang === 'kn' ? (plan.planting_schedule_kn || (isWrongScript(plan.planting_schedule, 'kn') ? '' : plan.planting_schedule))
      : lang === 'hi' ? (plan.planting_schedule_hi || (isWrongScript(plan.planting_schedule, 'hi') ? '' : plan.planting_schedule))
      : (plan.planting_schedule_en || (isWrongScript(plan.planting_schedule, 'en') ? '' : plan.planting_schedule)))
    : '';
  if (!activePlanting || isWrongScript(activePlanting, lang)) {
    const pMonths = cropMeta.planting_months?.[lang] || cropMeta.planting_months?.en;
    if (pMonths) {
      activePlanting = lang === 'kn'
        ? `🌱 ${getCropDropdownLabel(canonCrop, 'kn').toUpperCase()} ಬಿತ್ತನೆಗೆ ಉತ್ತಮ ಸಮಯ: ${pMonths}`
        : lang === 'hi'
          ? `🌱 ${getCropDropdownLabel(canonCrop, 'hi').toUpperCase()} की बुवाई का सर्वोत्तम समय: ${pMonths}`
          : `🌱 Best planting months for ${getCropDropdownLabel(canonCrop, 'en').toUpperCase()}: ${pMonths}`;
    }
  }

  // 2. Harvest Schedule
  let activeHarvest = plan
    ? (lang === 'kn' ? (plan.harvest_schedule_kn || (isWrongScript(plan.harvest_schedule, 'kn') ? '' : plan.harvest_schedule))
      : lang === 'hi' ? (plan.harvest_schedule_hi || (isWrongScript(plan.harvest_schedule, 'hi') ? '' : plan.harvest_schedule))
      : (plan.harvest_schedule_en || (isWrongScript(plan.harvest_schedule, 'en') ? '' : plan.harvest_schedule)))
    : '';
  if (!activeHarvest || isWrongScript(activeHarvest, lang)) {
    const hMonths = cropMeta.harvest_months?.[lang] || cropMeta.harvest_months?.en;
    if (hMonths) {
      activeHarvest = lang === 'kn'
        ? `🌾 ನಿರೀಕ್ಷಿತ ಕೊಯ್ಲು ತಿಂಗಳುಗಳು: ${hMonths}`
        : lang === 'hi'
          ? `🌾 कटाई के अनुमानित महीने: ${hMonths}`
          : `🌾 Expected harvest months: ${hMonths}`;
    }
  }

  // 3. Fertilizer Plan
  let activeFertilizer = plan
    ? (lang === 'kn' ? (plan.fertilizer_plan_kn || (isWrongScript(plan.fertilizer_plan, 'kn') ? '' : plan.fertilizer_plan))
      : lang === 'hi' ? (plan.fertilizer_plan_hi || (isWrongScript(plan.fertilizer_plan, 'hi') ? '' : plan.fertilizer_plan))
      : (plan.fertilizer_plan_en || (isWrongScript(plan.fertilizer_plan, 'en') ? '' : plan.fertilizer_plan)))
    : '';
  if (!activeFertilizer || isWrongScript(activeFertilizer, lang)) {
    const fPlan = cropMeta.fertilizer?.[lang] || cropMeta.fertilizer?.en;
    if (fPlan) {
      activeFertilizer = lang === 'kn'
        ? `🌿 ${getCropDropdownLabel(canonCrop, 'kn').toUpperCase()} ಗೊಬ್ಬರದ ಪ್ರಮಾಣ: ${fPlan}`
        : lang === 'hi'
          ? `🌿 ${getCropDropdownLabel(canonCrop, 'hi').toUpperCase()} उर्वरक योजना: ${fPlan}`
          : `🌿 Fertilizer plan for ${getCropDropdownLabel(canonCrop, 'en').toUpperCase()}: ${fPlan}`;
    }
  }

  // 4. Selling & Market Timing
  let activeSell = plan
    ? (lang === 'kn' ? (plan.sell_recommendation_kn || (isWrongScript(plan.sell_recommendation, 'kn') ? '' : plan.sell_recommendation))
      : lang === 'hi' ? (plan.sell_recommendation_hi || (isWrongScript(plan.sell_recommendation, 'hi') ? '' : plan.sell_recommendation))
      : (plan.sell_recommendation_en || (isWrongScript(plan.sell_recommendation, 'en') ? '' : plan.sell_recommendation)))
    : '';
  if (activeSell) {
    activeSell = localizePlannerPriceText(activeSell, lang);
  }
  if (!activeSell || isWrongScript(activeSell, lang)) {
    const sMonths = cropMeta.best_sell_months?.[lang] || cropMeta.best_sell_months?.en;
    const sTip = cropMeta.sell_tip?.[lang] || cropMeta.sell_tip?.en;
    if (sMonths && sTip) {
      activeSell = lang === 'kn'
        ? `💡 ಮಾರಾಟಕ್ಕೆ ಸೂಕ್ತ ತಿಂಗಳುಗಳು: ${sMonths}. ${sTip}`
        : lang === 'hi'
          ? `💡 बेचने के सर्वोत्तम महीने: ${sMonths}। ${sTip}`
          : `💡 Peak Selling Months: ${sMonths}. ${sTip}`;
    }
  }

  // 5. Pest Guide (IPM)
  let activePestGuide = plan
    ? (lang === 'kn' ? (plan.pest_guide_kn || (plan.pest_guide?.some(p => isWrongScript(p, 'kn')) ? null : plan.pest_guide))
      : lang === 'hi' ? (plan.pest_guide_hi || (plan.pest_guide?.some(p => isWrongScript(p, 'hi')) ? null : plan.pest_guide))
      : (plan.pest_guide_en || (plan.pest_guide?.some(p => isWrongScript(p, 'en')) ? null : plan.pest_guide)))
    : [];
  if (!activePestGuide || activePestGuide.length === 0 || activePestGuide.some(p => isWrongScript(p, lang))) {
    activePestGuide = cropMeta.pests?.[lang] || cropMeta.pests?.en || [];
  }

  let activeAdvice = plan
    ? (lang === 'kn' ? (plan.advice_kn || plan.advice) : lang === 'hi' ? (plan.advice_hi || plan.advice) : (plan.advice_en || plan.advice))
    : [];
  if (Array.isArray(activeAdvice)) {
    activeAdvice = activeAdvice
      .map(a => localizePlannerAdviceItem(a, lang, canonCrop, city))
      .filter(a => Boolean(a) && !isWrongScript(a, lang));
  }

  const activeAlerts = plan
    ? (lang === 'kn' ? (plan.alerts_kn || plan.alerts) : lang === 'hi' ? (plan.alerts_hi || plan.alerts) : (plan.alerts_en || plan.alerts))
    : [];

  const activePriority = plan
    ? (lang === 'kn' ? (plan.priority_kn || plan.priority) : lang === 'hi' ? (plan.priority_hi || plan.priority) : (plan.priority_en || plan.priority))
    : [];

  const displayDisease = (!predictedDisease || ['none', 'diseasenotdetected', 'cropmismatch', 'ಲಭ್ಯವಿಲ್ಲ', 'उपलब्ध नहीं', 'not available'].includes(String(predictedDisease).toLowerCase().trim()))
    ? t('notAvailable')
    : predictedDisease;

  const activeAiPlan = plan
    ? (lang === 'kn' ? (plan.ai_plan_kn || plan.ai_plan) : lang === 'hi' ? (plan.ai_plan_hi || plan.ai_plan) : (plan.ai_plan_en || plan.ai_plan))
    : '';

  function toggleSpeakPlan() {
    if (speaking) {
      api.stopSpeech();
      setSpeaking(false);
      return;
    }

    let textToRead = '';
    if (activeSummary && activeSummary.trim()) {
      textToRead = activeSummary;
      if (activePlanting) {
        textToRead += (lang === 'kn' ? ' ಬಿತ್ತನೆ ಸಮಯ: ' : lang === 'hi' ? ' बुवाई समय: ' : ' Sowing: ') + activePlanting;
      }
    } else if (activeAiPlan && activeAiPlan.trim()) {
      textToRead = activeAiPlan.replace(/[#*`_~|]/g, ' ').replace(/\s+/g, ' ').slice(0, 350);
    } else if (Array.isArray(activeAdvice) && activeAdvice.length > 0) {
      textToRead = activeAdvice.slice(0, 2).join('. ');
    }

    if (!textToRead) return;

    setSpeaking(true);
    api.playSpeech({
      text: textToRead,
      lang: lang,
      onStart: () => setSpeaking(true),
      onEnd: () => setSpeaking(false),
      onError: () => setSpeaking(false)
    });
  }

  const buttonText = loading
    ? (lang === 'kn' ? '🌾 ಸಮಗ್ರ ಯೋಜನೆ ರಚಿಸಲಾಗುತ್ತಿದೆ…' : lang === 'hi' ? '🌾 संपूर्ण कार्य योजना तैयार हो रही है…' : '🌾 Generating 360° Farm Plan…')
    : (lang === 'kn' ? '🌾 ಸಮಗ್ರ ಕೃಷಿ ಕ್ರಿಯಾ ಯೋಜನೆ ಪಡೆಯಿರಿ (360° Plan)' : lang === 'hi' ? '🌾 संपूर्ण 360° कृषि कार्य योजना प्राप्त करें' : '🌾 Get Complete 360° Farm Action Plan');

  return (
    <div className="section-box" id="planner">
      <div className="section-header">
        <span className="section-icon" role="img" aria-label="Robot">🤖</span>
        <div>
          <h2>{t('plannerTitle')}</h2>
          <p className="section-desc">{t('plannerDesc')}</p>
        </div>
      </div>

      <div className="plan-card green-card">
        <p>
          <strong>🌱 {lang === 'kn' ? 'ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆ:' : lang === 'hi' ? 'अनुशंसित फसल:' : 'Recommended Crop:'}</strong>{' '}
          {recommendedCrop ? getCropDropdownLabel(recommendedCrop, lang) : t('notAvailable')}
        </p>

        <p>
          <strong>🍃 {lang === 'kn' ? 'ಪತ್ತೆಯಾದ ರೋಗ:' : lang === 'hi' ? 'पहचाना गया रोग:' : 'Disease Detected:'}</strong>{' '}
          {displayDisease}
        </p>

        <p>
          <strong>💰 {lang === 'kn' ? 'ಮಾರುಕಟ್ಟೆ ಬೆಲೆ:' : lang === 'hi' ? 'बाजार मूल्य:' : 'Market Price:'}</strong>{' '}
          {displayPrice}
        </p>

        <p>
          <strong>💧 {lang === 'kn' ? 'ನೀರಾವರಿ ವೇಳಾಪಟ್ಟಿ:' : lang === 'hi' ? 'सिंचाई अनुसूची:' : 'Irrigation Schedule:'}</strong>{' '}
          {displayIrrigation}
        </p>

        <p>
          <strong>📍 {lang === 'kn' ? 'ನಗರ / ಜಿಲ್ಲೆ:' : lang === 'hi' ? 'शहर / जिला:' : 'City / District:'}</strong>{' '}
          {city ? getDistrictDropdownLabel(city, lang) : t('notAvailable')}
        </p>
      </div>

      {!hasAnyInput && (
        <p className="info-note" style={{ marginTop: '12px' }}>{t('plannerNeedsInput')}</p>
      )}

      {/* SINGLE UNIFIED PRIMARY ACTION BUTTON */}
      <div style={{ marginTop: '16px' }}>
        <button
          type="button"
          className="gov-btn"
          style={{
            width: '100%',
            padding: '14px 24px',
            fontSize: '1.05rem',
            fontWeight: '600',
            background: hasAnyInput && !loading
              ? 'linear-gradient(135deg, #1b5e20 0%, #2e7d32 50%, #388e3c 100%)'
              : '#a5d6a7',
            boxShadow: '0 4px 14px rgba(27, 94, 32, 0.35)',
            cursor: !hasAnyInput || loading ? 'not-allowed' : 'pointer',
            transition: 'all 0.2s ease-in-out'
          }}
          onClick={handleGeneratePlan}
          disabled={!hasAnyInput || loading}
        >
          {buttonText}
        </button>
      </div>

      {/* UNIFIED 360° FARM ACTION PLAN RESULT CARD */}
      {(plan?.ai_plan || plan?.planting_schedule || plan?.summary) && (
        <div
          id="unifiedFarmPlanCard"
          style={{
            display: 'flex',
            flexDirection: 'column',
            width: '100%',
            boxSizing: 'border-box',
            marginTop: '24px',
            background: 'linear-gradient(180deg, #f8fbf8 0%, #ffffff 100%)',
            border: '2px solid #81c784',
            borderRadius: '12px',
            boxShadow: '0 6px 20px rgba(46, 125, 50, 0.14)',
            padding: '22px'
          }}
        >
          {/* Master Card Header */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '10px',
              borderBottom: '2px solid #c8e6c9',
              paddingBottom: '12px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>
                {lang === 'kn' ? '🌾 ಸಂಪೂರ್ಣ 360° ಕೃಷಿ ಕ್ರಿಯಾ ಯೋಜನೆ ಮತ್ತು ಕೃಷಿ ತಜ್ಞರ ಮಾರ್ಗಸೂಚಿ' : lang === 'hi' ? '🌾 संपूर्ण 360° कृषि कार्ययोजना एवं रोडमैप' : '🌾 Complete 360° Farm Action Plan & Agronomist Roadmap'}
              </span>
              {plan.provider && (
                <span className="ai-provider-badge" style={{ background: '#2e7d32', color: '#fff', fontSize: '11px', padding: '3px 9px', borderRadius: '12px', fontWeight: '600' }}>
                  ⚡ {plan.provider}
                </span>
              )}
            </div>
            <button
              type="button"
              className="gov-btn"
              onClick={toggleSpeakPlan}
              style={{
                padding: '6px 16px',
                fontSize: '13px',
                background: speaking ? '#d32f2f' : 'linear-gradient(135deg, #2e7d32, #1b5e20)',
                margin: 0
              }}
            >
              {speaking
                ? (lang === 'kn' ? '⏹ ಆಡಿಯೋ ನಿಲ್ಲಿಸಿ' : lang === 'hi' ? '⏹ ऑडियो रोकें' : '⏹ Stop Audio')
                : (lang === 'kn' ? '🔊 ಧ್ವನಿಯಲ್ಲಿ ಕೇಳಿ' : lang === 'hi' ? '🔊 बोलकर सुनाएं' : '🔊 Read Aloud')}
            </button>
          </div>

          {/* Executive Summary Status Banner */}
          {activeSummary && (
            <div
              style={{
                marginTop: '16px',
                padding: '12px 16px',
                borderRadius: '8px',
                background: activeSummary.includes('🚨')
                  ? '#fef2f2'
                  : activeSummary.includes('⚠')
                    ? '#fffbeb'
                    : '#f0fdf4',
                border: activeSummary.includes('🚨')
                  ? '1px solid #fecaca'
                  : activeSummary.includes('⚠')
                    ? '1px solid #fde68a'
                    : '1px solid #bbf7d0',
                color: activeSummary.includes('🚨')
                  ? '#991b1b'
                  : activeSummary.includes('⚠')
                    ? '#92400e'
                    : '#166534',
                fontWeight: '600',
                fontSize: '15px'
              }}
            >
              {activeSummary}
            </div>
          )}

          {/* Plant Health & Disease Diagnosis Badge */}
          <div
            style={{
              width: '100%',
              boxSizing: 'border-box',
              marginTop: '14px',
              padding: '12px 16px',
              borderRadius: '8px',
              background: predictedDisease && predictedDisease.toLowerCase().includes('healthy')
                ? '#f0fdf4'
                : predictedDisease
                  ? '#fef2f2'
                  : '#f8fafc',
              border: predictedDisease && predictedDisease.toLowerCase().includes('healthy')
                ? '1px solid #86efac'
                : predictedDisease
                  ? '1px solid #fecaca'
                  : '1px solid #e2e8f0',
              color: predictedDisease && predictedDisease.toLowerCase().includes('healthy')
                ? '#166534'
                : predictedDisease
                  ? '#991b1b'
                  : '#334155',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '8px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '600', fontSize: '14.5px' }}>
              <span style={{ fontSize: '18px' }}>🍃</span>
              <div>
                <span>{lang === 'kn' ? 'ಸಸ್ಯದ ಆರೋಗ್ಯ ಮತ್ತು ರೋಗ ಸ್ಥಿತಿ: ' : lang === 'hi' ? 'पौधे का स्वास्थ्य एवं रोग स्थिति: ' : 'Plant Health & Disease Status: '}</span>
                <strong style={{ marginLeft: '6px' }}>
                  {predictedDisease || (lang === 'kn' ? 'ಯಾವುದೇ ಸಕ್ರಿಯ ರೋಗವಿಲ್ಲ (ಮುನ್ನೆಚ್ಚರಿಕೆ IPM ಸಕ್ರಿಯ)' : lang === 'hi' ? 'कोई सक्रिय रोग नहीं (निवारक IPM सक्रिय)' : 'No Active Disease Reported (Preventive IPM Active)')}
                </strong>
              </div>
            </div>
            {predictedDisease ? (
              predictedDisease.toLowerCase().includes('healthy') ? (
                <span style={{ background: '#166534', color: '#ffffff', padding: '3px 9px', borderRadius: '10px', fontSize: '11px', fontWeight: '700' }}>
                  ✅ HEALTHY
                </span>
              ) : (
                <span style={{ background: '#dc2626', color: '#ffffff', padding: '3px 9px', borderRadius: '10px', fontSize: '11px', fontWeight: '700' }}>
                  🚨 ACTIVE PATHOGEN
                </span>
              )
            ) : (
              <span style={{ background: '#475569', color: '#ffffff', padding: '3px 9px', borderRadius: '10px', fontSize: '11px', fontWeight: '700' }}>
                ℹ PREVENTIVE IPM
              </span>
            )}
          </div>

          {/* AI Strategic Agronomist Advisory */}
          {activeAiPlan && (
            <div
              style={{
                marginTop: '18px',
                padding: '16px',
                background: '#ffffff',
                borderRadius: '8px',
                border: '1px solid #e2e8f0'
              }}
            >
              <div style={{ fontWeight: '700', color: '#166534', marginBottom: '8px', fontSize: '15px' }}>
                💡 {lang === 'kn' ? 'AI ಕೃಷಿ ತಜ್ಞರ ವೈಜ್ಞಾನಿಕ ಕಾರ್ಯತಂತ್ರ ನೀಲನಕ್ಷೆ' : lang === 'hi' ? 'AI कृषि वैज्ञानिक रणनीतिक ब्लूप्रिंट' : 'AI Agronomist Strategic Blueprint'}
              </div>
              <div
                className="plan-card-body"
                style={{
                  whiteSpace: 'pre-line',
                  fontSize: '1.01rem',
                  lineHeight: '1.8',
                  color: '#1e293b'
                }}
              >
                {activeAiPlan}
              </div>

              {plan.sources && plan.sources.length > 0 && (
                <div
                  className="ai-sources-tag"
                  style={{
                    marginTop: '16px',
                    paddingTop: '10px',
                    borderTop: '1px dashed #a5d6a7'
                  }}
                >
                  <span className="source-label" style={{ fontWeight: 'bold', marginRight: '6px' }}>
                    📚 {lang === 'kn' ? 'ಆಧಾರಿತ ಕೃಷಿ ಜ್ಞಾನ ಮೂಲಗಳು:' : lang === 'hi' ? 'आधारित कृषि ज्ञान स्रोत:' : 'Grounded Knowledge Sources:'}
                  </span>
                  {plan.sources.map((src, i) => (
                    <span
                      key={i}
                      className="source-pill"
                      style={{
                        display: 'inline-block',
                        margin: '2px 4px',
                        padding: '2px 8px',
                        background: '#e8f5e9',
                        border: '1px solid #c8e6c9',
                        borderRadius: '12px',
                        fontSize: '11px'
                      }}
                    >
                      {src}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Critical Priority Actions */}
          {activePriority?.length > 0 && (
            <div style={{ marginTop: '16px' }}>
              <div className="result-section-title critical-title">
                {lang === 'kn' ? '🚨 ತುರ್ತು ಆದ್ಯತೆಯ ಕ್ರಮಗಳು' : lang === 'hi' ? '🚨 अति महत्वपूर्ण प्राथमिकता कदम' : '🚨 Critical Priority Actions'}
              </div>
              {activePriority.map((p, i) => (
                <div key={i} className="result-card critical-result" style={{ marginBottom: '8px' }}>
                  {p}
                </div>
              ))}
            </div>
          )}

          {/* Verified Telemetry Advice & Alerts */}
          {(activeAdvice?.length > 0 || activeAlerts?.length > 0) && (
            <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {activeAdvice?.map((a, i) => (
                <div
                  key={i}
                  className="result-card crop-result"
                  style={{ margin: 0, background: '#f0fdf4', borderColor: '#86efac' }}
                >
                  {a}
                </div>
              ))}
              {activeAlerts?.map((a, i) => (
                <div key={i} className="result-card alert-result" style={{ margin: 0 }}>
                  {a}
                </div>
              ))}
            </div>
          )}

          {/* Structured Field Operations Matrix */}
          {activePlanting && (
            <div style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px dashed #cbd5e1' }}>
              <div style={{ fontWeight: '700', color: '#1e293b', fontSize: '15px', marginBottom: '12px' }}>
                {lang === 'kn' ? '📋 ಕೃಷಿ ಕಾರ್ಯಾಚರಣೆ ಮತ್ತು ಉತ್ಪಾದನಾ ವೇಳಾಪಟ್ಟಿ' : lang === 'hi' ? '📋 कृषि परिचालन एवं उत्पादन कैलेंडर' : '📋 Operations & Production Calendar'}
              </div>
              <div className="plan-grid">
                <div className="plan-card green-card">
                  <div className="plan-card-title">{lang === 'kn' ? '🌱 ಬಿತ್ತನೆ ವೇಳಾಪಟ್ಟಿ' : lang === 'hi' ? '🌱 बुवाई समय-सारणी' : '🌱 Planting Schedule'}</div>
                  <div className="plan-card-body">{activePlanting}</div>
                </div>
                <div className="plan-card green-card">
                  <div className="plan-card-title">{lang === 'kn' ? '🌾 ಕಟಾವು ವೇಳಾಪಟ್ಟಿ' : lang === 'hi' ? '🌾 कटाई समय-सारणी' : '🌾 Harvest Schedule'}</div>
                  <div className="plan-card-body">{activeHarvest}</div>
                </div>
                <div className="plan-card blue-card">
                  <div className="plan-card-title">{lang === 'kn' ? '🌿 ರಸಗೊಬ್ಬರ ಯೋಜನೆ (NPK)' : lang === 'hi' ? '🌿 संतुलित उर्वरक योजना (NPK)' : '🌿 Fertilizer Plan (NPK)'}</div>
                  <div className="plan-card-body">{activeFertilizer}</div>
                </div>
                <div className="plan-card purple-card">
                  <div className="plan-card-title">{lang === 'kn' ? '💰 ಮಾರುಕಟ್ಟೆ ಮತ್ತು ಮಾರಾಟ ತಂತ್ರ' : lang === 'hi' ? '💰 विपणन एवं बिक्री रणनीति' : '💰 Selling & Market Timing'}</div>
                  <div className="plan-card-body">{activeSell}</div>
                </div>
              </div>
              {activePestGuide?.length > 0 && (
                <div className="plan-card orange-card" style={{ marginTop: '12px' }}>
                  <div className="plan-card-title">{lang === 'kn' ? '🐛 ಸಮಗ್ರ ಕೀಟ ನಿರ್ವಹಣೆ (IPM)' : lang === 'hi' ? '🐛 एकीकृत कीट प्रबंधन (IPM)' : '🐛 Integrated Pest Management (IPM)'}</div>
                  {activePestGuide.map((pest, i) => (
                    <div key={i} className="pest-item">
                      • {pest}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
