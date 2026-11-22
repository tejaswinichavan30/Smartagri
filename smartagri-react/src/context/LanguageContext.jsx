import { createContext, useContext, useState } from 'react';

// Every UI string that had data-en / data-kn / data-hi attributes in the
// original Jinja templates lives here, keyed the same way across pages.
// AI-generated result text (crop/disease/price/planner/query answers) stays
// English-only, matching the note in the original header.
const translations = {
  tagline: {
    en: 'Agent-Based Intelligent System for Farmer Decision Support',
    kn: 'ರೈತ ನಿರ್ಧಾರ ಬೆಂಬಲಕ್ಕಾಗಿ ಏಜೆಂಟ್-ಆಧಾರಿತ ಬುದ್ಧಿವಂತ ವ್ಯವಸ್ಥೆ',
    hi: 'किसान निर्णय समर्थन के लिए एजेंट-आधारित बुद्धिमान प्रणाली'
  },
  taglineShort: {
    en: 'Agent-Based AI System for Farmer Decision Support',
    kn: 'ರೈತ ನಿರ್ಧಾರ ಬೆಂಬಲಕ್ಕಾಗಿ AI ವ್ಯವಸ್ಥೆ',
    hi: 'किसान निर्णय समर्थन के लिए AI प्रणाली'
  },
  navCrop: { en: '🌱 Crop Recommendation', kn: '🌱 ಬೆಳೆ ಶಿಫಾರಸು', hi: '🌱 फसल अनुशंसा' },
  navPrice: { en: '💰 Market Price', kn: '💰 ಮಾರುಕಟ್ಟೆ ಬೆಲೆ', hi: '💰 बाजार मूल्य' },
  navDisease: { en: '🍃 Disease Detection', kn: '🍃 ರೋಗ ಪತ್ತೆ', hi: '🍃 रोग पहचान' },
  navIrrigation: { en: '💧 Smart Irrigation', kn: '💧 ಸ್ಮಾರ್ಟ್ ನೀರಾವರಿ', hi: '💧 स्मार्ट सिंचाई' },
  navPlanner: { en: '🤖 Planner Agent', kn: '🤖 ಯೋಜಕ ಏಜೆಂಟ್', hi: '🤖 योजनाकार एजेंट' },
  marquee: {
    en: '🌾 Welcome to SmartAgri AI — Empowering Farmers with Artificial Intelligence | 🌱 Get Crop Recommendations | 💰 Check Market Prices | 🍃 Detect Leaf Diseases | 🤖 Get AI Farm Planning',
    kn: '🌾 ಸ್ಮಾರ್ಟ್‌ಆಗ್ರಿ AIಗೆ ಸ್ವಾಗತ — ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆಯಿಂದ ರೈತರನ್ನು ಸಶಕ್ತಗೊಳಿಸುವುದು | 🌱 ಬೆಳೆ ಶಿಫಾರಸು ಪಡೆಯಿರಿ | 💰 ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ತಿಳಿಯಿರಿ | 🍃 ಎಲೆ ರೋಗ ಪತ್ತೆ ಮಾಡಿ',
    hi: '🌾 स्मार्टएग्री AI में आपका स्वागत है — कृत्रिम बुद्धिमत्ता से किसानों को सशक्त बनाना | 🌱 फसल अनुशंसा पाएं | 💰 बाजार मूल्य जांचें | 🍃 पत्ती रोग पहचानें'
  },
  langNote: {
    en: 'Note: AI-generated results (crop/disease/price/planner text) are currently shown in English only.',
    kn: 'ಗಮನಿಸಿ: AI-ರಚಿತ ಫಲಿತಾಂಶಗಳು (ಬೆಳೆ/ರೋಗ/ಬೆಲೆ/ಯೋಜಕ) ಪ್ರಸ್ತುತ ಇಂಗ್ಲಿಷ್‌ನಲ್ಲಿ ಮಾತ್ರ ತೋರಿಸಲಾಗುತ್ತದೆ.',
    hi: 'ध्यान दें: AI-जनित परिणाम (फसल/रोग/मूल्य/योजना) फिलहाल केवल अंग्रेज़ी में दिखाए जाते हैं.'
  },
  resetSession: { en: '🔄 Start New Session', kn: '🔄 ಹೊಸ ಸೆಶನ್ ಪ್ರಾರಂಭಿಸಿ', hi: '🔄 नया सत्र शुरू करें' },
  resetConfirm: {
    en: 'Start a new session? This clears all current results.',
    kn: 'ಹೊಸ ಸೆಶನ್ ಪ್ರಾರಂಭಿಸುವುದೇ? ಇದು ಎಲ್ಲಾ ಪ್ರಸ್ತುತ ಫಲಿತಾಂಶಗಳನ್ನು ತೆರವುಗೊಳಿಸುತ್ತದೆ.',
    hi: 'नया सत्र शुरू करें? इससे सभी वर्तमान परिणाम साफ़ हो जाएंगे।'
  },
  voiceTitle: { en: 'Voice Query Assistant', kn: 'ಧ್ವನಿ ಪ್ರಶ್ನೆ ಸಹಾಯಕ', hi: 'वॉयस क्वेरी सहायक' },
  voiceDesc: {
    en: 'Ask any farming question in English, Kannada or Hindi',
    kn: 'ಇಂಗ್ಲಿಷ್, ಕನ್ನಡ ಅಥವಾ ಹಿಂದಿಯಲ್ಲಿ ಯಾವುದೇ ಕೃಷಿ ಪ್ರಶ್ನೆ ಕೇಳಿ',
    hi: 'अंग्रेजी, कन्नड़ या हिंदी में कोई भी कृषि प्रश्न पूछें'
  },
  voicePlaceholder: {
    en: 'e.g. Which crop should I grow? / What fertilizer for tomato?',
    kn: 'ಉದಾ. ಯಾವ ಬೆಳೆ ಬೆಳೆಯಬೇಕು? / ಟೊಮೆಟೊಗೆ ಯಾವ ಗೊಬ್ಬರ?',
    hi: 'जैसे कौन सी फसल उगाएं? / टमाटर के लिए कौन सा खाद?'
  },
  startVoice: { en: '🎤 Start Voice Input', kn: '🎤 ಧ್ವನಿ ಇನ್‌ಪುಟ್ ಪ್ರಾರಂಭಿಸಿ', hi: '🎤 वॉयस इनपुट शुरू करें' },
  listening: { en: '🎤 Listening…', kn: '🎤 ಆಲಿಸುತ್ತಿದೆ…', hi: '🎤 सुन रहा है…' },
  getAnswer: { en: '🔍 Get Answer', kn: '🔍 ಉತ್ತರ ಪಡೆಯಿರಿ', hi: '🔍 उत्तर पाएं' },
  diseaseTitle: { en: 'Leaf Disease Detection', kn: 'ಎಲೆ ರೋಗ ಪತ್ತೆ', hi: 'पत्ती रोग पहचान' },
  diseaseDesc: {
    en: 'Upload a leaf image to detect plant diseases using AI',
    kn: 'AI ಬಳಸಿ ಸಸ್ಯ ರೋಗಗಳನ್ನು ಪತ್ತೆ ಮಾಡಲು ಎಲೆ ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ',
    hi: 'AI का उपयोग करके पौधों की बीमारियों का पता लगाने के लिए पत्ती की छवि अपलोड करें'
  },
  diseaseFileTypes: {
    en: '📌 Accepted file types: JPG, JPEG, PNG',
    kn: '📌 ಸ್ವೀಕೃತ ಫೈಲ್ ಪ್ರಕಾರಗಳು: JPG, JPEG, PNG',
    hi: '📌 स्वीकृत फ़ाइल प्रकार: JPG, JPEG, PNG'
  },
  selectLeafImage: { en: 'Select Leaf Image', kn: 'ಎಲೆ ಚಿತ್ರ ಆಯ್ಕೆ ಮಾಡಿ', hi: 'पत्ती की छवि चुनें' },
  referenceImageBadge: {
    en: 'Reference image (source not yet verified)',
    kn: 'ಉಲ್ಲೇಖ ಚಿತ್ರ (ಮೂಲ ಪರಿಶೀಲಿಸಬೇಕಿದೆ)',
    hi: 'संदर्भ छवि (स्रोत अभी सत्यापित नहीं है)'
  },
  detectDisease: { en: '🔍 Detect Disease', kn: '🔍 ರೋಗ ಪತ್ತೆ ಮಾಡಿ', hi: '🔍 रोग पहचानें' },
  uploadedImage: { en: 'Uploaded Image:', kn: 'ಅಪ್‌ಲೋಡ್ ಮಾಡಿದ ಚಿತ್ರ:', hi: 'अपलोड की गई छवि:' },
  priceTitle: { en: 'Market Price Prediction', kn: 'ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಮುನ್ಸೂಚನೆ', hi: 'बाजार मूल्य पूर्वानुमान' },
  priceDesc: {
    en: 'Predict mandi prices before selling your crop',
    kn: 'ನಿಮ್ಮ ಬೆಳೆ ಮಾರಾಟ ಮಾಡುವ ಮೊದಲು ಮಂಡಿ ಬೆಲೆಗಳನ್ನು ಊಹಿಸಿ',
    hi: 'अपनी फसल बेचने से पहले मंडी की कीमतों का अनुमान लगाएं'
  },
  selectCrop: { en: '-- Select Crop --', kn: '-- ಬೆಳೆ ಆಯ್ಕೆ ಮಾಡಿ --', hi: '-- फसल चुनें --' },
  selectCropLabel: { en: 'Select Crop', kn: 'ಬೆಳೆ ಆಯ್ಕೆ ಮಾಡಿ', hi: 'फसल चुनें' },
  selectDistrictLabel: { en: 'Select District', kn: 'ಜಿಲ್ಲೆ ಆಯ್ಕೆ ಮಾಡಿ', hi: 'जिला चुनें' },
  month: { en: 'Month', kn: 'ತಿಂಗಳು', hi: 'महीना' },
  year: { en: 'Year', kn: 'ವರ್ಷ', hi: 'वर्ष' },
  predictPrice: { en: '📊 Predict Price', kn: '📊 ಬೆಲೆ ಮುನ್ಸೂಚಿಸಿ', hi: '📊 मूल्य पूर्वानुमान' },
  cropTitle: { en: 'Crop Recommendation', kn: 'ಬೆಳೆ ಶಿಫಾರಸು', hi: 'फसल अनुशंसा' },
  cropDesc: {
    en: 'Get AI-powered crop suggestions based on soil and live weather data',
    kn: 'ಮಣ್ಣು ಮತ್ತು ನೇರ ಹವಾಮಾನ ಡೇಟಾ ಆಧರಿಸಿ AI ಬೆಳೆ ಸಲಹೆಗಳನ್ನು ಪಡೆಯಿರಿ',
    hi: 'मिट्टी और लाइव मौसम डेटा के आधार पर AI फसल सुझाव प्राप्त करें'
  },
  cropStep1: {
    en: '📋 Step 1: Select your district to auto-fill typical soil values',
    kn: '📋 ಹಂತ 1: ವಿಶಿಷ್ಟ ಮಣ್ಣಿನ ಮೌಲ್ಯಗಳನ್ನು ತಂತಾನೇ ತುಂಬಲು ನಿಮ್ಮ ಜಿಲ್ಲೆಯನ್ನು ಆಯ್ಕೆ ಮಾಡಿ',
    hi: '📋 चरण 1: विशिष्ट मिट्टी मान स्वचालित रूप से भरने के लिए अपना जिला चुनें'
  },
  cropAutoFillHint: {
    en: 'Fields will auto-fill once you select a district — you can still edit any value.',
    kn: 'ನೀವು ಜಿಲ್ಲೆಯನ್ನು ಆಯ್ಕೆ ಮಾಡಿದ ನಂತರ ಕ್ಷೇತ್ರಗಳು ಸ್ವಯಂಚಾಲಿತವಾಗಿ ತುಂಬಲ್ಪಡುತ್ತವೆ — ನೀವು ಯಾವುದೇ ಮೌಲ್ಯವನ್ನು ಇನ್ನೂ ಸಂಪಾದಿಸಬಹುದು.',
    hi: 'जिला चुनने के बाद फ़ील्ड अपने आप भर जाएंगे — आप किसी भी मान को अभी भी संपादित कर सकते हैं।'
  },
  cropDistrictAutoFillLabel: {
    en: 'Select District (Auto-fill soil values)',
    kn: 'ಜಿಲ್ಲೆ ಆಯ್ಕೆ ಮಾಡಿ (ಮಣ್ಣಿನ ಮೌಲ್ಯ ತಂತಾನೇ ತುಂಬುತ್ತದೆ)',
    hi: 'जिला चुनें (मिट्टी के मान स्वचालित भरें)'
  },
  farmingSeason: { en: 'Farming Season', kn: 'ಕೃಷಿ ಋತು', hi: 'कृषि मौसम / ऋतु' },
  seasonAuto: {
    en: '🌤 Auto Detect (Current Season: Kharif - Monsoon)',
    kn: '🌤 ಸ್ವಯಂಚಾಲಿತ (ಪ್ರಸ್ತುತ ತಿಂಗಳು: ಖಾರೀಫ್ - ಮುಂಗಾರು)',
    hi: '🌤 स्वचालित पहचान (वर्तमान माह: खरीफ - मानसून)'
  },
  seasonKharif: {
    en: '🌧 Kharif (Monsoon: June - October)',
    kn: '🌧 ಖಾರೀಫ್ (ಮುಂಗಾರು: ಜೂನ್ - ಅಕ್ಟೋಬರ್)',
    hi: '🌧 खरीफ (मानसून: जून - अक्टूबर)'
  },
  seasonRabi: {
    en: '❄ Rabi (Winter: October - March)',
    kn: '❄ ರಬಿ (ಹಿಂಗಾರು: ಅಕ್ಟೋಬರ್ - ಮಾರ್ಚ್)',
    hi: '❄ रबी (सर्दियां: अक्टूबर - मार्च)'
  },
  seasonZaid: {
    en: '☀ Zaid (Summer: March - June)',
    kn: '☀ ಜೈದ್ (ಬೇಸಿಗೆ: ಮಾರ್ಚ್ - ಜೂನ್)',
    hi: '☀ जायद (गर्मी: मार्च - जून)'
  },
  seasonWholeYear: {
    en: '🌱 Whole Year / Perennial',
    kn: '🌱 ವರ್ಷಪೂರ್ತಿ / ದೀರ್ಘಕಾಲೀನ ಬೆಳೆ',
    hi: '🌱 पूरे साल / बारहमासी'
  },
  nitrogen: { en: 'Nitrogen (N)', kn: 'ಸಾರಜನಕ (N)', hi: 'नाइट्रोजन (N)' },
  phosphorus: { en: 'Phosphorus (P)', kn: 'ರಂಜಕ (P)', hi: 'फास्फोरस (P)' },
  potassium: { en: 'Potassium (K)', kn: 'ಪೊಟ್ಯಾಸಿಯಮ್ (K)', hi: 'पोटेशियम (K)' },
  phValue: { en: 'pH Value', kn: 'pH ಮೌಲ್ಯ', hi: 'pH मान' },
  rainfall: { en: 'Rainfall (mm)', kn: 'ಮಳೆ (mm)', hi: 'वर्षा (mm)' },
  recommendCrop: { en: '🌾 Recommend Crop', kn: '🌾 ಬೆಳೆ ಶಿಫಾರಸು ಮಾಡಿ', hi: '🌾 फसल की सिफारिश करें' },
  plannerTitle: {
    en: 'Planner Agent — Final Farm Decision',
    kn: 'ಯೋಜಕ ಏಜೆಂಟ್ — ಅಂತಿಮ ಕೃಷಿ ನಿರ್ಧಾರ',
    hi: 'योजनाकार एजेंट — अंतिम खेत निर्णय'
  },
  plannerDesc: {
    en: 'AI orchestration combining all module outputs for final farming advice',
    kn: 'ಅಂತಿಮ ಕೃಷಿ ಸಲಹೆಗಾಗಿ ಎಲ್ಲಾ ಮಾಡ್ಯೂಲ್ ಔಟ್‌ಪುಟ್‌ಗಳನ್ನು ಸಂಯೋಜಿಸುವ AI ಆರ್ಕೆಸ್ಟ್ರೇಶನ್',
    hi: 'अंतिम कृषि सलाह के लिए सभी मॉड्यूल आउटपुट को जोड़ने वाला AI ऑर्केस्ट्रेशन'
  },
  plannerNeedsInput: {
    en: '⚠ Run at least one module above (Crop / Disease / Price) before generating a plan.',
    kn: '⚠ ಯೋಜನೆ ರಚಿಸುವ ಮೊದಲು ಮೇಲಿನ ಕನಿಷ್ಠ ಒಂದು ಮಾಡ್ಯೂಲ್ ಅನ್ನು ಚಲಾಯಿಸಿ.',
    hi: '⚠ योजना बनाने से पहले ऊपर दिए गए कम से कम एक मॉड्यूल को चलाएं।'
  },
  getFarmPlan: {
    en: '🤖 Get Complete Farm Plan',
    kn: '🤖 ಸಂಪೂರ್ಣ ಕೃಷಿ ಯೋಜನೆ ಪಡೆಯಿರಿ',
    hi: '🤖 पूर्ण कृषि योजना प्राप्त करें'
  },
  notAvailable: { en: 'Not Available', kn: 'ಲಭ್ಯವಿಲ್ಲ', hi: 'उपलब्ध नहीं' },

  // Smart Irrigation Agent
  irrigationTitle: {
    en: 'Smart Irrigation Agent — Precision Water Planner',
    kn: 'ಸ್ಮಾರ್ಟ್ ನೀರಾವರಿ ಏಜೆಂಟ್ — ನಿಖರ ನೀರಿನ ಯೋಜನೆ',
    hi: 'स्मार्ट सिंचाई एजेंट — सटीक जल नियोजन'
  },
  irrigationDesc: {
    en: 'FAO Penman-Monteith crop evapotranspiration (ETc) model integrated with live district weather and soil moisture dynamics',
    kn: 'ಲೈವ್ ಜಿಲ್ಲಾ ಹವಾಮಾನ ಮತ್ತು ಮಣ್ಣಿನ ತೇವಾಂಶದೊಂದಿಗೆ ಸಂಯೋಜಿತ FAO ನಿಖರ ಬೆಳೆ ನೀರಾವರಿ ಮಾದರಿ',
    hi: 'लाइव जिला मौसम एवं मिट्टी की नमी के साथ एकीकृत एफएओ सटीक फसल जल मॉडल'
  },
  growthStage: { en: 'Growth Stage', kn: 'ಬೆಳವಣಿಗೆಯ ಹಂತ', hi: 'फसल की अवस्था' },
  soilTexture: { en: 'Soil Texture', kn: 'ಮಣ್ಣಿನ ವಿಧ', hi: 'मिट्टी का प्रकार' },
  landArea: { en: 'Land Area (Acres)', kn: 'ಜಮೀನಿನ ವಿಸ್ತೀರ್ಣ (ಎಕರೆ)', hi: 'खेत का क्षेत्रफल (एकड़)' },
  irrigationSystem: { en: 'Irrigation System', kn: 'ನೀರಾವರಿ ಪದ್ಧತಿ', hi: 'सिंचाई प्रणाली' },
  locationDistrict: { en: 'Location District (Live Weather)', kn: 'ಜಿಲ್ಲೆ (ನೇರ ಹವಾಮಾನ)', hi: 'जिला (लाइव मौसम)' },
  calculateIrrigation: {
    en: '💧 Calculate Precision Irrigation Plan',
    kn: '💧 ನಿಖರ ನೀರಾವರಿ ಯೋಜನೆ ಲೆಕ್ಕಾಚಾರ ಮಾಡಿ',
    hi: '💧 सटीक सिंचाई योजना की गणना करें'
  },
  waterReqSchedule: {
    en: 'Precision Water Requirement & Schedule',
    kn: 'ನಿಖರ ನೀರಿನ ಅಗತ್ಯ ಮತ್ತು ವೇಳಾಪಟ್ಟಿ',
    hi: 'सटीक जल आवश्यकता एवं समय सारणी'
  },
  totalDailyWater: { en: 'Total Daily Water', kn: 'ದೈನಂದಿನ ಒಟ್ಟು ನೀರು', hi: 'दैनिक कुल पानी' },
  pumpRuntime: { en: 'Pump Runtime', kn: 'ಪಂಪ್ ಚಾಲನಾ ಸಮಯ', hi: 'पंप चलाने का समय' },
  frequency: { en: 'Frequency', kn: 'ಆವರ್ತನ', hi: 'आवृत्ति' },
  liveWeatherIndex: { en: 'Live Weather Index', kn: 'ಲೈವ್ ಹವಾಮಾನ ಸೂಚ್ಯಂಕ', hi: 'लाइव मौसम सूचकांक' },
  readAloud: { en: '🔊 Read Aloud', kn: '🔊 ಧ್ವನಿಯಲ್ಲಿ ಕೇಳಿ', hi: '🔊 बोलकर सुनाएं' },
  stopAudio: { en: '⏹ Stop Audio', kn: '⏹ ಆಡಿಯೊ ನಿಲ್ಲಿಸಿ', hi: '⏹ ऑडियो रोकें' },
  
  // Decision Intelligence Suite
  diTitle: {
    en: 'AI Decision Intelligence & Simulation Hub',
    kn: 'AI ನಿರ್ಧಾರ ಬುದ್ಧಿಮತ್ತೆ ಮತ್ತು ಸಿಮ್ಯುಲೇಶನ್ ಹಬ್',
    hi: 'AI निर्णय बुद्धिमत्ता एवं सिमुलेशन हब'
  },
  diDesc: {
    en: 'Next-Generation Causal Reasoning, Digital Twin Sandbox, Multi-Agent Debate & Regret-Minimization Planning',
    kn: 'ಮುಂದಿನ ಪೀಳಿಗೆಯ ಕಾರಣಾತ್ಮಕ ತಾರ್ಕಿಕತೆ, ಡಿಜಿಟಲ್ ಟ್ವಿನ್ ಸಿಮ್ಯುಲೇಟರ್, ಮಲ್ಟಿ-ಏಜೆಂಟ್ ಚರ್ಚೆ ಮತ್ತು ರಿಸ್ಕ್-ಅಡಾಪ್ಟಿವ್ ಯೋಜನೆ',
    hi: 'अगली पीढ़ी का कारण संबंधी तर्क, डिजिटल ट्विन सिमुलेटर, मल्टी-एजेंट डिबेट और जोखिम-अनुकूली योजना'
  },
  tabDigitalTwin: { en: '🎛️ Digital Twin Simulator', kn: '🎛️ ಡಿಜಿಟಲ್ ಟ್ವಿನ್ ಸಿಮ್ಯುಲೇಟರ್', hi: '🎛️ डिजिटल ट्विन सिमुलेटर' },
  tabCounterfactual: { en: '⏪ Counterfactual "What-If" AI', kn: '⏪ ಕೌಂಟರ್‌ಫ್ಯಾಕ್ಚುಯಲ್ "ಏನಾಗುತ್ತಿತ್ತು?" AI', hi: '⏪ काउंटरफैक्चुअल "क्या होता?" AI' },
  tabDebate: { en: '🎭 Multi-Agent Debate Room', kn: '🎭 ಮಲ್ಟಿ-ಏಜೆಂಟ್ ಚರ್ಚಾ ಕೊಠಡಿ', hi: '🎭 मल्टी-एजेंट डिबेट रूम' },
  tabRegret: { en: '🛡️ Regret Minimization Plans', kn: '🛡️ ವಿಷಾದ ಕನಿಷ್ಠೀಕರಣ ಯೋಜನೆಗಳು', hi: '🛡️ रिग्रेट न्यूनीकरण योजनाएं' }
};

const LanguageContext = createContext(null);

export function LanguageProvider({ children }) {
  const [lang, setLang] = useState('en');
  // t(key) looks up the current-language string, falling back to English.
  const t = (key) => (translations[key] ? translations[key][lang] || translations[key].en : key);
  return (
    <LanguageContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error('useLanguage must be used within a LanguageProvider');
  return ctx;
}
