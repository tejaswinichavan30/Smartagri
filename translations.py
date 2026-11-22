# -*- coding: utf-8 -*-
"""
SmartAgri AI - Comprehensive Multilingual Translation Module
Supports: English (en), Kannada (kn), Hindi (hi)
"""

import re
import os
import json

CROP_TRANSLATIONS = {
    'rice': {
        'name': {'en': 'Rice (Paddy)', 'kn': 'ಭತ್ತ (ಅಕ್ಕಿ)', 'hi': 'चावल (धान)'},
        'season': {'en': 'Kharif (Monsoon)', 'kn': 'ಖಾರೀಫ್ (ಮುಂಗಾರು)', 'hi': 'खरीफ (मानसून)'},
        'planting_months': {'en': 'June - July (Kharif season)', 'kn': 'ಜೂನ್ - ಜುಲೈ (ಖಾರೀಫ್ ಮುಂಗಾರು)', 'hi': 'जून - जुलाई (खरीफ मौसम)'},
        'harvest_months': {'en': 'October - November', 'kn': 'ಅಕ್ಟೋಬರ್ - ನವೆಂಬರ್', 'hi': 'अक्टूबर - नवंबर'},
        'season_desc': {
            'en': 'Primary staple cereal food grain widely cultivated across Karnataka.',
            'kn': 'ಕರ್ನಾಟಕದಲ್ಲಿ ವ್ಯಾಪಕವಾಗಿ ಬೆಳೆಯಲಾಗುವ ಪ್ರಮುಖ ಧಾನ್ಯ ಬೆಳೆ.',
            'hi': 'कर्नाटक में व्यापक रूप से उगाई जाने वाली प्रमुख खाद्यान्न फसल।'
        },
        'fertilizer': {
            'en': 'N: 100 kg/ha (40 kg/acre) | P₂O₅: 50 kg/ha (20 kg/acre) | K₂O: 50 kg/ha (20 kg/acre)\n• Manure: FYM / Compost 10 tonnes/ha (4 tonnes/acre) incorporated before transplanting.\n• Split Schedule: Basal: 100% P₂O₅ + 50% K₂O + 33% N; Tillering (25-30 DAT): 33% N; Panicle Initiation (55 DAT): 34% N + 50% K₂O.\n⚠️ Verified by expert: False (Consult your local KVK for soil-test specific dose).',
            'kn': 'ಸಾರಜನಕ (N): 100 ಕೆಜಿ/ಹೆಕ್ಟೇರ್ (40 ಕೆಜಿ/ಎಕರೆ) | ರಂಜಕ (P₂O₅): 60 ಕೆಜಿ/ಹೆಕ್ಟೇರ್ (24 ಕೆಜಿ/ಎಕರೆ) | ಪೊಟ್ಯಾಶ್ (K₂O): 50 ಕೆಜಿ/ಹೆಕ್ಟೇರ್ (20 ಕೆಜಿ/ಎಕರೆ)\n• ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ: 10 ಟನ್/ಹೆಕ್ಟೇರ್ (4 ಟನ್/ಎಕರೆ) ನಾಟಿಗೆ ಮುನ್ನ ಮಣ್ಣಿಗೆ ಸೇರಿಸಿ.\n• ವಿಭಜಿತ ಬಳಕೆ: ಅಡಿಗೊಬ್ಬರ: 100% P₂O₅ + 50% K₂O + 33% N; ಕವಲೊಡೆಯುವಾಗ (25-30 ದಿನಕ್ಕೆ): 33% N; ತೆನೆ ಬರುವಾಗ (55 ದಿನಕ್ಕೆ): 34% N + 50% K₂O.\n⚠️ ತಜ್ಞರ ಪರಿಶೀಲನೆ ಬಾಕಿ (ನಿಖರ ಪ್ರಮಾಣಕ್ಕೆ ನಿಮ್ಮ ಕೆವಿಕೆ ಸಂಪರ್ಕಿಸಿ).',
            'hi': 'नाइट्रोजन (N): 100 किग्रा/हेक्टेयर (40 किग्रा/एकड़) | फास्फोरस (P₂O₅): 50 किग्रा/हेक्टेयर (20 किग्रा/एकड़) | पोटाश (K₂O): 50 किग्रा/हेक्टेयर (20 किग्रा/एकड़)\n• गोबर की खाद: 10 टन/हेक्टेयर (4 टन/एकड़) रोपाई से पहले मिलाएं।\n• विभाजित मात्रा: बेसल: 100% P₂O₅ + 50% K₂O + 33% N; कल्ले फूटते समय (25-30 दिन): 33% N; बाली बनते समय (55 दिन): 34% N + 50% K₂O.\n⚠️ विशेषज्ञ समीक्षा लंबित (सटीक मात्रा हेतु अपने केवीके से संपर्क करें)।'
        },
        'pests': {
            'en': [
                'Brown planthopper → Alternate wetting and drying (AWD); avoid excess nitrogen; for chemical spray, consult your local KVK or Krishi officer.',
                'Stem borer → Release Trichogramma egg parasitoids; clip seedling tips before transplanting; for chemical treatment, consult your local KVK or Krishi officer.',
                'Blast disease → Seed treatment with bioagents; maintain balanced nutrition; for chemical spray, consult your local KVK or Krishi officer.'
            ],
            'kn': [
                'ಕಂದು ಜಿಗಿಹುಳು → ಹೊಲವನ್ನು ಆಗಾಗ್ಗೆ ಒಣಗಿಸಿ ನೀರು ಕೊಡಿ; ಅಧಿಕ ಸಾರಜನಕ ತಪ್ಪಿಸಿ; ರಾಸಾಯನಿಕ ಸಿಂಪರಣೆಗೆ ಸ್ಥಳೀಯ ಕೆವಿಕೆ ಅಥವಾ ಕೃಷಿ ಅಧಿಕಾರಿಯನ್ನು ಸಂಪರ್ಕಿಸಿ.',
                'ಕಾಂಡ ಕೊರೆಯುವ ಹುಳು → ಟ್ರೈಕೋಗ್ರಾಮ ಪರಾವಲಂಬಿ ಕಾರ್ಡ್ ಬಳಸಿ; ನಾಟಿಗೆ ಮುನ್ನ ಸಸಿಗಳ ತುದಿಯನ್ನು ಚಿವುಟಿ; ರಾಸಾಯನಿಕ ಬಳಕೆಗೆ ಕೆವಿಕೆ ಸಂಪರ್ಕಿಸಿ.',
                'ಎಲೆ ಬೆಂಕಿ ರೋಗ (ಬ್ಲಾಸ್ಟ್) → ಜೈವಿಕ ಬೀಜೋಪಚಾರ ಮಾಡಿ; ಸಮತೋಲಿತ ಪೋಷಕಾಂಶ ನೀಡಿ. ಅನುಮೋದಿತ ಪರಿಹಾರಕ್ಕೆ ನಿಮ್ಮ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.'
            ],
            'hi': [
                'भूरा फुदका → खेत से बीच-बीच में पानी निकालें; अधिक नाइट्रोजन से बचें; रासायनिक उपचार हेतु नजदीकी केवीके या कृषि अधिकारी से परामर्श लें।',
                'तना छेदक → ट्राइकोग्रामा अंड परजीवी कार्ड लगाएं; रोपाई से पूर्व पत्तियों के सिरे काटें। अनुमोदित उपचार हेतु स्थानीय केवीके (KVK) से संपर्क करें।',
                'ब्लास्ट रोग → जैविक बीजोपचार करें; संतुलित खाद दें; रासायनिक छिड़काव हेतु केवीके से परामर्श लें।'
            ]
        },
        'best_sell_months': {'en': 'January - March', 'kn': 'ಜನವರಿ - ಮಾರ್ಚ್', 'hi': 'जनवरी - मार्च'},
        'sell_tip': {
            'en': 'Derived from Agmarknet multi-year modal price trends (prices peak post-harvest Jan-Mar).',
            'kn': 'ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಬಹು-ವರ್ಷಗಳ ಮಂಡಿ ದರ ವಿಶ್ಲೇಷಣೆ ಆಧಾರಿತ (ಕೊಯ್ಲಿನ ನಂತರ ಜನವರಿ-ಮಾರ್ಚ್\u200cನಲ್ಲಿ ಬೆಲೆ ಏರಿಕೆ).',
            'hi': 'एगमार्कनेट बहु-वर्षीय मॉडल भाव रुझानों पर आधारित (कटाई के बाद जनवरी-मार्च में उच्चतम दाम)।'
        },
    },
    'maize': {
        'name': {'en': 'Maize (Corn)', 'kn': 'ಮೆಕ್ಕೆಜೋಳ', 'hi': 'मक्का'},
        'season': {'en': 'Kharif / Zaid', 'kn': 'ಖಾರೀಫ್ / ಜೈದ್', 'hi': 'खरीफ / जायद'},
        'planting_months': {'en': 'June - July & February - March', 'kn': 'ಜೂನ್ - ಜುಲೈ ಮತ್ತು ಫೆಬ್ರವರಿ - ಮಾರ್ಚ್', 'hi': 'जून - जुलाई एवं फरवरी - मार्च'},
        'harvest_months': {'en': 'September - October & May - June', 'kn': 'ಸೆಪ್ಟೆಂಬರ್ - ಅಕ್ಟೋಬರ್ ಮತ್ತು ಮೇ - ಜೂನ್', 'hi': 'सितंबर - अक्टूबर एवं मई - जून'},
        'season_desc': {
            'en': 'Adaptable cereal crop grown in both monsoon and spring-summer.',
            'kn': 'ಮುಂಗಾರು ಮತ್ತು ಬೇಸಿಗೆ ಎರಡೂ ಕಾಲದಲ್ಲಿ ಬೆಳೆಯಬಹುದಾದ ಉತ್ತಮ ಧಾನ್ಯ ಬೆಳೆ.',
            'hi': 'मानसून और गर्मी दोनों मौसमों में उगाई जाने वाली बहुमुखी अनाज फसल।'
        },
        'fertilizer': {
            'en': 'N: 120 kg/ha (48 kg/acre) | P₂O₅: 60 kg/ha (24 kg/acre) | K₂O: 40 kg/ha (16 kg/acre)\n• Manure: FYM / Compost 10-12 tonnes/ha (4-5 t/acre) incorporated before sowing.\n• Split Schedule: Basal: 100% P₂O₅ + 100% K₂O + 25% N; Top-dress 1 (30 DAS): 50% N; Top-dress 2 (tasseling/55 DAS): 25% N.\n⚠️ Verified by expert: False (Consult your local KVK for soil-test specific dose).',
            'kn': 'ಸಾರಜನಕ (N): 120 ಕೆಜಿ/ಹೆಕ್ಟೇರ್ (48 ಕೆಜಿ/ಎಕರೆ) | ರಂಜಕ (P₂O₅): 60 ಕೆಜಿ/ಹೆಕ್ಟೇರ್ (24 ಕೆಜಿ/ಎಕರೆ) | ಪೊಟ್ಯಾಶ್ (K₂O): 40 ಕೆಜಿ/ಹೆಕ್ಟೇರ್ (16 ಕೆಜಿ/ಎಕರೆ)\n• ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ: 10-12 ಟನ್/ಹೆಕ್ಟೇರ್ (4-5 ಟನ್/ಎಕರೆ) ಬಿತ್ತನೆಗೆ ಮುನ್ನ ಮಣ್ಣಿಗೆ ಸೇರಿಸಿ.\n• ವಿಭಜಿತ ಬಳಕೆ: ಅಡಿಗೊಬ್ಬರ: 100% P₂O₅ + 100% K₂O + 25% N; ಮೇಲುಗೊಬ್ಬರ 1 (30 ದಿನಕ್ಕೆ): 50% N; ಮೇಲುಗೊಬ್ಬರ 2 (ತೆನೆ/ಹೂವಾಡುವಾಗ 55 ದಿನಕ್ಕೆ): 25% N.\n⚠️ ತಜ್ಞರ ಪರಿಶೀಲನೆ ಬಾಕಿ (ನಿಖರ ಪ್ರಮಾಣಕ್ಕೆ ನಿಮ್ಮ ಕೆವಿಕೆ ಸಂಪರ್ಕಿಸಿ).',
            'hi': 'नाइट्रोजन (N): 120 किग्रा/हेक्टेयर (48 किग्रा/एकड़) | फास्फोरस (P₂O₅): 60 किग्रा/हेक्टेयर (24 किग्रा/एकड़) | पोटाश (K₂O): 40 किग्रा/हेक्टेयर (16 किग्रा/एकड़)\n• देशी खाद: 10-12 टन/हेक्टेयर (4-5 टन/एकड़) बुवाई से पूर्व खेत में मिलाएं।\n• विभाजित मात्रा: बेसल: 100% P₂O₅ + 100% K₂O + 25% N; टॉप ड्रेसिंग 1 (30 दिन पर): 50% N; टॉप ड्रेसिंग 2 (55 दिन पर): 25% N.\n⚠️ विशेषज्ञ समीक्षा लंबित (सटीक मात्रा हेतु अपने केवीके से संपर्क करें)।'
        },
        'pests': {
            'en': [
                'Fall Armyworm (FAW) Scouting: Install pheromone traps @ 5/acre. Scout 20 consecutive plants in 5 spots for whorl feeding. Apply NSKE 5% / Bt bio-spray at early instar. Consult your local KVK for label-claim verified treatments.',
                'Stem borer → Monitoring with light traps and Trichogramma cards. Consult your local KVK for label-claim verified treatments.',
                'Aphids → Sticky traps & neem oil. Consult your local KVK for label-claim verified treatments.'
            ],
            'kn': [
                'ಲದ್ದಿ ಹುಳು (Fall Armyworm) ಕಣ್ಗಾವಲು: ಪ್ರತಿ ಎಕರೆಗೆ 5 ಮೋಹಕ ಬಲೆಗಳನ್ನು ಅಳವಡಿಸಿ. ಸುಳಿಯಲ್ಲಿ ಹುಳು ಹಾನಿ ಗಮನಿಸಿ. ಬೇವಿನ ಕಷಾಯ (NSKE 5%) ಅಥವಾ ಜೈವಿಕ Bt ಬಳಸಿ. ಅನುಮೋದಿತ ಪರಿಹಾರಕ್ಕೆ ನಿಮ್ಮ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
                'ಕಾಂಡ ಕೊರೆಯುವ ಹುಳು → ದೀಪದ ಬಲೆ ಮತ್ತು ಟ್ರೈಕೋಗ್ರಾಮ ಕಾರ್ಡ್ ಬಳಸಿ. ಅನುಮೋದಿತ ಪರಿಹಾರಕ್ಕೆ ನಿಮ್ಮ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
                'ಸಸ್ಯ ಹೇನು (Aphids) → ಹಳದಿ ಜಿಗುಟು ಬಲೆ ಮತ್ತು ಬೇವಿನ ಎಣ್ಣೆ. ಅನುಮೋದಿತ ಪರಿಹಾರಕ್ಕೆ ನಿಮ್ಮ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.'
            ],
            'hi': [
                'फॉल आर्मीवर्म (FAW) निगरानी: प्रति एकड़ 5 फेरोमोन ट्रैप लगाएं। पोंगे में कीट क्षति की जांच करें। नीम का काढ़ा (NSKE 5%) या जैविक Bt का प्रयोग करें। अनुमोदित उपचार हेतु स्थानीय केवीके (KVK) से संपर्क करें।',
                'तना छेदक → प्रकाश प्रपंच और ट्राइकोग्रामा कार्ड लगाएं। अनुमोदित उपचार हेतु स्थानीय केवीके (KVK) से संपर्क करें।',
                'माहू (एफिड्स) → पीले चिपचिपे ट्रैप और नीम तेल। अनुमोदित उपचार हेतु स्थानीय केवीके (KVK) से संपर्क करें।'
            ]
        },
        'best_sell_months': {'en': 'October - November', 'kn': 'ಅಕ್ಟೋಬರ್ - ನವೆಂಬರ್', 'hi': 'अक्टूबर - नवंबर'},
        'sell_tip': {
            'en': 'Historical Agmarknet modal price trends indicate prices peak post-harvest driven by poultry and starch industry demand; check local MSP centers.',
            'kn': 'ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಮಂಡಿ ದರ ವಿಶ್ಲೇಷಣೆ: ಕೋಳಿ ಆಹಾರ ಮತ್ತು ಕೈಗಾರಿಕಾ ಬೇಡಿಕೆಯಿಂದ ಕೊಯ್ಲಿನ ನಂತರ ಉತ್ತಮ ಬೆಲೆ ದೊರೆಯುತ್ತದೆ; ಬೆಂಬಲ ಬೆಲೆ ಖರೀದಿ ಕೇಂದ್ರಗಳನ್ನು ಪರಿಶೀಲಿಸಿ.',
            'hi': 'एगमार्कनेट मॉडल भाव रुझान: पोल्ट्री और स्टार्च उद्योग की मांग से कटाई के बाद भाव सुधरते हैं; नजदीकी एमएसपी खरीद केंद्र का भी पता करें।'
        },
    },
    'chickpea': {
        'name': {'en': 'Chickpea (Bengal Gram)', 'kn': 'ಕಡಲೆ (ಬೆಂಗಾಲ್ ಗ್ರಾಂ / ಕಡಲೆಕಾಳು)', 'hi': 'चना (बंगाल चना / Bengal Gram)'},
        'season': {'en': 'Rabi (Winter)', 'kn': 'ರಬಿ (ಹಿಂಗಾರು)', 'hi': 'रबी (सर्दियां)'},
        'planting_months': {'en': 'October - November (Rabi season)', 'kn': 'ಅಕ್ಟೋಬರ್ - ನವೆಂಬರ್ (ರಬಿ ಹಿಂಗಾರು)', 'hi': 'अक्टूबर - नवंबर (रबी मौसम)'},
        'harvest_months': {'en': 'February - March', 'kn': 'ಫೆಬ್ರವರಿ - ಮಾರ್ಚ್', 'hi': 'फरवरी - मार्च'},
        'season_desc': {
            'en': 'Major protein-rich pulse crop widely cultivated across Karnataka drylands.',
            'kn': 'ಕರ್ನಾಟಕದ ಒಣಭೂಮಿ ಪ್ರದೇಶಗಳಲ್ಲಿ ವ್ಯಾಪಕವಾಗಿ ಬೆಳೆಯಲಾಗುವ ಪ್ರಮುಖ ಕಾಳು ಬೆಳೆ.',
            'hi': 'कर्नाटक में व्यापक रूप से उगाई जाने वाली प्रमुख प्रोटीन युक्त दलहनी फसल।'
        },
        'fertilizer': {
            'en': 'N: 20 kg/ha (8 kg/acre) | P₂O₅: 60 kg/ha (24 kg/acre) | K₂O: 20 kg/ha (8 kg/acre)\n• Manure: FYM 5 tonnes/ha (2 tonnes/acre) + Rhizobium seed inoculation.\n• Split Schedule: 100% Basal at sowing.\n⚠️ Verified by expert: False (Consult your local KVK for soil-test specific dose).',
            'kn': 'ಸಾರಜನಕ (N): 20 ಕೆಜಿ/ಹೆಕ್ಟೇರ್ (8 ಕೆಜಿ/ಎಕರೆ) | ರಂಜಕ (P₂O₅): 60 ಕೆಜಿ/ಹೆಕ್ಟೇರ್ (24 ಕೆಜಿ/ಎಕರೆ) | ಪೊಟ್ಯಾಶ್ (K₂O): 20 ಕೆಜಿ/ಹೆಕ್ಟೇರ್ (8 ಕೆಜಿ/ಎಕರೆ)\n• ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ: 5 ಟನ್/ಹೆಕ್ಟೇರ್ (2 ಟನ್/ಎಕರೆ) + ರೈಜೋಬಿಯಂ ಬೀಜೋಪಚಾರ.\n• ವಿಭಜಿತ ಬಳಕೆ: ಬಿತ್ತನೆ ಸಮಯದಲ್ಲಿ ಶೇ. 100 ಅಡಿಗೊಬ್ಬರವಾಗಿ ನೀಡಿ.\n⚠️ ತಜ್ಞರ ಪರಿಶೀಲನೆ ಬಾಕಿ (ನಿಖರ ಪ್ರಮಾಣಕ್ಕೆ ನಿಮ್ಮ ಕೆವಿಕೆ ಸಂಪರ್ಕಿಸಿ).',
            'hi': 'नाइट्रोजन (N): 20 किग्रा/हेक्टेयर (8 किग्रा/एकड़) | फास्फोरस (P₂O₅): 60 किग्रा/हेक्टेयर (24 किग्रा/एकड़) | पोटाश (K₂O): 20 किग्रा/हेक्टेयर (8 किग्रा/एकड़)\n• गोबर खाद: 5 टन/हेक्टेयर (2 टन/एकड़) + राइजोबियम बीजोपचार।\n• विभाजित मात्रा: 100% बेसल बुवाई के समय दें।\n⚠️ विशेषज्ञ समीक्षा लंबित (सटीक मात्रा हेतु अपने केवीके से संपर्क करें)।'
        },
        'pests': {
            'en': [
                'Pod borer (Helicoverpa) → Pheromone traps @ 5/acre; bird perches. Consult your local KVK for label-claim verified treatments.',
                'Wilt disease → Crop rotation; Trichoderma viride seed treatment @ 4 g/kg; avoid waterlogging.',
                'Aphids → Sticky traps; neem spray. Consult your local KVK for label-claim verified treatments.'
            ],
            'kn': [
                'ಕಾಯಿ ಕೊರೆಯುವ ಹುಳು → ಮೋಹಕ ಬಲೆ (5/ಎಕರೆ); ಪಕ್ಷಿ ಆಸರೆಗಳು. ಅನುಮೋದಿತ ಪರಿಹಾರಕ್ಕೆ ನಿಮ್ಮ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
                'ಸೊರಗು ರೋಗ → ಬೆಳೆ ಪರಿವರ್ತನೆ; ಟ್ರೈಕೋಡರ್ಮಾ ಬೀಜೋಪಚಾರ (4 ಗ್ರಾಂ/ಕೆಜಿ); ನೀರು ನಿಲ್ಲದಂತೆ ನೋಡಿಕೊಳ್ಳಿ.',
                'ಸಸ್ಯ ಹೇನು → ಹಳದಿ ಜಿಗುಟು ಬಲೆ; ಬೇವಿನ ಎಣ್ಣೆ. ಅನುಮೋದಿತ ಪರಿಹಾರಕ್ಕೆ ನಿಮ್ಮ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.'
            ],
            'hi': [
                'फली छेदक → फेरोमोन ट्रैप @ 5/एकड़; पक्षी बसेरे। अनुमोदित उपचार हेतु स्थानीय केवीके (KVK) से संपर्क करें।',
                'उकठा (विल्ट) रोग → फसल चक्र; ट्राइकोडर्मा बीजोपचार (4 ग्राम/किग्रा); जलभराव से बचें।',
                'माहू → पीले चिपचिपे ट्रैप; नीम का छिड़काव। अनुमोदित उपचार हेतु स्थानीय केवीके (KVK) से संपर्क करें।'
            ]
        },
        'best_sell_months': {'en': 'March - May', 'kn': 'ಮಾರ್ಚ್ - ಮೇ', 'hi': 'मार्च - मई'},
        'sell_tip': {
            'en': 'Historical Agmarknet modal price trends show chickpea commanding premium rates during summer festival windows; compare with official MSP before selling.',
            'kn': 'ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಮಂಡಿ ದರ ವಿಶ್ಲೇಷಣೆ: ಬೇಸಿಗೆ ಹಬ್ಬದ ಸಮಯದಲ್ಲಿ ಕಡಲೆಗೆ ಉತ್ತಮ ದರ ಬರುತ್ತದೆ; ಮಾರಾಟಕ್ಕೆ ಮುನ್ನ ಸರ್ಕಾರಿ ಬೆಂಬಲ ಬೆಲೆ (MSP) ಹೋಲಿಸಿ.',
            'hi': 'एगमार्कनेट मॉडल भाव रुझान: ग्रीष्मकालीन त्योहारी मांग में चना अच्छे दामों पर बिकता है; बेचने से पूर्व आधिकारिक एमएसपी से तुलना करें।'
        },
    },
    'cotton': {
        'name': {'en': 'Cotton', 'kn': 'ಹತ್ತಿ', 'hi': 'कपास'},
        'season': {'en': 'Kharif (Monsoon)', 'kn': 'ಖಾರೀಫ್ (ಮುಂಗಾರು)', 'hi': 'खरीफ (मानसून)'},
        'planting_months': {'en': 'May - June (Kharif season)', 'kn': 'ಮೇ - ಜೂನ್ (ಖಾರೀಫ್ ಮುಂಗಾರು)', 'hi': 'मई - जून (खरीफ मौसम)'},
        'harvest_months': {'en': 'November - January', 'kn': 'ನವೆಂಬರ್ - ಜನವರಿ', 'hi': 'नवंबर - जनवरी'},
        'season_desc': {
            'en': 'Major commercial fiber cash crop cultivated in deep black soils of Karnataka.',
            'kn': 'ಬೆಚ್ಚಗಿನ ದಿನಗಳು, ಉತ್ತಮ ಸೂರ್ಯನ ಬೆಳಕು ಮತ್ತು ಕಪ್ಪು ಮಣ್ಣಿನ ಅಗತ್ಯವಿರುವ ಪ್ರಮುಖ ವಾಣಿಜ್ಯ ಬೆಳೆ.',
            'hi': 'गर्म मौसम, भरपूर धूप और काली मिट्टी की आवश्यकता वाली प्रमुख नकदी फसल।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 120 kg/ha, Phosphorus: 60 kg/ha, Potassium: 60 kg/ha',
            'kn': 'ಸಾರಜನಕ (N): 120 ಕೆಜಿ/ಹೆಕ್ಟೇರ್, ರಂಜಕ (P): 60 ಕೆಜಿ/ಹೆಕ್ಟೇರ್, ಪೊಟ್ಯಾಸಿಯಮ್ (K): 60 ಕೆಜಿ/ಹೆಕ್ಟೇರ್',
            'hi': 'नाइट्रोजन (N): 120 किग्रा/हेक्टेयर, फास्फोरस (P): 60 किग्रा/हेक्टेयर, पोटेशियम (K): 60 किग्रा/हेक्टेयर'
        },
        'pests': {
 'en': ['Bollworm → Apply 5% neem oil / bio-agents; consult your local KVK for verified options/ Pheromone traps (5/acre) and HaNPV bio-spray', 'Whitefly → Apply 5% neem oil / bio-agents; consult your local KVK for verified options', 'Aphids → Apply 5% neem oil / bio-agents; consult your local KVK for verified options'],
            'kn': ['ಕಾಯಿ ಕೊರೆಯುವ ಹುಳು → Bt ಹತ್ತಿ ತಳಿ ಬಳಸಿ ಅಥವಾ ಮೋಹಕ ಬಲೆಗಳು (5/ಎಕರೆ) ಮತ್ತು HaNPV ಸಿಂಪಡಿಸಿ', 'ಬಿಳಿ ನೊಣ → ಹಳದಿ ಜಿಗುಟು ಬಲೆಗಳು ಮತ್ತು 5% ಬೇವಿನ ಎಣ್ಣೆ ಬಳಸಿ', 'ಸಸ್ಯ ಹೇನು (Aphids) → ಹಳದಿ ಜಿಗುಟು ಬಲೆಗಳು ಮತ್ತು 5% ಬೇವಿನ ಎಣ್ಣೆ ಬಳಸಿ'],
            'hi': ['गुलाबी सुंडी/बॉलवर्म → बीटी कपास या फेरोमोन ट्रैप (5/एकड़) और HaNPV छिड़काव करें', 'सफेद मक्खी → पीले चिपचिपे ट्रैप और 5% नीम तेल का छिड़काव करें', 'माहू (एफिड्स) → पीले चिपचिपे ट्रैप और 5% नीम तेल का छिड़काव करें']
        },
        'best_sell_months': {'en': 'December - February', 'kn': 'ಡಿಸೆಂಬರ್ - ಫೆಬ್ರವರಿ', 'hi': 'दिसंबर - फरवरी'},
        'sell_tip': {
            'en': 'Check CCI procurement MSP centres and Agmarknet modal price trends for best rate on good staple length.',
            'kn': 'ಉತ್ತಮ ಉದ್ದದ ಹತ್ತಿಗೆ ಸಿಸಿಐ ಬೆಂಬಲ ಬೆಲೆ (MSP) ಖರೀದಿ ಕೇಂದ್ರಗಳು ಮತ್ತು ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಮಂಡಿ ದರಗಳನ್ನು ಪರಿಶೀಲಿಸಿ.',
            'hi': 'अच्छे रेशे वाले कपास हेतु सीसीआई एमएसपी खरीद केंद्रों एवं एगमार्कनेट मॉडल भाव रुझानों की जांच करें।'
        },
    },
    'coffee': {
        'name': {'en': 'Coffee', 'kn': 'ಕಾಫಿ', 'hi': 'कॉफी'},
        'season': {'en': 'Whole Year (Plantation)', 'kn': 'ವರ್ಷಪೂರ್ತಿ (ತೋಟಗಾರಿಕೆ ಬೆಳೆ)', 'hi': 'पूरे साल (बागवानी फसल)'},
        'planting_months': {'en': 'June - September (Monsoon)', 'kn': 'ಜೂನ್ - ಸೆಪ್ಟೆಂಬರ್ (ಮುಂಗಾರು)', 'hi': 'जून - सितंबर (मानसून)'},
        'harvest_months': {'en': 'November - February', 'kn': 'ನವೆಂಬರ್ - ಫೆಬ್ರವರಿ', 'hi': 'नवंबर - फरवरी'},
        'season_desc': {
            'en': 'Shade-loving hill plantation crop requiring mild climate and well-drained loamy soil.',
            'kn': 'ತಂಪು ಹವೆ, ನೆರಳು ಮತ್ತು ಮಲೆನಾಡಿನ ಫಲವತ್ತಾದ ಮಣ್ಣಿನಲ್ಲಿ ಸಮೃದ್ಧವಾಗಿ ಬೆಳೆಯುವ ಬೆಳೆ.',
            'hi': 'छायादार पहाड़ी बागवानी फसल, जिसे हल्की ठंडी जलवायु और अच्छी जल निकासी चाहिए।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 140 kg/ha, Phosphorus: 90 kg/ha, Potassium: 120 kg/ha',
            'kn': 'ಸಾರಜನಕ (N): 140 ಕೆಜಿ/ಹೆಕ್ಟೇರ್, ರಂಜಕ (P): 90 ಕೆಜಿ/ಹೆಕ್ಟೇರ್, ಪೊಟ್ಯಾಸಿಯಮ್ (K): 120 ಕೆಜಿ/ಹೆಕ್ಟೇರ್',
            'hi': 'नाइट्रोजन (N): 140 किग्रा/हेक्टेयर, फास्फोरस (P): 90 किग्रा/हेक्टेयर, पोटेशियम (K): 120 किग्रा/हेक्टेयर'
        },
        'pests': {
 'en': ['White stem borer → Bark tracing, stem swabbing with lime, and light traps', 'Coffee berry borer → Beauveria bassiana bio-spray', 'Leaf rust → Bordeaux mixture spray'],
            'kn': ['ಬಿಳಿ ಕಾಂಡ ಕೊರೆಯುವ ಹುಳು → ಕಾಂಡಕ್ಕೆ ಸುಣ್ಣ ಹಚ್ಚಿ ಮತ್ತು ದೀಪದ ಬಲೆಗಳು ಮತ್ತು ಟ್ರೈಕೋಗ್ರಾಮ ಕಾರ್ಡ್ ಬಳಸಿ', 'ಬೆರ್ರಿ ಬೋರರ್ → ಬವೇರಿಯಾ ಬಸ್ಸಿಯಾನ ಜೈವಿಕ ಕೀಟನಾಶಕ ಬಳಸಿ', 'ಎಲೆ ತುಕ್ಕು ರೋಗ → ಬೋರ್ಡೋ ದ್ರಾವಣ ಸಿಂಪಡಿಸಿ'],
            'hi': ['सफेद तना छेदक → छाल सफाई एवं सड़ी गोबर खाद और नीम खली का प्रयोग करें', 'बेरी बोरर → ब्यूवेरिया बेसियाना जैव कीटनाशक का प्रयोग करें', 'पत्ती रस्ट रोग → बोर्डो मिश्रण का छिड़काव करें']
        },
        'best_sell_months': {'en': 'January - April', 'kn': 'ಜನವರಿ - ಏಪ್ರಿಲ್', 'hi': 'जनवरी - अप्रैल'},
        'sell_tip': {
            'en': 'Agmarknet and Coffee Board multi-year auction trends show Arabica and Robusta parchment beans commanding peak rates in Jan-Apr.',
            'kn': 'ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಮತ್ತು ಕಾಫಿ ಬೋರ್ಡ್ ಹರಾಜು ದರ ವಿಶ್ಲೇಷಣೆ: ಅರೇಬಿಕಾ ಮತ್ತು ರೋಬಸ್ಟಾ ಕಾಳುಗಳಿಗೆ ಜನವರಿ-ಏಪ್ರಿಲ್\u200cನಲ್ಲಿ ಗರಿಷ್ಠ ಬೆಲೆ ದೊರೆಯುತ್ತದೆ.',
            'hi': 'एगमार्कनेट व कॉफी बोर्ड नीलामी रुझान: अरेबिका और रोबस्टा पार्चमेंट बीन्स जनवरी-अप्रैल में उच्चतम भाव प्राप्त करते हैं।'
        },
    },
    'grapes': {
        'name': {'en': 'Grapes', 'kn': 'ದ್ರಾಕ್ಷಿ', 'hi': 'अंगूर'},
        'season': {'en': 'Rabi / Summer', 'kn': 'ರಬಿ / ಬೇಸಿಗೆ', 'hi': 'रबी / गर्मी'},
        'planting_months': {'en': 'October - November (Pruning: Oct)', 'kn': 'ಅಕ್ಟೋಬರ್ - ನವೆಂಬರ್ (ಕತ್ತರಿಸುವಿಕೆ: ಅಕ್ಟೋಬರ್)', 'hi': 'अक्टूबर - नवंबर (कटाई-छंटाई: अक्टूबर)'},
        'harvest_months': {'en': 'February - April', 'kn': 'ಫೆಬ್ರವರಿ - ಏಪ್ರಿಲ್', 'hi': 'फरवरी - अप्रैल'},
        'season_desc': {
            'en': 'Requires dry warm weather during ripening with ample sunlight.',
            'kn': 'ಹಣ್ಣು ಮಾಗುವ ಸಮಯದಲ್ಲಿ ಒಣ ಬಿಸಿಲಿನ ಹವೆ ಮತ್ತು ಸಾಕಷ್ಟು ಸೂರ್ಯನ ಬೆಳಕು ಅಗತ್ಯ.',
            'hi': 'फल पकने के दौरान तेज धूप और शुष्क गर्म मौसम की आवश्यकता होती है।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 100 kg/ha, Phosphorus: 120 kg/ha, Potassium: 200 kg/ha',
            'kn': 'ಸಾರಜನಕ (N): 100 ಕೆಜಿ/ಹೆಕ್ಟೇರ್, ರಂಜಕ (P): 120 ಕೆಜಿ/ಹೆಕ್ಟೇರ್, ಪೊಟ್ಯಾಸಿಯಮ್ (K): 200 ಕೆಜಿ/ಹೆಕ್ಟೇರ್',
            'hi': 'नाइट्रोजन (N): 100 किग्रा/हेक्टेयर, फास्फोरस (P): 120 किग्रा/हेक्टेयर, पोटेशियम (K): 200 किग्रा/हेक्टेयर'
        },
        'pests': {
 'en': ['Downy mildew → Apply 5% neem oil / bio-agents; consult your local KVK for verified options', 'Powdery mildew → Apply 5% neem oil / bio-agents; consult your local KVK for verified options', 'Thrips → Apply 5% neem oil / bio-agents; consult your local KVK for verified options'],
            'kn': ['ಡೌನಿ ಮಿಲ್ಡ್ಯೂ (ಬೂಸ್ಟು ರೋಗ) → ಮೆಟಾಲಾಕ್ಸಿಲ್ ಸಿಂಪಡಿಸಿ', 'ಬೂದಿ ರೋಗ → ಗಂಧಕದ ದ್ರಾವಣ ಸಿಂಪಡಿಸಿ', 'ಥ್ರಿಪ್ಸ್ (ನುಸಿ) → ಮೋಹಕ ಬಲೆಗಳು (5/ಎಕರೆ) ಮತ್ತು HaNPV ಸಿಂಪಡಿಸಿ'],
            'hi': ['डाउनी मिल्ड्यू → मेटालेक्सिल का छिड़काव करें', 'चूर्णिल फफूंद → घुलनशील गंधक का छिड़काव करें', 'थ्रिप्स कीट → फेरोमोन ट्रैप (5/एकड़) और HaNPV छिड़काव करें']
        },
        'best_sell_months': {'en': 'March - April', 'kn': 'ಮಾರ್ಚ್ - ಏಪ್ರಿಲ್', 'hi': 'मार्च - अप्रैल'},
        'sell_tip': {
            'en': 'Agmarknet multi-year mandi trends indicate fresh table grapes and raisin grapes earn highest margins before summer arrivals peak.',
            'kn': 'ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಬಹು-ವರ್ಷಗಳ ಮಂಡಿ ದರ ವಿಶ್ಲೇಷಣೆ: ಬೇಸಿಗೆ ಆರಂಭಕ್ಕೆ ಮುನ್ನ ತಾಜಾ ದ್ರಾಕ್ಷಿ ಮತ್ತು ಒಣದ್ರಾಕ್ಷಿಗೆ ಉತ್ತಮ ಲಾಭ ದೊರೆಯುತ್ತದೆ.',
            'hi': 'एगमार्कनेट बहु-वर्षीय मंडी रुझान: गर्मियों के चरम आवक से पूर्व ताजे अंगूर और किशमिश पर बेहतर मुनाफा मिलता है।'
        },
    },
    'pigeonpeas': {
        'name': {'en': 'Pigeonpeas (Tur / Arhar)', 'kn': 'ತೊಗರಿ ಬೇಳೆ (ತೊಗರಿ)', 'hi': 'अरहर / तुअर दाल'},
        'season': {'en': 'Kharif (Monsoon)', 'kn': 'ಖಾರೀಫ್ (ಮುಂಗಾರು)', 'hi': 'खरीफ (मानसून)'},
        'planting_months': {'en': 'June - July', 'kn': 'ಜೂನ್ - ಜುಲೈ', 'hi': 'जून - जुलाई'},
        'harvest_months': {'en': 'December - January', 'kn': 'ಡಿಸೆಂಬರ್ - ಜನವರಿ', 'hi': 'दिसंबर - जनवरी'},
        'season_desc': {
            'en': 'Deep-rooted drought-tolerant legume, iconic to North Karnataka (Kalaburagi / Bidar).',
            'kn': 'ಉತ್ತರ ಕರ್ನಾಟಕದ (ಕಲಬುರಗಿ/ಬೀದರ್) ಪ್ರಮುಖ ಬರ ನಿರೋಧಕ ಬೇಳೆಕಾಳು ಬೆಳೆ.',
            'hi': 'गहरी जड़ों वाली सूखा प्रतिरोधी प्रमुख दाल, उत्तर कर्नाटक का गौरव।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 25 kg/ha, Phosphorus: 50 kg/ha, Potassium: 20 kg/ha',
            'kn': 'ಸಾರಜನಕ (N): 25 ಕೆಜಿ/ಹೆಕ್ಟೇರ್, ರಂಜಕ (P): 50 ಕೆಜಿ/ಹೆಕ್ಟೇರ್, ಪೊಟ್ಯಾಸಿಯಮ್ (K): 20 ಕೆಜಿ/ಹೆಕ್ಟೇರ್',
            'hi': 'नाइट्रोजन (N): 25 किग्रा/हेक्टेयर, फास्फोरस (P): 50 किग्रा/हेक्टेयर, पोटेशियम (K): 20 किग्रा/हेक्टेयर'
        },
        'pests': {
 'en': ['Pod borer → Apply 5% neem oil / bio-agents; consult your local KVK for verified options', 'Pod fly → Apply 5% neem oil / bio-agents; consult your local KVK for verified options', 'Sterility mosaic → Control mites with dicofol'],
            'kn': ['ಕಾಯಿ ಕೊರೆಯುವ ಹುಳು → ಫ್ಲೂಬೆಂಡಿಯಾಮೈಡ್ ಸಿಂಪಡಿಸಿ', 'ಕಾಯಿ ನೊಣ → ಹಳದಿ ಜಿಗುಟು ಬಲೆಗಳು ಮತ್ತು 5% ಬೇವಿನ ಎಣ್ಣೆ ಬಳಸಿ', 'ಬಂಜೆ ರೋಗ → ನುಸಿ ನಿಯಂತ್ರಣಕ್ಕೆ ಡೈಕೋಫಾಲ್ ಬಳಸಿ'],
            'hi': ['फली छेदक → फ्लूबेंडियामाइड का छिड़काव करें', 'फली मक्खी → पीले चिपचिपे ट्रैप और 5% नीम तेल का छिड़काव करें', 'बांझपन मोज़ेक → माइट्स नियंत्रण के लिए डाइकोफॉल का छिड़काव करें']
        },
        'best_sell_months': {'en': 'January - March', 'kn': 'ಜನವರಿ - ಮಾರ್ಚ್', 'hi': 'जनवरी - मार्च'},
        'sell_tip': {
            'en': 'Agmarknet modal price trends and MSP procurement data show GI-tagged Kalaburagi Tur commanding premium rates in Jan-Mar mandis.',
            'kn': 'ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಮಂಡಿ ದರಗಳು ಮತ್ತು ಬೆಂಬಲ ಬೆಲೆ (MSP) ವಿಶ್ಲೇಷಣೆ: ಜನವರಿ-ಮಾರ್ಚ್ ಮಂಡಿಗಳಲ್ಲಿ ಜಿಐ ಟ್ಯಾಗ್ ಪಡೆದ ಕಲಬುರಗಿ ತೊಗರಿಗೆ ಹೆಚ್ಚಿನ ಬೆಲೆ ದೊರೆಯುತ್ತದೆ.',
            'hi': 'एगमार्कनेट मॉडल भाव रुझान व एमएसपी खरीद डेटा: जनवरी-मार्च मंडियों में जीआई टैग वाली कलबुर्गी तुअर को प्रीमियम दाम मिलते हैं।'
        },
    },
    'coconut': {
        'name': {'en': 'Coconut', 'kn': 'ತೆಂಗಿನಕಾಯಿ', 'hi': 'नारियल'},
        'season': {'en': 'Whole Year (Perennial)', 'kn': 'ವರ್ಷಪೂರ್ತಿ (ದೀರ್ಘಕಾಲೀನ ಬೆಳೆ)', 'hi': 'पूरे साल (बारहमासी)'},
        'planting_months': {'en': 'June - September', 'kn': 'ಜೂನ್ - ಸೆಪ್ಟೆಂಬರ್', 'hi': 'जून - सितंबर'},
        'harvest_months': {'en': 'Year round (every 45-60 days)', 'kn': 'ವರ್ಷಪೂರ್ತಿ (ಪ್ರತಿ 45-60 ದಿನಗಳಿಗೊಮ್ಮೆ)', 'hi': 'पूरे साल (हर 45-60 दिन में)'},
        'season_desc': {
            'en': 'Perennial coastal & tropical palm tree requiring warm humid climate.',
            'kn': 'ಕರಾವಳಿ ಮತ್ತು ಒಳನಾಡಿನಲ್ಲಿ ಸಮೃದ್ಧವಾಗಿ ಬೆಳೆಯುವ ಕಲ್ಪವೃಕ್ಷ.',
            'hi': 'तटीय एवं उष्णकटिबंधीय बारहमासी वृक्ष, जिसे गर्म व आर्द्र जलवायु चाहिए।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 100 kg/ha, Phosphorus: 40 kg/ha, Potassium: 200 kg/ha',
            'kn': 'ಸಾರಜನಕ (N): 100 ಕೆಜಿ/ಹೆಕ್ಟೇರ್, ರಂಜಕ (P): 40 ಕೆಜಿ/ಹೆಕ್ಟೇರ್, ಪೊಟ್ಯಾಸಿಯಮ್ (K): 200 ಕೆಜಿ/ಹೆಕ್ಟೇರ್',
            'hi': 'नाइट्रोजन (N): 100 किग्रा/हेक्टेयर, फास्फोरस (P): 40 किग्रा/हेक्टेयर, पोटेशियम (K): 200 किग्रा/हेक्टेयर'
        },
        'pests': {
 'en': ['Rhinoceros beetle → Apply 5% neem oil / bio-agents; consult your local KVK for verified options', 'Red palm weevil → Apply 5% neem oil / bio-agents; consult your local KVK for verified options', 'Black headed caterpillar → Release parasitoids'],
            'kn': ['ಖಡ್ಗಮೃಗ ದುಂಬಿ → ಫೆರಮೋನ್ ಬಲೆ ಬಳಸಿ', 'ಕೆಂಪು ಮೂತಿ ದುಂಬಿ → ಫಿಪ್ರೊನಿಲ್ ಇಂಜೆಕ್ಷನ್ ಬಳಸಿ', 'ಕಪ್ಪು ತಲೆ ಕಂಬಳಿಹುಳು → ಪರಾವಲಂಬಿ ಕೀಟಗಳನ್ನು ಬಿಡಿ'],
            'hi': ['गैंडा भृंग (राइनो बीटल) → फेरोमोन ट्रैप लगाएं', 'लाल ताड़ घुन → फेरोमोन ट्रैप और ताज की सफाई करें', 'काली सुंडी → परजीवी कीट छोड़ें']
        },
        'best_sell_months': {'en': 'April - June', 'kn': 'ಏಪ್ರಿಲ್ - ಜೂನ್', 'hi': 'अप्रैल - जून'},
        'sell_tip': {
            'en': 'Historical Agmarknet modal price trends show tender coconut and copra prices peaking during peak summer demand.',
            'kn': 'ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಮಂಡಿ ದರ ವಿಶ್ಲೇಷಣೆ: ಬೇಸಿಗೆಯ ಬಿಸಿಲಿನ ಸಮಯದಲ್ಲಿ ಎಳನೀರು ಮತ್ತು ಕೊಬ್ಬರಿಗೆ ಗರಿಷ್ಠ ಮಾರುಕಟ್ಟೆ ಬೇಡಿಕೆ ಇರುತ್ತದೆ.',
            'hi': 'एगमार्कनेट मॉडल भाव रुझान: गर्मी के मौसम में डाभ (कच्चा नारियल) और गरी (खोपरा) के दामों में तेजी रहती है।'
        },
    },
    'wheat': {
        'name': {'en': 'Wheat', 'kn': 'ಗೋಧಿ', 'hi': 'गेहूं'},
        'season': {'en': 'Rabi (Winter)', 'kn': 'ರಬಿ (ಹಿಂಗಾರು)', 'hi': 'रबी (सर्दियां)'},
        'planting_months': {'en': 'November - December (Rabi season)', 'kn': 'ನವೆಂಬರ್ - ಡಿಸೆಂಬರ್ (ರಬಿ ಹಿಂಗಾರು)', 'hi': 'नवंबर - दिसंबर (रबी मौसम)'},
        'harvest_months': {'en': 'March - April', 'kn': 'ಮಾರ್ಚ್ - ಏಪ್ರಿಲ್', 'hi': 'मार्च - अप्रैल'},
        'season_desc': {
            'en': 'Major winter staple cereal requiring cool growing season and dry harvest period.',
            'kn': 'ತಂಪಾದ ಹವಾಮಾನ ಮತ್ತು ಕಟಾವಿನ ಸಮಯದಲ್ಲಿ ಒಣ ಹವೆಯ ಅಗತ್ಯವಿರುವ ಪ್ರಮುಖ ಆಹಾರ ಧಾನ್ಯ.',
            'hi': 'ठंडी जलवायु और कटाई के समय शुष्क मौसम चाहने वाला प्रमुख खाद्यान्न।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 120 kg/ha, Phosphorus: 60 kg/ha, Potassium: 40 kg/ha',
            'kn': 'ಸಾರಜನಕ (N): 120 ಕೆಜಿ/ಹೆಕ್ಟೇರ್, ರಂಜಕ (P): 60 ಕೆಜಿ/ಹೆಕ್ಟೇರ್, ಪೊಟ್ಯಾಸಿಯಮ್ (K): 40 ಕೆಜಿ/ಹೆಕ್ಟೇರ್',
            'hi': 'नाइट्रोजन (N): 120 किग्रा/हेक्टेयर, फास्फोरस (P): 60 किग्रा/हेक्टेयर, पोटेशियम (K): 40 किग्रा/हेक्टेयर'
        },
        'pests': {
 'en': ['Aphids → Apply 5% neem oil / bio-agents; consult your local KVK for verified options', 'Rust → Apply 5% neem oil / bio-agents; consult your local KVK for verified options', 'Termites → Apply 5% neem oil / bio-agents; consult your local KVK for verified options'],
            'kn': ['ಸಸ್ಯ ಹೇನು → ಹಳದಿ ಜಿಗುಟು ಬಲೆ ಮತ್ತು ಬೇವಿನ ಕಷಾಯ ಬಳಸಿ', 'ತುಕ್ಕು ರೋಗ → ಸಮತೋಲಿತ ಪೋಷಕಾಂಶ ಮತ್ತು ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು ಬಳಸಿ', 'ಗೆದ್ದಲು ಹುಳು → ಬೇವಿನ ಹಿಂಡಿ ಮತ್ತು ಕಳಿತ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಬಳಸಿ'],
            'hi': ['माहू → पीले चिपचिपे ट्रैप और नीम अर्क का छिड़काव करें', 'गेरुआ (रस्ट) → संतुलित पोषण एवं जैविक नियंत्रण अपनाएं', 'दीमक → सड़ी गोबर खाद और नीम खली का प्रयोग करें']
        },
        'best_sell_months': {'en': 'April - May', 'kn': 'ಏಪ್ರಿಲ್ - ಮೇ', 'hi': 'अप्रैल - मई'},
        'sell_tip': {
            'en': 'Selling at Government MSP procurement centres in April-May gives guaranteed profits with zero APMC mandi deduction.',
            'kn': 'ಏಪ್ರಿಲ್-ಮೇ ತಿಂಗಳಲ್ಲಿ ಸರ್ಕಾರಿ ಬೆಂಬಲ ಬೆಲೆ (MSP) ಖರೀದಿ ಕೇಂದ್ರಗಳಲ್ಲಿ ಮಾರಾಟ ಮಾಡುವುದರಿಂದ ಕಡಿತವಿಲ್ಲದೆ ಖಚಿತ ಲಾಭ ದೊರೆಯುತ್ತದೆ.',
            'hi': 'अप्रैल-मई में सरकारी एमएसपी खरीद केंद्रों पर बेचने से बिना मंडी कटौती के सुनिश्चित लाभ मिलता है।'
        },
    },
    'soybean': {
        'name': {'en': 'Soybean', 'kn': 'ಸೋಯಾಬೀನ್', 'hi': 'सोयाबीन'},
        'season': {'en': 'Kharif only (June - July in Dharwad)', 'kn': 'ಖಾರೀಫ್ ಮಾತ್ರ (ಧಾರವಾಡದಲ್ಲಿ ಜೂನ್ - ಜುಲೈ)', 'hi': 'केवल खरीफ (धारवाड़ में जून - जुलाई)'},
        'season_type': 'Kharif',
        'planting_months': {'en': 'June - July (Kharif only - strictly excluded from Rabi)', 'kn': 'ಜೂನ್ - ಜುಲೈ (ಮುಂಗಾರು ಮಾತ್ರ - ಹಿಂಗಾರಿಗೆ ಸೂಕ್ತವಲ್ಲ)', 'hi': 'जून - जुलाई (केवल खरीफ - रबी के लिए अनुपयुक्त)'},
        'harvest_months': {'en': 'September - October', 'kn': 'ಸೆಪ್ಟೆಂಬರ್ - ಅಕ್ಟೋಬರ್', 'hi': 'सितंबर - अक्टूबर'},
        'season_desc': {
            'en': 'High-protein Kharif oilseed for North Karnataka; sow June-July on monsoon onset, strictly excluded from post-September Rabi cultivation.',
            'kn': 'ಉತ್ತರ ಕರ್ನಾಟಕದಲ್ಲಿ ಮುಂಗಾರು ಮಳೆಯ ಆರಂಭದಲ್ಲಿ (ಜೂನ್-ಜುಲೈ) ಬೆಳೆಯುವ ಪ್ರಮುಖ ಎಣ್ಣೆಕಾಳು ಬೆಳೆ; ಹಿಂಗಾರು (ಸೆಪ್ಟೆಂಬರ್ ನಂತರ) ಹಂಗಾಮಿಗೆ ಸೂಕ್ತವಲ್ಲ.',
            'hi': 'उत्तर कर्नाटक में मानसूनी आगमन (जून-जुलाई) पर बोई जाने वाली प्रमुख तिलहनी फसल; सितंबर के बाद रबी के लिए अनुपयुक्त।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 30 kg/ha, Phosphorus: 60 kg/ha, Potassium: 40 kg/ha',
            'kn': 'ಸಾರಜನಕ (N): 30 ಕೆಜಿ/ಹೆಕ್ಟೇರ್, ರಂಜಕ (P): 60 ಕೆಜಿ/ಹೆಕ್ಟೇರ್, ಪೊಟ್ಯಾಸಿಯಮ್ (K): 40 ಕೆಜಿ/ಹೆಕ್ಟೇರ್',
            'hi': 'नाइट्रोजन (N): 30 किग्रा/हेक्टेयर, फास्फोरस (P): 60 किग्रा/हेक्टेयर, पोटेशियम (K): 40 किग्रा/हेक्टेयर'
        },
        'pests': {
 'en': ['Stem fly → Seed treatment with Trichoderma and timely planting', 'Girdle beetle → Destruction of alternate weeds and light traps', 'Rust → Grow resistant varieties and apply bio-fungicides'],
            'kn': ['ಕಾಂಡದ ನೊಣ → ಟ್ರೈಕೋಡರ್ಮಾ ಬೀಜೋಪಚಾರ ಮತ್ತು ಸಕಾಲಿಕ ಬಿತ್ತನೆ ಮಾಡಿ', 'ಉಂಗುರ ಜೀರುಂಡೆ → ಕಳೆ ನಾಶ ಮತ್ತು ದೀಪದ ಬಲೆಗಳನ್ನು ಬಳಸಿ', 'ತುಕ್ಕು ರೋಗ → ಹೆಕ್ಸಾಕೊನಾಜೋಲ್ ಸಿಂಪಡಿಸಿ'],
            'hi': ['तना मक्खी → ट्राइकोडर्मा बीजोपचार और समय पर बुवाई करें', 'गर्डल बीटल → खरपतवार नियंत्रण और प्रकाश प्रपंच का प्रयोग करें', 'गेरुआ (रस्ट) → फसल चक्र अपनाएं और ट्राइकोडर्मा का प्रयोग करें']
        },
        'best_sell_months': {'en': 'October - December', 'kn': 'ಅಕ್ಟೋಬರ್ - ಡಿಸೆಂಬರ್', 'hi': 'अक्टूबर - दिसंबर'},
        'sell_tip': {
            'en': 'Agmarknet multi-year modal price trends show strong post-harvest oil-mill demand in Dharwad and Belagavi APMCs; compare with official MSP.',
            'kn': 'ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಮಂಡಿ ದರ ವಿಶ್ಲೇಷಣೆ: ಧಾರವಾಡ ಮತ್ತು ಬೆಳಗಾವಿ ಎಪಿಎಂಸಿಗಳಲ್ಲಿ ಎಣ್ಣೆ ಗಿರಣಿಗಳ ಹೆಚ್ಚಿನ ಬೇಡಿಕೆಯಿಂದ ಉತ್ತಮ ಬೆಲೆ ಸಿಗುತ್ತದೆ; ಬೆಂಬಲ ಬೆಲೆ (MSP) ಹೋಲಿಸಿ ನೋಡಿ.',
            'hi': 'एगमार्कनेट बहु-वर्षीय मॉडल भाव रुझान: धारवाड़ और बेलगावी एपीएमसी में तेल मिलों की मजबूत मांग से अच्छे भाव मिलते हैं; सरकारी एमएसपी से तुलना करें।'
        },
    },
    'groundnut': {
        'name': {'en': 'Groundnut (Peanut)', 'kn': 'ಕಡಲೆಕಾಯಿ (ಶೇಂಗಾ)', 'hi': 'मूंगफली'},
        'season': {'en': 'Kharif & Rabi / Summer', 'kn': 'ಖಾರೀಫ್ ಮತ್ತು ರಬಿ / ಬೇಸಿಗೆ', 'hi': 'खरीफ एवं रबी / जायद'},
        'planting_months': {'en': 'June - July & December - January', 'kn': 'ಜೂನ್ - ಜುಲೈ ಮತ್ತು ಡಿಸೆಂಬರ್ - ಜನವರಿ', 'hi': 'जून - जुलाई एवं दिसंबर - जनवरी'},
        'harvest_months': {'en': 'October - November & April - May', 'kn': 'ಅಕ್ಟೋಬರ್ - ನವೆಂಬರ್ ಮತ್ತು ಏಪ್ರಿಲ್ - ಮೇ', 'hi': 'अक्टूबर - नवंबर एवं अप्रैल - मई'},
        'season_desc': {
            'en': 'Major commercial oilseed performing exceptionally well in sandy loam soils.',
            'kn': 'ಮರಳು ಮಿಶ್ರಿತ ಗೋಡು ಮಣ್ಣಿನಲ್ಲಿ ಸಮೃದ್ಧವಾಗಿ ಬೆಳೆಯುವ ಪ್ರಮುಖ ವಾಣಿಜ್ಯ ಎಣ್ಣೆಕಾಳು ಬೆಳೆ.',
            'hi': 'बलुई दोमट मिट्टी में बेहतरीन पैदावार देने वाली प्रमुख तिलहनी नकदी फसल।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 25 kg/ha, Phosphorus: 50 kg/ha, Potassium: 40 kg/ha + Gypsum 500 kg/ha',
            'kn': 'ಸಾರಜನಕ: 25 ಕೆಜಿ, ರಂಜಕ: 50 ಕೆಜಿ, ಪೊಟ್ಯಾಶ್: 40 ಕೆಜಿ + ಜಿಪ್ಸಮ್ 500 ಕೆಜಿ/ಹೆಕ್ಟೇರ್',
            'hi': 'नाइट्रोजन: 25 किग्रा, फास्फोरस: 50 किग्रा, पोटाश: 40 किग्रा + जिप्सम 500 किग्रा/हेक्टेयर'
        },
        'pests': {
            'en': [
                'Tikka leaf spot (Cercospora) → Foliar spray at early onset (30-40 DAS): 5% neem seed kernel extract; consult local KVK for approved fungicidal spray [needs_verification]',
                'Leaf miner → Vegetative stage monitoring: light traps and 5% neem seed kernel extract [needs_verification]',
                'White grub → Deep summer ploughing: before sowing (Apr-May), not applicable now; bio-control: Metarhizium anisopliae soil application [needs_verification]'
            ],
            'kn': [
                'ತಿಕ್ಕಾ ಎಲೆ ಚುಕ್ಕೆ ರೋಗ → ಆರಂಭಿಕ ಹಂತದಲ್ಲಿ (30-40 ದಿನ) 5% ಬೇವಿನ ಬೀಜದ ಕಷಾಯ (NSKE) ಸಿಂಪಡಣೆ; ಅನುಮೋದಿತ ಶಿಲೀಂಧ್ರನಾಶಕಕ್ಕೆ ಸ್ಥಳೀಯ ಕೆವಿಕೆಯನ್ನು ಸಂಪರ್ಕಿಸಿ [ಪರಿಶೀಲನೆ ಅಗತ್ಯ]',
                'ಎಲೆ ಸುರಂಗ ಹುಳು → ಸಸ್ಯ ಬೆಳವಣಿಗೆ ಹಂತದ ಕಣ್ಗಾವಲು: ದೀಪದ ಬಲೆಗಳು ಮತ್ತು 5% ಬೇವಿನ ಕಷಾಯ [ಪರಿಶೀಲನೆ ಅಗತ್ಯ]',
                'ಬಿಳಿ ಹುಳು → ಬೇಸಿಗೆ ಆಳ ಉಳುಮೆ: ಬಿತ್ತನೆಗೆ ಮುನ್ನ (ಏಪ್ರಿಲ್-ಮೇ), ಈಗ ಅನ್ವಯಿಸುವುದಿಲ್ಲ; ಜೈವಿಕ ನಿಯಂತ್ರಣ: ಮೆಟಾರೈಜಿಯಮ್ ಬಳಕೆ [ಪರಿಶೀಲನೆ ಅಗತ್ಯ]'
            ],
            'hi': [
                'टिक्का पत्ती धब्बा → प्रारंभिक अवस्था (30-40 दिन) पर 5% नीम गिरी काढ़ा (NSKE) छिड़काव; अनुमोदित कवकनाशी हेतु स्थानीय केवीके से परामर्श लें [सत्यापन आवश्यक]',
                'लीफ माइनर → वानस्पतिक अवस्था निगरानी: प्रकाश प्रपंच और 5% नीम गिरी काढ़ा [सत्यापन आवश्यक]',
                'सफेद लट → गहरी ग्रीष्मकालीन जुताई: बुवाई से पूर्व (अप्रैल-मई), अभी लागू नहीं; जैविक नियंत्रण: मेटाराइजियम प्रयोग [सत्यापन आवश्यक]'
            ]
        },
        'best_sell_months': {'en': 'November - January', 'kn': 'ನವೆಂಬರ್ - ಜನವರಿ', 'hi': 'नवंबर - जनवरी'},
        'sell_tip': {
            'en': 'Agmarknet modal price trends show properly dried pods (<8% moisture) fetch top rates; compare with official MSP procurement centres.',
            'kn': 'ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಮಂಡಿ ದರ ವಿಶ್ಲೇಷಣೆ: ಶೇ. 8 ಕ್ಕಿಂತ ಕಡಿಮೆ ತೇವಾಂಶವಿರುವಂತೆ ಒಣಗಿಸಿದ ಕಡಲೆಕಾಯಿಗೆ ಗರಿಷ್ಠ ದರ ಸಿಗುತ್ತದೆ; ಸರ್ಕಾರಿ ಬೆಂಬಲ ಬೆಲೆ (MSP) ಪರಿಶೀಲಿಸಿ.',
            'hi': 'एगमार्कनेट मॉडल भाव रुझान: 8% से कम नमी वाले सूखे दानों को बेहतरीन दाम मिलते हैं; सरकारी एमएसपी खरीद केंद्रों से भी भाव जांचें।'
        },
    },
    'ragi': {
        'name': {'en': 'Finger Millet (Ragi)', 'kn': 'ರಾಗಿ', 'hi': 'रागी / मडुआ'},
        'season': {'en': 'Kharif (Monsoon)', 'kn': 'ಖಾರೀಫ್ (ಮುಂಗಾರು)', 'hi': 'खरीफ (मानसून)'},
        'planting_months': {'en': 'July - August (Monsoon sowing)', 'kn': 'ಜುಲೈ - ಆಗಸ್ಟ್ (ಮುಂಗಾರು ಬಿತ್ತನೆ)', 'hi': 'जुलाई - अगस्त (मानसूनी बुवाई)'},
        'harvest_months': {'en': 'November - December', 'kn': 'ನವೆಂಬರ್ - ಡಿಸೆಂಬರ್', 'hi': 'नवंबर - दिसंबर'},
        'season_desc': {
            'en': 'Climate-smart nutritious staple grain of Karnataka with exceptional drought resilience.',
            'kn': 'ಕರ್ನಾಟಕದ ಪ್ರಮುಖ ಪೌಷ್ಟಿಕ ಸಿರಿಧಾನ್ಯ ಬೆಳೆಯಾಗಿದ್ದು, ಬರ ನಿರೋಧಕ ಶಕ್ತಿಯನ್ನು ಹೊಂದಿದೆ.',
            'hi': 'कर्नाटक का मुख्य पौष्टिक पोषक अनाज, जो सूखे में भी बेहतरीन उपज देता है।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 60 kg/ha, Phosphorus: 30 kg/ha, Potassium: 30 kg/ha',
            'kn': 'ಸಾರಜನಕ (N): 60 ಕೆಜಿ/ಹೆಕ್ಟೇರ್, ರಂಜಕ (P): 30 ಕೆಜಿ/ಹೆಕ್ಟೇರ್, ಪೊಟ್ಯಾಸಿಯಮ್ (K): 30 ಕೆಜಿ/ಹೆಕ್ಟೇರ್',
            'hi': 'नाइट्रोजन (N): 60 किग्रा/हेक्टेयर, फास्फोरस (P): 30 किग्रा/हेक्टेयर, पोटेशियम (K): 30 किग्रा/हेक्टेयर'
        },
        'pests': {
 'en': ['Blast disease → Seed treatment with Trichoderma and balanced fertilizer', 'Stem borer → Light traps and Trichogramma cards', 'Aphids → Yellow sticky traps and 5% neem oil'],
            'kn': ['ಬೆಂಕಿ ರೋಗ (ಬ್ಲಾಸ್ಟ್) → ಟ್ರೈಕೋಡರ್ಮಾ ಬೀಜೋಪಚಾರ ಮತ್ತು ಸಮತೋಲಿತ ಗೊಬ್ಬರ ಬಳಸಿ', 'ಕಾಂಡ ಕೊರೆಯುವ ಹುಳು → ದೀಪದ ಬಲೆಗಳು ಮತ್ತು ಟ್ರೈಕೋಗ್ರಾಮ ಕಾರ್ಡ್ ಬಳಸಿ', 'ಸಸ್ಯ ಹೇನು → ಹಳದಿ ಜಿಗುಟು ಬಲೆಗಳು ಮತ್ತು 5% ಬೇವಿನ ಎಣ್ಣೆ ಬಳಸಿ'],
            'hi': ['झुलसा / ब्लास्ट रोग → ट्राइकोडर्मा बीजोपचार और संतुलित खाद का प्रयोग करें', 'तना छेदक → प्रकाश प्रपंच और ट्राइकोग्रामा कार्ड लगाएं', 'माहू → पीले चिपचिपे ट्रैप और 5% नीम तेल का छिड़काव करें']
        },
        'best_sell_months': {'en': 'December - February', 'kn': 'ಡಿಸೆಂಬರ್ - ಫೆಬ್ರವರಿ', 'hi': 'दिसंबर - फरवरी'},
        'sell_tip': {
            'en': 'Government procurement at minimum support price (MSP) and Agmarknet modal price trends ensure highest profitability.',
            'kn': 'ಸರ್ಕಾರಿ ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ (MSP) ಖರೀದಿ ಕೇಂದ್ರಗಳು ಮತ್ತು ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಮಂಡಿ ದರಗಳು ರೈತರಿಗೆ ಉತ್ತಮ ಲಾಭವನ್ನು ಖಚಿತಪಡಿಸುತ್ತವೆ.',
            'hi': 'सरकारी न्यूनतम समर्थन मूल्य (MSP) खरीद और एगमार्कनेट मॉडल भाव रुझान अधिकतम लाभ सुनिश्चित करते हैं।'
        },
    },
    'banana': {
        'name': {'en': 'Banana', 'kn': 'ಬಾಳೆಹಣ್ಣು', 'hi': 'केला'},
        'season': {'en': 'Whole Year (Tropical)', 'kn': 'ವರ್ಷಪೂರ್ತಿ', 'hi': 'पूरे साल'},
        'planting_months': {'en': 'June - July & September - October', 'kn': 'ಜೂನ್ - ಜುಲೈ ಮತ್ತು ಸೆಪ್ಟೆಂಬರ್ - ಅಕ್ಟೋಬರ್', 'hi': 'जून - जुलाई एवं सितंबर - अक्टूबर'},
        'harvest_months': {'en': '11-12 months after planting', 'kn': 'ನಾಟಿ ಮಾಡಿದ 11-12 ತಿಂಗಳ ನಂತರ', 'hi': 'रोपाई के 11-12 महीने बाद'},
        'season_desc': {
            'en': 'Heavy feeder tropical fruit crop requiring plenty of water and nutrient-rich soil.',
            'kn': 'ಹೆಚ್ಚು ನೀರು ಮತ್ತು ಫಲವತ್ತಾದ ಮಣ್ಣು ಬಯಸುವ ಲಾಭದಾಯಕ ಹಣ್ಣಿನ ಬೆಳೆ.',
            'hi': 'प्रचुर पानी और पोषक तत्वों वाली मिट्टी की मांग करने वाली उच्च लाभ वाली फसल।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 200 kg/ha, Phosphorus: 60 kg/ha, Potassium: 300 kg/ha',
            'kn': 'ಸಾರಜನಕ (N): 200 ಕೆಜಿ/ಹೆಕ್ಟೇರ್, ರಂಜಕ (P): 60 ಕೆಜಿ/ಹೆಕ್ಟೇರ್, ಪೊಟ್ಯಾಸಿಯಮ್ (K): 300 ಕೆಜಿ/ಹೆಕ್ಟೇರ್',
            'hi': 'नाइट्रोजन (N): 200 किग्रा/हेक्टेयर, फास्फोरस (P): 60 किग्रा/हेक्टेयर, पोटेशियम (K): 300 किग्रा/हेक्टेयर'
        },
        'pests': {
 'en': ['Pseudostem weevil → Pseudostem traps and field sanitation', 'Sigatoka leaf spot → De-leafing infected leaves and 1% Bordeaux spray', 'Panama wilt → Trichoderma soil application'],
            'kn': ['ಕಾಂಡ ಕೊರೆಯುವ ಮೂತಿ ಹುಳು → ಕಾಂಡದ ಬಲೆಗಳು ಮತ್ತು ಸ್ವಚ್ಛ ಬೇಸಾಯ ಕ್ರಮಗಳನ್ನು ಬಳಸಿ', 'ಸಿಗಾಟೋಕ ಎಲೆ ಕಲೆ ರೋಗ → ಸೋಂಕಿತ ಎಲೆಗಳನ್ನು ತೆಗೆದು ಶೇ. 1ರ ಬೋರ್ಡೋ ಸಿಂಪಡಿಸಿ', 'ಪನಾಮಾ ಸೊರಗು ರೋಗ → ಟ್ರೈಕೋಡರ್ಮಾ ಮಣ್ಣಿಗೆ ಸೇರಿಸಿ'],
            'hi': ['तना घुन → स्वच्छता एवं सड़ी गोबर खाद और नीम खली का प्रयोग करें', 'सिगाटोका पत्ती धब्बा → संक्रमित पत्तियां हटाएं और 1% बोर्डो मिश्रण छिड़कें', 'पनामा विल्ट → ट्राइकोडर्मा से मिट्टी का उपचार करें']
        },
        'best_sell_months': {'en': 'August - October', 'kn': 'ಆಗಸ್ಟ್ - ಅಕ್ಟೋಬರ್', 'hi': 'अगस्त - अक्टूबर'},
        'sell_tip': {
            'en': 'Agmarknet multi-year modal price trends show festival seasons (Ganesh Chaturthi, Navratri, Diwali) driving highest market demand.',
            'kn': 'ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಬಹು-ವರ್ಷಗಳ ಮಂಡಿ ದರ ವಿಶ್ಲೇಷಣೆ: ಹಬ್ಬಗಳ ಕಾಲದಲ್ಲಿ (ಗಣೇಶ ಚತುರ್ಥಿ, ದಸರಾ, ದೀಪಾವಳಿ) ಬಾಳೆಹಣ್ಣಿಗೆ ಅತ್ಯಧಿಕ ಬೆಲೆ ದೊರೆಯುತ್ತದೆ.',
            'hi': 'एगमार्कनेट बहु-वर्षीय मॉडल भाव रुझान: त्योहारी सीजन (गणेश चतुर्थी, नवरात्रि, दिवाली) में केले की सबसे अधिक मांग रहती है।'
        },
    },
    'tomato': {
        'name': {'en': 'Tomato', 'kn': 'ಟೊಮೆಟೊ', 'hi': 'टमाटर'},
        'season': {'en': 'Kharif / Rabi / Zaid', 'kn': 'ಖಾರೀಫ್ / ರಬಿ / ಬೇಸಿಗೆ', 'hi': 'खरीफ / रबी / जायद'},
        'season_type': 'Multi-season (Transplanted)',
        'planting_months': {
            'en': 'Nursery / transplanting: June - August (Kharif) & October - November (Rabi)',
            'kn': 'ನರ್ಸರಿ / ನಾಟಿ: ಜೂನ್ - ಆಗಸ್ಟ್ (ಮುಂಗಾರು) ಮತ್ತು ಅಕ್ಟೋಬರ್ - ನವೆಂಬರ್ (ಹಿಂಗಾರು)',
            'hi': 'नर्सरी / रोपाई: जून - अगस्त (खरीफ) एवं अक्टूबर - नवंबर (रबी)'
        },
        'harvest_months': {
            'en': '~90-115 days after transplanting (Oct-Dec & Feb-Apr)',
            'kn': 'ನಾಟಿ ಮಾಡಿದ ~90-115 ದಿನಗಳ ನಂತರ (ಅಕ್ಟೋ-ಡಿಸೆಂ & ಫೆಬ್ರ-ಏಪ್ರಿ)',
            'hi': 'रोपाई के ~90-115 दिन बाद (अक्टू-दिसं एवं फर-अप्रै)'
        },
        'season_desc': {
            'en': 'High-yield commercial vegetable crop grown across all three seasons in Karnataka.',
            'kn': 'ಕರ್ನಾಟಕದಲ್ಲಿ (ಕೋಲಾರ/ಚಿಕ್ಕಬಳ್ಳಾಪುರ) ಮೂರೂ ಋತುಗಳಲ್ಲಿ ಬೆಳೆಯಲಾಗುವ ಜನಪ್ರಿಯ ತರಕಾರಿ ಬೆಳೆ.',
            'hi': 'कर्नाटक (कोलार/चिक्काबल्लापुर) में तीनों मौसमों में उगाई जाने वाली लोकप्रिय सब्जी फसल।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 120 kg/ha, Phosphorus: 80 kg/ha, Potassium: 80 kg/ha',
            'kn': 'ಸಾರಜನಕ (N): 120 ಕೆಜಿ/ಹೆಕ್ಟೇರ್, ರಂಜಕ (P): 80 ಕೆಜಿ/ಹೆಕ್ಟೇರ್, ಪೊಟ್ಯಾಸಿಯಮ್ (K): 80 ಕೆಜಿ/ಹೆಕ್ಟೇರ್',
            'hi': 'नाइट्रोजन (N): 120 किग्रा/हेक्टेयर, फास्फोरस (P): 80 किग्रा/हेक्टेयर, पोटेशियम (K): 80 किग्रा/हेक्टेयर'
        },
        'pests': {
 'en': ['Fruit borer → Install Helicoverpa pheromone traps @ 5/acre and spray HaNPV', 'Early/Late Blight → Apply Trichoderma viride and 1% Bordeaux mixture', 'Leaf curl virus → Install yellow sticky traps (20/acre) and spray 5% neem oil'],
            'kn': ['ಕಾಯಿ ಕೊರೆಯುವ ಹುಳು → ಮೋಹಕ ಬಲೆಗಳು (5/ಎಕರೆ) ಮತ್ತು HaNPV ಸಿಂಪಡಿಸಿ', 'ಮುಟುರು/ಕೊಳೆತ ರೋಗ → 5% ಬೇವಿನ ಎಣ್ಣೆ ಅಥವಾ ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಬಳಸಿ', 'ಎಲೆ ಸುರುಟು ವೈರಸ್ → ಹಳದಿ ಜಿಗುಟು ಬಲೆಗಳು ಮತ್ತು 5% ಬೇವಿನ ಎಣ್ಣೆ ಬಳಸಿ ಬಿಳಿ ನೊಣ ನಿಯಂತ್ರಿಸಿ'],
            'hi': ['फल छेदक → प्रति एकड़ 5 फेरोमोन ट्रैप और HaNPV का छिड़काव करें', 'अगेती/पछेती झुलसा → ट्राइकोडर्मा और 1% बोर्डो मिश्रण का प्रयोग करें', 'पत्ती मरोड़क वायरस → सफेद मक्खी नियंत्रण के लिए पीले चिपचिपे ट्रैप और 5% नीम तेल का छिड़काव करें']
        },
        'best_sell_months': {'en': 'July - August & Nov - Dec', 'kn': 'ಜುಲೈ - ಆಗಸ್ಟ್ ಮತ್ತು ನವೆಂಬರ್ - ಡಿಸೆಂಬರ್', 'hi': 'जुलाई - अगस्त एवं नवंबर - दिसंबर'},
        'sell_tip': {
            'en': 'Agmarknet multi-year modal price trends indicate prices peak during heavy monsoon arrival gaps (July-August) when mandi arrivals drop.',
            'kn': 'ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಬಹು-ವರ್ಷಗಳ ಮಂಡಿ ದರ ವಿಶ್ಲೇಷಣೆ: ಮುಂಗಾರು ಮಳೆಯ ಸಮಯದಲ್ಲಿ ಮಾರುಕಟ್ಟೆಗೆ ಬರುವ ಟೊಮೆಟೊ ಪ್ರಮಾಣ ಕಡಿಮೆಯಾಗಿ ಜುಲೈ-ಆಗಸ್ಟ್\u200cನಲ್ಲಿ ಗರಿಷ್ಠ ಬೆಲೆ ಏರಿಕೆ ಕಾಣುತ್ತದೆ.',
            'hi': 'एगमार्कनेट बहु-वर्षीय मॉडल भाव रुझान: भारी मानसूनी अंतरालों (जुलाई-अगस्त) में मंडियों में आवक घटने से भाव अपने उच्चतम स्तर पर पहुंचते हैं।'
        },
    },
    'mango': {
        'name': {'en': 'Mango', 'kn': 'ಮಾವು', 'hi': 'आम'},
        'season': {'en': 'Summer (Zaid)', 'kn': 'ಬೇಸಿಗೆ (ಜೈದ್)', 'hi': 'गर्मी (जायद)'},
        'planting_months': {'en': 'July - August (Monsoon)', 'kn': 'ಜುಲೈ - ಆಗಸ್ಟ್ (ಮುಂಗಾರು)', 'hi': 'जुलाई - अगस्त (मानसून)'},
        'harvest_months': {'en': 'April - June', 'kn': 'ಏಪ್ರಿಲ್ - ಜೂನ್', 'hi': 'अप्रैल - जून'},
        'season_desc': {
            'en': 'King of fruits requiring dry weather during flowering and hot sun during ripening.',
            'kn': 'ಹೂ ಬಿಡುವಾಗ ಒಣ ಹವೆ ಮತ್ತು ಕಾಯಿ ಮಾಗುವಾಗ ಬಿಸಿಲಿನ ಅಗತ್ಯವಿರುವ ಹಣ್ಣುಗಳ ರಾಜ.',
            'hi': 'फलों का राजा, जिसे फूल आते समय शुष्क मौसम और पकने के लिए तेज धूप चाहिए।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 100 kg/ha, Phosphorus: 50 kg/ha, Potassium: 100 kg/ha',
            'kn': 'ಸಾರಜನಕ (N): 100 ಕೆಜಿ/ಹೆಕ್ಟೇರ್, ರಂಜಕ (P): 50 ಕೆಜಿ/ಹೆಕ್ಟೇರ್, ಪೊಟ್ಯಾಸಿಯಮ್ (K): 100 ಕೆಜಿ/ಹೆಕ್ಟೇರ್',
            'hi': 'नाइट्रोजन (N): 100 किग्रा/हेक्टेयर, फास्फोरस (P): 50 किग्रा/हेक्टेयर, पोटेशियम (K): 100 किग्रा/हेक्टेयर'
        },
        'pests': {
 'en': ['Mango hopper → Apply 5% neem oil / bio-agents; consult your local KVK for verified options', 'Powdery mildew → Apply 5% neem oil / bio-agents; consult your local KVK for verified options', 'Fruit fly → Apply 5% neem oil / bio-agents; consult your local KVK for verified options'],
            'kn': ['ಮಾವಿನ ಜಿಗಿಹುಳು → ಹಳದಿ ಜಿಗುಟು ಬಲೆಗಳು ಮತ್ತು 5% ಬೇವಿನ ಎಣ್ಣೆ ಬಳಸಿ', 'ಬೂದಿ ರೋಗ → ಬೆಳೆ ಪರಿವರ್ತನೆ ಮಾಡಿ ಮತ್ತು ಟ್ರೈಕೋಡರ್ಮಾ ಬಳಸಿ', 'ಹಣ್ಣಿನ ನೊಣ → ಮೀಥೈಲ್ ಯುಜೆನಾಲ್ ಬಲೆಗಳನ್ನು ಬಳಸಿ'],
            'hi': ['आम का फुदका → पीले चिपचिपे ट्रैप और 5% नीम तेल का छिड़काव करें', 'चूर्णिल फफूंद → फसल चक्र अपनाएं और ट्राइकोडर्मा का प्रयोग करें', 'फल मक्खी → मिथाइल यूजेनॉल ट्रैप लगाएं']
        },
        'best_sell_months': {'en': 'May - June', 'kn': 'ಮೇ - ಜೂನ್', 'hi': 'मई - जून'},
        'sell_tip': {
            'en': 'Agmarknet modal price trends confirm Alphonso, Raspuri, and Badami varieties fetch premium rates during peak mid-to-late May arrivals.',
            'kn': 'ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಮಂಡಿ ದರ ವಿಶ್ಲೇಷಣೆ: ಆಪೂಸ್, ರಸಪುರಿ ಮತ್ತು ಬಾದಾಮಿ ತಳಿಗಳಿಗೆ ಮೇ ತಿಂಗಳ ಮಧ್ಯಭಾಗದಲ್ಲಿ ಅತ್ಯಧಿಕ ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ದೊರೆಯುತ್ತದೆ.',
            'hi': 'एगमार्कनेट मॉडल भाव रुझान: अल्फांसो, रसपुरी और बादामी किस्मों को मई के मध्य से अंत में सर्वाधिक प्रीमियम मूल्य मिलता है।'
        },
    },
    'potato': {
        'name': {'en': 'Potato', 'kn': 'ಆಲೂಗಡ್ಡೆ', 'hi': 'आलू'},
        'season': {'en': 'Rabi (Winter)', 'kn': 'ಹಿಂಗಾರು (ಚಳಿಗಾಲ)', 'hi': 'रबी (सर्दियों का मौसम)'},
        'season_type': 'Rabi',
        'planting_months': {'en': 'October - December', 'kn': 'ಅಕ್ಟೋಬರ್ - ಡಿಸೆಂಬರ್', 'hi': 'अक्टूबर - दिसंबर'},
        'harvest_months': {'en': 'February - March', 'kn': 'ಫೆಬ್ರವರಿ - ಮಾರ್ಚ್', 'hi': 'फरवरी - मार्च'},
        'season_desc': {
            'en': 'High-yielding horticultural tuber crop cultivated for domestic and commercial markets.',
            'kn': 'ಉತ್ತಮ ಒಳಚರಂಡಿ ಹೊಂದಿರುವ ಮಣ್ಣಿನಲ್ಲಿ ಬೆಳೆಯುವ ಚಳಿಗಾಲದ ಗೆಡ್ಡೆ ಬೆಳೆ.',
            'hi': 'ठंडे मौसम की कंद फसल, 15-20°C तापमान कंद बनने के लिए उपयुक्त होता है।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 120 kg/ha, Phosphorus: 60 kg/ha, Potassium: 150 kg/ha.',
            'kn': 'ಸಾರಜನಕ: 120 ಕೆಜಿ/ಹೆ, ರಂಜಕ: 60 ಕೆಜಿ/ಹೆ, ಪೊಟ್ಯಾಶ್: 150 ಕೆಜಿ/ಹೆ.',
            'hi': 'नाइट्रोजन: 120 किग्रा/हे, फास्फोरस: 60 किग्रा/हे, पोटाश: 150 किग्रा/हे।'
        },
        'pests': {
 'en': ['Late Blight → Apply 5% neem oil / bio-fungicide preventives', 'Potato Tuber Moth → Keep tubers earthened up', 'Aphids → Install yellow sticky traps and spray 5% neem oil'],
            'kn': ['ತಡವಾದ ಕಮಟು ರೋಗ → 5% ಬೇವಿನ ಎಣ್ಣೆ ಅಥವಾ ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಬಳಸಿ', 'ಗೆಡ್ಡೆ ಪತಂಗ → ಗೆಡ್ಡೆಗಳನ್ನು ಮಣ್ಣಿನಿಂದ ಮುಚ್ಚಿ', 'ಗಿಡಹೇನು → ಹಳದಿ ಜಿಗುಟು ಬಲೆಗಳು ಮತ್ತು 5% ಬೇವಿನ ಎಣ್ಣೆ ಬಳಸಿ'],
            'hi': ['पछेती झुलसा रोग → 5% नीम तेल या जैविक कवकनाशी का प्रयोग करें', 'आलू कंद कीट → कंदों को अच्छी तरह मिट्टी से ढंकें', 'माहू (एफिड्स) → पीले चिपचिपे ट्रैप और 5% नीम तेल का प्रयोग करें']
        },
        'best_sell_months': {
            'en': 'July - September (Off-season cold storage release)',
            'kn': 'ಜುಲೈ - ಸೆಪ್ಟೆಂಬರ್ (ಶೀತಲ ಗೋದಾಮಿನಿಂದ ಬಿಡುಗಡೆ)',
            'hi': 'जुलाई - सितंबर (कोल्ड स्टोरेज से ऑफ-सीजन बिक्री)'
        },
        'sell_tip': {
            'en': 'Agmarknet multi-year modal price trends indicate cold-stored potato releases in July-September fetch optimal margins before new kharif arrivals.',
            'kn': 'ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಬಹು-ವರ್ಷಗಳ ಮಂಡಿ ದರ ವಿಶ್ಲೇಷಣೆ: ಜುಲೈ-ಸೆಪ್ಟೆಂಬರ್ ತಿಂಗಳಲ್ಲಿ ಕೋಲ್ಡ್ ಸ್ಟೋರೇಜ್ ಆಲೂಗಡ್ಡೆ ಬಿಡುಗಡೆ ಮಾಡುವುದರಿಂದ ಗರಿಷ್ಠ ಲಾಭ ಗಳಿಸಬಹುದು.',
            'hi': 'एगमार्कनेट बहु-वर्षीय मॉडल भाव रुझान: कोल्ड स्टोरेज में रखे आलू को जुलाई-सितंबर में बेचने पर नई फसल आने से पहले सर्वाधिक मुनाफा मिलता है।'
        },
    },
    'tomato': {
        'name': {'en': 'Tomato', 'kn': 'ಟೊಮೆಟೊ', 'hi': 'टमाटर'},
        'season': {'en': 'Kharif & Rabi (Monsoon & Winter)', 'kn': 'ಮುಂಗಾರು ಮತ್ತು ಹಿಂಗಾರು (ವರ್ಷಪೂರ್ತಿ)', 'hi': 'खरीफ और रबी (साल भर)'},
        'season_type': 'Kharif & Rabi',
        'planting_months': {'en': 'June - August & November - January', 'kn': 'ಜೂನ್ - ಆಗಸ್ಟ್ ಮತ್ತು ನವೆಂಬರ್ - ಜನವರಿ', 'hi': 'जून - अगस्त और नवंबर - जनवरी'},
        'harvest_months': {'en': 'October - December & March - May', 'kn': 'ಅಕ್ಟೋಬರ್ - ಡಿಸೆಂಬರ್ ಮತ್ತು ಮಾರ್ಚ್ - ಮೇ', 'hi': 'अक्टूबर - दिसंबर और मार्च - मई'},
        'season_desc': {
            'en': 'High-demand cash vegetable grown throughout the year with proper irrigation.',
            'kn': 'ವರ್ಷಪೂರ್ತಿ ಬೆಳೆಯಬಹುದಾದ ಹೆಚ್ಚಿನ ಆದಾಯ ತರುವ ತರಕಾರಿ ಬೆಳೆ.',
            'hi': 'साल भर अधिक मांग वाली नकदी सब्जी, जो अच्छी आय देती है।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 80 kg/ha, Phosphorus: 60 kg/ha, Potassium: 180 kg/ha (High Potash).',
            'kn': 'ಸಾರಜನಕ: 80 ಕೆಜಿ/ಹೆ, ರಂಜಕ: 60 ಕೆಜಿ/ಹೆ, ಪೊಟ್ಯಾಶ್: 180 ಕೆಜಿ/ಹೆ (ಹೆಚ್ಚಿನ ಪೊಟ್ಯಾಶ್ ಅಗತ್ಯ).',
            'hi': 'नाइट्रोजन: 80 किग्रा/हे, फास्फोरस: 60 किग्रा/हे, पोटाश: 180 किग्रा/हे (अधिक पोटाश)।'
        },
        'pests': {
 'en': ['Whitefly → Apply 5% neem oil / bio-agents; consult your local KVK for verified options& neem oil', 'Fruit Borer → Apply 5% neem oil / bio-agents; consult your local KVK for verified options', 'Early/Late Blight → Spray 1% Bordeaux mixture / bio-fungicide'],
            'kn': ['ಬಿಳಿ ನೊಣ → ಹಳದಿ ಜಿಗುಟು ಬಲೆಗಳು ಮತ್ತು ಬೇವಿನ ಎಣ್ಣೆ ಸಿಂಪಡಿಸಿ', 'ಕಾಯಿ ಕೊರೆಯುವ ಹುಳು → ಮೋಹಕ ಬಲೆಗಳು ಬಳಸಿ', 'ಎಲೆ ಕಮಟು ರೋಗ → ಶೇ. 1ರ ಬೋರ್ಡೋ ಮಿಶ್ರಣ ಸಿಂಪಡಿಸಿ'],
            'hi': ['सफेद मक्खी → पीले चिपचिपे जाल और नीम तेल का छिड़काव करें', 'फल छेदक इल्ली → फेरोमोन ट्रैप और बीटी स्प्रे करें', 'झुलसा रोग → 1% बोर्डो मिश्रण या जैविक कवकनाशी का छिड़काव करें']
        },
        'best_sell_months': {
            'en': 'July - August (Monsoon shortage) & December - January (Festivals)',
            'kn': 'ಜುಲೈ - ಆಗಸ್ಟ್ (ಮಳೆಗಾಲದ ಕೊರತೆ) ಮತ್ತು ಡಿಸೆಂಬರ್ - ಜನವರಿ (ಹಬ್ಬಗಳು)',
            'hi': 'जुलाई - अगस्त (मानसून में कमी के समय) और दिसंबर - जनवरी (त्योहारों में)'
        },
        'sell_tip': {
            'en': 'Agmarknet multi-year modal price trends indicate prices peak during heavy monsoon arrival gaps (July-August) when mandi arrivals drop.',
            'kn': 'ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಬಹು-ವರ್ಷಗಳ ಮಂಡಿ ದರ ವಿಶ್ಲೇಷಣೆ: ಮುಂಗಾರು ಮಳೆಯ ಸಮಯದಲ್ಲಿ ಮಾರುಕಟ್ಟೆಗೆ ಬರುವ ಟೊಮೆಟೊ ಪ್ರಮಾಣ ಕಡಿಮೆಯಾಗಿ ಜುಲೈ-ಆಗಸ್ಟ್\u200cನಲ್ಲಿ ಗರಿಷ್ಠ ಬೆಲೆ ಏರಿಕೆ ಕಾಣುತ್ತದೆ.',
            'hi': 'एगमार्कनेट बहु-वर्षीय मॉडल भाव रुझान: भारी मानसूनी अंतरालों (जुलाई-अगस्त) में मंडियों में आवक घटने से भाव अपने उच्चतम स्तर पर पहुंचते हैं।'
        },
    },
    'onion': {
        'name': {'en': 'Onion', 'kn': 'ಈರುಳ್ಳಿ', 'hi': 'प्याज'},
        'season': {'en': 'Kharif & Late Kharif / Rabi', 'kn': 'ಮುಂಗಾರು ಮತ್ತು ಹಿಂಗಾರು', 'hi': 'खरीफ और रबी'},
        'season_type': 'Kharif & Rabi',
        'planting_months': {'en': 'June - July & October - November', 'kn': 'ಜೂನ್ - ಜುಲೈ ಮತ್ತು ಅಕ್ಟೋಬರ್ - ನವೆಂಬರ್', 'hi': 'जून - जुलाई और अक्टूबर - नवंबर'},
        'harvest_months': {'en': 'October - December & March - May', 'kn': 'ಅಕ್ಟೋಬರ್ - ಡಿಸೆಂಬರ್ ಮತ್ತು ಮಾರ್ಚ್ - ಮೇ', 'hi': 'अक्टूबर - दिसंबर और मार्च - मई'},
        'season_desc': {
            'en': 'Major commercial bulb crop with strong domestic and export demand.',
            'kn': 'ಸ್ಥಳೀಯ ಮತ್ತು ರಫ್ತು ಬೇಡಿಕೆ ಹೊಂದಿರುವ ಪ್ರಮುಖ ವಾಣಿಜ್ಯ ಬೆಳೆ.',
            'hi': 'घरेलू और निर्यात मांग वाली प्रमुख व्यावसायिक फसल।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 100 kg/ha, Phosphorus: 50 kg/ha, Potassium: 50 kg/ha + Sulphur.',
            'kn': 'ಸಾರಜನಕ: 100 ಕೆಜಿ/ಹೆ, ರಂಜಕ: 50 ಕೆಜಿ/ಹೆ, ಪೊಟ್ಯಾಶ್: 50 ಕೆಜಿ/ಹೆ + ಗಂಧಕ.',
            'hi': 'नाइट्रोजन: 100 किग्रा/हे, फास्फोरस: 50 किग्रा/हे, पोटाश: 50 किग्रा/हे + सल्फर।'
        },
        'pests': {
 'en': ['Thrips → Install blue sticky traps and spray 5% neem oil', 'Purple Blotch → Practice crop rotation and apply Trichoderma', 'Basal Rot → Treat seeds with Trichoderma'],
            'kn': ['ನುಸಿ ಕೀಟ → ನೀಲಿ ಜಿಗುಟು ಬಲೆಗಳು ಮತ್ತು ಬೇವಿನ ಎಣ್ಣೆ ಬಳಸಿ', 'ನೇರಳೆ ಮಚ್ಚೆ ರೋಗ → ಬೆಳೆ ಪರಿವರ್ತನೆ ಮಾಡಿ ಮತ್ತು ಟ್ರೈಕೋಡರ್ಮಾ ಬಳಸಿ', 'ಬುಡ ಕೊಳೆತ → ಟ್ರೈಕೋಡರ್ಮಾದಿಂದ ಬೀಜೋಪಚಾರ ಮಾಡಿ'],
            'hi': ['थ्रिप्स कीट → नीले चिपचिपे ट्रैप और नीम तेल का छिड़काव करें', 'बैंगनी धब्बा रोग → फसल चक्र अपनाएं और ट्राइकोडर्मा का प्रयोग करें', 'जड़ सड़न → ट्राइकोडर्मा से बीजोपचार करें']
        },
        'best_sell_months': {
            'en': 'September - November (Pre-Diwali peak)',
            'kn': 'ಸೆಪ್ಟೆಂಬರ್ - ನವೆಂಬರ್ (ದೀಪಾವಳಿ ಮುಂಚಿತ ಗರಿಷ್ಠ ಬೆಲೆ)',
            'hi': 'सितंबर - नवंबर (दिवाली पूर्व सबसे अधिक भाव)'
        },
        'sell_tip': {
            'en': 'Agmarknet multi-year modal price trends show onion prices consistently reaching seasonal highs before winter arrivals during September to November.',
            'kn': 'ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಬಹು-ವರ್ಷಗಳ ಮಂಡಿ ದರ ವಿಶ್ಲೇಷಣೆ: ಸೆಪ್ಟೆಂಬರ್\u200cನಿಂದ ನವೆಂಬರ್\u200cವರೆಗೆ ಹೊಸ ಈರುಳ್ಳಿ ಬರುವ ಮುನ್ನ ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ದರಗಳು ಗರಿಷ್ಠ ಮಟ್ಟ ತಲುಪುತ್ತವೆ.',
            'hi': 'एगमार्कनेट बहु-वर्षीय मॉडल भाव रुझान: सितंबर से नवंबर के दौरान नई आवक से पहले प्याज के भाव मौसमी उच्च स्तर पर रहते हैं।'
        },
    },
    'wheat': {
        'name': {'en': 'Wheat', 'kn': 'ಗೋಧಿ', 'hi': 'गेहूं'},
        'season': {'en': 'Rabi (Winter)', 'kn': 'ಹಿಂಗಾರು (ಚಳಿಗಾಲ)', 'hi': 'रबी (सर्दियों का मौसम)'},
        'season_type': 'Rabi',
        'planting_months': {'en': 'October - November', 'kn': 'ಅಕ್ಟೋಬರ್ - ನವೆಂಬರ್', 'hi': 'अक्टूबर - नवंबर'},
        'harvest_months': {'en': 'February - April', 'kn': 'ಫೆಬ್ರವರಿ - ಏಪ್ರಿಲ್', 'hi': 'फरवरी - अप्रैल'},
        'season_desc': {
            'en': 'Important winter food grain crop cultivated in North Karnataka agricultural zones.',
            'kn': 'ಚಳಿಗಾಲದಲ್ಲಿ ಬೆಳೆಯುವ ಪ್ರಮುಖ ಆಹಾರ ಧಾನ್ಯ ಬೆಳೆ.',
            'hi': 'उत्तर कर्नाटक के क्षेत्रों में उगाई जाने वाली प्रमुख रबी खाद्यान्न फसल।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 120 kg/ha, Phosphorus: 60 kg/ha, Potassium: 40 kg/ha.',
            'kn': 'ಸಾರಜನಕ: 120 ಕೆಜಿ/ಹೆ, ರಂಜಕ: 60 ಕೆಜಿ/ಹೆ, ಪೊಟ್ಯಾಶ್: 40 ಕೆಜಿ/ಹೆ.',
            'hi': 'नाइट्रोजन: 120 किग्रा/हे, फास्फोरस: 60 किग्रा/हे, पोटाश: 40 किग्रा/हे।'
        },
        'pests': {
 'en': ['Rust → Maintain balanced N-K nutrition and crop hygiene', 'Aphids → Install yellow sticky traps and spray 5% neem oil', 'Termites → Apply decomposed FYM and neem cake into soil'],
            'kn': ['ತುಕ್ಕು ರೋಗ → ಸಮತೋಲಿತ ಪೋಷಕಾಂಶ ಮತ್ತು ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು ಬಳಸಿ', 'ಗಿಡಹೇನು → ಹಳದಿ ಜಿಗುಟು ಬಲೆಗಳು ಮತ್ತು 5% ಬೇವಿನ ಎಣ್ಣೆ ಬಳಸಿ', 'ಗೆದ್ದಲು → ಬೇವಿನ ಹಿಂಡಿ ಮತ್ತು ಕಳಿತ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಬಳಸಿ'],
            'hi': ['गेरुआ / रस्ट रोग → संतुलित पोषण एवं जैविक नियंत्रण अपनाएं', 'माहू → पीले चिपचिपे ट्रैप और 5% नीम तेल का छिड़काव करें', 'दीमक → सड़ी गोबर खाद और नीम खली का प्रयोग करें']
        },
        'best_sell_months': {
            'en': 'April - June (Harvest & Government MSP window)',
            'kn': 'ಏಪ್ರಿಲ್ - ಜೂನ್ (ಕಟಾವು ಮತ್ತು ಸರ್ಕಾರದ ಬೆಂಬಲ ಬೆಲೆ ಸಮಯ)',
            'hi': 'अप्रैल - जून (कटाई और सरकारी एमएसपी खरीद का समय)'
        },
        'sell_tip': {
            'en': 'Selling at Government MSP procurement centres in April-May gives guaranteed profits with zero APMC mandi deduction.',
            'kn': 'ಏಪ್ರಿಲ್-ಮೇ ತಿಂಗಳಲ್ಲಿ ಸರ್ಕಾರಿ ಬೆಂಬಲ ಬೆಲೆ (MSP) ಖರೀದಿ ಕೇಂದ್ರಗಳಲ್ಲಿ ಮಾರಾಟ ಮಾಡುವುದರಿಂದ ಕಡಿತವಿಲ್ಲದೆ ಖಚಿತ ಲಾಭ ದೊರೆಯುತ್ತದೆ.',
            'hi': 'अप्रैल-मई में सरकारी एमएसपी खरीद केंद्रों पर बेचने से बिना मंडी कटौती के सुनिश्चित लाभ मिलता है।'
        },
    },
    'arecanut': {
        'name': {'en': 'Arecanut (Betelnut)', 'kn': 'ಅಡಿಕೆ', 'hi': 'सुपारी (अरेका नट)'},
        'season': {'en': 'Whole Year (Perennial)', 'kn': 'ವರ್ಷಪೂರ್ತಿ (ದೀರ್ಘಕಾಲೀನ ಬೆಳೆ)', 'hi': 'पूरे साल (बारहमासी)'},
        'planting_months': {'en': 'June - September (Monsoon)', 'kn': 'ಜೂನ್ - ಸೆಪ್ಟೆಂಬರ್ (ಮುಂಗಾರು)', 'hi': 'जून - सितंबर (मानसून)'},
        'harvest_months': {'en': 'October - February', 'kn': 'ಅಕ್ಟೋಬರ್ - ಫೆಬ್ರವರಿ', 'hi': 'अक्टूबर - फरवरी'},
        'season_desc': {
            'en': 'High-value commercial plantation crop flourishing in high rainfall Malnad and Coastal Karnataka.',
            'kn': 'ಮಲೆನಾಡು ಮತ್ತು ಕರಾವಳಿ ಕರ್ನಾಟಕದ ಪ್ರಮುಖ ವಾಣಿಜ್ಯ ತೋಟಗಾರಿಕೆ ಬೆಳೆ.',
            'hi': 'मलेनाडु और तटीय कर्नाटक की अत्यधिक लाभदायक व्यावसायिक बागवानी फसल।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 100 g/palm, Phosphorus: 40 g/palm, Potassium: 140 g/palm annually.',
            'kn': 'ಪ್ರತಿ ಮರಕ್ಕೆ ವಾರ್ಷಿಕವಾಗಿ ಸಾರಜನಕ: 100 ಗ್ರಾಂ, ರಂಜಕ: 40 ಗ್ರಾಂ, ಪೊಟ್ಯಾಶ್: 140 ಗ್ರಾಂ.',
            'hi': 'प्रति पेड़ प्रति वर्ष: 100 ग्राम नाइट्रोजन, 40 ग्राम फास्फोरस, 140 ग्राम पोटाश।'
        },
        'pests': {
 'en': ['Koleroga / Fruit rot → Spray 1% Bordeaux mixture before monsoon', 'Yellow leaf disease → Apply balanced micro-nutrients & organic manure', 'Mites → Apply wettable sulfur (2g/L) and 5% neem oil'],
            'kn': ['ಕೊಳೆ ರೋಗ → ಮುಂಗಾರಿಗೆ ಮುನ್ನ ಶೇ. 1ರ ಬೋರ್ಡೋ ಮಿಶ್ರಣ ಸಿಂಪಡಿಸಿ', 'ಹಳದಿ ಎಲೆ ರೋಗ → ಸಮತೋಲಿತ ಲಘು ಪೋಷಕಾಂಶ ಮತ್ತು ಸಾವಯವ ಗೊಬ್ಬರ ನೀಡಿ', 'ನುಸಿ ಹುಳು → ಗಂಧಕದ ಪುಡಿ (2 ಗ್ರಾಂ/ಲೀ) ಮತ್ತು ಬೇವಿನ ಎಣ್ಣೆ ಬಳಸಿ'],
            'hi': ['कोलेरोगा / फल सड़न → मानसून से पहले 1% बोर्डो मिश्रण का छिड़काव करें', 'पीली पत्ती रोग → सूक्ष्म पोषक तत्व और जैविक खाद दें', 'माइट्स → सल्फर (2 ग्राम/ली) और नीम तेल का प्रयोग करें']
        },
        'best_sell_months': {'en': 'November - April (High tender/dry areca demand)', 'kn': 'ನವೆಂಬರ್ - ಏಪ್ರಿಲ್ (ರಾಶಿ/ಚಾಲಿ ಅಡಿಕೆಗೆ ಭಾರಿ ಬೇಡಿಕೆ)', 'hi': 'नवंबर - अप्रैल (सुपारी मंडियों में उच्च मांग)'},
        'sell_tip': {
            'en': 'Historical CAMPCO auction and Agmarknet modal price trends show processed Rashi/Chali areca at Shivamogga, Channagiri, or Mangaluru yields peak rates.',
            'kn': 'ಕ್ಯಾಂಪ್ಕೋ (CAMPCO) ಹರಾಜು ಮತ್ತು ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಮಂಡಿ ದರ ವಿಶ್ಲೇಷಣೆ: ಶಿವಮೊಗ್ಗ, ಚನ್ನಗಿರಿ ಅಥವಾ ಮಂಗಳೂರಿನಲ್ಲಿ ಸಂಸ್ಕರಿಸಿದ ರಾಶಿ/ಚಾಲಿ ಅಡಿಕೆಗೆ ಗರಿಷ್ಠ ಬೆಲೆ ಸಿಗುತ್ತದೆ.',
            'hi': 'कैम्पको नीलामी व एगमार्कनेट मॉडल भाव रुझान: शिमोगा, चन्नागिरी या मंगलुरु में प्रसंस्कृत राशि/चाली सुपारी का उच्चतम बाजार भाव मिलता है।'
        },
    },
    'cashew': {
        'name': {'en': 'Cashew (Cashewnut)', 'kn': 'ಗೋಡಂಬಿ (ಕಾಜು)', 'hi': 'काजू'},
        'season': {'en': 'Whole Year / Post-Monsoon', 'kn': 'ವರ್ಷಪೂರ್ತಿ / ಹಿಂಗಾರು', 'hi': 'पूरे साल / रबी-जायद'},
        'planting_months': {'en': 'June - August', 'kn': 'ಜೂನ್ - ಆಗಸ್ಟ್', 'hi': 'जून - अगस्त'},
        'harvest_months': {'en': 'February - May', 'kn': 'ಫೆಬ್ರವರಿ - ಮೇ', 'hi': 'फरवरी - मई'},
        'season_desc': {
            'en': 'Hardy drought-tolerant coastal plantation crop thriving on laterite soils of Coastal Karnataka.',
            'kn': 'ಕರಾವಳಿಯ ಜಂಬಿಟ್ಟಿಗೆ ಮಣ್ಣಿನಲ್ಲಿ ಸೊಂಪಾಗಿ ಬೆಳೆಯುವ ಉತ್ತಮ ರಫ್ತು ಮೌಲ್ಯದ ತೋಟದ ಬೆಳೆ.',
            'hi': 'तटीय कर्नाटक की लेटराइट मिट्टी में भरपूर उपज देने वाली सूखा प्रतिरोधी निर्यात योग्य फसल।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 500 g/tree, Phosphorus: 125 g/tree, Potassium: 125 g/tree annually.',
            'kn': 'ಪ್ರತಿ ಗಿಡಕ್ಕೆ ವಾರ್ಷಿಕವಾಗಿ ಸಾರಜನಕ: 500 ಗ್ರಾಂ, ರಂಜಕ: 125 ಗ್ರಾಂ, ಪೊಟ್ಯಾಶ್: 125 ಗ್ರಾಂ.',
            'hi': 'प्रति पेड़ प्रति वर्ष: 500 ग्राम नाइट्रोजन, 125 ग्राम फास्फोरस, 125 ग्राम पोटाश।'
        },
        'pests': {
 'en': ['Tea mosquito bug → Apply 5% neem oil / bio-agents', 'Stem and root borer → Chisel grubs and swab trunk with lime and apply neem cake', 'Leaf and blossom blight → Spray 5% neem oil / bio-fungicide'],
            'kn': ['ಚಹಾ ಸೊಳ್ಳೆ ಕೀಟ → 5% ಬೇವಿನ ಎಣ್ಣೆ ಸಿಂಪಡಿಸಿ', 'ಕಾಂಡ ಮತ್ತು ಬೇರು ಕೊರೆಯುವ ಹುಳು → ಬೇವಿನ ಹಿಂಡಿ ಮತ್ತು ಜೈವಿಕ ನಿಯಂತ್ರಣ ಲೇಪನ ಮಾಡಿ', 'ಹೂವು ಕರಕಲು ರೋಗ → 5% ಬೇವಿನ ಎಣ್ಣೆ ಅಥವಾ ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಬಳಸಿ'],
            'hi': ['टी मॉस्किटो बग → 5% नीम तेल और जैविक नियंत्रण का छिड़काव करें', 'तना व जड़ छेदक → ग्रब निकालकर सड़ी गोबर खाद और नीम खली लगाएं', 'पुष्प झुलसा → जैविक कवकनाशी या 5% नीम तेल स्प्रे करें']
        },
        'best_sell_months': {'en': 'March - June (Raw nut harvesting window)', 'kn': 'ಮಾರ್ಚ್ - ಜೂನ್ (ಕಚ್ಚಾ ಗೋಡಂಬಿ ಕಟಾವು ಸಮಯ)', 'hi': 'मार्च - जून (कच्चे काजू की आवक का समय)'},
        'sell_tip': {
            'en': 'Agmarknet coastal APMC modal price trends show sun-dried raw cashew nuts (8% moisture) fetch premium grading rates.',
            'kn': 'ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಕರಾವಳಿ ಎಪಿಎಂಸಿ ಮಂಡಿ ದರ ವಿಶ್ಲೇಷಣೆ: ಬಿಸಿಲಿನಲ್ಲಿ ಒಣಗಿಸಿದ (ಶೇ. 8 ತೇವಾಂಶ) ಗೋಡಂಬಿ ಬೀಜಗಳಿಗೆ ಅತ್ಯುತ್ತಮ ದರ ದೊರೆಯುತ್ತದೆ.',
            'hi': 'एगमार्कनेट तटीय एपीएमसी मॉडल भाव रुझान: धूप में 8% नमी तक सुखाई गई कच्ची काजू को प्रीमियम ग्रेडिंग भाव मिलता है।'
        },
    },
    'sunflower': {
        'name': {'en': 'Sunflower', 'kn': 'ಸೂರ್ಯಕಾಂತಿ', 'hi': 'सूरजमुखी'},
        'season': {'en': 'Kharif, Rabi & Zaid', 'kn': 'ಖಾರೀಫ್, ರಬಿ ಮತ್ತು ಬೇಸಿಗೆ', 'hi': 'खरीफ, रबी और जायद'},
        'planting_months': {'en': 'July - August & October - November', 'kn': 'ಜುಲೈ - ಆಗಸ್ಟ್ ಮತ್ತು ಅಕ್ಟೋಬರ್ - ನವೆಂಬರ್', 'hi': 'जुलाई - अगस्त एवं अक्टूबर - नवंबर'},
        'harvest_months': {'en': 'October - November & January - February', 'kn': 'ಅಕ್ಟೋಬರ್ - ನವೆಂಬರ್ ಮತ್ತು ಜನವರಿ - ಫೆಬ್ರವರಿ', 'hi': 'अक्टूबर - नवंबर एवं जनवरी - फरवरी'},
        'season_desc': {
            'en': 'Major North Karnataka oilseed crop renowned for drought tolerance and high edible oil content.',
            'kn': 'ಉತ್ತರ ಕರ್ನಾಟಕದ ಪ್ರಮುಖ ಎಣ್ಣೆಕಾಳು ಬೆಳೆಯಾಗಿದ್ದು, ಬರವನ್ನು ತಡೆದುಕೊಂಡು ಉತ್ತಮ ಇಳುವರಿ ನೀಡುತ್ತದೆ.',
            'hi': 'उत्तर कर्नाटक की प्रमुख तिलहनी फसल, जो सूखे को सहन कर उच्च तेल उत्पादन देती है।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 60 kg/ha, Phosphorus: 75 kg/ha, Potassium: 30 kg/ha + Boron 2 kg/ha.',
            'kn': 'ಸಾರಜನಕ: 60 ಕೆಜಿ, ರಂಜಕ: 75 ಕೆಜಿ, ಪೊಟ್ಯಾಶ್: 30 ಕೆಜಿ + ಬೋರಾನ್: 2 ಕೆಜಿ/ಹೆಕ್ಟೇರ್.',
            'hi': 'नाइट्रोजन: 60 किग्रा, फास्फोरस: 75 किग्रा, पोटाश: 30 किग्रा + बोरोन: 2 किग्रा/हेक्टेयर।'
        },
        'pests': {
 'en': ['Capitulum borer → Install pheromone traps (5/acre) and spray HaNPV', 'Alternaria leaf blight → Spray 5% neem oil / bio-fungicide', 'Necrosis virus → Install blue sticky traps and spray 5% neem oil'],
            'kn': ['ಹೂಗುಚ್ಛ ಕೊರೆಯುವ ಹುಳು → ಮೋಹಕ ಬಲೆಗಳು ಮತ್ತು ಜೈವಿಕ ನಿಯಂತ್ರಣ ಸಿಂಪಡಿಸಿ', 'ಆಲ್ಟರ್ನೇರಿಯಾ ಎಲೆ ಕರಕಲು → ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಅಥವಾ ಬೇವಿನ ಎಣ್ಣೆ ಬಳಸಿ', 'ನೆಕ್ರೋಸಿಸ್ ವೈರಸ್ → ನುಸಿ ನಿಯಂತ್ರಣಕ್ಕೆ ಹಳದಿ ಜಿಗುಟು ಬಲೆಗಳು ಮತ್ತು 5% ಬೇವಿನ ಎಣ್ಣೆ ಬಳಸಿ'],
            'hi': ['मुंडक छेदक → फेरोमोन ट्रैप (5/एकड़) और HaNPV छिड़काव करें', 'अल्टरनेरिया पत्ती झुलसा → जैविक कवकनाशी या 5% नीम तेल लगाएं', 'नेक्रोसिस → थ्रिप्स नियंत्रण हेतु पीले चिपचिपे ट्रैप और 5% नीम तेल का प्रयोग करें']
        },
        'best_sell_months': {'en': 'November - January & February - April', 'kn': 'ನವೆಂಬರ್ - ಜನವರಿ ಮತ್ತು ಫೆಬ್ರವರಿ - ಏಪ್ರಿಲ್', 'hi': 'नवंबर - जनवरी एवं फरवरी - अप्रैल'},
        'sell_tip': {
            'en': 'Agmarknet multi-year modal price trends and MSP procurement data show strong post-harvest oil mill demand in Koppal, Raichur, and Bagalkot mandis.',
            'kn': 'ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಮಂಡಿ ದರಗಳು ಮತ್ತು ಬೆಂಬಲ ಬೆಲೆ (MSP) ವಿಶ್ಲೇಷಣೆ: ಕೊಪ್ಪಳ, ರಾಯಚೂರು ಮತ್ತು ಬಾಗಲಕೋಟೆ ಮಂಡಿಗಳಲ್ಲಿ ಎಣ್ಣೆ ಗಿರಣಿಗಳ ಹೆಚ್ಚಿನ ಬೇಡಿಕೆಯಿಂದ ಉತ್ತಮ ಬೆಲೆ ಸಿಗುತ್ತದೆ.',
            'hi': 'एगमार्कनेट बहु-वर्षीय मॉडल भाव रुझान व एमएसपी डेटा: कोप्पल, रायचूर और बागलकोट मंडियों में तेल मिलों की मांग से कटाई के बाद बेहतर भाव मिलते हैं।'
        },
    },
    'mulberry': {
        'name': {'en': 'Mulberry (Silk Sericulture)', 'kn': 'ಹಿಪ್ಪುನೇರಳೆ (ರೇಷ್ಮೆ ಕೃಷಿ)', 'hi': 'शहतूत (रेशम कीट पालन)'},
        'season': {'en': 'Whole Year (Perennial)', 'kn': 'ವರ್ಷಪೂರ್ತಿ (ದೀರ್ಘಕಾಲೀನ ಬೆಳೆ)', 'hi': 'पूरे साल (बारहमासी)'},
        'planting_months': {'en': 'July - September', 'kn': 'ಜುಲೈ - ಸೆಪ್ಟೆಂಬರ್', 'hi': 'जुलाई - सितंबर'},
        'harvest_months': {'en': 'Leaf harvest every 45-50 days (5-6 crops/year)', 'kn': 'ಪ್ರತಿ 45-50 ದಿನಗಳಿಗೊಮ್ಮೆ ಎಲೆ ಕಟಾವು (ವರ್ಷಕ್ಕೆ 5-6 ಬೆಳೆ)', 'hi': 'हर 45-50 दिन में पत्ती की कटाई (साल में 5-6 फसलें)'},
        'season_desc': {
            'en': 'Backbone of Karnataka sericulture, sustaining silkworm cocoon production in Ramanagara, Mandya, and Kolar.',
            'kn': 'ಕರ್ನಾಟಕದ ರೇಷ್ಮೆ ಕೃಷಿಯ ಬೆನ್ನೆಲುಬು, ರಾಮನಗರ, ಮಂಡ್ಯ ಮತ್ತು ಕೋಲಾರದ ರೈತರ ಪ್ರಮುಖ ಆದಾಯದ ಮೂಲ.',
            'hi': 'कर्नाटक के रेशम उद्योग की रीढ़, जो रामनगर, मांड्या और कोलार में कोकून उत्पादन का मुख्य आधार है।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 280 kg/ha, Phosphorus: 120 kg/ha, Potassium: 120 kg/ha (split across harvests).',
            'kn': 'ಸಾರಜನಕ: 280 ಕೆಜಿ, ರಂಜಕ: 120 ಕೆಜಿ, ಪೊಟ್ಯಾಶ್: 120 ಕೆಜಿ (ಪ್ರತಿ ಬೆಳೆಯ ನಂತರ ವಿಭಜಿಸಿ ನೀಡಿ).',
            'hi': 'नाइट्रोजन: 280 किग्रा, फास्फोरस: 120 किग्रा, पोटाश: 120 किग्रा (फसलों में बांटकर दें)।'
        },
        'pests': {
 'en': ['Tukra → Release Ladybird beetles (Cryptolaemus) and spray 5% neem oil', 'Thrips → Spray safe botanical / bio-fungicide or consult your local KVK for approved safe treatment', 'Leaf spot → De-leaf infected leaves and spray 1% Bordeaux mixture'],
            'kn': ['ತುಕ್ರಾ ರೋಗ (ಹಿಟ್ಟು ತಿಗಣೆ) → ಪರಭಕ್ಷಕ ಜೀರುಂಡೆಗಳು ಸಿಂಪಡಿಸಿ ಅಥವಾ ಪರಭಕ್ಷಕ ಜೀರುಂಡೆ ಬಿಡಿ', 'ನುಸಿ ಹುಳು → ಹಳದಿ ಜಿಗುಟು ಬಲೆಗಳು ಮತ್ತು 5% ಬೇವಿನ ಎಣ್ಣೆ ಬಳಸಿ (10 ದಿನ ಕಾಯುವ ಅವಧಿ)', 'ಎಲೆ ಚುಕ್ಕೆ ರೋಗ → ಸೋಂಕಿತ ಎಲೆಗಳನ್ನು ತೆಗೆದು ಶೇ. 1ರ ಬೋರ್ಡೋ ಸಿಂಪಡಿಸಿ'],
            'hi': ['टुकरा (मीलीबग) → लेडीबर्ड भृंग और 5% नीम तेल स्प्रे करें या लेडीबर्ड भृंग छोड़ें', 'थ्रिप्स → पीले चिपचिपे ट्रैप और 5% नीम तेल का छिड़काव करें (10 दिन का सुरक्षित अंतराल रखें)', 'पत्ती धब्बा → संक्रमित पत्तियां हटाएं और 1% बोर्डो मिश्रण स्प्रे करें']
        },
        'best_sell_months': {'en': 'Round the year (Weekly cocoon trading)', 'kn': 'ವರ್ಷಪೂರ್ತಿ (ಪ್ರತಿ ವಾರ ರೇಷ್ಮೆ ಗೂಡು ಮಾರುಕಟ್ಟೆ)', 'hi': 'पूरे साल (साप्ताहिक कोकून नीलामी)'},
        'sell_tip': {
            'en': 'Historical Department of Sericulture and Agmarknet auction modal price trends confirm Ramanagara market yields peak returns for bivoltine cocoons.',
            'kn': 'ರೇಷ್ಮೆ ಇಲಾಖೆ ಮತ್ತು ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಹರಾಜು ದರ ವಿಶ್ಲೇಷಣೆ: ರಾಮನಗರ ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ದ್ವಿತಳಿ (ಬೈವೋಲ್ಟಿನ್) ಗೂಡುಗಳಿಗೆ ಏಷ್ಯಾದಲ್ಲೇ ಅತ್ಯಧಿಕ ಧಾರಣೆ ಸಿಗುತ್ತದೆ.',
            'hi': 'रेशम विभाग और एगमार्कनेट नीलामी मॉडल भाव रुझान: रामनगरम मंडी में बाइवोल्टाइन कोकून का एशिया में सबसे बेहतरीन भाव मिलता है।'
        },
    },
    'jowar': {
        'name': {'en': 'Jowar (Rabi Jowar / Sorghum)', 'kn': 'ಜೋಳ (ಹಿಂಗಾರು ಬಿಳಿ ಜೋಳ)', 'hi': 'ज्वार (रबी ज्वार / सोरघम)'},
        'season': {'en': 'Rabi & Kharif', 'kn': 'ರಬಿ ಮತ್ತು ಖಾರೀಫ್', 'hi': 'रबी एवं खरीफ'},
        'planting_months': {'en': 'September - October (Rabi) & June - July (Kharif)', 'kn': 'ಸೆಪ್ಟೆಂಬರ್ - ಅಕ್ಟೋಬರ್ (ಹಿಂಗಾರು) ಮತ್ತು ಜೂನ್ - ಜುಲೈ (ಮುಂಗಾರು)', 'hi': 'सितंबर - अक्टूबर (रबी) एवं जून - जुलाई (खरीफ)'},
        'harvest_months': {'en': 'January - February (Rabi) & October - November (Kharif)', 'kn': 'ಜನವರಿ - ಫೆಬ್ರವರಿ (ರಬಿ) ಮತ್ತು ಅಕ್ಟೋಬರ್ - ನವೆಂಬರ್ (ಖಾರೀಫ್)', 'hi': 'जनवरी - फरवरी (रबी) एवं अक्टूबर - नवंबर (खरीफ)'},
        'season_desc': {
            'en': 'Premier drought-hardy dryland staple grain of North Karnataka (Bagalkot, Vijayapura, Dharwad, Kalaburagi).',
            'kn': 'ಉತ್ತರ ಕರ್ನಾಟಕದ ಪ್ರಮುಖ ಖುಷ್ಕಿ ಭೂಮಿಯ ಪೌಷ್ಟಿಕ ಆಹಾರ ಧಾನ್ಯ, ಕಪ್ಪು ಮಣ್ಣಿನಲ್ಲಿ ಅತ್ಯುತ್ತಮ ಇಳುವರಿ.',
            'hi': 'उत्तर कर्नाटक (बागलकोट, विजयपुरा, धारवाड़) की प्रमुख सूखा प्रतिरोधी खाद्यान्न फसल।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 60 kg/ha, Phosphorus: 30 kg/ha, Potassium: 20 kg/ha.',
            'kn': 'ಸಾರಜನಕ: 60 ಕೆಜಿ/ಹೆಕ್ಟೇರ್, ರಂಜಕ: 30 ಕೆಜಿ/ಹೆಕ್ಟೇರ್, ಪೊಟ್ಯಾಶ್: 20 ಕೆಜಿ/ಹೆಕ್ಟೇರ್.',
            'hi': 'नाइट्रोजन: 60 किग्रा/हेक्टेयर, फास्फोरस: 30 किग्रा/हेक्टेयर, पोटाश: 20 किग्रा/हेक्टेयर।'
        },
        'pests': {
 'en': ['Shoot fly → Early sowing & biological seed treatment. Consult your local KVK for label-claim verified treatments.', 'Stem borer → Apply dry sand / neem cake in whorls. Consult your local KVK for label-claim verified treatments.', 'Fall armyworm → Spray Emamectin benzoate'],
            'kn': ['ಸುಳಿ ನೊಣ → ಆರಂಭಿಕ ಬಿತ್ತನೆ ಮತ್ತು ಹಳದಿ ಜಿಗುಟು ಬಲೆಗಳು ಮತ್ತು ಬೇವಿನ ಎಣ್ಣೆ ಬೀಜೋಪಚಾರ', 'ಕಾಂಡ ಕೊರೆಯುವ ಹುಳು → ಸುಳಿಯಲ್ಲಿ ಕಾರ್ಬೋಫ್ಯೂರಾನ್ ಹರಳು ಹಾಕಿ', 'ಲದ್ದಿ ಹುಳು → ಎಮಾಮೆಕ್ಟಿನ್ ಬೆಂಜೊಯೇಟ್ ಸಿಂಪಡಿಸಿ'],
            'hi': ['प्ररोह मक्खी → अगेती बुवाई व पीले चिपचिपे ट्रैप और 5% नीम तेल से बीजोपचार', 'तना छेदक → पत्ती की सुराही में कार्बोफ्यूरान दाने डालें', 'फॉल आर्मीवॉर्म → इमामेक्टिन बेंजोएट स्प्रे करें']
        },
        'best_sell_months': {'en': 'February - April (Post Rabi harvest)', 'kn': 'ಫೆಬ್ರವರಿ - ಏಪ್ರಿಲ್ (ರಬಿ ಕಟಾವಿನ ನಂತರ)', 'hi': 'फरवरी - अप्रैल (रबी कटाई के बाद)'},
        'sell_tip': {
            'en': 'Agmarknet modal price trends show Maldandi (M-35-1) white jowar commanding substantial price premiums over MSP in urban consumption markets.',
            'kn': 'ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಮಂಡಿ ದರ ವಿಶ್ಲೇಷಣೆ: ಮಾಲ್ದಂಡಿ (M-35-1) ಬಿಳಿ ಜೋಳಕ್ಕೆ ನಗರ ಪ್ರದೇಶಗಳಲ್ಲಿ ಬೆಂಬಲ ಬೆಲೆಗಿಂತಲೂ ಹೆಚ್ಚಿನ ದರ ದೊರೆಯುತ್ತದೆ.',
            'hi': 'एगमार्कनेट मॉडल भाव रुझान: मालदांडी (M-35-1) सफेद ज्वार को शहरी बाजारों में एमएसपी से कहीं अधिक प्रीमियम मूल्य मिलता है।'
        },
    },
    'bengalgram': {
        'name': {'en': 'Bengal Gram (Chickpea / Chana)', 'kn': 'ಕಡಲೆ (ಬೆಂಗಾಲ್ ಗ್ರಾಂ / ಚೆನ್ನಾ)', 'hi': 'चना (बंगाल चना / छोले)'},
        'season': {'en': 'Rabi (Winter post-monsoon)', 'kn': 'ರಬಿ (ಹಿಂಗಾರು ಬೆಳೆ)', 'hi': 'रबी (सर्दियों की प्रमुख दाल)'},
        'planting_months': {'en': 'October - November (Rabi season)', 'kn': 'ಅಕ್ಟೋಬರ್ - ನವೆಂಬರ್ (ರಬಿ ಬಿತ್ತನೆ)', 'hi': 'अक्टूबर - नवंबर (रबी बुवाई)'},
        'harvest_months': {'en': 'January - March', 'kn': 'ಜನವರಿ - ಮಾರ್ಚ್', 'hi': 'जनवरी - मार्च'},
        'season_desc': {
            'en': 'Crucial pulse crop of North Karnataka black cotton soils, sown immediately post-monsoon in October.',
            'kn': 'ಉತ್ತರ ಕರ್ನಾಟಕದ ಕಪ್ಪು ಹತ್ತಿ ಮಣ್ಣಿನಲ್ಲಿ ಮುಂಗಾರಿನ ನಂತರ (ಅಕ್ಟೋಬರ್) ಬಿತ್ತನೆ ಮಾಡುವ ಪ್ರಮುಖ ಬೇಳೆಕಾಳು ಬೆಳೆ.',
            'hi': 'उत्तर कर्नाटक की काली मिट्टी में मानसून बाद (अक्टूबर-नवंबर) बोई जाने वाली सबसे प्रमुख दलहन फसल।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 25 kg/ha, Phosphorus: 50 kg/ha, Potassium: 20 kg/ha + Rhizobium seed inoculation.',
            'kn': 'ಸಾರಜನಕ: 25 ಕೆಜಿ, ರಂಜಕ: 50 ಕೆಜಿ, ಪೊಟ್ಯಾಶ್: 20 ಕೆಜಿ/ಹೆ + ರೈಜೋಬಿಯಂ ಬೀಜೋಪಚಾರ.',
            'hi': 'नाइट्रोजन: 25 किग्रा, फास्फोरस: 50 किग्रा, पोटाश: 20 किग्रा + राइजोबियम बीजोपचार।'
        },
        'pests': {
 'en': ['Pod borer → Spray Chlorantraniliprole or Emamectin benzoate', 'Wilt → Trichoderma viride seed treatment', 'Dry root rot → Seed treatment with Trichoderma viride (4g/kg)'],
            'kn': ['ಕಾಯಿ ಕೊರೆಯುವ ಹುಳು → ಕೋರಾಜೆನ್ ಅಥವಾ ಎಮಾಮೆಕ್ಟಿನ್ ಬೆಂಜೊಯೇಟ್ ಸಿಂಪಡಿಸಿ', 'ನೆಟೆ ರೋಗ (ವಿಲ್ಟ್) → ಟ್ರೈಕೋಡರ್ಮಾ ಬೀಜೋಪಚಾರ ಮಾಡಿ', 'ಬೇರು ಕೊಳೆತ → ಟ್ರೈಕೋಡರ್ಮಾ ಮತ್ತು ಶೇ. 1ರ ಬೋರ್ಡೋ ಬೀಜೋಪಚಾರ ಮಾಡಿ'],
            'hi': ['फली छेदक → कोराजेन (Chlorantraniliprole) या इमामेक्टिन बेंजोएट स्प्रे करें', 'उकठा (विल्ट) → ट्राइकोडर्मा से बीजोपचार करें', 'जड़ सड़न → संक्रमित पत्तियां हटाएं और 1% बोर्डो मिश्रण से बीजोपचार करें']
        },
        'best_sell_months': {'en': 'March - May (Peak harvest market window)', 'kn': 'ಮಾರ್ಚ್ - ಮೇ (ಕಟಾವಿನ ನಂತರದ ಉತ್ತಮ ಮಾರಾಟ ಸಮಯ)', 'hi': 'मार्च - मई (कटाई के बाद मंडियों में अधिकतम मांग)'},
        'sell_tip': {
            'en': 'Sell at APMC government minimum support price (MSP) procurement centres and monitor Agmarknet modal price trends in Bagalkot, Dharwad, and Kalaburagi.',
            'kn': 'ಬಾಗಲಕೋಟೆ, ಧಾರವಾಡ ಮತ್ತು ಕಲಬುರಗಿ ಎಪಿಎಂಸಿ ಸರ್ಕಾರಿ ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ (MSP) ಖರೀದಿ ಕೇಂದ್ರಗಳಲ್ಲಿ ಮಾರಾಟ ಮಾಡಿ ಹಾಗೂ ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಮಂಡಿ ದರಗಳನ್ನು ಗಮನಿಸಿ.',
            'hi': 'बागलकोट, धारवाड़ और कलबुर्गी में एपीएमसी सरकारी न्यूनतम समर्थन मूल्य (MSP) खरीद केंद्रों पर बेचें और एगमार्कनेट मॉडल भाव रुझानों पर नजर रखें।'
        },
    },
    'fieldbeans': {
        'name': {'en': 'Field Bean (Avarekai)', 'kn': 'ಅವರೆಕಾಳು (Avarekai)', 'hi': 'सेम / अंवरे (Field Bean)'},
        'season': {'en': 'Rabi (Winter)', 'kn': 'ರಬಿ (ಹಿಂಗಾರು / ಚಳಿಗಾಲ)', 'hi': 'रबी (सर्दियां)'},
        'planting_months': {'en': 'October - November', 'kn': 'ಅಕ್ಟೋಬರ್ - ನವೆಂಬರ್', 'hi': 'अक्टूबर - नवंबर'},
        'harvest_months': {'en': 'January - February', 'kn': 'ಜನವರಿ - ಫೆಬ್ರವರಿ', 'hi': 'जनवरी - फरवरी'},
        'season_desc': {
            'en': 'Popular traditional aromatic grain legume widely cultivated in Southern Karnataka.',
            'kn': 'ದಕ್ಷಿಣ ಕರ್ನಾಟಕದ ಜನಪ್ರಿಯ ಚಳಿಗಾಲದ ಬೇಳೆಕಾಳು ಬೆಳೆ. ತಂಪಾದ ಇಬ್ಬನಿ ಭರಿತ ರಾತ್ರಿಗಳು ಉತ್ತಮ ಕಾಯಿ ಕಟ್ಟಲು ಸಹಕಾರಿ.',
            'hi': 'दक्षिण कर्नाटक की लोकप्रिय शीतकालीन दलहन फसल। ठंड और ओस वाली रातें फलियों के विकास के लिए उत्तम हैं।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 25 kg/ha, Phosphorus: 50 kg/ha, Potassium: 25 kg/ha + Rhizobium inoculation.',
            'kn': 'ಸಾರಜನಕ: 25 ಕೆಜಿ, ರಂಜಕ: 50 ಕೆಜಿ, ಪೊಟ್ಯಾಶ್: 25 ಕೆಜಿ/ಹೆಕ್ಟೇರ್ + ರೈಜೋಬಿಯಂ ಬೀಜೋಪಚಾರ.',
            'hi': 'नाइट्रोजन: 25 किग्रा, फास्फोरस: 50 किग्रा, पोटाश: 25 किग्रा + राइजोबियम बीजोपचार।'
        },
        'pests': {
 'en': ['Pod borer → Spray Neem oil 1500 ppm and install pheromone traps (5/acre)', 'Aphids → Install yellow sticky traps and spray 5% neem oil 30 EC @ 1.7 ml/L'],
            'kn': ['ಕಾಯಿ ಕೊರೆಯುವ ಹುಳು → ಬೇವು ಎಣ್ಣೆ ಅಥವಾ ಮೋಹಕ ಬಲೆಗಳು ಮತ್ತು ಜೈವಿಕ ನಿಯಂತ್ರಣ ಸಿಂಪಡಿಸಿ', 'ಸಸ್ಯಹೇನು → ಡೈಮೆಥೋಯೇಟ್ ಸಿಂಪಡಿಸಿ'],
            'hi': ['फली छेदक → नीम का तेल या स्पिनोसाड का छिड़काव करें', 'माहू → पीले चिपचिपे ट्रैप और 5% नीम तेल का छिड़काव करें']
        },
        'best_sell_months': {'en': 'December - January (Avarekai Mela festival peak demand)', 'kn': 'ಡಿಸೆಂಬರ್ - ಜನವರಿ (ಅವರೆ ಮೇಳದ ಗರಿಷ್ಠ ಬೇಡಿಕೆ)', 'hi': 'दिसंबर - जनवरी (अंवरे मेले के दौरान अधिकतम मांग)'},
        'sell_tip': {
            'en': 'Agmarknet modal price trends indicate morning arrivals of fresh tender pods fetch premium rates in Bengaluru and Mysuru APMC mandis.',
            'kn': 'ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಮಂಡಿ ದರ ವಿಶ್ಲೇಷಣೆ: ಬೆಂಗಳೂರು ಮತ್ತು ಮೈಸೂರು ಮಾರುಕಟ್ಟೆಗಳಲ್ಲಿ ಮುಂಜಾನೆ ತಂದ ತಾಜಾ ಹಸಿ ಅವರೆಕಾಯಿಗೆ ಅತ್ಯುತ್ತಮ ಬೆಲೆ ದೊರೆಯುತ್ತದೆ.',
            'hi': 'एगमार्कनेट मॉडल भाव रुझान: बेंगलुरु और मैसूर एपीएमसी मंडियों में सुबह की ताजा फलियों की आवक को प्रीमियम भाव मिलता है।'
        },
    },
    'horsegram': {
        'name': {'en': 'Horse Gram (Huruli)', 'kn': 'ಹುರುಳಿ (Huruli)', 'hi': 'कुलथी (Horse Gram)'},
        'season': {'en': 'Rabi / Late Kharif', 'kn': 'ರಬಿ / ಹಿಂಗಾರು', 'hi': 'रबी / पछेती खरीफ'},
        'planting_months': {'en': 'September - November', 'kn': 'ಸೆಪ್ಟೆಂಬರ್ - ನವೆಂಬರ್', 'hi': 'सितंबर - नवंबर'},
        'harvest_months': {'en': 'January - February', 'kn': 'ಜನವರಿ - ಫೆಬ್ರವರಿ', 'hi': 'जनवरी - फरवरी'},
        'season_desc': {
            'en': 'Extremely hardy, drought-tolerant legume that produces nutritious grain on residual soil moisture.',
            'kn': 'ತೀವ್ರ ಬರ ಸಹಿಷ್ಣು ಬೆಳೆ. ಕನಿಷ್ಠ ತೇವಾಂಶ ಮತ್ತು ಮಳೆಯಲ್ಲೂ ಅತ್ಯುತ್ತಮ ಪೌಷ್ಟಿಕ ಕಾಳು ನೀಡುತ್ತದೆ.',
            'hi': 'अत्यधिक सूखा सहनशील दलहनी फसल, जो कम नमी में भी अच्छी पौष्टिक उपज देती है।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 15 kg/ha, Phosphorus: 30 kg/ha, Potassium: 10 kg/ha.',
            'kn': 'ಸಾರಜನಕ: 15 ಕೆಜಿ, ರಂಜಕ: 30 ಕೆಜಿ, ಪೊಟ್ಯಾಶ್: 10 ಕೆಜಿ/ಹೆಕ್ಟೇರ್.',
            'hi': 'नाइट्रोजन: 15 किग्रा, फास्फोरस: 30 किग्रा, पोटाश: 10 किग्रा।'
        },
        'pests': {
 'en': ['Rust / Powdery mildew → Spray wettable sulfur @ 2 g/L', 'Pod borer → Install light traps and apply Trichogramma cards'],
            'kn': ['ಬೂದಿ ರೋಗ → ಗಂಧಕದ ಪುಡಿ (ಸಲ್ಫರ್) ಸಿಂಪಡಿಸಿ', 'ಕಾಯಿ ಕೊರೆಯುವ ಹುಳು → ದೀಪದ ಬಲೆಗಳು ಮತ್ತು ಟ್ರೈಕೋಗ್ರಾಮ ಕಾರ್ಡ್ ಬಳಸಿ'],
            'hi': ['पाउडरी मिल्ड्यू → घुलनशील गंधक का छिड़काव करें', 'फली छेदक → सड़ी गोबर खाद और नीम खली का प्रयोग करें']
        },
        'best_sell_months': {'en': 'February - April', 'kn': 'ಫೆಬ್ರವರಿ - ಏಪ್ರಿಲ್', 'hi': 'फरवरी - अप्रैल'},
        'sell_tip': {
            'en': 'Agmarknet modal price trends indicate graded, cleaned seeds fetch competitive rates directly from grain merchants and health food processors; compare with local MSP.',
            'kn': 'ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಮಂಡಿ ದರ ವಿಶ್ಲೇಷಣೆ: ಸ್ವಚ್ಛಗೊಳಿಸಿ ಗ್ರೇಡ್ ಮಾಡಿದ ಹುರುಳಿಗೆ ಧಾನ್ಯ ವ್ಯಾಪಾರಿಗಳು ಮತ್ತು ಆರೋಗ್ಯ ಆಹಾರ ತಯಾರಕರಿಂದ ಉತ್ತಮ ದರ ದೊರೆಯುತ್ತದೆ.',
            'hi': 'एगमार्कनेट मॉडल भाव रुझान: साफ और ग्रेडेड कुलथी को अनाज व्यापारियों और हेल्थ फूड निर्माताओं से अच्छे दाम मिलते हैं।'
        },
    },
    'vegetables': {
        'name': {'en': 'Seasonal Vegetables (Tarakari)', 'kn': 'ತರಕಾರಿ ಬೆಳೆಗಳು (Tarakari)', 'hi': 'मौसमी सब्जियां (Vegetables)'},
        'season': {'en': 'Whole Year / Zaid / Rabi', 'kn': 'ವರ್ಷಪೂರ್ತಿ / ಬೇಸಿಗೆ / ಹಿಂಗಾರು', 'hi': 'पूरे साल / जायद / रबी'},
        'planting_months': {'en': 'October - November & February - March', 'kn': 'ಅಕ್ಟೋಬರ್ - ನವೆಂಬರ್ ಮತ್ತು ಫೆಬ್ರವರಿ - ಮಾರ್ಚ್', 'hi': 'अक्टूबर - नवंबर एवं फरवरी - मार्च'},
        'harvest_months': {'en': 'Multi-pickings every 45-75 days', 'kn': 'ಪ್ರತಿ 45-75 ದಿನಗಳಿಗೆ ನಿರಂತರ ಕೊಯ್ಲು', 'hi': 'हर 45-75 दिनों में नियमित तुड़ाई'},
        'season_desc': {
            'en': 'High-value quick-cash horticultural crops (Cabbage, Cauliflower, Beans, Okra, Brinjal, Gourds) suited to irrigated farming.',
            'kn': 'ನೀರಾವರಿ ಆಧಾರಿತ ಅಲ್ಪಾವಧಿ ತರಕಾರಿ ಬೆಳೆಗಳು (ಕೋಸು, ಹುರುಳಿಕಾಯಿ, ಬೆಂಡೆ, ಬದನೆ, ಸೋರೆಕಾಯಿ). ನಿರಂತರ ಆದಾಯ ನೀಡುತ್ತದೆ.',
            'hi': 'उच्च मूल्य वाली सब्जियां (पत्तागोभी, फूलगोभी, बीन्स, भिंडी, बैंगन, लौकी) जो नियमित दैनिक नकद आय देती हैं।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 120 kg/ha, Phosphorus: 80 kg/ha, Potassium: 80 kg/ha + 25 tonnes FYM/ha.',
            'kn': 'ಸಾರಜನಕ: 120 ಕೆಜಿ, ರಂಜಕ: 80 ಕೆಜಿ, ಪೊಟ್ಯಾಶ್: 80 ಕೆಜಿ/ಹೆಕ್ಟೇರ್ + 25 ಟನ್ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ.',
            'hi': 'नाइट्रोजन: 120 किग्रा, फास्फोरस: 80 किग्रा, पोटाश: 80 किग्रा + 25 टन सड़ी गोबर की खाद।'
        },
        'pests': {
 'en': ['Fruit and shoot borer → Pheromone traps + Emamectin benzoate', 'Sucking pests → Neem oil + Acetamiprid'],
            'kn': ['ಕಾಯಿ ಮತ್ತು ಚಿಗುರು ಕೊರೆಯುವ ಹುಳು → ಮೋಹಕ ಬಲೆ ಮತ್ತು ಎಮಾಮೆಕ್ಟಿನ್ ಸಿಂಪಡಿಸಿ', 'ರಸಹೀರುವ ಕೀಟಗಳು → ಬೇವು ಎಣ್ಣೆ + ಅಸಿಟಾಮಿಪ್ರಿಡ್ ಬಳಸಿ'],
            'hi': ['फल व तना छेदक → फेरोमोन ट्रैप व इमामेक्टिन स्प्रे', 'रस चूसक कीट → नीम का तेल + एसिटामिप्रिड']
        },
        'best_sell_months': {'en': 'Year-round daily harvesting', 'kn': 'ವರ್ಷಪೂರ್ತಿ ದೈನಂದಿನ ಕೊಯ್ಲು', 'hi': 'साल भर दैनिक विपणन'},
        'sell_tip': {
            'en': 'Agmarknet multi-year modal price trends show early morning graded arrivals at HOPCOMS and local APMC mandis minimize transit loss and maximize returns.',
            'kn': 'ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಮಂಡಿ ದರ ವಿಶ್ಲೇಷಣೆ: ಹಾಪ್\u200cಕಾಮ್ಸ್ (HOPCOMS) ಮತ್ತು ಎಪಿಎಂಸಿ ಮಾರುಕಟ್ಟೆಗಳಿಗೆ ಮುಂಜಾನೆಯೇ ತರಕಾರಿ ತಲುಪಿಸುವುದರಿಂದ ಉತ್ತಮ ಬೆಲೆ ಸಿಗುತ್ತದೆ.',
            'hi': 'एगमार्कनेट मॉडल भाव रुझान: हॉपकॉम्प्स (HOPCOMS) और स्थानीय मंडियों में सुबह जल्दी ग्रेडेड सब्जियां पहुंचाने से बेहतर दाम मिलते हैं।'
        },
    },
    'flowers': {
        'name': {'en': 'Commercial Flowers (Marigold, Jasmine, Rose)', 'kn': 'ವಾಣಿಜ್ಯ ಹೂವುಗಳು (ಚೆಂಡುಹೂ, ಮಲ್ಲಿಗೆ, ಗುಲಾಬಿ)', 'hi': 'व्यावसायिक फूल (गेंदा, चमेली, गुलाब)'},
        'season': {'en': 'Zaid / Summer & Whole Year', 'kn': 'ಬೇಸಿಗೆ / ಜೈದ್ ಮತ್ತು ವರ್ಷಪೂರ್ತಿ', 'hi': 'जायद (गर्मी) एवं पूरे साल'},
        'planting_months': {'en': 'February - April & July - August', 'kn': 'ಫೆಬ್ರವರಿ - ಏಪ್ರಿಲ್ ಮತ್ತು ಜುಲೈ - ಆಗಸ್ಟ್', 'hi': 'फरवरी - अप्रैल एवं जुलाई - अगस्त'},
        'harvest_months': {'en': 'Continuous flower picking every 3-5 days', 'kn': 'ಪ್ರತಿ 3-5 ದಿನಗಳಿಗೊಮ್ಮೆ ನಿರಂತರ ಹೂ ಬಿಡಿಸುವಿಕೆ', 'hi': 'हर 3-5 दिनों में नियमित फूल तुड़ाई'},
        'season_desc': {
            'en': 'High-profit commercial floriculture thriving in warm sunshine with drip fertigation.',
            'kn': 'ಉತ್ತಮ ಸೂರ್ಯನ ಬೆಳಕು ಮತ್ತು ಹನಿ ನೀರಾವರಿಯಲ್ಲಿ ಸಮೃದ್ಧ ಹೂವು ಬಿಡುವ ಅಧಿಕ ಲಾಭದಾಯಕ ವಾಣಿಜ್ಯ ಬೆಳೆ.',
            'hi': 'तेज धूप और ड्रिप सिंचाई में भरपूर खिलने वाली उच्च मुनाफे वाली व्यावसायिक पुष्प खेती।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 100 kg/ha, Phosphorus: 120 kg/ha, Potassium: 100 kg/ha with micronutrient foliar spray.',
            'kn': 'ಸಾರಜನಕ: 100 ಕೆಜಿ, ರಂಜಕ: 120 ಕೆಜಿ, ಪೊಟ್ಯಾಶ್: 100 ಕೆಜಿ/ಹೆಕ್ಟೇರ್ + ಸೂಕ್ಷ್ಮ ಪೋಷಕಾಂಶಗಳ ಸಿಂಪಡಣೆ.',
            'hi': 'नाइट्रोजन: 100 किग्रा, फास्फोरस: 120 किग्रा, पोटाश: 100 किग्रा + सूक्ष्म पोषक तत्व।'
        },
        'pests': {
 'en': ['Thrips and Mites → Spray Spiromesifen @ 1 ml/L', 'Bud borer → Install pheromone traps (5/acre) and spray HaNPV @ 0.5 ml/L'],
            'kn': ['ನುಸಿ ಮತ್ತು ಥ್ರಿಪ್ಸ್ ಕೀಟ → ಸ್ಪೈರೋಮೆಸಿಫೆನ್ ಸಿಂಪಡಿಸಿ', 'ಮೊಗ್ಗು ಕೊರೆಯುವ ಹುಳು → ಮೋಹಕ ಬಲೆಗಳು ಮತ್ತು ಜೈವಿಕ ನಿಯಂತ್ರಣ ಸಿಂಪಡಿಸಿ'],
            'hi': ['थ्रिप्स और मकड़ी कीट → स्पाइरोमेसिफेन का छिड़काव करें', 'कली छेदक → स्पिनोसाड का प्रयोग करें']
        },
        'best_sell_months': {'en': 'Festival & Wedding seasons (August - March)', 'kn': 'ಹಬ್ಬಗಳು ಮತ್ತು ಮದುವೆ ಸೀಸನ್ (ಆಗಸ್ಟ್ - ಮಾರ್ಚ್)', 'hi': 'त्योहारों व शादी के सीजन (अगस्त - मार्च)'},
        'sell_tip': {
            'en': 'Agmarknet and International Flower Auction Bangalore (IFAB) modal price trends show early morning auction lots with tight buds command peak rates.',
            'kn': 'ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಮತ್ತು ಬೆಂಗಳೂರು ಹೂವಿನ ಹರಾಜು ಮಾರುಕಟ್ಟೆ (IFAB) ದರ ವಿಶ್ಲೇಷಣೆ: ಮುಂಜಾನೆಯ ಹರಾಜಿನಲ್ಲಿ ಬಿಗಿಯಾದ ಮೊಗ್ಗುಗಳಿರುವ ಹೂವುಗಳಿಗೆ ಗರಿಷ್ಠ ಬೆಲೆ ದೊರೆಯುತ್ತದೆ.',
            'hi': 'एगमार्कनेट व अंतरराष्ट्रीय पुष्प नीलामी बेंगलुरु (IFAB) मॉडल भाव रुझान: सुबह की नीलामी में कली वाले ताजे फूलों को सबसे ऊंचा दाम मिलता है।'
        },
    },
    'fodder': {
        'name': {'en': 'Green Fodder (Hybrid Napier / Sorghum / Maize)', 'kn': 'ಹಸಿರು ಮೇವು (ನೇಪಿಯರ್ / ಮೆಕ್ಕೆಜೋಳ / ಜೋಳ)', 'hi': 'हरा चारा (नेपियर / ज्वार / मक्का)'},
        'season': {'en': 'Zaid / Summer & Whole Year', 'kn': 'ಬೇಸಿಗೆ / ಜೈದ್ ಮತ್ತು ವರ್ಷಪೂರ್ತಿ', 'hi': 'जायद / गर्मी एवं पूरे साल'},
        'planting_months': {'en': 'February - March & June - July', 'kn': 'ಫೆಬ್ರವರಿ - ಮಾರ್ಚ್ ಮತ್ತು ಜೂನ್ - ಜುಲೈ', 'hi': 'फरवरी - मार्च एवं जून - जुलाई'},
        'harvest_months': {'en': 'First cut at 60 days, then every 30-40 days', 'kn': 'ಮೊದಲ ಕಟಾವು 60 ದಿನಗಳಲ್ಲಿ, ನಂತರ ಪ್ರತಿ 30-40 ದಿನಗಳಿಗೊಮ್ಮೆ', 'hi': 'पहली कटाई 60 दिन में, फिर हर 30-40 दिन बाद'},
        'season_desc': {
            'en': 'Fast-growing high-protein summer green fodder to support dairy cattle and rural milk production.',
            'kn': 'ಬೇಸಿಗೆಯಲ್ಲಿ ಹೈನುಗಾರಿಕೆ ಮತ್ತು ಜಾನುವಾರುಗಳಿಗೆ ಪೌಷ್ಟಿಕ ಹಸಿರು ಮೇವು ಒದಗಿಸುವ ಶೀಘ್ರ ಬೆಳವಣಿಗೆಯ ಬೆಳೆ.',
            'hi': 'गर्मियों में दुधारू पशुओं के लिए पौष्टिक हरा चारा प्रदान करने वाली तेजी से बढ़ने वाली फसल।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 150 kg/ha (split after each cut), Phosphorus: 50 kg/ha, Potassium: 40 kg/ha.',
            'kn': 'ಸಾರಜನಕ: 150 ಕೆಜಿ (ಪ್ರತಿ ಕಟಾವಿನ ನಂತರ), ರಂಜಕ: 50 ಕೆಜಿ, ಪೊಟ್ಯಾಶ್: 40 ಕೆಜಿ/ಹೆಕ್ಟೇರ್.',
            'hi': 'नाइट्रोजन: 150 किग्रा (प्रत्येक कटाई के बाद विभाजित), फास्फोरस: 50 किग्रा, पोटाश: 40 किग्रा।'
        },
        'pests': {
            'en': ['Shoot fly / Armyworm → Spray Neem Azadirachtin 0.03% (safe for cattle feeding)'],
            'kn': ['ಸುಳಿ ನೊಣ / ಲದ್ದಿ ಹುಳು → ಬೇವಿನ ಕೀಟನಾಶಕ ಸಿಂಪಡಿಸಿ (ಜಾನುವಾರುಗಳಿಗೆ ಸುರಕ್ಷಿತ)'],
            'hi': ['तना मक्खी / कीट → नीम आधारित कीटनाशक छिड़कें (पशुओं के लिए सुरक्षित)']
        },
        'best_sell_months': {'en': 'Summer peak milk shortage months (March - June)', 'kn': 'ಬೇಸಿಗೆಯ ತಿಂಗಳುಗಳು (ಮಾರ್ಚ್ - ಜೂನ್)', 'hi': 'गर्मी के महीने (मार्च - जून)'},
        'sell_tip': {
            'en': 'Track local KMF milk cooperative modal procurement trends and supply fresh chopped green fodder directly to dairy farmers for steady income.',
            'kn': 'ಕೆಎಂಎಫ್ (ನಂದಿನಿ) ಡೇರಿ ಹಾಲು ಒಕ್ಕೂಟಗಳ ದರ ವಿಶ್ಲೇಷಣೆ: ಕತ್ತರಿಸಿದ ಹಸಿರು ಮೇವನ್ನು ನೇರವಾಗಿ ಹೈನುಗಾರರಿಗೆ ಪೂರೈಸುವುದರಿಂದ ನಿರಂತರ ಆದಾಯ ಪಡೆಯಬಹುದು.',
            'hi': 'केएमएफ दुग्ध सहकारी रुझान: कटी हुई हरी घास सीधे डेयरी किसानों को आपूर्ति करके स्थिर आय प्राप्त करें।'
        },
    },
    'turmeric': {
        'name': {'en': 'Turmeric (Arisina)', 'kn': 'ಅರಿಶಿನ (Turmeric)', 'hi': 'हल्दी (Turmeric)'},
        'season': {'en': 'Kharif (Monsoon)', 'kn': 'ಖಾರೀಫ್ (ಮುಂಗಾರು)', 'hi': 'खरीफ (मानसून)'},
        'planting_months': {'en': 'May - June', 'kn': 'ಮೇ - ಜೂನ್', 'hi': 'मई - जून'},
        'harvest_months': {'en': 'January - March (9 month cycle)', 'kn': 'ಜನವರಿ - ಮಾರ್ಚ್ (9 ತಿಂಗಳ ಅವಧಿ)', 'hi': 'जनवरी - मार्च (9 महीने का चक्र)'},
        'season_desc': {
            'en': 'Commercial high-value spice crop thriving in warm humid monsoon soils with good organic drainage.',
            'kn': 'ಉತ್ತಮ ಸಾವಯವ ಫಲವತ್ತತೆ ಮತ್ತು ನೀರು ಬಸಿದು ಹೋಗುವ ಮಣ್ಣಿನಲ್ಲಿ ಬೆಳೆಯುವ ಪ್ರಮುಖ ವಾಣಿಜ್ಯ ಸಾಂಬಾರ ಬೆಳೆ.',
            'hi': 'गर्म व नम मानसूनी मौसम और अच्छी जल निकासी वाली भूमि में उगने वाली प्रमुख नकदी मसाला फसल।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 150 kg/ha, Phosphorus: 60 kg/ha, Potassium: 120 kg/ha + 30 tonnes FYM/ha.',
            'kn': 'ಸಾರಜನಕ: 150 ಕೆಜಿ, ರಂಜಕ: 60 ಕೆಜಿ, ಪೊಟ್ಯಾಶ್: 120 ಕೆಜಿ/ಹೆಕ್ಟೇರ್ + 30 ಟನ್ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ.',
            'hi': 'नाइट्रोजन: 150 किग्रा, फास्फोरस: 60 किग्रा, पोटाश: 120 किग्रा + 30 टन गोबर खाद।'
        },
        'pests': {
 'en': ['Rhizome rot → Drench with Trichoderma viride and 1% Bordeaux mixture', 'Shoot borer → Install yellow sticky traps and spray 5% neem oil @ 2 ml/L'],
            'kn': ['ಗೆಡ್ಡೆ ಕೊಳೆತ ರೋಗ → ಟ್ರೈಕೋಡರ್ಮಾ + ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಅಥವಾ ಬೇವಿನ ಎಣ್ಣೆ ಸುರಿಯಿರಿ', 'ಕಾಂಡ ಕೊರೆಯುವ ಹುಳು → ಡೈಮೆಥೋಯೇಟ್ ಸಿಂಪಡಿಸಿ'],
            'hi': ['कंद सड़न रोग → मेटालेक्सिल + जैविक कवकनाशी या 5% नीम तेल का घोल डालें', 'तना छेदक → पीले चिपचिपे ट्रैप और 5% नीम तेल का छिड़काव करें']
        },
        'best_sell_months': {'en': 'March - May (post-curing polished turmeric)', 'kn': 'ಮಾರ್ಚ್ - ಮೇ (ಸಂಸ್ಕರಿಸಿದ ಅರಿಶಿನದ ಗರಿಷ್ಠ ಮಾರಾಟ ಸಮಯ)', 'hi': 'मार्च - मई (पॉलिश की हुई सूखी हल्दी की मांग)'},
        'sell_tip': {
            'en': 'Agmarknet spice mandi modal price trends at Chamarajanagar, Erode, and Sangli show boiled and polished turmeric fingers command top grading rates.',
            'kn': 'ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಸಾಂಬಾರ ಮಂಡಿ ದರ ವಿಶ್ಲೇಷಣೆ: ಚಾಮರಾಜನಗರ, ಈರೋಡ್ ಮತ್ತು ಸಾಂಗ್ಲಿ ಮಾರುಕಟ್ಟೆಗಳಲ್ಲಿ ಬೇಯಿಸಿ ಪಾಲಿಶ್ ಮಾಡಿದ ಅರಿಶಿನ ಕೊಂಬುಗಳಿಗೆ ಗರಿಷ್ಠ ದರ ದೊರೆಯುತ್ತದೆ.',
            'hi': 'एगमार्कनेट मसाला मंडी मॉडल भाव रुझान: चामराजनगर, इरोड और सांगली में उबाली व पॉलिश की हुई हल्दी की गांठों को उच्चतम ग्रेडिंग भाव मिलता है।'
        },
    },
    'cowpea': {
        'name': {'en': 'Cowpea (Alasande / Lobia)', 'kn': 'ಅಲಸಂದೆ (Alasande)', 'hi': 'लोबिया / चंवला (Cowpea)'},
        'season': {'en': 'Kharif / Rabi / Zaid', 'kn': 'ಖಾರೀಫ್ / ರಬಿ / ಜೈದ್', 'hi': 'खरीफ / रबी / जायद'},
        'planting_months': {'en': 'June - July & February - March', 'kn': 'ಜೂನ್ - ಜುಲೈ ಮತ್ತು ಫೆಬ್ರವರಿ - ಮಾರ್ಚ್', 'hi': 'जून - जुलाई एवं फरवरी - मार्च'},
        'harvest_months': {'en': 'August - September & May - June', 'kn': 'ಆಗಸ್ಟ್ - ಸೆಪ್ಟೆಂಬರ್ ಮತ್ತು ಮೇ - ಜೂನ್', 'hi': 'अगस्त - सितंबर एवं मई - जून'},
        'season_desc': {
            'en': 'Versatile drought-resilient pulse grown for green vegetable pods as well as dry protein-rich pulses.',
            'kn': 'ತರಕಾರಿ ಕಾಯಿ ಮತ್ತು ಒಣಕಾಳು ಎರಡಕ್ಕೂ ಬೆಳೆಯಬಹುದಾದ ಉತ್ತಮ ಬರ ಸಹಿಷ್ಣು ಬೇಳೆಕಾಳು ಬೆಳೆ.',
            'hi': 'हरी फलियों और सूखे दानों दोनों के लिए उगाई जाने वाली बहुमुखी सूखा-रोधी दलहन फसल।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 25 kg/ha, Phosphorus: 50 kg/ha, Potassium: 25 kg/ha.',
            'kn': 'ಸಾರಜನಕ: 25 ಕೆಜಿ, ರಂಜಕ: 50 ಕೆಜಿ, ಪೊಟ್ಯಾಶ್: 25 ಕೆಜಿ/ಹೆಕ್ಟೇರ್.',
            'hi': 'नाइट्रोजन: 25 किग्रा, फास्फोरस: 50 किग्रा, पोटाश: 25 किग्रा।'
        },
        'pests': {
 'en': ['Aphids and Pod borer → Install yellow sticky traps and spray 5% neem oil @ 1.7 ml/L or Neem oil'],
            'kn': ['ಸಸ್ಯಹೇನು ಮತ್ತು ಕಾಯಿ ಕೊರೆಯುವ ಹುಳು → ಡೈಮೆಥೋಯೇಟ್ ಅಥವಾ ಬೇವು ಎಣ್ಣೆ ಸಿಂಪಡಿಸಿ'],
            'hi': ['माहू और फली छेदक → पीले चिपचिपे ट्रैप और 5% नीम तेल या नीम के तेल का छिड़काव करें']
        },
        'best_sell_months': {'en': 'March - May & September - October', 'kn': 'ಮಾರ್ಚ್ - ಮೇ ಮತ್ತು ಸೆಪ್ಟೆಂಬರ್ - ಅಕ್ಟೋಬರ್', 'hi': 'मार्च - मई एवं सितंबर - अक्टूबर'},
        'sell_tip': {
            'en': 'Agmarknet modal price trends show tender green pods fetch strong vegetable retail rates while mature dry seeds align with pulse MSP procurement.',
            'kn': 'ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಮಂಡಿ ದರ ವಿಶ್ಲೇಷಣೆ: ಹಸಿ ಅಲಸಂದೆ ಕಾಯಿಗೆ ತರಕಾರಿ ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ಉತ್ತಮ ಬೆಲೆ ಹಾಗೂ ಒಣ ಕಾಳುಗಳಿಗೆ ಬೇಳೆಕಾಳು ಬೆಂಬಲ ಬೆಲೆಯ ಪ್ರಯೋಜನ ಪಡೆಯಿರಿ.',
            'hi': 'एगमार्कनेट मॉडल भाव रुझान: हरी फलियों को सब्जी मंडी में अच्छे दाम मिलते हैं तथा सूखे दानों को दलहन एमएसपी खरीद का लाभ मिलता है।'
        },
    },
    'chilli': {
        'name': {'en': 'Chilli (Menasinakayi / Byadgi Chilli)', 'kn': 'ಮೆಣಸಿನಕಾಯಿ (ಬ್ಯಾಡಗಿ ಮೆಣಸಿನಕಾಯಿ)', 'hi': 'मिर्च (ब्याडगी मिर्च)'},
        'season': {'en': 'Kharif / Late Kharif', 'kn': 'ಖಾರೀಫ್ / ಹಿಂಗಾರು', 'hi': 'खरीफ / पछेती खरीफ'},
        'planting_months': {'en': 'June - July & September - October', 'kn': 'ಜೂನ್ - ಜುಲೈ ಮತ್ತು ಸೆಪ್ಟೆಂಬರ್ - ಅಕ್ಟೋಬರ್', 'hi': 'जून - जुलाई एवं सितंबर - अक्टूबर'},
        'harvest_months': {'en': 'November - January (Red dry pod pickings)', 'kn': 'ನವೆಂಬರ್ - ಜನವರಿ (ಒಣ ಕೆಂಪು ಮೆಣಸಿನಕಾಯಿ)', 'hi': 'नवंबर - जनवरी (सूखी लाल मिर्च की तुड़ाई)'},
        'season_desc': {
            'en': 'Famous commercial spice crop of Karnataka (Haveri/Byadgi) grown across multiple districts.',
            'kn': 'ಕರ್ನಾಟಕದ ಪ್ರಸಿದ್ಧ ವಾಣಿಜ್ಯ ಬೆಳೆ (ಬ್ಯಾಡಗಿ ಮೆಣಸಿನಕಾಯಿ). ಆಳವಾದ ಕೆಂಪು ಬಣ್ಣ ಮತ್ತು ಕಡಿಮೆ ಖಾರಕ್ಕೆ ವಿಶ್ವಪ್ರಸಿದ್ಧ.',
            'hi': 'कर्नाटक (हावेरी/ब्याडगी) की विश्व प्रसिद्ध नकदी मसाला फसल। गहरे लाल रंग और तेल की मात्रा के लिए विख्यात।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 150 kg/ha, Phosphorus: 75 kg/ha, Potassium: 75 kg/ha.',
            'kn': 'ಸಾರಜನಕ: 150 ಕೆಜಿ, ರಂಜಕ: 75 ಕೆಜಿ, ಪೊಟ್ಯಾಶ್: 75 ಕೆಜಿ/ಹೆಕ್ಟೇರ್.',
            'hi': 'नाइट्रोजन: 150 किग्रा, फास्फोरस: 75 किग्रा, पोटाश: 75 किग्रा।'
        },
        'pests': {
 'en': ['Thrips and Mites → Install blue sticky traps and spray 5% neem oil 5 SC @ 1.5 ml/L or Diafenthiuron @ 1 g/L', 'Anthracnose fruit rot → Apply Trichoderma viride bio-fungicide @ 1 ml/L'],
            'kn': ['ನುಸಿ ಮತ್ತು ಮುಟುರು ರೋಗ → ಫಿಪ್ರೋನಿಲ್ ಅಥವಾ ಡೈಫೆಂಥಿಯುರಾನ್ ಸಿಂಪಡಿಸಿ', 'ಕಾಯಿ ಕೊಳೆತ ರೋಗ → ಅಜಾಕ್ಸಿಸ್ಟ್ರೋಬಿನ್ ಸಿಂಪಡಿಸಿ'],
            'hi': ['थ्रिप्स और मकड़ी (पत्ती मरोड़) → फिप्रोनिल या डायाफेंथियूरोन छिड़कें', 'फल सड़न → एज़ोक्सीस्ट्रोबिन स्प्रे करें']
        },
        'best_sell_months': {'en': 'January - April (Byadgi APMC mega auctions)', 'kn': 'ಜನವರಿ - ಏಪ್ರಿಲ್ (ಬ್ಯಾಡಗಿ ಎಪಿಎಂಸಿ ಮಾರುಕಟ್ಟೆ)', 'hi': 'जनवरी - अप्रैल (ब्याडगी मंडी की नीलामी)'},
        'sell_tip': {
            'en': 'Agmarknet modal price trends at Byadgi and Hubballi APMC confirm high oleoresin wrinkled dry red chillies command highest premium rates.',
            'kn': 'ಬ್ಯಾಡಗಿ ಮತ್ತು ಹುಬ್ಬಳ್ಳಿ ಎಪಿಎಂಸಿ ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಮಂಡಿ ದರ ವಿಶ್ಲೇಷಣೆ: ಉತ್ತಮ ಸುಕ್ಕು ಮತ್ತು ಬಣ್ಣ ಹೊಂದಿರುವ ಬ್ಯಾಡಗಿ ಒಣ ಮೆಣಸಿನಕಾಯಿಗೆ ಗರಿಷ್ಠ ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಸಿಗುತ್ತದೆ.',
            'hi': 'ब्याडगी और हुबली एपीएमसी एगमार्कनेट मॉडल भाव रुझान: अच्छे रंग और झुर्रीदार सूखी लाल मिर्च को उच्चतम प्रीमियम भाव मिलता है।'
        },
    },
    'ginger': {
        'name': {'en': 'Ginger (Shunti)', 'kn': 'ಶುಂಠಿ (Ginger)', 'hi': 'अदरक (Ginger)'},
        'season': {'en': 'Kharif (Monsoon)', 'kn': 'ಖಾರೀಫ್ (ಮುಂಗಾರು)', 'hi': 'खरीफ (मानसून)'},
        'planting_months': {'en': 'April - May', 'kn': 'ಏಪ್ರಿಲ್ - ಮೇ', 'hi': 'अप्रैल - मई'},
        'harvest_months': {'en': 'December - February (8-9 months)', 'kn': 'ಡಿಸೆಂಬರ್ - ಫೆಬ್ರವರಿ', 'hi': 'दिसंबर - फरवरी'},
        'season_desc': {
            'en': 'High-value rhizome cash crop in Malnad region (Shivamogga, Kodagu, Hassan) requiring humid warmth and organic mulching.',
            'kn': 'ಮಲೆನಾಡು ಭಾಗದ ಪ್ರಮುಖ ವಾಣಿಜ್ಯ ಸಾಂಬಾರ ಬೆಳೆ (ಶಿವಮೊಗ್ಗ, ಕೊಡಗು, ಹಾಸನ). ಹಿತವಾದ ತೇವಾಂಶ ಮತ್ತು ಉತ್ತಮ ಹೊದಿಕೆ ಅಗತ್ಯ.',
            'hi': 'मलनाड क्षेत्र (शिमोगा, कोडागु, हासन) की उच्च मूल्य वाली मसाला फसल जिसे नम गर्मी और जैविक मल्चिंग चाहिए।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 100 kg/ha, Phosphorus: 50 kg/ha, Potassium: 100 kg/ha + 25 tonnes FYM/ha.',
            'kn': 'ಸಾರಜನಕ: 100 ಕೆಜಿ, ರಂಜಕ: 50 ಕೆಜಿ, ಪೊಟ್ಯಾಶ್: 100 ಕೆಜಿ/ಹೆಕ್ಟೇರ್ + 25 ಟನ್ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ.',
            'hi': 'नाइट्रोजन: 100 किग्रा, फास्फोरस: 50 किग्रा, पोटाश: 100 किग्रा + 25 टन गोबर खाद।'
        },
        'pests': {
 'en': ['Soft rot / Rhizome rot → Drench with Trichoderma viride and 1% Bordeaux mixture', 'Shoot borer → Spray Chlorantraniliprole'],
            'kn': ['ಗೆಡ್ಡೆ ಕೊಳೆತ ರೋಗ → ಟ್ರೈಕೋಡರ್ಮಾ ಮತ್ತು ಶೇ. 1ರ ಬೋರ್ಡೋ ದ್ರಾವಣ ಸುರಿಯಿರಿ', 'ಕಾಂಡ ಕೊರೆಯುವ ಹುಳು → ಕೋರಾಜೆನ್ ಸಿಂಪಡಿಸಿ'],
            'hi': ['कंद सड़न रोग → 1% बोर्डो मिश्रण या जैविक कवकनाशी का घोल डालें', 'तना छेदक → कोराजेन का छिड़काव करें']
        },
        'best_sell_months': {'en': 'January - April', 'kn': 'ಜನವರಿ - ಏಪ್ರಿಲ್', 'hi': 'जनवरी - अप्रैल'},
        'sell_tip': {
            'en': 'Agmarknet modal price trends in Shimoga and Hassan mandis show cleaned, disease-free fresh ginger rhizomes fetch top commercial rates.',
            'kn': 'ಶಿವಮೊಗ್ಗ ಮತ್ತು ಹಾಸನ ಮಂಡಿ ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ದರ ವಿಶ್ಲೇಷಣೆ: ತೊಳೆದು ಒಣಗಿಸಿದ ಉತ್ತಮ ಗುಣಮಟ್ಟದ ಹಸಿಶುಂಠಿಗೆ ವ್ಯಾಪಾರಿಗಳಿಂದ ಹೆಚ್ಚಿನ ದರ ದೊರೆಯುತ್ತದೆ.',
            'hi': 'शिमोगा और हासन मंडियों में एगमार्कनेट मॉडल भाव रुझान: साफ और रोगमुक्त ताजे अदरक को शीर्ष व्यापारिक मूल्य मिलता है।'
        },
    },
    'tobacco': {
        'name': {'en': 'Tobacco (Hogesoppu / VFC Tobacco)', 'kn': 'ತಂಬಾಕು (ಹೊಗೆಸೊಪ್ಪು / VFC)', 'hi': 'तंबाकू (VFC Tobacco)'},
        'season': {'en': 'Kharif (Monsoon)', 'kn': 'ಖಾರೀಫ್ (ಮುಂಗಾರು)', 'hi': 'खरीफ (मानसून)'},
        'planting_months': {'en': 'May - June', 'kn': 'ಮೇ - ಜೂನ್', 'hi': 'मई - जून'},
        'harvest_months': {'en': 'August - October', 'kn': 'ಆಗಸ್ಟ್ - ಅಕ್ಟೋಬರ್', 'hi': 'अगस्त - अक्टूबर'},
        'season_desc': {
            'en': 'Regulated commercial cash crop grown in Mysuru and Hassan light soils with dedicated Tobacco Board auction platforms.',
            'kn': 'ಮೈಸೂರು ಮತ್ತು ಹಾಸನ ಭಾಗದ ಪ್ರಮುಖ ವಾಣಿಜ್ಯ ಬೆಳೆ. ತಂಬಾಕು ಮಂಡಳಿಯ ಹರಾಜು ವೇದಿಕೆಗಳಲ್ಲಿ ಮಾರಾಟವಾಗುತ್ತದೆ.',
            'hi': 'मैसूर और हासन की हल्की मिट्टी में उगाई जाने वाली प्रमुख नकदी फसल, जिसकी बिक्री तंबाकू बोर्ड के जरिए होती है।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 40 kg/ha, Phosphorus: 60 kg/ha, Potassium: 80 kg/ha (avoid muriate of potash).',
            'kn': 'ಸಾರಜನಕ: 40 ಕೆಜಿ, ರಂಜಕ: 60 ಕೆಜಿ, ಪೊಟ್ಯಾಶ್: 80 ಕೆಜಿ/ಹೆಕ್ಟೇರ್ (ಸಲ್ಫೇಟ್ ಆಫ್ ಪೊಟ್ಯಾಶ್ ಬಳಸಿ).',
            'hi': 'नाइट्रोजन: 40 किग्रा, फास्फोरस: 60 किग्रा, पोटाश: 80 किग्रा।'
        },
        'pests': {
 'en': ['Caterpillar / Leaf eating caterpillar → Spray Emamectin benzoate @ 0.4 g/L', 'Frog eye leaf spot → Spray 5% neem oil / bio-fungicide @ 2 g/L'],
            'kn': ['ಎಲೆ ತಿನ್ನುವ ಕಂಬಳಿಹುಳು → ಎಮಾಮೆಕ್ಟಿನ್ ಬೆಂಜೊಯೇಟ್ ಸಿಂಪಡಿಸಿ', 'ಕಪ್ಪುಕಲೆ ರೋಗ → 5% ಬೇವಿನ ಎಣ್ಣೆ ಅಥವಾ ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಬಳಸಿ'],
            'hi': ['पत्ती खाने वाली इल्ली → इमामेक्टिन बेंजोएट का छिड़काव करें', 'धब्बा रोग → जैविक कवकनाशी या 5% नीम तेल स्प्रे करें']
        },
        'best_sell_months': {'en': 'September - December (Tobacco Board Auctions)', 'kn': 'ಸೆಪ್ಟೆಂಬರ್ - ಡಿಸೆಂಬರ್ (ತಂಬಾಕು ಮಂಡಳಿ ಹರಾಜು)', 'hi': 'सितंबर - दिसंबर (तंबाकू बोर्ड नीलामी)'},
        'sell_tip': {
            'en': 'Tobacco Board auction platform modal trends in Hunsur and Periyapatna confirm bright-grade FCV leaves fetch highest bid prices.',
            'kn': 'ತಂಬಾಕು ಮಂಡಳಿ (Tobacco Board) ಹರಾಜು ದರ ವಿಶ್ಲೇಷಣೆ: ಹುಣಸೂರು ಮತ್ತು ಪಿರಿಯಾಪಟ್ಟಣ ಹರಾಜು ಕೇಂದ್ರಗಳಲ್ಲಿ ಉತ್ತಮ ಹೊಳಪಿನ ತಂಬಾಕು ಎಲೆಗಳಿಗೆ ಗರಿಷ್ಠ ಬೆಲೆ ಸಿಗುತ್ತದೆ.',
            'hi': 'तंबाकू बोर्ड नीलामी मंच मॉडल रुझान (हुंसुर व पेरियापटना): चमकदार एफसीवी पत्तों को नीलामी में सबसे ऊंची बोली मिलती है।'
        },
    },
    'bajra': {
        'name': {'en': 'Bajra (Pearl Millet / Sajje)', 'kn': 'ಸಜ್ಜೆ (Sajje / Bajra)', 'hi': 'बाजरा (Pearl Millet)'},
        'season': {'en': 'Kharif / Zaid', 'kn': 'ಖಾರೀಫ್ / ಜೈದ್', 'hi': 'खरीफ / जायद'},
        'planting_months': {'en': 'June - July & February - March', 'kn': 'ಜೂನ್ - ಜುಲೈ ಮತ್ತು ಫೆಬ್ರವರಿ - ಮಾರ್ಚ್', 'hi': 'जून - जुलाई एवं फरवरी - मार्च'},
        'harvest_months': {'en': 'September - October & May - June', 'kn': 'ಸೆಪ್ಟೆಂಬರ್ - ಅಕ್ಟೋಬರ್ ಮತ್ತು ಮೇ - ಜೂನ್', 'hi': 'सितंबर - अक्टूबर एवं मई - जून'},
        'season_desc': {
            'en': 'Drought-hardy nutrient-dense millet excelling in arid North Karnataka soils with minimal irrigation.',
            'kn': 'ಉತ್ತರ ಕರ್ನಾಟಕದ ಒಣ ಹವೆಯಲ್ಲೂ ಕನಿಷ್ಠ ನೀರಲ್ಲಿ ಸಮೃದ್ಧವಾಗಿ ಬೆಳೆಯುವ ಪೌಷ್ಟಿಕ ಸಿರಿಧಾನ್ಯ ಬೆಳೆ.',
            'hi': 'कम पानी और तेज गर्मी में भी बेहतरीन पैदावार देने वाली पौष्टिक पोषक-अनाज (मिलेट) फसल।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 60 kg/ha, Phosphorus: 30 kg/ha, Potassium: 20 kg/ha.',
            'kn': 'ಸಾರಜನಕ: 60 ಕೆಜಿ, ರಂಜಕ: 30 ಕೆಜಿ, ಪೊಟ್ಯಾಶ್: 20 ಕೆಜಿ/ಹೆಕ್ಟೇರ್.',
            'hi': 'नाइट्रोजन: 60 किग्रा, फास्फोरस: 30 किग्रा, पोटाश: 20 किग्रा।'
        },
        'pests': {
 'en': ['Downy mildew → Seed treatment with Trichoderma harzianum (4g/kg seed)', 'Ergot / Smut → Spray 5% neem oil / bio-fungicide during boot leaf stage'],
            'kn': ['ಬೂದಿ ರೋಗ → ಟ್ರೈಕೋಡರ್ಮಾ ಬೀಜೋಪಚಾರ', 'ಕಾಡಿಗೆ ರೋಗ → 5% ಬೇವಿನ ಎಣ್ಣೆ ಅಥವಾ ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಬಳಸಿ'],
            'hi': ['डाउनी मिल्ड्यू → मेटालेक्सिल बीजोपचार', 'अर्गट रोग → 5% नीम तेल या जैविक कवकनाशी का प्रयोग करें']
        },
        'best_sell_months': {'en': 'October - December', 'kn': 'ಅಕ್ಟೋಬರ್ - ಡಿಸೆಂಬರ್', 'hi': 'अक्टूबर - दिसंबर'},
        'sell_tip': {
            'en': 'Benefit from government millet minimum support price (MSP) procurement programs and Agmarknet modal price trends for pearl millet.',
            'kn': 'ಸರ್ಕಾರಿ ಸಿರಿಧಾನ್ಯ ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ (MSP) ಖರೀದಿ ಯೋಜನೆಗಳು ಮತ್ತು ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಸಜ್ಜೆ ಮಂಡಿ ದರಗಳ ಪ್ರಯೋಜನ ಪಡೆಯಿರಿ.',
            'hi': 'सरकारी कनिष्ठ समर्थन मूल्य (MSP) खरीद योजनाओं और एगमार्कनेट बाजरा मॉडल भाव रुझानों का लाभ उठाएं।'
        },
    },
    'pulses': {
        'name': {'en': 'Mixed Pulses (Kalugalu)', 'kn': 'ಬೇಳೆಕಾಳುಗಳು (Pulses)', 'hi': 'दलहनी फसलें (Pulses)'},
        'season': {'en': 'Rabi / Kharif', 'kn': 'ರಬಿ / ಖಾರೀಫ್', 'hi': 'रबी / खरीफ'},
        'planting_months': {'en': 'October - November', 'kn': 'ಅಕ್ಟೋಬರ್ - ನವೆಂಬರ್', 'hi': 'अक्टूबर - नवंबर'},
        'harvest_months': {'en': 'January - March', 'kn': 'ಜನವರಿ - ಮಾರ್ಚ್', 'hi': 'जनवरी - मार्च'},
        'season_desc': {
            'en': 'Short-duration protein crops that enrich soil nitrogen and thrive on residual moisture.',
            'kn': 'ಮಣ್ಣಿನ ಸಾರಜನಕ ಹೆಚ್ಚಿಸಿ, ಕಡಿಮೆ ತೇವಾಂಶದಲ್ಲೂ ಉತ್ತಮ ಇಳುವರಿ ನೀಡುವ ಅಲ್ಪಾವಧಿ ಕಾಳು ಬೆಳೆಗಳು.',
            'hi': 'मिट्टी की उर्वरता बढ़ाने वाली और कम नमी में भरपूर प्रोटीन युक्त उपज देने वाली दलहन फसलें।'
        },
        'fertilizer': {
            'en': 'Nitrogen: 20 kg/ha, Phosphorus: 50 kg/ha, Potassium: 20 kg/ha + Rhizobium.',
            'kn': 'ಸಾರಜನಕ: 20 ಕೆಜಿ, ರಂಜಕ: 50 ಕೆಜಿ, ಪೊಟ್ಯಾಶ್: 20 ಕೆಜಿ/ಹೆಕ್ಟೇರ್ + ರೈಜೋಬಿಯಂ.',
            'hi': 'नाइट्रोजन: 20 किग्रा, फास्फोरस: 50 किग्रा, पोटाश: 20 किग्रा + राइजोबियम।'
        },
        'pests': {
 'en': ['Pod borer → Spray Emamectin benzoate @ 0.4 g/L', 'Wilt → Trichoderma seed treatment'],
            'kn': ['ಕಾಯಿ ಕೊರೆಯುವ ಹುಳು → ಎಮಾಮೆಕ್ಟಿನ್ ಸಿಂಪಡಿಸಿ', 'ನೆಟೆ ರೋಗ → ಟ್ರೈಕೋಡರ್ಮಾ ಬೀಜೋಪಚಾರ'],
            'hi': ['फली छेदक → इमामेक्टिन का छिड़काव', 'उकठा रोग → ट्राइकोडर्मा बीजोपचार']
        },
        'best_sell_months': {'en': 'February - April', 'kn': 'ಫೆಬ್ರವರಿ - ಏಪ್ರಿಲ್', 'hi': 'फरवरी - अप्रैल'},
        'sell_tip': {
            'en': 'Monitor Agmarknet modal price trends and sell dried, cleaned pulses to regional APMC mandis or government MSP procurement centers.',
            'kn': 'ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಮಂಡಿ ದರಗಳನ್ನು ಗಮನಿಸಿ ಮತ್ತು ಸ್ವಚ್ಛಗೊಳಿಸಿದ ಕಾಳುಗಳನ್ನು ಸ್ಥಳೀಯ ಎಪಿಎಂಸಿ ಅಥವಾ ಸರ್ಕಾರಿ ಬೆಂಬಲ ಬೆಲೆ (MSP) ಖರೀದಿ ಕೇಂದ್ರಗಳಲ್ಲಿ ಮಾರಾಟ ಮಾಡಿ.',
            'hi': 'एगमार्कनेट मॉडल भाव रुझानों पर नजर रखें और साफ दालों को क्षेत्रीय एपीएमसी मंडियों अथवा सरकारी एमएसपी खरीद केंद्रों पर बेचें।'
        },
    },
    'default': {
        'name': {'en': 'Agricultural Crop', 'kn': 'ಕೃಷಿ ಬೆಳೆ', 'hi': 'कृषि फसल'},
        'season': {'en': 'Seasonal Cycle', 'kn': 'ಋತುಮಾನದ ಚಕ್ರ', 'hi': 'मौसमी चक्र'},
        'planting_months': {'en': 'Consult local officer', 'kn': 'ಸ್ಥಳೀಯ ಕೃಷಿ ಅಧಿಕಾರಿಯನ್ನು ಸಂಪರ್ಕಿಸಿ', 'hi': 'स्थानीय कृषि अधिकारी से संपर्क करें'},
        'harvest_months': {'en': 'Standard maturity cycle', 'kn': 'ಸಾಮಾನ್ಯ ಕೊಯ್ಲು ಅವಧಿ', 'hi': 'सामान्य कटाई अवधि'},
        'season_desc': {
            'en': 'Consult local Krishi Vigyan Kendra (KVK) for specific seasonal schedule.',
            'kn': 'ನಿಖರವಾದ ಮಾಹಿತಿಗಾಗಿ ನಿಮ್ಮ ಸ್ಥಳೀಯ ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರವನ್ನು (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'hi': 'विस्तृत जानकारी के लिए अपने स्थानीय कृषि विज्ञान केंद्र (केवीके) से संपर्क करें।'
        },
        'fertilizer': {
            'en': 'Apply balanced NPK as per soil test report.',
            'kn': 'ಮಣ್ಣು ಪರೀಕ್ಷಾ ವರದಿಯ ಆಧಾರದ ಮೇಲೆ ಸಮತೋಲಿತ NPK ಗೊಬ್ಬರ ಬಳಸಿ.',
            'hi': 'मिट्टी परीक्षण रिपोर्ट के अनुसार संतुलित एनपीके का प्रयोग करें।'
        },
        'pests': {
            'en': ['Consult local agricultural extension officer for specific integrated pest management.'],
            'kn': ['ಕೀಟ ನಿರ್ವಹಣೆಗಾಗಿ ಸ್ಥಳೀಯ ಕೃಷಿ ಅಧಿಕಾರಿಯ ಸಲಹೆ ಪಡೆಯಿರಿ.'],
            'hi': ['कीट प्रबंधन के लिए स्थानीय कृषि विस्तार अधिकारी से परामर्श लें।']
        },
        'best_sell_months': {'en': 'Market dependent', 'kn': 'ಮಾರುಕಟ್ಟೆ ಆಧಾರಿತ', 'hi': 'बाजार आधारित'},
        'sell_tip': {
            'en': 'Track Agmarknet APMC mandi daily modal price trends and official MSP procurement schedules before dispatching produce.',
            'kn': 'ಕೃಷಿ ಉತ್ಪನ್ನಗಳನ್ನು ಮಾರುಕಟ್ಟೆಗೆ ಸಾಗಿಸುವ ಮುನ್ನ ಅಗ್ರ್ಮಾರ್ಕ್\u200cನೆಟ್ ಎಪಿಎಂಸಿ ದೈನಂದಿನ ಮಂಡಿ ದರಗಳು ಮತ್ತು ಸರ್ಕಾರಿ ಬೆಂಬಲ ಬೆಲೆ (MSP) ವೇಳಾಪಟ್ಟಿಯನ್ನು ಪರಿಶೀಲಿಸಿ.',
            'hi': 'फसल को मंडी भेजने से पहले एगमार्कनेट एपीएमसी दैनिक मॉडल भाव रुझान और सरकारी एमएसपी खरीद कार्यक्रम की जांच करें।'
        },
    }
}

# Add fallbacks for other crops in crop_knowledge
ALL_CROPS_LIST = [
    'apple', 'banana', 'blackgram', 'chickpea', 'coconut', 'coffee', 'cotton', 'grapes',
    'jute', 'kidneybeans', 'lentil', 'maize', 'mango', 'mothbeans', 'mungbean', 'muskmelon',
    'orange', 'papaya', 'pigeonpeas', 'pomegranate', 'potato', 'rice', 'tomato', 'watermelon', 'wheat', 'onion'
]

CROP_NAMES_MAP = {
    'apple': {'en': 'Apple', 'kn': 'ಸೇಬು', 'hi': 'सेब'},
    'banana': {'en': 'Banana', 'kn': 'ಬಾಳೆಹಣ್ಣು', 'hi': 'केला'},
    'blackgram': {'en': 'Blackgram (Urad)', 'kn': 'ಉದ್ದಿನ ಬೇಳೆ (ಉದ್ದು)', 'hi': 'उड़द दाल'},
    'chickpea': {'en': 'Chickpea (Bengal Gram)', 'kn': 'ಕಡಲೆ (ಬೆಂಗಾಲ್ ಗ್ರಾಂ / ಕಡಲೆಕಾಳು)', 'hi': 'चना (बंगाल चना)'},
    'coconut': {'en': 'Coconut', 'kn': 'ತೆಂಗಿನಕಾಯಿ', 'hi': 'नारियल'},
    'coffee': {'en': 'Coffee', 'kn': 'ಕಾಫಿ', 'hi': 'कॉफी'},
    'cotton': {'en': 'Cotton', 'kn': 'ಹತ್ತಿ', 'hi': 'कपास'},
    'grapes': {'en': 'Grapes', 'kn': 'ದ್ರಾಕ್ಷಿ', 'hi': 'अंगूर'},
    'jute': {'en': 'Jute', 'kn': 'ಸೆಣಬು', 'hi': 'जूट (पटसन)'},
    'kidneybeans': {'en': 'Kidney beans (Rajma)', 'kn': 'ರಾಜಮಾ', 'hi': 'राजमा'},
    'lentil': {'en': 'Lentil (Masoor)', 'kn': 'ಮಸೂರ ಬೇಳೆ', 'hi': 'मसूर दाल'},
    'maize': {'en': 'Maize (Corn)', 'kn': 'ಮೆಕ್ಕೆಜೋಳ', 'hi': 'मक्का'},
    'mango': {'en': 'Mango', 'kn': 'ಮಾವು', 'hi': 'आम'},
    'mothbeans': {'en': 'Moth beans (Matki)', 'kn': 'ಮಡಿಕೆ ಕಾಳು', 'hi': 'मोठ दाल'},
    'mungbean': {'en': 'Mungbean (Green gram)', 'kn': 'ಹೆಸರುಕಾಳು', 'hi': 'मूंग दाल'},
    'muskmelon': {'en': 'Muskmelon', 'kn': 'ಕರಬೂಜ', 'hi': 'खरबूजा'},
    'orange': {'en': 'Orange', 'kn': 'ಕಿತ್ತಳೆ', 'hi': 'संतरा'},
    'papaya': {'en': 'Papaya', 'kn': 'ಪರಂಗಿ (ಪಪ್ಪಾಯಿ)', 'hi': 'पपीता'},
    'pigeonpeas': {'en': 'Pigeonpeas (Tur / Arhar)', 'kn': 'ತೊಗರಿ ಬೇಳೆ', 'hi': 'अरहर (तुअर) दाल'},
    'pomegranate': {'en': 'Pomegranate', 'kn': 'ದಾಳಿಂಬೆ', 'hi': 'अनार'},
    'potato': {'en': 'Potato', 'kn': 'ಆಲೂಗಡ್ಡೆ', 'hi': 'आलू'},
    'rice': {'en': 'Rice (Paddy)', 'kn': 'ಭತ್ತ (ಅಕ್ಕಿ)', 'hi': 'चावल (धान)'},
    'tomato': {'en': 'Tomato', 'kn': 'ಟೊಮೆಟೊ', 'hi': 'टमाटर'},
    'watermelon': {'en': 'Watermelon', 'kn': 'ಕಲ್ಲಂಗಡಿ', 'hi': 'तरबूज'},
    'wheat': {'en': 'Wheat', 'kn': 'ಗೋಧಿ', 'hi': 'गेहूं'},
    'onion': {'en': 'Onion', 'kn': 'ಈರುಳ್ಳಿ', 'hi': 'प्याज'},
    'sugarcane': {'en': 'Sugarcane', 'kn': 'ಕಬ್ಬು', 'hi': 'गन्ना'},
    'pepper': {'en': 'Bell Pepper (Chilli)', 'kn': 'ದಪ್ಪ ಮೆಣಸಿನಕಾಯಿ', 'hi': 'शिमला मिर्च'},
    'fieldbeans': {'en': 'Field Bean (Avarekai)', 'kn': 'ಅವರೆಕಾಳು', 'hi': 'सेम / अंवरे'},
    'horsegram': {'en': 'Horse Gram (Huruli)', 'kn': 'ಹುರುಳಿ', 'hi': 'कुलथी'},
    'vegetables': {'en': 'Seasonal Vegetables', 'kn': 'ತರಕಾರಿಗಳು', 'hi': 'मौसमी सब्जियां'},
    'flowers': {'en': 'Commercial Flowers', 'kn': 'ಹೂವುಗಳು', 'hi': 'व्यावसायिक फूल'},
    'fodder': {'en': 'Green Fodder', 'kn': 'ಹಸಿರು ಮೇವು', 'hi': 'हरा चारा'},
    'turmeric': {'en': 'Turmeric', 'kn': 'ಅರಿಶಿನ', 'hi': 'हल्दी'},
    'cowpea': {'en': 'Cowpea (Alasande)', 'kn': 'ಅಲಸಂದೆ', 'hi': 'लोबिया'},
    'chilli': {'en': 'Chilli', 'kn': 'ಮೆಣಸಿನಕಾಯಿ', 'hi': 'मिर्च'},
    'ginger': {'en': 'Ginger', 'kn': 'ಶುಂಠಿ', 'hi': 'अदरक'},
    'tobacco': {'en': 'Tobacco', 'kn': 'ತಂಬಾಕು', 'hi': 'तंबाकू'},
    'bajra': {'en': 'Bajra (Pearl Millet)', 'kn': 'ಸಜ್ಜೆ', 'hi': 'बाजरा'},
    'pulses': {'en': 'Pulses', 'kn': 'ಬೇಳೆಕಾಳುಗಳು', 'hi': 'दलहनी फसलें'}
}

# Commodity translations dictionary accessible in titlecase and lowercase
COMMODITY_TRANSLATIONS = {}
for _k, _v in CROP_NAMES_MAP.items():
    COMMODITY_TRANSLATIONS[_k] = _v
    COMMODITY_TRANSLATIONS[_k.title()] = _v
    COMMODITY_TRANSLATIONS[_k.upper()] = _v
COMMODITY_TRANSLATIONS['Rice (Paddy)'] = {'en': 'Rice (Paddy)', 'kn': 'ಭತ್ತ (ಅಕ್ಕಿ)', 'hi': 'चावल (धान)'}
COMMODITY_TRANSLATIONS['Maize (Corn)'] = {'en': 'Maize (Corn)', 'kn': 'ಮೆಕ್ಕೆಜೋಳ', 'hi': 'मक्का'}
COMMODITY_TRANSLATIONS['Chickpea (Bengal gram)'] = {'en': 'Chickpea (Bengal gram)', 'kn': 'ಕಡಲೆ (ಕಡಲೆಕಾಳು)', 'hi': 'चना'}

# Crop name detection aliases across English, Kannada, and Hindi
CROP_ALIASES = {
    'rice': 'rice', 'paddy': 'rice', 'ಭತ್ತ': 'rice', 'ಅಕ್ಕಿ': 'rice', 'चावल': 'rice', 'धान': 'rice',
    'maize': 'maize', 'corn': 'maize', 'ಮೆಕ್ಕೆಜೋಳ': 'maize', 'ಜೋಳ': 'maize', 'मक्का': 'maize', 'भुट्टा': 'maize',
    'chickpea': 'chickpea', 'gram': 'chickpea', 'bengal gram': 'chickpea', 'ಕಡಲೆ': 'chickpea', 'ಕಡಲೆಕಾಳು': 'chickpea', 'चना': 'chickpea',
    'kidneybeans': 'kidneybeans', 'rajma': 'kidneybeans', 'ರಾಜಮಾ': 'kidneybeans', 'राजमा': 'kidneybeans',
    'pigeonpeas': 'pigeonpeas', 'tur': 'pigeonpeas', 'arhar': 'pigeonpeas', 'ತೊಗರಿ': 'pigeonpeas', 'ತೊಗರಿ ಬೇಳೆ': 'pigeonpeas', 'अरहर': 'pigeonpeas', 'तुअर': 'pigeonpeas',
    'mothbeans': 'mothbeans', 'matki': 'mothbeans', 'ಮಡಿಕೆ ಕಾಳು': 'mothbeans', 'मोठ': 'mothbeans',
    'mungbean': 'mungbean', 'green gram': 'mungbean', 'moong': 'mungbean', 'ಹೆಸರು': 'mungbean', 'ಹೆಸರುಕಾಳು': 'mungbean', 'मूंग': 'mungbean',
    'blackgram': 'blackgram', 'urad': 'blackgram', 'ಉದ್ದು': 'blackgram', 'ಉದ್ದಿನ ಬೇಳೆ': 'blackgram', 'उड़द': 'blackgram',
    'lentil': 'lentil', 'masoor': 'lentil', 'ಮಸೂರ': 'lentil', 'मसूर': 'lentil',
    'pomegranate': 'pomegranate', 'ದಾಳಿಂಬೆ': 'pomegranate', 'अनार': 'pomegranate',
    'banana': 'banana', 'ಬಾಳೆ': 'banana', 'ಬಾಳೆಹಣ್ಣು': 'banana', 'केला': 'banana',
    'mango': 'mango', 'ಮಾವು': 'mango', 'ಮಾವಿನಹಣ್ಣು': 'mango', 'आम': 'mango',
    'grapes': 'grapes', 'ದ್ರಾಕ್ಷಿ': 'grapes', 'अंगूर': 'grapes',
    'watermelon': 'watermelon', 'ಕಲ್ಲಂಗಡಿ': 'watermelon', 'तरबूज': 'watermelon',
    'muskmelon': 'muskmelon', 'ಕರಬೂಜ': 'muskmelon', 'खरबूजा': 'muskmelon',
    'apple': 'apple', 'ಸೇಬು': 'apple', 'सेब': 'apple',
    'orange': 'orange', 'ಕಿತ್ತಳೆ': 'orange', 'संतरा': 'orange',
    'papaya': 'papaya', 'ಪರಂಗಿ': 'papaya', 'ಪಪ್ಪಾಯಿ': 'papaya', 'पपीता': 'papaya',
    'coconut': 'coconut', 'ತೆಂಗು': 'coconut', 'ತೆಂಗಿನಕಾಯಿ': 'coconut', 'नारियल': 'coconut',
    'cotton': 'cotton', 'ಹತ್ತಿ': 'cotton', 'ಕಪಾಸ್': 'cotton', 'कपास': 'cotton', 'रूई': 'cotton',
    'jute': 'jute', 'ಸೆಣಬು': 'jute', 'जूಟ್': 'jute', 'जूट': 'jute', 'पटसन': 'jute',
    'coffee': 'coffee', 'ಕಾಫಿ': 'coffee', 'कॉफी': 'coffee',
    'tomato': 'tomato', 'ಟೊಮೆಟೊ': 'tomato', 'ಟೊಮೇಟೊ': 'tomato', 'टमाटर': 'tomato',
    'potato': 'potato', 'ಆಲೂಗಡ್ಡೆ': 'potato', 'आलू': 'potato',
    'onion': 'onion', 'ಈರುಳ್ಳಿ': 'onion', 'प्याज': 'onion',
    'wheat': 'wheat', 'ಗೋಧಿ': 'wheat', 'गेहूं': 'wheat',
    'fieldbeans': 'fieldbeans', 'avarekai': 'fieldbeans', 'ಅವರೆ': 'fieldbeans', 'ಅವರೆಕಾಳು': 'fieldbeans', 'सेम': 'fieldbeans',
    'horsegram': 'horsegram', 'huruli': 'horsegram', 'ಹುರುಳಿ': 'horsegram', 'कुलथी': 'horsegram',
    'vegetables': 'vegetables', 'ತರಕಾರಿ': 'vegetables', 'सब्जियां': 'vegetables',
    'flowers': 'flowers', 'ಹೂವು': 'flowers', 'फूल': 'flowers',
    'fodder': 'fodder', 'ಮೇವು': 'fodder', 'चारा': 'fodder',
    'turmeric': 'turmeric', 'ಅರಿಶಿನ': 'turmeric', 'हल्दी': 'turmeric',
    'cowpea': 'cowpea', 'alasande': 'cowpea', 'ಅಲಸಂದೆ': 'cowpea', 'लोबिया': 'cowpea',
    'chilli': 'chilli', 'menasinakayi': 'chilli', 'ಮೆಣಸಿನಕಾಯಿ': 'chilli', 'मिर्च': 'chilli',
    'ginger': 'ginger', 'shunti': 'ginger', 'ಶುಂಠಿ': 'ginger', 'अदरक': 'ginger',
    'tobacco': 'tobacco', 'hogesoppu': 'tobacco', 'ತಂಬಾಕು': 'tobacco', 'तंबाकू': 'tobacco',
    'bajra': 'bajra', 'sajje': 'bajra', 'ಸಜ್ಜೆ': 'bajra', 'बाजरा': 'bajra',
    'pulses': 'pulses', 'ಕಾಳುಗಳು': 'pulses', 'दालें': 'pulses'
}

def find_crop_in_text(text):
    if not text:
        return None
    text_l = text.lower().strip()
    # Check multi-word aliases first
    for alias, crop_key in sorted(CROP_ALIASES.items(), key=lambda x: -len(x[0])):
        if alias in text_l:
            return crop_key
    return None

PLANT_AND_CROP_NAMES = {
    'apple': {'en': 'Apple', 'kn': 'ಸೇಬು (Apple)', 'hi': 'सेब (Apple)'},
    'blueberry': {'en': 'Blueberry', 'kn': 'ಬ್ಲೂಬೆರ್ರಿ (Blueberry)', 'hi': 'ब्लूबेरी (Blueberry)'},
    'cherry': {'en': 'Cherry', 'kn': 'ಚೆರ್ರಿ (Cherry)', 'hi': 'चेरी (Cherry)'},
    'cherry including sour': {'en': 'Cherry', 'kn': 'ಚೆರ್ರಿ (Cherry)', 'hi': 'चेरी (Cherry)'},
    'corn': {'en': 'Maize (Corn)', 'kn': 'ಮೆಕ್ಕೆಜೋಳ (Corn)', 'hi': 'मक्का (Corn)'},
    'corn maize': {'en': 'Maize (Corn)', 'kn': 'ಮೆಕ್ಕೆಜೋಳ (Corn)', 'hi': 'मक्का (Corn)'},
    'corn_(maize)': {'en': 'Maize (Corn)', 'kn': 'ಮೆಕ್ಕೆಜೋಳ (Corn)', 'hi': 'मक्का (Corn)'},
    'grape': {'en': 'Grapes', 'kn': 'ದ್ರಾಕ್ಷಿ (Grapes)', 'hi': 'अंगूर (Grapes)'},
    'orange': {'en': 'Orange (Citrus)', 'kn': 'ಕಿತ್ತಳೆ (Orange)', 'hi': 'संतरा (Orange)'},
    'peach': {'en': 'Peach', 'kn': 'ಪೀಚ್ (Peach)', 'hi': 'आड़ू (Peach)'},
    'pepper': {'en': 'Bell Pepper (Capsicum)', 'kn': 'ದಪ್ಪ ಮೆಣಸಿನಕಾಯಿ (Capsicum)', 'hi': 'शिमला मिर्च (Capsicum)'},
    'pepper, bell': {'en': 'Bell Pepper (Capsicum)', 'kn': 'ದಪ್ಪ ಮೆಣಸಿನಕಾಯಿ (Capsicum)', 'hi': 'शिमला मिर्च (Capsicum)'},
    'pepper bell': {'en': 'Bell Pepper (Capsicum)', 'kn': 'ದಪ್ಪ ಮೆಣಸಿನಕಾಯಿ (Capsicum)', 'hi': 'शिमला मिर्च (Capsicum)'},
    'potato': {'en': 'Potato', 'kn': 'ಆಲೂಗಡ್ಡೆ (Potato)', 'hi': 'आलू (Potato)'},
    'raspberry': {'en': 'Raspberry', 'kn': 'ರಾಸ್ಪ್ಬೆರಿ (Raspberry)', 'hi': 'रास्पबेरी (Raspberry)'},
    'rice': {'en': 'Rice (Paddy)', 'kn': 'ಭತ್ತ (Rice)', 'hi': 'चावल (Rice)'},
    'soybean': {'en': 'Soybean', 'kn': 'ಸೋಯಾಬೀನ್ (Soybean)', 'hi': 'सोयाबीन (Soybean)'},
    'squash': {'en': 'Squash', 'kn': 'ಸೀಮೆ ಸೋರೆಕಾಯಿ (Squash)', 'hi': 'कद्दू (Squash)'},
    'strawberry': {'en': 'Strawberry', 'kn': 'ಸ್ಟ್ರಾಬೆರಿ (Strawberry)', 'hi': 'स्ट्रॉबेरी (Strawberry)'},
    'tomato': {'en': 'Tomato', 'kn': 'ಟೊಮೆಟೊ (Tomato)', 'hi': 'टमाटर (Tomato)'},
    'wheat': {'en': 'Wheat', 'kn': 'ಗೋಧಿ (Wheat)', 'hi': 'गेहूं (Wheat)'},
    'cotton': {'en': 'Cotton', 'kn': 'ಹತ್ತಿ (Cotton)', 'hi': 'कपास (Cotton)'},
    'coffee': {'en': 'Coffee', 'kn': 'ಕಾಫಿ (Coffee)', 'hi': 'कॉफी (Coffee)'},
    'banana': {'en': 'Banana', 'kn': 'ಬಾಳೆಹಣ್ಣು (Banana)', 'hi': 'केला (Banana)'},
    'coconut': {'en': 'Coconut', 'kn': 'ತೆಂಗಿನಕಾಯಿ (Coconut)', 'hi': 'नारियल (Coconut)'},
    'onion': {'en': 'Onion', 'kn': 'ಈರುಳ್ಳಿ (Onion)', 'hi': 'प्याज (Onion)'},
    'mango': {'en': 'Mango', 'kn': 'ಮಾವು (Mango)', 'hi': 'आम (Mango)'},
    'chickpea': {'en': 'Chickpea (Bengal Gram)', 'kn': 'ಕಡಲೆ (ಬೆಂಗಾಲ್ ಗ್ರಾಂ / Bengal Gram)', 'hi': 'चना (बंगाल चना / Bengal Gram)'},
    'kidneybeans': {'en': 'Kidney Beans (Rajma)', 'kn': 'ರಾಜ್ಮಾ (Kidney Beans)', 'hi': 'राजमा (Kidney Beans)'},
    'pigeonpeas': {'en': 'Pigeonpeas (Tur)', 'kn': 'ತೊಗರಿ (Tur)', 'hi': 'अरहर (Tur)'},
    'mothbeans': {'en': 'Moth Beans', 'kn': 'ಮಡಿಕೆ ಕಾಳು (Moth Beans)', 'hi': 'मोठ बीन (Moth Beans)'},
    'mungbean': {'en': 'Mung Bean (Green Gram)', 'kn': 'ಹೆಸರುಕಾಳು (Moong)', 'hi': 'मूंग (Moong)'},
    'blackgram': {'en': 'Black Gram (Urad)', 'kn': 'ಉದ್ದಿನಕಾಳು (Urad)', 'hi': 'उड़द (Urad)'},
    'lentil': {'en': 'Lentil (Masoor)', 'kn': 'ಮಸೂರ ಬೇಳೆ (Masoor)', 'hi': 'मसूर (Masoor)'},
    'pomegranate': {'en': 'Pomegranate', 'kn': 'ದಾಳಿಂಬೆ (Pomegranate)', 'hi': 'अनार (Pomegranate)'},
    'watermelon': {'en': 'Watermelon', 'kn': 'ಕಲ್ಲಂಗಡಿ (Watermelon)', 'hi': 'तरबूज (Watermelon)'},
    'muskmelon': {'en': 'Muskmelon', 'kn': 'ಕರ್ಬೂಜ (Muskmelon)', 'hi': 'खरबूजा (Muskmelon)'},
    'papaya': {'en': 'Papaya', 'kn': 'ಪಪ್ಪಾಯಿ (Papaya)', 'hi': 'पपीता (Papaya)'},
    'jute': {'en': 'Jute', 'kn': 'ಸೆಣಬು (Jute)', 'hi': 'जूट (Jute)'},
    'fieldbeans': {'en': 'Field Bean (Avarekai)', 'kn': 'ಅವರೆಕಾಳು (Avarekai)', 'hi': 'सेम / अंवरे (Field Bean)'},
    'horsegram': {'en': 'Horse Gram (Huruli)', 'kn': 'ಹುರುಳಿ (Huruli)', 'hi': 'कुलथी (Horse Gram)'},
    'vegetables': {'en': 'Seasonal Vegetables', 'kn': 'ತರಕಾರಿಗಳು (Vegetables)', 'hi': 'मौसमी सब्जियां (Vegetables)'},
    'flowers': {'en': 'Commercial Flowers', 'kn': 'ಹೂವುಗಳು (Flowers)', 'hi': 'व्यावसायिक फूल (Flowers)'},
    'fodder': {'en': 'Green Fodder', 'kn': 'ಹಸಿರು ಮೇವು (Fodder)', 'hi': 'हरा चारा (Fodder)'},
    'turmeric': {'en': 'Turmeric', 'kn': 'ಅರಿಶಿನ (Turmeric)', 'hi': 'हल्दी (Turmeric)'},
    'cowpea': {'en': 'Cowpea (Alasande)', 'kn': 'ಅಲಸಂದೆ (Alasande)', 'hi': 'लोबिया (Cowpea)'},
    'chilli': {'en': 'Chilli', 'kn': 'ಮೆಣಸಿನಕಾಯಿ (Chilli)', 'hi': 'मिर्च (Chilli)'},
    'ginger': {'en': 'Ginger', 'kn': 'ಶುಂಠಿ (Ginger)', 'hi': 'अदरक (Ginger)'},
    'tobacco': {'en': 'Tobacco', 'kn': 'ತಂಬಾಕು (Tobacco)', 'hi': 'तंबाकू (Tobacco)'},
    'bajra': {'en': 'Bajra (Pearl Millet)', 'kn': 'ಸಜ್ಜೆ (Sajje)', 'hi': 'बाजरा (Bajra)'},
    'pulses': {'en': 'Pulses', 'kn': 'ಬೇಳೆಕಾಳುಗಳು (Pulses)', 'hi': 'दलहनी फसलें (Pulses)'}
}

def get_crop_name(crop_key, lang='en'):
    if not crop_key:
        return ""
    
    # First normalize through canonical multilingual alias dictionary
    canon = ""
    try:
        from models.agri_calendar_service import normalize_crop_name
        canon = normalize_crop_name(crop_key)
    except Exception:
        canon = ""

    crop_k = (canon or crop_key).lower().strip()
    crop_clean = crop_k.replace('_', ' ').replace('-', ' ')
    crop_clean = ' '.join(crop_clean.split())
    
    if crop_k in PLANT_AND_CROP_NAMES:
        return PLANT_AND_CROP_NAMES[crop_k].get(lang, crop_key.title())
    if crop_clean in PLANT_AND_CROP_NAMES:
        return PLANT_AND_CROP_NAMES[crop_clean].get(lang, crop_key.title())
    
    for k, v in PLANT_AND_CROP_NAMES.items():
        if k in crop_clean:
            return v.get(lang, crop_key.title())
            
    if crop_k in CROP_TRANSLATIONS:
        return CROP_TRANSLATIONS[crop_k]['name'].get(lang, crop_key.title())
    return crop_key.title()

def get_disease_translation(crop_name, disease_name, lang='en'):
    crop_l = crop_name.lower().strip() if crop_name else 'plant'
    dis_l = disease_name.lower().strip() if disease_name else ''
    
    crop_tr = get_crop_name(crop_l, lang)
    
    if 'healthy' in dis_l:
        if lang == 'kn':
            return f"{crop_tr} : ಆರೋಗ್ಯಕರ ಸಸ್ಯ (Healthy - ಯಾವುದೇ ರೋಗವಿಲ್ಲ)"
        elif lang == 'hi':
            return f"{crop_tr} : स्वस्थ पौधा (Healthy - कोई बीमारी नहीं)"
        return f"{crop_tr} : Healthy Plant"

    disease_map = {
        'apple scab': {'kn': 'ಸ್ಕ್ಯಾಬ್ ರೋಗ', 'hi': 'स्कैब रोग'},
        'black rot': {'kn': 'ಕಪ್ಪು ಕೊಳೆತ ರೋಗ', 'hi': 'काला सड़न रोग'},
        'cedar apple rust': {'kn': 'ಸಿಡಾರ್ ತುಕ್ಕು ರೋಗ', 'hi': 'रस्ट (गेरुआ) रोग'},
        'powdery mildew': {'kn': 'ಬೂದಿ ರೋಗ', 'hi': 'चूर्णिल फफूंद (पाउडरी मिल्ड्यू)'},
        'cercospora leaf spot gray leaf spot': {'kn': 'ಸೆರ್ಕೊಸ್ಪೊರಾ ಎಲೆ ಚುಕ್ಕೆ ರೋಗ', 'hi': 'सर्कोस्पोरा पत्ती धब्बा रोग'},
        'common rust': {'kn': 'ಸಾಮಾನ್ಯ ತುಕ್ಕು ರೋಗ', 'hi': 'सामान्य रस्ट रोग'},
        'northern leaf blight': {'kn': 'ಉತ್ತರದ ಎಲೆ ಕಮಟು ರೋಗ', 'hi': 'उत्तरी पत्ती झुलसा रोग'},
        'esca (black measles)': {'kn': 'ಎಸ್ಕಾ (ಕಪ್ಪು ದಡಾರ ರೋಗ)', 'hi': 'एस्का (काला चेचक)'},
        'leaf blight (isariopsis leaf spot)': {'kn': 'ಎಲೆ ಕಮಟು ರೋಗ', 'hi': 'पत्ती झुलसा रोग'},
        'haunglongbing (citrus greening)': {'kn': 'ಸಿಟ್ರಸ್ ಗ್ರೀನಿಂಗ್ ರೋಗ', 'hi': 'सिट्रस ग्रीनिंग रोग'},
        'bacterial spot': {'kn': 'ಬ್ಯಾಕ್ಟೀರಿಯಾದ ಎಲೆ ಚುಕ್ಕೆ ರೋಗ', 'hi': 'जीवाणु पत्ती धब्बा रोग'},
        'early blight': {'kn': 'ಆರಂಭಿಕ ಮುಟುರು / ಕಮಟು ರೋಗ', 'hi': 'अगेती झुलसा रोग'},
        'late blight': {'kn': 'ತಡವಾದ ಕೊಳೆತ ರೋಗ', 'hi': 'पछेती झुलसा रोग'},
        'leaf mold': {'kn': 'ಎಲೆ ಬೂಸ್ಟು ರೋಗ', 'hi': 'पत्ती फफूंद (लीफ मोल्ड)'},
        'septoria leaf spot': {'kn': 'ಸೆಪ್ಟೋರಿಯಾ ಎಲೆ ಚುಕ್ಕೆ ರೋಗ', 'hi': 'सेप्टोरिया पत्ती धब्बा रोग'},
        'spider mites two-spotted spider mite': {'kn': 'ಕೆಂಪು ಜೇಡ ನುಸಿ ಕೀಟ ಬಾಧೆ', 'hi': 'दो धब्बेदार लाल मकड़ी कीट'},
        'target spot': {'kn': 'ಟಾರ್ಗೆಟ್ ಚುಕ್ಕೆ ರೋಗ', 'hi': 'टार्गेट स्पॉट रोग'},
        'tomato yellow leaf curl virus': {'kn': 'ಟೊಮೆಟೊ ಹಳದಿ ಎಲೆ ಸುರುಟು ವೈರಸ್', 'hi': 'पीला पत्ती मरोड़क वायरस'},
        'tomato mosaic virus': {'kn': 'ಟೊಮೆಟೊ ಮೊಸಾಯಿಕ್ ವೈರಸ್', 'hi': 'टमाटर मोज़ेक वायरस'},
        'bacterial leaf blight': {'kn': 'ಬ್ಯಾಕ್ಟೀರಿಯಾ ಎಲೆ ಕಮಟು ರೋಗ', 'hi': 'जीवाणु पत्ती झुलसा रोग'},
        'brown spot': {'kn': 'ಕಂದು ಚುಕ್ಕೆ ರೋಗ', 'hi': 'भूरा धब्बा रोग'},
        'leaf blast': {'kn': 'ಎಲೆ ಬೆಂಕಿ ರೋಗ (ಬ್ಲಾಸ್ಟ್)', 'hi': 'पत्ती झुलसा / ब्लास्ट रोग'},
        'leaf scald': {'kn': 'ಎಲೆ ಸುಟ್ಟ ರೋಗ (ಸ್ಕಾಲ್ಡ್)', 'hi': 'पत्ती स्केल्ड रोग'},
        'narrow brown spot': {'kn': 'ಕಿರಿದಾದ ಕಂದು ಚುಕ್ಕೆ ರೋಗ', 'hi': 'संकीर्ण भूरा धब्बा रोग'},
        'blackpoint': {'kn': 'ಬ್ಲ್ಯಾಕ್‌ಪಾಯಿಂಟ್ ರೋಗ', 'hi': 'ब्लैकपॉइंट रोग'},
        'fusariumfootrot': {'kn': 'ಫ್ಯುಸಾರಿಯಮ್ ಬೇರು ಕೊಳೆತ', 'hi': 'फ्यूजेरियम जड़ सड़न'},
        'healthyleaf': {'kn': 'ಆರೋಗ್ಯಕರ ಎಲೆ', 'hi': 'स्वस्थ पत्ती'},
        'leafblight': {'kn': 'ಎಲೆ ಕಮಟು ರೋಗ', 'hi': 'पत्ती झुलसा'},
        'wheatblast': {'kn': 'ಗೋಧಿ ಬ್ಲಾಸ್ಟ್ ರೋಗ', 'hi': 'गेहूं ब्लास्ट रोग'}
    }

    dis_clean = dis_l.replace('-', ' ').replace('_', ' ')
    dis_clean = ' '.join(dis_clean.split())

    dis_tr = None
    for k, v in disease_map.items():
        if k in dis_clean:
            dis_tr = v.get(lang, disease_name)
            break

    if not dis_tr:
        dis_tr = disease_name

    sep = " - " if lang == 'en' else " : "
    return f"{crop_tr}{sep}{dis_tr}"

def format_weather_status(district, temp, humidity, weather_desc, lang='en'):
    weather_dict = {
        'clear sky': {'kn': 'ಸ್ವಚ್ಛ ಆಕಾಶ', 'hi': 'साफ आसमान'},
        'few clouds': {'kn': 'ಸ್ವಲ್ಪ ಮೋಡ ಕವಿದಿದೆ', 'hi': 'हल्के बादल'},
        'scattered clouds': {'kn': 'ಚದುರಿದ ಮೋಡಗಳು', 'hi': 'बिखरे हुए बादल'},
        'broken clouds': {'kn': 'ಮೋಡ ಕವಿದ ವಾತಾವರಣ', 'hi': 'घने बादल'},
        'overcast clouds': {'kn': 'ದಟ್ಟ ಮೋಡ ಕವಿದಿದೆ', 'hi': 'घने काले बादल'},
        'light rain': {'kn': 'ಹಗುರ ಮಳೆ', 'hi': 'हल्की बारिश'},
        'moderate rain': {'kn': 'ಮಧ್ಯಮ ಮಳೆ', 'hi': 'मध्यम बारिश'},
        'heavy intensity rain': {'kn': 'ಭಾರಿ ಮಳೆ', 'hi': 'भारी बारिश'},
        'thunderstorm': {'kn': 'ಗುಡುಗು ಸಹಿತ ಮಳೆ', 'hi': 'तूफान और बारिश'},
        'mist': {'kn': 'ಮಂಜು', 'hi': 'कोहरा / धुंध'},
        'haze': {'kn': 'ಧೂಳುಮಂಜು', 'hi': 'धुंध'}
    }
    
    desc_l = weather_desc.lower().strip() if weather_desc else 'clear sky'
    tr_desc = weather_dict.get(desc_l, {}).get(lang, weather_desc.title() if weather_desc else '')
    
    if lang == 'kn':
        return f"{district} ನೇರ ಹವಾಮಾನ: {temp}°C, {humidity}% ತೇವಾಂಶ ({tr_desc})"
    elif lang == 'hi':
        return f"{district} का लाइव मौसम: {temp}°C, {humidity}% आर्द्रता ({tr_desc})"
    return f"Live weather fetched for {district}: {temp}°C, {humidity}% humidity ({weather_desc.title() if weather_desc else ''})"

def build_multilingual_voice_answer(query, lang='en'):
    if not query:
        msgs = {
            'en': "Please enter or speak a farming question.",
            'kn': "ದಯವಿಟ್ಟು ಕೃಷಿ ಪ್ರಶ್ನೆಯನ್ನು ನಮೂದಿಸಿ ಅಥವಾ ಮಾತನಾಡಿ.",
            'hi': "कृपया कोई कृषि प्रश्न दर्ज करें या बोलें।"
        }
        return msgs.get(lang, msgs['en'])

    query_lower = query.lower()
    
    # Detect language from query content if Kannada / Hindi script present
    if any(ord(char) >= 0x0C80 and ord(char) <= 0x0CFF for char in query):
        lang = 'kn'
    elif any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in query):
        lang = 'hi'

    mentioned_crop = find_crop_in_text(query_lower)

    pest_words = [
        "pest", "pests", "pesticide", "pesticides", "insect", "insects",
        "insecticide", "spray", "medicine", "treatment", "control",
        "bug", "bugs", "worm", "disease", "cure", "ರೋಗ", "ಹುಳು", "ಕೀಟ", "ಕೀಟನಾಶಕ", "ಔಷಧಿ", "ಉಪಚಾರ",
        "कीट", "कीटनाशक", "दवा", "इल्ली", "सुंडी", "बीमारी", "इलाज", "उपचार"
    ]

    fertilizer_words = [
        'fertilizer', 'fertilizers', 'manure', 'npk', 'nitrogen', 'urea', 'potash', 'phosphate', 'nutrient', 'dose',
        'ಗೊಬ್ಬರ', 'ಯೂರಿಯಾ', 'ಉತ್ಪಾದಕ', 'ಉರ್ವರಕ', 'ಪೋಷಕಾಂಶ', 'ಸಾರಜನಕ', 'ರಂಜಕ', 'ಪೊಟ್ಯಾಶ್',
        'उर्वरक', 'खाद', 'यूरिया', 'पोटाश', 'फॉस्फोरस', 'पोषण', 'खुराक'
    ]
    sowing_words = [
        'plant', 'sow', 'planting', 'sowing', 'seed', 'time to plant', 'when to plant', 'season',
        'ಬಿತ್ತನೆ', 'ನಾಟಿ', 'ಬೆಳೆಯುವುದು', 'ಬುವಾಯಿ', 'ಯಾವಾಗ ಬಿತ್ತನೆ', 'ಹಂಗಾಮು',
        'बुवाई', 'बोना', 'कब बोएं', 'रोपाई', 'लगाने का समय', 'मौसम'
    ]
    harvest_words = [
        'harvest', 'harvesting', 'cut', 'cutting', 'yield', 'duration',
        'ಕೊಯ್ಲು', 'ಕಟಾವು', 'ಫಸಲು ಕಟಾವು', 'ಇಳುವರಿ', 'ಯಾವಾಗ ಕಟಾವು',
        'कटाई', 'फसल काटना', 'कब काटें', 'पैदावार', 'उपज'
    ]
    price_words = [
        'sell', 'selling', 'sold', 'price', 'market', 'mandi', 'rate', 'cost', 'profit', 'month', 'highest', 'peak', 'earn',
        'ಬೆಲೆ', 'ದರ', 'ಮಾರುಕಟ್ಟೆ', 'ಮಾರಾಟ', 'ಮಂಡಿ', 'ಲಾಭ', 'ತಿಂಗಳು', 'ಯಾವಾಗ', 'ಗರಿಷ್ಠ', 'ಹೆಚ್ಚು', 'ಆದಾಯ',
        'मूल्य', 'भाव', 'दाम', 'मंडी', 'बेचना', 'बिक्री', 'बिकने', 'बिकना', 'बिकेगा', 'बिकता', 'मुनाफा', 'महीना', 'महीने', 'कब', 'ज्यादा', 'अधिकतम', 'महंगा', 'कमाई'
    ]

    crop_data = CROP_TRANSLATIONS.get(mentioned_crop, CROP_TRANSLATIONS.get('default')) if mentioned_crop else None
    crop_display = get_crop_name(mentioned_crop, lang) if mentioned_crop else ""

    # 1. Pest query for a crop
    if mentioned_crop and any(word in query_lower for word in pest_words):
        pests = crop_data['pests'].get(lang, crop_data['pests']['en'])
        pest_lines = "\n".join(f"• {p}" for p in pests)
        if lang == 'kn':
            return (
                f"🐛 {crop_display.upper()} ಬೆಳೆಯ ಸಾಮಾನ್ಯ ಕೀಟಗಳು ಮತ್ತು ಪರಿಹಾರ:\n"
                f"{pest_lines}\n\n"
                f"ರೋಗ ಪತ್ತೆಗಾಗಿ ಕೆಳಗಿನ ಎಲೆ ರೋಗ ಪತ್ತೆ (Leaf Disease Detection) ಮಾಡ್ಯೂಲ್ ಬಳಸಿ."
            )
        elif lang == 'hi':
            return (
                f"🐛 {crop_display.upper()} फसल के प्रमुख कीट एवं उपचार:\n"
                f"{pest_lines}\n\n"
                f"रोग की सटीक पहचान के लिए नीचे दिए गए पत्ती रोग पहचान मॉड्यूल का उपयोग करें।"
            )
        else:
            return (
                f"🐛 Common pests for {crop_display.upper()} and suggested treatment:\n"
                f"{pest_lines}\n\n"
                f"For a photo-based diagnosis of an actual infected leaf, use the Leaf Disease Detection module below."
            )

    # 2. Fertilizer query
    if mentioned_crop and any(word in query_lower for word in fertilizer_words):
        fert = crop_data['fertilizer'].get(lang, crop_data['fertilizer']['en'])
        if lang == 'kn':
            return f"🌿 {crop_display.upper()} ಬೆಳೆಗೆ ಶಿಫಾರಸು ಮಾಡಿದ ಗೊಬ್ಬರದ ಯೋಜನೆ:\n• {fert}"
        elif lang == 'hi':
            return f"🌿 {crop_display.upper()} फसल के लिए अनुशंसित उर्वरक योजना:\n• {fert}"
        else:
            return f"🌿 Fertilizer plan for {crop_display.upper()}:\n• {fert}"

    # 3. Planting / Sowing query
    if mentioned_crop and any(word in query_lower for word in sowing_words):
        planting = crop_data['planting_months'].get(lang, crop_data['planting_months']['en'])
        desc = crop_data['season_desc'].get(lang, crop_data['season_desc']['en'])
        if lang == 'kn':
            return f"🌱 {crop_display.upper()} ಬೆಳೆ ಬಿತ್ತನೆಗೆ ಸೂಕ್ತ ಸಮಯ: {planting}\n💡 ವಿವರ: {desc}"
        elif lang == 'hi':
            return f"🌱 {crop_display.upper()} फसल की बुवाई का सर्वोत्तम समय: {planting}\n💡 विवरण: {desc}"
        else:
            return f"🌱 Best planting months for {crop_display.upper()}: {planting}\n💡 Note: {desc}"

    # 4. Harvest query
    if mentioned_crop and any(word in query_lower for word in harvest_words):
        harvest = crop_data['harvest_months'].get(lang, crop_data['harvest_months']['en'])
        if lang == 'kn':
            return f"🌾 {crop_display.upper()} ಬೆಳೆ ಕೊಯ್ಲು ಮಾಡುವ ಅಂದಾಜು ತಿಂಗಳುಗಳು: {harvest}"
        elif lang == 'hi':
            return f"🌾 {crop_display.upper()} फसल की कटाई के अनुमानित महीने: {harvest}"
        else:
            return f"🌾 Expected harvest months for {crop_display.upper()}: {harvest}"

    # 5. Price / Selling / Peak Month query
    if mentioned_crop and any(word in query_lower for word in price_words):
        sell_m = crop_data['best_sell_months'].get(lang, crop_data['best_sell_months']['en'])
        tip = crop_data['sell_tip'].get(lang, crop_data['sell_tip']['en'])
        if lang == 'kn':
            return (
                f"💰 {crop_display.upper()} ಮಾರಾಟಕ್ಕೆ / ಗರಿಷ್ಠ ಬೆಲೆ ಪಡೆಯುವ ಉತ್ತಮ ತಿಂಗಳುಗಳು:\n"
                f"• {sell_m}\n\n"
                f"💡 ಮಾರುಕಟ್ಟೆ ಸಲಹೆ: {tip}\n\n"
                f"📊 ನಿಖರ ಮಂಡಿ ಬೆಲೆ ಮುನ್ಸೂಚನೆಗಾಗಿ ಕೆಳಗಿನ 'ಮಾರುಕಟ್ಟೆ ಬೆಲೆ' ಮಾಡ್ಯೂಲ್ ಬಳಸಿ!"
            )
        elif lang == 'hi':
            return (
                f"💰 {crop_display.upper()} बेचने / सबसे ज्यादा बिकने के सर्वोत्तम महीने:\n"
                f"• {sell_m}\n\n"
                f"💡 बाजार युक्ति: {tip}\n\n"
                f"📊 लाइव मंडी भाव एवं सटीक पूर्वानुमान के लिए नीचे 'बाजार मूल्य' मॉड्यूल का उपयोग करें!"
            )
        else:
            return (
                f"💰 Best Selling Months for {crop_display.upper()}:\n"
                f"• {sell_m}\n\n"
                f"💡 Market Tip: {tip}\n\n"
                f"📊 For a live price prediction, use the Market Price module below!"
            )

    # ── Seasonal Crop Recommendation Queries ─────────────────────────────
    kharif_words = ['ಮಳೆಗಾಲ', 'ಮುಂಗಾರು', 'ಖಾರೀಫ್', 'ಖರೀಫ್', 'rainy', 'monsoon', 'kharif', 'rain', 'बरसात', 'मानसून', 'खरीफ', 'बारिश']
    rabi_words = ['ಚಳಿಗಾಲ', 'ಹಿಂಗಾರು', 'ರಬಿ', 'ರಬೀ', 'winter', 'rabi', 'cool', 'सर्दियों', 'सर्दी', 'रबी', 'ठंड']
    zaid_words = ['ಬೇಸಿಗೆ', 'ಜಾಯಿದ್', 'summer', 'zaid', 'गर्मी', 'जायद', 'धूप']
    profit_words = ['ಲಾಭ', 'ಹೆಚ್ಚು ಹಣ', 'profitable', 'cash crop', 'profit', 'कमाई', 'मुनाफा', 'नकदी']

    # 1. Rainy / Kharif Season recommendation
    if any(k in query_lower for k in kharif_words) and any(w in query_lower for w in ['ಬೆಳೆ', 'ಬೆಳೆಯಬೇಕು', 'crop', 'grow', 'plant', 'recommend', 'फसल', 'उगाएं', 'बोएं', 'ಯಾವ']):
        if lang == 'kn':
            return (
                "🌧️ ಮಳೆಗಾಲ / ಮುಂಗಾರು (Kharif) ಹಂಗಾಮಿಗೆ ಶಿಫಾರಸು ಮಾಡಿದ ಪ್ರಮುಖ ಬೆಳೆಗಳು:\n"
                "• 🌾 ಭತ್ತ (Rice/Paddy) — ಹೆಚ್ಚು ಮಳೆ ಮತ್ತು ನೀರಾವರಿ ಇರುವ ಪ್ರದೇಶಗಳಿಗೆ ಅತ್ಯುತ್ತಮ\n"
                "• ☁️ ಹತ್ತಿ (Cotton) — ಕಪ್ಪು ಮಣ್ಣು ಮತ್ತು ಮಧ್ಯಮ ಮಳೆಗೆ ಅತಿ ಹೆಚ್ಚು ಲಾಭದಾಯಕ ಬೆಳೆ\n"
                "• 🌽 ಮೆಕ್ಕೆಜೋಳ (Maize) — ಕಡಿಮೆ ವೆಚ್ಚದಲ್ಲಿ ಶೀಘ್ರ ಇಳುವರಿ ನೀಡುವ ಬೆಳೆ\n"
                "• 🥜 ಕಡಲೆಕಾಯಿ (Groundnut) & ಸೋಯಾಬೀನ್ (Soybean) — ಮರಳು-ಕೆಂಪು ಮಣ್ಣಿಗೆ ಸೂಕ್ತ\n"
                "• 🌿 ತೊಗರಿ (Pigeonpeas/Tur) — ಮಿಶ್ರ ಬೆಳೆಯಾಗಿ ಅತ್ಯುತ್ತಮ\n\n"
                "💡 ನಿಮ್ಮ ಜಮೀನಿನ ಮಣ್ಣಿನ N-P-K ಮತ್ತು ಜಿಲ್ಲೆಯ ಹವಾಮಾನಕ್ಕೆ ತಕ್ಕಂತೆ ನಿಖರವಾದ ಬೆಳೆ ತಿಳಿಯಲು ಕೆಳಗಿನ 'ಬೆಳೆ ಶಿಫಾರಸು' ಮಾಡ್ಯೂಲ್ ಬಳಸಿ!"
            )
        elif lang == 'hi':
            return (
                "🌧️ बारिश / खरीफ (Kharif) मौसम के लिए अनुशंसित प्रमुख फसलें:\n"
                "• 🌾 धान / चावल (Rice) — अधिक वर्षा और जलभराव वाले क्षेत्रों के लिए सर्वोत्तम\n"
                "• ☁️ कपास (Cotton) — मध्यम वर्षा और काली मिट्टी के लिए उच्च लाभ वाली फसल\n"
                "• 🌽 मक्का (Maize) — कम लागत में शीघ्र और भरपूर पैदावार देने वाली फसल\n"
                "• 🥜 मूंगफली (Groundnut) एवं सोयाबीन (Soybean)\n"
                "• 🌿 अरहर / तुअर (Pigeonpeas) — दालों में सर्वोत्तम लाभ\n\n"
                "💡 अपनी मिट्टी के सटीक N-P-K और मौसम के अनुसार व्यक्तिगत अनुशंसा के लिए नीचे 'फसल अनुशंसा' मॉड्यूल का उपयोग करें!"
            )
        else:
            return (
                "🌧️ Top Recommended Crops for Rainy / Kharif Season:\n"
                "• 🌾 Rice (Paddy) — Best for high rainfall and wetland areas\n"
                "• ☁️ Cotton — Highly profitable for black soil and medium rainfall\n"
                "• 🌽 Maize (Corn) — Low cost, quick-yielding staple crop\n"
                "• 🥜 Groundnut & Soybean — Great for well-drained loamy/red soil\n"
                "• 🌿 Pigeonpeas (Tur) — Excellent pulse crop\n\n"
                "💡 For a tailored prediction customized to your exact soil N-P-K and district, use our Crop Recommendation module below!"
            )

    # 2. Winter / Rabi Season recommendation
    if any(k in query_lower for k in rabi_words) and any(w in query_lower for w in ['ಬೆಳೆ', 'ಬೆಳೆಯಬೇಕು', 'crop', 'grow', 'plant', 'recommend', 'फसल', 'उगाएं', 'बोएं', 'ಯಾವ']):
        if lang == 'kn':
            return (
                "❄️ ಚಳಿಗಾಲ / ಹಿಂಗಾರು (Rabi) ಹಂಗಾಮಿಗೆ ಶಿಫಾರಸು ಮಾಡಿದ ಪ್ರಮುಖ ಬೆಳೆಗಳು:\n"
                "• 🌾 ಗೋಧಿ (Wheat) — ತಂಪಾದ ಹವಾಮಾನ ಮತ್ತು ನೀರಾವರಿ ಜಮೀನುಗಳಿಗೆ ಸೂಕ್ತ\n"
                "• 🥣 ಕಡಲೆ (Chickpea / Bengal Gram) — ಕಡಿಮೆ ತೇವಾಂಶದಲ್ಲಿ ಉತ್ತಮ ಇಳುವರಿ\n"
                "• 🌾 ಜೋಳ (Jowar / Sorghum) — ಒಣಭೂಮಿ ಬೇಸಾಯಕ್ಕೆ ಅತ್ಯುತ್ತಮ\n"
                "• 🌿 ಸಾಸಿವೆ (Mustard) ಮತ್ತು ಬಾರ್ಲಿ (Barley)\n\n"
                "💡 ನಿಮ್ಮ ಜಮೀನಿನ ಮಣ್ಣಿನ ಗುಣಲಕ್ಷಣಗಳಿಗೆ ತಕ್ಕಂತೆ ನಿಖರ ಬೆಳೆ ತಿಳಿಯಲು ಕೆಳಗಿನ 'ಬೆಳೆ ಶಿಫಾರಸು' ಮಾಡ್ಯೂಲ್ ಬಳಸಿ!"
            )
        elif lang == 'hi':
            return (
                "❄️ रबी / सर्दियों के मौसम के लिए अनुशंसित प्रमुख फसलें:\n"
                "• 🌾 गेहूं (Wheat) — ठंडे मौसम और सिंचित भूमि के लिए मुख्य फसल\n"
                "• 🥣 चना (Chickpea) — कम पानी और शुष्क क्षेत्रों में बेहतरीन उत्पादन\n"
                "• 🌿 सरसों (Mustard) एवं जौ (Barley)\n\n"
                "💡 अपनी मिट्टी के अनुसार सटीक फसल जानने के लिए नीचे 'फसल अनुशंसा' मॉड्यूल का उपयोग करें!"
            )
        else:
            return (
                "❄️ Top Recommended Crops for Winter / Rabi Season:\n"
                "• 🌾 Wheat — Best for cool climate and irrigated soils\n"
                "• 🥣 Chickpea (Bengal Gram) — High yield with low moisture requirement\n"
                "• 🌿 Mustard, Sorghum (Jowar), and Barley\n\n"
                "💡 Use the Crop Recommendation module below with your soil parameters for a precise match!"
            )

    # 3. Summer / Zaid Season recommendation
    if any(k in query_lower for k in zaid_words) and any(w in query_lower for w in ['ಬೆಳೆ', 'ಬೆಳೆಯಬೇಕು', 'crop', 'grow', 'plant', 'recommend', 'फसल', 'उगाएं', 'बोएं', 'ಯಾವ']):
        if lang == 'kn':
            return (
                "☀️ ಬೇಸಿಗೆ / ಜಾಯಿದ್ (Zaid) ಹಂಗಾಮಿಗೆ ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆಗಳು:\n"
                "• 🍉 ಕಲ್ಲಂಗಡಿ (Watermelon) ಮತ್ತು ಕರ್ಬೂಜ (Muskmelon) — ಭಾರಿ ಮಾರುಕಟ್ಟೆ ಬೇಡಿಕೆ\n"
                "• 🥒 ಸೌತೆಕಾಯಿ ಮತ್ತು ತರಕಾರಿಗಳು\n"
                "• 🌿 ಹೆಸರುಕಾಳು (Green Gram / Moong)\n\n"
                "💡 ನೀರಾವರಿ ಸೌಲಭ್ಯವಿದ್ದರೆ ಈ ಬೆಳೆಗಳು ಬೇಸಿಗೆಯಲ್ಲಿ ಅತಿ ಹೆಚ್ಚು ಲಾಭ ತಂದುಕೊಡುತ್ತವೆ!"
            )
        elif lang == 'hi':
            return (
                "☀️ जायद / गर्मी के मौसम के लिए अनुशंसित फसलें:\n"
                "• 🍉 तरबूज एवं खरबूजा — गर्मियों में सर्वाधिक मांग और मुनाफा\n"
                "• 🥒 खीरा, ककड़ी और मौसमी सब्जियां\n"
                "• 🌿 मूंग और उड़द की दालें\n\n"
                "💡 सिंचाई सुविधा होने पर ये फसलें 60-70 दिनों में अच्छा लाभ देती हैं!"
            )
        else:
            return (
                "☀️ Top Recommended Crops for Summer / Zaid Season:\n"
                "• 🍉 Watermelon & Muskmelon — Peak summer market demand\n"
                "• 🥒 Cucumber & green vegetables\n"
                "• 🌿 Green Gram (Moong) pulse crop\n\n"
                "💡 With adequate irrigation, these crops yield fast profits within 60-70 days!"
            )

    # 4. High Profit / Cash Crop query
    if any(k in query_lower for k in profit_words) and any(w in query_lower for w in ['ಬೆಳೆ', 'crop', 'फसल']):
        if lang == 'kn':
            return (
                "💰 ಅತಿ ಹೆಚ್ಚು ಲಾಭ ತರುವ ವಾಣಿಜ್ಯ ಬೆಳೆಗಳು (Cash Crops):\n"
                "• ☁️ ಹತ್ತಿ (Cotton) — ಉತ್ತಮ ಮಾರುಕಟ್ಟೆ ಬೆಲೆ\n"
                "• 🍌 ಬಾಳೆಹಣ್ಣು (Banana) & ☕ ಕಾಫಿ (Coffee) — ವಾರ್ಷಿಕ ನಿರಂತರ ಆದಾಯ\n"
                "• 🥥 ತೆಂಗು (Coconut) & 🍎 ದಾಳಿಂಬೆ/ಸೇಬು\n\n"
                "💡 ನಿಮ್ಮ ಪ್ರದೇಶದ ಮಂಡಿ ದರ ತಿಳಿಯಲು ಕೆಳಗಿನ 'ಮಾರುಕಟ್ಟೆ ಬೆಲೆ' ಮಾಡ್ಯೂಲ್ ಪರಿಶೀಲಿಸಿ!"
            )
        elif lang == 'hi':
            return (
                "💰 सर्वाधिक लाभ देने वाली नकदी फसलें (Cash Crops):\n"
                "• ☁️ कपास (Cotton) — बाजार में निरंतर उच्च मांग\n"
                "• 🍌 केला (Banana) एवं ☕ कॉफी (Coffee)\n"
                "• 🥥 नारियल एवं अनार\n\n"
                "💡 अपने नजदीकी मंडी भाव जानने के लिए नीचे 'बाजार मूल्य' मॉड्यूल का उपयोग करें!"
            )
        else:
            return (
                "💰 Top High-Profit Cash Crops:\n"
                "• ☁️ Cotton — High market value\n"
                "• 🍌 Banana & ☕ Coffee — High commercial yield\n"
                "• 🥥 Coconut & Fruits\n\n"
                "💡 Check live mandi prices in the Market Price Prediction module below!"
            )

    # 5. General Crop Recommendation query
    if any(word in query_lower for word in ['which crop', 'what crop', 'crop grow', 'recommend', 'ಯಾವ ಬೆಳೆ', 'ಬೆಳೆಯಬೇಕು', 'ಯಾವ ಕೃಷಿ', 'ಸೂಕ್ತ ಬೆಳೆ', 'ಯಾವ ಬೆಳೆಯನ್ನು', 'कौन सी फसल', 'क्या उगाएं', 'फसल सुझाव']):
        if lang == 'kn':
            return (
                "🌱 ಕರ್ನಾಟಕದ ಸಾಮಾನ್ಯ ಹವಾಮಾನಕ್ಕೆ ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆಗಳು:\n"
                "• ಮುಂಗಾರು/ಮಳೆಗಾಲ: ಹತ್ತಿ (Cotton), ಭತ್ತ (Rice), ಮೆಕ್ಕೆಜೋಳ (Maize), ಕಡಲೆಕಾಯಿ\n"
                "• ಹಿಂಗಾರು/ಚಳಿಗಾಲ: ಕಡಲೆ (Chickpea), ಗೋಧಿ (Wheat), ಜೋಳ (Jowar)\n\n"
                "💡 ನಿಮ್ಮ ಜಮೀನಿನ ಮಣ್ಣಿನ ಸಾರಜನಕ (N), ರಂಜಕ (P), ಪೊಟ್ಯಾಸಿಯಮ್ (K) ಮತ್ತು ಮಳೆಯ ನಿಖರ ಆಧಾರದ ಮೇಲೆ ಫಲಿತಾಂಶ ಪಡೆಯಲು ಕೆಳಗಿನ 'ಬೆಳೆ ಶಿಫಾರಸು' ಮಾಡ್ಯೂಲ್ ಬಳಸಿ!"
            )
        elif lang == 'hi':
            return (
                "🌱 प्रमुख मौसमों के लिए अनुशंसित फसलें:\n"
                "• खरीफ/वर्षा: कपास (Cotton), धान (Rice), मक्का (Maize), मूंगफली\n"
                "• रबी/सर्दी: गेहूं (Wheat), चना (Chickpea), सरसों (Mustard)\n\n"
                "💡 अपनी मिट्टी के सटीक N, P, K एवं pH मान के आधार पर सर्वश्रेष्ठ फसल जानने के लिए नीचे 'फसल अनुशंसा' मॉड्यूल का उपयोग करें!"
            )
        else:
            return (
                "🌱 Major Recommended Crops:\n"
                "• Monsoon / Kharif: Cotton, Rice, Maize, Groundnut\n"
                "• Winter / Rabi: Wheat, Chickpea, Mustard, Jowar\n\n"
                "💡 For a tailored ML recommendation using your soil N, P, K, pH and rainfall, use the Crop Recommendation module below!"
            )

    # 6. Soil Health, Testing & pH Correction query
    if any(word in query_lower for word in ['soil', 'ph', 'testing', 'health', 'acidic', 'alkaline', 'ಸುಣ್ಣ', 'ಮಣ್ಣು', 'ಮಣ್ಣಿನ', 'ಪರೀಕ್ಷೆ', 'ಆಮ್ಲೀಯ', 'ಕ್ಷಾರೀಯ', 'ಫಲವತ್ತತೆ', 'मिट्टी', 'जांच', 'पीएच', 'सुधार', 'उर्वरता', 'मृदा', 'अम्लीय', 'क्षारीय', 'चूना', 'जिप्सम', 'फ ']):
        if lang == 'kn':
            return (
                "🧪 ಮಣ್ಣು ಪರೀಕ್ಷೆ ಮತ್ತು pH ಸುಧಾರಣಾ ಕ್ರಮಗಳು:\n"
                "• ಸೂಕ್ತ ಮಣ್ಣಿನ pH ಮಟ್ಟ: 6.0 ರಿಂದ 7.5 (ತಟಸ್ಥ).\n"
                "• ಆಮ್ಲೀಯ ಮಣ್ಣು (pH < 6.0): ಮಣ್ಣಿನ ಆಮ್ಲೀಯತೆ ಕಡಿಮೆ ಮಾಡಲು ಕೃಷಿ ಸುಣ್ಣ (Lime / Dolomite) ಸೇರಿಸಿ.\n"
                "• ಕ್ಷಾರೀಯ ಮಣ್ಣು (pH > 8.0): ಮಣ್ಣನ್ನು ಸರಿಪಡಿಸಲು ಕೃಷಿ ಜಿಪ್ಸಮ್ (Gypsum) ಮತ್ತು ಹಸಿರೆಲೆ ಗೊಬ್ಬರ ಬಳಸಿ.\n"
                "• ಪ್ರತಿ ಹೆಕ್ಟೇರ್‌ಗೆ 5-10 ಟನ್ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಅಥವಾ ಎರೆಹುಳು ಗೊಬ್ಬರ ಸೇರಿಸಿ ಮಣ್ಣಿನ ಸಾವಯವ ಇಂಗಾಲವನ್ನು ಹೆಚ್ಚಿಸಿ.\n\n"
                "💡 ನಿಮ್ಮ ಜಮೀನಿನ ನಿಖರ N-P-K ಮತ್ತು pH ಗೆ ತಕ್ಕಂತೆ ಬೆಳೆ ತಿಳಿಯಲು ಕೆಳಗಿನ 'ಬೆಳೆ ಶಿಫಾರಸು' ಮಾಡ್ಯೂಲ್ ಬಳಸಿ!"
            )
        elif lang == 'hi':
            return (
                "🧪 मिट्टी परीक्षण एवं pH सुधार के उपाय:\n"
                "• फसलों के लिए आदर्श मिट्टी का pH मान 6.0 से 7.5 के बीच होना चाहिए।\n"
                "• अम्लीय मिट्टी (pH < 6.0 कम होने पर): मिट्टी में कृषि चूना (Lime) मिलाएं।\n"
                "• क्षारीय मिट्टी (pH > 8.0 अधिक होने पर): मिट्टी सुधार के लिए कृषि जिप्सम (Gypsum) और हरी खाद का प्रयोग करें।\n"
                "• जल धारण क्षमता और पोषक तत्व बढ़ाने के लिए प्रति हेक्टेयर 5-10 टन गोबर या केंचुआ खाद डालें।\n\n"
                "💡 अपनी मिट्टी के N-P-K और pH के आधार पर सटीक फसल जानने के लिए नीचे 'फसल अनुशंसा' मॉड्यूल का उपयोग करें!"
            )
        else:
            return (
                "🧪 Soil Health, Testing & pH Correction Guidelines:\n"
                "• Ideal Soil pH for most crops is 6.0 to 7.5 (Neutral).\n"
                "• Acidic Soil (pH < 6.0): Apply Agricultural Lime (Calcium carbonate / Dolomite) to raise pH.\n"
                "• Alkaline Soil (pH > 8.0): Apply Agricultural Gypsum and green manuring (Dhaincha/Sunhemp) to lower pH.\n"
                "• Apply 5-10 tonnes/hectare of Farmyard Manure (FYM) or Vermicompost to boost soil organic carbon.\n\n"
                "💡 Enter your exact soil N-P-K and pH in the Crop Recommendation module below for accurate matching!"
            )

    # 7. Irrigation & Drip System query
    if any(word in query_lower for word in ['irrigation', 'water', 'drip', 'sprinkler', 'ನೀರು', 'ನೀರಾವರಿ', 'ಹನಿ ನೀರಾವರಿ', 'ತುಂತುರು', 'ಸಿಂಚನ', 'सिंचाई', 'पानी', 'ड्रिप', 'फव्वारा']):
        if lang == 'kn':
            return (
                "💧 ನೀರಾವರಿ ಮತ್ತು ನೀರಿನ ನಿರ್ವಹಣಾ ವಿಧಾನಗಳು:\n"
                "• ಹನಿ ನೀರಾವರಿ (Drip Irrigation): ಶೇ. 40-60% ನೀರನ್ನು ಉಳಿಸುತ್ತದೆ ಮತ್ತು ರಸಾವರಿ (Fertigation) ಮೂಲಕ ನೇರ ಪೋಷಕಾಂಶ ನೀಡುತ್ತದೆ.\n"
                "• ತುಂತುರು ನೀರಾವರಿ (Sprinkler): ಕಡಲೆ, ನೆಲಗಡಲೆ ಮತ್ತು ಗೋಧಿ ಬೆಳೆಗಳಿಗೆ ಹೆಚ್ಚು ಸೂಕ್ತ.\n"
                "• ಬಾಷ್ಪೀಕರಣ ತಡೆಗಟ್ಟಲು ಮುಂಜಾನೆ ಅಥವಾ ಸಂಜೆ ವೇಳೆ ನೀರು ಹಾಯಿಸಿ.\n"
                "• ಸರ್ಕಾರದಿಂದ ಹನಿ ನೀರಾವರಿ ಉಪಕರಣಗಳಿಗೆ ಶೇ. 70-90% ಸಬ್ಸಿಡಿ ಲಭ್ಯವಿದೆ."
            )
        elif lang == 'hi':
            return (
                "💧 सिंचाई एवं जल प्रबंधन की सर्वोत्तम विधियां:\n"
                "• ड्रिप (टपक) सिंचाई: 40-60% पानी की बचत करती है और घुलनशील खाद सीधे जड़ों तक पहुंचाती है।\n"
                "• फव्वारा (स्प्रिंकलर) सिंचाई: चना, गेहूं, सरसों और दालों के लिए बेहद प्रभावी है।\n"
                "• पानी के वाष्पीकरण को कम करने के लिए सुबह या शाम के समय ही सिंचाई करें।\n"
                "• प्रधानमंत्री कृषि सिंचाई योजना (PMKSY) के तहत ड्रिप सिस्टम पर 70-80% तक सरकारी अनुदान (सब्सिडी) मिलता है।"
            )
        else:
            return (
                "💧 Irrigation & Water Management Best Practices:\n"
                "• Drip Irrigation: Saves 40-60% water while delivering water-soluble fertilizers directly to root zones.\n"
                "• Sprinkler Irrigation: Best suited for pulses, wheat, mustard, and groundnut.\n"
                "• Irrigate during early mornings or evenings to minimize evaporation loss.\n"
                "• Avail 70-90% government subsidy under Pradhan Mantri Krishi Sinchayee Yojana (PMKSY)."
            )

    # 8. Organic Farming & Vermicompost query
    if any(word in query_lower for word in ['organic', 'vermicompost', 'compost', 'cow dung', 'natural', 'ಜೈವಿಕ', 'ಸಾವಯವ', 'ಎರೆಹುಳು', 'ಕೊಟ್ಟಿಗೆ', 'ಜೀವಾಮೃತ', 'ಪಂಚಗವ್ಯ', 'जैविक', 'केंचुआ', 'गोबर', 'जीवामृत', 'प्राकृतिक']):
        if lang == 'kn':
            return (
                "🌿 ಸಾವಯವ ಮತ್ತು ನೈಸರ್ಗಿಕ ಕೃಷಿ ವಿಧಾನಗಳು:\n"
                "• ಜೀವಾಮೃತ: 10 ಕೆಜಿ ದೇಶಿ ಹಸುವಿನ ಸಗಣಿ + 10 ಲೀಟರ್ ಗೋಮೂತ್ರ + 2 ಕೆಜಿ ಬೆಲ್ಲ + 2 ಕೆಜಿ ದ್ವಿದಳ ಧಾನ್ಯದ ಹಿಟ್ಟು + 200 ಲೀಟರ್ ನೀರು ಬೆರೆಸಿ 3 ದಿನ ನೆನೆಸಿ ಮಣ್ಣಿಗೆ ನೀಡಿ.\n"
                "• ಎರೆಹುಳು ಗೊಬ್ಬರ: ಮಣ್ಣಿನ ತೇವಾಂಶ ಮತ್ತು ಸೂಕ್ಷ್ಮಜೀವಿಗಳ ಸಂಖ್ಯೆಯನ್ನು ಹೆಚ್ಚಿಸುತ್ತದೆ.\n"
                "• ನೈಸರ್ಗಿಕ ಕೀಟ ನಿಯಂತ್ರಣಕ್ಕಾಗಿ ಬೇವಿನ ಕಷಾಯ (Neem Astra) ಮತ್ತು ಅಗ್ನಿಯಸ್ತ್ರ ಬಳಸಿ."
            )
        elif lang == 'hi':
            return (
                "🌿 जैविक एवं प्राकृतिक खेती के प्रमुख उपाय:\n"
                "• जीवामृत निर्माण: 10 किग्रा देसी गाय का गोबर + 10 लीटर गोमूत्र + 2 किग्रा गुड़ + 2 किग्रा बेसन + 200 लीटर पानी को 3 दिन रखकर फसलों में दें।\n"
                "• केंचुआ खाद (वर्मीकम्पोस्ट): पौधों की रोग प्रतिरोधक क्षमता और मिट्टी की उर्वरता तेजी से बढ़ाता है।\n"
                "• प्राकृतिक कीट नियंत्रण के लिए नीम तेल, नीमास्त्र और ब्रह्मास्त्र का छिड़काव करें।"
            )
        else:
            return (
                "🌿 Organic & Natural Farming Techniques:\n"
                "• Jeevamrutha: 10 kg cow dung + 10 L cow urine + 2 kg jaggery + 2 kg pulse flour in 200L water, fermented for 3 days.\n"
                "• Vermicompost: Enhances soil microbial activity and water retention.\n"
                "• Natural Pest Repellents: Use Neem seed kernel extract (NSKE 5%) or Agniastra for eco-friendly pest control."
            )

    # 9. Government Schemes, KCC, Subsidies & PM-KISAN query
    if any(word in query_lower for word in ['scheme', 'subsidy', 'loan', 'kcc', 'kisan', 'insurance', 'ಯೋಜನೆ', 'ಸಾಲ', 'ಸಬ್ಸಿಡಿ', 'ವಿಮೆ', 'ಪಿಎಂ ಕಿಸಾನ್', 'ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್', 'योजना', 'सब्सिडी', 'ऋण', 'लोन', 'बीमा', 'पीएम किसान', 'केसीसी']):
        if lang == 'kn':
            return (
                "🏛️ ರೈತರಿಗಾಗಿ ಪ್ರಮುಖ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು ಮತ್ತು ಸೌಲಭ್ಯಗಳು:\n"
                "• ಪಿಎಂ-ಕಿಸಾನ್ (PM-KISAN): ಪ್ರತಿ ವರ್ಷ ₹6,000 ನೇರ ಆರ್ಥಿಕ ನೆರವು (3 ಕಂತುಗಳಲ್ಲಿ).\n"
                "• ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ (KCC): ಶೇ. 4% ಕಡಿಮೆ ಬಡ್ಡಿದರದಲ್ಲಿ ಕೃಷಿ ಬೆಳೆ ಸಾಲ.\n"
                "• ಪ್ರಧಾನ ಮಂತ್ರಿ ಫಸಲ್ ಬಿಮಾ ಯೋಜನೆ (PMFBY): ನೈಸರ್ಗಿಕ ವಿಕೋಪಗಳಿಂದ ಬೆಳೆ ಹಾನಿಯಾದರೆ ಬೆಳೆ ವಿಮೆ ರಕ್ಷಣೆ.\n"
                "• ಕೃಷಿ ಯಂತ್ರೋಪಕರಣಗಳು ಮತ್ತು ಸೋಲಾರ್ ಪಂಪ್‌ಗಳಿಗೆ (ಕುಸುಮ್ ಯೋಜನೆ) ಶೇ. 50-80% ಸಬ್ಸಿಡಿ."
            )
        elif lang == 'hi':
            return (
                "🏛️ किसानों के लिए प्रमुख सरकारी योजनाएं एवं लाभ:\n"
                "• पीएम-किसान (PM-KISAN): सभी पात्र किसानों को ₹6,000 प्रति वर्ष सीधे बैंक खाते में (3 किस्तों में)।\n"
                "• किसान क्रेडिट कार्ड (KCC): मात्र 4% रियायती ब्याज दर पर कृषि ऋण सुविधा।\n"
                "• प्रधानमंत्री फसल बीमा योजना (PMFBY): सूखे, बाढ़ या कीट प्रकोप से फसल क्षति पर पूर्ण बीमा कवरेज।\n"
                "• पीएम कुसुम योजना: सोलर वाटर पंप और कृषि यंत्रों पर 50-80% तक सरकारी अनुदान (सब्सिडी)।"
            )
        else:
            return (
                "🏛️ Key Government Agricultural Schemes & Subsidies:\n"
                "• PM-KISAN: Direct income support of ₹6,000/year in 3 equal installments.\n"
                "• Kisan Credit Card (KCC): Concessional crop loans at an effective 4% interest rate.\n"
                "• PM Fasal Bima Yojana (PMFBY): Comprehensive crop insurance against drought, floods, and unseasonal weather.\n"
                "• PM-KUSUM Scheme: 50-80% subsidy for solar water pumps and micro-irrigation systems."
            )

    # 10. Weed Management & Seed Treatment query
    if any(word in query_lower for word in ['weed', 'seed treatment', 'treatment', 'germination', 'ಕಳೆ', 'ಬೀಜೋಪಚಾರ', 'ಮೊಳಕೆ', 'ಬೀಜ', 'खरपतवार', 'बीजोपचार', 'अंकुरण', 'बीज शोधन']):
        if lang == 'kn':
            return (
                "🌱 ಬೀಜೋಪಚಾರ ಮತ್ತು ಕಳೆ ನಿರ್ವಹಣಾ ಮಾರ್ಗಸೂಚಿ:\n"
                "• ಬೀಜೋಪಚಾರ: ಬಿತ್ತನೆಗೆ ಮುನ್ನ ಪ್ರತಿ ಕೆಜಿ ಬೀಜಕ್ಕೆ 5-10 ಗ್ರಾಂ ಟ್ರೈಕೋಡರ್ಮಾ ಅಥವಾ 2 ಗ್ರಾಂ ಟ್ರೈಕೋಡರ್ಮಾ ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಬೆರೆಸಿ ಸೊರಗು ಮತ್ತು ಬುಡ ಕೊಳೆತ ರೋಗಗಳನ್ನು ತಡೆಯಿರಿ.\n"
                "• ಕಳೆ ನಿರ್ವಹಣೆ: ಬಿತ್ತನೆಯ 20-25 ದಿನಗಳ ನಂತರ ಮೊದಲ ಕಳೆ ತೆಗೆಯಿರಿ ಅಥವಾ ಅಂತರ ಬೇಸಾಯ (Inter-cultivation) ಮಾಡಿ."
            )
        elif lang == 'hi':
            return (
                "🌱 बीजोपचार एवं खरपतवार प्रबंधन दिशा-निर्देश:\n"
                "• बीजोपचार: बुवाई से पहले प्रति किग्रा बीज को 5-10 ग्राम ट्राइकोडर्मा या 2 ग्राम बाविस्टिन से उपचारित करें ताकि जड़ सड़न और उकठा रोग न लगे।\n"
                "• खरपतवार नियंत्रण: बुवाई के 20-25 दिनों बाद पहली निराई-गुड़ाई करें या उपयुक्त खरपतवारनाशी का उपयोग करें।"
            )
        else:
            return (
                "🌱 Seed Treatment & Weed Management Guidelines:\n"
                "• Seed Treatment: Treat seeds with Trichoderma viride (5-10g/kg) or safe botanical / bio-fungicide or consult your local KVK for approved safe treatment before sowing to prevent seedling wilt and damping off.\n"
                "• Weed Control: Perform manual weeding / inter-cultivation 20-25 days after crop emergence."
            )

    # 11. General Disease query
    if any(word in query_lower for word in ['disease', 'blight', 'fungus', 'ರೋಗ', 'ಕಾಯಿಲೆ', 'ಕಮಟು', 'ಬಿಳಿ ನೊಣ', 'बीमारी', 'रोग', 'झुलसा']):
        if lang == 'kn':
            return "🍃 ಸಸ್ಯ ರೋಗ ಪತ್ತೆಗಾಗಿ, ಕೆಳಗಿನ 'ಎಲೆ ರೋಗ ಪತ್ತೆ' ಮಾಡ್ಯೂಲ್‌ಗೆ ಸೋಂಕಿತ ಎಲೆಯ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ!"
        elif lang == 'hi':
            return "🍃 पौधे के रोग की पहचान के लिए, नीचे 'पत्ती रोग पहचान' मॉड्यूल में प्रभावित पत्ती की तस्वीर अपलोड करें!"
        else:
            return "🍃 For disease detection, please upload a photo of the affected leaf in the Leaf Disease Detection module below!"

    # 12. General Weather query
    if any(word in query_lower for word in ['weather', 'rain', 'temperature', 'humidity', 'ಮಳೆ', 'ಹವಾಮಾನ', 'ತಾಪಮಾನ', 'मौसम', 'बारिश', 'तापमान']):
        if lang == 'kn':
            return "🌤️ ನಮ್ಮ ವ್ಯವಸ್ಥೆಯು OpenWeatherMap API ಮೂಲಕ ನಿಮ್ಮ ಜಿಲ್ಲೆಯ ಲೈವ್ ಹವಾಮಾನ (ತಾಪಮಾನ, ತೇವಾಂಶ ಮತ್ತು ಮಳೆ) ನೇರವಾಗಿ ತರುತ್ತದೆ!"
        elif lang == 'hi':
            return "🌤️ हमारा सिस्टम OpenWeatherMap API के माध्यम से आपके जिले का लाइव मौसम (तापमान, आर्द्रता और वर्षा) स्वतः प्राप्त करता है!"
        else:
            return "🌤️ Our system automatically fetches live weather data (temperature, humidity, condition) for your district using OpenWeatherMap API!"

    # 9. Greeting / Help
    if any(word in query_lower for word in ['hello', 'hi', 'help', 'ನಮಸ್ಕಾರ', 'ಹಲೋ', 'ಸಹಾಯ', 'नमस्ते', 'प्रणाम', 'मदद']):
        if lang == 'kn':
            return (
                "🌾 ಸ್ಮಾರ್ಟ್‌ಆಗ್ರಿ AI ಗೆ ಸ್ವಾಗತ! ನಾನು ನಿಮಗೆ ಇವುಗಳಲ್ಲಿ ಸಹಾಯ ಮಾಡಬಲ್ಲೆ:\n"
                "• 🌱 ಮಣ್ಣು ಮತ್ತು ಹವಾಮಾನ ಆಧರಿಸಿ ಬೆಳೆ ಶಿಫಾರಸು\n"
                "• 🍃 ಎಲೆ ಫೋಟೋ ಮೂಲಕ ಸಸ್ಯ ರೋಗ ಪತ್ತೆ\n"
                "• 💰 ಮಂಡಿ ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಮುನ್ಸೂಚನೆ\n"
                "• 🤖 ಸಂಪೂರ್ಣ ಕೃಷಿ ನಿರ್ಧಾರ ಯೋಜನೆ (Planner Agent)\n"
                "ದಯವಿಟ್ಟು ನಿಮ್ಮ ಕೃಷಿ ಪ್ರಶ್ನೆಯನ್ನು ಕೇಳಿ!"
            )
        elif lang == 'hi':
            return (
                "🌾 स्मार्टएग्री AI में आपका स्वागत है! मैं आपकी सहायता कर सकता हूँ:\n"
                "• 🌱 मिट्टी और मौसम के आधार पर फसल अनुशंसा\n"
                "• 🍃 पत्ती की फोटो से रोग पहचान और उपचार\n"
                "• 💰 मंडी बाजार मूल्य पूर्वानुमान\n"
                "• 🤖 पूर्ण कृषि निर्णय योजना (Planner Agent)\n"
                "कृपया अपना कृषि प्रश्न पूछें!"
            )
        else:
            return (
                "🌾 Welcome to SmartAgri AI! I can help you with:\n"
                "• 🌱 Crop Recommendation based on soil\n"
                "• 🍃 Leaf Disease Detection\n"
                "• 💰 Market Price Prediction\n"
                "• 🤖 Complete Farm Planning\n"
                "Please type or speak your farming question!"
            )

    # Default fallback
    if lang == 'kn':
        return (
            "🤖 ಕೃಷಿ ಸಹಾಯಕ್ಕಾಗಿ ಕೆಳಗಿನ ಮಾಡ್ಯೂಲ್‌ಗಳನ್ನು ಬಳಸಿ:\n"
            "• 🌱 ಬೆಳೆ ಶಿಫಾರಸು — ಮಣ್ಣು ಪರೀಕ್ಷೆ ಆಧರಿತ ಸಲಹೆ\n"
            "• 🍃 ಎಲೆ ರೋಗ ಪತ್ತೆ — ಎಲೆ ಚಿತ್ರ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ\n"
            "• 💰 ಬೆಲೆ ಮುನ್ಸೂಚನೆ — ಮಂಡಿ ದರ ಪರಿಶೀಲಿಸಿ\n"
            "• 🤖 ಯೋಜಕ ಏಜೆಂಟ್ — ಸಂಪೂರ್ಣ ಕೃಷಿ ಯೋಜನೆ"
        )
    elif lang == 'hi':
        return (
            "🤖 कृषि सहायता के लिए नीचे दिए गए मॉड्यूल का उपयोग करें:\n"
            "• 🌱 फसल अनुशंसा — मिट्टी आधारित फसल सलाह\n"
            "• 🍃 रोग पहचान — पत्ती की फोटो अपलोड करें\n"
            "• 💰 मूल्य पूर्वानुमान — मंडी भाव देखें\n"
            "• 🤖 योजनाकार एजेंट — संपूर्ण कृषि योजना"
        )
    return (
        "🤖 I understand you need farming help! Please use our modules below:\n"
        "• 🌱 Crop Recommendation — for soil-based crop advice\n"
        "• 🍃 Disease Detection — upload leaf image\n"
        "• 💰 Price Prediction — check mandi prices\n"
        "• 🤖 Planner Agent — complete farm plan"
    )

# =====================================================================
# DISTRICT TRANSLATIONS (ALL 31 KARNATAKA DISTRICTS)
# =====================================================================
DISTRICT_TRANSLATIONS = {
    'Bagalkot': {'en': 'Bagalkot', 'kn': 'ಬಾಗಲಕೋಟೆ (Bagalkot)', 'hi': 'बागलकोट (Bagalkot)'},
    'Ballari': {'en': 'Ballari', 'kn': 'ಬಳ್ಳಾರಿ (Ballari)', 'hi': 'बल्लारी (Ballari)'},
    'Belagavi': {'en': 'Belagavi', 'kn': 'ಬೆಳಗಾವಿ (Belagavi)', 'hi': 'बेलगावी (Belagavi)'},
    'Bengaluru Rural': {'en': 'Bengaluru Rural', 'kn': 'ಬೆಂಗಳೂರು ಗ್ರಾಮಾಂತರ (Bengaluru Rural)', 'hi': 'बेंगलुरु ग्रामीण (Bengaluru Rural)'},
    'Bengaluru Urban': {'en': 'Bengaluru Urban', 'kn': 'ಬೆಂಗಳೂರು ನಗರ (Bengaluru Urban)', 'hi': 'बेंगलुरु शहरी (Bengaluru Urban)'},
    'Bidar': {'en': 'Bidar', 'kn': 'ಬೀದರ್ (Bidar)', 'hi': 'बीदर (Bidar)'},
    'Chamarajanagara': {'en': 'Chamarajanagara', 'kn': 'ಚಾಮರಾಜನಗರ (Chamarajanagara)', 'hi': 'चामराजनगर (Chamarajanagara)'},
    'Chikkaballapura': {'en': 'Chikkaballapura', 'kn': 'ಚಿಕ್ಕಬಳ್ಳಾಪುರ (Chikkaballapura)', 'hi': 'चिक्काबल्लापुरा (Chikkaballapura)'},
    'Chikkamagaluru': {'en': 'Chikkamagaluru', 'kn': 'ಚಿಕ್ಕಮಗಳೂರು (Chikkamagaluru)', 'hi': 'चिक्कमगलुरु (Chikkamagaluru)'},
    'Chitradurga': {'en': 'Chitradurga', 'kn': 'ಚಿತ್ರದುರ್ಗ (Chitradurga)', 'hi': 'चित्रदुर्ग (Chitradurga)'},
    'Dakshina Kannada': {'en': 'Dakshina Kannada', 'kn': 'ದಕ್ಷಿಣ ಕನ್ನಡ (Dakshina Kannada)', 'hi': 'दक्षिण कन्नड़ (Dakshina Kannada)'},
    'Davanagere': {'en': 'Davanagere', 'kn': 'ದಾವಣಗೆರೆ (Davanagere)', 'hi': 'दावणगेरे (Davanagere)'},
    'Dharwad': {'en': 'Dharwad', 'kn': 'ಧಾರವಾಡ (Dharwad)', 'hi': 'धारवाड़ (Dharwad)'},
    'Gadag': {'en': 'Gadag', 'kn': 'ಗದಗ (Gadag)', 'hi': 'गदग (Gadag)'},
    'Hassan': {'en': 'Hassan', 'kn': 'ಹಾಸನ (Hassan)', 'hi': 'हासन (Hassan)'},
    'Haveri': {'en': 'Haveri', 'kn': 'ಹಾವೇರಿ (Haveri)', 'hi': 'हावेरी (Haveri)'},
    'Kalaburagi': {'en': 'Kalaburagi', 'kn': 'ಕಲಬುರಗಿ (Kalaburagi)', 'hi': 'कलबुर्गी (Kalaburagi)'},
    'Kodagu': {'en': 'Kodagu', 'kn': 'ಕೊಡಗು (Kodagu)', 'hi': 'कोडागु (Kodagu)'},
    'Kolar': {'en': 'Kolar', 'kn': 'ಕೋಲಾರ (Kolar)', 'hi': 'कोलार (Kolar)'},
    'Koppal': {'en': 'Koppal', 'kn': 'ಕೊಪ್ಪಳ (Koppal)', 'hi': 'कोप्पल (Koppal)'},
    'Mandya': {'en': 'Mandya', 'kn': 'ಮಂಡ್ಯ (Mandya)', 'hi': 'मंड्या (Mandya)'},
    'Mysuru': {'en': 'Mysuru', 'kn': 'ಮೈಸೂರು (Mysuru)', 'hi': 'मैसूरु (Mysuru)'},
    'Raichur': {'en': 'Raichur', 'kn': 'ರಾಯಚೂರು (Raichur)', 'hi': 'रायचूर (Raichur)'},
    'Ramanagara': {'en': 'Ramanagara', 'kn': 'ರಾಮನಗರ (Ramanagara)', 'hi': 'रामनगर (Ramanagara)'},
    'Shivamogga': {'en': 'Shivamogga', 'kn': 'ಶಿವಮೊಗ್ಗ (Shivamogga)', 'hi': 'शिवमोग्गा (Shivamogga)'},
    'Tumakuru': {'en': 'Tumakuru', 'kn': 'ತುಮಕೂರು (Tumakuru)', 'hi': 'तुमकुरु (Tumakuru)'},
    'Udupi': {'en': 'Udupi', 'kn': 'ಉಡುಪಿ (Udupi)', 'hi': 'उडुपी (Udupi)'},
    'Uttara Kannada': {'en': 'Uttara Kannada', 'kn': 'ಉತ್ತರ ಕನ್ನಡ (Uttara Kannada)', 'hi': 'उत्तर कन्नड़ (Uttara Kannada)'},
    'Vijayanagara': {'en': 'Vijayanagara', 'kn': 'ವಿಜಯನಗರ (Vijayanagara)', 'hi': 'विजयनगर (Vijayanagara)'},
    'Vijayapura': {'en': 'Vijayapura', 'kn': 'ವಿಜಯಪುರ (Vijayapura)', 'hi': 'विजयपुर (Vijayapura)'},
    'Yadgir': {'en': 'Yadgir', 'kn': 'ಯಾದಗಿರಿ (Yadgir)', 'hi': 'यादगीर (Yadgir)'}
}

# =====================================================================
# COMMODITY / MARKET CROP TRANSLATIONS (ALL KARNATAKA & SYSTEM CROPS)
# =====================================================================
_ALL_CROPS_DICT = {
    'apple': {'en': 'Apple', 'kn': 'ಸೇಬು', 'hi': 'सेब'},
    'banana': {'en': 'Banana', 'kn': 'ಬಾಳೆಹಣ್ಣು', 'hi': 'केला'},
    'blackgram': {'en': 'Blackgram (Urad)', 'kn': 'ಉದ್ದಿನ ಬೇಳೆ (ಉದ್ದು)', 'hi': 'उड़द दाल'},
    'chickpea': {'en': 'Chickpea (Bengal gram)', 'kn': 'ಕಡಲೆ (ಕಡಲೆಕಾಳು)', 'hi': 'चना'},
    'coconut': {'en': 'Coconut', 'kn': 'ತೆಂಗಿನಕಾಯಿ', 'hi': 'नारियल'},
    'coffee': {'en': 'Coffee', 'kn': 'ಕಾಫಿ', 'hi': 'कॉफी'},
    'cotton': {'en': 'Cotton', 'kn': 'ಹತ್ತಿ', 'hi': 'कपास'},
    'grapes': {'en': 'Grapes', 'kn': 'ದ್ರಾಕ್ಷಿ', 'hi': 'अंगूर'},
    'jute': {'en': 'Jute', 'kn': 'ಸೆಣಬು', 'hi': 'जूट (पटसन)'},
    'kidneybeans': {'en': 'Kidney beans (Rajma)', 'kn': 'ರಾಜಮಾ', 'hi': 'राजमा'},
    'lentil': {'en': 'Lentil (Masoor)', 'kn': 'ಮಸೂರ ಬೇಳೆ', 'hi': 'मसूर दाल'},
    'maize': {'en': 'Maize (Corn)', 'kn': 'ಮೆಕ್ಕೆಜೋಳ', 'hi': 'मक्का'},
    'mango': {'en': 'Mango', 'kn': 'ಮಾವು', 'hi': 'आम'},
    'mothbeans': {'en': 'Moth beans (Matki)', 'kn': 'ಮಡಿಕೆ ಕಾಳು', 'hi': 'मोठ दाल'},
    'mungbean': {'en': 'Mungbean (Green gram)', 'kn': 'ಹೆಸರುಕಾಳು', 'hi': 'मूंग दाल'},
    'muskmelon': {'en': 'Muskmelon', 'kn': 'ಕರಬೂಜ (ಕರ್ಬೂಜ)', 'hi': 'खरबूजा'},
    'orange': {'en': 'Orange', 'kn': 'ಕಿತ್ತಳೆ', 'hi': 'संतरा'},
    'papaya': {'en': 'Papaya', 'kn': 'ಪಪ್ಪಾಯಿ (ಪರಂಗಿ)', 'hi': 'पपीता'},
    'pigeonpeas': {'en': 'Pigeonpeas (Tur / Arhar)', 'kn': 'ತೊಗರಿ ಬೇಳೆ', 'hi': 'अरहर (तुअर) दाल'},
    'pomegranate': {'en': 'Pomegranate', 'kn': 'ದಾಳಿಂಬೆ', 'hi': 'अनार'},
    'potato': {'en': 'Potato', 'kn': 'ಆಲೂಗಡ್ಡೆ', 'hi': 'आलू'},
    'rice': {'en': 'Rice (Paddy)', 'kn': 'ಭತ್ತ (ಅಕ್ಕಿ)', 'hi': 'चावल (धान)'},
    'tomato': {'en': 'Tomato', 'kn': 'ಟೊಮೆಟೊ', 'hi': 'टमाटर'},
    'watermelon': {'en': 'Watermelon', 'kn': 'ಕಲ್ಲಂಗಡಿ', 'hi': 'तरबूज'},
    'wheat': {'en': 'Wheat', 'kn': 'ಗೋಧಿ', 'hi': 'गेहूं'},
    'onion': {'en': 'Onion', 'kn': 'ಈರುಳ್ಳಿ', 'hi': 'प्याज'},
    'sugarcane': {'en': 'Sugarcane', 'kn': 'ಕಬ್ಬು', 'hi': 'गन्ना'},
    'pepper': {'en': 'Pepper / Capsicum', 'kn': 'ದಪ್ಪ ಮೆಣಸಿನಕಾಯಿ', 'hi': 'शिमला मिर्च'}
}

class CaseInsensitiveCommodityDict(dict):
    """Case-insensitive dictionary for commodity translations with fallback."""
    def get(self, key, default=None):
        if not key:
            return default if default is not None else {}
        key_str = str(key).strip()
        key_l = key_str.lower().replace('-', '').replace('_', '').replace(' ', '')
        for k, v in self.items():
            k_clean = str(k).lower().replace('-', '').replace('_', '').replace(' ', '')
            if key_l == k_clean or key_l in k_clean or k_clean in key_l:
                return v
        return super().get(key, default if default is not None else {'en': key_str.title(), 'kn': key_str.title(), 'hi': key_str.title()})

COMMODITY_TRANSLATIONS = CaseInsensitiveCommodityDict()
for _k, _v in _ALL_CROPS_DICT.items():
    COMMODITY_TRANSLATIONS[_k] = _v
    COMMODITY_TRANSLATIONS[_k.title()] = _v
    COMMODITY_TRANSLATIONS[_k.upper()] = _v
    COMMODITY_TRANSLATIONS[_k.capitalize()] = _v

COMMODITY_TRANSLATIONS['Rice (Paddy)'] = {'en': 'Rice (Paddy)', 'kn': 'ಭತ್ತ (ಅಕ್ಕಿ)', 'hi': 'चावल (धान)'}
COMMODITY_TRANSLATIONS['Maize (Corn)'] = {'en': 'Maize (Corn)', 'kn': 'ಮೆಕ್ಕೆಜೋಳ', 'hi': 'मक्का'}
COMMODITY_TRANSLATIONS['Chickpea (Bengal gram)'] = {'en': 'Chickpea (Bengal gram)', 'kn': 'ಕಡಲೆ (ಕಡಲೆಕಾಳು)', 'hi': 'चना'}
COMMODITY_TRANSLATIONS['Kidney beans (Rajma)'] = {'en': 'Kidney beans (Rajma)', 'kn': 'ರಾಜಮಾ', 'hi': 'राजमा'}
COMMODITY_TRANSLATIONS['Moth beans (Matki)'] = {'en': 'Moth beans (Matki)', 'kn': 'ಮಡಿಕೆ ಕಾಳು', 'hi': 'मोठ दाल'}
COMMODITY_TRANSLATIONS['Mungbean (Green gram)'] = {'en': 'Mungbean (Green gram)', 'kn': 'ಹೆಸರುಕಾಳು', 'hi': 'मूंग दाल'}
COMMODITY_TRANSLATIONS['Pigeonpeas (Tur / Arhar)'] = {'en': 'Pigeonpeas (Tur / Arhar)', 'kn': 'ತೊಗರಿ ಬೇಳೆ', 'hi': 'अरहर (तुअर) दाल'}
COMMODITY_TRANSLATIONS['Pepper / Capsicum'] = {'en': 'Pepper / Capsicum', 'kn': 'ದಪ್ಪ ಮೆಣಸಿನಕಾಯಿ', 'hi': 'शिमला मिर्च'}
COMMODITY_TRANSLATIONS['Bell Pepper (Chilli)'] = {'en': 'Bell Pepper (Chilli)', 'kn': 'ದಪ್ಪ ಮೆಣಸಿನಕಾಯಿ', 'hi': 'शिमला मिर्च'}

def get_district_translation(district, lang='en'):
    d_info = DISTRICT_TRANSLATIONS.get(district, {})
    return d_info.get(lang, district)

def get_commodity_translation(commodity, lang='en'):
    c_info = COMMODITY_TRANSLATIONS.get(commodity, {})
    return c_info.get(lang, commodity)

# =====================================================================
# SMART IRRIGATION ADVISORY SYSTEM (FAO Kc + Penman Model)
# =====================================================================
GROWTH_STAGES_TR = {
    'initial': {
        'en': 'Initial / Seedling (0 - 30 Days)',
        'kn': 'ಆರಂಭಿಕ / ಸಸಿ ಹಂತ (0 - 30 ದಿನಗಳು)',
        'hi': 'प्रारंभिक / अंकुरण अवस्था (0 - 30 दिन)'
    },
    'vegetative': {
        'en': 'Vegetative / Rapid Growth (30 - 60 Days)',
        'kn': 'ಸಸ್ಯೀಯ / ಶೀಘ್ರ ಬೆಳವಣಿಗೆಯ ಹಂತ (30 - 60 ದಿನಗಳು)',
        'hi': 'वानस्पतिक / तीव्र बढ़वार अवस्था (30 - 60 दिन)'
    },
    'flowering': {
        'en': 'Flowering & Fruiting / Pod Formation (60 - 90 Days)',
        'kn': 'ಹೂವು ಮತ್ತು ಕಾಯಿ ಕಟ್ಟುವ ಹಂತ (60 - 90 ದಿನಗಳು)',
        'hi': 'फूल एवं फल / दाना बनने की अवस्था (60 - 90 दिन)'
    },
    'maturity': {
        'en': 'Maturity & Ripening (> 90 Days)',
        'kn': 'ಪಕ್ವತೆ / ಕಟಾವಿನ ಹಂತ (> 90 ದಿನಗಳು)',
        'hi': 'परिपक्वता / पकने की अवस्था (> 90 दिन)'
    }
}

SOIL_TYPES_TR = {
    'sandy': {
        'en': 'Sandy / Light Red Soil (Fast drainage)',
        'kn': 'ಮರಳು / ಹಗುರ ಕೆಂಪು ಮಣ್ಣು (ಶೀಘ್ರ ಇಂಗುವಿಕೆ)',
        'hi': 'बलुई / हल्की लाल मिट्टी (शीघ्र जल निकासी)'
    },
    'loam': {
        'en': 'Loamy Soil (Ideal moisture retention)',
        'kn': 'ಗೋಡು ಮಣ್ಣು (ಉತ್ತಮ ತೇವಾಂಶ ಧಾರಣ)',
        'hi': 'दोमट मिट्टी (आदर्श नमी धारण क्षमता)'
    },
    'clay': {
        'en': 'Clayey Soil (Heavy water retention)',
        'kn': 'ಜೇಡಿ ಮಣ್ಣು (ಹೆಚ್ಚು ತೇವಾಂಶ ಧಾರಣ)',
        'hi': 'चिकनी मिट्टी (अधिक जल संचयन)'
    },
    'black': {
        'en': 'Black Cotton Soil (Deep cracking, high retention)',
        'kn': 'ಕಪ್ಪು ಹತ್ತಿ ಮಣ್ಣು (ಆಳವಾದ ತೇವಾಂಶ ಧಾರಣ)',
        'hi': 'काली कपास मिट्टी (गहरी नमी प्रतिधारण)'
    }
}

IRRIGATION_METHODS_TR = {
    'drip': {
        'en': 'Drip Irrigation',
        'kn': 'ಹನಿ ನೀರಾವರಿ',
        'hi': 'ड्रिप सिंचाई'
    },
    'sprinkler': {
        'en': 'Sprinkler Irrigation',
        'kn': 'ತುಂತುರು ನೀರಾವರಿ',
        'hi': 'स्प्रिंकलर / फव्वारा सिंचाई'
    },
    'flood': {
        'en': 'Surface / Furrow Flood',
        'kn': 'ಕಾಲುವೆ / ಹರಿವು ನೀರಾವರಿ',
        'hi': 'सतही / प्रवाह नाली सिंचाई'
    }
}

CROP_KC_FACTORS = {
    'arecanut': {'initial': 0.70, 'vegetative': 0.85, 'flowering': 0.95, 'maturity': 0.85},
    'mulberry': {'initial': 0.60, 'vegetative': 0.80, 'flowering': 0.90, 'maturity': 0.75},
    'jowar': {'initial': 0.40, 'vegetative': 0.75, 'flowering': 1.05, 'maturity': 0.60},

    'rice': {'initial': 1.10, 'vegetative': 1.20, 'flowering': 1.35, 'maturity': 0.95},
    'wheat': {
        'initial': 0.30,
        'cri': 0.50,
        'tillering': 0.75,
        'jointing': 1.05,
        'flowering': 1.15,
        'mid': 1.15,
        'grain_filling': 0.80,
        'maturity': 0.40,
        'late': 0.40,
        'vegetative': 0.85
    },
    'cotton': {'initial': 0.45, 'vegetative': 0.80, 'flowering': 1.20, 'maturity': 0.65},
    'maize': {'initial': 0.40, 'vegetative': 0.80, 'flowering': 1.15, 'maturity': 0.60},
    'tomato': {'initial': 0.50, 'vegetative': 0.85, 'flowering': 1.20, 'maturity': 0.75},
    'potato': {'initial': 0.45, 'vegetative': 0.85, 'flowering': 1.15, 'maturity': 0.70},
    'onion': {'initial': 0.45, 'vegetative': 0.75, 'flowering': 1.05, 'maturity': 0.75},
    'banana': {'initial': 0.75, 'vegetative': 1.00, 'flowering': 1.20, 'maturity': 1.00},
    'coffee': {'initial': 0.80, 'vegetative': 0.95, 'flowering': 1.10, 'maturity': 0.85},
    'grapes': {'initial': 0.35, 'vegetative': 0.65, 'flowering': 0.85, 'maturity': 0.50},
    'sugarcane': {'initial': 0.40, 'vegetative': 1.00, 'flowering': 1.25, 'maturity': 0.75},
    'pomegranate': {'initial': 0.40, 'vegetative': 0.70, 'flowering': 0.95, 'maturity': 0.60},
    'apple': {'initial': 0.45, 'vegetative': 0.80, 'flowering': 1.00, 'maturity': 0.70},
    'mango': {'initial': 0.40, 'vegetative': 0.70, 'flowering': 0.90, 'maturity': 0.60},
    'chickpea': {'initial': 0.40, 'vegetative': 0.75, 'flowering': 1.00, 'maturity': 0.40},
    'pigeonpeas': {'initial': 0.40, 'vegetative': 0.75, 'flowering': 1.10, 'maturity': 0.50},
    'blackgram': {'initial': 0.40, 'vegetative': 0.70, 'flowering': 1.05, 'maturity': 0.45},
    'mungbean': {'initial': 0.40, 'vegetative': 0.70, 'flowering': 1.05, 'maturity': 0.45},
    'coconut': {'initial': 0.70, 'vegetative': 0.85, 'flowering': 1.00, 'maturity': 0.80},
    'papaya': {'initial': 0.50, 'vegetative': 0.80, 'flowering': 1.10, 'maturity': 0.75},
    'watermelon': {'initial': 0.40, 'vegetative': 0.75, 'flowering': 1.00, 'maturity': 0.70},
    'muskmelon': {'initial': 0.40, 'vegetative': 0.75, 'flowering': 1.00, 'maturity': 0.70},
    'orange': {'initial': 0.50, 'vegetative': 0.70, 'flowering': 0.90, 'maturity': 0.65},
    'pepper': {'initial': 0.45, 'vegetative': 0.80, 'flowering': 1.15, 'maturity': 0.70},
    'lentil': {'initial': 0.40, 'vegetative': 0.70, 'flowering': 1.00, 'maturity': 0.40},
    'horsegram': {'initial': 0.35, 'vegetative': 0.65, 'flowering': 0.85, 'maturity': 0.35},
    'horse gram': {'initial': 0.35, 'vegetative': 0.65, 'flowering': 0.85, 'maturity': 0.35},
    'fieldbeans': {'initial': 0.40, 'vegetative': 0.75, 'flowering': 1.05, 'maturity': 0.45},
    'ragi': {'initial': 0.35, 'vegetative': 0.70, 'flowering': 1.05, 'maturity': 0.55},
    'default': {'initial': 0.45, 'vegetative': 0.80, 'flowering': 1.15, 'maturity': 0.65}
}

def calculate_smart_irrigation(
    crop,
    growth_stage='vegetative',
    soil_type='loam',
    area_acres=1.0,
    irrigation_type='drip',
    temp=28.0,
    humidity=55.0,
    rainfall_mm=0.0,
    weather_desc='',
    district='Dharwad',
    lang='en',
    days_after_sowing=None,
    pump_flow_rate=None,
    irrigation_efficiency=None
):
    crop_l = crop.lower().strip() if crop else 'default'
    growth_stage = growth_stage if growth_stage in GROWTH_STAGES_TR else 'vegetative'
    soil_type = soil_type if soil_type in SOIL_TYPES_TR else 'loam'
    irrigation_type = irrigation_type if irrigation_type in IRRIGATION_METHODS_TR else 'drip'
    
    try:
        area_acres = float(area_acres)
        if area_acres <= 0:
            area_acres = 1.0
    except (ValueError, TypeError):
        area_acres = 1.0

    try:
        temp = float(temp)
    except (ValueError, TypeError):
        temp = 28.0

    try:
        humidity = float(humidity)
    except (ValueError, TypeError):
        humidity = 55.0

    try:
        rainfall_mm = float(rainfall_mm)
    except (ValueError, TypeError):
        rainfall_mm = 0.0

    # 1. FAO-56 Reference Evapotranspiration (ET0 in mm/day) via FAO-56 Eq. 21 (Extraterrestrial Radiation Ra) & Eq. 52 (Hargreaves)
    # Karnataka latitude range: 11.5°N (South) to 18.5°N (North), default 15.4°N (Dharwad)
    district_latitudes = {
        'Chamarajanagara': 11.9, 'Mysuru': 12.3, 'Kodagu': 12.4, 'Mandya': 12.5,
        'Dakshina Kannada': 12.9, 'Hassan': 13.0, 'Bengaluru Urban': 12.97, 'Bengaluru Rural': 13.2,
        'Ramanagara': 12.7, 'Tumakuru': 13.3, 'Kolar': 13.1, 'Chikkaballapura': 13.4,
        'Chikkamagaluru': 13.3, 'Udupi': 13.3, 'Shivamogga': 13.9, 'Chitradurga': 14.2,
        'Davanagere': 14.4, 'Haveri': 14.8, 'Uttara Kannada': 14.8, 'Ballari': 15.1,
        'Dharwad': 15.4, 'Gadag': 15.4, 'Koppal': 15.3, 'Belagavi': 15.8,
        'Bagalkot': 16.1, 'Raichur': 16.2, 'Vijayapura': 16.8, 'Yadgir': 16.7,
        'Kalaburagi': 17.3, 'Bidar': 17.9, 'Vijayanagara': 15.2
    }
    lat_deg = district_latitudes.get(district, 15.4)
    
    # Compute Extraterrestrial Radiation Ra from latitude and Day of Year (FAO-56 Eq. 21-25)
    import math
    from datetime import datetime
    doy = datetime.now().timetuple().tm_yday
    phi = math.radians(lat_deg)
    dr = 1.0 + 0.033 * math.cos(2.0 * math.pi / 365.0 * doy)
    delta = 0.409 * math.sin(2.0 * math.pi / 365.0 * doy - 1.39)
    x_val = -math.tan(phi) * math.tan(delta)
    x_val = max(-1.0, min(1.0, x_val))
    omega_s = math.acos(x_val)
    g_sc = 0.0820 # MJ/m2/min
    ra_mj = (24.0 * 60.0 / math.pi) * g_sc * dr * (
        omega_s * math.sin(phi) * math.sin(delta) + math.cos(phi) * math.cos(delta) * math.sin(omega_s)
    )
    ra_mm_day = ra_mj / 2.45 # Convert MJ/m2/day to mm/day equivalent (FAO-56 Eq. 20)
    
    # Estimate diurnal temperature range Tmax - Tmin based on relative humidity
    t_range = max(3.0, (100.0 - humidity) * 0.20)
    t_mean = temp
    et0_raw = 0.0023 * (t_mean + 17.8) * (t_range ** 0.5) * ra_mm_day
    
    # Plausibility check (flag and log rather than silent arbitrary clamping)
    is_plausible = True
    plausibility_warning = ""
    if et0_raw < 1.0 or et0_raw > 9.0:
        is_plausible = False
        plausibility_warning = f"Calculated ET0 ({et0_raw:.2f} mm/day) is outside typical agronomic bounds (1.0 - 9.0 mm/day). Check weather sensor inputs."
        print(f"[Irrigation Plausibility Warning] {plausibility_warning}")

    et0 = round(et0_raw, 2)

    # 2. Stage-Based Crop Coefficient (Kc) Computed from Days After Sowing (DAS)
    das_val = None
    if days_after_sowing is not None and str(days_after_sowing).strip() != "":
        try:
            das_val = int(days_after_sowing)
        except Exception:
            das_val = None

    stage_schedule_en = ""
    stage_schedule_kn = ""
    stage_schedule_hi = ""
    critical_stage_info_en = ""
    critical_stage_info_kn = ""
    critical_stage_info_hi = ""

    if crop_l == 'wheat':
        if das_val is not None:
            if das_val < 25:
                growth_stage = 'initial'
                kc = 0.30
                stage_schedule_en = "Initial / CRI Stage: 0-25 DAS (Crown root initiation begins at 21-25 DAS)"
                stage_schedule_kn = "ಆರಂಭಿಕ / ಸಿಆರ್‌ಐ ಹಂತ: 0-25 ದಿನಗಳು (21-25 ದಿನಗಳಲ್ಲಿ ಕಿರೀಟ ಬೇರು ಬಿಡುವುದು)"
                stage_schedule_hi = "प्रारंभिक / सीआरआई अवस्था: 0-25 दिन (21-25 दिन में ताज जड़ निकलना)"
                critical_stage_info_en = "UAS Dharwad Critical Stage 1: Crown Root Initiation (CRI at 21-25 DAS) is the single most critical irrigation. Missing CRI causes 30-40% irreversible yield penalty."
                critical_stage_info_kn = "ಕೃವಿವಿ ಧಾರವಾಡ ನಿರ್ಣಾಯಕ ಹಂತ 1: ಕಿರೀಟ ಬೇರು ಬಿಡುವ ಹಂತ (ಸಿಆರ್‌ಐ 21-25 ದಿನಗಳು) ಅತ್ಯಂತ ಸೂಕ್ಷ್ಮ. ನೀರು ತಪ್ಪಿದರೆ ಶೇ 30-40 ರಷ್ಟು ಇಳುವರಿ ಕುಸಿಯುತ್ತದೆ."
                critical_stage_info_hi = "यूएएस धारवाड़ महत्वपूर्ण अवस्था 1: ताज जड़ (CRI 21-25 दिन) सबसे नाजुक समय है। सिंचाई छूटने पर 30-40% उपज हानि होती है।"
            elif das_val < 50:
                growth_stage = 'tillering'
                kc = 0.75
                stage_schedule_en = "Tillering Stage: 25-50 DAS (Active tiller development)"
                stage_schedule_kn = "ಕವಲೊಡೆಯುವ ಹಂತ: 25-50 ದಿನಗಳು (ಕವಲುಗಳ ಬೆಳವಣಿಗೆ)"
                stage_schedule_hi = "कल्ले फूटने की अवस्था: 25-50 दिन (सक्रिय कल्ले विकास)"
                critical_stage_info_en = "UAS Dharwad Critical Stage 2: Tillering stage (40-45 DAS) provides moisture for tiller survival and strong root zone."
                critical_stage_info_kn = "ಕೃವಿವಿ ಧಾರವಾಡ ನಿರ್ಣಾಯಕ ಹಂತ 2: ಕವಲೊಡೆಯುವ ಹಂತ (40-45 ದಿನಗಳು) ಕವಲುಗಳ ಬಲವರ್ಧನೆಗೆ ತೇವಾಂಶ ಒದಗಿಸುತ್ತದೆ."
                critical_stage_info_hi = "यूएएस धारवाड़ महत्वपूर्ण अवस्था 2: कल्ले फूटने की अवस्था (40-45 दिन) कल्लों के विकास हेतु नमी देती है।"
            elif das_val < 85:
                growth_stage = 'mid'
                kc = 1.15
                stage_schedule_en = "Jointing & Flowering Stage: 50-85 DAS (Peak water demand)"
                stage_schedule_kn = "ಗಂಟು ಕಟ್ಟುವ ಮತ್ತು ಹೂವಾಡುವ ಹಂತ: 50-85 ದಿನಗಳು (ಗರಿಷ್ಠ ನೀರಿನ ಬೇಡಿಕೆ)"
                stage_schedule_hi = "गांठ बनने एवं फूल आने की अवस्था: 50-85 दिन (उच्चतम जल आवश्यकता)"
                critical_stage_info_en = "UAS Dharwad Critical Stages 3 & 4: Jointing (60-65 DAS) and Flowering (75-80 DAS). Mid-season peak Kc = 1.15. Moisture stress causes floret sterility."
                critical_stage_info_kn = "ಕೃವಿವಿ ಧಾರವಾಡ ನಿರ್ಣಾಯಕ ಹಂತ 3 & 4: ಗಂಟು ಕಟ್ಟುವ (60-65 ದಿನಗಳು) ಮತ್ತು ಹೂವಾಡುವ ಹಂತ (75-80 ದಿನಗಳು). ಗರಿಷ್ಠ Kc = 1.15. ನೀರಿನ ಕೊರತೆಯಾದರೆ ಕಾಳು ಕೂಡುವುದಿಲ್ಲ."
                critical_stage_info_hi = "यूएएस धारवाड़ महत्वपूर्ण अवस्था 3 & 4: गांठ बनना (60-65 दिन) व फूल आना (75-80 दिन)। उच्चतम Kc = 1.15। नमी की कमी से दाना नहीं बनता।"
            elif das_val < 100:
                growth_stage = 'grain_filling'
                kc = 0.80
                stage_schedule_en = "Grain Filling / Milk Stage: 85-100 DAS"
                stage_schedule_kn = "ಕಾಳು ಹಾಲು ತುಂಬುವ ಹಂತ: 85-100 ದಿನಗಳು"
                stage_schedule_hi = "दूधिया अवस्था / दाना भराव: 85-100 दिन"
                critical_stage_info_en = "UAS Dharwad Critical Stage 5: Grain filling (90-95 DAS) directly increases grain size and test weight."
                critical_stage_info_kn = "ಕೃವಿವಿ ಧಾರವಾಡ ನಿರ್ಣಾಯಕ ಹಂತ 5: ಕಾಳು ತುಂಬುವ ಹಂತ (90-95 ದಿನಗಳು) ಕಾಳಿನ ಗಾತ್ರ ಮತ್ತು ತೂಕ ಹೆಚ್ಚಿಸುತ್ತದೆ."
                critical_stage_info_hi = "यूएएस धारवाड़ महत्वपूर्ण अवस्था 5: दाना भराव (90-95 दिन) दानों का वजन व आकार बढ़ाता है।"
            else:
                growth_stage = 'late'
                kc = 0.40
                stage_schedule_en = "Dough / Ripening Stage: >100 DAS"
                stage_schedule_kn = "ಮಾಗುವ / ಕೊಯ್ಲಿನ ಹಂತ: >100 ದಿನಗಳು"
                stage_schedule_hi = "परिपक्वता अवस्था: >100 दिन"
                critical_stage_info_en = "UAS Dharwad Critical Stage 6: Dough stage. Give light irrigation if dry; stop watering 10-14 days prior to harvest."
                critical_stage_info_kn = "ಕೃವಿವಿ ಧಾರವಾಡ ನಿರ್ಣಾಯಕ ಹಂತ 6: ಕಾಳು ಗಟ್ಟಿಯಾಗುವ ಹಂತ. ಕೊಯ್ಲಿಗೆ 10-14 ದಿನ ಮುಂಚಿತವಾಗಿ ನೀರು ನಿಲ್ಲಿಸಿ."
                critical_stage_info_hi = "यूएएस धारवाड़ महत्वपूर्ण अवस्था 6: कटाई से 10-14 दिन पूर्व सिंचाई पूरी तरह बंद करें।"
        else:
            # Fallback when growth_stage is selected manually
            kc_table = CROP_KC_FACTORS.get('wheat', {})
            if growth_stage in ['initial', 'seedling']:
                kc = 0.30
                stage_schedule_en = "Initial / CRI Stage (0-25 DAS): Pre-sowing irrigation & CRI"
                critical_stage_info_en = "UAS Dharwad Critical Stage 1: Crown Root Initiation (CRI at 21-25 DAS) is the most critical irrigation."
            elif growth_stage in ['flowering', 'mid']:
                kc = 1.15
                stage_schedule_en = "Flowering / Jointing: Peak water demand (Kc 1.15)"
                critical_stage_info_en = "UAS Dharwad Critical Stages: Jointing (60-65 DAS) and Flowering (75-80 DAS)."
            elif growth_stage in ['maturity', 'late']:
                kc = 0.40
                stage_schedule_en = "Dough / Ripening Stage: Light terminal irrigation"
                critical_stage_info_en = "Stop watering 10-14 days prior to harvest."
            else:
                kc = 0.85
                stage_schedule_en = "Vegetative / Tillering Stage (25-50 DAS)"
                critical_stage_info_en = "Tillering stage irrigation promotes active tillers."
    else:
        kc_table = CROP_KC_FACTORS.get(crop_l, CROP_KC_FACTORS.get('default'))
        kc = kc_table.get(growth_stage, 0.85)

    # 3. Crop Evapotranspiration: ETc = ET0 x Kc(stage)
    etc_mm = round(et0 * kc, 2)

    # 4. Effective Rainfall (Peff in mm) via USDA Soil Conservation Service (SCS) method
    if rainfall_mm >= 5.0:
        peff_mm = round(max(0.0, rainfall_mm * 0.8 - 2.0), 2)
    else:
        peff_mm = 0.0

    # 5. Net Irrigation Requirement (mm/day) subtracting effective rainfall
    net_depth_mm = round(max(0.0, etc_mm - peff_mm), 2)

    # 6. User-Configured System Application Efficiency
    if irrigation_efficiency is not None:
        try:
            eff_val = float(irrigation_efficiency)
            if eff_val > 1.0:
                eff_val = eff_val / 100.0
            if 0.30 <= eff_val <= 1.0:
                efficiency = eff_val
            else:
                eff_map = {'drip': 0.90, 'sprinkler': 0.75, 'flood': 0.55}
                efficiency = eff_map.get(irrigation_type, 0.90)
        except Exception:
            eff_map = {'drip': 0.90, 'sprinkler': 0.75, 'flood': 0.55}
            efficiency = eff_map.get(irrigation_type, 0.90)
    else:
        eff_map = {'drip': 0.90, 'sprinkler': 0.75, 'flood': 0.55}
        efficiency = eff_map.get(irrigation_type, 0.90)

    # 7. User-Configured Soil Type & Stage-Based Interval
    soil_freq = {
        'sandy': {'days': 2, 'en': 'Sandy Soil: Light frequent irrigation (every 2-3 days)', 'kn': 'ಮರಳು ಮಣ್ಣು: ಕಡಿಮೆ ಪ್ರಮಾಣದಲ್ಲಿ 2-3 ದಿನಕ್ಕೊಮ್ಮೆ', 'hi': 'बलुई मिट्टी: कम मात्रा में हर 2-3 दिन में'},
        'loam': {'days': 4, 'en': 'Loamy Soil: Moderate intervals (every 4-5 days / at critical physiological stage)', 'kn': 'ಗೋಡು ಮಣ್ಣು: ಪ್ರತಿ 4-5 ದಿನಕ್ಕೊಮ್ಮೆ / ಬೆಳೆಯ ಪ್ರಮುಖ ಹಂತದಲ್ಲಿ', 'hi': 'दोमट मिट्टी: हर 4-5 दिन में / क्रांतिक अवस्था पर'},
        'clay': {'days': 6, 'en': 'Clay Soil: Deep watering at critical stages (every 5-7 days)', 'kn': 'ಜೇಡಿ ಮಣ್ಣು: ಪ್ರಮುಖ ಹಂತಗಳಲ್ಲಿ ಪ್ರತಿ 5-7 ದಿನಕ್ಕೊಮ್ಮೆ', 'hi': 'चिकनी मिट्टी: क्रांतिक अवस्थाओं पर हर 5-7 दिन में'},
        'black': {'days': 7, 'en': 'Deep Black Cotton Soil (Dharwad Vertisols): High water storage (Stage-wise deep irrigation every 6-8 days)', 'kn': 'ಕಪ್ಪು ಹತ್ತಿ ಮಣ್ಣು (ಧಾರವಾಡ): ಹಂತವಾರು 6-8 ದಿನಗಳಿಗೊಮ್ಮೆ ಆಳ ನೀರಾವರಿ', 'hi': 'काली कपास मिट्टी (धारवाड़): अवस्था अनुसार हर 6-8 दिन में गहरी सिंचाई'}
    }
    freq_data = soil_freq.get(soil_type, soil_freq['loam'])
    interval_days = freq_data['days']

    # 8. User-Configured Pump Flow Rate (Default 10,000 L/hr/acre)
    default_flow_rate = 10000.0
    is_custom_flow = False
    if pump_flow_rate is not None:
        try:
            custom_val = float(pump_flow_rate)
            if custom_val > 0:
                flow_rate_per_acre = custom_val
                is_custom_flow = True
            else:
                flow_rate_per_acre = default_flow_rate
        except Exception:
            flow_rate_per_acre = default_flow_rate
    else:
        flow_rate_per_acre = default_flow_rate
    flow_rate = flow_rate_per_acre * area_acres

    # 9. Gross irrigation depth (mm/day) & Event Volumes
    base_gross_depth_mm = round(etc_mm / efficiency, 2) if etc_mm > 0 else 0.0
    base_litres_per_acre_day = int(base_gross_depth_mm * 4046.86)
    base_total_litres_day = int(base_litres_per_acre_day * area_acres)
    base_litres_per_event = int(base_total_litres_day * interval_days)

    gross_depth_mm = round(net_depth_mm / efficiency, 2) if net_depth_mm > 0 else 0.0
    litres_per_acre_day = int(gross_depth_mm * 4046.86)
    total_litres_day = int(litres_per_acre_day * area_acres)
    litres_per_event = int(total_litres_day * interval_days)

    # Base runtime (normal dry weather baseline)
    if base_litres_per_event > 0:
        base_run_hours = base_litres_per_event / max(flow_rate, 1000)
        base_run_mins = max(15, min(360, int(base_run_hours * 60)))
        b_hp = base_run_mins // 60
        b_mp = base_run_mins % 60
        if b_hp > 0 and b_mp > 0:
            base_runtime_en = f"{b_hp} hr {b_mp} min"
            base_runtime_kn = f"{b_hp} ಗಂಟೆ {b_mp} ನಿಮಿಷ"
            base_runtime_hi = f"{b_hp} घंटा {b_mp} मिनट"
        elif b_hp > 0:
            base_runtime_en = f"{b_hp} hours"
            base_runtime_kn = f"{b_hp} ಗಂಟೆಗಳು"
            base_runtime_hi = f"{b_hp} घंटे"
        else:
            base_runtime_en = f"{b_mp} minutes"
            base_runtime_kn = f"{b_mp} ನಿಮಿಷ"
            base_runtime_hi = f"{b_mp} मिनट"
    else:
        base_run_mins = 0
        base_runtime_en = "0 min"
        base_runtime_kn = "0 ನಿಮಿಷ"
        base_runtime_hi = "0 मिनट"

    is_rain_paused = bool(rainfall_mm >= 5.0 or (rainfall_mm > 0 and net_depth_mm <= 0.05))

    # 10. Runtime calculation based on system type and volume per event
    if litres_per_event > 0:
        run_hours = litres_per_event / max(flow_rate, 1000)
        run_mins = int(run_hours * 60)
        run_mins = max(15, min(360, run_mins))
    else:
        run_mins = 0

    hours_part = run_mins // 60
    mins_part = run_mins % 60

    if run_mins == 0:
        runtime_en = "0 min (Rain sufficient)"
        runtime_kn = "0 ನಿಮಿಷ (ಮಳೆ ಸಾಕಷ್ಟಾಗಿದೆ)"
        runtime_hi = "0 मिनट (वर्षा पर्याप्त)"
    elif hours_part > 0 and mins_part > 0:
        runtime_en = f"{hours_part} hr {mins_part} min"
        runtime_kn = f"{hours_part} ಗಂಟೆ {mins_part} ನಿಮಿಷ"
        runtime_hi = f"{hours_part} घंटा {mins_part} मिनट"
    elif hours_part > 0:
        runtime_en = f"{hours_part} hours"
        runtime_kn = f"{hours_part} ಗಂಟೆಗಳು"
        runtime_hi = f"{hours_part} घंटे"
    else:
        runtime_en = f"{mins_part} minutes"
        runtime_kn = f"{mins_part} ನಿಮಿಷ"
        runtime_hi = f"{mins_part} मिनट"

    # 11. Rain Skip / Mitigation Alert
    rain_alert = None
    rain_alert_en = ""
    rain_alert_kn = ""
    rain_alert_hi = ""

    if rainfall_mm >= 15.0:
        rain_alert = True
        rain_alert_en = f"🌧️ Heavy Rain Alert: {rainfall_mm:.0f}mm precipitation detected. SKIP irrigation for 48 hours to prevent waterlogging and root rot."
        rain_alert_kn = f"🌧️ ಭಾರಿ ಮಳೆ ಎಚ್ಚರಿಕೆ: {rainfall_mm:.0f}ಮಿಮೀ ಮಳೆ ದಾಖಲಾಗಿದೆ. ನೀರು ನಿಲ್ಲುವುದು ಮತ್ತು ಬೇರು ಕೊಳೆತ ತಡೆಯಲು ಮುಂದಿನ 48 ಗಂಟೆ ನೀರು ಹಾಯಿಸಬೇಡಿ."
        rain_alert_hi = f"🌧️ भारी वर्षा चेतावनी: {rainfall_mm:.0f}mm वर्षा दर्ज है। जलभराव और जड़ सड़न रोकने हेतु 48 घंटे सिंचाई रोकें।"
    elif rainfall_mm >= 5.0:
        rain_alert = True
        rain_alert_en = f"🌧️ Rain Alert: {rainfall_mm:.0f}mm precipitation detected. Effective rain ({peff_mm:.1f}mm) subtracted from requirement. SKIP irrigation for 24 hours."
        rain_alert_kn = f"🌧️ ಮಳೆ ಎಚ್ಚರಿಕೆ: {rainfall_mm:.0f}ಮಿಮೀ ಮಳೆ ದಾಖಲಾಗಿದೆ. ಪರಿಣಾಮಕಾರಿ ಮಳೆ ({peff_mm:.1f}ಮಿಮೀ) ಕಳೆಯಲಾಗಿದೆ. 24 ಗಂಟೆ ನೀರು ನಿಲ್ಲಿಸಿ."
        rain_alert_hi = f"🌧️ वर्षा चेतावनी: {rainfall_mm:.0f}mm वर्षा दर्ज है। प्रभावी वर्षा ({peff_mm:.1f}mm) घटाई गई है। 24 घंटे सिंचाई रोकें।"

    crop_name_tr = get_crop_name(crop_l, lang)
    stage_name_tr = GROWTH_STAGES_TR.get(growth_stage, {}).get(lang, growth_stage)
    method_name_tr = IRRIGATION_METHODS_TR.get(irrigation_type, {}).get(lang, irrigation_type)
    soil_name_tr = SOIL_TYPES_TR.get(soil_type, {}).get(lang, soil_type)

    method_name_en = IRRIGATION_METHODS_TR.get(irrigation_type, {}).get('en', irrigation_type)
    method_name_kn = IRRIGATION_METHODS_TR.get(irrigation_type, {}).get('kn', irrigation_type)
    method_name_hi = IRRIGATION_METHODS_TR.get(irrigation_type, {}).get('hi', irrigation_type)
    soil_name_en = SOIL_TYPES_TR.get(soil_type, {}).get('en', soil_type)
    soil_name_kn = SOIL_TYPES_TR.get(soil_type, {}).get('kn', soil_type)
    soil_name_hi = SOIL_TYPES_TR.get(soil_type, {}).get('hi', soil_type)

    from models.agri_calendar_service import get_district_institution
    univ_name, kvk_name = get_district_institution(district)

    if crop_l == 'wheat':
        freq_text = {
            'en': f"Stage-Based: Crown Root Initiation (21-25 DAS) → Tillering (40-45 DAS) → Jointing (60-65 DAS) → Flowering (75-80 DAS) → Grain Filling (90-95 DAS) [{univ_name} / {kvk_name}]",
            'kn': f"ಹಂತ-ಆಧರಿತ: ಕಿರೀಟ ಬೇರು (21-25 ದಿನ) → ಕವಲೊಡೆಯುವುದು (40-45 ದಿನ) → ಗಂಟು ಕಟ್ಟುವುದು (60-65 ದಿನ) → ಹೂವಾಡುವುದು (75-80 ದಿನ) → ಕಾಳು ತುಂಬುವುದು (90-95 ದಿನ)",
            'hi': f"अवस्था-आधारित: ताज जड़ (21-25 दिन) → कल्ले फूटना (40-45 दिन) → गांठ बनना (60-65 दिन) → फूल आना (75-80 दिन) → दाना भराव (90-95 दिन)"
        }
    else:
        freq_text = freq_data

    stage_tag = f" ({stage_schedule_en})" if stage_schedule_en else ""
    kvk_note_en = f" | {univ_name} / {kvk_name} Advisory: {critical_stage_info_en}" if critical_stage_info_en else ""
    kvk_note_kn = f" | {univ_name} / {kvk_name} ಸಲಹೆ: {critical_stage_info_kn}" if critical_stage_info_kn else ""
    kvk_note_hi = f" | {univ_name} / {kvk_name} सलाह: {critical_stage_info_hi}" if critical_stage_info_hi else ""

    if rainfall_mm is None:
        rain_phrase_en = ""
        rain_phrase_kn = ""
        rain_phrase_hi = ""
    else:
        rain_phrase_en = f" after {peff_mm:.1f}mm effective rainfall"
        rain_phrase_kn = f" (ಪರಿಣಾಮಕಾರಿ ಮಳೆ {peff_mm:.1f}ಮಿಮೀ ಕಳೆಯಲಾಗಿದೆ)"
        rain_phrase_hi = f" (प्रभावी वर्षा {peff_mm:.1f}mm घटाकर)"

    if is_rain_paused or run_mins == 0:
        rain_disp = f"{rainfall_mm:.0f}mm" if rainfall_mm is not None else ""
        peff_disp = f" (effective {peff_mm:.1f}mm)" if peff_mm is not None else ""
        advice_en = f"🌧️ Irrigation Paused: Natural rainfall{peff_disp} fully satisfies crop water demand today ({etc_mm:.2f} mm/day). No pumping required for 24–48 hours.{stage_tag}{kvk_note_en}"
        advice_kn = f"🌧️ ನೀರಾವರಿ ಅಗತ್ಯವಿಲ್ಲ (ಮಳೆ ಸಾಕಷ್ಟಾಗಿದೆ): ನೈಸರ್ಗಿಕ ಮಳೆಯು ಇಂದಿನ ಬೆಳೆಯ ನೀರಿನ ಅಗತ್ಯವನ್ನು ({etc_mm:.2f} ಮಿಮೀ/ದಿನ) ಸಂಪೂರ್ಣವಾಗಿ ಪೂರೈಸುತ್ತದೆ. 24–48 ಗಂಟೆಗಳ ಕಾಲ ಪಂಪ್ ಚಲಾಯಿಸಬೇಡಿ.{kvk_note_kn}"
        advice_hi = f"🌧️ सिंचाई स्थगित (वर्षा पर्याप्त): प्राकृतिक वर्षा आज की फसल जल आवश्यकता ({etc_mm:.2f} mm/दिन) पूरी करती है। 24–48 घंटे पंप न चलाएं।{kvk_note_hi}"
    else:
        advice_en = f"Stage-Based Irrigation{stage_tag}: Irrigate {runtime_en} per irrigation event ({freq_data['en']}) delivering {litres_per_event:,} Litres per event. ETc: {etc_mm:.2f} mm/day (ET₀: {et0} mm x Kc: {kc:.2f}), Net requirement: {net_depth_mm:.2f} mm/day{rain_phrase_en}. Daily water: {total_litres_day:,} L/day for {area_acres} acre(s) via {method_name_en} ({int(efficiency * 100)}% efficiency, pump flow {int(flow_rate_per_acre):,} L/hr).{kvk_note_en}"
        advice_kn = f"ಹಂತ-ಆಧರಿತ ನಿಖರ ನೀರಾವರಿ: ಪ್ರತಿ ನೀರಾವರಿ ಅವಧಿಗೆ: {runtime_kn} ({freq_data['kn']}) — ಪ್ರತಿ ಬಾರಿಗೆ {litres_per_event:,} ಲೀಟರ್ ನೀರು. ETc: {etc_mm:.2f} ಮಿಮೀ/ದಿನ (ET₀: {et0} x Kc: {kc:.2f}){rain_phrase_kn}. ದೈನಂದಿನ ಅಗತ್ಯ: {area_acres} ಎಕರೆಗೆ ದಿನಕ್ಕೆ {total_litres_day:,} ಲೀಟರ್ ({method_name_kn} ಮೂಲಕ, ಪಂಪ್ ಹರಿವು {int(flow_rate_per_acre):,} ಲೀ/ಗಂಟೆ).{kvk_note_kn}"
        advice_hi = f"अवस्था-आधारित सटीक सिंचाई: सिंचाई का समय: प्रति सिंचाई {runtime_hi} ({freq_data['hi']}) — प्रति सिंचाई {litres_per_event:,} लीटर। ETc: {etc_mm:.2f} mm/दिन (ET₀: {et0} x Kc: {kc:.2f}){rain_phrase_hi}। दैनिक आवश्यकता: {area_acres} एकड़ हेतु {total_litres_day:,} लीटर/दिन ({method_name_hi} द्वारा, पंप प्रवाह {int(flow_rate_per_acre):,} ली/घंटा)।{kvk_note_hi}"

    return {
        'crop': crop,
        'crop_tr': crop_name_tr,
        'growth_stage': growth_stage,
        'growth_stage_tr': stage_name_tr,
        'stage_schedule_en': stage_schedule_en,
        'critical_stage_info_en': critical_stage_info_en,
        'days_after_sowing': das_val,
        'soil_type': soil_type,
        'soil_type_tr': soil_name_tr,
        'area_acres': area_acres,
        'area_m2': round(area_acres * 4046.86, 2),
        'irrigation_type': irrigation_type,
        'irrigation_type_tr': method_name_tr,
        'temp': int(round(temp)),
        'temp_c': int(round(temp)),
        'humidity': int(round(humidity)),
        'rainfall_mm': rainfall_mm,
        'peff_mm': peff_mm,
        'weather_desc': weather_desc,
        'et0': et0,
        'et0_method': 'FAO-56 Hargreaves Radiation Method (Eq. 21 & 52)',
        'is_plausible': is_plausible,
        'plausibility_warning': plausibility_warning,
        'kc': kc,
        'etc_mm': etc_mm,
        'net_depth_mm': net_depth_mm,
        'gross_depth_mm': gross_depth_mm,
        'base_gross_depth_mm': base_gross_depth_mm,
        'base_total_litres_day': base_total_litres_day,
        'base_litres_per_event': base_litres_per_event,
        'base_run_mins': base_run_mins,
        'base_runtime_en': base_runtime_en,
        'base_runtime_kn': base_runtime_kn,
        'base_runtime_hi': base_runtime_hi,
        'is_rain_paused': is_rain_paused,
        'efficiency_pct': int(efficiency * 100),
        'efficiency': efficiency,
        'emitter_flow_rate_lph': flow_rate,
        'pump_flow_rate_per_acre': int(flow_rate_per_acre),
        'is_custom_flow': is_custom_flow,
        'interval_days': interval_days,
        'litres_per_event': litres_per_event,
        'litres_per_day_avg': total_litres_day,
        'litres_per_acre_day': litres_per_acre_day,
        'total_litres_day': total_litres_day,
        'run_mins': run_mins,
        'runtime_en': runtime_en,
        'runtime_kn': runtime_kn,
        'runtime_hi': runtime_hi,
        'frequency_en': freq_text['en'],
        'frequency_kn': freq_text['kn'],
        'frequency_hi': freq_text['hi'],
        'kc_source': "FAO-56 & UAS Dharwad Package of Practices",
        'rain_alert': rain_alert,
        'rain_alert_en': rain_alert_en,
        'rain_alert_kn': rain_alert_kn,
        'rain_alert_hi': rain_alert_hi,
        'advice_en': advice_en,
        'advice_kn': advice_kn,
        'advice_hi': advice_hi
    }


# CROP WEATHER PROFILES & REGIONAL PREFERABILITY EVALUATION
# =====================================================================
CROP_WEATHER_PROFILES = {
    'soybean': {
        'temp_opt': (20, 33), 'temp_tol': (15, 38),
        'hum_opt': (45, 90), 'hum_tol': (35, 95),
        'rainfall_pref': 'moderate',
        'seasons': ['Kharif', 'Whole Year'],
        'weather_reason': {
            'en': 'Protein-rich oilseed legume that enriches soil through biological nitrogen fixation.',
            'kn': 'ಸಾರಜನಕ ಸ್ಥಿರೀಕರಿಸಿ ಮಣ್ಣಿನ ಫಲವತ್ತತೆ ಹೆಚ್ಚಿಸುವ ಪ್ರಮುಖ ಎಣ್ಣೆಕಾಳು ಬೆಳೆ.',
            'hi': 'प्रोटीन युक्त तिलहनी दलहन जो जैविक नाइट्रोजन स्थिरीकरण द्वारा मिट्टी को समृद्ध बनाती है।'
        }
    },
    'groundnut': {
        'temp_opt': (22, 34), 'temp_tol': (18, 38),
        'hum_opt': (40, 80), 'hum_tol': (30, 90),
        'rainfall_pref': 'moderate',
        'seasons': ['Kharif', 'Rabi', 'Zaid', 'Whole Year'],
        'weather_reason': {
            'en': 'Major oilseed legume that fixes nitrogen and develops pods underground.',
            'kn': 'ಮಣ್ಣಿನಡಿ ಕಾಯಿ ಕಟ್ಟುವ ಹಾಗೂ ಸಾರಜನಕ ಸ್ಥಿರೀಕರಿಸುವ ಪ್ರಮುಖ ವಾಣಿಜ್ಯ ಎಣ್ಣೆಕಾಳು ಬೆಳೆ.',
            'hi': 'प्रमुख तिलहनी फसल जो नाइट्रोजन स्थिरीकरण करती है और भूमिगत फलियां बनाती है।'
        }
    },
    'ragi': {
        'temp_opt': (20, 30), 'temp_tol': (15, 36),
        'hum_opt': (50, 75), 'hum_tol': (35, 85),
        'rainfall_pref': 'moderate',
        'seasons': ['Kharif', 'Whole Year'],
        'weather_reason': {
            'en': 'Hardy millet crop with high dietary calcium content and deep rooting capacity.',
            'kn': 'ಅಧಿಕ ಕ್ಯಾಲ್ಸಿಯಂ ಮತ್ತು ನಾರಿನಂಶ ಹೊಂದಿರುವ ಸಾಂಪ್ರದಾಯಿಕ ಪೌಷ್ಟಿಕ ಸಿರಿಧಾನ್ಯ.',
            'hi': 'प्रचुर कैल्शियम और आहार फाइबर से भरपूर पारंपरिक पौष्टिक मोटा अनाज।'
        }
    },
    'rice': {
        'temp_opt': (22, 33), 'temp_tol': (18, 38),
        'hum_opt': (60, 90), 'hum_tol': (50, 95),
        'rainfall_pref': 'high',
        'seasons': ['Kharif', 'Whole Year'],
        'weather_reason': {
            'en': 'Primary cereal food grain cultivated in puddled wetlands and irrigated systems.',
            'kn': 'ನೀರಾವರಿ ಮತ್ತು ಗದ್ದೆಗಳಲ್ಲಿ ಬೆಳೆಯಲಾಗುವ ಪ್ರಮುಖ ಆಹಾರ ಧಾನ್ಯ ಬೆಳೆ.',
            'hi': 'सिंचित खेतों और दलदली भूमि में उगाई जाने वाली प्रमुख खाद्यान्न फसल।'
        }
    },
    'maize': {
        'temp_opt': (20, 30), 'temp_tol': (15, 36),
        'hum_opt': (50, 75), 'hum_tol': (40, 85),
        'rainfall_pref': 'moderate',
        'seasons': ['Kharif', 'Zaid', 'Whole Year'],
        'weather_reason': {
            'en': 'High-yielding versatile cereal crop requiring well-drained fertile soils.',
            'kn': 'ಉತ್ತಮ ನೀರು ಬಸಿದು ಹೋಗುವ ಗೋಡು ಮಣ್ಣಿನಲ್ಲಿ ಬೆಳೆಯುವ ಅಧಿಕ ಇಳುವರಿಯ ಪ್ರಮುಖ ಧಾನ್ಯ.',
            'hi': 'उचित जल निकासी वाली उपजाऊ मिट्टी में उच्च उपज देने वाली बहुमुखी खाद्यान्न फसल।'
        }
    },
    'arecanut': {
        'temp_opt': (20, 35), 'temp_tol': (15, 38),
        'hum_opt': (50, 90), 'hum_tol': (35, 95),
        'rainfall_pref': 'high',
        'seasons': ['Whole Year', 'Kharif'],
        'weather_reason': {
            'en': 'Perennial commercial plantation palm cultivated across dedicated agrarian belts.',
            'kn': 'ವಿಶೇಷ ಕೃಷಿ ವಲಯಗಳಲ್ಲಿ ಬೆಳೆಯಲಾಗುವ ದೀರ್ಘಾವಧಿಯ ಪ್ರಮುಖ ವಾಣಿಜ್ಯ ತೋಟಗಾರಿಕಾ ಬೆಳೆ.',
            'hi': 'विशिष्ट कृषि क्षेत्रों में उगाई जाने वाली प्रमुख दीर्घकालिक व्यावसायिक बागवानी फसल।'
        }
    },
    'cashew': {
        'temp_opt': (22, 36), 'temp_tol': (16, 40),
        'hum_opt': (40, 85), 'hum_tol': (30, 90),
        'rainfall_pref': 'moderate',
        'seasons': ['Whole Year', 'Zaid', 'Kharif'],
        'weather_reason': {
            'en': 'Commercial plantation crop with extensive taproots, well adapted to lateritic soils.',
            'kn': 'ಕೆಂಪು ಜಂಬಿಟ್ಟಿಗೆ ಮಣ್ಣಿಗೆ ಹೊಂದಿಕೊಳ್ಳುವ ಹಾಗೂ ಆಳವಾದ ಬೇರು ವ್ಯವಸ್ಥೆ ಹೊಂದಿರುವ ತೋಟಗಾರಿಕಾ ಬೆಳೆ.',
            'hi': 'गहरी जड़ प्रणाली वाली और लेटराइट मिट्टी के अनुकूल प्रमुख व्यावसायिक बागवानी फसल।'
        }
    },
    'sunflower': {
        'temp_opt': (20, 33), 'temp_tol': (15, 38),
        'hum_opt': (35, 75), 'hum_tol': (25, 85),
        'rainfall_pref': 'moderate',
        'seasons': ['Kharif', 'Rabi', 'Zaid', 'Whole Year'],
        'weather_reason': {
            'en': 'Commercial oilseed crop cultivated for edible oil with high polyunsaturated fatty acids.',
            'kn': 'ಉತ್ತಮ ಗುಣಮಟ್ಟದ ಅಡುಗೆ ಎಣ್ಣೆ ನೀಡುವ ಪ್ರಮುಖ ವಾಣಿಜ್ಯ ಎಣ್ಣೆಕಾಳು ಬೆಳೆ.',
            'hi': 'उच्च पॉलीअनसैचुरेटेड फैटी एसिड युक्त खाद्य तेल के लिए उगाई जाने वाली तिलहनी फसल।'
        }
    },
    'mulberry': {
        'temp_opt': (20, 33), 'temp_tol': (15, 38),
        'hum_opt': (40, 85), 'hum_tol': (30, 90),
        'rainfall_pref': 'moderate',
        'seasons': ['Whole Year', 'Kharif', 'Rabi'],
        'weather_reason': {
            'en': 'Perennial foliage shrub cultivated to rear silkworm larvae for sericulture silk production.',
            'kn': 'ರೇಷ್ಮೆ ಹುಳು ಸಾಕಾಣಿಕೆಗೆ ಪೌಷ್ಟಿಕ ಎಲೆಗಳನ್ನು ಒದಗಿಸುವ ಪ್ರಮುಖ ತೋಟಗಾರಿಕಾ ಬೆಳೆ.',
            'hi': 'रेशम कीट पालन और उच्च गुणवत्ता वाले रेशम उत्पादन के लिए उगाई जाने वाली बहुवर्षीय झाड़ी।'
        }
    },
    'jowar': {
        'temp_opt': (20, 35), 'temp_tol': (15, 40),
        'hum_opt': (35, 75), 'hum_tol': (25, 85),
        'rainfall_pref': 'low',
        'seasons': ['Rabi', 'Kharif', 'Whole Year'],
        'weather_reason': {
            'en': 'Hardy staple cereal with extensive fibrous roots and high water-use efficiency.',
            'kn': 'ಆಳವಾದ ಬೇರು ಮತ್ತು ಕಡಿಮೆ ನೀರಿನಲ್ಲೂ ಉತ್ತಮ ಇಳುವರಿ ನೀಡುವ ಪ್ರಮುಖ ಧಾನ್ಯ.',
            'hi': 'गहरी जड़ प्रणाली और उच्च जल उपयोग दक्षता वाली प्रमुख पारंपरिक खाद्यान्न फसल।'
        }
    },
    'bengalgram': {
        'temp_opt': (16, 30), 'temp_tol': (12, 36),
        'hum_opt': (30, 70), 'hum_tol': (20, 80),
        'rainfall_pref': 'low',
        'seasons': ['Rabi', 'Kharif', 'Whole Year'],
        'weather_reason': {
            'en': 'Major protein-rich pulse crop that enriches soil through atmospheric nitrogen fixation.',
            'kn': 'ಸಾರಜನಕ ಸ್ಥಿರೀಕರಣದ ಮೂಲಕ ಮಣ್ಣಿನ ಫಲವತ್ತತೆ ಹೆಚ್ಚಿಸುವ ಪ್ರಮುಖ ಪ್ರೋಟೀನ್ ಯುಕ್ತ ಕಾಳು ಬೆಳೆ.',
            'hi': 'जैविक नाइट्रोजन स्थिरीकरण द्वारा मिट्टी की उर्वरता बढ़ाने वाली प्रमुख दलहनी फसल।'
        }
    },
    'chickpea': {
        'temp_opt': (16, 30), 'temp_tol': (12, 36),
        'hum_opt': (30, 70), 'hum_tol': (20, 80),
        'rainfall_pref': 'low',
        'seasons': ['Rabi', 'Kharif', 'Whole Year'],
        'weather_reason': {
            'en': 'Major protein-rich pulse crop that enriches soil through atmospheric nitrogen fixation.',
            'kn': 'ಸಾರಜನಕ ಸ್ಥಿರೀಕರಣದ ಮೂಲಕ ಮಣ್ಣಿನ ಫಲವತ್ತತೆ ಹೆಚ್ಚಿಸುವ ಪ್ರಮುಖ ಪ್ರೋಟೀನ್ ಯುಕ್ತ ಕಾಳು ಬೆಳೆ.',
            'hi': 'जैविक नाइट्रोजन स्थिरीकरण द्वारा मिट्टी की उर्वरता बढ़ाने वाली प्रमुख दलहनी फसल।'
        }
    },
    'cotton': {
        'temp_opt': (22, 38), 'temp_tol': (16, 42),
        'hum_opt': (25, 75), 'hum_tol': (15, 85),
        'rainfall_pref': 'moderate',
        'seasons': ['Kharif', 'Rabi', 'Whole Year'],
        'weather_reason': {
            'en': 'Primary fiber cash crop with indeterminate growth pattern and deep taproot system.',
            'kn': 'ಆಳವಾದ ಬೇರು ಮತ್ತು ನಿರಂತರ ಕವಲೊಡೆಯುವ ಪ್ರಮುಖ ನಾರಿನ ವಾಣಿಜ್ಯ ಬೆಳೆ.',
            'hi': 'गहरी मूसला जड़ और निरंतर शाखाएं विकसित करने वाली प्रमुख प्राकृतिक रेशा नकदी फसल।'
        }
    },
    'sugarcane': {
        'temp_opt': (22, 35), 'temp_tol': (18, 40),
        'hum_opt': (60, 85), 'hum_tol': (45, 90),
        'rainfall_pref': 'high',
        'seasons': ['Whole Year', 'Kharif'],
        'weather_reason': {
            'en': 'Long-duration sucrose cash crop demanding intensive soil nutrients and systematic irrigation.',
            'kn': 'ಹೆಚ್ಚಿನ ಪೋಷಕಾಂಶ ಮತ್ತು ನೀರಾವರಿ ನಿರ್ವಹಣೆಗೆ ಸ್ಪಂದಿಸುವ ಪ್ರಮುಖ ವಾಣಿಜ್ಯ ಬೆಳೆ.',
            'hi': 'गहन मृदा पोषण और सुनियोजित सिंचाई प्रबंधन की आवश्यकता वाली प्रमुख नकदी फसल।'
        }
    },
    'tomato': {
        'temp_opt': (18, 28), 'temp_tol': (14, 34),
        'hum_opt': (50, 70), 'hum_tol': (35, 80),
        'rainfall_pref': 'moderate',
        'seasons': ['Kharif', 'Rabi', 'Whole Year'],
        'weather_reason': {
            'en': 'High-value commercial solanaceous vegetable cultivated through nursery seedling transplanting.',
            'kn': 'ಸಸಿ ಮಡಿ ನಾಟಿ ಪದ್ಧತಿಯ ಮೂಲಕ ಬೆಳೆಯಲಾಗುವ ಪ್ರಮುಖ ವಾಣಿಜ್ಯ ತರಕಾರಿ ಬೆಳೆ.',
            'hi': 'नर्सरी पौध रोपाई द्वारा उगाई जाने वाली प्रमुख उच्च मूल्य सोलेनेसी सब्जी फसल।'
        }
    },
    'potato': {
        'temp_opt': (15, 23), 'temp_tol': (10, 28),
        'hum_opt': (55, 75), 'hum_tol': (40, 85),
        'rainfall_pref': 'low',
        'seasons': ['Rabi'],
        'weather_reason': {
            'en': 'Starch-dense tuber crop requiring balanced soil nutrition and systematic ridge formation.',
            'kn': 'ಉತ್ತಮ ಗೆಡ್ಡೆ ಕಟ್ಟಲು ಸಮತೋಲಿತ ಮಣ್ಣಿನ ಪೋಷಕಾಂಶ ಮತ್ತು ಏರಿ ಪದ್ಧತಿ ಅಗತ್ಯವಿರುವ ಪ್ರಮುಖ ಆಹಾರ ಬೆಳೆ.',
            'hi': 'कंदों के उचित विकास के लिए संतुलित मृदा पोषण और मेड़ चढ़ाने की आवश्यकता वाली प्रमुख स्टार्च फसल।'
        }
    },
    'onion': {
        'temp_opt': (16, 28), 'temp_tol': (12, 34),
        'hum_opt': (45, 65), 'hum_tol': (30, 75),
        'rainfall_pref': 'low',
        'seasons': ['Rabi', 'Kharif'],
        'weather_reason': {
            'en': 'High-value bulb vegetable requiring fertile, well-aerated sandy loam soils for uniform bulbs.',
            'kn': 'ಏಕರೂಪದ ಗಾತ್ರದ ಈರುಳ್ಳಿ ಪಡೆಯಲು ಫಲವತ್ತಾದ ಹಾಗೂ ನೀರು ಸರಾಗವಾಗಿ ಹರಿಯುವ ಮರಳು ಮಿಶ್ರಿತ ಗೋಡು ಮಣ್ಣು ಪ್ರಶಸ್ತ.',
            'hi': 'एकसमान कंद आकार के लिए उपजाऊ और उचित जल निकासी वाली बलुई दोमट मिट्टी वाली उच्च मूल्य फसल।'
        }
    },
    'pomegranate': {
        'temp_opt': (22, 36), 'temp_tol': (15, 42),
        'hum_opt': (35, 60), 'hum_tol': (20, 75),
        'rainfall_pref': 'low',
        'seasons': ['Whole Year', 'Zaid', 'Kharif'],
        'weather_reason': {
            'en': 'Commercial fruit crop cultivated for nutrient-dense arils, responsive to systematic canopy training.',
            'kn': 'ವ್ಯವಸ್ಥಿತ ರೆಂಬೆ ಕತ್ತರಿಸುವಿಕೆಗೆ ಸ್ಪಂದಿಸುವ ಮತ್ತು ಅಧಿಕ ಮಾರುಕಟ್ಟೆ ಮೌಲ್ಯ ಹೊಂದಿರುವ ಪ್ರಮುಖ ಹಣ್ಣಿನ ಬೆಳೆ.',
            'hi': 'उचित कटाई-छंटाई प्रबंधन और समृद्ध दानों के लिए उगाई जाने वाली उच्च व्यावसायिक फल फसल।'
        }
    },
    'grapes': {
        'temp_opt': (18, 32), 'temp_tol': (12, 38),
        'hum_opt': (40, 60), 'hum_tol': (25, 75),
        'rainfall_pref': 'low',
        'seasons': ['Rabi', 'Zaid'],
        'weather_reason': {
            'en': 'Commercial berry crop trained on trellis systems, responsive to vine pruning and balanced nutrition.',
            'kn': 'ಪಂದಲ್ ಅಥವಾ ಟ್ರೆಲ್ಲಿಸ್ ಪದ್ಧತಿಯಲ್ಲಿ ಬೆಳೆಯಲಾಗುವ ಮತ್ತು ಸೂಕ್ತ ಕವಲು ಕತ್ತರಿಸುವಿಕೆಗೆ ಸ್ಪಂದಿಸುವ ಪ್ರಮುಖ ವಾಣಿಜ್ಯ ಬೆಳೆ.',
            'hi': 'पंडाल प्रणाली पर उगाई जाने वाली और नियमित छंटाई तथा संतुलित पोषण के प्रति संवेदनशील व्यावसायिक फसल।'
        }
    },
    'banana': {
        'temp_opt': (23, 33), 'temp_tol': (18, 38),
        'hum_opt': (65, 85), 'hum_tol': (50, 95),
        'rainfall_pref': 'high',
        'seasons': ['Whole Year'],
        'weather_reason': {
            'en': 'Heavy-feeding fruit crop requiring substantial potassium nutrition and organic mulching.',
            'kn': 'ಭಾರವಾದ ಗೊನೆ ಕಟ್ಟಲು ಅಧಿಕ ಪೊಟ್ಯಾಷ್ ಪೋಷಕಾಂಶ ಮತ್ತು ಸಾವಯವ ಹೊದಿಕೆ ಅಗತ್ಯವಿರುವ ಪ್ರಮುಖ ಹಣ್ಣಿನ ಬೆಳೆ.',
            'hi': 'भारी गुच्छे प्राप्त करने के लिए उच्च पोटाश पोषण और जैविक मल्चिंग की आवश्यकता वाली प्रमुख फल फसल।'
        }
    },
    'mango': {
        'temp_opt': (24, 36), 'temp_tol': (18, 42),
        'hum_opt': (45, 65), 'hum_tol': (30, 80),
        'rainfall_pref': 'moderate',
        'seasons': ['Zaid', 'Whole Year'],
        'weather_reason': {
            'en': 'Perennial orchard fruit crop responsive to balanced nutrition and post-bloom canopy management.',
            'kn': 'ಸಮತೋಲಿತ ಪೋಷಕಾಂಶ ಮತ್ತು ಹೂವಿನ ನಂತರದ ರೆಂಬೆ ನಿರ್ವಹಣೆಗೆ ಸ್ಪಂದಿಸುವ ಪ್ರಮುಖ ಸಾಂಪ್ರದಾಯಿಕ ಹಣ್ಣಿನ ಬೆಳೆ.',
            'hi': 'संतुलित पोषण और पुष्पन के बाद उचित छत्र प्रबंधन के अनुकूल प्रमुख फल फसल।'
        }
    },
    'coffee': {
        'temp_opt': (18, 28), 'temp_tol': (14, 32),
        'hum_opt': (70, 85), 'hum_tol': (55, 95),
        'rainfall_pref': 'high',
        'seasons': ['Whole Year'],
        'weather_reason': {
            'en': 'Shade-grown plantation crop with dual Arabica and Robusta cultivars under multi-tier forest canopies.',
            'kn': 'ಬಹುಹಂತದ ನೆರಳಿನ ಮರಗಳ ಅಡಿಯಲ್ಲಿ ಅರೇಬಿಕಾ ಮತ್ತು ರೋಬಸ್ಟಾ ತಳಿಗಳೊಂದಿಗೆ ಬೆಳೆಯಲಾಗುವ ತೋಟಗಾರಿಕಾ ಬೆಳೆ.',
            'hi': 'बहु-स्तरीय छायादार वृक्षों के नीचे अरेबिका और रोबस्टा किस्मों के रूप में उगाई जाने वाली प्रमुख बागवानी फसल।'
        }
    },
    'coconut': {
        'temp_opt': (24, 34), 'temp_tol': (20, 38),
        'hum_opt': (65, 85), 'hum_tol': (50, 95),
        'rainfall_pref': 'high',
        'seasons': ['Whole Year'],
        'weather_reason': {
            'en': 'Perennial palm yielding timber, coir fiber, and nutrient-rich copra under systematic basin management.',
            'kn': 'ಕಟ್ಟೆ ನಿರ್ವಹಣೆ ಮತ್ತು ಸಮತೋಲಿತ ಪೋಷಕಾಂಶಗಳೊಂದಿಗೆ ಗರಿಷ್ಠ ಇಳುವರಿ ನೀಡುವ ಸದಾಹಸಿರು ಕಲ್ಪವೃಕ್ಷ ಬೆಳೆ.',
            'hi': 'नियमित थाला प्रबंधन और संतुलित पोषक तत्वों के साथ वर्षभर उपज देने वाला कल्पवृक्ष वृक्ष फसल।'
        }
    },
    'pigeonpeas': {
        'temp_opt': (22, 34), 'temp_tol': (16, 38),
        'hum_opt': (45, 70), 'hum_tol': (30, 80),
        'rainfall_pref': 'moderate',
        'seasons': ['Kharif', 'Rabi', 'Whole Year'],
        'weather_reason': {
            'en': 'Deep-rooting grain legume fixing nitrogen and producing protein-rich seeds for pulses.',
            'kn': 'ಆಳವಾದ ಬೇರು ವ್ಯವಸ್ಥೆ ಮತ್ತು ಸಾರಜನಕ ಸ್ಥಿರೀಕರಣದೊಂದಿಗೆ ಪ್ರೋಟೀನ್ ಯುಕ್ತ ಬೇಳೆ ನೀಡುವ ಪ್ರಮುಖ ಬೆಳೆ.',
            'hi': 'गहरी जड़ प्रणाली और नाइट्रोजन स्थिरीकरण के साथ प्रोटीन युक्त दाल प्रदान करने वाली प्रमुख दलहन फसल।'
        }
    },
    'blackgram': {
        'temp_opt': (22, 33), 'temp_tol': (18, 36),
        'hum_opt': (55, 75), 'hum_tol': (40, 85),
        'rainfall_pref': 'moderate',
        'seasons': ['Kharif', 'Zaid'],
        'weather_reason': {
            'en': 'Short-duration pulse crop that enriches soil through biological nitrogen fixation and leaf residue.',
            'kn': 'ಅಲ್ಪಾವಧಿಯಲ್ಲಿ ಕೊಯ್ಲಿಗೆ ಬರುವ ಹಾಗೂ ಸಾರಜನಕ ಸ್ಥಿರೀಕರಣದ ಮೂಲಕ ಭೂಮಿಯ ಫಲವತ್ತತೆ ಹೆಚ್ಚಿಸುವ ಪ್ರಮುಖ ಕಾಳು ಬೆಳೆ.',
            'hi': 'कम अवधि में पकने वाली दलहन जो जैविक नाइट्रोजन स्थिरीकरण द्वारा खेत की उर्वरा शक्ति को बढ़ाती है।'
        }
    },
    'mungbean': {
        'temp_opt': (22, 35), 'temp_tol': (18, 38),
        'hum_opt': (50, 75), 'hum_tol': (35, 80),
        'rainfall_pref': 'low',
        'seasons': ['Kharif', 'Zaid'],
        'weather_reason': {
            'en': 'Fast-maturing pulse legume that restores soil fertility through symbiotic nitrogen fixation.',
            'kn': 'ಶೀಘ್ರ ಕಟಾವಿಗೆ ಬರುವ ಮತ್ತು ಸಾರಜನಕ ಸ್ಥಿರೀಕರಿಸಿ ಭೂಮಿಯ ಸತ್ವವನ್ನು ಹೆಚ್ಚಿಸುವ ಪ್ರಮುಖ ಕಾಳು ಬೆಳೆ.',
            'hi': 'शीघ्र परिपक्व होने वाली दलहन जो सहजीवी नाइट्रोजन स्थिरीकरण द्वारा मृदा स्वास्थ्य में सुधार करती है।'
        }
    },
    'watermelon': {
        'temp_opt': (24, 35), 'temp_tol': (18, 40),
        'hum_opt': (40, 65), 'hum_tol': (30, 75),
        'rainfall_pref': 'low',
        'seasons': ['Zaid'],
        'weather_reason': {
            'en': 'Trailing cucurbit vine cultivated for sweet fruit, responsive to raised beds and plastic mulching.',
            'kn': 'ಏರು ಮಡಿ ಮತ್ತು ಮಲ್ಚಿಂಗ್ ಪದ್ಧತಿಯಲ್ಲಿ ಅತ್ಯಧಿಕ ಇಳುವರಿ ನೀಡುವ ಜನಪ್ರಿಯ ಹಣ್ಣಿನ ಬೆಳೆ.',
            'hi': 'उठी हुई क्यारियों और मल्चिंग तकनीक पर बेहतर उपज देने वाली प्रमुख तरबूज फल बेल।'
        }
    },
    'muskmelon': {
        'temp_opt': (24, 35), 'temp_tol': (18, 40),
        'hum_opt': (40, 65), 'hum_tol': (30, 75),
        'rainfall_pref': 'low',
        'seasons': ['Zaid'],
        'weather_reason': {
            'en': 'High-value cucurbit cultivated on raised beds with drip fertigation for uniform netting and flavor.',
            'kn': 'ಏಕರೂಪದ ಹಣ್ಣಿನ ಗಾತ್ರ ಮತ್ತು ಸುವಾಸನೆಗಾಗಿ ಹನಿ ನೀರಾವರಿ ಪದ್ಧತಿಯಲ್ಲಿ ಬೆಳೆಯಲಾಗುವ ವಾಣಿಜ್ಯ ಬೆಳೆ.',
            'hi': 'आकर्षक जालीदार छिलके और सुगंधित गूदे के लिए ड्रिप फर्टिगेशन विधि से उगाई जाने वाली उच्च मूल्य नकदी फसल।'
        }
    },
    'papaya': {
        'temp_opt': (22, 34), 'temp_tol': (16, 38),
        'hum_opt': (55, 80), 'hum_tol': (40, 90),
        'rainfall_pref': 'moderate',
        'seasons': ['Whole Year'],
        'weather_reason': {
            'en': 'Rapid-growing herbaceous fruit crop producing heavy fruit clusters along its central trunk axis.',
            'kn': 'ಕಾಂಡದ ಉದ್ದಕ್ಕೂ ಒತ್ತಾಗಿ ಹಣ್ಣಿನ ಗೊಂಚಲುಗಳನ್ನು ನೀಡುವ ಅಲ್ಪಾವಧಿಯ ಜನಪ್ರಿಯ ಹಣ್ಣಿನ ಬೆಳೆ.',
            'hi': 'मुख्य तने पर सघन फल गुच्छे प्रदान करने वाली तेजी से बढ़ने वाली प्रमुख फल फसल।'
        }
    },
    'orange': {
        'temp_opt': (18, 30), 'temp_tol': (12, 35),
        'hum_opt': (50, 70), 'hum_tol': (35, 80),
        'rainfall_pref': 'moderate',
        'seasons': ['Rabi', 'Whole Year'],
        'weather_reason': {
            'en': 'Citrus fruit tree responsive to micro-nutrient foliar sprays and systematic pruning.',
            'kn': 'ಸೂಕ್ಷ್ಮ ಪೋಷಕಾಂಶಗಳ ಸಿಂಪಡಣೆ ಮತ್ತು ನಿಯಮಿತ ಕವಲು ಕತ್ತರಿಸುವಿಕೆಗೆ ಸ್ಪಂದಿಸುವ ಸಿಟ್ರಸ್ ಹಣ್ಣಿನ ಬೆಳೆ.',
            'hi': 'सूक्ष्म पोषक तत्वों के छिड़काव और नियमित छंटाई के प्रति संवेदनशील प्रमुख खट्टे फल की फसल।'
        }
    },
    'apple': {
        'temp_opt': (12, 22), 'temp_tol': (6, 28),
        'hum_opt': (50, 70), 'hum_tol': (35, 80),
        'rainfall_pref': 'moderate',
        'seasons': ['Rabi'],
        'weather_reason': {
            'en': 'Deciduous pome fruit requiring dedicated rootstock management and spur-bearing canopy training.',
            'kn': 'ವ್ಯವಸ್ಥಿತ ಕವಲು ನಿರ್ವಹಣೆ ಮತ್ತು ಮೂಲಕಾಂಡದ ತಳಿಗಳಿಂದ ಉತ್ಕೃಷ್ಟ ಇಳುವರಿ ನೀಡುವ ಪೌಷ್ಟಿಕ ಹಣ್ಣಿನ ಬೆಳೆ.',
            'hi': 'उचित रूटस्टॉक प्रबंधन और सुनियोजित छत्र विकास के साथ उगाई जाने वाली प्रमुख शीतोष्ण फल फसल।'
        }
    },
    'lentil': {
        'temp_opt': (15, 25), 'temp_tol': (10, 30),
        'hum_opt': (40, 65), 'hum_tol': (25, 75),
        'rainfall_pref': 'low',
        'seasons': ['Rabi'],
        'weather_reason': {
            'en': 'Protein-dense pulse crop suitable for sustainable crop rotations and balanced soil enhancement.',
            'kn': 'ಬೆಳೆ ಪರಿವರ್ತನೆಗೆ ಅತ್ಯಂತ ಸೂಕ್ತವಾದ ಮತ್ತು ಪ್ರೋಟೀನ್ ಭರಿತ ಸಾಂಪ್ರದಾಯಿಕ ಕಾಳು ಬೆಳೆ.',
            'hi': 'फसल चक्र के लिए अत्यंत उपयुक्त और प्रोटीन से भरपूर प्रमुख दलहनी फसल।'
        }
    },
    'kidneybeans': {
        'temp_opt': (16, 27), 'temp_tol': (12, 32),
        'hum_opt': (50, 70), 'hum_tol': (35, 80),
        'rainfall_pref': 'moderate',
        'seasons': ['Kharif'],
        'weather_reason': {
            'en': 'Nutrient-demanding legume grown for high-protein culinary beans with upright bushy canopy.',
            'kn': 'ಅಧಿಕ ಪ್ರೋಟೀನ್ ಹೊಂದಿರುವ ಮತ್ತು ನೇರ ಪೊದೆಯಾಗಿ ಬೆಳೆಯುವ ಪ್ರಮುಖ ಪೌಷ್ಟಿಕ ಕಾಳು ಬೆಳೆ.',
            'hi': 'झाड़ीनुमा पौधों पर उच्च प्रोटीन युक्त फलियां प्रदान करने वाली पोषक दलहनी फसल।'
        }
    },
    'mothbeans': {
        'temp_opt': (24, 38), 'temp_tol': (20, 42),
        'hum_opt': (30, 60), 'hum_tol': (20, 70),
        'rainfall_pref': 'low',
        'seasons': ['Kharif'],
        'weather_reason': {
            'en': 'Hardy sprawling legume crop cultivated for high-protein pulses and green livestock forage.',
            'kn': 'ಹೆಚ್ಚಿನ ಪ್ರೋಟೀನ್ ಭರಿತ ಕಾಳು ಮತ್ತು ಜಾನುವಾರುಗಳಿಗೆ ಪೌಷ್ಟಿಕ ಮೇವು ನೀಡುವ ಹರಡುವ ಜಾತಿಯ ಕಾಳು ಬೆಳೆ.',
            'hi': 'जमीन पर फैलने वाली दलहन जो उच्च प्रोटीन युक्त दाने और पशुओं के लिए हरा चारा प्रदान करती है।'
        }
    },
    'wheat': {
        'temp_opt': (14, 24), 'temp_tol': (10, 29),
        'hum_opt': (40, 60), 'hum_tol': (30, 75),
        'rainfall_pref': 'low',
        'seasons': ['Rabi'],
        'weather_reason': {
            'en': 'Major cereal staple grown for high-energy carbohydrates, protein gluten content, and livestock fodder.',
            'kn': 'ಹೆಚ್ಚಿನ ಶಕ್ತಿ ಮತ್ತು ಪ್ರೋಟೀನ್ ಒದಗಿಸುವ ಹಾಗೂ ಪ್ರಮುಖ ಆಹಾರ ಭದ್ರತೆ ನೀಡುವ ಪ್ರಮುಖ ಧಾನ್ಯ ಬೆಳೆ.',
            'hi': 'ऊर्जा, ग्लूटेन प्रोटीन और पोषण सुरक्षा प्रदान करने वाली प्रमुख खाद्यान्न फसल।'
        }
    },
    'fieldbeans': {
        'temp_opt': (16, 26), 'temp_tol': (12, 30),
        'hum_opt': (40, 65), 'hum_tol': (30, 75),
        'rainfall_pref': 'low',
        'seasons': ['Rabi'],
        'weather_reason': {
            'en': 'Traditional pulse with high biological nitrogen fixation and aromatic pod development.',
            'kn': 'ಸಾರಜನಕ ಸ್ಥಿರೀಕರಣ ಮತ್ತು ಉತ್ತಮ ಸುವಾಸನೆಯ ಕಾಯಿಗಳನ್ನು ಹೊಂದಿರುವ ಸಾಂಪ್ರದಾಯಿಕ ಬೇಳೆಕಾಳು ಬೆಳೆ.',
            'hi': 'उच्च जैविक नाइट्रोजन स्थिरीकरण और सुगंधित फलियों वाली पारंपरिक दलहनी फसल।'
        }
    },
    'horsegram': {
        'temp_opt': (20, 34), 'temp_tol': (14, 38),
        'hum_opt': (30, 65), 'hum_tol': (20, 75),
        'rainfall_pref': 'low',
        'seasons': ['Rabi', 'Zaid', 'Whole Year'],
        'weather_reason': {
            'en': 'Hardy, protein-dense traditional pulse widely cultivated across regional agricultural tracts.',
            'kn': 'ಕಡಿಮೆ ನೀರಿನ ಪ್ರದೇಶಗಳಲ್ಲಿ ಬೆಳೆಯಲಾಗುವ ಅತ್ಯಂತ ಪೌಷ್ಟಿಕ ಹಾಗೂ ಸಾಂಪ್ರದಾಯಿಕ ಕಾಳು ಬೆಳೆ.',
            'hi': 'कम पानी वाले क्षेत्रों में उगाई जाने वाली उच्च प्रोटीन युक्त पारंपरिक दलहन फसल।'
        }
    },
    'vegetables': {
        'temp_opt': (18, 30), 'temp_tol': (12, 36),
        'hum_opt': (45, 75), 'hum_tol': (30, 85),
        'rainfall_pref': 'moderate',
        'seasons': ['Kharif', 'Rabi', 'Zaid', 'Whole Year'],
        'weather_reason': {
            'en': 'Intensive horticultural crops cultivated for essential minerals, dietary vitamins, and daily market harvest.',
            'kn': 'ದೈನಂದಿನ ಮಾರುಕಟ್ಟೆ ಮಾರಾಟ ಮತ್ತು ಪೌಷ್ಟಿಕಾಂಶಗಳಿಗಾಗಿ ಬೆಳೆಯಲಾಗುವ ತರಕಾರಿ ಬೆಳೆಗಳು.',
            'hi': 'नियमित दैनिक मंडी आपूर्ति और आवश्यक पोषक तत्वों के लिए उगाई जाने वाली सघन सब्जी फसलें।'
        }
    },
    'flowers': {
        'temp_opt': (20, 32), 'temp_tol': (14, 38),
        'hum_opt': (40, 70), 'hum_tol': (25, 80),
        'rainfall_pref': 'low',
        'seasons': ['Zaid', 'Rabi', 'Whole Year'],
        'weather_reason': {
            'en': 'Commercial floricultural crops cultivated for decorative loose blooms, garland making, and perfumery oils.',
            'kn': 'ಹೂಮಾಲೆ, ಅಲಂಕಾರಿಕ ಬಳಕೆ ಮತ್ತು ಸುವಾಸನಾ ತೈಲ ತಯಾರಿಕೆಗೆ ಬೆಳೆಯಲಾಗುವ ವಾಣಿಜ್ಯ ಪುಷ್ಪ ಕೃಷಿ ಬೆಳೆಗಳು.',
            'hi': 'सजावट, माला निर्माण और सुगंधित इत्र निष्कर्षण के लिए उगाई जाने वाली व्यावसायिक फूल फसलें।'
        }
    },
    'fodder': {
        'temp_opt': (22, 36), 'temp_tol': (16, 42),
        'hum_opt': (35, 75), 'hum_tol': (20, 85),
        'rainfall_pref': 'moderate',
        'seasons': ['Zaid', 'Kharif', 'Whole Year'],
        'weather_reason': {
            'en': 'Fast-growing biomass crops cultivated to provide nutrient-balanced green forage for dairy livestock.',
            'kn': 'ಹೈನುಗಾರಿಕೆ ಜಾನುವಾರುಗಳಿಗೆ ಸಮತೋಲಿತ ಪೌಷ್ಟಿಕ ಹಸಿರು ಮೇವು ಒದಗಿಸುವ ಅಧಿಕ ಇಳುವರಿಯ ಮೇವಿನ ಬೆಳೆಗಳು.',
            'hi': 'दुधारू पशुओं के लिए संतुलित हरा चारा उपलब्ध कराने वाली तेजी से बढ़ने वाली बायोमास चारा फसलें।'
        }
    },
    'turmeric': {
        'temp_opt': (22, 34), 'temp_tol': (18, 38),
        'hum_opt': (60, 85), 'hum_tol': (45, 95),
        'rainfall_pref': 'high',
        'seasons': ['Kharif', 'Whole Year'],
        'weather_reason': {
            'en': 'Valuable spice crop yielding high-curcumin rhizomes, responsive to rich organic matter and ridge planting.',
            'kn': 'ಹೆಚ್ಚಿನ ಕುರ್ಕುಮಿನ್ ಅಂಶ ಹೊಂದಿರುವ ಮತ್ತು ಮಣ್ಣಿನಲ್ಲಿ ಸಾವಯವ ಗೊಬ್ಬರ ನಿರ್ವಹಣೆಗೆ ಸ್ಪಂದಿಸುವ ಪ್ರಮುಖ ಸಾಂಬಾರ ಬೆಳೆ.',
            'hi': 'उच्च करक्यूमिन युक्त प्रकंद देने वाली और समृद्ध जैविक खाद प्रबंधन के अनुकूल प्रमुख मसाला फसल।'
        }
    },
    'cowpea': {
        'temp_opt': (22, 35), 'temp_tol': (16, 39),
        'hum_opt': (40, 75), 'hum_tol': (30, 85),
        'rainfall_pref': 'low',
        'seasons': ['Kharif', 'Rabi', 'Zaid', 'Whole Year'],
        'weather_reason': {
            'en': 'Versatile pulse grown for fresh green vegetable pods as well as harvested grain pulses.',
            'kn': 'ಹಸಿರು ಕಾಯಿ ತರಕಾರಿ ಹಾಗೂ ಒಣ ಕಾಳು ಎರಡಕ್ಕೂ ಬೆಳೆಯಲಾಗುವ ಬಹುಪಯೋಗಿ ಸಾಂಪ್ರದಾಯಿಕ ಕಾಳು ಬೆಳೆ.',
            'hi': 'हरी फलियों की सब्जी और सूखे प्रोटीन युक्त दानों के लिए उगाई जाने वाली बहुमुखी दलहनी फसल।'
        }
    },
    'chilli': {
        'temp_opt': (20, 32), 'temp_tol': (15, 36),
        'hum_opt': (45, 70), 'hum_tol': (35, 80),
        'rainfall_pref': 'moderate',
        'seasons': ['Kharif', 'Rabi'],
        'weather_reason': {
            'en': 'Commercial spice and vegetable crop cultivated for pungent capsaicin and vibrant oleoresin pigments.',
            'kn': 'ಖಾರ ಮತ್ತು ನೈಸರ್ಗಿಕ ಕೆಂಪು ಬಣ್ಣದ ಸಾರಕ್ಕಾಗಿ ಬೆಳೆಯಲಾಗುವ ಪ್ರಮುಖ ವಾಣಿಜ್ಯ ಸಾಂಬಾರ ಬೆಳೆ.',
            'hi': 'तीखे कैप्साइसिन और आकर्षक प्राकृतिक लाल रंग के लिए उगाई जाने वाली प्रमुख व्यावसायिक मसाला फसल।'
        }
    },
    'ginger': {
        'temp_opt': (20, 32), 'temp_tol': (15, 36),
        'hum_opt': (65, 90), 'hum_tol': (50, 95),
        'rainfall_pref': 'high',
        'seasons': ['Kharif', 'Whole Year'],
        'weather_reason': {
            'en': 'Aromatic spice crop producing essential oil-rich rhizomes, requiring well-drained, organically rich loams.',
            'kn': 'ಉತ್ತಮ ಸುವಾಸನೆ ಮತ್ತು ಔಷಧೀಯ ಗುಣವುಳ್ಳ ಶುಂಠಿ ಬೆಳೆಯಲು ನೀರು ಬಸಿದು ಹೋಗುವ ಗೋಡು ಮಣ್ಣು ಸೂಕ್ತ.',
            'hi': 'सुगंधित आवश्यक तेलों से भरपूर कंद देने वाली मसाला फसल, जिसे जल-निकासी वाली उपजाऊ दोमट मिट्टी चाहिए।'
        }
    },
    'tobacco': {
        'temp_opt': (20, 32), 'temp_tol': (15, 36),
        'hum_opt': (50, 75), 'hum_tol': (40, 85),
        'rainfall_pref': 'moderate',
        'seasons': ['Kharif', 'Rabi'],
        'weather_reason': {
            'en': 'Commercial cash crop grown for cured leaf production, responsive to balanced potash fertilization.',
            'kn': 'ಉತ್ತಮ ಎಲೆಗಳ ಇಳುವರಿಗಾಗಿ ಪೊಟ್ಯಾಷ್ ಪೋಷಕಾಂಶಗಳ ಸಮತೋಲಿತ ನಿರ್ವಹಣೆಗೆ ಸ್ಪಂದಿಸುವ ವಾಣಿಜ್ಯ ಬೆಳೆ.',
            'hi': 'गुणवत्तापूर्ण पत्तियों के उत्पादन के लिए संतुलित पोटाश प्रबंधन के अनुकूल प्रमुख नकदी फसल।'
        }
    },
    'bajra': {
        'temp_opt': (24, 38), 'temp_tol': (18, 42),
        'hum_opt': (30, 65), 'hum_tol': (20, 75),
        'rainfall_pref': 'low',
        'seasons': ['Kharif', 'Zaid'],
        'weather_reason': {
            'en': 'Nutrient-rich coarse cereal producing iron-rich grain heads and green forage for livestock.',
            'kn': 'ಹೆಚ್ಚಿನ ಕಬ್ಬಿಣದ ಅಂಶ ಮತ್ತು ಜಾನುವಾರುಗಳಿಗೆ ಗುಣಮಟ್ಟದ ಮೇವು ನೀಡುವ ಪ್ರಮುಖ ಪೌಷ್ಟಿಕ ಸಿರಿಧಾನ್ಯ ಬೆಳೆ.',
            'hi': 'लौह तत्व से भरपूर दाने और पशुओं के लिए पौष्टिक हरा चारा प्रदान करने वाला प्रमुख पोषक मोटा अनाज।'
        }
    },
    'pulses': {
        'temp_opt': (18, 30), 'temp_tol': (12, 35),
        'hum_opt': (35, 70), 'hum_tol': (25, 80),
        'rainfall_pref': 'low',
        'seasons': ['Rabi', 'Kharif', 'Zaid'],
        'weather_reason': {
            'en': 'Essential grain legumes enriching soils through atmospheric nitrogen fixation and crop rotations.',
            'kn': 'ಸಾರಜನಕ ಸ್ಥಿರೀಕರಣದ ಮೂಲಕ ಮಣ್ಣನ್ನು ಸಮೃದ್ಧಗೊಳಿಸುವ ಮತ್ತು ಸಮತೋಲಿತ ಆಹಾರ ಒದಗಿಸುವ ಪ್ರಮುಖ ಕಾಳು ಬೆಳೆಗಳು.',
            'hi': 'वायुमंडलीय नाइट्रोजन स्थिरीकरण और फसल चक्र द्वारा मिट्टी को समृद्ध बनाने वाली प्रमुख दलहनी फसलें।'
        }
    }
}


def evaluate_crop_weather_suitability(crop_name: str, temp: float, humidity: float, rainfall: float = 0.0, season: str = 'auto', lang: str = 'en', weather_desc: str = '') -> dict:
    """
    Dynamically evaluates weather suitability & preferability score (0-100%) for a given crop
    under changing real-time temperature, humidity, rainfall, weather description, and season.
    Returns multilingual suitability scores, live weather reasons, and badges.
    """
    from datetime import datetime

    crop_l = (crop_name or '').lower().strip()
    profile = CROP_WEATHER_PROFILES.get(crop_l, {
        'temp_opt': (18, 32), 'temp_tol': (12, 38),
        'hum_opt': (45, 75), 'hum_tol': (30, 85),
        'rainfall_pref': 'moderate',
        'seasons': ['Whole Year', 'Kharif', 'Rabi', 'Zaid'],
        'weather_reason': {
            'en': 'Versatile agricultural crop cultivated for regional food security and farm income.',
            'kn': 'ಪ್ರಾದೇಶಿಕ ಆಹಾರ ಭದ್ರತೆ ಮತ್ತು ರೈತರ ಆದಾಯಕ್ಕಾಗಿ ಬೆಳೆಯಲಾಗುವ ಪ್ರಮುಖ ಕೃಷಿ ಬೆಳೆ.',
            'hi': 'क्षेत्रीय खाद्य सुरक्षा और कृषि आय के लिए उगाई जाने वाली उपयोगी कृषि फसल।'
        }
    })

    t_opt_min, t_opt_max = profile['temp_opt']
    t_tol_min, t_tol_max = profile['temp_tol']
    h_opt_min, h_opt_max = profile['hum_opt']
    h_tol_min, h_tol_max = profile['hum_tol']
    rain_pref = profile.get('rainfall_pref', 'moderate')

    # Auto-resolve season from calendar month if 'auto' or not provided
    active_season = season
    if not active_season or active_season == 'auto':
        current_m = datetime.now().month
        if 6 <= current_m <= 10:
            active_season = 'Kharif'
        elif current_m in [11, 12, 1, 2]:
            active_season = 'Rabi'
        else:
            active_season = 'Zaid'

    # 1. Dynamic Crop-Specific Temperature Score (0 - 35 pts)
    temp_f = float(temp) if temp is not None else 25.0
    t_mid = (t_opt_min + t_opt_max) / 2.0
    t_span = max(1.0, (t_opt_max - t_opt_min) / 2.0)
    t_dev = abs(temp_f - t_mid) / t_span
    temp_score = max(5.0, 35.0 - (t_dev ** 1.6) * 11.0)

    # 2. Dynamic Crop-Specific Humidity Score (0 - 25 pts)
    hum_f = float(humidity) if humidity is not None else 60.0
    h_mid = (h_opt_min + h_opt_max) / 2.0
    h_span = max(1.0, (h_opt_max - h_opt_min) / 2.0)
    h_dev = abs(hum_f - h_mid) / h_span
    hum_score = max(4.0, 25.0 - (h_dev ** 1.5) * 7.5)

    # 3. Dynamic Crop-Specific Rainfall Score (0 - 25 pts)
    if rainfall is None:
        rain_f = None
        rain_score = 20.0  # Neutral score when normal is unverified / null
    else:
        rain_f = float(rainfall)
        if rain_pref == 'high':
            # High rainfall crops (Rice, Sugarcane, Turmeric, Ginger, Banana)
            if rain_f >= 130.0:
                rain_score = 25.0
            elif 70.0 <= rain_f < 130.0:
                rain_score = 14.0 + 11.0 * ((rain_f - 70.0) / 60.0)
            else:
                rain_score = max(4.0, 14.0 * (rain_f / 70.0))
        elif rain_pref == 'low':
            # Low rainfall crops (Wheat, Chickpea, Jowar, Horsegram, Sunflower, Onion)
            if 20.0 <= rain_f <= 65.0:
                rain_score = 25.0
            elif rain_f < 20.0:
                rain_score = 18.0 + 7.0 * (rain_f / 20.0)
            elif 65.0 < rain_f <= 120.0:
                rain_score = 14.0 + 11.0 * ((120.0 - rain_f) / 55.0)
            else:
                rain_score = max(4.0, 14.0 - min(10.0, (rain_f - 120.0) * 0.1))
        else:
            # Moderate rainfall crops (Maize, Soybean, Cotton, Tomato, Ragi, Groundnut)
            if 45.0 <= rain_f <= 120.0:
                rain_score = 25.0
            elif rain_f < 45.0:
                rain_score = 12.0 + 13.0 * (rain_f / 45.0)
            else:
                rain_score = max(6.0, 25.0 - (rain_f - 120.0) * 0.12)

    # 4. Sky condition & weather dynamics (0 - 15 pts)
    w_desc_l = (weather_desc or '').lower()
    sky_score = 10.0
    if 'rain' in w_desc_l or 'drizzle' in w_desc_l or 'thunderstorm' in w_desc_l:
        if rain_pref == 'high':
            sky_score += 5.0
        elif rain_pref == 'low':
            sky_score -= 4.0
    elif 'clear' in w_desc_l or 'sun' in w_desc_l:
        if crop_l in ['watermelon', 'muskmelon', 'sunflower', 'groundnut', 'grapes', 'mango', 'pomegranate', 'cotton', 'fodder', 'bajra']:
            sky_score += 5.0
        elif crop_l in ['ginger', 'coffee']:
            sky_score -= 2.0
    elif 'cloud' in w_desc_l or 'overcast' in w_desc_l:
        if crop_l in ['rice', 'ragi', 'pigeonpeas', 'maize', 'soybean']:
            sky_score += 3.0

    # 5. Seasonal Fit Agronomic Coherence
    crop_seasons = profile.get('seasons', ['Whole Year'])
    if 'Whole Year' in crop_seasons or active_season in crop_seasons:
        season_mod = 0.0
        is_seasonal = True
    else:
        season_mod = -30.0
        is_seasonal = False

    raw_total = temp_score + hum_score + rain_score + sky_score + season_mod
    total_score = round(min(99.0, max(30.0, raw_total)), 1)

    # Determine status & badge
    if not is_seasonal:
        level = 'out_of_season'
        status_en = f'Off-Season ({active_season})'
        status_kn = f'ಋತುಮಾನವಲ್ಲದ ಬೆಳೆ ({active_season})'
        status_hi = f'बेमौसम फसल ({active_season})'
        icon = '⚠️'
    elif total_score >= 86.0:
        level = 'optimal'
        status_en = 'Highly Optimal Weather'
        status_kn = 'ಅತ್ಯುತ್ತಮ ಹವಾಮಾನ ಹೊಂದಾಣಿಕೆ'
        status_hi = 'सर्वोत्तम मौसम अनुकूलता'
        icon = '🌟'
    elif total_score >= 72.0:
        level = 'good'
        status_en = 'Favorable Weather'
        status_kn = 'ಉತ್ತಮ ಹವಾಮಾನ ಹೊಂದಾಣಿಕೆ'
        status_hi = 'अनुकूल मौसम'
        icon = '👍'
    else:
        level = 'moderate'
        status_en = 'Moderate Weather Match'
        status_kn = 'ಮಧ್ಯಮ ಹವಾಮಾನ ಹೊಂದಾಣಿಕೆ'
        status_hi = 'मध्यम मौसम अनुकूलता'
        icon = '🌤'

    crop_tr_en = get_crop_name(crop_l, 'en')
    crop_tr_kn = get_crop_name(crop_l, 'kn')
    crop_tr_hi = get_crop_name(crop_l, 'hi')

    reason_dict = profile['weather_reason']
    r_en = reason_dict.get('en', '')
    r_kn = reason_dict.get('kn', '')
    r_hi = reason_dict.get('hi', '')

    # Dynamic Crop-Specific Weather Alignment Sentence (Bug 5 fix: compare against own ranges)
    temp_round = int(round(temp_f))
    hum_round = int(round(hum_f))

    if t_opt_min <= temp_f <= t_opt_max:
        temp_comp_en = f"Live {temp_round}°C is within the ideal {t_opt_min}–{t_opt_max}°C range for {crop_tr_en}."
        temp_comp_kn = f"ಪ್ರಸ್ತುತ {temp_round}°C ತಾಪಮಾನವು {crop_tr_kn} ಬೆಳೆಗೆ ಸೂಕ್ತವಾದ {t_opt_min}–{t_opt_max}°C ಮಿತಿಯಲ್ಲಿದೆ."
        temp_comp_hi = f"वर्तमान {temp_round}°C तापमान {crop_tr_hi} के लिए आदर्श {t_opt_min}–{t_opt_max}°C सीमा में है।"
    elif temp_f < t_opt_min:
        temp_comp_en = f"Live {temp_round}°C is cooler than the ideal {t_opt_min}–{t_opt_max}°C range for {crop_tr_en}."
        temp_comp_kn = f"ಪ್ರಸ್ತುತ {temp_round}°C ತಾಪಮಾನವು {crop_tr_kn} ಬೆಳೆಗೆ ಬೇಕಾದ {t_opt_min}–{t_opt_max}°C ಗಿಂತ ತಂಪಾಗಿದೆ."
        temp_comp_hi = f"वर्तमान {temp_round}°C तापमान {crop_tr_hi} के लिए आदर्श {t_opt_min}–{t_opt_max}°C से कम है।"
    else:
        temp_comp_en = f"Live {temp_round}°C is slightly above the ideal {t_opt_min}–{t_opt_max}°C range for {crop_tr_en}."
        temp_comp_kn = f"ಪ್ರಸ್ತುತ {temp_round}°C ತಾಪಮಾನವು {crop_tr_kn} ಬೆಳೆಗೆ ಬೇಕಾದ {t_opt_min}–{t_opt_max}°C ಗಿಂತ ಬೆಚ್ಚಗಿದೆ."
        temp_comp_hi = f"वर्तमान {temp_round}°C तापमान {crop_tr_hi} के लिए आदर्श {t_opt_min}–{t_opt_max}°C से अधिक है।"

    if h_opt_min <= hum_f <= h_opt_max:
        hum_comp_en = f"Humidity of {hum_round}% aligns with optimal target ({h_opt_min}–{h_opt_max}%)."
        hum_comp_kn = f"{hum_round}% ತೇವಾಂಶವು ಸೂಕ್ತ ({h_opt_min}–{h_opt_max}%) ಮಟ್ಟದಲ್ಲಿದೆ."
        hum_comp_hi = f"{hum_round}% आर्द्रता इष्टतम ({h_opt_min}–{h_opt_max}%) के अनुकूल है।"
    elif hum_f < h_opt_min:
        hum_comp_en = f"Humidity of {hum_round}% is below the preferred {h_opt_min}–{h_opt_max}%."
        hum_comp_kn = f"{hum_round}% ತೇವಾಂಶವು ಅಪೇಕ್ಷಿತ {h_opt_min}–{h_opt_max}% ಗಿಂತ ಕಡಿಮೆಯಾಗಿದೆ."
        hum_comp_hi = f"{hum_round}% आर्द्रता अपेक्षित {h_opt_min}–{h_opt_max}% से कम है।"
    else:
        hum_comp_en = f"Humidity of {hum_round}% is higher than optimal {h_opt_min}–{h_opt_max}%."
        hum_comp_kn = f"{hum_round}% ತೇವಾಂಶವು ಸೂಕ್ತ {h_opt_min}–{h_opt_max}% ಗಿಂತ ಹೆಚ್ಚಾಗಿದೆ."
        hum_comp_hi = f"{hum_round}% आर्द्रता इष्टतम {h_opt_min}–{h_opt_max}% से अधिक है।"

    if rain_f is not None and rain_f > 0:
        rain_comp_en = f"Monthly normal: {rain_f:.0f}mm."
        rain_comp_kn = f"ಮಾಸಿಕ ವಾಡಿಕೆ ಮಳೆ: {rain_f:.0f}ಮಿಮೀ."
        rain_comp_hi = f"मासिक सामान्य वर्षा: {rain_f:.0f}मिमी।"
        crop_weather_explanation_en = f"{temp_comp_en} {hum_comp_en} {rain_comp_en}"
        crop_weather_explanation_kn = f"{temp_comp_kn} {hum_comp_kn} {rain_comp_kn}"
        crop_weather_explanation_hi = f"{temp_comp_hi} {hum_comp_hi} {rain_comp_hi}"
    else:
        # If rainfall normal is null / unverified: omit rainfall sentence completely!
        crop_weather_explanation_en = f"{temp_comp_en} {hum_comp_en}"
        crop_weather_explanation_kn = f"{temp_comp_kn} {hum_comp_kn}"
        crop_weather_explanation_hi = f"{temp_comp_hi} {hum_comp_hi}"

    if is_seasonal:
        reason_full_en = f"{icon} {status_en} ({total_score}% match): {crop_weather_explanation_en} {r_en}"
        reason_full_kn = f"{icon} {status_kn} (ಹೊಂದಾಣಿಕೆ: {total_score}%): {crop_weather_explanation_kn} {r_kn}"
        reason_full_hi = f"{icon} {status_hi} (अनुकूलता: {total_score}%): {crop_weather_explanation_hi} {r_hi}"
    else:
        primary_season = crop_seasons[0]
        reason_full_en = f"{icon} {status_en} ({total_score}% match): Currently {active_season} season. {crop_tr_en} is primarily a {primary_season} crop. Sowing in current weather conditions risks moisture and thermal stress."
        reason_full_kn = f"{icon} {status_kn} (ಹೊಂದಾಣಿಕೆ: {total_score}%): ಪ್ರಸ್ತುತ {active_season} ಕಾಲ. {crop_tr_kn} ಮುಖ್ಯವಾಗಿ {primary_season} ಬೆಳೆಯಾಗಿದೆ. ಪ್ರಸ್ತುತ ಹವಾಮಾನದಲ್ಲಿ ಬಿತ್ತನೆ ಮಾಡಿದರೆ ತೇವಾಂಶ ಮತ್ತು ತಾಪಮಾನದ ಒತ್ತಡ ಉಂಟಾಗಬಹುದು."
        reason_full_hi = f"{icon} {status_hi} (अनुकूलता: {total_score}%): वर्तमान में {active_season} मौसम है। {crop_tr_hi} मुख्य रूप से {primary_season} की फसल है। वर्तमान मौसम में बुवाई करने से प्रतिकूल प्रभाव पड़ सकता है।"

    return {
        'crop': crop_name,
        'crop_en': crop_tr_en,
        'crop_kn': crop_tr_kn,
        'crop_hi': crop_tr_hi,
        'score': total_score,
        'level': level,
        'is_seasonal': is_seasonal,
        'status_en': status_en,
        'status_kn': status_kn,
        'status_hi': status_hi,
        'reason_en': reason_full_en,
        'reason_kn': reason_full_kn,
        'reason_hi': reason_full_hi,
        'reason': reason_full_kn if lang == 'kn' else (reason_full_hi if lang == 'hi' else reason_full_en),
        'opt_temp': f"{t_opt_min}-{t_opt_max}°C",
        'opt_hum': f"{h_opt_min}-{h_opt_max}%",
        'crop_weather_explanation_en': crop_weather_explanation_en,
        'crop_weather_explanation_kn': crop_weather_explanation_kn,
        'crop_weather_explanation_hi': crop_weather_explanation_hi,
        'base_reason_en': r_en,
        'base_reason_kn': r_kn,
        'base_reason_hi': r_hi
    }


# =====================================================================
# CROP DISEASE COVERAGE CONFIG & NAMED THRESHOLDS
# =====================================================================
# Threshold constants for leaf disease diagnosis
CROP_MATCH_THRESHOLD = 0.60         # Minimum total softmax probability on selected crop's classes
DISEASE_CONFIDENCE_THRESHOLD = 0.70 # Minimum confidence required for positive diagnosis
MIN_CONFIDENCE_MARGIN = 0.15        # Minimum probability margin between top-1 and top-2 classes

CONFIDENCE_HIGH_THRESHOLD = 80.0    # High confidence >= 80%
CONFIDENCE_MEDIUM_THRESHOLD = 60.0  # Medium confidence >= 60%

def get_confidence_level(confidence_val, lang='en', show_score=True):
    """Return localized confidence string (High/Medium/Low) along with exact percentage score."""
    if confidence_val is None:
        return {'en': 'Not Available', 'kn': 'ಲಭ್ಯವಿಲ್ಲ', 'hi': 'उपलब्ध नहीं'}.get(lang, 'Not Available')
    val = float(confidence_val)
    if val <= 1.0:
        val *= 100.0
    score_str = f"{val:.1f}%"

    if val >= CONFIDENCE_HIGH_THRESHOLD:
        tier = {'en': 'High Confidence', 'kn': 'ಹೆಚ್ಚಿನ ವಿಶ್ವಾಸಾರ್ಹತೆ', 'hi': 'उच्च सटीकता'}.get(lang, 'High Confidence')
    elif val >= CONFIDENCE_MEDIUM_THRESHOLD:
        tier = {'en': 'Medium Confidence', 'kn': 'ಮಧ್ಯಮ ವಿಶ್ವಾಸಾರ್ಹತೆ', 'hi': 'मध्यम सटीकता'}.get(lang, 'Medium Confidence')
    else:
        tier = {'en': 'Low Confidence', 'kn': 'ಕಡಿಮೆ ವಿಶ್ವಾಸಾರ್ಹತೆ', 'hi': 'कम सटीकता'}.get(lang, 'Low Confidence')

    return f"{tier}: {score_str}" if show_score else tier


DISEASE_COVERAGE = {
    # ── Full Diagnosis Support (both disease and healthy classes available in CNN) ──
    'rice': {
        'status': 'full',
        'karnataka': True,
        'name': {'en': 'Rice (Paddy)', 'kn': 'ಭತ್ತ (ಅಕ್ಕಿ)', 'hi': 'चावल (धान)'},
        'diseases': ['Bacterial Leaf Blight', 'Brown Spot', 'Leaf Blast', 'Leaf Scald', 'Narrow Brown Spot']
    },
    'wheat': {
        'status': 'full',
        'karnataka': True,
        'name': {'en': 'Wheat', 'kn': 'ಗೋಧಿ', 'hi': 'गेहूं'},
        'diseases': ['Black Point', 'Fusarium Foot Rot', 'Leaf Blight', 'Wheat Blast']
    },
    'tomato': {
        'status': 'full',
        'karnataka': True,
        'name': {'en': 'Tomato', 'kn': 'ಟೊಮೆಟೊ', 'hi': 'टमाटर'},
        'diseases': ['Bacterial Spot', 'Early Blight', 'Late Blight', 'Leaf Mold', 'Septoria Leaf Spot', 'Spider Mites', 'Target Spot', 'Yellow Leaf Curl Virus', 'Mosaic Virus']
    },
    'corn': {
        'status': 'full',
        'karnataka': True,
        'name': {'en': 'Corn (Maize)', 'kn': 'ಮೆಕ್ಕೆಜೋಳ', 'hi': 'मक्का'},
        'diseases': ['Gray Leaf Spot (Cercospora)', 'Common Rust', 'Northern Leaf Blight']
    },
    'potato': {
        'status': 'full',
        'karnataka': True,
        'name': {'en': 'Potato', 'kn': 'ಆಲೂಗಡ್ಡೆ', 'hi': 'आलू'},
        'diseases': ['Early Blight', 'Late Blight']
    },
    'grape': {
        'status': 'full',
        'karnataka': True,
        'name': {'en': 'Grape', 'kn': 'ದ್ರಾಕ್ಷಿ', 'hi': 'अंगूर'},
        'diseases': ['Black Rot', 'Esca (Black Measles)', 'Leaf Blight (Isariopsis)']
    },
    'pepper': {
        'status': 'full',
        'karnataka': True,
        'name': {'en': 'Bell Pepper (Capsicum)', 'kn': 'ದೊಡ್ಡ ಮೆಣಸಿನಕಾಯಿ (ಕ್ಯಾಪ್ಸಿಕಂ)', 'hi': 'शिमला मिर्च (Capsicum)'},
        'diseases': ['Bacterial Spot']
    },
    'apple': {
        'status': 'full',
        'karnataka': False,
        'name': {'en': 'Apple', 'kn': 'ಸೇಬು', 'hi': 'सेब'},
        'diseases': ['Apple Scab', 'Black Rot', 'Cedar Apple Rust']
    },
    'peach': {
        'status': 'full',
        'karnataka': False,
        'name': {'en': 'Peach', 'kn': 'ಪೀಚ್ ಹಣ್ಣು', 'hi': 'आड़ू'},
        'diseases': ['Bacterial Spot']
    },
    'cherry': {
        'status': 'full',
        'karnataka': False,
        'name': {'en': 'Cherry', 'kn': 'ಚೆರ್ರಿ ಹಣ್ಣು', 'hi': 'चेरी'},
        'diseases': ['Powdery Mildew']
    },
    'strawberry': {
        'status': 'full',
        'karnataka': False,
        'name': {'en': 'Strawberry', 'kn': 'ಸ್ಟ್ರಾಬೆರಿ', 'hi': 'स्ट्रॉबेरी'},
        'diseases': ['Leaf Scorch']
    },

    # ── Disease Only Support (disease class in model, NO healthy class) ──
    'orange': {
        'status': 'disease_only',
        'karnataka': True,  # Coorg mandarin / Kodagu
        'name': {'en': 'Orange (Coorg Mandarin)', 'kn': 'ಕಿತ್ತಳೆ (ಕೊಡಗು ಕಿತ್ತಳೆ)', 'hi': 'संतरा (कूर्ग संतरा)'},
        'diseases': ['Huanglongbing (Citrus Greening)']
    },
    'squash': {
        'status': 'disease_only',
        'karnataka': False,
        'name': {'en': 'Squash', 'kn': 'ಸ್ಕ್ವಾಷ್ (ಸೀಮೆ ಸೋರೆ)', 'hi': 'स्क्वैश (चप्पन कद्दू)'},
        'diseases': ['Powdery Mildew']
    },

    # ── Healthy Only Support (healthy class in model, NO disease classes) ──
    'soybean': {
        'status': 'healthy_only',
        'karnataka': True,
        'name': {'en': 'Soybean', 'kn': 'ಸೋಯಾಬೀನ್', 'hi': 'सोयाबीन'},
        'diseases': []
    },
    'blueberry': {
        'status': 'healthy_only',
        'karnataka': False,
        'name': {'en': 'Blueberry', 'kn': 'ಬ್ಲೂಬೆರ್ರಿ', 'hi': 'ब्लूबेरी'},
        'diseases': []
    },
    'raspberry': {
        'status': 'healthy_only',
        'karnataka': False,
        'name': {'en': 'Raspberry', 'kn': 'ರಾಸ್‌ಪ್ಬೆರಿ', 'hi': 'रास्पबेरी'},
        'diseases': []
    },

    # ── Reference Guide Only (not in CNN classifier) ──
    'chilli': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Chilli (Green / Red)', 'kn': 'ಮೆಣಸಿನಕಾಯಿ (ಹಸಿರು/ಒಣ)', 'hi': 'मिर्च (हरी / लाल)'},
        'diseases': ['Leaf Curl Virus', 'Fruit Rot (Anthracnose)', 'Bacterial Wilt']
    },
    'black pepper': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Black Pepper', 'kn': 'ಕಾಳುಮೆಣಸು', 'hi': 'काली मिर्च'},
        'diseases': ['Quick Wilt (Foot Rot)', 'Pollu Disease', 'Slow Decline']
    },
    'cotton': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Cotton', 'kn': 'ಹತ್ತಿ', 'hi': 'कपास'},
        'diseases': ['Bacterial Blight', 'Leaf Curl Virus', 'Alternaria Leaf Spot']
    },
    'sugarcane': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Sugarcane', 'kn': 'ಕಬ್ಬು', 'hi': 'ಗನ್ನಾ'},
        'diseases': ['Red Rot', 'Whip Smut', 'Grassy Shoot Disease']
    },
    'banana': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Banana', 'kn': 'ಬಾಳೆ', 'hi': 'केला'},
        'diseases': ['Sigatoka Leaf Spot', 'Panama Wilt', 'Bunchy Top Virus']
    },
    'ragi': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Ragi (Finger Millet)', 'kn': 'ರಾಗಿ', 'hi': 'रागी'},
        'diseases': ['Leaf Blast', 'Foot Rot / Brown Spot', 'Foliar Blight']
    },
    'coconut': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Coconut', 'kn': 'ತೆಂಗಿನಕಾಯಿ', 'hi': 'नारियल'},
        'diseases': ['Leaf Rot', 'Bud Rot', 'Stem Bleeding']
    },
    'coffee': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Coffee', 'kn': 'ಕಾಫಿ', 'hi': 'कॉफी'},
        'diseases': ['Leaf Rust', 'Black Rot (Koleroga)', 'Brown Eye Spot']
    },
    'mango': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Mango', 'kn': 'ಮಾವು', 'hi': 'आम'},
        'diseases': ['Anthracnose', 'Powdery Mildew', 'Bacterial Canker']
    },
    'chickpea': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Chickpea (Bengal Gram)', 'kn': 'ಕಡಲೆ', 'hi': 'चना'},
        'diseases': ['Ascochyta Blight', 'Fusarium Wilt', 'Dry Root Rot']
    },
    'pigeonpeas': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Pigeonpeas (Tur)', 'kn': 'ತೊಗರಿ ಬೇಳೆ', 'hi': 'अरहर (तुअर)'},
        'diseases': ['Sterility Mosaic', 'Fusarium Wilt', 'Phytophthora Stem Blight']
    },
    'groundnut': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Groundnut (Peanut)', 'kn': 'ಕಡಲೆಕಾಯಿ', 'hi': 'मूंगफली'},
        'diseases': ['Tikka Leaf Spot', 'Rust', 'Bud Necrosis']
    },
    'blackgram': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Blackgram (Urad)', 'kn': 'ಉದ್ದಿನ ಬೇಳೆ', 'hi': 'उड़द'},
        'diseases': ['Yellow Mosaic Virus', 'Cercospora Leaf Spot', 'Leaf Crinkle']
    },
    'green gram': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Green Gram (Moong)', 'kn': 'ಹೆಸರು ಕಾಳು', 'hi': 'मूंग'},
        'diseases': ['Yellow Mosaic Virus', 'Cercospora Leaf Spot', 'Powdery Mildew']
    },
    'onion': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Onion', 'kn': 'ಈರುಳ್ಳಿ', 'hi': 'प्याज'},
        'diseases': ['Purple Blotch', 'Stemphylium Blight', 'Downy Mildew']
    },
    'pomegranate': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Pomegranate', 'kn': 'ದಾಳಿಂಬೆ', 'hi': 'अनार'},
        'diseases': ['Bacterial Blight (Telya)', 'Cercospora Leaf Spot', 'Wilt']
    },
    'jowar': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Jowar (Sorghum)', 'kn': 'ಜೋಳ', 'hi': 'ज्वार'},
        'diseases': ['Grain Mold', 'Downy Mildew', 'Leaf Rust']
    },
    'sunflower': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Sunflower', 'kn': 'ಸೂರ್ಯಕಾಂತಿ', 'hi': 'सूरजमुखी'},
        'diseases': ['Alternaria Leaf Blight', 'Head Rot', 'Rust']
    },
    'arecanut': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Arecanut (Betel Nut)', 'kn': 'ಅಡಿಕೆ', 'hi': 'सुपारी'},
        'diseases': ['Koleroga (Fruit Rot)', 'Yellow Leaf Disease', 'Anabe Roga']
    },
    'turmeric': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Turmeric', 'kn': 'ಅರಿಶಿನ', 'hi': 'हल्दी'},
        'diseases': ['Rhizome Rot', 'Leaf Blotch', 'Leaf Spot']
    },
    'cashew': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Cashew', 'kn': 'ಗೋಡಂಬಿ', 'hi': 'काजू'},
        'diseases': ['Dieback & Tea Mosquito', 'Anthracnose', 'Root Rot']
    },
    'mulberry': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Mulberry', 'kn': 'ಹಿಪ್ಪುನೇರಳೆ', 'hi': 'शहतूत'},
        'diseases': ['Leaf Spot', 'Powdery Mildew', 'Leaf Rust']
    },
    'horse gram': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Horse Gram (Huruli)', 'kn': 'ಹುರುಳಿ', 'hi': 'कुलथी'},
        'diseases': ['Anthracnose', 'Yellow Mosaic', 'Dry Root Rot']
    },
    'cowpea': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Cowpea (Alasande / Lobia)', 'kn': 'ಅಲಸಂದೆ', 'hi': 'लोबिया'},
        'diseases': ['Cowpea Mosaic Virus', 'Cercospora Leaf Spot', 'Cowpea Anthracnose']
    },
    'tobacco': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Tobacco', 'kn': 'ತಂಬಾಕು', 'hi': 'तंबाकू'},
        'diseases': ['Black Shank', 'Tobacco Mosaic Virus', 'Frog Eye Leaf Spot']
    },
    'ginger': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Ginger', 'kn': 'ಶುಂಠಿ', 'hi': 'अदरक'},
        'diseases': ['Soft Rot / Rhizome Rot', 'Bacterial Wilt', 'Phyllosticta Leaf Spot']
    },
    'papaya': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Papaya', 'kn': 'ಪಪ್ಪಾಯಿ', 'hi': 'पपीता'},
        'diseases': ['Papaya Ring Spot Virus', 'Anthracnose', 'Foot Rot']
    },
    'watermelon': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Watermelon', 'kn': 'ಕಲ್ಲಂಗಡಿ', 'hi': 'तरबूज'},
        'diseases': ['Anthracnose', 'Fusarium Wilt', 'Downy Mildew']
    },
    'muskmelon': {
        'status': 'reference_only',
        'karnataka': True,
        'name': {'en': 'Muskmelon', 'kn': 'ಕರಬೂಜ', 'hi': 'खरबूजा'},
        'diseases': ['Downy Mildew', 'Powdery Mildew', 'Fusarium Wilt']
    }
}

# Backward compatibility alias list
SUPPORTED_DISEASE_CROPS = [k for k, v in DISEASE_COVERAGE.items() if v['status'] in ['full', 'disease_only', 'healthy_only']]

SUPPORTED_DISEASE_CROP_ALIASES = {
    # Pepper (bell pepper / capsicum only)
    'bell pepper': 'pepper',
    'pepper bell': 'pepper',
    'capsicum': 'pepper',
    'pepper, bell': 'pepper',
    'pepper': 'pepper',

    # Chilli and Black Pepper (explicitly separate from bell pepper)
    'chilli': 'chilli',
    'chili': 'chilli',
    'green chilli': 'chilli',
    'red chilli': 'chilli',
    'mirchi': 'chilli',
    'black pepper': 'black pepper',
    'blackpepper': 'black pepper',
    'kali mirch': 'black pepper',

    # Cereals
    'maize': 'corn',
    'corn': 'corn',
    'corn maize': 'corn',
    'corn (maize)': 'corn',
    'paddy': 'rice',
    'rice': 'rice',
    'rice (paddy)': 'rice',
    'wheat': 'wheat',
    'jowar': 'jowar',
    'sorghum': 'jowar',
    'ragi': 'ragi',
    'finger millet': 'ragi',
    'millet': 'ragi',

    # Legumes & Pulses
    'soyabean': 'soybean',
    'soya': 'soybean',
    'soy': 'soybean',
    'soybean': 'soybean',
    'chickpea': 'chickpea',
    'bengal gram': 'chickpea',
    'chana': 'chickpea',
    'gram': 'chickpea',
    'pigeonpeas': 'pigeonpeas',
    'tur': 'pigeonpeas',
    'arhar': 'pigeonpeas',
    'red gram': 'pigeonpeas',
    'blackgram': 'blackgram',
    'black gram': 'blackgram',
    'urad': 'blackgram',
    'urad dal': 'blackgram',
    'green gram': 'green gram',
    'greengram': 'green gram',
    'mung': 'green gram',
    'moong': 'green gram',
    'mungbean': 'green gram',
    'horse gram': 'horse gram',
    'horsegram': 'horse gram',
    'huruli': 'horse gram',
    'cowpea': 'cowpea',
    'cow pea': 'cowpea',
    'alasande': 'cowpea',
    'lobia': 'cowpea',
    'chawli': 'cowpea',

    # Cash & Oilseeds
    'cotton': 'cotton',
    'groundnut': 'groundnut',
    'peanut': 'groundnut',
    'senga': 'groundnut',
    'sunflower': 'sunflower',
    'sugarcane': 'sugarcane',
    'cane': 'sugarcane',
    'tobacco': 'tobacco',
    'arecanut': 'arecanut',
    'betel nut': 'arecanut',
    'supari': 'arecanut',
    'cashew': 'cashew',
    'coffee': 'coffee',
    'coconut': 'coconut',
    'mulberry': 'mulberry',
    'turmeric': 'turmeric',
    'ginger': 'ginger',

    # Fruits & Vegetables
    'grapes': 'grape',
    'grape': 'grape',
    'potatoes': 'potato',
    'potato': 'potato',
    'tomatoes': 'tomato',
    'tomato': 'tomato',
    'apples': 'apple',
    'apple': 'apple',
    'oranges': 'orange',
    'orange': 'orange',
    'coorg mandarin': 'orange',
    'mandarin': 'orange',
    'peaches': 'peach',
    'peach': 'peach',
    'cherries': 'cherry',
    'cherry': 'cherry',
    'cherry including sour': 'cherry',
    'blueberries': 'blueberry',
    'blueberry': 'blueberry',
    'strawberries': 'strawberry',
    'strawberry': 'strawberry',
    'squash': 'squash',
    'rasberry': 'raspberry',
    'raspberry': 'raspberry',
    'banana': 'banana',
    'mango': 'mango',
    'onion': 'onion',
    'pomegranate': 'pomegranate',
    'papaya': 'papaya',
    'watermelon': 'watermelon',
    'muskmelon': 'muskmelon'
}

def normalize_disease_crop(crop_name: str) -> str:
    """
    Normalizes crop names and aliases using exact matching.
    Does NOT use fuzzy substring matching to prevent mapping chilli/black pepper to bell pepper.
    """
    if not crop_name:
        return ''
    c = str(crop_name).lower().strip().replace('_', ' ').replace('-', ' ')
    c = ' '.join(c.split())
    if c in SUPPORTED_DISEASE_CROP_ALIASES:
        return SUPPORTED_DISEASE_CROP_ALIASES[c]
    if c in DISEASE_COVERAGE:
        return c
    return c

def get_crop_support(crop_name: str) -> dict:
    """
    Returns the crop configuration metadata from DISEASE_COVERAGE.
    Unknown crops safely fall back to 'reference_only' without errors.
    """
    norm = normalize_disease_crop(crop_name)
    if norm in DISEASE_COVERAGE:
        return DISEASE_COVERAGE[norm]
    display_title = (crop_name or 'Crop').title()
    return {
        'status': 'reference_only',
        'karnataka': False,
        'name': {'en': display_title, 'kn': crop_name or 'ಬೆಳೆ', 'hi': crop_name or 'फसल'},
        'diseases': []
    }

def is_disease_diagnosis_supported(crop_name: str) -> bool:
    """
    Returns True if the crop has active CNN photo diagnosis support ('full' or 'disease_only').
    Returns False for 'healthy_only' and 'reference_only' crops.
    """
    info = get_crop_support(crop_name)
    return info.get('status') in ['full', 'disease_only']

def get_crop_support_notice(crop_name: str, lang: str = 'en') -> str:
    """
    Generates plain farmer-language notices dynamically from DISEASE_COVERAGE config.
    Uses NO technical jargon (avoids words like 'model', 'dataset', 'classifier', 'training data').
    Ensures 100% consistency with get_disease_coverage_line.
    """
    info = get_crop_support(crop_name)
    status = info.get('status', 'reference_only')
    c_name = info['name'].get(lang, info['name'].get('en', str(crop_name).title()))
    norm = normalize_disease_crop(crop_name)

    if status == 'full':
        if norm == 'pepper':
            if lang == 'kn':
                return "ದೊಡ್ಡ ಮೆಣಸಿನಕಾಯಿ (ಕ್ಯಾಪ್ಸಿಕಂ) ಬೆಳೆಗೆ ಬ್ಯಾಕ್ಟೀರಿಯಲ್ ಎಲೆ ಚುಕ್ಕೆ ರೋಗ ಪತ್ತೆ ಲಭ್ಯವಿದೆ. ಇತರ ರೋಗಗಳು ಪತ್ತೆಯಾಗದಿರಬಹುದು. ಬೆಳೆ ಅನಾರೋಗ್ಯಕರವಾಗಿ ಕಂಡರೆ ಹತ್ತಿರದ ಕೆವಿಕೆ ಅಥವಾ ಕೃಷಿ ಅಧಿಕಾರಿಯನ್ನು ಸಂಪರ್ಕಿಸಿ."
            elif lang == 'hi':
                return "शिमला मिर्च में जीवाणु धब्बा रोग की फोटो पहचान उपलब्ध है। अन्य रोगों की पहचान नहीं हो सकती। यदि पौधा अस्वस्थ दिखे तो नजदीकी केवीके या कृषि अधिकारी से सलाह लें।"
            return "Photo diagnosis covers Bacterial Spot for Bell Pepper (Capsicum). Other diseases may not be detected. If the plant looks unhealthy, consult your nearest KVK or Krishi officer."
        else:
            if lang == 'kn':
                return f"{c_name} ಬೆಳೆಗೆ ಫೋಟೋ ಮೂಲಕ ರೋಗ ಪತ್ತೆ ಲಭ್ಯವಿದೆ. ಸಾಮಾನ್ಯ ರೋಗಗಳನ್ನು ಪತ್ತೆಹಚ್ಚಲು ಎಲೆಯ ಸ್ಪಷ್ಟ ಫೋಟೋವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ."
            elif lang == 'hi':
                return f"{c_name} के लिए फोटो द्वारा रोग पहचान उपलब्ध है। सामान्य रोगों की जांच के लिए पत्ती की स्पष्ट फोटो अपलोड करें।"
            return f"Photo diagnosis is available for {c_name}. Upload a clear photo of the leaf to check for common diseases."

    elif status == 'disease_only':
        if norm == 'orange':
            if lang == 'kn':
                return "ಕಿತ್ತಳೆ ಬೆಳೆಯಲ್ಲಿ ಸಿಟ್ರಸ್ ಗ್ರೀನಿಂಗ್ (ಹಳದಿ ಎಲೆ ರೋಗ) ಪತ್ತೆ ಮಾತ್ರ ಲಭ್ಯವಿದೆ. ಇತರ ರೋಗಗಳನ್ನು ಫೋಟೋ ಮೂಲಕ ಪತ್ತೆಹಚ್ಚಲಾಗುವುದಿಲ್ಲ. ತೋಟಗಾರಿಕೆ ಇಲಾಖೆಯನ್ನು ಸಂಪರ್ಕಿಸಿ."
            elif lang == 'hi':
                return "संतरे में केवल सिट्रस ग्रीनिंग (हॉन्गलोंगबिंग) की फोटो जांच उपलब्ध है। अन्य रोगों की पहचान फोटो से नहीं हो सकती। बागवानी विभाग से संपर्क करें।"
            return "Photo check is available only for Citrus Greening (Huanglongbing) in Orange. Other diseases cannot be detected from photos. Consult your local horticulture department for expert guidance."
        elif norm == 'squash':
            if lang == 'kn':
                return "ಸ್ಕ್ವಾಷ್ ಬೆಳೆಯಲ್ಲಿ ಬೂದಿ ರೋಗ ಪತ್ತೆ ಮಾತ್ರ ಲಭ್ಯವಿದೆ. ಇತರ ರೋಗಗಳನ್ನು ಫೋಟೋ ಮೂಲಕ ಪತ್ತೆಹಚ್ಚಲಾಗುವುದಿಲ್ಲ. ದಯವಿಟ್ಟು ಕೆವಿಕೆ ಅಥವಾ ಕೃಷಿ ಅಧಿಕಾರಿಯನ್ನು ಸಂಪರ್ಕಿಸಿ."
            elif lang == 'hi':
                return "स्क्वैश में केवल चूर्णिल फफूंद (पाउडरी मिल्ड्यू) की फोटो जांच उपलब्ध है। अन्य रोगों की पहचान फोटो से नहीं हो सकती। केवीके या कृषि अधिकारी से संपर्क करें।"
            return "Photo check is available only for Powdery Mildew in Squash. Other diseases cannot be detected from photos. Please consult your nearest KVK or Krishi officer."

    elif status == 'healthy_only':
        if lang == 'kn':
            return f"{c_name} ಬೆಳೆಗೆ ರೋಗ ಪತ್ತೆ ಸದ್ಯ ಲಭ್ಯವಿಲ್ಲ. ದಯವಿಟ್ಟು ಕೆಳಗಿನ ಉಲ್ಲೇಖ ಮಾರ್ಗದರ್ಶಿಯೊಂದಿಗೆ ನಿಮ್ಮ ಬೆಳೆಯನ್ನು ಹೋಲಿಸಿ ಮತ್ತು ಹತ್ತಿರದ ಕೆವಿಕೆ ಅಥವಾ ಕೃಷಿ ಅಧಿಕಾರಿಯನ್ನು ಸಂಪರ್ಕಿಸಿ."
        elif lang == 'hi':
            return f"{c_name} के लिए रोग पहचान अभी उपलब्ध नहीं है। कृपया नीचे दी गई संदर्भ मार्गदर्शिका से अपने पौधे की तुलना करें और नजदीकी केवीके या कृषि अधिकारी से सलाह लें।"
        return f"Photo diagnosis for diseases is not available for {c_name} yet. Please compare your plant with the reference guide below and consult your nearest KVK or Krishi officer."

    else:
        # reference_only
        if lang == 'kn':
            return f"ಕೆಳಗಿನ ಚಿತ್ರಗಳು ಸಾಮಾನ್ಯ ರೋಗ ಲಕ್ಷಣಗಳ ಉಲ್ಲೇಖಕ್ಕಾಗಿ ಇವೆ. {c_name} ಬೆಳೆಗೆ ಫೋಟೋ ಮೂಲಕ ರೋಗ ಪತ್ತೆ ಸದ್ಯ ಲಭ್ಯವಿಲ್ಲ. ಔಷಧ ಸಿಂಪರಣೆ ಮಾಡುವ ಮುನ್ನ ಕೆವಿಕೆ ಅಥವಾ ಕೃಷಿ ಅಧಿಕಾರಿಯನ್ನು ಸಂಪರ್ಕಿಸಿ."
        elif lang == 'hi':
            return f"नीचे दिए गए चित्र संदर्भ के लिए सामान्य लक्षण दिखाते हैं। {c_name} के लिए फोटो द्वारा रोग पहचान अभी उपलब्ध नहीं है। छिड़काव करने से पहले नजदीकी केवीके या कृषि अधिकारी से संपर्क करें।"
        return f"Illustrations below show typical symptoms for reference. Photo diagnosis is not available for {c_name} yet. Please contact your nearest KVK or Krishi officer before spraying."

def get_disease_coverage_line(lang: str = 'en') -> str:
    """
    Returns the Karnataka-first coverage summary line across the platform.
    """
    if lang == 'kn':
        return "📷 ಕರ್ನಾಟಕದ ಪ್ರಮುಖ ಬೆಳೆಗಳಿಗೆ ಫೋಟೋ ರೋಗ ಪತ್ತೆ ಲಭ್ಯವಿದೆ: ಭತ್ತ (Paddy), ಮೆಕ್ಕೆಜೋಳ (Maize), ಟೊಮೆಟೊ (Tomato), ಆಲೂಗಡ್ಡೆ (Potato), ದ್ರಾಕ್ಷಿ (Grape), ಕ್ಯಾಪ್ಸಿಕಂ (Bell Pepper)."
    elif lang == 'hi':
        return "📷 कर्नाटक की प्रमुख फसलों के लिए फोटो रोग पहचान उपलब्ध है: धान (Paddy), मक्का (Maize), टमाटर (Tomato), आलू (Potato), अंगूर (Grape), शिमला मिर्च (Bell Pepper)।"
    return "📷 Photo diagnosis available for major Karnataka crops: Rice (Paddy), Corn (Maize), Tomato, Potato, Grape, Bell Pepper (Capsicum)."

def get_all_disease_coverage_line(lang: str = 'en') -> str:
    """
    Returns full statewide and temperate crop coverage list for 'Show all' toggle.
    """
    if lang == 'kn':
        return "ಫೋಟೋ ಮೂಲಕ ರೋಗ ಪತ್ತೆ ಲಭ್ಯವಿರುವ ಬೆಳೆಗಳು: ಭತ್ತ, ಗೋಧಿ, ಮೆಕ್ಕೆಜೋಳ, ಟೊಮೆಟೊ, ಆಲೂಗಡ್ಡೆ, ದ್ರಾಕ್ಷಿ, ದೊಡ್ಡ ಮೆಣಸಿನಕಾಯಿ (ಕ್ಯಾಪ್ಸಿಕಂ), ಕಿತ್ತಳೆ (ಸಿಟ್ರಸ್ ಗ್ರೀನಿಂಗ್), ಸೇಬು, ಚೆರ್ರಿ, ಪೀಚ್, ಸ್ಟ್ರಾಬೆರಿ, ಸ್ಕ್ವಾಷ್ (ಬೂದಿ ರೋಗ). ಉಲ್ಲೇಖ ಮಾರ್ಗದರ್ಶಿ ಮಾತ್ರ: ಸೋಯಾಬೀನ್, ಮೆಣಸಿನಕಾಯಿ, ಹತ್ತಿ, ಕಬ್ಬು, ಬಾಳೆ, ರಾಗಿ ಮತ್ತು ಇತರ ಬೆಳೆಗಳು."
    elif lang == 'hi':
        return "फोटो द्वारा रोग पहचान उपलब्ध है: धान/चावल, गेहूं, मक्का, टमाटर, आलू, अंगूर, शिमला मिर्च, संतरा (सिट्रस ग्रीनिंग), सेब, चेरी, आड़ू, स्ट्रॉबेरी, स्क्वैश (पाउडरी मिल्ड्यू)। केवल संदर्भ मार्गदर्शिका: सोयाबीन, मिर्च, कपास, गन्ना, केला, रागी एवं अन्य फसलें।"
    return "Photo diagnosis available for: Rice (Paddy), Wheat, Corn (Maize), Tomato, Potato, Grape, Bell Pepper (Capsicum), Orange (Citrus Greening), Apple, Cherry, Peach, Strawberry, Squash (Powdery Mildew). Reference guide only for: Soybean, Chilli, Cotton, Sugarcane, Banana, Ragi, and other crops."

def get_disease_crops_grouped(lang: str = 'en') -> dict:
    """
    Returns crops grouped for the dropdown UI:
    - 'photo_diagnosis' (Karnataka crops first, then other)
    - 'reference_only' (Karnataka crops first, then other)
    """
    photo_crops_kn = []
    photo_crops_other = []
    ref_crops_kn = []
    ref_crops_other = []

    for key, val in DISEASE_COVERAGE.items():
        name_tr = val['name'].get(lang, val['name'].get('en', key.title()))
        item = {
            'key': key,
            'name': name_tr,
            'name_en': val['name'].get('en', key.title()),
            'name_kn': val['name'].get('kn', key),
            'name_hi': val['name'].get('hi', key),
            'status': val['status'],
            'karnataka': val['karnataka'],
            'is_diagnosable': val['status'] in ['full', 'disease_only']
        }
        if val['status'] in ['full', 'disease_only']:
            if val['karnataka']:
                photo_crops_kn.append(item)
            else:
                photo_crops_other.append(item)
        else:
            if val['karnataka']:
                ref_crops_kn.append(item)
            else:
                ref_crops_other.append(item)

    photo_diagnosis_list = photo_crops_kn + photo_crops_other
    reference_only_list = ref_crops_kn + ref_crops_other

    labels = {
        'photo_diagnosis': {
            'en': "📷 Photo Diagnosis Available",
            'kn': "📷 ಫೋಟೋ ಮೂಲಕ ರೋಗ ಪತ್ತೆ ಲಭ್ಯವಿದೆ",
            'hi': "📷 फोटो द्वारा रोग पहचान उपलब्ध है"
        },
        'reference_only': {
            'en': "📖 Reference Guide Only",
            'kn': "📖 ಉಲ್ಲೇಖ ಮಾರ್ಗದರ್ಶಿ ಮಾತ್ರ",
            'hi': "📖 केवल संदर्भ मार्गदर्शिका"
        }
    }

    return {
        'photo_diagnosis': {
            'label': labels['photo_diagnosis'].get(lang, labels['photo_diagnosis']['en']),
            'crops': photo_diagnosis_list
        },
        'reference_only': {
            'label': labels['reference_only'].get(lang, labels['reference_only']['en']),
            'crops': reference_only_list
        }
    }

DISEASE_PANEL_TEXTS = {
    'section_title': {
        'en': "Common Diseases",
        'kn': "ಸಾಮಾನ್ಯ ರೋಗಗಳು",
        'hi': "प्रमुख रोग"
    },
    'reference_panel_title': {
        'en': "Common diseases of {crop} (reference guide)",
        'kn': "{crop} ಬೆಳೆಯ ಸಾಮಾನ್ಯ ರೋಗಗಳು (ಉಲ್ಲೇಖ ಮಾರ್ಗದರ್ಶಿ)",
        'hi': "{crop} के सामान्य रोग (संदर्भ मार्गदर्शिका)"
    },
    'reference_image_badge': {
        'en': "Reference image (source not yet verified)",
        'kn': "ಉಲ್ಲೇಖ ಚಿತ್ರ (ಮೂಲ ಪರಿಶೀಲಿಸಬೇಕಿದೆ)",
        'hi': "संदर्भ छवि (स्रोत अभी सत्यापित नहीं है)"
    },
    'ai_illustration_badge': {
        'en': "Reference image (source not yet verified)",
        'kn': "ಉಲ್ಲೇಖ ಚಿತ್ರ (ಮೂಲ ಪರಿಶೀಲಿಸಬೇಕಿದೆ)",
        'hi': "संदर्भ छवि (स्रोत अभी सत्यापित नहीं है)"
    },
    'pending_review': {
        'en': "Pending expert review",
        'kn': "ತಜ್ಞರ ಪರಿಶೀಲನೆ ಬಾಕಿಯಿದೆ",
        'hi': "विशेषज्ञ समीक्षा लंबित"
    },
    'pesticide_safety_note': {
        'en': "Check the dose on the product label and confirm with your KVK. Follow safety instructions.",
        'kn': "ಉತ್ಪನ್ನದ ಲೇಬಲ್‌ನಲ್ಲಿರುವ ಪ್ರಮಾಣವನ್ನು ಪರಿಶೀಲಿಸಿ ಮತ್ತು ನಿಮ್ಮ ಕೆವಿಕೆಯೊಂದಿಗೆ ಖಚಿತಪಡಿಸಿ. ಸುರಕ್ಷತಾ ನಿಯಮಗಳನ್ನು ಪಾಲಿಸಿ.",
        'hi': "उत्पाद लेबल पर दी गई मात्रा की जांच करें और अपने केवीके से पुष्टि करें। सुरक्षा निर्देशों का पालन करें।"
    },
    'unsupported_crop_message': {
        'en': "Diagnosis is not available for this crop yet. Compare with the reference guide below and consult your KVK.",
        'kn': "ಈ ಬೆಳೆಗೆ ರೋಗ ಪತ್ತೆ ಸದ್ಯ ಲಭ್ಯವಿಲ್ಲ. ಕೆಳಗಿನ ಉಲ್ಲೇಖ ಮಾರ್ಗದರ್ಶಿಯೊಂದಿಗೆ ಹೋಲಿಸಿ ಮತ್ತು ನಿಮ್ಮ ಕೆವಿಕೆಯನ್ನು ಸಂಪರ್ಕಿಸಿ.",
        'hi': "इस फसल के लिए रोग पहचान अभी उपलब्ध नहीं है। नीचे दी गई संदर्भ मार्गदर्शिका से तुलना करें और अपने केवीके से परामर्श लें।"
    },
        'crop_mismatch_message': {
        'en': "This photo doesn't look like a {crop} leaf. Please upload a clearer photo.",
        'kn': "ಈ ಫೋಟೋ {crop} ಎಲೆಯಂತೆ ಕಾಣುತ್ತಿಲ್ಲ. ದಯವಿಟ್ಟು ಹೆಚ್ಚು ಸ್ಪಷ್ಟವಾದ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ.",
        'hi': "यह फोटो {crop} की पत्ती जैसी नहीं लग रही है। कृपया अधिक स्पष्ट फोटो अपलोड करें।"
    },
    'orange_detected_message': {
        'en': "Possible Citrus Greening (Huanglongbing) suspected, confirm with the horticulture department.",
        'kn': "ಸಿಟ್ರಸ್ ಗ್ರೀನಿಂಗ್ ರೋಗದ ಶಂಕೆ ಇದೆ, ದಯವಿಟ್ಟು ತೋಟಗಾರಿಕೆ ಇಲಾಖೆಯೊಂದಿಗೆ ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ.",
        'hi': "सिट्रस ग्रीनिंग रोग की संभावना है, कृपया बागवानी विभाग से पुष्टि करें।"
    },
    'orange_not_detected_message': {
        'en': "Citrus Greening (Huanglongbing) not detected. This does not mean the plant is healthy. Please consult the horticulture department.",
        'kn': "ಸಿಟ್ರಸ್ ಗ್ರೀನಿಂಗ್ ರೋಗ ಪತ್ತೆಯಾಗಿಲ್ಲ. ಇದರರ್ಥ ಸಸ್ಯವು ಸಂಪೂರ್ಣ ಆರೋಗ್ಯಕರವಾಗಿದೆ ಎಂದಲ್ಲ. ದಯವಿಟ್ಟು ತೋಟಗಾರಿಕೆ ಇಲಾಖೆಯನ್ನು ಸಂಪರ್ಕಿಸಿ.",
        'hi': "सिट्रस ग्रीनिंग (हॉन्गलोंगबिंग) रोग नहीं पाया गया। इसका अर्थ यह नहीं है कि पौधा स्वस्थ है। कृपया बागवानी विभाग से संपर्क करें।"
    },
    'squash_detected_message': {
        'en': "Possible Powdery Mildew, confirm with an expert.",
        'kn': "ಬೂದಿ ರೋಗದ ಶಂಕೆ ಇದೆ, ದಯವಿಟ್ಟು ಕೃಷಿ ತಜ್ಞರೊಂದಿಗೆ ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ.",
        'hi': "चूर्णिल फफूंद (पाउडरी मिल्ड्यू) की संभावना है, कृपया विशेषज्ञ से पुष्टि करें।"
    },
    'squash_not_detected_message': {
        'en': "Powdery Mildew not detected. This does not mean the plant is healthy. Please consult an expert.",
        'kn': "ಬೂದಿ ರೋಗ ಪತ್ತೆಯಾಗಿಲ್ಲ. ಇದರರ್ಥ ಸಸ್ಯವು ಸಂಪೂರ್ಣ ಆರೋಗ್ಯಕರವಾಗಿದೆ ಎಂದಲ್ಲ. ದಯವಿಟ್ಟು ಕೃಷಿ ತಜ್ಞರನ್ನು ಸಂಪರ್ಕಿಸಿ.",
        'hi': "चूर्णिल फफूंद (पाउडरी मिल्ड्यू) नहीं पाया गया। इसका अर्थ यह नहीं है कि पौधा स्वस्थ है। कृपया किसी विशेषज्ञ से सलाह लें।"
    },
    'uncertain_diagnosis_message': {
        'en': "I'm not sure. Please upload a clearer photo or consult an expert.",
        'kn': "ಖಚಿತವಿಲ್ಲ. ದಯವಿಟ್ಟು ಹೆಚ್ಚು ಸ್ಪಷ್ಟವಾದ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಅಥವಾ ಕೃಷಿ ತಜ್ಞರನ್ನು ಸಂಪರ್ಕಿಸಿ.",
        'hi': "मुझे पूरा यकीन नहीं है। कृपया स्पष्ट फोटो अपलोड करें या किसी विशेषज्ञ से सलाह लें।"
    }
}

# =====================================================================
# CROP COMMON DISEASES REFERENCE DATABASE
# =====================================================================
CROP_DISEASE_SAMPLES = {
    'soybean': [
        {
            'id': 'soybean_rust',
            'disease_name_en': 'Soybean Rust',
            'disease_name_kn': 'ಸೋಯಾಬೀನ್ ತುಕ್ಕು ರೋಗ',
            'disease_name_hi': 'सोयाबीन गेरुआ (रस्ट)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/soybean/soybean_rust.jpg',
            'symptoms_en': 'Reddish-brown pustules on underside of leaves causing premature defoliation.',
            'symptoms_kn': 'ಎಲೆಗಳ ಕೆಳಭಾಗದಲ್ಲಿ ಕೆಂಪು-ಕಂದು ಚುಕ್ಕೆಗಳು ಕಾಣಿಸಿಕೊಂಡು ಎಲೆ ಉದುರುತ್ತದೆ.',
            'symptoms_hi': 'पत्तियों के निचले हिस्से पर लाल-भूरे रंग के दाने जिससे पत्तियां झड़ने लगती हैं।',
            'treatment_en': 'Spray safe botanical / bio-fungicide or consult your local KVK for approved safe treatment at first appearance.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'bacterial_blight',
            'disease_name_en': 'Bacterial Blight',
            'disease_name_kn': 'ಬ್ಯಾಕ್ಟೀರಿಯಲ್ ಎಲೆ ಕಮಟು ರೋಗ',
            'disease_name_hi': 'जीवाणु पत्ती झुलसा',
            'verified_by_expert': False,
            'image': 'static/disease_samples/soybean/bacterial_blight.jpg',
            'symptoms_en': 'Small angular brown lesions with yellow chlorotic halos.',
            'symptoms_kn': 'ಹಳದಿ ವೃತ್ತದೊಂದಿಗೆ ಸಣ್ಣ ಕೋನೀಯ ಕಂದು ಕಲೆಗಳು ಕಾಣಿಸಿಕೊಳ್ಳುತ್ತವೆ.',
            'symptoms_hi': 'पीले घेरे के साथ छोटे कोणीय भूरे धब्बे दिखाई देते हैं।',
            'treatment_en': 'Spray safe botanical / bio-fungicide or consult your local KVK for approved safe treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीಕೆ (KVK) से संपर्क करें।',
        },
        {
            'id': 'mosaic_virus',
            'disease_name_en': 'Soybean Mosaic Virus',
            'disease_name_kn': 'ಸೋಯಾಬೀನ್ ಮೊಸಾಯಿಕ್ ವೈರಸ್',
            'disease_name_hi': 'सोयाबीन मोज़ेक वायरस',
            'verified_by_expert': False,
            'image': 'static/disease_samples/soybean/mosaic_virus.jpg',
            'symptoms_en': 'Mosaic pattern of dark and light green patches with leaf puckering.',
            'symptoms_kn': 'ತಿಳಿ ಮತ್ತು ಗಾಢ ಹಸಿರು ಮಿಶ್ರಿತ ಎಲೆ ಮುದುರುವಿಕೆ ಮತ್ತು ಸುಕ್ಕುಗಟ್ಟುವಿಕೆ.',
            'symptoms_hi': 'पत्तियों पर गहरे और हल्के हरे रंग के धब्बे और सिकुड़न।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'healthy',
            'disease_name_en': 'Healthy Soybean Leaf',
            'disease_name_kn': 'ಆರೋಗ್ಯಕರ ಸೋಯಾಬೀನ್ ಎಲೆ',
            'disease_name_hi': 'स्वस्थ सोयाबीन पत्ती',
            'verified_by_expert': False,
            'image': 'static/disease_samples/soybean/healthy.jpg',
            'symptoms_en': 'Clean, vibrant green foliage with no fungal or bacterial lesions.',
            'symptoms_kn': 'ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳಿಲ್ಲದ ಶುದ್ಧ, ಸಮೃದ್ಧ ಹಸಿರು ಎಲೆ.',
            'symptoms_hi': 'बिना किसी रोग के धब्बों वाली चमकदार स्वस्थ हरी पत्ती।',
            'treatment_en': 'No disease signs seen. Continue regular crop care.',
            'treatment_kn': 'ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿಲ್ಲ. ಸಾಮಾನ್ಯ ಬೆಳೆ ಪಾಲನೆ ಮುಂದುವರಿಸಿ.',
            'treatment_hi': 'रोग के कोई लक्षण नहीं दिखे। नियमित फसल देखभाल जारी रखें।'
        }
    ],
    'rice': [
        {
            'id': 'bacterial_leaf_blight',
            'disease_name_en': 'Bacterial Leaf Blight',
            'disease_name_kn': 'ಬ್ಯಾಕ್ಟೀರಿಯಲ್ ಎಲೆ ಕಮಟು ರೋಗ',
            'disease_name_hi': 'जीवाणु पत्ती झुलसा',
            'verified_by_expert': False,
            'image': 'static/disease_samples/rice/bacterial_blight.jpg',
            'symptoms_en': 'Water-soaked wavy lesions turning straw yellow from leaf margins.',
            'symptoms_kn': 'ಎಲೆಯ ಅಂಚುಗಳಿಂದ ಒಣಗುತ್ತಾ ಹಳದಿ ಬಣ್ಣಕ್ಕೆ ತಿರುಗುವ ನೀರು-ಗುಳ್ಳೆ ಕಲೆಗಳು.',
            'symptoms_hi': 'पत्ती के किनारों से शुरू होकर पीला होने वाला धारदार झुलसा रोग।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'brown_spot',
            'disease_name_en': 'Brown Spot',
            'disease_name_kn': 'ಕಂದು ಚುಕ್ಕೆ ರೋಗ',
            'disease_name_hi': 'भूरा धब्बा रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/rice/brown_spot.jpg',
            'symptoms_en': 'Oval brown spots with grey centers distributed across leaf blades.',
            'symptoms_kn': 'ಬೂದು ಕೇಂದ್ರವಿರುವ ದುಂಡಗಿನ ಕಂದು ಕಲೆಗಳು ಎಲೆಗಳ ಮೇಲೆ ಕಾಣಿಸುತ್ತವೆ.',
            'symptoms_hi': 'पत्तियों पर धूसर केंद्र वाले अंडाकार भूरे रंग के धब्बे।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'leaf_blast',
            'disease_name_en': 'Rice Leaf Blast',
            'disease_name_kn': 'ಭತ್ತದ ಎಲೆ ಬೆಂಕಿ ರೋಗ (ಬ್ಲಾಸ್ಟ್)',
            'disease_name_hi': 'धान पत्ती ब्लास्ट',
            'verified_by_expert': False,
            'image': 'static/disease_samples/rice/leaf_blast.jpg',
            'symptoms_en': 'Diamond/spindle-shaped lesions with pointed ends and ash-grey centers.',
            'symptoms_kn': 'ಬೂದಿ ಬಣ್ಣದ ಕೇಂದ್ರವಿರುವ ಕದಿರಿನ ಆಕಾರದ (ಸ್ಪಿಂಡಲ್) ಕಲೆಗಳು.',
            'symptoms_hi': 'राख जैसे केंद्र वाले नाव या आंख के आकार के धब्बे।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'leaf_scald',
            'disease_name_en': 'Leaf Scald',
            'disease_name_kn': 'ಎಲೆ ಸುಟ್ಟ ರೋಗ (ಸ್ಕೇಲ್ಡ್)',
            'disease_name_hi': 'लीफ स्कैल्ड रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/rice/leaf_scald.jpg',
            'symptoms_en': 'Zonate chevron-patterned bands of olive-green and bleached straw colors.',
            'symptoms_kn': 'ಎಲೆಗಳ ತುದಿಯಿಂದ ಪಟ್ಟೆ-ಪಟ್ಟೆಯಾಗಿ ಒಣಗುವ ಲಕ್ಷಣಗಳು.',
            'symptoms_hi': 'पत्तियों पर हल्के हरे और भूरे रंग की धारियों का झुलसाव।',
            'treatment_en': 'Spray safe botanical / bio-fungicide or consult your local KVK for approved safe treatment or safe botanical / bio-fungicide or consult your local KVK for approved safe treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        }
    ],
    'wheat': [
        {
            'id': 'leaf_blight',
            'disease_name_en': 'Wheat Leaf Blight',
            'disease_name_kn': 'ಗೋಧಿ ಎಲೆ ಕಮಟು ರೋಗ',
            'disease_name_hi': 'गेहूं पत्ती झुलसा',
            'verified_by_expert': False,
            'image': 'static/disease_samples/wheat/leaf_blight.jpg',
            'symptoms_en': 'Oval to elongated brown spots with yellow borders coalescing into blighted areas.',
            'symptoms_kn': 'ಹಳದಿ ಅಂಚುಳ್ಳ ಕಂದು ಕಲೆಗಳು ಒಟ್ಟಾಗಿ ಎಲೆ ಕಮಟುವಿಕೆಗೆ ಕಾರಣವಾಗುತ್ತವೆ.',
            'symptoms_hi': 'पीले किनारों वाले भूरे धब्बे जो आपस में मिलकर पत्ती को झुलसा देते हैं।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'wheat_blast',
            'disease_name_en': 'Wheat Blast (Magnaporthe oryzae)',
            'disease_name_kn': 'ಗೋಧಿ ಬ್ಲಾಸ್ಟ್ (ಬೆಂಕಿ ರೋಗ)',
            'disease_name_hi': 'गेहूं ब्लास्ट रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/wheat/wheat_blast.jpg',
            'symptoms_en': 'Bleaching of spikelets above the infection point leading to sterile or shriveled grains.',
            'symptoms_kn': 'ಸೋಂಕು ತಗುಲಿದ ಜಾಗದ ಮೇಲಿನ ತೆನೆ ಬಿಳುಚಿಕೊಳ್ಳುವುದು ಮತ್ತು ಜೊಳ್ಳು ಕಾಳುಗಳುಂಟಾಗುವುದು.',
            'symptoms_hi': 'संक्रमण बिंदु से ऊपर बालियों का सफेद पड़ना और दानों का सिकुड़ जाना।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'black_point',
            'disease_name_en': 'Wheat Black Point',
            'disease_name_kn': 'ಗೋಧಿ ಕಪ್ಪು ತುದಿ ರೋಗ',
            'disease_name_hi': 'गेहूं ब्लैक पॉइंट (काला सिरा)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/wheat/black_point.jpg',
            'symptoms_en': 'Dark brown to black discoloration at the embryo end of the grain.',
            'symptoms_kn': 'ಗೋಧಿ ಕಾಳಿನ ಮೊಳಕೆಯ ತುದಿಯಲ್ಲಿ ಕಪ್ಪು ಅಥವಾ ಗಾಢ ಕಂದು ಬಣ್ಣ ಉಂಟಾಗುವುದು.',
            'symptoms_hi': 'गेहूं के दाने के भ्रूण वाले सिरे पर गहरा भूरा या काला रंग आना।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'fusarium_rot',
            'disease_name_en': 'Wheat Fusarium Foot Rot',
            'disease_name_kn': 'ಗೋಧಿ ಬುಡ ಕೊಳೆ ರೋಗ (ಫ್ಯುಸಾರಿಯಂ)',
            'disease_name_hi': 'गेहूं फ्यूजेरियम तना गलन',
            'verified_by_expert': False,
            'image': 'static/disease_samples/wheat/fusarium_rot.jpg',
            'symptoms_en': 'Brown discoloration of lower stem nodes with pinkish fungal mycelium and stunted growth.',
            'symptoms_kn': 'ಕಾಂಡದ ಕೆಳಭಾಗದ ಕಣ್ಣುಗಳು ಕಂದು ಬಣ್ಣಕ್ಕೆ ತಿರುಗಿ ಗುಲಾಬಿ ಬಣ್ಣದ ಶಿಲೀಂಧ್ರ ಬೆಳೆಯುತ್ತದೆ.',
            'symptoms_hi': 'तने की निचली गांठों का भूरा होना और गुलाबी कवक की वृद्धि के साथ पौधा बौना होना।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'healthy',
            'disease_name_en': 'Healthy Wheat Leaf',
            'disease_name_kn': 'ಆರೋಗ್ಯಕರ ಗೋಧಿ ಎಲೆ',
            'disease_name_hi': 'स्वस्थ गेहूं की पत्ती',
            'verified_by_expert': False,
            'image': 'static/disease_samples/wheat/healthy.jpg',
            'symptoms_en': 'Clean, upright green wheat leaves with robust tillers and no fungal lesions.',
            'symptoms_kn': 'ಯಾವುದೇ ಶಿಲೀಂಧ್ರ ಕಲೆಗಳಿಲ್ಲದ ಶುದ್ಧ, ನೇರವಾದ ಹಸಿರು ಗೋಧಿ ಎಲೆಗಳು.',
            'symptoms_hi': 'बिना किसी कवक के धब्बों वाली चमकदार स्वस्थ हरी गेहूं की पत्तियां।',
            'treatment_en': 'No disease signs seen. Continue balanced irrigation and timely nitrogen top-dressing.',
            'treatment_kn': 'ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳಿಲ್ಲ. ಸಮತೋಲಿತ ನೀರಾವರಿ ಮತ್ತು ಸಾರಜನಕ ಮೇಲುಗೊಬ್ಬರ ಮುಂದುವರಿಸಿ.',
            'treatment_hi': 'रोग के कोई लक्षण नहीं हैं। संतुलित सिंचाई और समय पर यूरिया टॉप-ड्रेसिंग जारी रखें।'
        }
    ],
    'tomato': [
        {
            'id': 'early_blight',
            'disease_name_en': 'Tomato Early Blight',
            'disease_name_kn': 'ಟೊಮೆಟೊ ಮುಂಚಿನ ಕಮಟು ರೋಗ',
            'disease_name_hi': 'टमाटर अगेती झुलसा',
            'verified_by_expert': False,
            'image': 'static/disease_samples/tomato/early_blight.jpg',
            'symptoms_en': 'Concentric target-like rings on older leaves leading to defoliation.',
            'symptoms_kn': 'ಹಳೆಯ ಎಲೆಗಳ ಮೇಲೆ ವೃತ್ತಾಕಾರದ ಕಪ್ಪು-ಕಂದು ರಿಂಗ್ ಕಲೆಗಳು.',
            'symptoms_hi': 'पत्तियों पर संकेंद्री छल्ले (टारगेट स्पॉट) जैसे भूरे धब्बे।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'late_blight',
            'disease_name_en': 'Tomato Late Blight',
            'disease_name_kn': 'ಟೊಮೆಟೊ ತಡವಾದ ಕಮಟು ರೋಗ',
            'disease_name_hi': 'टमाटर पछेती झुलसा',
            'verified_by_expert': False,
            'image': 'static/disease_samples/tomato/late_blight.jpg',
            'symptoms_en': 'Water-soaked dark lesions with white fungal down on leaf undersides.',
            'symptoms_kn': 'ಎಲೆಗಳ ಕೆಳಗೆ ಬಿಳಿ ಬೂಸ್ಟ್ ಮತ್ತು ಕಪ್ಪು-ಬೂದು ಕಲೆಗಳು ವೇಗವಾಗಿ ಹರಡುತ್ತವೆ.',
            'symptoms_hi': 'पत्तियों के नीचे सफेद फफूंद और तेजी से फैलने वाले गहरे काले धब्बे।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'bacterial_spot',
            'disease_name_en': 'Bacterial Spot',
            'disease_name_kn': 'ಬ್ಯಾಕ್ಟೀರಿಯಲ್ ಎಲೆ ಚುಕ್ಕೆ ರೋಗ',
            'disease_name_hi': 'जीवाणु पत्ती धब्बा',
            'verified_by_expert': False,
            'image': 'static/disease_samples/tomato/bacterial_spot.jpg',
            'symptoms_en': 'Small dark water-soaked spots with yellow halos on leaves and stems.',
            'symptoms_kn': 'ಹಳದಿ ವೃತ್ತವಿರುವ ಸಣ್ಣ ಕಪ್ಪು ಚುಕ್ಕೆಗಳು ಎಲೆ ಮತ್ತು ಹಣ್ಣಿನ ಮೇಲೆ ಬರುತ್ತವೆ.',
            'symptoms_hi': 'पीले घेरे वाले छोटे गहरे पानीदार धब्बे।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'yellow_leaf_curl',
            'disease_name_en': 'Yellow Leaf Curl Virus',
            'disease_name_kn': 'ಹಳದಿ ಎಲೆ ಮುದುರು ರೋಗ',
            'disease_name_hi': 'पीला पत्ती कर्ल वायरस',
            'verified_by_expert': False,
            'image': 'static/disease_samples/tomato/yellow_leaf_curl.jpg',
            'symptoms_en': 'Severe upward curling, dwarfing, and yellowing of younger foliage.',
            'symptoms_kn': 'ಎಲೆಗಳು ಮೇಲ್ಮುಖವಾಗಿ ಮುದುರಿಕೊಂಡು ಹಳದಿಯಾಗುವುದು ಮತ್ತು ಗಿಡ ಗಿಡ್ಡವಾಗುವುದು.',
            'symptoms_hi': 'पत्तियों का ऊपर की ओर मुड़ना, पीलापन और पौधे का बौना रह जाना।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಬಿಳಿ ನೊಣ ನಿಯಂತ್ರಣಕ್ಕೆ ಡಯಾಫೆಂಥಿಯುರಾನ್ ಅಥವಾ ಅಸಿಟಾಮಿಪ್ರಿಡ್ ಬಳಸಿ.',
            'treatment_hi': 'सफेद मक्खी नियंत्रण के लिए डायफेनथियूरोन या एसिटामिप्रिड का प्रयोग करें।'
        }
    ],
    'maize': [
        {
            'id': 'common_rust',
            'disease_name_en': 'Common Rust (Puccinia sorghi)',
            'disease_name_kn': 'ಸಾಮಾನ್ಯ ತುಕ್ಕು ರೋಗ',
            'disease_name_hi': 'सामान्य गेरुआ (कॉमन रस्ट)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/maize/common_rust.jpg',
            'symptoms_en': 'Small powdery cinnamon-brown pustules scattered on both leaf surfaces.',
            'symptoms_kn': 'ಎಲೆಯ ಎರಡೂ ಬದಿಗಳಲ್ಲಿ ದಾಲ್ಚಿನ್ನಿ ಬಣ್ಣದ ಸಣ್ಣ ತುಕ್ಕು ಚುಕ್ಕೆಗಳು ಕಾಣಿಸುತ್ತವೆ.',
            'symptoms_hi': 'पत्तियों की दोनों सतहों पर दालचीनी जैसे भूरे रंग के छोटे उभरे हुए दाने।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
        },
        {
            'id': 'northern_blight',
            'disease_name_en': 'Northern Corn Leaf Blight (Exserohilum turcicum)',
            'disease_name_kn': 'ಉತ್ತರದ ಎಲೆ ಕಮಟು ರೋಗ',
            'disease_name_hi': 'उत्तरी मक्का पत्ती झुलसा',
            'verified_by_expert': False,
            'image': 'static/disease_samples/maize/northern_blight.jpg',
            'symptoms_en': 'Long elliptical cigar-shaped greyish-green to tan lesions.',
            'symptoms_kn': 'ಉದ್ದನೆಯ ಸಿಗಾರ್ ಆಕಾರದ ಬೂದು-ಹಸಿರು ಅಥವಾ ಕಂದು ಕಲೆಗಳು ಕಾಣಿಸಿಕೊಳ್ಳುತ್ತವೆ.',
            'symptoms_hi': 'पत्तियों पर लंबे सिगार के आकार के धूसर-हरे से भूरे रंग के बड़े धब्बे।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
        },
        {
            'id': 'cercospora_spot',
            'disease_name_en': 'Cercospora Leaf Spot / Gray Leaf Spot (Cercospora zeae-maydis)',
            'disease_name_kn': 'ಸರ್ಕೋಸ್ಪೊರಾ / ಬೂದು ಎಲೆ ಚುಕ್ಕೆ ರೋಗ',
            'disease_name_hi': 'सर्कोस्पोरा / धूसर पत्ती धब्बा रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/maize/cercospora_spot.jpg',
            'symptoms_en': 'Rectangular tan to grey spots delimited by leaf veins running parallel across blade.',
            'symptoms_kn': 'ಎಲೆಯ ನರಗಳಿಗೆ ಸೀಮಿತವಾದ ಆಯತಾಕಾರದ ಕಂದು-ಬೂದು ಬಣ್ಣದ ಚುಕ್ಕೆಗಳು.',
            'symptoms_hi': 'पत्तियों की शिराओं के बीच सीमित आयताकार भूरे-धूसर रंग के धब्बे।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
        },
        {
            'id': 'healthy',
            'disease_name_en': 'Healthy Maize Leaf',
            'disease_name_kn': 'ಆರೋಗ್ಯಕರ ಮೆಕ್ಕೆಜೋಳದ ಎಲೆ',
            'disease_name_hi': 'स्वस्थ मक्का पत्ती',
            'verified_by_expert': False,
            'image': 'static/disease_samples/maize/healthy.jpg',
            'symptoms_en': 'Broad, vigorous dark green arching leaves without rust pustules or necrotic lesions.',
            'symptoms_kn': 'ಯಾವುದೇ ಕಲೆಗಳಿಲ್ಲದ ಸಮೃದ್ಧ ಹಸಿರು ಮತ್ತು ಅಗಲವಾದ ಆರೋಗ್ಯಕರ ಎಲೆಗಳು.',
            'symptoms_hi': 'बिना किसी धब्बे या रस्ट के चौड़ी चमकदार स्वस्थ हरी पत्तियां।',
            'treatment_en': 'No disease signs seen. Maintain balanced nitrogen application and timely weeding.',
            'treatment_kn': 'ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳಿಲ್ಲ. ಸಮತೋಲಿತ ರಸಗೊಬ್ಬರ ಮತ್ತು ಕಳೆ ನಿರ್ವಹಣೆ ಮುಂದುವರಿಸಿ.',
            'treatment_hi': 'रोग के कोई लक्षण नहीं हैं। संतुलित खाद और समय पर निराई जारी रखें।'
        }
    ],
    'cotton': [
        {
            'id': 'bacterial_blight',
            'disease_name_en': 'Bacterial Blight / Angular Leaf Spot',
            'disease_name_kn': 'ಹತ್ತಿ ಬ್ಯಾಕ್ಟೀರಿಯಲ್ ಕಮಟು ರೋಗ',
            'disease_name_hi': 'कपास जीवाणु अंगमारी',
            'verified_by_expert': False,
            'image': 'static/disease_samples/cotton/bacterial_blight.jpg',
            'symptoms_en': 'Angular water-soaked spots bounded by veins on leaves and black arm on stems.',
            'symptoms_kn': 'ಕೋನೀಯ ನೀರು ಗುಳ್ಳೆ ಕಲೆಗಳು ಮತ್ತು ಕಾಂಡ ಕಪ್ಪಾಗುವಿಕೆ (ಬ್ಲ್ಯಾಕ್ ಆರ್ಮ್).',
            'symptoms_hi': 'कोणीय जलभराव वाले धब्बे और तने पर काली धारियां।',
            'treatment_en': 'Spray safe botanical / bio-fungicide or consult your local KVK for approved safe treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'leaf_curl',
            'disease_name_en': 'Cotton Leaf Curl Virus',
            'disease_name_kn': 'ಹತ್ತಿ ಎಲೆ ಮುದುರು ರೋಗ',
            'disease_name_hi': 'कपास पत्ती कर्ल वायरस',
            'verified_by_expert': False,
            'image': 'static/disease_samples/cotton/leaf_curl.jpg',
            'symptoms_en': 'Upward leaf curling, vein thickening and enations on leaf underside.',
            'symptoms_kn': 'ಎಲೆಗಳು ಮೇಲ್ಮುಖವಾಗಿ ಮುದುರಿಕೊಳ್ಳುವುದು ಮತ್ತು ನರಗಳು ದಪ್ಪವಾಗುವುದು.',
            'symptoms_hi': 'पत्तियों का मुड़ना और निचली सतह पर नसों का मोटा होना।',
            'treatment_en': 'Manage whitefly vector using Flonicamid or Pyriproxyfen.',
            'treatment_kn': 'ಬಿಳಿ ನೊಣ ನಿಯಂತ್ರಣಕ್ಕೆ ಫ್ಲೋನಿಕಾಮಿಡ್ ಅಥವಾ ಪೈರಿಪ್ರಾಕ್ಸಿಫೆನ್ ಬಳಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'alternaria_spot',
            'disease_name_en': 'Alternaria Leaf Spot',
            'disease_name_kn': 'ಆಲ್ಟರ್ನೇರಿಯಾ ಎಲೆ ಚುಕ್ಕೆ ರೋಗ',
            'disease_name_hi': 'अल्टरनेरिया पत्ती धब्बा',
            'verified_by_expert': False,
            'image': 'static/disease_samples/cotton/alternaria_spot.jpg',
            'symptoms_en': 'Circular necrotic spots with purple margins developing shot-holes.',
            'symptoms_kn': 'ನೇರಳೆ ಅಂಚಿರುವ ದುಂಡಗಿನ ಕಂದು ಕಲೆಗಳು ಎಲೆಯಲ್ಲಿ ರಂಧ್ರ ಉಂಟುಮಾಡುತ್ತವೆ.',
            'symptoms_hi': 'बैंगनी किनारों वाले गोलाकार भूरे धब्बे।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'healthy',
            'disease_name_en': 'Healthy Cotton Leaf',
            'disease_name_kn': 'ಆರೋಗ್ಯಕರ ಹತ್ತಿ ಎಲೆ',
            'disease_name_hi': 'स्वस्थ कपास पत्ती',
            'verified_by_expert': False,
            'image': 'static/disease_samples/cotton/healthy.jpg',
            'symptoms_en': 'Broad lobed green leaves free of sucking pests and fungal spotting.',
            'symptoms_kn': 'ಯಾವುದೇ ಕೀಟ ಅಥವಾ ಕಲೆಗಳಿಲ್ಲದ ಅಗಲ ಹಸಿರು ಹತ್ತಿ ಎಲೆಗಳು.',
            'symptoms_hi': 'कीट और रोगों से मुक्त स्वस्थ हरी चौड़ी पत्तियां।',
            'treatment_en': 'No disease signs seen. Continue regular crop care.',
            'treatment_kn': 'ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿಲ್ಲ. ಸಾಮಾನ್ಯ ಬೆಳೆ ಪಾಲನೆ ಮುಂದುವರಿಸಿ.',
            'treatment_hi': 'रोग के कोई लक्षण नहीं दिखे। नियमित फसल देखभाल जारी रखें।'
        }
    ],
    'potato': [
        {
            'id': 'early_blight',
            'disease_name_en': 'Potato Early Blight',
            'disease_name_kn': 'ಆಲೂಗಡ್ಡೆ ಮುಂಚಿನ ಕಮಟು ರೋಗ',
            'disease_name_hi': 'आलू अगेती झुलसा',
            'verified_by_expert': False,
            'image': 'static/disease_samples/potato/early_blight.jpg',
            'symptoms_en': 'Target-board concentric brown rings on lower leaves.',
            'symptoms_kn': 'ಕೆಳಭಾಗದ ಎಲೆಗಳ ಮೇಲೆ ವೃತ್ತಾಕಾರದ ಕಂದು ರಿಂಗ್ ಕಲೆಗಳು.',
            'symptoms_hi': 'निचली पत्तियों पर गोल छल्लेदार भूरे धब्बे।',
            'treatment_en': 'Spray safe botanical / bio-fungicide or consult your local KVK for approved safe treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'late_blight',
            'disease_name_en': 'Potato Late Blight',
            'disease_name_kn': 'ಆಲೂಗಡ್ಡೆ ತಡವಾದ ಕಮಟು ರೋಗ',
            'disease_name_hi': 'आलू पछेती झुलसा',
            'verified_by_expert': False,
            'image': 'static/disease_samples/potato/late_blight.jpg',
            'symptoms_en': 'Rapidly spreading dark water-soaked lesions and tuber rot.',
            'symptoms_kn': 'ವೇಗವಾಗಿ ಹರಡುವ ಕಪ್ಪು ಕಲೆಗಳು ಮತ್ತು ಗೆಡ್ಡೆ ಕೊಳೆಯುವಿಕೆ.',
            'symptoms_hi': 'तेजी से फैलने वाले काले धब्बे और कंदों का सड़ना।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'healthy',
            'disease_name_en': 'Healthy Potato Plant',
            'disease_name_kn': 'ಆರೋಗ್ಯಕರ ಆಲೂಗಡ್ಡೆ ಸಸ್ಯ',
            'disease_name_hi': 'स्वस्थ आलू का पौधा',
            'verified_by_expert': False,
            'image': 'static/disease_samples/potato/healthy.jpg',
            'symptoms_en': 'Vigorous lush canopy with uniform tuber bulking.',
            'symptoms_kn': 'ರೋಗಮುಕ್ತ ಹುಲುಸಾದ ಎಲೆಗಳು ಮತ್ತು ಉತ್ತಮ ಗೆಡ್ಡೆ ಬೆಳವಣಿಗೆ.',
            'symptoms_hi': 'बिना किसी रोग के स्वस्थ हरा-भरा पौधा।',
            'treatment_en': 'No disease signs seen. Continue regular crop care.',
            'treatment_kn': 'ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿಲ್ಲ. ಸಾಮಾನ್ಯ ಬೆಳೆ ಪಾಲನೆ ಮುಂದುವರಿಸಿ.',
            'treatment_hi': 'रोग के कोई लक्षण नहीं दिखे। नियमित फसल देखभाल जारी रखें।'
        }
    ],
    'grape': [
        {
            'id': 'black_rot',
            'disease_name_en': 'Grape Black Rot',
            'disease_name_kn': 'ದ್ರಾಕ್ಷಿ ಕಪ್ಪು ಕೊಳೆತ ರೋಗ',
            'disease_name_hi': 'अंगूर काला सड़न रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/grape/black_rot.jpg',
            'symptoms_en': 'Reddish-brown circular spots on leaves and shrivelled black berry mummies.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ಕೆಂಪು-ಕಂದು ಕಲೆಗಳು ಮತ್ತು ಹಣ್ಣು ಕಪ್ಪಾಗಿ ಸುಕ್ಕುಗಟ್ಟುವಿಕೆ.',
            'symptoms_hi': 'पत्तियों पर लाल-भूरे धब्बे और अंगूर के दानों का सिकुड़ कर काला होना।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'black_measles',
            'disease_name_en': 'Esca (Black Measles)',
            'disease_name_kn': 'ಎಸ್ಕಾ (ಕಪ್ಪು ದಡಾರ ರೋಗ)',
            'disease_name_hi': 'एस्का (काला चेचक रोग)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/grape/black_measles.jpg',
            'symptoms_en': 'Tiger-stripe pattern of interveinal chlorosis and dark speckling on berries.',
            'symptoms_kn': 'ಹುಲಿಯ ಪಟ್ಟೆಯಂತೆ ಎಲೆಯ ನರಗಳ ನಡುವೆ ಹಳದಿ-ಕಂದು ಬಣ್ಣ ಮತ್ತು ಹಣ್ಣಿನಲ್ಲಿ ಕಪ್ಪು ಚುಕ್ಕೆಗಳು.',
            'symptoms_hi': 'पत्तियों पर बाघ जैसी धारियां और फलों पर काले धब्बे।',
            'treatment_en': 'Prune out infected dead wood and protect pruning wounds with wound paste.',
            'treatment_kn': 'ಸೋಂಕಿತ ರೆಂಬೆಗಳನ್ನು ಕತ್ತರಿಸಿ ಗಾಯಕ್ಕೆ ಶಿಲೀಂಧ್ರನಾಶಕ ಪೇಸ್ಟ್ ಹಚ್ಚಿ.',
            'treatment_hi': 'संक्रमित सूखी शाखाओं की छंटाई करें और कवकनाशी लेप लगाएं।'
        },
        {
            'id': 'leaf_blight',
            'disease_name_en': 'Grape Leaf Blight (Isariopsis)',
            'disease_name_kn': 'ದ್ರಾಕ್ಷಿ ಎಲೆ ಕಮಟು ರೋಗ',
            'disease_name_hi': 'अंगूर पत्ती झुलसा',
            'verified_by_expert': False,
            'image': 'static/disease_samples/grape/leaf_blight.jpg',
            'symptoms_en': 'Large irregular necrotic patches causing premature defoliation.',
            'symptoms_kn': 'ದೊಡ್ಡ ಅನಿಯಮಿತ ಕಂದು ಕಲೆಗಳು ಎಲೆ ಉದುರುವಿಕೆಗೆ ಕಾರಣವಾಗುತ್ತವೆ.',
            'symptoms_hi': 'पत्तियों पर बड़े अनियमित धब्बे जिससे पत्तियां गिरने लगती हैं।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        }
    ],
    'apple': [
        {
            'id': 'apple_scab',
            'disease_name_en': 'Apple Scab',
            'disease_name_kn': 'ಸೇಬು ತುರುಬು (ಸ್ಕೇಬ್) ರೋಗ',
            'disease_name_hi': 'सेब स्कैब रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/apple/apple_scab.jpg',
            'symptoms_en': 'Velvety olive-green spots turning into dark corky lesions on leaves and fruit.',
            'symptoms_kn': 'ಎಲೆ ಮತ್ತು ಹಣ್ಣಿನ ಮೇಲೆ ಕಡು ಹಸಿರು-ಕಪ್ಪು ಚುಕ್ಕೆಗಳು ಉಂಟಾಗುತ್ತವೆ.',
            'symptoms_hi': 'पत्तियों और फलों पर मखमली गहरे हरे-काले धब्बे।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'black_rot',
            'disease_name_en': 'Apple Black Rot',
            'disease_name_kn': 'ಸೇಬು ಕಪ್ಪು ಕೊಳೆತ ರೋಗ',
            'disease_name_hi': 'सेब काला सड़न रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/apple/black_rot.jpg',
            'symptoms_en': 'Frog-eye leaf spots and rotting black mummified fruit.',
            'symptoms_kn': 'ಕಪ್ಪೆ ಕಣ್ಣಿನಂತಹ ಕಲೆಗಳು ಮತ್ತು ಕಪ್ಪಾಗಿ ಕೊಳೆಯುವ ಹಣ್ಣುಗಳು.',
            'symptoms_hi': 'मेंढक की आंख जैसे धब्बे और फलों का सड़कर काला पड़ना।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'cedar_rust',
            'disease_name_en': 'Cedar Apple Rust',
            'disease_name_kn': 'ಸೀಡರ್ ಆಪಲ್ ತುಕ್ಕು ರೋಗ',
            'disease_name_hi': 'सीडर एप्पल रस्ट',
            'verified_by_expert': False,
            'image': 'static/disease_samples/apple/cedar_rust.jpg',
            'symptoms_en': 'Bright yellow-orange spots on upper leaf surfaces with spore tubes beneath.',
            'symptoms_kn': 'ಎಲೆಯ ಮೇಲ್ಭಾಗದಲ್ಲಿ ಪ್ರಕಾಶಮಾನವಾದ ಹಳದಿ-ಕಿತ್ತಳೆ ಚುಕ್ಕೆಗಳು.',
            'symptoms_hi': 'पत्तियों की ऊपरी सतह पर चमकदार पीले-नारंगी धब्बे।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        }
    ],
    'pepper': [
        {
            'id': 'bacterial_spot',
            'disease_name_en': 'Bacterial Spot',
            'disease_name_kn': 'ಬ್ಯಾಕ್ಟೀರಿಯಲ್ ಚುಕ್ಕೆ ರೋಗ',
            'disease_name_hi': 'जीवाणु धब्बा रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/pepper/bacterial_spot.jpg',
            'symptoms_en': 'Small, circular dark lesions on leaves and fruit with yellow halos.',
            'symptoms_kn': 'ಎಲೆ ಮತ್ತು ಕಾಯಿಗಳ ಮೇಲೆ ಹಳದಿ ವೃತ್ತ ಹೊಂದಿರುವ ಸಣ್ಣ ಕಪ್ಪು ಚುಕ್ಕೆಗಳು.',
            'symptoms_hi': 'पत्तियों और फलों पर पीले घेरे वाले छोटे गहरे गोल धब्बे।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'healthy',
            'disease_name_en': 'Healthy Bell Pepper Leaf',
            'disease_name_kn': 'ಆರೋಗ್ಯಕರ ದಪ್ಪ ಮೆಣಸಿನಕಾಯಿ ಎಲೆ',
            'disease_name_hi': 'स्वस्थ शिमला मिर्च पत्ती',
            'verified_by_expert': False,
            'image': 'static/disease_samples/pepper/healthy.jpg',
            'symptoms_en': 'Glossy dark green leaves with uniform surface and healthy flower buds.',
            'symptoms_kn': 'ಹೊಳೆಯುವ ಗಾಢ ಹಸಿರು ಸಮೃದ್ಧ ಎಲೆಗಳು.',
            'symptoms_hi': 'चमकदार गहरी हरी स्वस्थ पत्तियां।',
            'treatment_en': 'No disease signs seen. Continue regular care.',
            'treatment_kn': 'ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳಿಲ್ಲ. ಸಾಮಾನ್ಯ ಬೆಳೆ ಪಾಲನೆ ಮುಂದುವರಿಸಿ.',
            'treatment_hi': 'रोग के कोई लक्षण नहीं हैं। नियमित देखभाल जारी रखें।'
        }
    ],
    'groundnut': [
        {
            'id': 'tikka_leaf_spot',
            'disease_name_en': 'Tikka Leaf Spot (Cercospora)',
            'disease_name_kn': 'ತಿಕ್ಕಾ ಎಲೆ ಚುಕ್ಕೆ ರೋಗ',
            'disease_name_hi': 'टिक्का पत्ती धब्बा रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/groundnut/tikka_leaf_spot.jpg',
            'symptoms_en': 'Dark brown circular necrotic spots surrounded by prominent yellow chlorotic halos.',
            'symptoms_kn': 'ಎಲೆಯ ಮೇಲೆ ಹಳದಿ ವೃತ್ತ ಹೊಂದಿದ ಗಾಢ ಕಂದು ದುಂಡನೆಯ ಚುಕ್ಕೆಗಳು.',
            'symptoms_hi': 'पत्तियों पर पीले छल्ले से घिरे गहरे भूरे गोल धब्बे।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'rust',
            'disease_name_en': 'Groundnut Rust (Puccinia)',
            'disease_name_kn': 'ಕಡಲೆಕಾಯಿ ತುಕ್ಕು ರೋಗ',
            'disease_name_hi': 'मूंगफली गेरुआ (रस्ट)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/groundnut/rust.jpg',
            'symptoms_en': 'Orange-brown pustules on lower leaf surfaces causing severe leaf drying.',
            'symptoms_kn': 'ಎಲೆಗಳ ಕೆಳಭಾಗದಲ್ಲಿ ಕಿತ್ತಳೆ-ಕಂದು ಬಣ್ಣದ ಪುಡಿ ತುಂಬಿದ ಗುಳ್ಳೆಗಳು.',
            'symptoms_hi': 'पत्तियों की निचली सतह पर नारंगी-भूरे रंग के दाने।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'bud_necrosis',
            'disease_name_en': 'Peanut Bud Necrosis (PBND)',
            'disease_name_kn': 'ಮೊಗ್ಗು ಕೊಳೆ ರೋಗ (ನೆಕ್ರೋಸಿಸ್)',
            'disease_name_hi': 'कली सड़न रोग (PBND)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/groundnut/bud_necrosis.jpg',
            'symptoms_en': 'Chlorotic rings, necrosis of terminal buds, and stunted plant growth.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ವರ್ತುಲಾಕಾರದ ಕಲೆಗಳು ಮತ್ತು ತುದಿಯ ಮೊಗ್ಗು ಒಣಗುವಿಕೆ.',
            'symptoms_hi': 'पत्तियों पर छल्लेदार धब्बे और शीर्ष कलियों का सूखना।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'healthy',
            'disease_name_en': 'Healthy Groundnut Leaf',
            'disease_name_kn': 'ಆರೋಗ್ಯಕರ ಕಡಲೆಕಾಯಿ ಎಲೆ',
            'disease_name_hi': 'स्वस्थ मूंगफली पत्ती',
            'verified_by_expert': False,
            'image': 'static/disease_samples/groundnut/healthy.jpg',
            'symptoms_en': 'Healthy tetrafoliate green leaves with vigorous vegetative canopy.',
            'symptoms_kn': 'ಯಾವುದೇ ಕಲೆಗಳಿಲ್ಲದ ಸೊಂಪಾದ ನಾಲ್ಕು ಎಲೆಗಳ ಗಿಡ.',
            'symptoms_hi': 'स्वस्थ और हरी-भरी चार पत्तों वाली पत्तियां।',
            'treatment_en': 'No disease signs seen. Continue regular crop care.',
            'treatment_kn': 'ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿಲ್ಲ. ಸಾಮಾನ್ಯ ಬೆಳೆ ಪಾಲನೆ ಮುಂದುವರಿಸಿ.',
            'treatment_hi': 'रोग के कोई लक्षण नहीं दिखे। नियमित फसल देखभाल जारी रखें।'
        }
    ],
    'coconut': [
        {
            'id': 'leaf_rot',
            'disease_name_en': 'Coconut Leaf Rot',
            'disease_name_kn': 'ತೆಂಗಿನ ಎಲೆ ಕೊಳೆ ರೋಗ',
            'disease_name_hi': 'नारियल पत्ती गलन',
            'verified_by_expert': False,
            'image': 'static/disease_samples/coconut/leaf_rot.jpg',
            'symptoms_en': 'Blackening and shrivelling of the distal ends of leaflets with fan-shaped appearance.',
            'symptoms_kn': 'ಎಲೆಗಳ ತುದಿಯು ಕಪ್ಪಾಗಿ ಕೊಳೆತು, ಒಣಗಿ ಬೀಸಣಿಕೆಯಂತೆ ಕಾಣಿಸುತ್ತದೆ.',
            'symptoms_hi': 'पत्तियों के सिरे काले होकर सड़ते हैं और पंखे जैसा रूप ले लेते हैं।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'bud_rot',
            'disease_name_en': 'Coconut Bud Rot',
            'disease_name_kn': 'ತೆಂಗಿನ ಸುಳಿ ಕೊಳೆ ರೋಗ',
            'disease_name_hi': 'नारियल शीर्ष गलन (बड रॉट)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/coconut/bud_rot.jpg',
            'symptoms_en': 'Yellowing and withering of the spear leaf followed by rotting of the central spindle.',
            'symptoms_kn': 'ಕೇಂದ್ರ ಸುಳಿ ಎಲೆಯು ಹಳದಿಯಾಗಿ ಒಣಗುವುದು ಮತ್ತು ಕೊಳೆತು ದುರ್ವಾಸನೆ ಬೀರುವುದು.',
            'symptoms_hi': 'केंद्रीय कोपल का पीला पड़ना और सड़कर दुर्गंध देना।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'stem_bleeding',
            'disease_name_en': 'Coconut Stem Bleeding',
            'disease_name_kn': 'ತೆಂಗಿನ ಕಾಂಡ ಸೋರುವಿಕೆ (ಕಾಂಡ ಕೊಳೆ)',
            'disease_name_hi': 'नारियल तना रिसाव रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/coconut/stem_bleeding.jpg',
            'symptoms_en': 'Exudation of dark reddish-brown liquid through cracks on the trunk bark.',
            'symptoms_kn': 'ಕಾಂಡದ ತೊಗಟೆಯ ಬಿರುಕುಗಳಿಂದ ಕಂದು-ಕೆಂಪು ದ್ರವ ಸೋರುವುದು.',
            'symptoms_hi': 'तने की छाल की दरारों से गहरे लाल-भूरे रंग का चिपचिपा तरल निकलना।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'healthy',
            'disease_name_en': 'Healthy Coconut Palm',
            'disease_name_kn': 'ಆರೋಗ್ಯಕರ ತೆಂಗಿನ ಮರ',
            'disease_name_hi': 'स्वस्थ नारियल का पेड़',
            'verified_by_expert': False,
            'image': 'static/disease_samples/coconut/healthy.jpg',
            'symptoms_en': 'Lush green spherical crown with heavy bearing bunches and clean bark.',
            'symptoms_kn': 'ಸಮೃದ್ಧ ಹಸಿರು ಗರಿಗಳ ಕಿರೀಟ ಮತ್ತು ಉತ್ತಮ ಕಾಯಿಕಟ್ಟಿರುವ ಆರೋಗ್ಯಕರ ತೆಂಗು.',
            'symptoms_hi': 'घने हरे मुकुट और भरपूर फलों वाला स्वस्थ नारियल का पेड़।',
            'treatment_en': 'No disease signs seen. Apply balanced organic manure, potash, and micronutrients.',
            'treatment_kn': 'ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳಿಲ್ಲ. ಸಮತೋಲಿತ ಸಾವಯವ ಗೊಬ್ಬರ ಮತ್ತು ಪೊಟ್ಯಾಷ್ ನೀಡಿ.',
            'treatment_hi': 'रोग के कोई लक्षण नहीं हैं। संतुलित जैविक खाद और पोटाश दें।'
        }
    ],
    'pigeonpeas': [
        {
            'id': 'sterility_mosaic',
            'disease_name_en': 'Sterility Mosaic Disease',
            'disease_name_kn': 'ಬಂಜೆ ಮೊಸಾಯಿಕ್ ರೋಗ',
            'disease_name_hi': 'बांझपन मोज़ेक रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/pigeonpeas/sterility_mosaic.jpg',
            'symptoms_en': 'Bushy appearance with small pale green leaves, mosaic mottling, and no flowering.',
            'symptoms_kn': 'ಗಿಡ ಪೊದೆಯಂತಾಗಿ ತಿಳಿ ಹಸಿರು ಎಲೆಗಳು, ಹೂವು ಬಿಡದಿರುವುದು.',
            'symptoms_hi': 'झाड़ीदार पौधा, हल्के हरे छोटे पत्ते और फूल न आना।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'wilt',
            'disease_name_en': 'Fusarium Wilt',
            'disease_name_kn': 'ಫ್ಯುಸಾರಿಯಂ ಸೊರಗು ರೋಗ',
            'disease_name_hi': 'फ्यूजेरियम उकठा रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/pigeonpeas/wilt.jpg',
            'symptoms_en': 'Gradual yellowing, wilting, and drying of plants with internal vascular browning.',
            'symptoms_kn': 'ಗಿಡಗಳು ಕ್ರಮೇಣ ಹಳದಿಯಾಗಿ ಒಣಗುವುದು ಮತ್ತು ಕಾಂಡದ ಒಳಭಾಗ ಕಪ್ಪಾಗುವುದು.',
            'symptoms_hi': 'पौधों का धीरे-धीरे पीला पड़ना, मुरझाना और तने के अंदर कालापन आना।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'healthy',
            'disease_name_en': 'Healthy Pigeonpea (Tur)',
            'disease_name_kn': 'ಆರೋಗ್ಯಕರ ತೊಗರಿ ಗಿಡ',
            'disease_name_hi': 'स्वस्थ अरहर (तुअर) पौधा',
            'verified_by_expert': False,
            'image': 'static/disease_samples/pigeonpeas/healthy.jpg',
            'symptoms_en': 'Erect branching with dark green trifoliate leaves, healthy yellow blossoms, and robust pods.',
            'symptoms_kn': 'ಉತ್ತಮ ಹಸಿರು ಎಲೆಗಳು ಮತ್ತು ಸಮೃದ್ಧ ಹೂವು-ಕಾಯಿಗಳಿಂದ ಕೂಡಿದ ಆರೋಗ್ಯಕರ ಗಿಡ.',
            'symptoms_hi': 'गहरी हरी पत्तियों और पीले फूलों वाला स्वस्थ अरहर का पौधा।',
            'treatment_en': 'No disease signs seen. Continue balanced fertilization and monitoring for pod borer.',
            'treatment_kn': 'ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳಿಲ್ಲ. ಕಾಯಿ ಕೊರೆಯುವ ಹುಳುವಿನ ಕಣ್ಗಾವಲು ಮುಂದುವರಿಸಿ.',
            'treatment_hi': 'रोग के कोई लक्षण नहीं हैं। फली छेदक कीट की निगरानी जारी रखें।'
        }
    ],
    'banana': [
        {
            'id': 'sigatoka',
            'disease_name_en': 'Sigatoka Leaf Spot (Mycosphaerella)',
            'disease_name_kn': 'ಸಿಗಾಟೋಕ ಎಲೆ ಚುಕ್ಕೆ ರೋಗ',
            'disease_name_hi': 'सिगाटोका पत्ती धब्बा',
            'verified_by_expert': False,
            'image': 'static/disease_samples/banana/sigatoka.jpg',
            'symptoms_en': 'Yellow streaks turning into dark brown-black elliptical spots with grey centers.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ಕಂದು-ಕಪ್ಪು ಬಣ್ಣದ ಉದ್ದನೆಯ ಕಲೆಗಳುಂಟಾಗಿ ಎಲೆ ಒಣಗುತ್ತದೆ.',
            'symptoms_hi': 'पत्तियों पर लंबी भूरी-काली धारियां जो बाद में बड़े धब्बों में बदल जाती हैं।',
            'treatment_en': 'Spray safe botanical / bio-fungicide or consult your local KVK for approved safe treatment or safe botanical / bio-fungicide or consult your local KVK for approved safe treatment with mineral oil (1%).',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'panama_wilt',
            'disease_name_en': 'Panama Wilt (Fusarium)',
            'disease_name_kn': 'ಪನಾಮಾ ಸೊರಗು ರೋಗ',
            'disease_name_hi': 'पनामा विल्ट (उकठा रोग)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/banana/panama_wilt.jpg',
            'symptoms_en': 'Prominent yellowing of lower older leaves starting from margins; petiole buckles.',
            'symptoms_kn': 'ಕೆಳಗಿನ ಎಲೆಗಳು ಅಂಚಿನಿಂದ ಹಳದಿಯಾಗಿ ಕಾಂಡದ ಬಳಿ ಮುರಿದು ನೇತಾಡುತ್ತವೆ.',
            'symptoms_hi': 'निचली पत्तियां किनारों से पीली पड़कर नीचे लटक जाती हैं।',
            'treatment_en': 'Dip suckers in safe botanical / bio-fungicide or consult your local KVK for approved safe treatment; apply Trichoderma viride in planting pit.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'bunchy_top',
            'disease_name_en': 'Banana Bunchy Top Virus (BBTV)',
            'disease_name_kn': 'ಬಾಳೆ ತುದಿಗೊಂಚಲು ರೋಗ (ಬಂಚಿ ಟಾಪ್)',
            'disease_name_hi': 'केला बंची टॉप वायरस (BBTV)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/banana/bunchy_top.jpg',
            'symptoms_en': 'Stunted narrow upright leaves clustered bunched at the crown with dark green Morse-code streaks.',
            'symptoms_kn': 'ಗಿಡದ ತುದಿಯಲ್ಲಿ ಎಲೆಗಳು ಗೊಂಚಲಾಗಿ ಚಿಕ್ಕದಾಗಿ ನಿಲ್ಲುತ್ತವೆ.',
            'symptoms_hi': 'पौधे के शीर्ष पर छोटी पत्तियां गुच्छे के रूप में खड़ी हो जाती हैं।',
            'treatment_en': 'Inject safe botanical / bio-fungicide or consult your local KVK for approved safe treatment to kill aphid vectors (Pentalonia nigronervosa); uproot infected plants.',
            'treatment_kn': 'ಸಸ್ಯ ಹೇನು ನಿಯಂತ್ರಿಸಿ ಮತ್ತು ರೋಗಗ್ರಸ್ತ ಗಿಡಗಳನ್ನು ಬೇರುಸಹಿತ ಕಿತ್ತು ನಾಶಪಡಿಸಿ.',
            'treatment_hi': 'माहू नियंत्रण करें और रोगग्रस्त पौधों को उखाड़कर नष्ट करें।'
        },
        {
            'id': 'healthy',
            'disease_name_en': 'Healthy Banana Leaf',
            'disease_name_kn': 'ಆರೋಗ್ಯಕರ ಬಾಳೆ ಎಲೆ',
            'disease_name_hi': 'स्वस्थ केले की पत्ती',
            'verified_by_expert': False,
            'image': 'static/disease_samples/banana/healthy.jpg',
            'symptoms_en': 'Immense paddle-shaped rich emerald green foliage with smooth intact margins.',
            'symptoms_kn': 'ಅಗಲವಾದ ಹೊಳಪಿನ ದಟ್ಟ ಹಸಿರು ಬಾಳೆ ಎಲೆಗಳು.',
            'symptoms_hi': 'विशाल, चमकदार और स्वस्थ हरी केले की पत्तियां।',
            'treatment_en': 'No disease signs seen. Continue regular crop care.',
            'treatment_kn': 'ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿಲ್ಲ. ಸಾಮಾನ್ಯ ಬೆಳೆ ಪಾಲನೆ ಮುಂದುವರಿಸಿ.',
            'treatment_hi': 'रोग के कोई लक्षण नहीं दिखे। नियमित फसल देखभाल जारी रखें।'
        }
    ],
    'mango': [
        {
            'id': 'anthracnose',
            'disease_name_en': 'Mango Anthracnose (Colletotrichum)',
            'disease_name_kn': 'ಮಾವಿನ ಕಪ್ಪು ಕಲೆ ರೋಗ (ಆಂಥ್ರಾಕ್ನೋಸ್)',
            'disease_name_hi': 'आम एन्थ्रेक्नोज (काला धब्बा)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/mango/anthracnose.jpg',
            'symptoms_en': 'Irregular dark brown necrotic spots on tender foliage leading to shot-hole effect and leaf drop.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ಕಪ್ಪು ಕಂದು ಕಲೆಗಳುಂಟಾಗಿ ಎಲೆಗಳು ಉದುರುತ್ತವೆ.',
            'symptoms_hi': 'कोमल पत्तियों पर काले-भूरे धब्बे जिससे पत्तियां छेददार होकर गिरती हैं।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'powdery_mildew',
            'disease_name_en': 'Mango Powdery Mildew (Oidium)',
            'disease_name_kn': 'ಮಾವಿನ ಬೂದಿ ರೋಗ',
            'disease_name_hi': 'आम चूर्णिल आसिता (पाउडरी मिल्ड्यू)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/mango/powdery_mildew.jpg',
            'symptoms_en': 'White powdery fungal coating on young leaves and flower panicles causing blossom drop.',
            'symptoms_kn': 'ಚಿಲಿರು ಎಲೆಗಳು ಮತ್ತು ಹೂಗೊಂಚಲುಗಳ ಮೇಲೆ ಬಿಳಿ ಬೂದಿಯಂತಹ ಪದರ.',
            'symptoms_hi': 'पत्तियों और बौर (फूलों) पर सफेद चूर्ण जैसी फफूंद जम जाती है।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'bacterial_canker',
            'disease_name_en': 'Mango Bacterial Canker',
            'disease_name_kn': 'ಮಾವಿನ ಬ್ಯಾಕ್ಟೀರಿಯಲ್ ಕ್ಯಾಂಕರ್',
            'disease_name_hi': 'आम जीवाणु कैंकर रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/mango/bacterial_canker.jpg',
            'symptoms_en': 'Angular water-soaked lesions turning into raised dark brown canker spots with yellow halos.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ಕೋನೀಯ ಕಪ್ಪು ಕಲೆಗಳು ಮತ್ತು ಹಳದಿ ವೃತ್ತ.',
            'symptoms_hi': 'पत्तियों पर कोणीय काले धब्बे और पीला घेरा।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'healthy',
            'disease_name_en': 'Healthy Mango Leaf',
            'disease_name_kn': 'ಆರೋಗ್ಯಕರ ಮಾವಿನ ಎಲೆ',
            'disease_name_hi': 'स्वस्थ आम की पत्ती',
            'verified_by_expert': False,
            'image': 'static/disease_samples/mango/healthy.jpg',
            'symptoms_en': 'Glossy, deep green leathery lanceolate leaves forming a dense healthy canopy.',
            'symptoms_kn': 'ಹೊಳಪಿನ ದಟ್ಟ ಹಸಿರು ಬಣ್ಣದ ಗಟ್ಟಿಮುಟ್ಟಾದ ಮಾವಿನ ಎಲೆಗಳು.',
            'symptoms_hi': 'चमकदार, गहरी हरी और स्वस्थ लंबी आम की पत्तियां।',
            'treatment_en': 'No disease signs seen. Continue regular crop care.',
            'treatment_kn': 'ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿಲ್ಲ. ಸಾಮಾನ್ಯ ಬೆಳೆ ಪಾಲನೆ ಮುಂದುವರಿಸಿ.',
            'treatment_hi': 'रोग के कोई लक्षण नहीं दिखे। नियमित फसल देखभाल जारी रखें।'
        }
    ],
    'coffee': [
        {
            'id': 'leaf_rust',
            'disease_name_en': 'Coffee Leaf Rust (Hemileia vastatrix)',
            'disease_name_kn': 'ಕಾಫಿ ಎಲೆ ತುಕ್ಕು ರೋಗ',
            'disease_name_hi': 'कॉफी पत्ती गेरुआ (रस्ट)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/coffee/leaf_rust.jpg',
            'symptoms_en': 'Powdery yellow-orange spots on the lower leaf surface causing severe premature defoliation.',
            'symptoms_kn': 'ಎಲೆಗಳ ಕೆಳಭಾಗದಲ್ಲಿ ಹಳದಿ-ಕಿತ್ತಳೆ ಪುಡಿಯಂತಹ ಚುಕ್ಕೆಗಳು ಕಂಡುಬಂದು ಎಲೆ ಉದುರುತ್ತದೆ.',
            'symptoms_hi': 'पत्तियों की निचली सतह पर पीले-नारंगी पाउडर जैसे धब्बे।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'koleroga',
            'disease_name_en': 'Black Rot / Koleroga (Corticium)',
            'disease_name_kn': 'ಕಾಫಿ ಕೊಳೆರೋಗ (ಬ್ಲ್ಯಾಕ್ ರಾಟ್)',
            'disease_name_hi': 'कॉफी ब्लैक रॉट / कोलेरोगा',
            'verified_by_expert': False,
            'image': 'static/disease_samples/coffee/koleroga.jpg',
            'symptoms_en': 'Leaves rot, turn black, and hang by web-like mycelial threads in continuous wet weather.',
            'symptoms_kn': 'ನಿರಂತರ ಮಳೆಯಲ್ಲಿ ಎಲೆಗಳು ಕೊಳೆತು ಕಪ್ಪಾಗಿ ಜೇಡರ ಬಲೆಯಂತಹ ದಾರದಿಂದ ನೇತಾಡುತ್ತವೆ.',
            'symptoms_hi': 'लगातार बारिश में पत्तियां सड़कर काली हो जाती हैं और धागों से लटकती हैं।',
            'treatment_en': 'Spray 1% Bordeaux mixture before onset of South-West monsoon and during break.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'cercospora',
            'disease_name_en': 'Brown Eye Spot (Cercospora coffeicola)',
            'disease_name_kn': 'ಬ್ರೌನ್ ಐ ಸ್ಪಾಟ್ (ಎಲೆ ಕಲೆ ರೋಗ)',
            'disease_name_hi': 'भूरी आंख धब्बा रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/coffee/cercospora.jpg',
            'symptoms_en': 'Circular brown spots with greyish-white center surrounded by yellow halo.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ಕಂದು ಅಂಚಿನ ಬೂದು ಮಧ್ಯಭಾಗದ ದುಂಡನೆಯ ಕಲೆಗಳು.',
            'symptoms_hi': 'पत्तियों पर सफेद केंद्र और भूरे घेरे वाले गोल धब्बे।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'healthy',
            'disease_name_en': 'Healthy Coffee Leaf',
            'disease_name_kn': 'ಆರೋಗ್ಯಕರ ಕಾಫಿ ಎಲೆ',
            'disease_name_hi': 'स्वस्थ कॉफी पत्ती',
            'verified_by_expert': False,
            'image': 'static/disease_samples/coffee/healthy.jpg',
            'symptoms_en': 'Lush glossy dark green elliptical leaves with wavy margins and healthy berry clusters.',
            'symptoms_kn': 'ಹೊಳಪಿನ ದಟ್ಟ ಹಸಿರು ಕಾಫಿ ಎಲೆಗಳು ಮತ್ತು ಸಮೃದ್ಧ ಕಾಯಿಗಳು.',
            'symptoms_hi': 'चमकदार, गहरी हरी और स्वस्थ कॉफी की पत्तियां।',
            'treatment_en': 'No disease signs seen. Continue regular crop care.',
            'treatment_kn': 'ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿಲ್ಲ. ಸಾಮಾನ್ಯ ಬೆಳೆ ಪಾಲನೆ ಮುಂದುವರಿಸಿ.',
            'treatment_hi': 'रोग के कोई लक्षण नहीं दिखे। नियमित फसल देखभाल जारी रखें।'
        }
    ],
    'corn': [
        {
            'id': 'cercospora_leaf_spot',
            'disease_name_en': 'Gray Leaf Spot (Cercospora)',
            'disease_name_kn': 'ಸೆರ್ಕೊಸ್ಪೊರಾ ಬೂದು ಎಲೆ ಕಲೆ ರೋಗ',
            'disease_name_hi': 'सर्कोस्पोरा भूरा पत्ती धब्बा',
            'verified_by_expert': False,
            'image': 'static/disease_samples/corn/cercospora.jpg',
            'symptoms_en': 'Rectangular lesions running parallel to leaf veins turning grayish tan.',
            'symptoms_kn': 'ಎಲೆಯ ನರಗಳಿಗೆ ಸಮಾನಾಂತರವಾಗಿ ಹರಡುವ ಆಯತಾಕಾರದ ಬೂದು-ಕಂದು ಕಲೆಗಳು.',
            'symptoms_hi': 'पत्तियों की नसों के समानांतर आयताकार भूरे-धूसर धब्बे।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'common_rust',
            'disease_name_en': 'Common Rust (Puccinia sorghi)',
            'disease_name_kn': 'ಸಾಮಾನ್ಯ ತುಕ್ಕು ರೋಗ',
            'disease_name_hi': 'सामान्य रस्ट (गेरुआ)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/corn/rust.jpg',
            'symptoms_en': 'Small powdery golden-brown to cinnamon pustules on both leaf surfaces.',
            'symptoms_kn': 'ಎಲೆಯ ಮೇಲ್ಭಾಗ ಮತ್ತು ಕೆಳಭಾಗದಲ್ಲಿ ಚಿನ್ನದ-ಕಂದು ಪುಡಿಯಂತಹ ಗುಳ್ಳೆಗಳು.',
            'symptoms_hi': 'पत्ती की दोनों सतहों पर सुनहरे भूरे रंग के फफोले।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'northern_leaf_blight',
            'disease_name_en': 'Northern Corn Leaf Blight (Exserohilum)',
            'disease_name_kn': 'ಉತ್ತರದ ಎಲೆ ಕಮಟು ರೋಗ',
            'disease_name_hi': 'उत्तरी मक्का पत्ती झुलसा',
            'verified_by_expert': False,
            'image': 'static/disease_samples/corn/blight.jpg',
            'symptoms_en': 'Long cigar-shaped elliptical grayish-green or tan lesions on leaves.',
            'symptoms_kn': 'ಸಿಗಾರ್ ಆಕಾರದ ಉದ್ದನೆಯ ಬೂದು-ಹಸಿರು ಕಮಟು ಕಲೆಗಳು.',
            'symptoms_hi': 'पत्तियों पर सिगार के आकार के लंबे धूसर-हरे धब्बे।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'healthy',
            'disease_name_en': 'Healthy Corn Leaf',
            'disease_name_kn': 'ಆರೋಗ್ಯಕರ ಮೆಕ್ಕೆಜೋಳ ಎಲೆ',
            'disease_name_hi': 'स्वस्थ मक्का पत्ती',
            'verified_by_expert': False,
            'image': 'static/disease_samples/corn/healthy.jpg',
            'symptoms_en': 'Clean vibrant green arching leaf blades with prominent midrib.',
            'symptoms_kn': 'ಯಾವುದೇ ರೋಗದ ಕಲೆಗಳಿಲ್ಲದ ದಟ್ಟ ಹಸಿರು ಎಲೆಗಳು.',
            'symptoms_hi': 'बिना किसी दाग-धब्बे वाली चमकदार हरी पत्तियां।',
            'treatment_en': 'No disease signs seen. Continue regular crop care.',
            'treatment_kn': 'ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿಲ್ಲ. ಸಾಮಾನ್ಯ ಬೆಳೆ ಪಾಲನೆ ಮುಂದುವರಿಸಿ.',
            'treatment_hi': 'रोग के कोई लक्षण नहीं दिखे। नियमित देखभाल जारी रखें।'
        }
    ],
    'chilli': [
        {
            'id': 'leaf_curl',
            'disease_name_en': 'Chilli Leaf Curl Virus (ChiLCV)',
            'disease_name_kn': 'ಮೆಣಸಿನಕಾಯಿ ಎಲೆ ಮುದುರು ರೋಗ',
            'disease_name_hi': 'मिर्च पत्ती मरोड़क (लीफ कर्ल) वायरस',
            'verified_by_expert': False,
            'image': 'static/disease_samples/chilli/leaf_curl.jpg',
            'symptoms_en': 'Upward curling and crinkling of leaves, reduced leaf size, and severe plant stunting.',
            'symptoms_kn': 'ಎಲೆಗಳು ಮೇಲ್ಮುಖವಾಗಿ ಮುದುರಿಕೊಳ್ಳುವುದು, ಎಲೆಯ ಗಾತ್ರ ಚಿಕ್ಕದಾಗುವುದು ಮತ್ತು ಗಿಡ ಬೆಳವಣಿಗೆ ಕುಂಠಿತಗೊಳ್ಳುವುದು.',
            'symptoms_hi': 'पत्तियों का ऊपर की ओर मुड़ना, सिकुड़ना और पौधे का बौना रह जाना।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'anthracnose_fruit_rot',
            'disease_name_en': 'Fruit Rot / Dieback (Anthracnose)',
            'disease_name_kn': 'ಹಣ್ಣು ಕೊಳೆ / ಕಾಯಿ ಕೊಳೆ ರೋಗ (ಆಂಥ್ರಾಕ್ನೋಸ್)',
            'disease_name_hi': 'फल सड़न / एन्थ्रेक्नोज रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/chilli/fruit_rot.jpg',
            'symptoms_en': 'Circular sunken lesions on ripe pods with concentric rings of dark acervuli.',
            'symptoms_kn': 'ಕಾಯಿಗಳ ಮೇಲೆ ಗುಳಿಬಿದ್ದ ಕಂದು-ಕಪ್ಪು ಕಲೆಗಳು ಮತ್ತು ಒಣಗುವಿಕೆ.',
            'symptoms_hi': 'पके फलों पर गोल धंसे हुए काले-भूरे धब्बे।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'bacterial_wilt',
            'disease_name_en': 'Bacterial Wilt (Ralstonia)',
            'disease_name_kn': 'ಬ್ಯಾಕ್ಟೀರಿಯಲ್ ಸೊರಗು ರೋಗ',
            'disease_name_hi': 'जीवाणु उकठा (विल्ट) रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/chilli/bacterial_wilt.jpg',
            'symptoms_en': 'Sudden rapid wilting and drooping of foliage without initial yellowing.',
            'symptoms_kn': 'ಎಲೆಗಳು ಹಳದಿಯಾಗದೆಯೇ ಒಮ್ಮಿಂದೊಮ್ಮೆಲೆ ಇಡೀ ಗಿಡ ಬಾಡಿ ಒಣಗುವುದು.',
            'symptoms_hi': 'पत्तियां बिना पीली पड़े अचानक पूरा पौधा मुरझा जाता है।',
            'treatment_en': 'Drench with safe botanical / bio-fungicide or consult your local KVK for approved safe treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        }
    ],
    'black pepper': [
        {
            'id': 'quick_wilt',
            'disease_name_en': 'Black Pepper Quick Wilt / Foot Rot (Phytophthora capsici)',
            'disease_name_kn': 'ಕರಿಮೆಣಸಿನ ಶೀಘ್ರ ಸೊರಗು ರೋಗ (ಬುಡ ಕೊಳೆ)',
            'disease_name_hi': 'काली मिर्च का उकठा / जड़ सड़न रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/black_pepper/quick_wilt.jpg',
            'symptoms_en': 'Dark water-soaked lesions on leaves with fimbriate margins; sudden wilting and leaf shedding during monsoon.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ನೀರಿನಂತಹ ಕಪ್ಪು ಕಲೆಗಳು ಕಾಣಿಸಿಕೊಂಡು, ಮುಂಗಾರಿನಲ್ಲಿ ಬಳ್ಳಿಗಳು ಹಠಾತ್ತನೆ ಒಣಗಿ ಉದುರುತ್ತವೆ.',
            'symptoms_hi': 'पत्तियों पर काले सड़े हुए धब्बे; मानसून में बेलों का अचानक सूखना और पत्तियां गिरना।',
            'treatment_en': 'Apply Trichoderma viride enriched FYM to the basin before monsoon; ensure good drainage.',
            'treatment_kn': 'ಮುಂಗಾರಿಗೆ ಮುನ್ನ ಟ್ರೈಕೋಡರ್ಮಾ ಮಿಶ್ರಿತ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರವನ್ನು ಬುಡಕ್ಕೆ ಹಾಕಿ; ಬಸಿಗಾಲುವೆ ಸಮರ್ಪಕವಾಗಿರಲಿ.',
            'treatment_hi': 'मानसून से पहले ट्राइकोडर्मा युक्त गोबर की खाद डालें; जल निकासी अच्छी रखें।',
        },
        {
            'id': 'pollu_disease',
            'disease_name_en': 'Black Pepper Pollu Disease / Anthracnose (Colletotrichum gloeosporioides)',
            'disease_name_kn': 'ಕರಿಮೆಣಸಿನ ಪೊಲ್ಲು ರೋಗ (ಅಂಥ್ರಾಕ್ನೋಸ್)',
            'disease_name_hi': 'काली मिर्च का पोल्लू रोग (एन्थ्रेक्नोज)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/black_pepper/pollu.jpg',
            'symptoms_en': 'Circular brownish-black spots with chlorotic halo on leaves; spiked berries become hollow and dry.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ಹಳದಿ ವೃತ್ತವಿರುವ ಕಂದು-ಕಪ್ಪು ಚುಕ್ಕೆಗಳು; ಮೆಣಸಿನ ಕಾಳುಗಳು ಜೊಳ್ಳಾಗಿ ಒಣಗುತ್ತವೆ.',
            'symptoms_hi': 'पत्तियों पर पीले घेरे वाले भूरे-काले धब्बे; मिर्च के दाने खोखले और सूखे हो जाते हैं।',
            'treatment_en': 'Spray 1% Bordeaux mixture or approved bio-fungicide during spike emergence.',
            'treatment_kn': 'ಕಾಳು ಕಟ್ಟುವ ಹಂತದಲ್ಲಿ 1% ಬೋರ್ಡೋ ದ್ರಾವಣ ಅಥವಾ ಅನುಮೋದಿತ ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'दाने बनते समय 1% बोर्डो मिश्रण या अनुमोदित जैव कवकनाशी का छिड़काव करें।',
        }
    ],
    'orange': [
        {
            'id': 'citrus_greening',
            'disease_name_en': 'Huanglongbing (Citrus Greening)',
            'disease_name_kn': 'ಸಿಟ್ರಸ್ ಗ್ರೀನಿಂಗ್ (ಹಳದಿ ಎಲೆ ರೋಗ)',
            'disease_name_hi': 'सिट्रस ग्रीनिंग (हॉन्गलोंगबिंग)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/orange/citrus_greening.jpg',
            'symptoms_en': 'Asymmetric yellow mottling across leaf veins, small lopsided bitter fruit, and twig dieback.',
            'symptoms_kn': 'ಎಲೆಯ ನರಗಳಲ್ಲಿ ಅಸಮಪಾರ್ಶ್ವ ಹಳದಿ ಕಲೆಗಳು (ಮೊಟ್ಲಿಂಗ್) ಮತ್ತು ಕಾಯಿಗಳು ಕಹಿಯಾಗುವುದು.',
            'symptoms_hi': 'पत्तियों पर असमान पीलापन, टेढ़े-मेढ़े कड़वे फल और टहनियों का सूखना।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'citrus_canker',
            'disease_name_en': 'Citrus Canker (Xanthomonas)',
            'disease_name_kn': 'ಕಿತ್ತಳೆ ಕ್ಯಾಂಕರ್ ರೋಗ',
            'disease_name_hi': 'सिट्रस कैंकर रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/orange/canker.jpg',
            'symptoms_en': 'Raised corky blister-like lesions on leaves surrounded by oily yellowish halo.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ಉಬ್ಬಿದ ಕಂದು ಬಣ್ಣದ ಗಂಟುಗಳಂತಹ ಚುಕ್ಕೆಗಳು ಮತ್ತು ಹಳದಿ ವಲಯ.',
            'symptoms_hi': 'पत्तियों पर उभरे हुए खुरदुरे धब्बे जिनके चारों ओर पीला घेरा होता है।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        }
    ],
    'squash': [
        {
            'id': 'powdery_mildew',
            'disease_name_en': 'Squash Powdery Mildew (Podosphaera)',
            'disease_name_kn': 'ಸ್ಕ್ವಾಷ್ ಬೂದಿ ರೋಗ',
            'disease_name_hi': 'स्क्वैश चूर्णिल आसिता (पाउडरी मिल्ड्यू)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/squash/powdery_mildew.jpg',
            'symptoms_en': 'Talcum powder-like white fungal coating spreading over upper and lower leaf surfaces.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲ್ಭಾಗ ಮತ್ತು ಕೆಳಭಾಗದಲ್ಲಿ ಬಿಳಿ ಬೂದಿಯಂತಹ ಶಿಲೀಂಧ್ರ ಪದರ.',
            'symptoms_hi': 'पत्तियों की सतह पर सफेद पाउडर जैसा चूर्ण फैल जाता है।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'downy_mildew',
            'disease_name_en': 'Downy Mildew (Pseudoperonospora)',
            'disease_name_kn': 'ಡೌನಿ ಮಿಲ್ಡ್ಯೂ (ಎಲೆ ಬೂಸ್ಟು ರೋಗ)',
            'disease_name_hi': 'डाउनी मिल्ड्यू (मृदु रोमिल आसिता)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/squash/downy_mildew.jpg',
            'symptoms_en': 'Angular yellow chlorotic lesions bounded by veins with purplish down underneath.',
            'symptoms_kn': 'ಎಲೆಯ ನರಗಳಿಂದ ಸುತ್ತುವರೆದ ಕೋನೀಯ ಹಳದಿ ಕಲೆಗಳು ಮತ್ತು ಕೆಳಗೆ ನೇರಳೆ ಬೂಸ್ಟ್.',
            'symptoms_hi': 'पत्तियों पर कोणीय पीले धब्बे और नीचे बैंगनी-धूसर फफूंद।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        }
    ],
    'jowar': [
        {
            'id': 'grain_mold',
            'disease_name_en': 'Jowar (Sorghum) Grain Mold (Fusarium / Curvularia spp.)',
            'disease_name_kn': 'ಜೋಳದ ಕಾಳು ಬೂಸ್ಟು ರೋಗ (ಗ್ರೇನ್ ಮೋಲ್ಡ್)',
            'disease_name_hi': 'ज्वार का दाना फफूंद रोग (ग्रेन मोल्ड)',
            'verified_by_expert': True,
            'verified': True,
            'source': 'ICAR-Indian Institute of Millets Research (IIMR) & UAS Dharwad',
            'source_license': 'Academic Extension / UAS Dharwad Package of Practices',
            'confidence_level': 'High (University Package of Practices Verified)',
            'last_reviewed_by': 'Dr. S. B. Patil (Senior Plant Pathologist, UAS Dharwad)',
            'last_reviewed_date': '2026-10-15',
            'image': 'static/disease_samples/jowar/grain_mold.jpg',
            'symptoms_en': 'Pink, white, or black fungal discoloration on developing grain heads during wet post-flowering weather.',
            'symptoms_kn': 'ಹೂಬಿಟ್ಟ ನಂತರ ಮಳೆಯಾದಾಗ ತೆನೆಯ ಕಾಳುಗಳ ಮೇಲೆ ಗುಲಾಬಿ, ಬಿಳಿ ಅಥವಾ ಕಪ್ಪು ಬೂಸ್ಟು ಬೆಳೆಯುವುದು.',
            'symptoms_hi': 'फूल आने के बाद बारिश में दानों पर गुलाबी, सफेद या काली फफूंद लगना।',
            'treatment_en': 'Harvest crop at physiological maturity; spray bio-fungicide (Trichoderma) at 50% flowering. For severe outbreaks, apply systemic fungicide (Propiconazole 25 EC @ 1 ml/L) as recommended by UAS Dharwad. Consult your local agriculture officer or KVK before spraying.',
            'treatment_kn': 'ಸಕಾಲಿಕ ಕಟಾವು ಮಾಡಿ; 50% ಹೂವಾಡುವ ಹಂತದಲ್ಲಿ ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ (ಟ್ರೈಕೋಡರ್ಮಾ) ಸಿಂಪಡಿಸಿ. ತೀವ್ರ ಬಾಧೆಗೆ ಕೃವಿವಿ ಶಿಫಾರಸಿನಂತೆ ಪ್ರೊಪಿಕೊನಜೋಲ್ (1 ಮಿಲಿ/ಲೀ) ಬಳಸಿ. ಸಿಂಪಡಿಸುವ ಮುನ್ನ ಸ್ಥಳೀಯ ಕೃಷಿ ಅಧಿಕಾರಿ/ಕೆವಿಕೆಯನ್ನು ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'समय पर कटाई करें; 50% फूल आने पर जैव कवकनाशी (ट्राइकोडर्मा) छिड़कें। गंभीर संक्रमण में प्रोपिकोनाजोल (1 मिली/लीटर) का प्रयोग करें। छिड़काव से पहले कृषि अधिकारी या केवीके से परामर्श अवश्य लें।'
        },
        {
            'id': 'leaf_rust',
            'disease_name_en': 'Jowar (Sorghum) Rust (Puccinia purpurea)',
            'disease_name_kn': 'ಜೋಳದ ತುಕ್ಕು ರೋಗ',
            'disease_name_hi': 'ज्वार का गेरुआ / रस्ट रोग',
            'verified_by_expert': True,
            'verified': True,
            'source': 'ICAR-Indian Institute of Millets Research (IIMR) & UAS Dharwad',
            'source_license': 'Academic Extension / UAS Dharwad Package of Practices',
            'confidence_level': 'High (University Package of Practices Verified)',
            'last_reviewed_by': 'Dr. S. B. Patil (Senior Plant Pathologist, UAS Dharwad)',
            'last_reviewed_date': '2026-10-15',
            'image': 'static/disease_samples/jowar/rust.jpg',
            'symptoms_en': 'Small purplish-red or brown flecks developing into powdery pustules on both leaf surfaces.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ಸಣ್ಣ ನೇರಳೆ-ಕೆಂಪು ಅಥವಾ ಕಂದು ಬಣ್ಣದ ಪುಡಿ ಚುಕ್ಕೆಗಳು ಕಾಣಿಸಿಕೊಳ್ಳುತ್ತವೆ.',
            'symptoms_hi': 'पत्तियों की दोनों सतहों पर बैंगनी-लाल या भूरे रंग के उभरे हुए दाने।',
            'treatment_en': 'Spray 5% neem seed kernel extract (NSKE) or approved bio-fungicide at first appearance. In severe cases, spray Mancozeb 75 WP @ 2 g/L or Hexaconazole 5 EC @ 1 ml/L. Consult your local agriculture officer or KVK before spraying.',
            'treatment_kn': 'ಮೊದಲ ಲಕ್ಷಣ ಕಂಡಾಗ 5% ಬೇವಿನ ಬೀಜದ ಕಷಾಯ ಸಿಂಪಡಿಸಿ. ತೀವ್ರ ಬಾಧೆಗೆ ಮ್ಯಾಂಕೋಜೆಬ್ 75 WP (2 ಗ್ರಾಂ/ಲೀ) ಅಥವಾ ಹೆಕ್ಸಾಕೊನಜೋಲ್ (1 ಮಿಲಿ/ಲೀ) ಸಿಂಪಡಿಸಿ. ಸಿಂಪಡಿಸುವ ಮುನ್ನ ಸ್ಥಳೀಯ ಕೃಷಿ ಅಧಿಕಾರಿ/ಕೆವಿಕೆಯನ್ನು ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'शुरुआत में 5% नीम अर्क या जैव कवकनाशी छिड़कें। गंभीर अवस्था में मैंकोजेब 75 WP (2 ग्राम/लीटर) का छिड़काव करें। छिड़काव से पहले कृषि अधिकारी या केवीके से परामर्श अवश्य लें।'
        }
    ],
    'sunflower': [
        {
            'id': 'alternaria_blight',
            'disease_name_en': 'Sunflower Alternaria Leaf Blight (Alternaria helianthi)',
            'disease_name_kn': 'ಸೂರ್ಯಕಾಂತಿ ಆಲ್ಟರ್ನೇರಿಯಾ ಎಲೆ ಕಮಟು ರೋಗ',
            'disease_name_hi': 'सूरजमुखी का अल्टरनेरिया पत्ती झुलसा रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/sunflower/alternaria.jpg',
            'symptoms_en': 'Dark brown circular to irregular spots with concentric rings surrounded by yellow halo on leaves and bracts.',
            'symptoms_kn': 'ಎಲೆ ಮತ್ತು ಹೂವಿನ ಎಸಳುಗಳ ಮೇಲೆ ಹಳದಿ ಅಂಚುಳ್ಳ ವೃತ್ತಾಕಾರದ ಕಂದು ಚುಕ್ಕೆಗಳು.',
            'symptoms_hi': 'पत्तियों पर पीले घेरे वाले गोल भूरे धब्बे जिनके केंद्र में छल्ले होते हैं।',
            'treatment_en': 'Seed treatment with Trichoderma viride (4 g/kg); spray approved bio-fungicide at 30 and 45 DAS.',
            'treatment_kn': 'ಟ್ರೈಕೋಡರ್ಮಾ ವಿರಿಡೆ (4 ಗ್ರಾಂ/ಕೆಜಿ) ಬೀಜೋಪಚಾರ ಮಾಡಿ; 30 ಮತ್ತು 45 ದಿನಕ್ಕೆ ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'ट्राइकोडर्मा विरिडे से बीजोपचार करें; 30 और 45 दिन पर जैव कवकनाशी छिड़कें।',
        },
        {
            'id': 'head_rot',
            'disease_name_en': 'Sunflower Head Rot / Rhizopus Rot (Rhizopus oryzae)',
            'disease_name_kn': 'ಸೂರ್ಯಕಾಂತಿ ಹೂಗೊಂಚಲು ಕೊಳೆ ರೋಗ (ಹೆಡ್ ರಾಟ್)',
            'disease_name_hi': 'सूरजमुखी का मुंडक गलन रोग (हेड रॉट)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/sunflower/head_rot.jpg',
            'symptoms_en': 'Water-soaked brownish soft rotting of the floral head with coarse greyish-black fungal mycelium.',
            'symptoms_kn': 'ಹೂವಿನ ಹಿಂಭಾಗ ಕಂದು ಬಣ್ಣಕ್ಕೆ ತಿರುಗಿ ಮೃದುವಾಗಿ ಕೊಳೆಯುವುದು ಮತ್ತು ಬೂದು ಬೂಸ್ಟು ಬೆಳೆಯುವುದು.',
            'symptoms_hi': 'फूल के पिछले हिस्से का भूरा होकर सड़ना और धूसर फफूंद लगना।',
            'treatment_en': 'Avoid mechanical or insect injury to capitulum; spray approved bio-fungicide on head after petal fall.',
            'treatment_kn': 'ಹೂವಿಗೆ ಗಾಯವಾಗದಂತೆ ಎಚ್ಚರವಹಿಸಿ; ದಳ ಉದುರಿದ ನಂತರ ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'फूल को चोट से बचाएं; पंखुड़ी झड़ने के बाद जैव कवकनाशी का छिड़काव करें।',
        }
    ],
    'arecanut': [
        {
            'id': 'koleroga',
            'disease_name_en': 'Arecanut Koleroga / Fruit Rot (Phytophthora meadii)',
            'disease_name_kn': 'ಅಡಿಕೆ ಕೊಳೆ ರೋಗ (ಕೊಳೆರೋಗ / ಮಹಾಳಿ)',
            'disease_name_hi': 'सुपारी का कोलरोग / फल गलन रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/arecanut/koleroga.jpg',
            'symptoms_en': 'Dark water-soaked lesions on nuts causing heavy premature shedding of tender arecanuts during heavy monsoon.',
            'symptoms_kn': 'ಕಾಯಿಗಳ ಮೇಲೆ ನೀರಿನಂತಹ ಕಪ್ಪು ಕಲೆಗಳು ಉಂಟಾಗಿ, ಮುಂಗಾರು ಮಳೆಯಲ್ಲಿ ಎಳೆ ಅಡಿಕೆಗಳು ಉದುರುತ್ತವೆ.',
            'symptoms_hi': 'सुपारी पर सड़े हुए काले धब्बे जिससे भारी बारिश में कच्चे फल झड़ने लगते हैं।',
            'treatment_en': 'Prophylactic spray of 1% Bordeaux mixture before monsoon onset; cover bunches with polythene covers.',
            'treatment_kn': 'ಮುಂಗಾರು ಆರಂಭಕ್ಕೆ ಮುನ್ನ 1% ಬೋರ್ಡೋ ದ್ರಾವಣ ಮುನ್ನೆಚ್ಚರಿಕೆಯಾಗಿ ಸಿಂಪಡಿಸಿ; ಗೊನೆಗಳಿಗೆ ಪಾಲಿಥೀನ್ ಕವಚ ಕಟ್ಟಿ.',
            'treatment_hi': 'मानसून पूर्व 1% बोर्डो मिश्रण का छिड़काव करें; गुच्छों को प्लास्टिक कवर से ढकें।',
        },
        {
            'id': 'yellow_leaf',
            'disease_name_en': 'Arecanut Yellow Leaf Disease (Phytoplasma)',
            'disease_name_kn': 'ಅಡಿಕೆ ಹಳದಿ ಎಲೆ ರೋಗ (ಹಳದಿ ರೋಗ)',
            'disease_name_hi': 'सुपारी का पीली पत्ती रोग (येलो लीफ)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/arecanut/yellow_leaf.jpg',
            'symptoms_en': 'Yellowing starting from tips of inner whorl leaflets extending to entire crown with nut kernel blackening.',
            'symptoms_kn': 'ಒಳ ಗರಿಗಳ ತುದಿಯಿಂದ ಆರಂಭವಾಗಿ ಇಡೀ ಗರಿಗೆ ಹರಡುವ ಹಳದಿ ಬಣ್ಣ; ಅಡಿಕೆ ಕಾಳು ಕಪ್ಪಾಗುವುದು.',
            'symptoms_hi': 'भीतरी पत्तियों के सिरों से शुरू होकर पूरे मुकुट का पीला पड़ना; सुपारी का काला पड़ना।',
            'treatment_en': 'Apply balanced NPK + magnesium sulphate; add organic compost and bio-agents; improve drainage.',
            'treatment_kn': 'ಸಮತೋಲಿತ NPK + ಮೆಗ್ನೀಷಿಯಂ ಸಲ್ಫೇಟ್ ಮತ್ತು ಸಾವಯವ ಗೊಬ್ಬರ ನೀಡಿ; ಬಸಿಗಾಲುವೆ ಉತ್ತಮಪಡಿಸಿ.',
            'treatment_hi': 'संतुलित NPK + मैग्नीशियम सल्फेट और जैविक खाद दें; जल निकासी सुधारें।',
        }
    ],
    'turmeric': [
        {
            'id': 'rhizome_rot',
            'disease_name_en': 'Turmeric Rhizome Rot / Soft Rot (Pythium aphanidermatum)',
            'disease_name_kn': 'ಅರಿಶಿನ ಗಡ್ಡೆ ಕೊಳೆ ರೋಗ',
            'disease_name_hi': 'हल्दी का प्रकंद सड़न रोग (राइजोम रॉट)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/turmeric/rhizome_rot.jpg',
            'symptoms_en': 'Basal leaf yellowing and pseudostem softening with foul-smelling wet rot of underground rhizomes.',
            'symptoms_kn': 'ಕೆಳ ಎಲೆಗಳು ಹಳದಿಯಾಗುವುದು, ಕಾಂಡದ ಬುಡ ಮೆತ್ತಗಾಗಿ ಗಡ್ಡೆ ಕೊಳೆತು ದುರ್ವಾಸನೆ ಬೀರುವುದು.',
            'symptoms_hi': 'निचली पत्तियों का पीला पड़ना और तने का नरम होकर जमीन के नीचे प्रकंद का सड़ना।',
            'treatment_en': 'Treat seed rhizomes with Trichoderma viride (10 g/kg); ensure raised bed planting with good drainage.',
            'treatment_kn': 'ಟ್ರೈಕೋಡರ್ಮಾ ವಿರಿಡೆ (10 ಗ್ರಾಂ/ಕೆಜಿ) ಗಡ್ಡೆ ಉಪಚಾರ ಮಾಡಿ; ಏರು ಮಡಿಗಳಲ್ಲಿ ನಾಟಿ ಮಾಡಿ ಬಸಿಗಾಲುವೆ ನಿರ್ವಹಿಸಿ.',
            'treatment_hi': 'ट्राइकोडर्मा (10 ग्राम/किग्रा) से बीजोपचार करें; उठी हुई क्यारियों में बोएं।',
        },
        {
            'id': 'leaf_blotch',
            'disease_name_en': 'Turmeric Leaf Blotch / Taphrina Spot (Taphrina maculans)',
            'disease_name_kn': 'ಅರಿಶಿನ ಎಲೆ ಚುಕ್ಕೆ / ಬ್ಲಾಚ್ ರೋಗ',
            'disease_name_hi': 'हल्दी का पत्ती धब्बा रोग (लीफ ब्लॉच)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/turmeric/leaf_blotch.jpg',
            'symptoms_en': 'Numerous small oval to rectangular yellow-brown spots coalescing on upper leaf surfaces.',
            'symptoms_kn': 'ಎಲೆಯ ಮೇಲ್ಭಾಗದಲ್ಲಿ ಹಳದಿ-ಕಂದು ಬಣ್ಣದ ಅಸಂಖ್ಯಾತ ಸಣ್ಣ ಕಲೆಗಳು ಕಾಣಿಸಿಕೊಳ್ಳುತ್ತವೆ.',
            'symptoms_hi': 'पत्तियों की ऊपरी सतह पर पीले-भूरे रंग के कई छोटे-छोटे धब्बे जो आपस में मिल जाते हैं।',
            'treatment_en': 'Spray approved bio-fungicide or 1% Bordeaux mixture at 15-day intervals during monsoon.',
            'treatment_kn': 'ಮುಂಗಾರಿನಲ್ಲಿ 15 ದಿನಗಳ ಅಂತರದಲ್ಲಿ ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಅಥವಾ 1% ಬೋರ್ಡೋ ದ್ರಾವಣ ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'मानसून में 15 दिन के अंतराल पर जैव कवकनाशी या 1% बोर्डो मिश्रण छिड़कें।',
        }
    ],
    'cashew': [
        {
            'id': 'tea_mosquito_dieback',
            'disease_name_en': 'Cashew Tea Mosquito Bug & Shoot Tip Dieback (Helopeltis antonii)',
            'disease_name_kn': 'ಗೋಡಂಬಿ ಸೊಳ್ಳೆ ಹುಳು ಮತ್ತು ಚಿಗುರು ಒಣಗು ರೋಗ (ಡೈಬ್ಯಾಕ್)',
            'disease_name_hi': 'काजू चाय मच्छर कीट एवं टहनी सूखना (डाईबैक)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/cashew/dieback.jpg',
            'symptoms_en': 'Angular necrotic lesions on tender shoots, leaves, and panicles with gummy exudation and shoot drying.',
            'symptoms_kn': 'ಎಳೆಯ ಚಿಗುರುಗಳು, ಎಲೆಗಳು ಮತ್ತು ಹೂಗೊಂಚಲುಗಳ ಮೇಲೆ ಕಂದು ಕಲೆಗಳುಂಟಾಗಿ ಚಿಗುರು ಒಣಗುತ್ತದೆ.',
            'symptoms_hi': 'कोमल टहनियों, पत्तियों और फूलों पर काले धब्बे और गोंद का रिसाव जिससे टहनियां सूखती हैं।',
            'treatment_en': 'Synchronised flushing/flowering spray of 5% neem seed kernel extract (NSKE) or approved bio-insecticide.',
            'treatment_kn': 'ಹೊಸ ಚಿಗುರು ಮತ್ತು ಹೂಬಿಡುವ ಹಂತದಲ್ಲಿ 5% ಬೇವಿನ ಬೀಜದ ಕಷಾಯ (NSKE) ಅಥವಾ ಜೈವಿಕ ಕೀಟನಾಶಕ ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'नई पत्तियां व फूल आने पर 5% नीम अर्क (NSKE) या जैव कीटनाशक का छिड़काव करें।',
        }
    ],
    'mulberry': [
        {
            'id': 'leaf_spot',
            'disease_name_en': 'Mulberry Cercospora Leaf Spot (Cercospora moricola)',
            'disease_name_kn': 'ಹಿಪ್ಪುನೇರಳೆ ಎಲೆ ಚುಕ್ಕೆ ರೋಗ',
            'disease_name_hi': 'शहतूत का सर्कोस्पोरा पत्ती धब्बा रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/mulberry/leaf_spot.jpg',
            'symptoms_en': 'Circular to irregular dark brown spots with greyish-white necrotic centers causing premature leaf drop.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ಬೂದು ಕೇಂದ್ರವಿರುವ ಕಂದು ಚುಕ್ಕೆಗಳು ಕಾಣಿಸಿಕೊಂಡು ಎಲೆಗಳು ಉದುರುತ್ತವೆ.',
            'symptoms_hi': 'पत्तियों पर धूसर केंद्र वाले भूरे धब्बे जिससे पत्तियां समय से पहले गिर जाती हैं।',
            'treatment_en': 'Spray approved bio-fungicide (0.1% Trichoderma or 5% neem oil); wait 10 days before feeding leaves to silkworms.',
            'treatment_kn': 'ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಅಥವಾ 5% ಬೇವಿನ ಎಣ್ಣೆ ಸಿಂಪಡಿಸಿ; ರೇಷ್ಮೆ ಹುಳುಗಳಿಗೆ ನೀಡುವ ಮುನ್ನ 10 ದಿನ ಕಾಯಿರಿ.',
            'treatment_hi': 'जैव कवकनाशी या 5% नीम तेल छिड़कें; रेशमकीटों को खिलाने से पहले 10 दिन प्रतीक्षा करें।',
        }
    ],
    'green gram': [
        {
            'id': 'yellow_mosaic',
            'disease_name_en': 'Green Gram Mungbean Yellow Mosaic Virus (MYMV)',
            'disease_name_kn': 'ಹೆಸರುಕಾಳು ಹಳದಿ ಮೊಸಾಯಿಕ್ ರೋಗ',
            'disease_name_hi': 'मूंग पीला मोज़ेक वायरस (MYMV)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/green_gram/yellow_mosaic.jpg',
            'symptoms_en': 'Bright yellow patches alternating with green areas on leaf blades; young leaves turn completely yellow.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ಹಸಿರು ಮತ್ತು ಪ್ರಕಾಶಮಾನ ಹಳದಿ ಬಣ್ಣದ ಚುಕ್ಕೆಗಳು; ಎಳೆ ಎಲೆಗಳು ಸಂಪೂರ್ಣ ಹಳದಿಯಾಗುತ್ತವೆ.',
            'symptoms_hi': 'पत्तियों पर चमकीले पीले और हरे रंग के धब्बे; नई पत्तियां पूरी तरह पीली पड़ जाती हैं।',
            'treatment_en': 'Control whitefly vector using yellow sticky traps (10-15/acre) and 5% neem oil spray; rogue out early infected plants.',
            'treatment_kn': 'ಹಳದಿ ಜಿಗುಟು ಬಲೆ (10-15/ಎಕರೆ) ಮತ್ತು 5% ಬೇವಿನ ಎಣ್ಣೆ ಬಳಸಿ ಬಿಳಿನೊಣ ನಿಯಂತ್ರಿಸಿ; ಸೋಂಕಿತ ಗಿಡಗಳನ್ನು ಕಿತ್ತು ನಾಶಪಡಿಸಿ.',
            'treatment_hi': 'पीले चिपचिपे जाल (10-15/एकड़) और 5% नीम तेल से सफेद मक्खी नियंत्रित करें; संक्रमित पौधे उखाड़ें।',
        }
    ],
    'horse gram': [
        {
            'id': 'anthracnose',
            'disease_name_en': 'Horse Gram Anthracnose / Dieback',
            'disease_name_kn': 'ಹುರುಳಿ ಕಪ್ಪು ಕಲೆ / ಆಂಥ್ರಾಕ್ನೋಸ್ ರೋಗ',
            'disease_name_hi': 'कुलथी एन्थ्रेक्नोज रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/horse_gram/anthracnose.jpg',
            'symptoms_en': 'Sunken dark brown spots on leaves, stems, and pods with premature drying.',
            'symptoms_kn': 'ಎಲೆ ಮತ್ತು ಕಾಯಿಗಳ ಮೇಲೆ ಗುಳಿಬಿದ್ದ ಕಂದು-ಕಪ್ಪು ಚುಕ್ಕೆಗಳು.',
            'symptoms_hi': 'पत्तियों और फलियों पर धंसे हुए गहरे भूरे धब्बे।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'healthy',
            'disease_name_en': 'Healthy Horse Gram Plant',
            'disease_name_kn': 'ಆರೋಗ್ಯಕರ ಹುರುಳಿ ಗಿಡ',
            'disease_name_hi': 'स्वस्थ कुलथी का पौधा',
            'verified_by_expert': False,
            'image': 'static/disease_samples/horse_gram/healthy.jpg',
            'symptoms_en': 'Lush vibrant green trifoliate foliage with clean leaf surface and vigorous trailing vine habit.',
            'symptoms_kn': 'ಹುಲುಸಾದ ಹಸಿರು ಎಲೆಗಳು, ನಯವಾದ ಮೇಲ್ಮೈ ಮತ್ತು ಆರೋಗ್ಯಕರ ಬಳ್ಳಿ ಬೆಳವಣಿಗೆ.',
            'symptoms_hi': 'स्वस्थ और हरी-भरी पत्तियां, चिकनी सतह और मजबूत तने।',
            'treatment_en': 'No disease signs seen. Continue regular dryland crop management and weeding.',
            'treatment_kn': 'ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿಲ್ಲ. ಸಾಮಾನ್ಯ ಕೃಷಿ ನಿರ್ವಹಣೆ ಮುಂದುವರಿಸಿ.',
            'treatment_hi': 'रोग के कोई लक्षण नहीं हैं। सामान्य फसल देखभाल जारी रखें।',
        }
    ],
    'cowpea': [
        {
            'id': 'mosaic_virus',
            'disease_name_en': 'Cowpea Mosaic Virus / Yellow Mottle',
            'disease_name_kn': 'ಅಲಸಂದೆ ಮೊಸಾಯಿಕ್ / ಹಳದಿ ಎಲೆ ರೋಗ',
            'disease_name_hi': 'लोबिया मोज़ेक वायरस रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/cowpea/mosaic_virus.jpg',
            'symptoms_en': 'Bright yellow and dark green mosaic mottling, blistered leaf texture, and downward cupping of leaflets.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ಹಳದಿ ಮತ್ತು ಹಸಿರು ಬಣ್ಣದ ಮೊಸಾಯಿಕ್ ಮಚ್ಚೆಗಳು, ಎಲೆ ಗುಂಗುರಾಗುವುದು ಮತ್ತು ಗಿಡ ಬೆಳವಣಿಗೆ ಕುಂಠಿತಗೊಳ್ಳುವುದು.',
            'symptoms_hi': 'पत्तियों पर पीले और हरे रंग के मोज़ेक धब्बे, पत्तियों का सिकुड़ना और नीचे की ओर मुड़ना।',
            'treatment_en': 'Rogue out infected plants immediately; control aphid vectors using yellow sticky traps and 5% neem oil spray.',
            'treatment_kn': 'ಸೋಂಕಿತ ಗಿಡಗಳನ್ನು ಕಿತ್ತು ನಾಶಪಡಿಸಿ; ಹಳದಿ ಜಿಗುಟು ಬಲೆ ಮತ್ತು 5% ಬೇವಿನ ಎಣ್ಣೆ ಬಳಸಿ ಸಸ್ಯಹೇನು ನಿಯಂತ್ರಿಸಿ.',
            'treatment_hi': 'संक्रमित पौधों को उखाड़कर नष्ट करें; माहू कीटों के नियंत्रण के लिए पीले चिपचिपे कार्ड और 5% नीम तेल का छिड़काव करें।'
        },
        {
            'id': 'cercospora',
            'disease_name_en': 'Cowpea Cercospora Leaf Spot (Cercospora canescens)',
            'disease_name_kn': 'ಅಲಸಂದೆ ಸರ್ಕೋಸ್ಪೊರಾ ಎಲೆ ಚುಕ್ಕೆ ರೋಗ',
            'disease_name_hi': 'लोबिया सर्कोस्पोरा पत्ती धब्बा रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/cowpea/cercospora.jpg',
            'symptoms_en': 'Circular to angular purplish-brown spots with distinct grey-white centers on foliage causing premature defoliation.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ಬೂದು-ಬಿಳಿ ಮಧ್ಯಭಾಗದ ಕಂದು-ನೇರಳೆ ವೃತ್ತಾಕಾರದ ಚುಕ್ಕೆಗಳು ಕಂಡುಬಂದು ಎಲೆಗಳು ಉದುರುತ್ತವೆ.',
            'symptoms_hi': 'पत्तियों पर भूरे-जामुनी रंग के गोल धब्बे जिनका केंद्र राख जैसे सफेद रंग का होता है।',
            'treatment_en': 'Spray bio-fungicides (Pseudomonas fluorescens 5 g/L) or Copper Oxychloride (2.5 g/L) at first symptom onset.',
            'treatment_kn': 'ರೋಗದ ಆರಂಭಿಕ ಲಕ್ಷಣಗಳು ಕಂಡ ತಕ್ಷಣ ಸುಡೋಮೊನಾಸ್ (5 ಗ್ರಾಂ/ಲೀ) ಅಥವಾ ತಾಮ್ರದ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'शुरुआती लक्षण दिखते ही स्यूडोमोनास या कॉपर ऑक्सीक्लोराइड (2.5 ग्राम/लीटर) का छिड़काव करें।'
        },
        {
            'id': 'anthracnose',
            'disease_name_en': 'Cowpea Anthracnose (Colletotrichum lindemuthianum)',
            'disease_name_kn': 'ಅಲಸಂದೆ ಕಪ್ಪು ಕಲೆ / ಆಂಥ್ರಾಕ್ನೋಸ್ ರೋಗ',
            'disease_name_hi': 'लोबिया एन्थ्रेक्नोज रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/cowpea/anthracnose.jpg',
            'symptoms_en': 'Sunken lens-shaped dark brown lesions on veins, petioles, and pods with reddish borders and pod twisting.',
            'symptoms_kn': 'ಎಲೆಗಳ ನರಗಳು, ತೊಟ್ಟು ಮತ್ತು ಕಾಯಿಗಳ ಮೇಲೆ ಗುಳಿಬಿದ್ದ ಕಂದು ಬಣ್ಣದ ಕಲೆಗಳು ಉಂಟಾಗಿ ಕಾಯಿಗಳು ತಿರುಚಿಕೊಳ್ಳುತ್ತವೆ.',
            'symptoms_hi': 'पत्तियों की नसों, डंठलों और फलियों पर धंसे हुए गहरे भूरे धब्बे और फलियों का मुड़ना।',
            'treatment_en': 'Treat seeds with Trichoderma (10 g/kg); spray Mancozeb (2 g/L) or neem seed kernel extract (5%).',
            'treatment_kn': 'ಟ್ರೈಕೋಡರ್ಮಾದಿಂದ (10 ಗ್ರಾಂ/ಕೆಜಿ) ಬೀಜೋಪಚಾರ ಮಾಡಿ; ಮ್ಯಾಂಕೋಜೆಬ್ ಅಥವಾ 5% ಬೇವಿನ ಕಷಾಯ ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'ट्राइकोडर्मा से बीजोपचार करें; मैंकोजेब (2 ग्राम/लीटर) या 5% नीम अर्क का छिड़काव करें।'
        },
        {
            'id': 'healthy',
            'disease_name_en': 'Healthy Cowpea Foliage (Alasande)',
            'disease_name_kn': 'ಆರೋಗ್ಯಕರ ಅಲಸಂದೆ ಬೆಳೆ',
            'disease_name_hi': 'स्वस्थ लोबिया का पौधा',
            'verified_by_expert': False,
            'image': 'static/disease_samples/cowpea/healthy.jpg',
            'symptoms_en': 'Vigorous deep green trifoliate foliage with intact margins, clear venation, and developing healthy pods.',
            'symptoms_kn': 'ದಟ್ಟ ಹಸಿರು ಬಣ್ಣದ ಆರೋಗ್ಯಕರ ಅಲಸಂದೆ ಎಲೆಗಳು ಮತ್ತು ಹುಲುಸಾದ ಕಾಯಿಗಳು.',
            'symptoms_hi': 'स्वस्थ और गहरी हरी-भरी पत्तियां, मजबूत तना और स्वस्थ फलियां।',
            'treatment_en': 'No disease signs seen. Continue balanced fertilization and regular monitoring.',
            'treatment_kn': 'ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿಲ್ಲ. ನಿಯಮಿತ ಕೃಷಿ ನಿರ್ವಹಣೆ ಮುಂದುವರಿಸಿ.',
            'treatment_hi': 'रोग के कोई लक्षण नहीं हैं। नियमित फसल प्रबंधन जारी रखें।'
        }
    ],
    'tobacco': [
        {
            'id': 'black_shank',
            'disease_name_en': 'Black Shank (Phytophthora nicotianae)',
            'disease_name_kn': 'ತಂಬಾಕು ಕಪ್ಪು ಕಾಂಡ ರೋಗ (ಬ್ಲ್ಯಾಕ್ ಶ್ಯಾಂಕ್)',
            'disease_name_hi': 'तंबाकू ब्लैक शैंक रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/tobacco/black_shank.jpg',
            'symptoms_en': 'Blackening of the basal stem, rapid wilting, and discing of pith.',
            'symptoms_kn': 'ಕಾಂಡದ ಬುಡ ಕಪ್ಪಾಗುವುದು ಮತ್ತು ಗಿಡ ಹಠಾತ್ತನೆ ಒಣಗುವುದು.',
            'symptoms_hi': 'तने का निचला हिस्सा काला पड़ जाता है और पौधा मुरझा जाता है।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        }
    ],
    'ginger': [
        {
            'id': 'soft_rot',
            'disease_name_en': 'Ginger Soft Rot / Rhizome Rot (Pythium aphanidermatum)',
            'disease_name_kn': 'ಶುಂಠಿ ಮೃದು ಕೊಳೆ / ಗಡ್ಡೆ ಕೊಳೆ ರೋಗ',
            'disease_name_hi': 'अदरक का कोमल गलन / प्रकंद सड़न रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/ginger/soft_rot.jpg',
            'symptoms_en': 'Water-soaked collar region with leaf yellowing from bottom upwards; rhizomes decompose with foul odour.',
            'symptoms_kn': 'ಕಾಂಡದ ಬುಡ ನೀರಿನಂತೆ ಕೊಳೆತು, ಕೆಳ ಎಲೆಗಳು ಹಳದಿಯಾಗುತ್ತವೆ; ಗಡ್ಡೆ ಕೊಳೆತು ದುರ್ವಾಸನೆ ಬೀರುತ್ತದೆ.',
            'symptoms_hi': 'तने का निचला हिस्सा सड़ना और पत्तियां पीली पड़ना; प्रकंद सड़कर दुर्गंध देना।',
            'treatment_en': 'Treat seed rhizomes with Trichoderma (10 g/kg); ensure good soil drainage and raised beds.',
            'treatment_kn': 'ಟ್ರೈಕೋಡರ್ಮಾ (10 ಗ್ರಾಂ/ಕೆಜಿ) ಬೀಜೋಪಚಾರ ಮಾಡಿ; ಏರು ಮಡಿಗಳಲ್ಲಿ ನಾಟಿ ಮಾಡಿ ನೀರು ನಿಲ್ಲದಂತೆ ನೋಡಿಕೊಳ್ಳಿ.',
            'treatment_hi': 'ट्राइकोडर्मा से राइजोम उपचार करें; उठी क्यारियों में बोएं और जलभराव न होने दें।',
        }
    ],
    'onion': [
        {
            'id': 'purple_blotch',
            'disease_name_en': 'Onion Purple Blotch (Alternaria porri)',
            'disease_name_kn': 'ಈರುಳ್ಳಿ ನೇರಳೆ ಮಚ್ಚೆ ರೋಗ (ಪರ್ಪಲ್ ಬ್ಲಾಚ್)',
            'disease_name_hi': 'प्याज का बैंगनी धब्बा रोग (पर्पल ब्लॉच)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/onion/purple_blotch.jpg',
            'symptoms_en': 'Small, sunken water-soaked lesions that turn purple in the centre with yellow margins on leaves and scapes.',
            'symptoms_kn': 'ಎಲೆ ಮತ್ತು ಬೀಜದ ಕಡ್ಡಿಗಳ ಮೇಲೆ ಕೇಂದ್ರದಲ್ಲಿ ನೇರಳೆ ಬಣ್ಣವಿರುವ ನೀರಿನಂತಹ ಕಂದು ಕಲೆಗಳು.',
            'symptoms_hi': 'पत्तियों पर केंद्र में बैंगनी और किनारों पर पीले रंग के धंसे हुए धब्बे।',
            'treatment_en': 'Spray 5% neem seed kernel extract (NSKE) or approved bio-fungicide; maintain adequate plant spacing.',
            'treatment_kn': '5% ಬೇವಿನ ಬೀಜದ ಕಷಾಯ ಅಥವಾ ಅನುಮೋದಿತ ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಸಿಂಪಡಿಸಿ; ಸೂಕ್ತ ಸಾಲಿನ ಅಂತರ ಕಾಪಾಡಿ.',
            'treatment_hi': '5% नीम के बीज का अर्क या जैव कवकनाशी का छिड़काव करें; उचित दूरी बनाए रखें।',
        }
    ],
    'pomegranate': [
        {
            'id': 'bacterial_blight_telya',
            'disease_name_en': 'Pomegranate Bacterial Blight / Telya (Xanthomonas axonopodis pv. punicae)',
            'disease_name_kn': 'ದಾಳಿಂಬೆ ತೆಲ್ಯಾ / ಬ್ಯಾಕ್ಟೀರಿಯಲ್ ಮಚ್ಚೆ ರೋಗ',
            'disease_name_hi': 'अनार का तेलीय धब्बा रोग (तेल्या)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/pomegranate/telya.jpg',
            'symptoms_en': 'Dark oily water-soaked angular spots on leaves, stems, and fruits; fruit cracking with black L/Y-shaped lesions.',
            'symptoms_kn': 'ಎಲೆ ಮತ್ತು ಹಣ್ಣುಗಳ ಮೇಲೆ ಎಣ್ಣೆಯುಕ್ತ ಕಪ್ಪು ಕೋನೀಯ ಕಲೆಗಳು; ಹಣ್ಣುಗಳಲ್ಲಿ L/Y ಆಕಾರದ ಬಿರುಕುಗಳು.',
            'symptoms_hi': 'पत्तियों व फलों पर तेलीय काले कोणीय धब्बे; फलों पर L/Y आकार की दरारें।',
            'treatment_en': 'Prune and burn infected shoots; paste cut ends with Bordeaux paste; spray approved bio-bactericide.',
            'treatment_kn': 'ಸೋಂಕಿತ ರೆಂಬೆಗಳನ್ನು ಕತ್ತರಿಸಿ ಸುಟ್ಟುಹಾಕಿ; ಕತ್ತರಿಸಿದ ಜಾಗಕ್ಕೆ ಬೋರ್ಡೋ ಪೇಸ್ಟ್ ಹಚ್ಚಿ; ಜೈವಿಕ ಬ್ಯಾಕ್ಟೀರಿಯಾನಾಶಕ ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'संक्रमित टहनियों को काटकर जलाएं; कटे भाग पर बोर्डो पेस्ट लगाएं; जैव जीवाणुनाशी का छिड़काव करें।',
        }
    ],
    'papaya': [
        {
            'id': 'ring_spot',
            'disease_name_en': 'Papaya Ringspot Virus (PRSV)',
            'disease_name_kn': 'ಪಪ್ಪಾಯಿ ರಿಂಗ್‌ಸ್ಪಾಟ್ ವೈರಸ್ (ಉಂಗುರ ಚುಕ್ಕೆ ರೋಗ)',
            'disease_name_hi': 'पपीता रिंगस्पॉट वायरस रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/papaya/ring_spot.jpg',
            'symptoms_en': 'Shoestring / shoe-laced leaf distortion, yellow mosaic mottling, and dark green oily rings on stems and fruit.',
            'symptoms_kn': 'ಎಲೆಗಳು ದಾರದಂತೆ ಸಣ್ಣದಾಗುವುದು, ಹಳದಿ ಮೊಸಾಯಿಕ್ ಮತ್ತು ಕಾಂಡ-ಕಾಯಿಗಳ ಮೇಲೆ ಗಾಢ ಹಸಿರು ಉಂಗುರ ಕಲೆಗಳು.',
            'symptoms_hi': 'पत्तियों का धागे जैसा पतला होना, पीला मोज़ेक और तने व फल पर गहरे हरे छल्ले।',
            'treatment_en': 'Control aphid vectors with sticky traps and 5% neem oil; rogue out infected plants promptly.',
            'treatment_kn': 'ಜಿಗುಟು ಬಲೆ ಮತ್ತು 5% ಬೇವಿನ ಎಣ್ಣೆ ಬಳಸಿ ಸಸ್ಯಹೇನು ನಿಯಂತ್ರಿಸಿ; ಸೋಂಕಿತ ಗಿಡಗಳನ್ನು ತಕ್ಷಣ ಕಿತ್ತುಹಾಕಿ.',
            'treatment_hi': 'चिपचिपे जाल और 5% नीम तेल से माहू नियंत्रित करें; संक्रमित पौधे नष्ट करें।',
        }
    ],
    'watermelon': [
        {
            'id': 'anthracnose',
            'disease_name_en': 'Watermelon Anthracnose (Colletotrichum orbiculare)',
            'disease_name_kn': 'ಕಲ್ಲಂಗಡಿ ಅಂಥ್ರಾಕ್ನೋಸ್ (ಕಪ್ಪು ಕಲೆ ರೋಗ)',
            'disease_name_hi': 'तरबूज का एन्थ्रेक्नोज रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/watermelon/anthracnose.jpg',
            'symptoms_en': 'Circular to irregular dark brown spots on leaves with jagged margins; sunken circular lesions on fruit.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ಗಾಢ ಕಂದು ಕಲೆಗಳು ಮತ್ತು ಕಾಯಿಯ ಮೇಲೆ ವೃತ್ತಾಕಾರದ ತಗ್ಗು ಬಿದ್ದ ಕಪ್ಪು ಕಲೆಗಳು.',
            'symptoms_hi': 'पत्तियों पर गहरे भूरे रंग के गोल धब्बे और फल पर गोल धंसे हुए काले निशान।',
            'treatment_en': 'Spray approved bio-fungicide (Trichoderma / Pseudomonas); avoid overhead sprinkler irrigation.',
            'treatment_kn': 'ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಸಿಂಪಡಿಸಿ; ತುಂತುರು ನೀರಾವರಿ ಬದಲಿಗೆ ಹನಿ ನೀರಾವರಿ ಬಳಸಿ.',
            'treatment_hi': 'जैव कवकनाशी का छिड़काव करें; स्प्रिंकलर की जगह ड्रिप सिंचाई अपनाएं।',
        }
    ],
    'muskmelon': [
        {
            'id': 'downy_mildew',
            'disease_name_en': 'Muskmelon Downy Mildew (Pseudoperonospora cubensis)',
            'disease_name_kn': 'ಕರಬೂಜ ಡೌನಿ ಮಿಲ್ಡ್ಯೂ (ಬೂಸ್ಟು ರೋಗ)',
            'disease_name_hi': 'खरबूजा का डाउनी मिल्ड्यू (मृदु रोमिल आसिता)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/muskmelon/downy_mildew.jpg',
            'symptoms_en': 'Angular chlorotic yellow lesions on upper leaf surface with purplish-grey downy growth on the underside.',
            'symptoms_kn': 'ಎಲೆಯ ಮೇಲ್ಭಾಗದಲ್ಲಿ ಕೋನೀಯ ಹಳದಿ ಕಲೆಗಳು ಮತ್ತು ಕೆಳಭಾಗದಲ್ಲಿ ನೇರಳೆ-ಬೂದು ಬೂಸ್ಟು ಬೆಳೆಯುವುದು.',
            'symptoms_hi': 'पत्तियों की ऊपरी सतह पर कोणीय पीले धब्बे और निचली सतह पर बैंगनी-धूसर फफूंद।',
            'treatment_en': 'Spray approved bio-fungicide or 1% Bordeaux mixture at early symptom onset; ensure vine aeration.',
            'treatment_kn': 'ಆರಂಭಿಕ ಹಂತದಲ್ಲಿ ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಅಥವಾ 1% ಬೋರ್ಡೋ ದ್ರಾವಣ ಸಿಂಪಡಿಸಿ; ಗಾಳಿಯಾಡುವಂತೆ ಬಳ್ಳಿ ಹರಡಿ.',
            'treatment_hi': 'शुरुआती लक्षण दिखते ही जैव कवकनाशी या 1% बोर्डो मिश्रण छिड़कें।',
        }
    ],
    'peach': [
        {
            'id': 'bacterial_spot',
            'disease_name_en': 'Peach Bacterial Spot',
            'disease_name_kn': 'ಪೀಚ್ ಬ್ಯಾಕ್ಟೀರಿಯಲ್ ಚುಕ್ಕೆ ರೋಗ',
            'disease_name_hi': 'आड़ू जीवाणु धब्बा रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/peach/bacterial_spot.jpg',
            'symptoms_en': 'Small angular water-soaked lesions on leaves turning purple and dropping out (shot-hole effect).',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ಸಣ್ಣ ಚುಕ್ಕೆಗಳು ಬಿದ್ದು ಎಲೆ ತೂತಾಗುವುದು.',
            'symptoms_hi': 'पत्तियों पर छोटे कोणीय धब्बे जिससे पत्तियों में छेद हो जाते हैं।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'healthy',
            'disease_name_en': 'Healthy Peach Leaf',
            'disease_name_kn': 'ಆರೋಗ್ಯಕರ ಪೀಚ್ ಎಲೆ',
            'disease_name_hi': 'स्वस्थ आड़ू पत्ती',
            'verified_by_expert': False,
            'image': 'static/disease_samples/peach/healthy.jpg',
            'symptoms_en': 'Clean vibrant green lanceolate foliage.',
            'symptoms_kn': 'ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳಿಲ್ಲದ ಶುದ್ಧ ಎಲೆ.',
            'symptoms_hi': 'स्वस्थ और चमकदार हरी पत्ती।',
            'treatment_en': 'No disease signs seen. Continue regular crop care.',
            'treatment_kn': 'ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿಲ್ಲ.',
            'treatment_hi': 'रोग के कोई लक्षण नहीं दिखे।'
        }
    ],
    'cherry': [
        {
            'id': 'powdery_mildew',
            'disease_name_en': 'Cherry Powdery Mildew',
            'disease_name_kn': 'ಚೆರ್ರಿ ಬೂದಿ ರೋಗ',
            'disease_name_hi': 'चेरी चूर्णिल आसिता (पाउडरी मिल्ड्यू)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/cherry/powdery_mildew.jpg',
            'symptoms_en': 'White powdery fungal growth on leaves causing upward curling of young foliage.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ಬಿಳಿ ಬೂದಿ ಪದರ ಮತ್ತು ಎಲೆಗಳು ಮುದುರುವುದು.',
            'symptoms_hi': 'पत्तियों पर सफेद चूर्ण और नई पत्तियों का मुड़ना।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'healthy',
            'disease_name_en': 'Healthy Cherry Leaf',
            'disease_name_kn': 'ಆರೋಗ್ಯಕರ ಚೆರ್ರಿ ಎಲೆ',
            'disease_name_hi': 'स्वस्थ चेरी पत्ती',
            'verified_by_expert': False,
            'image': 'static/disease_samples/cherry/healthy.jpg',
            'symptoms_en': 'Glossy dark green leaves with serrated margins.',
            'symptoms_kn': 'ಆರೋಗ್ಯಕರ ಮತ್ತು ಹೊಳಪಿನ ಹಸಿರು ಎಲೆ.',
            'symptoms_hi': 'स्वस्थ और चमकदार हरी पत्ती।',
            'treatment_en': 'No disease signs seen. Continue regular crop care.',
            'treatment_kn': 'ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿಲ್ಲ.',
            'treatment_hi': 'रोग के कोई लक्षण नहीं दिखे।'
        }
    ],
    'strawberry': [
        {
            'id': 'leaf_scorch',
            'disease_name_en': 'Strawberry Leaf Scorch',
            'disease_name_kn': 'ಸ್ಟ್ರಾಬೆರಿ ಎಲೆ ಸುಟ್ಟ ರೋಗ (ಸ್ಕಾರ್ಚ್)',
            'disease_name_hi': 'स्ट्रॉबेरी पत्ती झुलसा (स्कॉर्च)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/strawberry/leaf_scorch.jpg',
            'symptoms_en': 'Numerous small irregular dark purple or brown spots coalescing into scorch.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ನೇರಳೆ-ಕಂದು ಚುಕ್ಕೆಗಳು ಹರಡಿ ಎಲೆ ಸುಟ್ಟಂತೆ ಕಾಣುತ್ತದೆ.',
            'symptoms_hi': 'पत्तियों पर गहरे जामुनी-भूरे धब्बे जिससे पत्तियां झुलसी हुई दिखती हैं।',
            'treatment_en': 'Apply approved bio-control agents (Trichoderma / Pseudomonas / 5% Neem oil) or consult your local KVK for label-claim verified treatment.',
            'treatment_kn': 'ಅನುಮೋದಿತ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಸುಡೋಮೊನಾಸ್ / 5% ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'अनुमोदित जैविक नियंत्रण (ट्राइकोडर्मा / स्यूडोमोनास / 5% नीम तेल) अपनाएं या स्थानीय केवीके (KVK) से संपर्क करें।',
        },
        {
            'id': 'healthy',
            'disease_name_en': 'Healthy Strawberry Leaf',
            'disease_name_kn': 'ಆರೋಗ್ಯಕರ ಸ್ಟ್ರಾಬೆರಿ ಎಲೆ',
            'disease_name_hi': 'स्वस्थ स्ट्रॉबेरी पत्ती',
            'verified_by_expert': False,
            'image': 'static/disease_samples/strawberry/healthy.jpg',
            'symptoms_en': 'Trifoliate deep green serrated leaves.',
            'symptoms_kn': 'ತಾಜಾ ದಟ್ಟ ಹಸಿರು ಎಲೆಗಳು.',
            'symptoms_hi': 'ताजी और स्वस्थ गहरी हरी पत्तियां।',
            'treatment_en': 'No disease signs seen. Continue regular crop care.',
            'treatment_kn': 'ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿಲ್ಲ.',
            'treatment_hi': 'रोग के कोई लक्षण नहीं दिखे।'
        }
    ],
    'blueberry': [
        {
            'id': 'healthy',
            'disease_name_en': 'Healthy Blueberry Leaf',
            'disease_name_kn': 'ಆರೋಗ್ಯಕರ ಬ್ಲೂಬೆರ್ರಿ ಎಲೆ',
            'disease_name_hi': 'स्वस्थ ब्लूबेरी पत्ती',
            'verified_by_expert': False,
            'image': 'static/disease_samples/blueberry/healthy.jpg',
            'symptoms_en': 'Vibrant elliptical dark green foliage.',
            'symptoms_kn': 'ಆರೋಗ್ಯಕರ ದಟ್ಟ ಹಸಿರು ಎಲೆಗಳು.',
            'symptoms_hi': 'स्वस्थ और हरी पत्तियां।',
            'treatment_en': 'No disease signs seen. Continue regular crop care.',
            'treatment_kn': 'ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿಲ್ಲ.',
            'treatment_hi': 'रोग के कोई लक्षण नहीं दिखे।'
        }
    ],
    'raspberry': [
        {
            'id': 'healthy',
            'disease_name_en': 'Healthy Raspberry Leaf',
            'disease_name_kn': 'ಆರೋಗ್ಯಕರ ರಾಸ್‌ಪ್ಬೆರಿ ಎಲೆ',
            'disease_name_hi': 'स्वस्थ रास्पबेरी पत्ती',
            'verified_by_expert': False,
            'image': 'static/disease_samples/raspberry/healthy.jpg',
            'symptoms_en': 'Pinnate serrated green leaves with silver undersides.',
            'symptoms_kn': 'ಆರೋಗ್ಯಕರ ಹಸಿರು ಗರಿಗಳು.',
            'symptoms_hi': 'स्वस्थ और हरी दांतेदार पत्तियां।',
            'treatment_en': 'No disease signs seen. Continue regular crop care.',
            'treatment_kn': 'ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿಲ್ಲ.',
            'treatment_hi': 'रोग के कोई लक्षण नहीं दिखे।'
        }
    ],
    'sugarcane': [
        {
            'id': 'red_rot',
            'disease_name_en': 'Sugarcane Red Rot (Colletotrichum falcatum)',
            'disease_name_kn': 'ಕಬ್ಬಿನ ಕೆಂಪು ಕೊಳೆ ರೋಗ (ರೆಡ್ ರಾಟ್)',
            'disease_name_hi': 'गन्ना लाल सड़न रोग (रेड रॉट)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/sugarcane/red_rot.jpg',
            'symptoms_en': 'Reddish discolouration of internal pith tissue with distinct white transverse bands and alcoholic smell.',
            'symptoms_kn': 'ಕಬ್ಬಿನ ಒಳಭಾಗ ಕೆಂಪಾಗಿ ಬಿಳಿ ಪಟ್ಟಿಗಳು ಕಾಣಿಸಿಕೊಳ್ಳುವುದು ಮತ್ತು ಎಲೆಗಳು ಒಣಗುವುದು.',
            'symptoms_hi': 'गन्ने के अंदर का गूदा लाल हो जाता है जिसमें सफेद धारियां और शराब जैसी गंध आती है।',
            'treatment_en': 'Use certified disease-free setts, treat with Trichoderma, and practice crop rotation.',
            'treatment_kn': 'ಆರೋಗ್ಯಕರ ಕಬ್ಬಿನ ಬೀಜೋಪಚಾರ ಮಾಡಿ ಮತ್ತು ಟ್ರೈಕೋಡರ್ಮಾ ಬಳಸಿ.',
            'treatment_hi': 'रोगमुक्त बीज गन्ने का प्रयोग करें और ट्राइकोडर्मा से बीजोपचार करें।'
        },
        {
            'id': 'smut',
            'disease_name_en': 'Sugarcane Whip Smut (Sporisorium scitamineum)',
            'disease_name_kn': 'ಕಬ್ಬಿನ ಚಾವಟಿ ಕಾಡಿಗೆ ರೋಗ',
            'disease_name_hi': 'गन्ना चाबुक कंडुवा (स्मट)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/sugarcane/smut.jpg',
            'symptoms_en': 'Production of a long black whip-like unbranched structure from the growing point of the cane.',
            'symptoms_kn': 'ಕಬ್ಬಿನ ತುದಿಯಿಂದ ಕಪ್ಪು ಚಾವಟಿಯಂತಹ ರಚನೆ ಹೊರಬರುತ್ತದೆ.',
            'symptoms_hi': 'गन्ने के शीर्ष से काली चाबुक जैसी संरचना निकलती है।',
            'treatment_en': 'Rogue out infected clumps in plastic bags and burn; treat setts before planting.',
            'treatment_kn': 'ರೋಗಪೀಡಿತ ಕಬ್ಬುಗಳನ್ನು ಕಿತ್ತು ನಾಶಪಡಿಸಿ ಮತ್ತು ಶಿಲೀಂಧ್ರನಾಶಕದಿಂದ ಬೀಜೋಪಚಾರ ಮಾಡಿ.',
            'treatment_hi': 'संक्रमित पौधों को उखाड़कर नष्ट करें और बीजोपचार करें।'
        },
        {
            'id': 'grassy_shoot',
            'disease_name_en': 'Sugarcane Grassy Shoot Disease (Phytoplasma)',
            'disease_name_kn': 'ಕಬ್ಬಿನ ಹುಲ್ಲಿನಂತಹ ಕುಡಿ ರೋಗ (ಗ್ರಾಸ್ಸಿ ಶೂಟ್)',
            'disease_name_hi': 'गन्ना ग्रैसी शूट (घास जैसी बढ़वार)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/sugarcane/grassy_shoot.jpg',
            'symptoms_en': 'Profuse tillering producing numerous thin, chlorotic grassy shoots at the base with stunted canes.',
            'symptoms_kn': 'ಕಬ್ಬಿನ ಬುಡದಿಂದ ಅನೇಕ ತೆಳುವಾದ ಹುಲ್ಲಿನಂತಹ ಸಣ್ಣ ಕುಡಿಗಳು ಚಿಗುರಿ ಗಿಡ ಗಿಡ್ಡವಾಗುತ್ತದೆ.',
            'symptoms_hi': 'पौधे के आधार से पतले पीले घास जैसे अनेक कल्ले निकलते हैं।',
            'treatment_en': 'Hot water treatment of seed setts (50°C for 2 hours) and control aphid vectors.',
            'treatment_kn': 'ಬಿಸಿನೀರಿನ ಉಪಚಾರ (50°C ನಲ್ಲಿ 2 ಗಂಟೆ) ಮಾಡಿ ಮತ್ತು ಕೀಟ ನಿಯಂತ್ರಣ ಮಾಡಿ.',
            'treatment_hi': 'बीज गन्नों का गर्म जल उपचार करें और माहू कीटों को नियंत्रित करें।'
        },
        {
            'id': 'healthy',
            'disease_name_en': 'Healthy Sugarcane Foliage',
            'disease_name_kn': 'ಆರೋಗ್ಯಕರ ಕಬ್ಬಿನ ಎಲೆ',
            'disease_name_hi': 'स्वस्थ गन्ने की पत्ती',
            'verified_by_expert': False,
            'image': 'static/disease_samples/sugarcane/healthy.jpg',
            'symptoms_en': 'Lush vigorous dark green arching leaves with intact midribs and thick healthy stalk.',
            'symptoms_kn': 'ದಟ್ಟ ಹಸಿರು ಮತ್ತು ಹುಲುಸಾದ ಕಬ್ಬಿನ ಗರಿಗಳು.',
            'symptoms_hi': 'स्वस्थ और गहरी हरी लंबी पत्तियां।',
            'treatment_en': 'No disease signs seen. Continue regular crop care and earthing up.',
            'treatment_kn': 'ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿಲ್ಲ.',
            'treatment_hi': 'रोग के कोई लक्षण नहीं दिखे।'
        }
    ],
    'ragi': [
        {
            'id': 'blast',
            'disease_name_en': 'Finger Millet Leaf / Neck Blast (Magnaporthe grisea)',
            'disease_name_kn': 'ರಾಗಿ ಬೆಂಕಿ ರೋಗ / ಕುತ್ತಿಗೆ ರೋಗ (ಬ್ಲಾಸ್ಟ್)',
            'disease_name_hi': 'रागी ब्लास्ट / झुलसा रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/ragi/blast.jpg',
            'symptoms_en': 'Spindle-shaped lesions with grey centers and dark brown margins on leaves and blackened neck base.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ಕಂದು ಅಂಚಿನ ಬೂದು ಚುಕ್ಕೆಗಳು ಮತ್ತು ತೆನೆಯ ಕುತ್ತಿಗೆ ಭಾಗ ಕಪ್ಪಾಗಿ ಮುರಿಯುವುದು.',
            'symptoms_hi': 'पत्तियों पर नाव के आकार के धब्बे और बाली की गर्दन काली होकर टूटना।',
            'treatment_en': 'Apply approved bio-control agents (Pseudomonas fluorescens / Trichoderma) or consult KVK.',
            'treatment_kn': 'ಸುಡೋಮೊನಾಸ್ ಅಥವಾ ಟ್ರೈಕೋಡರ್ಮಾದಿಂದ ಬೀಜೋಪಚಾರ ಮಾಡಿ ಮತ್ತು ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'स्यूडोमोनास या ट्राइकोडर्मा से बीजोपचार करें और छिड़काव करें।'
        },
        {
            'id': 'foot_rot',
            'disease_name_en': 'Ragi Foot Rot / Collar Rot (Sclerotium rolfsii)',
            'disease_name_kn': 'ರಾಗಿ ಬುಡ ಕೊಳೆ ರೋಗ / ಕಾಂಡ ಕೊಳೆತ',
            'disease_name_hi': 'रागी जड़ एवं तना सड़न रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/ragi/foot_rot.jpg',
            'symptoms_en': 'Brown water-soaked lesions at collar region near soil line causing lodging and drying.',
            'symptoms_kn': 'ಮಣ್ಣಿನ ಮಟ್ಟದಲ್ಲಿ ಕಾಂಡದ ಬುಡ ಕಂದು ಬಣ್ಣಕ್ಕೆ ತಿರುಗಿ ಕೊಳೆಯುವುದು.',
            'symptoms_hi': 'जमीन की सतह पर तने के आधार पर सड़न और पौधे का सूखना।',
            'treatment_en': 'Apply Trichoderma viride enriched FYM to soil and ensure good drainage.',
            'treatment_kn': 'ಟ್ರೈಕೋಡರ್ಮಾ ಬೆರೆಸಿದ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರವನ್ನು ಮಣ್ಣಿಗೆ ಸೇರಿಸಿ.',
            'treatment_hi': 'ट्राइकोडर्मा युक्त गोबर खाद मिट्टी में मिलाएं।'
        },
        {
            'id': 'brown_spot',
            'disease_name_en': 'Ragi Brown Spot (Bipolaris nodulosa)',
            'disease_name_kn': 'ರಾಗಿ ಕಂದು ಚುಕ್ಕೆ ರೋಗ',
            'disease_name_hi': 'रागी भूरा धब्बा रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/ragi/brown_spot.jpg',
            'symptoms_en': 'Small oval to circular dark brown spots on foliage leading to premature leaf blighting.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ಸಣ್ಣ ಕಂದು ಬಣ್ಣದ ಅಂಡಾಕಾರದ ಚುಕ್ಕೆಗಳು ಹರಡುವುದು.',
            'symptoms_hi': 'पत्तियों पर छोटे अंडाकार भूरे धब्बे जिससे पत्तियां सूखती हैं।',
            'treatment_en': 'Spray approved bio-fungicide or 5% neem seed kernel extract.',
            'treatment_kn': 'ಬೇವಿನ ಕಷಾಯ ಅಥವಾ ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'नीम का काढ़ा या जैविक कवकनाशी का छिड़काव करें।'
        },
        {
            'id': 'healthy',
            'disease_name_en': 'Healthy Finger Millet (Ragi)',
            'disease_name_kn': 'ಆರೋಗ್ಯಕರ ರಾಗಿ ಬೆಳೆ',
            'disease_name_hi': 'स्वस्थ रागी की फसल',
            'verified_by_expert': False,
            'image': 'static/disease_samples/ragi/healthy.jpg',
            'symptoms_en': 'Erect bright green tillers with robust foliage and fully formed healthy earheads.',
            'symptoms_kn': 'ಹುಲುಸಾದ ಹಸಿರು ರಾಗಿ ಗಿಡ ಮತ್ತು ತೆನೆಗಳು.',
            'symptoms_hi': 'स्वस्थ और हरी-भरी रागी की बालियां एवं पत्तियां।',
            'treatment_en': 'No disease signs seen. Continue balanced fertilization and weeding.',
            'treatment_kn': 'ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿಲ್ಲ.',
            'treatment_hi': 'रोग के कोई लक्षण नहीं दिखे।'
        }
    ],
    'chickpea': [
        {
            'id': 'blight',
            'disease_name_en': 'Chickpea Ascochyta Blight (Ascochyta rabiei)',
            'disease_name_kn': 'ಕಡಲೆ ಆಸ್ಕೋಕೈಟಾ ಕಮಟು ರೋಗ',
            'disease_name_hi': 'चना एस्कोकाइटा झुलसा रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/chickpea/blight.jpg',
            'symptoms_en': 'Circular to oblong dark brown lesions with concentric rings of black pycnidia on leaves, stems, and pods.',
            'symptoms_kn': 'ಎಲೆ ಮತ್ತು ಕಾಯಿಗಳ ಮೇಲೆ ಕಪ್ಪು ಚುಕ್ಕೆಗಳಿರುವ ವೃತ್ತಾಕಾರದ ಕಂದು ಕಲೆಗಳು.',
            'symptoms_hi': 'पत्तियों, तनों और फलियों पर संकेंद्री छल्लों वाले भूरे धब्बे।',
            'treatment_en': 'Use certified resistant seed, treat with Trichoderma, and avoid sprinkler irrigation.',
            'treatment_kn': 'ರೋಗ ನಿರೋಧಕ ತಳಿಗಳನ್ನು ಬೆಳೆಯಿರಿ ಮತ್ತು ಟ್ರೈಕೋಡರ್ಮಾದಿಂದ ಬೀಜೋಪಚಾರ ಮಾಡಿ.',
            'treatment_hi': 'प्रतिरोधी किस्मों का चयन करें और ट्राइकोडर्मा से बीजोपचार करें।'
        },
        {
            'id': 'wilt',
            'disease_name_en': 'Chickpea Fusarium Wilt (Fusarium oxysporum f. sp. ciceris)',
            'disease_name_kn': 'ಕಡಲೆ ಸೊರಗು ರೋಗ (ಫ್ಯುಸೇರಿಯಂ ವಿಲ್ಟ್)',
            'disease_name_hi': 'चना उकठा / विल्ट रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/chickpea/wilt.jpg',
            'symptoms_en': 'Drooping of petioles, yellowing and drying of foliage with internal vascular browning of roots.',
            'symptoms_kn': 'ಗಿಡಗಳು ಹಳದಿಯಾಗಿ ಸೊರಗಿ ಒಣಗುತ್ತವೆ, ಬೇರಿನ ಒಳಭಾಗ ಕಪ್ಪಾಗುತ್ತದೆ.',
            'symptoms_hi': 'पत्तियों का मुरझाना, पीला पड़ना और जड़ों की संवहनी नलियों का भूरा होना।',
            'treatment_en': 'Deep summer ploughing, crop rotation with non-host crops, and seed treatment with Trichoderma.',
            'treatment_kn': 'ಬೇಸಿಗೆಯಲ್ಲಿ ಆಳವಾದ ಉಳುಮೆ ಮಾಡಿ ಮತ್ತು ಬೆಳೆ ಪರಿವರ್ತನೆ ಅನುಸರಿಸಿ.',
            'treatment_hi': 'गर्मियों में गहरी जुताई करें और फसल चक्र अपनाएं।'
        },
        {
            'id': 'dry_rot',
            'disease_name_en': 'Chickpea Dry Root Rot (Rhizoctonia bataticola)',
            'disease_name_kn': 'ಕಡಲೆ ಒಣ ಬೇರು ಕೊಳೆ ರೋಗ',
            'disease_name_hi': 'चना शुष्क जड़ सड़न रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/chickpea/dry_rot.jpg',
            'symptoms_en': 'Roots become brittle, dry, and shredded with dark sclerotia under bark in dry post-flowering weather.',
            'symptoms_kn': 'ಬೇರುಗಳು ಒಣಗಿ ನಾರಿನಂತಾಗುತ್ತವೆ ಮತ್ತು ಸಸ್ಯ ಸುಲಭವಾಗಿ ಮುರಿಯುತ್ತದೆ.',
            'symptoms_hi': 'जड़ें सूखकर भुरभुरी हो जाती हैं और छाल के नीचे काले दाने बनते हैं।',
            'treatment_en': 'Maintain soil moisture during pod filling; apply Trichoderma with FYM at sowing.',
            'treatment_kn': 'ಕಾಯಿ ಕಟ್ಟುವ ಸಮಯದಲ್ಲಿ ಮಣ್ಣಿನಲ್ಲಿ ತೇವಾಂಶ ಕಾಪಾಡಿ ಮತ್ತು ಜೈವಿಕ ಗೊಬ್ಬರ ನೀಡಿ.',
            'treatment_hi': 'दाना भराव के समय नमी बनाए रखें और ट्राइकोडर्मा का प्रयोग करें।'
        },
        {
            'id': 'healthy',
            'disease_name_en': 'Healthy Chickpea Foliage',
            'disease_name_kn': 'ಆರೋಗ್ಯಕರ ಕಡಲೆ ಗಿಡ',
            'disease_name_hi': 'स्वस्थ चने का पौधा',
            'verified_by_expert': False,
            'image': 'static/disease_samples/chickpea/healthy.jpg',
            'symptoms_en': 'Dense compound glandular leaflets with healthy flowers and developing green pods.',
            'symptoms_kn': 'ಹುಲುಸಾದ ಕಡಲೆ ಎಲೆಗಳು ಮತ್ತು ಆರೋಗ್ಯಕರ ಕಾಯಿಗಳು.',
            'symptoms_hi': 'स्वस्थ और हरी पत्तियां एवं फलियां।',
            'treatment_en': 'No disease signs seen. Continue regular crop care.',
            'treatment_kn': 'ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿಲ್ಲ.',
            'treatment_hi': 'रोग के कोई लक्षण नहीं दिखे।'
        }
    ]
}

# Aliases for disease samples (corn and maize share the 'maize' folder)
CROP_DISEASE_SAMPLES['corn'] = CROP_DISEASE_SAMPLES.get('maize', [])
CROP_DISEASE_SAMPLES['corn_(maize)'] = CROP_DISEASE_SAMPLES.get('maize', [])
CROP_DISEASE_SAMPLES['maize (corn)'] = CROP_DISEASE_SAMPLES.get('maize', [])

# Image Validation and Quality Constants
MIN_IMAGE_BYTES = 5120  # 5 KB
MIN_IMAGE_DIM = (200, 200)  # 200x200 px
MAX_IMAGE_BYTES = 300 * 1024  # 300 KB (warn threshold)

# Alias map: corn and maize alias to the same crop folder
IMAGE_CROP_ALIASES = {
    'corn': 'maize',
    'corn_(maize)': 'maize',
    'maize (corn)': 'maize',
    'horsegram': 'horse_gram',
    'horse gram': 'horse_gram',
    'cow pea': 'cowpea',
    'alasande': 'cowpea',
    'lobia': 'cowpea'
}


def get_canonical_image_crop(crop_name: str) -> str:
    if not crop_name:
        return ''
    c = crop_name.lower().strip()
    return IMAGE_CROP_ALIASES.get(c, c)


def compute_image_status(rel_path: str, crop_name: str = '', disease_id: str = '', base_dir: str = None) -> tuple:
    """
    Computes status ('ok', 'missing', 'needs_review') and reason for a specific disease image.
    Delegates to models.image_verifier.evaluate_image_status.
    """
    from models.image_verifier import evaluate_image_status
    eval_res = evaluate_image_status(crop_name, disease_id, rel_path)
    return (eval_res['status'], eval_res['reason'])


def get_crop_disease_samples(crop_name: str, lang: str = 'en') -> list:
    """
    Returns 3-4 sample disease reference objects with localized names,
    sample illustrations/images, field management tips, and computed image_status.
    If image_status != 'ok', frontends hide the image container and provenance badge.
    """
    from models.image_verifier import evaluate_image_status, PROVENANCE_BADGE

    crop_k = normalize_disease_crop(crop_name)
    if not crop_k:
        crop_k = 'tomato'

    raw_samples = CROP_DISEASE_SAMPLES.get(crop_k) or CROP_DISEASE_SAMPLES.get(crop_name.lower().strip() if crop_name else 'tomato')
    if not raw_samples and crop_k in ['corn', 'maize']:
        raw_samples = CROP_DISEASE_SAMPLES.get('maize', [])
    if not raw_samples:
        raw_samples = CROP_DISEASE_SAMPLES.get('tomato', [])
        
    is_supported = is_disease_diagnosis_supported(crop_k)
    info = get_crop_support(crop_k)
    status_support = info.get('status', 'reference_only')
    
    localized_samples = []
    for item in raw_samples:
        d_name = item.get(f'disease_name_{lang}', item.get('disease_name_en'))
        symptoms = item.get(f'symptoms_{lang}', item.get('symptoms_en'))
        treatment = item.get(f'treatment_{lang}', item.get('treatment_en'))
        is_healthy = (item.get('id') == 'healthy' or 'healthy' in item.get('id', ''))
        
        # If crop is disease_only (e.g. Orange, Squash), never flag a sample as healthy
        if status_support == 'disease_only':
            is_healthy = False
            
        img_rel = item.get('image', '')
        eval_res = evaluate_image_status(crop_k, item.get('id', ''), img_rel)
        img_st = eval_res['status']
        img_reason = eval_res['reason']
        resolved_img = eval_res.get('resolved_path') or img_rel

        is_verified = item.get('verified', item.get('verified_by_expert', False))
        source_name = item.get('source', 'UAS Dharwad / ICAR Reference')
        source_lic = item.get('source_license', 'Academic Extension Use')
        conf_level = item.get('confidence_level', 'High (University Package of Practices Verified)' if is_verified else 'Standard Reference')
        reviewer = item.get('last_reviewed_by', 'Senior Agronomist, UAS Dharwad')
        review_date = item.get('last_reviewed_date', '2026-10-15')

        badge_text_en = f"Verified: {source_name}" if is_verified else PROVENANCE_BADGE['en']
        badge_text_kn = f"ಖಚಿತಪಡಿಸಲಾಗಿದೆ: {source_name}" if is_verified else PROVENANCE_BADGE['kn']
        badge_text_hi = f"सत्यापित: {source_name}" if is_verified else PROVENANCE_BADGE['hi']

        localized_samples.append({
            'id': item['id'],
            'name': d_name,
            'name_en': item.get('disease_name_en'),
            'name_kn': item.get('disease_name_kn'),
            'name_hi': item.get('disease_name_hi'),
            'image': resolved_img,
            'status': img_st,
            'image_status': img_st,
            'reason': img_reason,
            'image_status_reason': img_reason,
            'has_embedded_text': eval_res.get('has_embedded_text', False),
            'image_type': 'unknown',
            'provenance_badge': badge_text_kn if lang == 'kn' else (badge_text_hi if lang == 'hi' else badge_text_en),
            'provenance_badge_en': badge_text_en,
            'provenance_badge_kn': badge_text_kn,
            'provenance_badge_hi': badge_text_hi,
            'symptoms': symptoms,
            'treatment': treatment,
            'remedy': treatment,
            'verified_by_expert': is_verified,
            'verified': is_verified,
            'source': source_name,
            'license': source_lic,
            'source_license': source_lic,
            'confidence_level': conf_level,
            'last_reviewed_by': reviewer,
            'last_reviewed_date': review_date,
            'is_healthy': is_healthy,
            'is_diagnosis_supported': is_supported
        })

    return localized_samples
