import { useState, useEffect, useRef } from 'react';
import { useLanguage } from '../../context/LanguageContext.jsx';
import { api } from '../../api.js';
import { getCropName } from '../../data/districts.js';

const DI_TEXTS = {
  badge: {
    en: 'RESEARCH INNOVATION SUITE',
    kn: 'ಸಂಶೋಧನಾ ಇನ್ನೋವೇಶನ್ ಸೂಟ್',
    hi: 'अनुसंधान नवाचार सुइट'
  },
  // Tab 1: Digital Twin Sandbox
  dtIntro: {
    en: 'Interactive Crop Sandbox: Adjust environmental and management sliders below to simulate soil moisture dynamics, crop stress indices, disease pressure, and projected net profits in real-time.',
    kn: 'ಸಂವಾದಾತ್ಮಕ ಬೆಳೆ ಸ್ಯಾಂಡ್‌ಬಾಕ್ಸ್: ಮಣ್ಣಿನ ತೇವಾಂಶ ಡೈನಾಮಿಕ್ಸ್, ಬೆಳೆ ಒತ್ತಡ ಸೂಚ್ಯಂಕಗಳು, ರೋಗದ ಬಾಧೆ ಮತ್ತು ನಿವ್ವಳ ಲಾಭವನ್ನು ನೈಜ ಸಮಯದಲ್ಲಿ ಸಿಮ್ಯುಲೇಟ್ ಮಾಡಲು ಕೆಳಗಿನ ಸ್ಲೈಡರ್‌ಗಳನ್ನು ಹೊಂದಿಸಿ.',
    hi: 'इंटरैक्टिव क्रॉप सैंडबॉक्स: वास्तविक समय में मिट्टी की नमी, फसल तनाव सूचकांक, रोग दबाव और अनुमानित शुद्ध लाभ का अनुकरण करने के लिए नीचे दिए गए स्लाइडर्स को समायोजित करें।'
  },
  dtControlsTitle: {
    en: 'What-If Simulation Parameters',
    kn: 'ವಾಟ್-ಇಫ್ ಸಿಮ್ಯುಲೇಶನ್ ನಿಯತಾಂಕಗಳು',
    hi: 'व्हाट-इफ सिमुलेशन पैरामीटर्स'
  },
  dtRainfallLabel: {
    en: 'Rainfall Variation:',
    kn: 'ಮಳೆ ವ್ಯತ್ಯಾಸ:',
    hi: 'वर्षा परिवर्तन:'
  },
  dtDrought: { en: '-50% (Drought)', kn: '-50% (ಬರಗಾಲ)', hi: '-50% (सूखा)' },
  dtNormal: { en: 'Normal', kn: 'ಸಾಮಾನ್ಯ', hi: 'सामान्य' },
  dtExcess: { en: '+50% (Excess)', kn: '+50% (ಹೆಚ್ಚುವರಿ)', hi: '+50% (अत्यधिक)' },
  dtSowingShiftLabel: {
    en: 'Sowing Date Shift:',
    kn: 'ಬಿತ್ತನೆ ದಿನಾಂಕ ಬದಲಾವಣೆ:',
    hi: 'बुवाई तिथि में बदलाव:'
  },
  dtEarlyTick: { en: '-20d Early', kn: '-20ದಿನ ಮುಂಚಿತ', hi: '-20दिन पहले' },
  dtZeroTick: { en: '0d', kn: '0ದಿನ', hi: '0दिन' },
  dtLateTick: { en: '+20d Delayed', kn: '+20ದಿನ ತಡವಾಗಿ', hi: '+20दिन देरी' },
  dtOptimalWindow: { en: 'Optimal Window', kn: 'ಸೂಕ್ತ ಬಿತ್ತನೆ ಸಮಯ', hi: 'इष्टतम बुवाई समय' },
  dtDaysLate: { en: 'days late', kn: 'ದಿನ ತಡವಾಗಿ', hi: 'दिन देरी' },
  dtDaysEarly: { en: 'days early', kn: 'ದಿನ ಮುಂಚಿತ', hi: 'दिन पहले' },
  dtFertLabel: {
    en: 'N-P-K Fertilizer Dosage:',
    kn: 'N-P-K ರಸಗೊಬ್ಬರ ಪ್ರಮಾಣ:',
    hi: 'N-P-K उर्वरक खुराक:'
  },
  dtDeficit: { en: '40% (Deficit)', kn: '40% (ಕೊರತೆ)', hi: '40% (कमी)' },
  dtRec: { en: '100% (Rec)', kn: '100% (ಶಿಫಾರಸು)', hi: '100% (अनुशंसित)' },
  dtHigh: { en: '160% (High)', kn: '160% (ಹೆಚ್ಚು)', hi: '160% (अधिक)' },
  dtOfRec: {
    en: '% of recommended',
    kn: '% ಶಿಫಾರಸು ಮಾಡಿದ ಪ್ರಮಾಣದ',
    hi: '% अनुशंसित मात्रा का'
  },
  dtIrrigLabel: {
    en: 'Irrigation Frequency:',
    kn: 'ನೀರಾವರಿ ಆವರ್ತನ:',
    hi: 'सिंचाई की आवृत्ति:'
  },
  dtEvery2: { en: 'Every 2 days', kn: 'ಪ್ರತಿ 2 ದಿನಕ್ಕೊಮ್ಮೆ', hi: 'प्रत्येक 2 दिन' },
  dtEvery7: { en: 'Every 7 days', kn: 'ಪ್ರತಿ 7 ದಿನಕ್ಕೊಮ್ಮೆ', hi: 'प्रत्येक 7 दिन' },
  dtEvery14: { en: 'Every 14 days', kn: 'ಪ್ರತಿ 14 ದಿನಕ್ಕೊಮ್ಮೆ', hi: 'प्रत्येक 14 दिन' },
  dtEveryXDays: {
    en: (d) => `Every ${d} days`,
    kn: (d) => `ಪ್ರತಿ ${d} ದಿನಗಳಿಗೊಮ್ಮೆ`,
    hi: (d) => `प्रत्येक ${d} दिन`
  },
  dtTelemetryTitle: {
    en: 'Simulated Field Telemetry',
    kn: 'ಸಿಮ್ಯುಲೇಟೆಡ್ ಫೀಲ್ಡ್ ಟೆಲಿಮೆಟ್ರಿ',
    hi: 'सिम्युलेटेड फील्ड टेलीमेट्री'
  },
  dtHealthScore: {
    en: 'CROP HEALTH SCORE',
    kn: 'ಬೆಳೆ ಆರೋಗ್ಯ ಸ್ಕೋರ್',
    hi: 'फसल स्वास्थ्य स्कोर'
  },
  dtSoilMoisture: { en: 'Soil Moisture:', kn: 'ಮಣ್ಣಿನ ತೇವಾಂಶ:', hi: 'मिट्टी की नमी:' },
  dtWaterStress: { en: 'Water Stress Index:', kn: 'ನೀರಿನ ಒತ್ತಡ ಸೂಚ್ಯಂಕ:', hi: 'जल तनाव सूचकांक:' },
  dtThermalStress: { en: 'Thermal Stress Index:', kn: 'ಉಷ್ಣ ಒತ್ತಡ ಸೂಚ್ಯಂಕ:', hi: 'तापीय तनाव सूचकांक:' },
  dtPathogenRisk: { en: 'Pathogen / Spore Risk:', kn: 'ರೋಗಾಣು / ಬೀಜಕ ಅಪಾಯ:', hi: 'रोगजनक / बीजाणु जोखिम:' },
  dtProjectedYield: { en: 'Projected Yield', kn: 'ಅಂದಾಜು ಇಳುವರಿ', hi: 'अनुमानित उपज' },
  dtVsBaseline: { en: 'vs baseline', kn: 'ಮೂಲಮಟ್ಟಕ್ಕೆ ಹೋಲಿಸಿದರೆ', hi: 'आधार रेखा की तुलना में' },
  dtQAcre: { en: 'q/acre', kn: 'ಕ್ವಿಂ/ಎಕರೆ', hi: 'क्विं/एकड़' },
  dtGrossRevenue: { en: 'Gross Revenue', kn: 'ಒಟ್ಟು ಆದಾಯ', hi: 'सकल राजस्व' },
  dtEstimatedCost: { en: 'Estimated Input Cost', kn: 'ಅಂದಾಜು ಪರಿಕರ ವೆಚ್ಚ', hi: 'अनुमानित लागत' },
  dtNetProfit: { en: 'Net Projected Profit', kn: 'ಅಂದಾಜು ನಿವ್ವಳ ಲಾಭ', hi: 'अनुमानित शुद्ध लाभ' },
  dtPerAcre: { en: '/ acre', kn: '/ ಎಕರೆ', hi: '/ एकड़' },
  dtComputing: {
    en: 'Computing digital twin dynamics...',
    kn: 'ಡಿಜಿಟಲ್ ಟ್ವಿನ್ ಡೈನಾಮಿಕ್ಸ್ ಲೆಕ್ಕಹಾಕಲಾಗುತ್ತಿದೆ...',
    hi: 'डिजिटल ट्विन सिमुलेशन गणना जारी...'
  },

  // Tab 2: Counterfactual Causal AI
  cfIntro: {
    en: "Structural Causal Inference: Most AI systems only predict the future. SmartAgri's Counterfactual AI analyzes what would have happened if you took a different action in the past, disentangling weather correlation from true causation.",
    kn: "ರಚನಾತ್ಮಕ ಕಾರಣಾತ್ಮಕ ತಾರ್ಕಿಕತೆ (Causal AI): ಹೆಚ್ಚಿನ AI ವ್ಯವಸ್ಥೆಗಳು ಭವಿಷ್ಯವನ್ನು ಮಾತ್ರ ಊಹಿಸುತ್ತವೆ. ಸ್ಮಾರ್ಟ್ಅಗ್ರಿಯ ಕೌಂಟರ್‌ಫ್ಯಾಕ್ಚುಯಲ್ AI ನೀವು ಹಿಂದೆ ಬೇರೆ ಕ್ರಮ ಕೈಗೊಂಡಿದ್ದರೆ ಏನಾಗುತ್ತಿತ್ತು ಎಂಬುದನ್ನು ವಿಶ್ಲೇಷಿಸುತ್ತದೆ.",
    hi: "संरचनात्मक कारणात्मक निष्कर्ष (Causal AI): अधिकांश AI प्रणालियां केवल भविष्य की भविष्यवाणी करती हैं। स्मार्टएग्री का काउंटरफैक्चुअल AI यह विश्लेषण करता है कि यदि आपने अतीत में कोई अलग कदम उठाया होता तो क्या होता।"
  },
  cfTrySample: {
    en: 'Try Sample What-If Queries:',
    kn: 'ಮಾದರಿ "ಏನಾಗುತ್ತಿತ್ತು?" ಪ್ರಶ್ನೆಗಳನ್ನು ಪ್ರಯತ್ನಿಸಿ:',
    hi: 'नमूना "क्या होता?" प्रश्न आज़माएं:'
  },
  cfPreset1Btn: {
    en: '💧 Irrigated 3 days earlier vs Disease',
    kn: '💧 3 ದಿನ ಮುಂಚಿತ ನೀರಾವರಿ vs ರೋಗ',
    hi: '💧 3 दिन पहले सिंचाई vs बीमारी'
  },
  cfPreset1Query: {
    en: 'If I had irrigated 3 days earlier, would my crop disease have been reduced?',
    kn: 'ನಾನು 3 ದಿನ ಮುಂಚಿತವಾಗಿ ನೀರು ಹಾಯಿಸಿದ್ದರೆ, ಬೆಳೆ ರೋಗ ಕಡಿಮೆಯಾಗುತ್ತಿತ್ತೇ?',
    hi: 'यदि मैंने 3 दिन पहले सिंचाई की होती, तो क्या फसल रोग कम हो जाता?'
  },
  cfPreset2Btn: {
    en: '📅 Sown 12 days earlier vs Heat Stress',
    kn: '📅 12 ದಿನ ಮುಂಚಿತ ಬಿತ್ತನೆ vs ಉಷ್ಣ ಒತ್ತಡ',
    hi: '📅 12 दिन पहले बुवाई vs ताप तनाव'
  },
  cfPreset2Query: {
    en: 'If I had sown 12 days earlier, would I have avoided heat stress during grain filling?',
    kn: 'ನಾನು 12 ದಿನ ಮೊದಲೇ ಬಿತ್ತನೆ ಮಾಡಿದ್ದರೆ, ಕಾಳು ತುಂಬುವ ಸಮಯದಲ್ಲಿ ಉಷ್ಣದ ಒತ್ತಡ ತಪ್ಪಿಸಬಹುದಿತ್ತೇ?',
    hi: 'यदि मैंने 12 दिन पहले बुवाई की होती, तो क्या दाना भरने के दौरान ताप तनाव से बचा जा सकता था?'
  },
  cfPreset3Btn: {
    en: '🔬 Prophylactic bio-spray vs Rain Blight',
    kn: '🔬 ಮುನ್ನೆಚ್ಚರಿಕೆ ಜೈವಿಕ ಸಿಂಪಡಣೆ vs ಮಳೆ ರೋಗ',
    hi: '🔬 निवारक बायो-स्प्रे vs बारिश झुलसा'
  },
  cfPreset3Query: {
    en: 'What if I had sprayed bio-fungicide 48 hours before the monsoon rain?',
    kn: 'ಮಳೆ ಬರುವ 48 ಗಂಟೆಗಳ ಮೊದಲು ನಾನು ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಸಿಂಪಡಿಸಿದ್ದರೆ ಏನಾಗುತ್ತಿತ್ತು?',
    hi: 'यदि मैंने मानसूनी बारिश से 48 घंटे पहले जैविक कवकनाशी का छिड़काव किया होता तो क्या होता?'
  },
  cfInputPlaceholder: {
    en: 'Ask any retrospective question: e.g. If I had applied fertilizer in 2 splits instead of 1...',
    kn: 'ಯಾವುದೇ ಹಿಂದಿನ ಪ್ರಶ್ನೆ ಕೇಳಿ: ಉದಾ. 1 ಬಾರಿಯ ಬದಲಿಗೆ 2 ಕಂತುಗಳಲ್ಲಿ ಗೊಬ್ಬರ ನೀಡಿದ್ದರೆ...',
    hi: 'कोई भी प्रश्न पूछें: उदा. यदि मैंने 1 के बजाय 2 बार में उर्वरक डाला होता...'
  },
  cfVoice: { en: 'Voice', kn: 'ಧ್ವನಿ', hi: 'आवाज़' },
  cfListening: { en: 'Listening…', kn: 'ಆಲಿಸುತ್ತಿದೆ…', hi: 'सुन रहा है…' },
  cfAnalysisBtn: { en: 'Causal Analysis', kn: 'ಕಾರಣಾತ್ಮಕ ವಿಶ್ಲೇಷಣೆ', hi: 'कारणात्मक विश्लेषण' },
  cfComputingBtn: { en: 'Computing SCM...', kn: 'ಲೆಕ್ಕಹಾಕಲಾಗುತ್ತಿದೆ...', hi: 'गणना हो रही है...' },
  cfTag: { en: 'Judea Pearl SCM Engine', kn: 'ಜೂಡಿಯಾ ಪರ್ಲ್ SCM ಎಂಜಿನ್', hi: 'जूडिया पर्ल SCM इंजन' },
  cfConfidence: { en: 'Confidence:', kn: 'ವಿಶ್ವಾಸಾರ್ಹತೆ:', hi: 'विश्वास:' },
  cfAssessment: {
    en: 'Causal Counterfactual Assessment',
    kn: 'ಕಾರಣಾತ್ಮಕ ಕೌಂಟರ್‌ಫ್ಯಾಕ್ಚುಯಲ್ ಮೌಲ್ಯಮಾಪನ',
    hi: 'कारणात्मक काउंटरफैक्चुअल मूल्यांकन'
  },
  cfFactualTitle: {
    en: 'Factual Reality (Observed History)',
    kn: 'ಗಮನಿಸಿದ ವಾಸ್ತವ ಇತಿಹಾಸ (Factual Reality)',
    hi: 'देखी गई वास्तविक स्थिति (Factual Reality)'
  },
  cfTarget: { en: 'Target:', kn: 'ಗುರಿ:', hi: 'लक्ष्य:' },
  cfFactualDesc: {
    en: 'Standard field management followed with post-outbreak intervention.',
    kn: 'ರೋಗ ಬಂದ ನಂತರ ಪ್ರಮಾಣಿತ ಕ್ಷೇತ್ರ ನಿರ್ವಹಣೆಯನ್ನು ಅನುಸರಿಸಲಾಗಿದೆ.',
    hi: 'रोग के बाद मानक प्रबंधन लागू किया गया।'
  },
  cfCounterfactualTitle: {
    en: 'Counterfactual Simulation',
    kn: 'ಕೌಂಟರ್‌ಫ್ಯಾಕ್ಚುಯಲ್ ಸಿಮ್ಯುಲೇಶನ್',
    hi: 'काउंटरफैक्चुअल सिमुलेशन'
  },
  cfIntervention: { en: 'Intervention:', kn: 'ಹಸ್ತಕ್ಷೇಪ ಕ್ರಮ:', hi: 'हस्तक्षेप कदम:' },
  cfCounterfactualDesc: {
    en: 'Evaluated against microclimate humidity, spore load, and moisture stress curves.',
    kn: 'ಸೂಕ್ಷ್ಮ ಹವಾಮಾನ, ಆರ್ದ್ರತೆ, ಬೀಜಕ ಸಾಂದ್ರತೆ ಮತ್ತು ತೇವಾಂಶ ವಕ್ರರೇಖೆಗಳ ವಿರುದ್ಧ ಮೌಲ್ಯಮಾಪನ ಮಾಡಲಾಗಿದೆ.',
    hi: 'सूक्ष्म जलवायु, आर्द्रता, बीजाणु घनत्व और नमी वक्र के विरुद्ध मूल्यांकन किया गया।'
  },

  // Tab 3: Multi-Agent Debate
  debateIntro: {
    en: '5-Agent Expert Consultation: Instead of relying on a single AI model, five specialized autonomous agents (Agronomist, Market Economist, Plant Pathologist, Smart Irrigation Specialist, and Risk Officer) actively debate to forge a balanced, foolproof recommendation.',
    kn: '5-ತಜ್ಞ ಏಜೆಂಟ್‌ಗಳ ಸಮಾಲೋಚನೆ: ಕೇವಲ ಒಂದೇ AI ಮಾದರಿಯನ್ನು ಅವಲಂಬಿಸುವ ಬದಲು, ಐದು ವಿಶೇಷ ಸ್ವಾಯತ್ತ ಏಜೆಂಟ್‌ಗಳು (ಕೃಷಿ ತಜ್ಞ, ಮಾರುಕಟ್ಟೆ ಅರ್ಥಶಾಸ್ತ್ರಜ್ಞ, ಸಸ್ಯ ರೋಗಶಾಸ್ತ್ರಜ್ಞ, ಸ್ಮಾರ್ಟ್ ನೀರಾವರಿ ತಜ್ಞ ಮತ್ತು ಅಪಾಯ ನಿಯಂತ್ರಕ) ಪರಸ್ಪರ ಚರ್ಚಿಸಿ ಸಮತೋಲಿತ ಮತ್ತು ವಿಶ್ವಾಸಾರ್ಹ ಶಿಫಾರಸು ನೀಡುತ್ತಾರೆ.',
    hi: '5-विशेषज्ञ एजेंट परामर्श: केवल एक AI मॉडल पर निर्भर रहने के बजाय, पांच स्वायत्त विशेषज्ञ एजेंट (कृषि विज्ञानी, बाजार अर्थशास्त्री, पादप रोग विज्ञानी, स्मार्ट सिंचाई विशेषज्ञ और जोखिम अधिकारी) मिलकर बहस करते हैं और एक संतुलित व सटीक सलाह तैयार करते हैं।'
  },
  debateReconvene: {
    en: 'Re-Convene Expert Debate',
    kn: '🔄 ತಜ್ಞರ ಚರ್ಚೆಯನ್ನು ಮರು-ಆರಂಭಿಸಿ',
    hi: '🔄 विशेषज्ञों की बहस पुनः प्रारंभ करें'
  },
  debateDebating: {
    en: '⚡ Agents Debating...',
    kn: '⚡ ಏಜೆಂಟ್‌ಗಳು ಚರ್ಚಿಸುತ್ತಿದ್ದಾರೆ...',
    hi: '⚡ एजेंट बहस कर रहे हैं...'
  },
  roleAgronomist: {
    en: 'Lead Agronomist',
    kn: 'ಮುಖ್ಯ ಕೃಷಿ ವಿಜ್ಞಾನಿ',
    hi: 'प्रमुख कृषि वैज्ञानिक'
  },
  roleEconomist: {
    en: 'APMC Market Economist',
    kn: 'APMC ಮಾರುಕಟ್ಟೆ ಅರ್ಥಶಾಸ್ತ್ರಜ್ಞ',
    hi: 'APMC बाज़ार अर्थशास्त्री'
  },
  rolePathologist: {
    en: 'Senior Plant Pathologist',
    kn: 'ಹಿರಿಯ ಸಸ್ಯ ರೋಗಶಾಸ್ತ್ರಜ್ಞೆ',
    hi: 'वरिष्ठ पादप रोग विशेषज्ञ'
  },
  roleIrrigation: {
    en: 'Smart Irrigation & Hydrology Specialist',
    kn: 'ಸ್ಮಾರ್ಟ್ ನೀರಾವರಿ ಮತ್ತು ಜಲವಿಜ್ಞಾನ ತಜ್ಞ',
    hi: 'स्मार्ट सिंचाई एवं जलविज्ञान विशेषज्ञ'
  },
  roleRisk: {
    en: 'Farm Credit & Risk Officer',
    kn: 'ಕೃಷಿ ಸಾಲ ಮತ್ತು ಅಪಾಯ ಅಧಿಕಾರಿ',
    hi: 'कृषि ऋण एवं जोखिम अधिकारी'
  },
  debateTyping: {
    en: '🌾 Dr. Rao, 📈 Sharmaji, 🔬 Dr. Tara, 💧 Er. Kulkarni & 🛡️ Patil are reviewing field telemetry...',
    kn: '🌾 ಡಾ. ರಾವ್, 📈 ಶರ್ಮಾಜಿ, 🔬 ಡಾ. ತಾರಾ, 💧 ಇಂ. ಕುಲಕರ್ಣಿ ಮತ್ತು 🛡️ ಪಾಟೀಲ್ ಫೀಲ್ಡ್ ಟೆಲಿಮೆಟ್ರಿ ಪರಿಶೀಲಿಸುತ್ತಿದ್ದಾರೆ...',
    hi: '🌾 डॉ. राव, 📈 शर्माजी, 🔬 डॉ. तारा, 💧 ईं. कुलकर्णी और 🛡️ पाटिल फील्ड टेलीमेट्री की समीक्षा कर रहे हैं...'
  },
  debateConsensusTitle: {
    en: 'Synthesized Unanimous Consensus Strategy',
    kn: '🏆 ಸರ್ವಾನುಮತದ ಒಮ್ಮತದ ಕಾರ್ಯತಂತ್ರ',
    hi: '🏆 सर्वसम्मत आम सहमति रणनीति'
  },
  debateTakeawaysTitle: {
    en: 'Key Action Protocols Agreed by All 5 Agents:',
    kn: '📋 ಎಲ್ಲಾ 5 ತಜ್ಞರು ಒಪ್ಪಿದ ಪ್ರಮುಖ ಕ್ರಿಯಾ ಕ್ರಮಗಳು:',
    hi: '📋 सभी 5 विशेषज्ञों द्वारा स्वीकृत प्रमुख कार्य बिंदु:'
  },

  // Tab 4: Regret Minimization Framework
  regretIntro: {
    en: 'Minimax Regret Decision Framework: A single crop failure can ruin a smallholder farmer. Our Regret Minimization Agent evaluates worst-case downside financial scenarios across weather shocks, pest outbreaks, and market crashes to deliver the least-regret strategic choice.',
    kn: 'ಮಿನಿಮ್ಯಾಕ್ಸ್ ರಿಗ್ರೆಟ್ (ವಿಷಾದ ಕನಿಷ್ಠೀಕರಣ) ಚೌಕಟ್ಟು: ಒಂದೇ ಬೆಳೆ ವೈಫಲ್ಯ ಸಣ್ಣ ರೈತನನ್ನು ಸಂಕಷ್ಟಕ್ಕೆ ತಳ್ಳಬಹುದು. ಕೆಟ್ಟ ಹವಾಮಾನ, ಕೀಟಬಾಧೆ ಮತ್ತು ಮಾರುಕಟ್ಟೆ ಕುಸಿತದ ಸಂದರ್ಭದಲ್ಲೂ ಕಡಿಮೆ ನಷ್ಟವಾಗುವ ಮತ್ತು ಗರಿಷ್ಠ ಸುರಕ್ಷತೆ ನೀಡುವ ಯೋಜನೆಯನ್ನು ಇದು ಆಯ್ಕೆ ಮಾಡುತ್ತದೆ.',
    hi: 'मिनीमैक्स रिग्रेट निर्णय ढांचा: एक फसल की विफलता छोटे किसान को संकट में डाल सकती है। हमारा रिग्रेट न्यूनीकरण एजेंट खराब मौसम, कीट प्रकोप और बाजार गिरावट में सबसे कम जोखिम वाली योजना का चयन करता है।'
  },
  regretPostureLabel: {
    en: 'Select Farmer Risk Posture:',
    kn: '🎯 ರೈತರ ಅಪಾಯದ ಆದ್ಯತೆಯನ್ನು ಆರಿಸಿ:',
    hi: '🎯 किसान की जोखिम वरीयता चुनें:'
  },
  riskSafe: {
    en: '🔵 Safe Plan (Defensive / Capital Preservation)',
    kn: '🔵 ಸುರಕ್ಷಿತ ಯೋಜನೆ (ಬಂಡವಾಳ ರಕ್ಷಣೆ)',
    hi: '🔵 सुरक्षित योजना (पूंजी सुरक्षा)'
  },
  riskBalanced: {
    en: '🟡 Balanced Plan (Optimal Hedging & Sharpe Ratio)',
    kn: '🟡 ಸಮತೋಲಿತ ಯೋಜನೆ (ಸೂಕ್ತ ಅಪಾಯ ನಿರ್ವಹಣೆ)',
    hi: '🟡 संतुलित योजना (इष्टतम जोखिम प्रबंधन)'
  },
  riskAggressive: {
    en: '🟢 Aggressive Plan (Peak Upside Alpha)',
    kn: '🟢 ಆಕ್ರಮಣಕಾರಿ ಯೋಜನೆ (ಗರಿಷ್ಠ ಲಾಭದ ಗುರಿ)',
    hi: '🟢 आक्रामक योजना (अधिकतम लाभ लक्ष्य)'
  },
  badgeDefensive: { en: '🔵 DEFENSIVE', kn: '🔵 ಸುರಕ್ಷಿತ / ರಕ್ಷಣಾತ್ಮಕ', hi: '🔵 सुरक्षित' },
  badgeSharpe: { en: '🟡 OPTIMAL SHARPE', kn: '🟡 ಸಮತೋಲಿತ', hi: '🟡 संतुलित' },
  badgeAlpha: { en: '🟢 HIGH ALPHA', kn: '🟢 ಹೆಚ್ಚಿನ ಆದಾಯ', hi: '🟢 उच्च लाभ' },
  regretExpectedProfit: {
    en: 'Expected Net Profit / Acre',
    kn: 'ಅಂದಾಜು ನಿವ್ವಳ ಲಾಭ / ಎಕರೆ',
    hi: 'अनुमानित शुद्ध लाभ / एकड़'
  },
  regretVariety: {
    en: 'Recommended Variety:',
    kn: 'ಶಿಫಾರಸು ಮಾಡಿದ ತಳಿ:',
    hi: 'अनुशंसित किस्म:'
  },
  regretDownside: {
    en: 'Worst-Case Downside:',
    kn: 'ಅತ್ಯಂತ ಕೆಟ್ಟ ಪರಿಸ್ಥಿತಿಯ ನಷ್ಟ:',
    hi: 'सबसे खराब स्थिति का नुकसान:'
  },
  regretCapital: {
    en: 'Capital Outlay:',
    kn: 'ಬಂಡವಾಳ ವೆಚ್ಚ:',
    hi: 'पूंजीगत व्यय:'
  },
  regretStrategy: {
    en: 'Core Strategy:',
    kn: 'ಮುಖ್ಯ ಕಾರ್ಯತಂತ್ರ:',
    hi: 'मुख्य रणनीति:'
  },
  regretScore: {
    en: 'Savage Regret:',
    kn: 'ವಿಷಾದ ಅಂಕ (Savage Regret):',
    hi: 'रिग्रेट स्कोर:'
  },
  regretLoading: {
    en: 'Loading Regret Matrix models...',
    kn: 'ರಿಗ್ರೆಟ್ ಮ್ಯಾಟ್ರಿಕ್ಸ್ ಮಾದರಿಗಳನ್ನು ಲೋಡ್ ಮಾಡಲಾಗುತ್ತಿದೆ...',
    hi: 'रिग्रेट मैट्रिक्स मॉडल लोड हो रहे हैं...'
  },
  stressTableTitle: {
    en: 'Macro Stress-Test Scenario Payoff Matrix',
    kn: 'ಸ್ಥೂಲ ಒತ್ತಡ-ಪರೀಕ್ಷಾ ಸನ್ನಿವೇಶದ ಪೇ-ಆಫ್ ಮ್ಯಾಟ್ರಿಕ್ಸ್',
    hi: 'मैक्रो स्ट्रेस-टेस्ट परिदृश्य पेऑफ मैट्रिक्स'
  },
  thScenario: {
    en: 'Seasonal Scenario',
    kn: 'ಹವಾಮಾನ / ಮಾರುಕಟ್ಟೆ ಸನ್ನಿವೇಶ',
    hi: 'मौसमी परिदृश्य'
  },
  thSafe: {
    en: '🔵 Safe Plan Net Gain',
    kn: '🔵 ಸುರಕ್ಷಿತ ಯೋಜನೆಯ ನಿವ್ವಳ ಲಾಭ',
    hi: '🔵 सुरक्षित योजना शुद्ध लाभ'
  },
  thBalanced: {
    en: '🟡 Balanced Plan Net Gain',
    kn: '🟡 ಸಮತೋಲಿತ ಯೋಜನೆಯ ನಿವ್ವಳ ಲಾಭ',
    hi: '🟡 संतुलित योजना शुद्ध लाभ'
  },
  thAggressive: {
    en: '🟢 Aggressive Plan Net Gain',
    kn: '🟢 ಆಕ್ರಮಣಕಾರಿ ಯೋಜನೆಯ ನಿವ್ವಳ ಲಾಭ',
    hi: '🟢 आक्रामक योजना शुद्ध लाभ'
  }
};

export default function DecisionIntelligenceSection({ moduleState = {} }) {
  const { t, lang } = useLanguage();
  const [activeTab, setActiveTab] = useState('digital_twin');

  const { recommendedCrop, city, predictedDisease, predictedPrice } = moduleState;
  const currentCrop = recommendedCrop || 'Rice';
  const currentDistrict = city || 'Dharwad';

  const localizedCropName = getCropName(currentCrop, lang) || currentCrop;

  const loc = (key, arg) => {
    const item = DI_TEXTS[key];
    if (!item) return key;
    const val = item[lang] || item.en;
    if (typeof val === 'function') return val(arg);
    return val;
  };

  // ====================================================
  // 1. DIGITAL TWIN SIMULATOR STATE
  // ====================================================
  const [simParams, setSimParams] = useState({
    crop: currentCrop,
    rainfall_delta_pct: 0,
    sowing_shift_days: 0,
    fertilizer_pct: 100,
    irrigation_frequency_days: 7
  });

  const [simResult, setSimResult] = useState(null);
  const [simLoading, setSimLoading] = useState(false);

  useEffect(() => {
    setSimParams((prev) => ({ ...prev, crop: currentCrop }));
  }, [currentCrop]);

  useEffect(() => {
    let cancel = false;
    async function runSim() {
      setSimLoading(true);
      try {
        const res = await api.simulateDigitalTwin({
          ...simParams,
          district: currentDistrict
        });
        if (!cancel && res && res.data) {
          setSimResult(res.data);
        }
      } catch (e) {
        console.error('Digital Twin simulation error:', e);
      } finally {
        if (!cancel) setSimLoading(false);
      }
    }
    const timer = setTimeout(runSim, 250);
    return () => {
      cancel = true;
      clearTimeout(timer);
    };
  }, [simParams, currentDistrict]);

  // ====================================================
  // 2. COUNTERFACTUAL CAUSAL AI STATE
  // ====================================================
  const [cfQuery, setCfQuery] = useState(loc('cfPreset1Query'));
  const [cfResult, setCfResult] = useState(null);
  const [cfLoading, setCfLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);

  // Sync default counterfactual query when language changes
  useEffect(() => {
    setCfQuery(loc('cfPreset1Query'));
  }, [lang]);

  async function handleRunCounterfactual(queryText) {
    const q = queryText || cfQuery;
    if (!q || !q.trim()) return;
    setCfLoading(true);
    try {
      const res = await api.simulateCounterfactual({
        query: q,
        crop: currentCrop,
        disease: predictedDisease,
        district: currentDistrict,
        lang: lang
      });
      setCfResult(res);
    } catch (err) {
      setCfResult({
        status: 'error',
        explanation: lang === 'kn'
          ? 'ಕಾರಣಾತ್ಮಕ ವಿಶ್ಲೇಷಣೆ ಲೆಕ್ಕಹಾಕಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೊಮ್ಮೆ ಪ್ರಯತ್ನಿಸಿ.'
          : lang === 'hi'
            ? 'कारणात्मक विश्लेषण की गणना नहीं की जा सकी। कृपया पुनः प्रयास करें।'
            : 'Could not compute counterfactual inference. Please check if backend is running.'
      });
    } finally {
      setCfLoading(false);
    }
  }

  function startVoiceInput() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert(lang === 'kn'
        ? 'ಈ ಬ್ರೌಸರ್‌ನಲ್ಲಿ ಧ್ವನಿ ಗುರುತಿಸುವಿಕೆ ಬೆಂಬಲಿತವಾಗಿಲ್ಲ. ದಯವಿಟ್ಟು ಗೂಗಲ್ ಕ್ರೋಮ್ ಬಳಸಿ.'
        : lang === 'hi'
          ? 'इस ब्राउज़र में स्पीच रिकग्निशन समर्थित नहीं है। कृपया गूगल क्रोम का उपयोग करें।'
          : 'Speech recognition is not supported in this browser. Please use Google Chrome or Edge.');
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = lang.startsWith('kn') ? 'kn-IN' : lang.startsWith('hi') ? 'hi-IN' : 'en-US';
    recognition.interimResults = false;

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setCfQuery(transcript);
      handleRunCounterfactual(transcript);
    };
    recognition.start();
  }

  // ====================================================
  // MULTILINGUAL AGENT & DEBATE FALLBACK TRANSLATORS
  // ====================================================
  const TAKEAWAYS_MAP = {
    kn: [
      'ಪೋಷಕಾಂಶ ಸೋರಿಕೆ ತಡೆಯಲು ಹನಿ ನೀರಾವರಿ ಮೂಲಕ ಕಂತುಗಳಲ್ಲಿ ಸಾರಜನಕ ಗೊಬ್ಬರ ನೀಡಿ',
      'ಬಿತ್ತನೆಗೆ ಮುನ್ನ ಟ್ರೈಕೋಡರ್ಮಾ ಜೈವಿಕ ಬೀಜೋಪಚಾರ ಕಡ್ಡಾಯವಾಗಿ ಮಾಡಿ',
      'ಬೆಳೆ ನೀರಿನ ಆವಿಯಾಗುವಿಕೆ (ETc) ಆಧಾರದ ಮೇಲೆ ನೀರಾವರಿ ನೀಡಿ, ಮಳೆಯಾದಾಗ ನೀರು ಹಾಯಿಸಬೇಡಿ',
      'ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ಬೆಲೆ ಕುಸಿತ ತಪ್ಪಿಸಲು 7-10 ದಿನಗಳ ಅಂತರದಲ್ಲಿ ಹಂತಹಂತವಾಗಿ ಕೊಯ್ಲು ಮಾಡಿ',
      '20% ದ್ವಿದಳ ಧಾನ್ಯದ ಅಂತರಬೆಳೆ ಬೆಳೆಯುವ ಮೂಲಕ ಆರ್ಥಿಕ ಭದ್ರತೆ ಕಾಪಾಡಿಕೊಳ್ಳಿ'
    ],
    hi: [
      'पोषक तत्वों की बर्बादी रोकने के लिए ड्रिप फर्टिगेशन द्वारा किस्तों में नाइट्रोजन दें',
      'बुवाई से पहले ट्राइकोडर्मा विरिडी से जैविक बीज उपचार अवश्य करें',
      'दैनिक वाष्पोत्सर्जन (ETc) के आधार पर सिंचाई करें और बारिश होने पर सिंचाई रोकें',
      'मंडी में भाव गिरने से बचने के लिए 7-10 दिनों के अंतराल में चरणबद्ध कटाई करें',
      '20% क्षेत्र में दलहनी अंतःफसल लगाकर वित्तीय सुरक्षा कवच बनाएं'
    ]
  };

  function localizeTurnStatement(turn) {
    if (!turn) return '';
    const st = turn.statement || '';
    if (lang === 'en') return st;

    const id = turn.agent_id;
    if (lang === 'kn') {
      if (id === 'agronomist') {
        return `${currentDistrict} ಜಿಲ್ಲೆಯಲ್ಲಿ ${localizedCropName} ಬೆಳೆಗೆ 25+ ಕ್ವಿಂಟಾಲ್ ಅಧಿಕ ಇಳುವರಿ ಸಾಧಿಸಲು ಸಮತೋಲಿತ 120:60:40 NPK ರಸಗೊಬ್ಬರ ಪ್ರಮಾಣ ಮತ್ತು ಸಾಲು-ಬದು (Ridge & Furrow) ಬಿತ್ತನೆ ಪದ್ಧತಿ ಅತ್ಯಗತ್ಯ.`;
      }
      if (id === 'economist') {
        return `ಡಾ. ರಾವ್ ಅವರೇ ಸ್ವಲ್ಪ ನಿಲ್ಲಿ, ${currentDistrict} ಜಿಲ್ಲೆಯ ಎಲ್ಲ ರೈತರು ಒಟ್ಟಿಗೆ ಕೊಯ್ಲು ಮಾಡಿದರೆ ಸ್ಥಳೀಯ APMC ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ಬೆಲೆ ಕುಸಿತ ಉಂಟಾಗುತ್ತದೆ. ಆದ್ದರಿಂದ ಬೇಗ ಕೊಯ್ಲು ಅಥವಾ ಕಣಜದಲ್ಲಿ ಸುರಕ್ಷಿತ ದಾಸ್ತಾನಿಗೆ ಯೋಜನೆ ರೂಪಿಸಬೇಕು.`;
      }
      if (id === 'pathologist') {
        return `ಅಕ್ಟೋಬರ್-ನವೆಂಬರ್ ತೇವಾಂಶವು ಶಿಲೀಂಧ್ರ ರೋಗ ಮತ್ತು ರಸಹೀರುವ ಕೀಟಗಳ ಅಪಾಯವನ್ನು ಹೆಚ್ಚಿಸುತ್ತದೆ. ಅತಿಯಾದ ಸಾರಜನಕವು ಬೆಳೆಯನ್ನು ರೋಗಕ್ಕೆ ತುತ್ತಾಗಿಸುತ್ತದೆ. ಟ್ರೈಕೋಡರ್ಮಾ ಬೀಜೋಪಚಾರ ಮತ್ತು ಬೇವಿನ ಎಣ್ಣೆ ಸಿಂಪಡಣೆಯನ್ನು ಕಡ್ಡಾಯಗೊಳಿಸಬೇಕು.`;
      }
      if (id === 'irrigation_specialist') {
        return `ಬೇರು ಕೊಳೆಯುವಿಕೆ ಮತ್ತು ಶಿಲೀಂಧ್ರ ಹರಡುವಿಕೆಯನ್ನು ತಡೆಯಲು, ದಿನದ ETc ಆಧಾರದ ಮೇಲೆ ಬೆಳಗಿನ ವೇಳೆಯಲ್ಲೇ ಹನಿ ನೀರಾವರಿ ಒದಗಿಸಬೇಕು. ಮಳೆಯು 5ಮಿ.ಮೀ ಮೀರಿದಾಗ 24-48 ಗಂಟೆಗಳ ಕಾಲ ನೀರು ಹಾಯಿಸುವುದನ್ನು ತಕ್ಷಣ ಸ್ಥಗಿತಗೊಳಿಸಬೇಕು.`;
      }
      if (id === 'risk_officer') {
        return `ನಾನು ಡಾ. ತಾರಾ, ಶರ್ಮಾಜಿ ಮತ್ತು ಕುಲಕರ್ಣಿ ಅವರ ಮಾತನ್ನು ಬೆಂಬಲಿಸುತ್ತೇನೆ. ರೈತರ ಬಂಡವಾಳ ರಕ್ಷಣೆಯಾಗಬೇಕು. ಹನಿ ನೀರಾವರಿ ಮೂಲಕ ರಸಗೊಬ್ಬರ ನೀಡುವುದರಿಂದ 40% ವೆಚ್ಚ ಉಳಿತಾಯವಾಗುತ್ತದೆ ಮತ್ತು 20% ವಿಸ್ತೀರ್ಣದಲ್ಲಿ ದ್ವಿದಳ ಧಾನ್ಯದ ಅಂತರಬೆಳೆ ಬೆಳೆಯುವುದರಿಂದ ಮಾರುಕಟ್ಟೆ ನಷ್ಟಕ್ಕೆ ವಿಮೆ ದೊರೆತಂತಾಗುತ್ತದೆ.`;
      }
    } else if (lang === 'hi') {
      if (id === 'agronomist') {
        return `${currentDistrict} में ${localizedCropName} की 25+ क्विंटल बंपर पैदावार के लिए संतुलित 120:60:40 NPK उर्वरक और मेड़-कूड़ विधि से समय पर बुवाई आवश्यक है।`;
      }
      if (id === 'economist') {
        return `डॉ. राव, थोड़ा रुकिए, यदि ${currentDistrict} के सभी किसान एक साथ फसल काटते हैं तो स्थानीय APMC मंडी में आवक बढ़ने से भाव गिर जाएंगे। हमें अगेती कटाई या खेत पर हवादार भंडारण की योजना बनानी चाहिए।`;
      }
      if (id === 'pathologist') {
        return `यह न भूलें कि मौसम की नमी से फफूंद जनित रोगों और रस चूसक कीटों का खतरा बढ़ जाता है। अत्यधिक नाइट्रोजन से पत्तियां कोमल होकर रोग की चपेट में आ सकती हैं। ट्राइकोडर्मा बीज उपचार और नीम का छिड़काव अनिवार्य है।`;
      }
      if (id === 'irrigation_specialist') {
        return `जड़ों में सड़न रोकने के लिए दैनिक ETc नमी खपत के अनुसार केवल सुबह के समय ड्रिप से पानी दें, और 5 मिमी से अधिक वर्षा होने पर 24-48 घंटे तक सिंचाई तुरंत रोकें।`;
      }
      if (id === 'risk_officer') {
        return `मैं डॉ. तारा, शर्माजी और कुलकर्णी जी से सहमत हूं। किसान की लागत सुरक्षित रहनी चाहिए। ड्रिप फर्टिगेशन से 40% खाद खर्च बचता है और 20% रकबे में दलहनी अंतःफसल लगाने से बाजार जोखिम का बीमा मिल जाता है।`;
      }
    }
    return st;
  }

  function localizeConsensusSummary(summary) {
    if (!summary) return '';
    if (lang === 'en') return summary;

    if (lang === 'kn') {
      if (summary.includes('5 expert agents') || summary.includes('unanimously agree') || !/[\u0C80-\u0CFF]/.test(summary) || /[\u0900-\u097F]/.test(summary)) {
        return `5 ತಜ್ಞ ಏಜೆಂಟ್‌ಗಳು ${localizedCropName} ಬೆಳೆಗೆ ಸಮಗ್ರ ಸ್ಮಾರ್ಟ್ ಕೃಷಿ ಶಿಷ್ಟಾಚಾರಕ್ಕೆ ಸರ್ವಾನುಮತದಿಂದ ಒಪ್ಪಿಗೆ ನೀಡಿದ್ದಾರೆ: ನೀರು-ಗೊಬ್ಬರ ಉಳಿಸಲು ಹನಿ ನೀರಾವರಿ (Fertigation), ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಬೀಜೋಪಚಾರ, ಮಳೆ-ಆಧಾರಿತ ನೀರಾವರಿ ನಿಯಂತ್ರಣ, ಮತ್ತು APMC ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಕುಸಿತ ತಪ್ಪಿಸಲು ಹಂತಹಂತದ ಕೊಯ್ಲು.`;
      }
    } else if (lang === 'hi') {
      if (summary.includes('5 expert agents') || summary.includes('unanimously agree') || !/[\u0900-\u097F]/.test(summary) || /[\u0C80-\u0CFF]/.test(summary)) {
        return `पांचों विशेषज्ञ एजेंट ${localizedCropName} के लिए एकीकृत स्मार्ट कृषि प्रोटोकॉल पर सर्वसम्मति से सहमत हैं: पानी और खाद बचाने के लिए ड्रिप फर्टिगेशन, बायो-फंगीसाइड बीज उपचार, मौसम आधारित सिंचाई नियंत्रण और APMC मंडी में भाव गिरने से बचने के लिए चरणबद्ध कटाई।`;
      }
    }
    return summary;
  }

  function localizeTakeaway(item, idx) {
    if (lang === 'en') return item;
    const list = TAKEAWAYS_MAP[lang];
    if (list && list[idx]) return list[idx];
    return item;
  }

  function localizeExplanation(explanation) {
    if (!explanation) return '';
    if (lang === 'en') return explanation;

    let text = explanation;
    if (lang === 'kn') {
      text = text
        .replace(/### \*\*1\. Step 1: Abduction.*?\*\*/gi, '### **1. ಹಂತ 1: ಅಬ್ಡಕ್ಷನ್ (ಅಗೋಚರ ಪರಿಸ್ಥಿತಿಗಳ ಪತ್ತೆ)**')
        .replace(/### \*\*2\. Step 2: Action.*?\*\*/gi, '### **2. ಹಂತ 2: ಕ್ರಿಯೆ (ಕಾರಣಾತ್ಮಕ ಹಸ್ತಕ್ಷೇಪ do(·))**')
        .replace(/### \*\*3\. Step 3: Prediction.*?\*\*/gi, '### **3. ಹಂತ 3: ಭವಿಷ್ಯ ನುಡಿ (ಕೌಂಟರ್‌ಫ್ಯಾಕ್ಚುಯಲ್ ಫಲಿತಾಂಶ ಲೆಕ್ಕಾಚಾರ)**')
        .replace(/### \*\*Summary of Counterfactual Outcome\*\*/gi, '### **ಕೌಂಟರ್‌ಫ್ಯಾಕ್ಚುಯಲ್ ಫಲಿತಾಂಶದ ಸಾರಾಂಶ**')
        .replace(/### \*\*The Trade-Off Analysis\*\*/gi, '### **ವ್ಯತ್ಯಾಸ ಮತ್ತು ತುಲನಾತ್ಮಕ ವಿಶ್ಲೇಷಣೆ**')
        .replace(/### \*\*Probabilistic Confidence Percentage\*\*/gi, '### **ಸಂಭಾವ್ಯತೆಯ ವಿಶ್ವಾಸಾರ್ಹತೆ ಶೇಕಡಾವಾರು**')
        .replace(/\| Parameter \| Observed Reality \| Counterfactual Action \|/gi, '| ನಿಯತಾಂಕ | ಗಮನಿಸಿದ ವಾಸ್ತವ | ಕೌಂಟರ್‌ಫ್ಯಾಕ್ಚುಯಲ್ ಕ್ರಮ |')
        .replace(/\| Parameter \| Observed History \| Counterfactual Adjustment \|/gi, '| ನಿಯತಾಂಕ | ಗಮನಿಸಿದ ವಾಸ್ತವ | ಕೌಂಟರ್‌ಫ್ಯಾಕ್ಚುಯಲ್ ಹೊಂದಾಣಿಕೆ |')
        .replace(/\| Parameter \| Observed \(Flood Irrigation\) \| Counterfactual \(Drip Irrigation\) \|/gi, '| ನಿಯತಾಂಕ | ಗಮನಿಸಿದ ವಾಸ್ತವ (ಹರಿವು ನೀರಾವರಿ) | ಕೌಂಟರ್‌ಫ್ಯಾಕ್ಚುಯಲ್ (ಹನಿ ನೀರಾವರಿ) |')
        .replace(/\| \*\*Resource Efficiency\*\* \| Standard baseline \| Optimized input delivery \|/gi, '| **ಸಂಪನ್ಮೂಲ ದಕ್ಷತೆ** | ಸಾಮಾನ್ಯ ಮೂಲಮಟ್ಟ | ಅತ್ಯುತ್ತಮ ಪರಿಕರ ನಿರ್ವಹಣೆ |')
        .replace(/\| \*\*Moisture Stress\*\* \| Moderate \| Alleviated by 30% \|/gi, '| **ತೇವಾಂಶದ ಒತ್ತಡ** | ಸಾಧಾರಣ | 30% ರಷ್ಟು ಇಳಿಕೆ |')
        .replace(/\| \*\*Canopy Microclimate\*\* \| Dry \| Slightly elevated night RH \|/gi, '| **ಮೇಲ್ಮೈ ಸೂಕ್ಷ್ಮ ಹವಾಮಾನ** | ಒಣಗಿದ ಸ್ಥಿತಿ | ರಾತ್ರಿಯ ಆರ್ದ್ರತೆ ಕೊಂಚ ಏರಿಕೆ |')
        .replace(/\| \*\*Water Application Efficiency\*\* \|.*?\| \*\*85% - 92%.*?\*\* \|/gi, '| **ನೀರಿನ ಬಳಕೆಯ ದಕ್ಷತೆ** | 40% - 50% (ಹೆಚ್ಚು ಸೋರಿಕೆ/ವ್ಯರ್ಥ) | **85% - 92% (ನೇರ ಬೇರಿಗೆ ತಲುಪುವಿಕೆ)** |')
        .replace(/\| \*\*Root Aeration & Nutrient Leaching\*\* \|.*?\| Continuous optimal aeration & fertigation \|/gi, '| **ಬೇರಿನ ಆಮ್ಲಜನಕ & ಪೋಷಕಾಂಶ** | ಕಾಲಕಾಲಕ್ಕೆ ಜಲಾವೃತ & N ಸೋರಿಕೆ | ನಿರಂತರ ಗರಿಷ್ಠ ಗಾಳಿಯಾಡುವಿಕೆ & ಫರ್ಟಿಗೇಷನ್ |')
        .replace(/\| \*\*Weed Growth & Inter-row Labor\*\* \|.*?\| Low \(Only cane row wetted\) \|/gi, '| **ಕಳೆ ಬೆಳವಣಿಗೆ & ಕೂಲಿ ವೆಚ್ಚ** | ಹೆಚ್ಚು (ಇಡೀ ಜಮೀನು ತೇವ) | ಕಡಿಮೆ (ಕೇವಲ ಸಾಲಿನ ಜಾಗ ಮಾತ್ರ ತೇವ) |')
        .replace(/\| \*\*Net Cane Yield & Profit\*\* \|.*?\| \*\*.*?higher yield per acre\*\* \|/gi, '| **ನಿವ್ವಳ ಇಳುವರಿ & ಲಾಭ** | ಮೂಲಮಟ್ಟ | **+18% ರಿಂದ +25% ಅಧಿಕ ಇಳುವರಿ/ಎಕರೆ** |')
        .replace(/Background baseline conditions for .*? in .*?\./gi, `${currentDistrict} ಜಿಲ್ಲೆಯಲ್ಲಿ ${localizedCropName} ಬೆಳೆಗೆ ಹಿನ್ನೆಲೆ ವಾಸ್ತವಿಕ ಪರಿಸ್ಥಿತಿಗಳು.`)
        .replace(/Reconstructing background moisture tension and fungal spore presence.*?for .*? in .*?\./gi, `${currentDistrict} ಜಿಲ್ಲೆಯಲ್ಲಿ ${localizedCropName} ಬೆಳೆಗೆ ವಾಸ್ತವಿಕ ನೀರಾವರಿ ಅಂತರದಲ್ಲಿ ಹಿನ್ನೆಲೆ ಮಣ್ಣಿನ ತೇವಾಂಶ ಮತ್ತು ಶಿಲೀಂಧ್ರ ಬೀಜಕಗಳ ಉಪಸ್ಥಿತಿಯನ್ನು ಪುನರ್ನಿರ್ಮಿಸಲಾಗುತ್ತಿದೆ.`)
        .replace(/Reconstructing background hydraulic conductivity.*?in .*?\./gi, `${currentDistrict} ಜಿಲ್ಲೆಯಲ್ಲಿ ಸಾಂಪ್ರದಾಯಿಕ ಕಾಲುವೆ/ಹರಿವು ನೀರಾವರಿ ಪದ್ಧತಿಯಡಿ ಮಣ್ಣಿನ ಆಮ್ಲಜನಕ ಕೊರತೆ ಮತ್ತು ನೀರಿನ ಹರಿವಿನ ನಷ್ಟವನ್ನು ಪುನರ್ನಿರ್ಮಿಸಲಾಗುತ್ತಿದೆ.`)
        .replace(/Applying surgical intervention do\((.*?)\)\./gi, 'ಕಾರಣಾತ್ಮಕ ಹಸ್ತಕ್ಷೇಪ do($1) ಅನ್ವಯಿಸಲಾಗುತ್ತಿದೆ.')
        .replace(/Modifying agronomic inputs creates direct positive shift in resource utilization efficiency\./gi, 'ಕೃಷಿ ಪರಿಕರಗಳ ಬಳಕೆಯಲ್ಲಿ ಬದಲಾವಣೆ ಮಾಡುವುದರಿಂದ ಸಂಪನ್ಮೂಲ ಬಳಕೆಯ ದಕ್ಷತೆಯಲ್ಲಿ ಧನಾತ್ಮಕ ಸುಧಾರಣೆಯಾಗುತ್ತದೆ.')
        .replace(/Moisture stress in vegetative \/ flowering stage is alleviated by 30%, but canopy relative humidity rises during night hours\./gi, 'ಸಸ್ಯಕ/ಹೂಬಿಡುವ ಹಂತದಲ್ಲಿ ತೇವಾಂಶದ ಒತ್ತಡವು 30% ರಷ್ಟು ಕಡಿಮೆಯಾಗುತ್ತದೆ, ಆದರೆ ರಾತ್ರಿಯ ಸಮಯದಲ್ಲಿ ಎಲೆಗಳ ಸಾಪೇಕ್ಷ ಆರ್ದ್ರತೆ ಸ್ವಲ್ಪ ಹೆಚ್ಚಾಗುತ್ತದೆ.')
        .replace(/Water application efficiency jumps from 45% to 90%.*?\./gi, 'ನೀರಿನ ಬಳಕೆಯ ದಕ್ಷತೆಯು 45% ರಿಂದ 90% ಕ್ಕೆ ಏರಿಕೆಯಾಗುತ್ತದೆ, ಕಳೆಗಳ ಬಾಧೆ 60% ಕಡಿಮೆಯಾಗುತ್ತದೆ ಮತ್ತು ಸಾರಜನಕ ಸೋರಿಕೆ ಸಂಪೂರ್ಣ ನಿಲ್ಲುತ್ತದೆ.')
        .replace(/The counterfactual intervention produces a measurable improvement in crop vigor and yield stability\./gi, 'ಈ ಕೌಂಟರ್‌ಫ್ಯಾಕ್ಚುಯಲ್ ಕ್ರಮವು ಬೆಳೆಯ ಹುರುಪು ಮತ್ತು ಇಳುವರಿಯ ಸ್ಥಿರತೆಯನ್ನು ಗಣನೀಯವಾಗಿ ಹೆಚ್ಚಿಸುತ್ತದೆ.')
        .replace(/Adjusted irrigation reduces moisture stress and safeguards yield, but requires drip or morning scheduling to avoid nocturnal leaf wetness\./gi, 'ಹೊಂದಾಣಿಕೆಯ ನೀರಾವರಿಯು ನೀರಿನ ಒತ್ತಡವನ್ನು ನಿವಾರಿಸಿ ಇಳುವರಿಯನ್ನು ರಕ್ಷಿಸುತ್ತದೆ, ಆದರೆ ರಾತ್ರಿಯ ಎಲೆಗಳ ತೇವಾಂಶ ತಪ್ಪಿಸಲು ಹನಿ ನೀರಾವರಿ ಅಥವಾ ಬೆಳಗಿನ ಸಮಯವನ್ನು ಆರಿಸಿಕೊಳ್ಳಬೇಕು.')
        .replace(/Switching from flood to drip would have conserved 45% water.*?\./gi, 'ಹನಿ ನೀರಾವರಿ ಅಳವಡಿಸಿದ್ದರೆ ನೀರಿನ ಬಳಕೆಯಲ್ಲಿ 45% ಉಳಿತಾಯವಾಗುತ್ತಿತ್ತು ಮತ್ತು ಬೆಳೆಯ ಇಳುವರಿಯಲ್ಲಿ +18% ರಿಂದ +25% ಹೆಚ್ಚಳವಾಗುತ್ತಿತ್ತು.')
        .replace(/(\d+)%\s+Confidence/gi, '$1% ವಿಶ್ವಾಸಾರ್ಹತೆ');
    } else if (lang === 'hi') {
      text = text
        .replace(/### \*\*1\. Step 1: Abduction.*?\*\*/gi, '### **1. चरण 1: एब्डक्शन (अप्रत्यक्ष स्थितियों का अनुमान)**')
        .replace(/### \*\*2\. Step 2: Action.*?\*\*/gi, '### **2. चरण 2: क्रिया (कारणात्मक हस्तक्षेप do(·))**')
        .replace(/### \*\*3\. Step 3: Prediction.*?\*\*/gi, '### **3. चरण 3: भविष्यवाणी (काउंटरफैक्चुअल परिणाम गणना)**')
        .replace(/### \*\*Summary of Counterfactual Outcome\*\*/gi, '### **काउंटरफैक्चुअल परिणाम का सारांश**')
        .replace(/### \*\*The Trade-Off Analysis\*\*/gi, '### **तुलनात्मक एवं ट्रेड-ऑफ विश्लेषण**')
        .replace(/### \*\*Probabilistic Confidence Percentage\*\*/gi, '### **संभाव्यता विश्वास प्रतिशत**')
        .replace(/\| Parameter \| Observed Reality \| Counterfactual Action \|/gi, '| पैरामीटर | देखी गई वास्तविकता | काउंटरफैक्चुअल कदम |')
        .replace(/\| Parameter \| Observed History \| Counterfactual Adjustment \|/gi, '| पैरामीटर | देखा गया वास्तविक | काउंटरफैक्चुअल समायोजन |')
        .replace(/\| Parameter \| Observed \(Flood Irrigation\) \| Counterfactual \(Drip Irrigation\) \|/gi, '| पैरामीटर | देखा गया वास्तविक (बाढ़ सिंचाई) | काउंटरफैक्चुअल (ड्रिप सिंचाई) |')
        .replace(/\| \*\*Resource Efficiency\*\* \| Standard baseline \| Optimized input delivery \|/gi, '| **संसाधन दक्षता** | मानक आधार रेखा | अनुकूलित इनपुट प्रबंधन |')
        .replace(/\| \*\*Moisture Stress\*\* \| Moderate \| Alleviated by 30% \|/gi, '| **नमी तनाव** | मध्यम | 30% तक कमी |')
        .replace(/\| \*\*Canopy Microclimate\*\* \| Dry \| Slightly elevated night RH \|/gi, '| **सूक्ष्म जलवायु** | शुष्क | रात की सापेक्ष आर्द्रता में थोड़ी वृद्धि |')
        .replace(/\| \*\*Water Application Efficiency\*\* \|.*?\| \*\*85% - 92%.*?\*\* \|/gi, '| **जल उपयोग दक्षता** | 40% - 50% (अधिक अपवाह/बर्बादी) | **85% - 92% (सीधे जड़ों तक आपूर्ति)** |')
        .replace(/\| \*\*Root Aeration & Nutrient Leaching\*\* \|.*?\| Continuous optimal aeration & fertigation \|/gi, '| **जड़ों में वातन एवं पोषक तत्व** | जलभराव और नाइट्रोजन रिसाव | निरंतर इष्टतम वायु संचार एवं फर्टिगेशन |')
        .replace(/\| \*\*Weed Growth & Inter-row Labor\*\* \|.*?\| Low \(Only cane row wetted\) \|/gi, '| **खरपतवार और श्रम लागत** | अधिक (पूरे खेत में नमी) | कम (केवल फसल कतार में नमी) |')
        .replace(/\| \*\*Net Cane Yield & Profit\*\* \|.*?\| \*\*.*?higher yield per acre\*\* \|/gi, '| **शुद्ध उपज एवं मुनाफा** | आधार रेखा | **+18% से +25% अधिक उपज प्रति एकड़** |')
        .replace(/Background baseline conditions for .*? in .*?\./gi, `${currentDistrict} में ${localizedCropName} के लिए आधारभूत पृष्ठभूमि स्थितियां।`)
        .replace(/Reconstructing background moisture tension and fungal spore presence.*?for .*? in .*?\./gi, `${currentDistrict} में ${localizedCropName} के लिए वास्तविक सिंचाई अंतराल के तहत मिट्टी की नमी और कवक बीजाणुओं की पृष्ठभूमि स्थिति का पुनर्निर्माण किया जा रहा है।`)
        .replace(/Reconstructing background hydraulic conductivity.*?in .*?\./gi, `${currentDistrict} में पारंपरिक बाढ़/नाली सिंचाई के तहत मिट्टी में ऑक्सीजन की कमी और जल बहाव नुकसान का पुनर्निर्माण किया जा रहा है।`)
        .replace(/Applying surgical intervention do\((.*?)\)\./gi, 'कारणात्मक हस्तक्षेप do($1) लागू किया जा रहा है।')
        .replace(/Modifying agronomic inputs creates direct positive shift in resource utilization efficiency\./gi, 'कृषि आदानों में समयोचित बदलाव से संसाधन उपयोग दक्षता में सीधा सुधार होता है।')
        .replace(/Moisture stress in vegetative \/ flowering stage is alleviated by 30%, but canopy relative humidity rises during night hours\./gi, 'वानस्पतिक/फूल अवस्था में नमी का तनाव 30% तक कम हो जाता है, लेकिन रात के समय पत्तियों की आर्द्रता थोड़ी बढ़ जाती है।')
        .replace(/Water application efficiency jumps from 45% to 90%.*?\./gi, 'जल उपयोग दक्षता 45% से बढ़कर 90% हो जाती है, खरपतवार में 60% कमी आती है और पोषक तत्वों का रिसाव बंद होता है।')
        .replace(/The counterfactual intervention produces a measurable improvement in crop vigor and yield stability\./gi, 'यह काउंटरफैक्चुअल हस्तक्षेप फसल की सेहत और उपज स्थिरता में उल्लेखनीय सुधार लाता है।')
        .replace(/Adjusted irrigation reduces moisture stress and safeguards yield, but requires drip or morning scheduling to avoid nocturnal leaf wetness\./gi, 'समय पर सिंचाई से नमी का तनाव कम होता है और उपज सुरक्षित रहती है, लेकिन रात की नमी से बचने के लिए सुबह ड्रिप से सिंचाई करनी चाहिए।')
        .replace(/Switching from flood to drip would have conserved 45% water.*?\./gi, 'ड्रिप सिंचाई अपनाने से 45% पानी की बचत होती और फसल पैदावार में +18% से +25% की वृद्धि दर्ज की जाती।')
        .replace(/(\d+)%\s+Confidence/gi, '$1% विश्वास');
    }
    return text;
  }

  // ====================================================
  // 3. MULTI-AGENT DEBATE ROOM STATE
  // ====================================================
  const [debateData, setDebateData] = useState(null);
  const [debateLoading, setDebateLoading] = useState(false);
  const [visibleTurns, setVisibleTurns] = useState([]);

  async function handleStartDebate() {
    setDebateLoading(true);
    setVisibleTurns([]);
    try {
      const res = await api.runMultiAgentDebate({
        crop: currentCrop,
        district: currentDistrict,
        disease: predictedDisease,
        price_info: predictedPrice,
        farmer_budget: 'moderate',
        lang: lang
      });
      setDebateData(res);

      if (res && res.debate_turns) {
        res.debate_turns.forEach((turn, idx) => {
          setTimeout(() => {
            setVisibleTurns((prev) => [...prev, turn]);
          }, (idx + 1) * 600);
        });
      }
    } catch (e) {
      setDebateData({
        status: 'error',
        consensus_summary: lang === 'kn'
          ? 'ಈ ಸಮಯದಲ್ಲಿ ಮಲ್ಟಿ-ಏಜೆಂಟ್ ಚರ್ಚೆಯನ್ನು ಪ್ರಾರಂಭಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.'
          : lang === 'hi'
            ? 'इस समय मल्टी-एजेंट बहस आयोजित नहीं की जा सकी।'
            : 'Could not convene the Multi-Agent debate at this time.'
      });
    } finally {
      setDebateLoading(false);
    }
  }

  // Reload debate when language changes if debate tab is active
  useEffect(() => {
    if (activeTab === 'debate' && debateData) {
      handleStartDebate();
    }
  }, [lang]);

  // ====================================================
  // 4. REGRET MINIMIZATION PLANS STATE
  // ====================================================
  const [regretPreference, setRegretPreference] = useState('balanced');
  const [regretPlans, setRegretPlans] = useState(null);
  const [regretLoading, setRegretLoading] = useState(false);

  useEffect(() => {
    let cancel = false;
    async function fetchPlans() {
      setRegretLoading(true);
      try {
        const res = await api.getRegretPlans({
          crop: currentCrop,
          risk_preference: regretPreference,
          lang: lang
        });
        if (!cancel && res) setRegretPlans(res);
      } catch (e) {
        console.error('Error fetching regret plans:', e);
      } finally {
        if (!cancel) setRegretLoading(false);
      }
    }
    fetchPlans();
    return () => { cancel = true; };
  }, [currentCrop, regretPreference, lang]);

  function getLocalizedPhenologyNote(note, l) {
    if (!note) return '';
    const s = String(note);
    if (l === 'kn') {
      if (s.includes('Optimal Vegetative') || s.includes('Grain Filling') || s.includes('ಅತ್ಯುತ್ತಮ')) {
        return 'ಅತ್ಯುತ್ತಮ ಸಸ್ಯಕ ಬೆಳವಣಿಗೆ ಮತ್ತು ಕಾಳು ತುಂಬುವ ಹಂತ';
      }
      if (s.includes('Delayed Anthesis') || s.includes('terminal heat') || s.includes('ವಿಳಂಬ')) {
        return 'ವಿಳಂಬವಾದ ಹೂಬಿಡುವಿಕೆ — ಕಾಳು ತುಂಬುವಾಗ ಅಂತ್ಯ ಹಂತದ ಶಾಖದ ಒತ್ತಡದ ಅಪಾಯ';
      }
      if (s.includes('Early Emergence') || s.includes('frost') || s.includes('ಮುಂಚಿನ')) {
        return 'ಮುಂಚಿನ ಮೊಳಕೆಯೊಡೆಯುವಿಕೆ — ಸಸಿಗಳಿಗೆ ಶೀತ ಅಥವಾ ಚಳಿ ಆಘಾತದ ಸಾಧ್ಯತೆ';
      }
      if (s.includes('Moisture Deficit') || s.includes('Critical Flowering') || s.includes('ಕೊರತೆ')) {
        return 'ನಿರ್ಣಾಯಕ ಹೂಬಿಡುವ ಹಂತದಲ್ಲಿ ತೇವಾಂಶದ ಕೊರತೆ';
      }
      if (s.includes('Spore Germination') || s.includes('High Humidity') || s.includes('ಆರ್ದ್ರತೆ')) {
        return 'ಹೆಚ್ಚಿನ ಆರ್ದ್ರತೆ: ಶಿಲೀಂಧ್ರ ಬೀಜಕಗಳು ಮೊಳಕೆಯೊಡೆಯುವ ಅಪಾಯ';
      }
    } else if (l === 'hi') {
      if (s.includes('Optimal Vegetative') || s.includes('Grain Filling') || s.includes('इष्टतम')) {
        return 'इष्टतम वानस्पतिक वृद्धि एवं दाना भराव अवस्था';
      }
      if (s.includes('Delayed Anthesis') || s.includes('terminal heat') || s.includes('देर')) {
        return 'देर से फूल आना — दाना भराव के दौरान अत्यधिक ताप तनाव का जोखिम';
      }
      if (s.includes('Early Emergence') || s.includes('frost') || s.includes('अगेती')) {
        return 'अगेती अंकुरण — पौधों को ठंड या शीतलहर का जोखिम';
      }
      if (s.includes('Moisture Deficit') || s.includes('Critical Flowering') || s.includes('कमी')) {
        return 'महत्वपूर्ण फूल अवस्था के दौरान नमी की कमी';
      }
      if (s.includes('Spore Germination') || s.includes('High Humidity') || s.includes('आर्द्रता')) {
        return 'उच्च आर्द्रता: कवक बीजाणु अंकुरण का उच्च जोखिम';
      }
    }
    return s;
  }

  function getLocalizedScenario(sc) {
    if (!sc) return '';
    const s = String(sc);
    if (lang === 'kn') {
      if (s.includes('Normal Season') || s.includes('ಸಾಮಾನ್ಯ ಹಂಗಾಮು') || s.includes('ಸಾಮಾನ್ಯ ಹವಾಮಾನ') || s.includes('सामान्य')) {
        return '☀️ ಸಾಮಾನ್ಯ ಹವಾಮಾನ ಹಂಗಾಮು (60% ಸಂಭವನೀಯತೆ)';
      }
      if (s.includes('Drought') || s.includes('Heatwave') || s.includes('ಬರಗಾಲ') || s.includes('ತಾಪಮಾನ') || s.includes('सूखा')) {
        return '🏜️ ಸಾಧಾರಣ ಬರಗಾಲ / ತೀವ್ರ ತಾಪಮಾನ (25% ಸಂಭವನೀಯತೆ)';
      }
      if (s.includes('Price Crash') || s.includes('ಕುಸಿತ') || s.includes('ಮಾರುಕಟ್ಟೆ ದರ') || s.includes('गिरावट')) {
        return '📉 APMC ಮಾರುಕಟ್ಟೆ ದರ ಕುಸಿತ (15% ಸಂಭವನೀಯತೆ)';
      }
    } else if (lang === 'hi') {
      if (s.includes('Normal Season') || s.includes('सामान्य मौसम') || s.includes('सामान्य') || s.includes('ಸಾಮಾನ್ಯ')) {
        return '☀️ सामान्य मौसम सीजन (60% संभावना)';
      }
      if (s.includes('Drought') || s.includes('Heatwave') || s.includes('सूखा') || s.includes('लू') || s.includes('ಬರಗಾಲ')) {
        return '🏜️ सूखा / लू का प्रकोप (25% संभावना)';
      }
      if (s.includes('Price Crash') || s.includes('गिरावट') || s.includes('मंडी भाव') || s.includes('ಕುಸಿತ')) {
        return '📉 APMC मंडी भाव में भारी गिरावट (15% संभावना)';
      }
    }
    return sc;
  }

  function getLocalizedPlanTitle(type, p) {
    if (!p) return '';
    if (lang === 'kn') {
      if (p.title_kn) return p.title_kn;
      if (type === 'safe') return '🔵 ಸುರಕ್ಷಿತ ಯೋಜನೆ (ಬಂಡವಾಳ ರಕ್ಷಣೆ & ಕಡಿಮೆ ನೀರು)';
      if (type === 'balanced') return '🟡 ಸಮತೋಲಿತ ಯೋಜನೆ (ಸೂಕ್ತ ಅಪಾಯ ನಿರ್ವಹಣೆ)';
      if (type === 'aggressive') return '🟢 ಆಕ್ರಮಣಕಾರಿ ಯೋಜನೆ (ಹೆಚ್ಚಿನ ಇಳುವರಿ & ಗರಿಷ್ಠ ಲಾಭ)';
    } else if (lang === 'hi') {
      if (p.title_hi) return p.title_hi;
      if (type === 'safe') return '🔵 सुरक्षित योजना (पूंजी सुरक्षा एवं कम जल उपयोग)';
      if (type === 'balanced') return '🟡 संतुलित योजना (इष्टतम जोखिम प्रबंधन)';
      if (type === 'aggressive') return '🟢 आक्रामक योजना (उच्च उपज एवं अधिकतम लाभ)';
    }
    return p.title || '';
  }

  function getLocalizedPlanVariety(type, p) {
    if (!p) return '';
    if (lang === 'kn') {
      if (p.variety_kn) return p.variety_kn;
      const v = p.variety || '';
      if (v.includes('Sahbhagi') || v.includes('Short-Duration') || v.includes('Drought-Tolerant')) return 'ಕಡಿಮೆ ಅವಧಿಯ ಬರ-ನಿರೋಧಕ ತಳಿ (ಉದಾ. ಸಹಭಾಗಿ ಧಾನ್ / R-RHZ-7)';
      if (v.includes('MTU 1010') || v.includes('Medium-Duration') || v.includes('High-Yield')) return 'ಮಧ್ಯಮ ಅವಧಿಯ ಅಧಿಕ ಇಳುವರಿ ತಳಿ (ಉದಾ. MTU 1010 / BPT 5204)';
      if (v.includes('Basmati') || v.includes('Pusa 1121') || v.includes('Aromatic')) return 'ಸುಗಂಧಿತ / ಸಣ್ಣ ಅಕ್ಕಿ ಬಾಸ್ಮತಿ ಅಥವಾ ಹೈಬ್ರಿಡ್ (ಉದಾ. ಪೂಸಾ 1121 / ಅರೈಸ್ 6444)';
      if (v.includes('TMV-2') || v.includes('Kadiri')) return 'ಕಡಿಮೆ ಅವಧಿಯ ಬರ-ನಿರೋಧಕ ಗೊಂಚಲು ತಳಿ (TMV-2 / JL-24 / ಕದಿರಿ-6)';
      if (v.includes('GPBD-4')) return 'ಅಧಿಕ ಇಳುವರಿ ಮತ್ತು ತಿಕ್ಕಾ ರೋಗ-ನಿರೋಧಕ ತಳಿ (GPBD-4 / G2-52 / ಕದಿರಿ-6)';
      if (v.includes('JG-11') || v.includes('Annigeri')) return 'ಜೆಜಿ-11 / ಅಣ್ಣಿಗೇರಿ-1 (ಬರ ಮತ್ತು ಸೊರಗು ರೋಗ ನಿರೋಧಕ)';
      if (!/[\u0C80-\u0CFF]/.test(v)) {
        if (type === 'safe') return 'ಕಡಿಮೆ ಅವಧಿಯ ಬರ ಮತ್ತು ರೋಗ-ನಿರೋಧಕ ಸ್ಥಳೀಯ ತಳಿ';
        if (type === 'balanced') return 'ಮಧ್ಯಮ ಅವಧಿಯ ಅಧಿಕ ಇಳುವರಿ ಸುಧಾರಿತ ತಳಿ';
        if (type === 'aggressive') return 'ಅಧಿಕ ಇಳುವರಿ ಪ್ರೀಮಿಯಂ ಹೈಬ್ರಿಡ್ ತಳಿ';
      }
    } else if (lang === 'hi') {
      if (p.variety_hi) return p.variety_hi;
      const v = p.variety || '';
      if (v.includes('Sahbhagi') || v.includes('Short-Duration') || v.includes('Drought-Tolerant')) return 'कम अवधि की सूखा-सहिष्णु किस्म (जैसे सहभागीय धान / R-RHZ-7)';
      if (v.includes('MTU 1010') || v.includes('Medium-Duration') || v.includes('High-Yield')) return 'मध्यम अवधि की उच्च उपज वाली किस्म (जैसे MTU 1010 / BPT 5204)';
      if (v.includes('Basmati') || v.includes('Pusa 1121') || v.includes('Aromatic')) return 'सुगंधित / महीन दाना बासमती या संकर (जैसे पूसा 1121 / अराइज 6444)';
      if (v.includes('TMV-2') || v.includes('Kadiri')) return 'कम अवधि की सूखा-प्रतिरोधी गुच्छा किस्म (TMV-2 / JL-24 / कदिरी-6)';
      if (v.includes('GPBD-4')) return 'उच्च उपज एवं टिक्का रोग-प्रतिरोधी किस्म (GPBD-4 / G2-52 / कदिरी-6)';
      if (v.includes('JG-11') || v.includes('Annigeri')) return 'जेजी-11 / अन्निगेरी-1 (सूखा व उकठा प्रतिरोधी)';
      if (!/[\u0900-\u097F]/.test(v)) {
        if (type === 'safe') return 'कम अवधि की सूखा व रोग-प्रतिरोधी स्थानीय किस्म';
        if (type === 'balanced') return 'मध्यम अवधि की उच्च उपज वाली उन्नत किस्म';
        if (type === 'aggressive') return 'उच्च उपज वाली प्रीमियम संकर किस्म';
      }
    }
    return p.variety || '';
  }

  function getLocalizedPlanDownside(type, p) {
    if (!p) return '';
    if (lang === 'kn') {
      if (p.downside_worst_case_kn) return p.downside_worst_case_kn;
      const d = p.downside_worst_case || '';
      if (d.includes('Protected Capital') || d.includes('+₹15,000') || d.includes('+₹10,000') || d.includes('+₹12,000')) return '+₹15,000 (ಬಂಡವಾಳ ಸಂಪೂರ್ಣ ಸುರಕ್ಷಿತ)';
      if (d.includes('Break-even') || d.includes('MSP') || d.includes('₹0')) return '₹0 (MSP ಬೆಂಬಲ ಬೆಲೆ ರಕ್ಷಣೆ)';
      if (d.includes('Loss') || d.includes('-₹18,000') || d.includes('-₹14,000') || d.includes('blast')) return '-₹18,000 (ತೀವ್ರ ರೋಗ ಅಥವಾ ಬೆಳೆ ಬಾಗಿದರೆ ನಷ್ಟದ ಸಾಧ್ಯತೆ)';
      if (!/[\u0C80-\u0CFF]/.test(d)) {
        if (type === 'safe') return '+₹15,000 (ಬಂಡವಾಳ ಸಂಪೂರ್ಣ ಸುರಕ್ಷಿತ)';
        if (type === 'balanced') return '₹0 (MSP ಬೆಂಬಲ ಬೆಲೆ ರಕ್ಷಣೆ)';
        if (type === 'aggressive') return '-₹18,000 (ತೀವ್ರ ರೋಗ ಅಥವಾ ನೈಸರ್ಗಿಕ ವಿಕೋಪದಲ್ಲಿ ನಷ್ಟದ ಅಪಾಯ)';
      }
    } else if (lang === 'hi') {
      if (p.downside_worst_case_hi) return p.downside_worst_case_hi;
      const d = p.downside_worst_case || '';
      if (d.includes('Protected Capital') || d.includes('+₹15,000') || d.includes('+₹10,000') || d.includes('+₹12,000')) return '+₹15,000 (पूंजी पूर्णतः सुरक्षित)';
      if (d.includes('Break-even') || d.includes('MSP') || d.includes('₹0')) return '₹0 (सरकारी एमएसपी सुरक्षा)';
      if (d.includes('Loss') || d.includes('-₹18,000') || d.includes('-₹14,000') || d.includes('blast')) return '-₹18,000 (गंभीर ब्लास्ट या फसल गिरने पर नुकसान)';
      if (!/[\u0900-\u097F]/.test(d)) {
        if (type === 'safe') return '+₹15,000 (पूंजी पूर्णतः सुरक्षित)';
        if (type === 'balanced') return '₹0 (सरकारी एमएसपी सुरक्षा)';
        if (type === 'aggressive') return '-₹18,000 (गंभीर रोग या प्राकृतिक आपदा में नुकसान का जोखिम)';
      }
    }
    return p.downside_worst_case || '';
  }

  function getLocalizedPlanCapital(type, p) {
    if (!p) return '';
    if (lang === 'kn') {
      if (p.capital_outlay_kn) return p.capital_outlay_kn;
      return (p.capital_outlay || '').replace(/\/ acre/gi, '/ ಎಕರೆ');
    } else if (lang === 'hi') {
      if (p.capital_outlay_hi) return p.capital_outlay_hi;
      return (p.capital_outlay || '').replace(/\/ acre/gi, '/ एकड़');
    }
    return p.capital_outlay || '';
  }

  function getLocalizedPlanStrategy(type, p) {
    if (!p) return '';
    if (lang === 'kn') {
      if (p.strategy_kn) return p.strategy_kn;
      const s = p.strategy || '';
      if (s.includes('Direct Seeded') || s.includes('DSR')) return 'ನೇರ ಬಿತ್ತನೆ ಭತ್ತ (DSR), ಕನಿಷ್ಠ ರಾಸಾಯನಿಕ ಬಳಕೆ, ಸಾವಯವ ಮಣ್ಣಿನ ಸುಧಾರಣೆ, ಶೂನ್ಯ ಸಾಲ, ಮೇವಿನ ಹೆಚ್ಚಿನ ಮೌಲ್ಯ.';
      if (s.includes('SRI') || s.includes('Intensification')) return 'ಶ್ರೀ (SRI) ಪದ್ಧತಿ, ಸಮಗ್ರ ಜೈವಿಕ ಗೊಬ್ಬರಗಳು, ಮತ್ತು PMFBY ಬೆಳೆ ವಿಮೆ ರಕ್ಷಣೆ.';
      if (s.includes('Intensive fertigation') || s.includes('tricyclazole')) return 'ತೀವ್ರ ಹನಿ ಫರ್ಟಿಗೇಷನ್, ನಿಖರ ಲಘು ಪೋಷಕಾಂಶಗಳು (ಸತು/ಬೋರಾನ್), ಮುನ್ನೆಚ್ಚರಿಕೆಯ ಟ್ರೈಸೈಕ್ಲಾಜೋಲ್ ಸಿಂಪಡಣೆ ವೇಳಾಪಟ್ಟಿ.';
      if (!/[\u0C80-\u0CFF]/.test(s)) {
        if (type === 'safe') return 'ಕಡಿಮೆ ಖರ್ಚಿನ ಸಾವಯವ ಪೋಷಣೆ, ಜೈವಿಕ ಬೀಜೋಪಚಾರ, ಶೂನ್ಯ ಸಾಲ, ಗರಿಷ್ಠ ಬಂಡವಾಳ ರಕ್ಷಣೆ.';
        if (type === 'balanced') return 'ಸಮಗ್ರ ಪೋಷಕಾಂಶ ನಿರ್ವಹಣೆ, ಮೈಕ್ರೋ-ನ್ಯೂಟ್ರಿಯೆಂಟ್ಸ್, ಮತ್ತು PMFBY ಬೆಳೆ ವಿಮೆ ರಕ್ಷಣೆ.';
        if (type === 'aggressive') return 'ತೀವ್ರ ಹನಿ ಫರ್ಟಿಗೇಷನ್, ನಿಖರ ಲಘು ಪೋಷಕಾಂಶಗಳು, ಮುನ್ನೆಚ್ಚರಿಕೆಯ ಸಸ್ಯ ಸಂರಕ್ಷಣೆ.';
      }
    } else if (lang === 'hi') {
      if (p.strategy_hi) return p.strategy_hi;
      const s = p.strategy || '';
      if (s.includes('Direct Seeded') || s.includes('DSR')) return 'सीधी बुवाई (DSR), न्यूनतम रासायनिक लागत, जैविक खाद, शून्य ऋण, उच्च चारा मूल्य।';
      if (s.includes('SRI') || s.includes('Intensification')) return 'एसआरआई (SRI) सघन धान प्रणाली, समन्वित जैव-उर्वरक और पीएमएफबीवाई (PMFBY) फसल बीमा।';
      if (s.includes('Intensive fertigation') || s.includes('tricyclazole')) return 'सघन फर्टिगेशन, सूक्ष्म पोषक तत्व (जिंक/बोरॉन) और निवारक ट्राइसाइक्लाजोल कवकनाशी समय सारणी।';
      if (!/[\u0900-\u097F]/.test(s)) {
        if (type === 'safe') return 'कम लागत जैविक पोषण, जैव-बीजोपचार, शून्य कर्ज और सुरक्षित पूंजी।';
        if (type === 'balanced') return 'संतुलित पोषण, सूक्ष्म पोषक तत्व और पीएमएफबीवाई फसल बीमा सुरक्षा।';
        if (type === 'aggressive') return 'सघन ड्रिप फर्टिगेशन, सूक्ष्म पोषक तत्व और अग्रिम फसल सुरक्षा समय सारणी।';
      }
    }
    return p.strategy || '';
  }

  function getLocalizedPlanScore(type, p) {
    if (!p) return '';
    if (lang === 'kn') {
      if (p.regret_score_kn) return p.regret_score_kn;
      const sc = p.regret_score || '';
      if (sc.includes('Minimum Regret') || sc.includes('0.08') || sc.includes('0.07') || sc.includes('0.09')) return 'ಕನಿಷ್ಠ ವಿಷಾದ (0.08) — ಮಳೆ ವಿಫಲತೆ ಅಥವಾ ಕಾಲುವೆ ವಿಳಂಬದಲ್ಲೂ ನಷ್ಟವಿಲ್ಲ.';
      if (sc.includes('Low Regret') || sc.includes('0.22') || sc.includes('0.18') || sc.includes('0.20')) return 'ಕಡಿಮೆ ವಿಷಾದ (0.22) — ಸಾಮಾನ್ಯ ಮಳೆಯ ಸಂದರ್ಭದಲ್ಲಿ ಅತ್ಯುತ್ತಮ ಅಪಾಯ-ಮುಕ್ತ ಲಾಭ.';
      if (sc.includes('High Regret') || sc.includes('0.65') || sc.includes('0.55') || sc.includes('0.58')) return 'ಹೆಚ್ಚಿನ ವಿಷಾದದ ಸಂಭವನೀಯತೆ (0.65) — ಹವಾಮಾನ ಅನುಕೂಲವಿದ್ದರೆ ಭರ್ಜರಿ ಲಾಭ, ರೋಗ ಬಂದರೆ ಹೆಚ್ಚಿನ ಅಪಾಯ.';
      if (!/[\u0C80-\u0CFF]/.test(sc)) {
        if (type === 'safe') return 'ಕನಿಷ್ಠ ವಿಷಾದ (0.08) — ಮಳೆ ವಿಫಲತೆ ಅಥವಾ ಕಾಲುವೆ ವಿಳಂಬದಲ್ಲೂ ನಷ್ಟವಿಲ್ಲ.';
        if (type === 'balanced') return 'ಕಡಿಮೆ ವಿಷಾದ (0.22) — ಸಾಮಾನ್ಯ ಮಳೆಯ ಸಂದರ್ಭದಲ್ಲಿ ಅತ್ಯುತ್ತಮ ಅಪಾಯ-ಮುಕ್ತ ಲಾಭ.';
        if (type === 'aggressive') return 'ಹೆಚ್ಚಿನ ವಿಷಾದದ ಸಂಭವನೀಯತೆ (0.65) — ಹವಾಮಾನ ಅನುಕೂಲವಿದ್ದರೆ ಭರ್ಜರಿ ಲಾಭ, ರೋಗ ಬಂದರೆ ಅಪಾಯ.';
      }
    } else if (lang === 'hi') {
      if (p.regret_score_hi) return p.regret_score_hi;
      const sc = p.regret_score || '';
      if (sc.includes('Minimum Regret') || sc.includes('0.08') || sc.includes('0.07') || sc.includes('0.09')) return 'न्यूनतम रिग्रेट (0.08) — बारिश में देरी या विफलता पर भी नुकसान नहीं।';
      if (sc.includes('Low Regret') || sc.includes('0.22') || sc.includes('0.18') || sc.includes('0.20')) return 'कम रिग्रेट (0.22) — सामान्य बारिश में सर्वोत्तम जोखिम-रहित शुद्ध लाभ।';
      if (sc.includes('High Regret') || sc.includes('0.65') || sc.includes('0.55') || sc.includes('0.58')) return 'उच्च रिग्रेट जोखिम (0.65) — मौसम अनुकूल रहने पर भारी मुनाफा, कीट प्रकोप होने पर बड़ा जोखिम।';
      if (!/[\u0900-\u097F]/.test(sc)) {
        if (type === 'safe') return 'न्यूनतम रिग्रेट (0.08) — बारिश में देरी या विफलता पर भी नुकसान नहीं।';
        if (type === 'balanced') return 'कम रिग्रेट (0.22) — सामान्य बारिश में सर्वोत्तम जोखिम-रहित शुद्ध लाभ।';
        if (type === 'aggressive') return 'उच्च रिग्रेट जोखिम (0.65) — मौसम अनुकूल रहने पर भारी मुनाफा, रोग आने पर जोखिम।';
      }
    }
    return p.regret_score || '';
  }

  function getLocalizedPlanProfit(p) {
    if (!p) return '';
    if (p[`expected_profit_acre_${lang}`]) return p[`expected_profit_acre_${lang}`];
    return p.expected_profit_acre || '';
  }

  return (
    <div className="section-box decision-intelligence-hub" id="decision-intelligence">
      {/* Header */}
      <div className="section-header di-header">
        <div className="di-header-titles">
          <div className="di-badge">{loc('badge')}</div>
          <h2>{t('diTitle')}</h2>
          <p className="section-desc">{t('diDesc')}</p>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="di-tabs-nav">
        <button
          type="button"
          className={`di-tab-btn ${activeTab === 'digital_twin' ? 'active' : ''}`}
          onClick={() => setActiveTab('digital_twin')}
        >
          {t('tabDigitalTwin')}
        </button>
        <button
          type="button"
          className={`di-tab-btn ${activeTab === 'counterfactual' ? 'active' : ''}`}
          onClick={() => setActiveTab('counterfactual')}
        >
          {t('tabCounterfactual')}
        </button>
        <button
          type="button"
          className={`di-tab-btn ${activeTab === 'debate' ? 'active' : ''}`}
          onClick={() => {
            setActiveTab('debate');
            if (!debateData) handleStartDebate();
          }}
        >
          {t('tabDebate')}
        </button>
        <button
          type="button"
          className={`di-tab-btn ${activeTab === 'regret' ? 'active' : ''}`}
          onClick={() => setActiveTab('regret')}
        >
          {t('tabRegret')}
        </button>
      </div>

      {/* TAB 1: DIGITAL TWIN SIMULATOR */}
      {activeTab === 'digital_twin' && (
        <div className="di-tab-content digital-twin-view">
          <div className="di-intro-card">
            <p>
              🎛️ <strong>{loc('dtControlsTitle')}:</strong> {loc('dtIntro')}
            </p>
          </div>

          <div className="dt-grid">
            {/* Sliders Column */}
            <div className="dt-controls-card">
              <h3>🎚️ {loc('dtControlsTitle')}</h3>

              <div className="dt-slider-group">
                <div className="dt-slider-label">
                  <span>🌧️ {loc('dtRainfallLabel')}</span>
                  <strong>{simParams.rainfall_delta_pct > 0 ? `+${simParams.rainfall_delta_pct}%` : `${simParams.rainfall_delta_pct}%`}</strong>
                </div>
                <input
                  type="range"
                  min="-50"
                  max="50"
                  step="5"
                  value={simParams.rainfall_delta_pct}
                  onChange={(e) => setSimParams({ ...simParams, rainfall_delta_pct: parseFloat(e.target.value) })}
                />
                <div className="dt-slider-ticks">
                  <span>{loc('dtDrought')}</span>
                  <span>{loc('dtNormal')}</span>
                  <span>{loc('dtExcess')}</span>
                </div>
              </div>

              <div className="dt-slider-group">
                <div className="dt-slider-label">
                  <span>📅 {loc('dtSowingShiftLabel')}</span>
                  <strong>
                    {simParams.sowing_shift_days > 0
                      ? `+${simParams.sowing_shift_days} ${loc('dtDaysLate')}`
                      : simParams.sowing_shift_days < 0
                        ? `${Math.abs(simParams.sowing_shift_days)} ${loc('dtDaysEarly')}`
                        : loc('dtOptimalWindow')}
                  </strong>
                </div>
                <input
                  type="range"
                  min="-20"
                  max="20"
                  step="2"
                  value={simParams.sowing_shift_days}
                  onChange={(e) => setSimParams({ ...simParams, sowing_shift_days: parseInt(e.target.value, 10) })}
                />
                <div className="dt-slider-ticks">
                  <span>{loc('dtEarlyTick')}</span>
                  <span>{loc('dtZeroTick')}</span>
                  <span>{loc('dtLateTick')}</span>
                </div>
              </div>

              <div className="dt-slider-group">
                <div className="dt-slider-label">
                  <span>🧪 {loc('dtFertLabel')}</span>
                  <strong>{simParams.fertilizer_pct}{loc('dtOfRec')}</strong>
                </div>
                <input
                  type="range"
                  min="40"
                  max="160"
                  step="10"
                  value={simParams.fertilizer_pct}
                  onChange={(e) => setSimParams({ ...simParams, fertilizer_pct: parseFloat(e.target.value) })}
                />
                <div className="dt-slider-ticks">
                  <span>{loc('dtDeficit')}</span>
                  <span>{loc('dtRec')}</span>
                  <span>{loc('dtHigh')}</span>
                </div>
              </div>

              <div className="dt-slider-group">
                <div className="dt-slider-label">
                  <span>💧 {loc('dtIrrigLabel')}</span>
                  <strong>{loc('dtEveryXDays', simParams.irrigation_frequency_days)}</strong>
                </div>
                <input
                  type="range"
                  min="2"
                  max="14"
                  step="1"
                  value={simParams.irrigation_frequency_days}
                  onChange={(e) => setSimParams({ ...simParams, irrigation_frequency_days: parseInt(e.target.value, 10) })}
                />
                <div className="dt-slider-ticks">
                  <span>{loc('dtEvery2')}</span>
                  <span>{loc('dtEvery7')}</span>
                  <span>{loc('dtEvery14')}</span>
                </div>
              </div>
            </div>

            {/* Live Telemetry Display */}
            <div className="dt-telemetry-card">
              <h3>📊 {loc('dtTelemetryTitle')} ({localizedCropName})</h3>

              {simResult ? (
                <div className="telemetry-grid">
                  <div className="telemetry-box gauge-health">
                    <span className="telemetry-title">{loc('dtHealthScore')}</span>
                    <div className="health-circle" style={{
                      borderColor: simResult.crop_health_score > 75 ? '#2e7d32' : simResult.crop_health_score > 50 ? '#f57f17' : '#c62828'
                    }}>
                      <span className="health-val">{simResult.crop_health_score}</span>
                      <span className="health-max">/100</span>
                    </div>
                    <small>{getLocalizedPhenologyNote(simResult.phenology_stage_note, lang) || loc('dtStageOptimal')}</small>
                  </div>

                  <div className="telemetry-box-metrics">
                    <div className="metric-row">
                      <span>{loc('dtSoilMoisture')}</span>
                      <div className="metric-bar-bg">
                        <div className="metric-bar-fill fill-blue" style={{ width: `${simResult.simulated_soil_moisture}%` }}></div>
                      </div>
                      <strong>{simResult.simulated_soil_moisture}%</strong>
                    </div>

                    <div className="metric-row">
                      <span>{loc('dtWaterStress')}</span>
                      <div className="metric-bar-bg">
                        <div className="metric-bar-fill fill-orange" style={{ width: `${simResult.water_stress_index}%` }}></div>
                      </div>
                      <strong>{simResult.water_stress_index}%</strong>
                    </div>

                    <div className="metric-row">
                      <span>{loc('dtThermalStress')}</span>
                      <div className="metric-bar-bg">
                        <div className="metric-bar-fill fill-red" style={{ width: `${simResult.thermal_stress_index}%` }}></div>
                      </div>
                      <strong>{simResult.thermal_stress_index}%</strong>
                    </div>

                    <div className="metric-row">
                      <span>{loc('dtPathogenRisk')}</span>
                      <div className="metric-bar-bg">
                        <div className="metric-bar-fill fill-purple" style={{ width: `${simResult.pathogen_risk_index}%` }}></div>
                      </div>
                      <strong>{simResult.pathogen_risk_index}%</strong>
                    </div>
                  </div>

                  {/* Financial Projection Banner */}
                  <div className="telemetry-financial-card">
                    <div className="fin-col">
                      <span className="fin-label">{loc('dtProjectedYield')}</span>
                      <strong className="fin-val">{simResult.projected_yield_q_acre} {loc('dtQAcre')}</strong>
                      <span className={`fin-delta ${simResult.yield_delta_pct >= 0 ? 'pos' : 'neg'}`}>
                        {simResult.yield_delta_pct >= 0 ? `+${simResult.yield_delta_pct}%` : `${simResult.yield_delta_pct}%`} {loc('dtVsBaseline')}
                      </span>
                    </div>
                    <div className="fin-col">
                      <span className="fin-label">{loc('dtGrossRevenue')}</span>
                      <strong className="fin-val">₹{simResult.projected_revenue_inr?.toLocaleString()}</strong>
                    </div>
                    <div className="fin-col">
                      <span className="fin-label">{loc('dtEstimatedCost')}</span>
                      <strong className="fin-val">₹{simResult.projected_cost_inr?.toLocaleString()}</strong>
                    </div>
                    <div className="fin-col fin-profit">
                      <span className="fin-label">{loc('dtNetProfit')}</span>
                      <strong className="fin-val highlight-profit">₹{simResult.projected_profit_inr?.toLocaleString()} {loc('dtPerAcre')}</strong>
                    </div>
                  </div>
                </div>
              ) : (
                <p className="loading-text">{loc('dtComputing')}</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: COUNTERFACTUAL CAUSAL AI */}
      {activeTab === 'counterfactual' && (
        <div className="di-tab-content counterfactual-view">
          <div className="di-intro-card">
            <p>
              ⏪ <strong>{t('tabCounterfactual')}:</strong> {loc('cfIntro')}
            </p>
          </div>

          {/* Preset Buttons */}
          <div className="cf-presets">
            <span className="cf-preset-label">💡 {loc('cfTrySample')}</span>
            <button
              type="button"
              className="cf-preset-btn"
              onClick={() => {
                const q = loc('cfPreset1Query');
                setCfQuery(q);
                handleRunCounterfactual(q);
              }}
            >
              {loc('cfPreset1Btn')}
            </button>
            <button
              type="button"
              className="cf-preset-btn"
              onClick={() => {
                const q = loc('cfPreset2Query');
                setCfQuery(q);
                handleRunCounterfactual(q);
              }}
            >
              {loc('cfPreset2Btn')}
            </button>
            <button
              type="button"
              className="cf-preset-btn"
              onClick={() => {
                const q = loc('cfPreset3Query');
                setCfQuery(q);
                handleRunCounterfactual(q);
              }}
            >
              {loc('cfPreset3Btn')}
            </button>
          </div>

          {/* Query Input Box */}
          <div className="cf-input-box">
            <input
              type="text"
              className="cf-text-input"
              value={cfQuery}
              onChange={(e) => setCfQuery(e.target.value)}
              placeholder={loc('cfInputPlaceholder')}
            />
            <button
              type="button"
              className={`mic-btn ${isListening ? 'listening' : ''}`}
              onClick={startVoiceInput}
              title={loc('cfVoice')}
            >
              🎤 {isListening ? loc('cfListening') : loc('cfVoice')}
            </button>
            <button
              type="button"
              className="gov-btn"
              onClick={() => handleRunCounterfactual()}
              disabled={cfLoading}
            >
              {cfLoading ? loc('cfComputingBtn') : `🔍 ${loc('cfAnalysisBtn')}`}
            </button>
          </div>

          {/* Counterfactual Result Display */}
          {cfResult && (
            <div className="cf-result-card">
              <div className="cf-result-header">
                <div className="cf-badge-row">
                  <span className="cf-tag">{loc('cfTag')}</span>
                  <span className="cf-confidence">🎯 {loc('cfConfidence')} {cfResult.confidence_pct}%</span>
                </div>
                <h3>{loc('cfAssessment')}</h3>
              </div>

              <div className="cf-comparison-grid">
                <div className="cf-box factual-box">
                  <h4>📌 {loc('cfFactualTitle')}</h4>
                  <p>
                    <strong>{loc('cfTarget')}</strong> {localizedCropName} {cfResult.disease ? `(${cfResult.disease})` : ''} - {currentDistrict}
                  </p>
                  <p>{loc('cfFactualDesc')}</p>
                </div>
                <div className="cf-box counterfactual-box">
                  <h4>🔄 {loc('cfCounterfactualTitle')}</h4>
                  <p>
                    <strong>{loc('cfIntervention')}</strong> <code>do({cfResult.action_description || cfResult.query})</code>
                  </p>
                  <p>{loc('cfCounterfactualDesc')}</p>
                </div>
              </div>

              <div className="cf-explanation-markdown">
                <div style={{ whiteSpace: 'pre-line', lineHeight: '1.6' }}>
                  {localizeExplanation(cfResult.explanation)}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: MULTI-AGENT DEBATE ROOM */}
      {activeTab === 'debate' && (
        <div className="di-tab-content debate-view">
          <div className="di-intro-card">
            <p>
              🎭 <strong>{t('tabDebate')}:</strong> {loc('debateIntro')}
            </p>
          </div>

          <div className="debate-action-bar">
            <button
              type="button"
              className="gov-btn"
              onClick={handleStartDebate}
              disabled={debateLoading}
            >
              {debateLoading ? loc('debateDebating') : loc('debateReconvene')}
            </button>
          </div>

          {/* Live Debate Chat Stream */}
          <div className="debate-chat-container">
            {visibleTurns.length > 0 ? (
              visibleTurns.map((turn, i) => (
                <div key={i} className={`debate-message-row agent-${turn.agent_id}`}>
                  <div className="agent-avatar-badge">
                    {turn.agent_id === 'agronomist' ? '🌾' : turn.agent_id === 'economist' ? '📈' : turn.agent_id === 'pathologist' ? '🔬' : turn.agent_id === 'irrigation_specialist' ? '💧' : '🛡️'}
                  </div>
                  <div className="debate-bubble">
                    <div className="agent-bubble-header">
                      <strong>
                        {lang === 'kn'
                          ? (turn.agent_id === 'agronomist' ? 'ಡಾ. ವಿ. ರಾವ್ (Dr. V. Rao)' : turn.agent_id === 'economist' ? 'ಆರ್. ಕೆ. ಶರ್ಮಾ (R. K. Sharma)' : turn.agent_id === 'pathologist' ? 'ಡಾ. ತಾರಾ ದೇವಿ (Dr. Tara Devi)' : turn.agent_id === 'irrigation_specialist' ? 'ಇಂ. ಆರ್. ಕುಲಕರ್ಣಿ (Er. R. Kulkarni)' : 'ಎಸ್. ಪಾಟೀಲ್ (S. Patil)')
                          : lang === 'hi'
                            ? (turn.agent_id === 'agronomist' ? 'डॉ. वी. राव (Dr. V. Rao)' : turn.agent_id === 'economist' ? 'आर. के. शर्मा (R. K. Sharma)' : turn.agent_id === 'pathologist' ? 'डॉ. तारा देवी (Dr. Tara Devi)' : turn.agent_id === 'irrigation_specialist' ? 'ईं. आर. कुलकर्णी (Er. R. Kulkarni)' : 'एस. पाटिल (S. Patil)')
                            : turn.name}
                      </strong>
                      <span className="agent-role-title">
                        {turn.agent_id === 'agronomist'
                          ? loc('roleAgronomist')
                          : turn.agent_id === 'economist'
                            ? loc('roleEconomist')
                            : turn.agent_id === 'pathologist'
                              ? loc('rolePathologist')
                              : turn.agent_id === 'irrigation_specialist'
                                ? loc('roleIrrigation')
                                : loc('roleRisk')}
                      </span>
                    </div>
                    <p>{localizeTurnStatement(turn)}</p>
                  </div>
                </div>
              ))
            ) : debateLoading ? (
              <div className="debate-typing-indicator">
                <span>{loc('debateTyping')}</span>
              </div>
            ) : null}
          </div>

          {/* Synthesized Consensus Card */}
          {debateData && debateData.consensus_summary && (
            <div className="debate-consensus-card">
              <h3>{loc('debateConsensusTitle')}</h3>
              <p className="consensus-body">{localizeConsensusSummary(debateData.consensus_summary)}</p>
              
              {debateData.key_takeaways && debateData.key_takeaways.length > 0 && (
                <div className="takeaways-box">
                  <h4>{loc('debateTakeawaysTitle')}</h4>
                  <ul>
                    {debateData.key_takeaways.map((item, idx) => (
                      <li key={idx}>✅ {localizeTakeaway(item, idx)}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* TAB 4: REGRET MINIMIZATION PLANS */}
      {activeTab === 'regret' && (
        <div className="di-tab-content regret-view">
          <div className="di-intro-card">
            <p>
              🛡️ <strong>{t('tabRegret')}:</strong> {loc('regretIntro')}
            </p>
          </div>

          {/* Risk Preference Selector */}
          <div className="risk-selector-container">
            <span className="risk-selector-label">{loc('regretPostureLabel')}</span>
            <div className="risk-buttons-row">
              <button
                type="button"
                className={`risk-btn risk-safe ${regretPreference === 'safe' ? 'selected' : ''}`}
                onClick={() => setRegretPreference('safe')}
              >
                {loc('riskSafe')}
              </button>
              <button
                type="button"
                className={`risk-btn risk-balanced ${regretPreference === 'balanced' ? 'selected' : ''}`}
                onClick={() => setRegretPreference('balanced')}
              >
                {loc('riskBalanced')}
              </button>
              <button
                type="button"
                className={`risk-btn risk-aggressive ${regretPreference === 'aggressive' ? 'selected' : ''}`}
                onClick={() => setRegretPreference('aggressive')}
              >
                {loc('riskAggressive')}
              </button>
            </div>
          </div>

          {/* 3-Tier Plans Display */}
          {regretPlans ? (
            <div className="regret-plans-grid">
              {/* Safe Plan Card */}
              <div className={`regret-card card-safe ${regretPreference === 'safe' ? 'active-highlight' : ''}`}>
                <div className="regret-card-badge">{loc('badgeDefensive')}</div>
                <h3>{getLocalizedPlanTitle('safe', regretPlans.safe_plan)}</h3>
                <div className="regret-profit-metric">
                  <span className="regret-profit-val">{getLocalizedPlanProfit(regretPlans.safe_plan)}</span>
                  <span className="regret-profit-label">{loc('regretExpectedProfit')}</span>
                </div>
                <div className="regret-details-list">
                  <p><strong>🌱 {loc('regretVariety')}</strong> {getLocalizedPlanVariety('safe', regretPlans.safe_plan)}</p>
                  <p><strong>🛡️ {loc('regretDownside')}</strong> <span className="downside-safe">{getLocalizedPlanDownside('safe', regretPlans.safe_plan)}</span></p>
                  <p><strong>💰 {loc('regretCapital')}</strong> {getLocalizedPlanCapital('safe', regretPlans.safe_plan)}</p>
                  <p><strong>📋 {loc('regretStrategy')}</strong> {getLocalizedPlanStrategy('safe', regretPlans.safe_plan)}</p>
                  <p><strong>🎯 {loc('regretScore')}</strong> {getLocalizedPlanScore('safe', regretPlans.safe_plan)}</p>
                </div>
              </div>

              {/* Balanced Plan Card */}
              <div className={`regret-card card-balanced ${regretPreference === 'balanced' ? 'active-highlight' : ''}`}>
                <div className="regret-card-badge">{loc('badgeSharpe')}</div>
                <h3>{getLocalizedPlanTitle('balanced', regretPlans.balanced_plan)}</h3>
                <div className="regret-profit-metric">
                  <span className="regret-profit-val">{getLocalizedPlanProfit(regretPlans.balanced_plan)}</span>
                  <span className="regret-profit-label">{loc('regretExpectedProfit')}</span>
                </div>
                <div className="regret-details-list">
                  <p><strong>🌱 {loc('regretVariety')}</strong> {getLocalizedPlanVariety('balanced', regretPlans.balanced_plan)}</p>
                  <p><strong>🛡️ {loc('regretDownside')}</strong> <span className="downside-balanced">{getLocalizedPlanDownside('balanced', regretPlans.balanced_plan)}</span></p>
                  <p><strong>💰 {loc('regretCapital')}</strong> {getLocalizedPlanCapital('balanced', regretPlans.balanced_plan)}</p>
                  <p><strong>📋 {loc('regretStrategy')}</strong> {getLocalizedPlanStrategy('balanced', regretPlans.balanced_plan)}</p>
                  <p><strong>🎯 {loc('regretScore')}</strong> {getLocalizedPlanScore('balanced', regretPlans.balanced_plan)}</p>
                </div>
              </div>

              {/* Aggressive Plan Card */}
              <div className={`regret-card card-aggressive ${regretPreference === 'aggressive' ? 'active-highlight' : ''}`}>
                <div className="regret-card-badge">{loc('badgeAlpha')}</div>
                <h3>{getLocalizedPlanTitle('aggressive', regretPlans.aggressive_plan)}</h3>
                <div className="regret-profit-metric">
                  <span className="regret-profit-val">{getLocalizedPlanProfit(regretPlans.aggressive_plan)}</span>
                  <span className="regret-profit-label">{loc('regretExpectedProfit')}</span>
                </div>
                <div className="regret-details-list">
                  <p><strong>🌱 {loc('regretVariety')}</strong> {getLocalizedPlanVariety('aggressive', regretPlans.aggressive_plan)}</p>
                  <p><strong>🛡️ {loc('regretDownside')}</strong> <span className="downside-aggressive">{getLocalizedPlanDownside('aggressive', regretPlans.aggressive_plan)}</span></p>
                  <p><strong>💰 {loc('regretCapital')}</strong> {getLocalizedPlanCapital('aggressive', regretPlans.aggressive_plan)}</p>
                  <p><strong>📋 {loc('regretStrategy')}</strong> {getLocalizedPlanStrategy('aggressive', regretPlans.aggressive_plan)}</p>
                  <p><strong>🎯 {loc('regretScore')}</strong> {getLocalizedPlanScore('aggressive', regretPlans.aggressive_plan)}</p>
                </div>
              </div>
            </div>
          ) : (
            <p className="loading-text">{loc('regretLoading')}</p>
          )}

          {/* Stress-Test Payoff Matrix Table */}
          {regretPlans && regretPlans.stress_test_matrix && (
            <div className="stress-test-table-card">
              <h3>🧪 {loc('stressTableTitle')}</h3>
              <table className="stress-table">
                <thead>
                  <tr>
                    <th>{loc('thScenario')}</th>
                    <th>{loc('thSafe')}</th>
                    <th>{loc('thBalanced')}</th>
                    <th>{loc('thAggressive')}</th>
                  </tr>
                </thead>
                <tbody>
                  {regretPlans.stress_test_matrix.map((row, idx) => (
                    <tr key={idx}>
                      <td><strong>{getLocalizedScenario(row.scenario)}</strong></td>
                      <td className="gain-pos">{row.safe}</td>
                      <td className="gain-pos">{row.balanced}</td>
                      <td className={row.aggressive?.startsWith('-') ? 'gain-neg' : 'gain-pos'}>{row.aggressive}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
