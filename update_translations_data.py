# -*- coding: utf-8 -*-
"""
Helper script to update translations.py with full disease reference database and exact disease helpers.
"""

EXTRA_CROP_SAMPLES = """    'corn': [
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
            'treatment_en': 'Spray Azoxystrobin (1 ml/L) or Pyraclostrobin at first symptom.',
            'treatment_kn': 'ಅಜಾಕ್ಸಿಸ್ಟ್ರೋಬಿನ್ (1 ಮಿಲಿ/ಲೀ) ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'एजोक्सीस्ट्रोबिन (1 मिली/लीटर) का छिड़काव करें।'
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
            'treatment_en': 'Spray Mancozeb (2.5 g/L) or Propiconazole (1 ml/L).',
            'treatment_kn': 'ಮ್ಯಾಂಕೋಜೆಬ್ (2.5 ಗ್ರಾಂ/ಲೀ) ಅಥವಾ ಪ್ರೊಪಿಕೊನಾಜೋಲ್ ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'मैनकोजेब (2.5 ग्राम/लीटर) या प्रोपिकोनाजोल का छिड़काव करें।'
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
            'treatment_en': 'Spray Mancozeb (2.5 g/L) or Chlorothalonil (2 g/L).',
            'treatment_kn': 'ಮ್ಯಾಂಕೋಜೆಬ್ (2.5 ಗ್ರಾಂ/ಲೀ) ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'मैनकोजेब या क्लोरोथैलोनिल का छिड़काव करें।'
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
            'treatment_en': 'Spray Diafenthiuron (1 g/L) or Imidacloprid (0.3 ml/L) to control whitefly vector.',
            'treatment_kn': 'ಬಿಳಿ ನೊಣ ನಿಯಂತ್ರಣಕ್ಕೆ ಡಯಾಫೆಂಥಿಯುರಾನ್ (1 ಗ್ರಾಂ/ಲೀ) ಅಥವಾ ಇಮಿಡಾಕ್ಲೋಪ್ರಿಡ್ ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'सफेद मक्खी नियंत्रण हेतु डायफेनथियूरोन (1 ग्राम/लीटर) या इमिडाक्लोप्रिड का छिड़काव करें।'
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
            'treatment_en': 'Spray Azoxystrobin (1 ml/L) or Difenoconazole (0.5 ml/L) at fruit set.',
            'treatment_kn': 'ಅಜಾಕ್ಸಿಸ್ಟ್ರೋಬಿನ್ (1 ಮಿಲಿ/ಲೀ) ಅಥವಾ ಡೈಫೆನೊಕೊನಾಜೋಲ್ ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'एजोक्सीस्ट्रोबिन या डाइफेनोकोनाजोल का छिड़काव करें।'
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
            'treatment_en': 'Drench with Copper Oxychloride (3 g/L) + Streptocycline (0.1 g/L).',
            'treatment_kn': 'ಕಾಪರ್ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ (3 ಗ್ರಾಂ/ಲೀ) + ಸ್ಟ್ರೆಪ್ಟೊಸೈಕ್ಲಿನ್ ಬುಡಕ್ಕೆ ಸುರಿಯಿರಿ.',
            'treatment_hi': 'कॉपर ऑक्सीक्लोराइड + स्ट्रेप्टोसाइक्लिन का थालों में छिड़काव करें।'
        }
    ],
    'black pepper': [
        {
            'id': 'quick_wilt',
            'disease_name_en': 'Quick Wilt / Foot Rot (Phytophthora)',
            'disease_name_kn': 'ಕಾಳುಮೆಣಸಿನ ಶೀಘ್ರ ಸೊರಗು ರೋಗ (ಕೊಳೆರೋಗ)',
            'disease_name_hi': 'काली मिर्च त्वरित विल्ट / जड़ सड़न',
            'verified_by_expert': False,
            'image': 'static/disease_samples/black_pepper/quick_wilt.jpg',
            'symptoms_en': 'Dark water-soaked lesions on leaves and collar region leading to sudden vine collapse in monsoon.',
            'symptoms_kn': 'ಮುಂಗಾರು ಮಳೆಯಲ್ಲಿ ಕಾಂಡದ ಬುಡ ಕೊಳೆತು ಬಳ್ಳಿಗಳು ಹಠಾತ್ತನೆ ಉದುರಿ ಒಣಗುತ್ತವೆ.',
            'symptoms_hi': 'मानसून में तने के निचले हिस्से में सड़न जिससे पूरी बेल अचानक सूख जाती है।',
            'treatment_en': 'Apply 1% Bordeaux mixture spray and drench root zone with Metalaxyl (1.25 g/L).',
            'treatment_kn': '1% ಬೋರ್ಡೋ ದ್ರಾವಣ ಸಿಂಪಡಿಸಿ ಮತ್ತು ಬುಡಕ್ಕೆ ಮೆಟಾಲಾಕ್ಸಿಲ್ ಹಾಕಿ.',
            'treatment_hi': '1% बोर्डो मिश्रण का छिड़काव करें और थालों में मेटालेक्सिल डालें।'
        },
        {
            'id': 'pollu_disease',
            'disease_name_en': 'Pollu Disease (Anthracnose)',
            'disease_name_kn': 'ಪೊಳ್ಳು ರೋಗ (ಆಂಥ್ರಾಕ್ನೋಸ್)',
            'disease_name_hi': 'पोल्लू रोग (एन्थ्रेक्नोज)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/black_pepper/pollu.jpg',
            'symptoms_en': 'Circular brownish spots on leaves and premature dropping of pepper spikes with hollow berries.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ಕಂದು ಕಲೆಗಳು ಮತ್ತು ಕಾಳುಗಳು ಪೊಳ್ಳಾಗಿ ಉದುರುವುದು.',
            'symptoms_hi': 'पत्तियों पर भूरे धब्बे और खोखले दानों वाली बालियों का गिरना।',
            'treatment_en': 'Spray 1% Bordeaux mixture or Carbendazim (1 g/L) during berry formation.',
            'treatment_kn': '1% ಬೋರ್ಡೋ ದ್ರಾವಣ ಅಥವಾ ಕಾರ್ಬೆಂಡಾಜಿಮ್ (1 ಗ್ರಾಂ/ಲೀ) ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': '1% बोर्डो मिश्रण या कार्बेन्डाजिम का छिड़काव करें।'
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
            'treatment_en': 'Control citrus psyllid vector with Imidacloprid (0.5 ml/L); consult horticulture officer.',
            'treatment_kn': 'ಸಿಟ್ರಸ್ ಸಿಲ್ಲಾ ಕೀಟ ನಿಯಂತ್ರಣಕ್ಕೆ ಇಮಿಡಾಕ್ಲೋಪ್ರಿಡ್ ಸಿಂಪಡಿಸಿ; ತೋಟಗಾರಿಕೆ ಇಲಾಖೆಯನ್ನು ಸಂಪರ್ಕಿಸಿ.',
            'treatment_hi': 'सिट्रस साइला कीट नियंत्रण हेतु इमिडाक्लोप्रिड का छिड़काव करें; बागवानी अधिकारी से सलाह लें।'
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
            'treatment_en': 'Spray Streptocycline (0.1 g/L) + Copper Oxychloride (2.5 g/L).',
            'treatment_kn': 'ಸ್ಟ್ರೆಪ್ಟೊಸೈಕ್ಲಿನ್ (0.1 ಗ್ರಾಂ/ಲೀ) + ಕಾಪರ್ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'स्ट्रेप्टोसाइक्लिन (0.1 ग्राम/लीटर) + कॉपर ऑक्सीक्लोराइड का छिड़काव करें।'
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
            'treatment_en': 'Spray Wettable Sulphur (2 g/L) or Dinocap (1 ml/L) or Hexaconazole.',
            'treatment_kn': 'ಕರಗುವ ಗಂಧಕ (2 ಗ್ರಾಂ/ಲೀ) ಅಥವಾ ಹೆಕ್ಸಾಕೊನಾಜೋಲ್ ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'घुलनशील गंधक (2 ग्राम/लीटर) या हेक्साकोनाजोल का छिड़काव करें।'
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
            'treatment_en': 'Spray Metalaxyl + Mancozeb (2 g/L) or Cymoxanil.',
            'treatment_kn': 'ಮೆಟಾಲಾಕ್ಸಿಲ್ + ಮ್ಯಾಂಕೋಜೆಬ್ (2 ಗ್ರಾಂ/ಲೀ) ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'मेटालेक्सिल + मैनकोजेब का छिड़काव करें।'
        }
    ],
    'jowar': [
        {
            'id': 'grain_mold',
            'disease_name_en': 'Sorghum Grain Mold',
            'disease_name_kn': 'ಜೋಳದ ಕಾಳು ಬೂಸ್ಟು ರೋಗ',
            'disease_name_hi': 'ज्वार दाना फफूंद (ग्रेन मोल्ड)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/jowar/grain_mold.jpg',
            'symptoms_en': 'Black or pinkish fungal discolouration on developing grain panicles during wet weather.',
            'symptoms_kn': 'ತೆನೆಗಳಲ್ಲಿ ಕಾಳುಗಳು ಕಪ್ಪು ಅಥವಾ ಗುಲಾಬಿ ಬಣ್ಣಕ್ಕೆ ತಿರುಗಿ ಕೊಳೆಯುತ್ತವೆ.',
            'symptoms_hi': 'बालियों में दानों पर काले या गुलाबी रंग की फफूंद लग जाती है।',
            'treatment_en': 'Spray Propiconazole (1 ml/L) at 50% flowering stage.',
            'treatment_kn': 'ಹೂವಾಡುವ ಹಂತದಲ್ಲಿ ಪ್ರೊಪಿಕೊನಾಜೋಲ್ (1 ಮಿಲಿ/ಲೀ) ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'फूल आने के समय प्रोपिकोनाजोल (1 मिली/लीटर) का छिड़काव करें।'
        },
        {
            'id': 'leaf_rust',
            'disease_name_en': 'Sorghum Leaf Rust (Puccinia purpurea)',
            'disease_name_kn': 'ಜೋಳದ ಎಲೆ ತುಕ್ಕು ರೋಗ',
            'disease_name_hi': 'ज्वार पत्ती गेरुआ (रस्ट)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/jowar/rust.jpg',
            'symptoms_en': 'Small purplish-red or brown pustules scattered over leaf blades.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ಸಣ್ಣ ನೇರಳೆ-ಕೆಂಪು ಅಥವಾ ಕಂದು ಬಣ್ಣದ ತುಕ್ಕು ಚುಕ್ಕೆಗಳು.',
            'symptoms_hi': 'पत्तियों पर छोटे जामुनी-लाल या भूरे फफोले।',
            'treatment_en': 'Spray Mancozeb (2.5 g/L) at first symptom.',
            'treatment_kn': 'ಮ್ಯಾಂಕೋಜೆಬ್ (2.5 ಗ್ರಾಂ/ಲೀ) ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'मैनकोजेब (2.5 ग्राम/लीटर) का छिड़काव करें।'
        }
    ],
    'sunflower': [
        {
            'id': 'alternaria_blight',
            'disease_name_en': 'Alternaria Leaf Blight (Alternaria helianthi)',
            'disease_name_kn': 'ಸೂರ್ಯಕಾಂತಿ ಎಲೆ ಕಮಟು ರೋಗ',
            'disease_name_hi': 'सूरजमुखी अल्टरनेरिया पत्ती झुलसा',
            'verified_by_expert': False,
            'image': 'static/disease_samples/sunflower/alternaria.jpg',
            'symptoms_en': 'Dark brown to black circular lesions with concentric rings surrounded by yellow halo.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ಕಪ್ಪು-ಕಂದು ವೃತ್ತಾಕಾರದ ಕಲೆಗಳುಂಟಾಗಿ ಎಲೆಗಳು ಕಮರುತ್ತವೆ.',
            'symptoms_hi': 'पत्तियों पर संकेंद्री छल्लों वाले काले-भूरे गोल धब्बे।',
            'treatment_en': 'Spray Mancozeb (2.5 g/L) or Iprodione (1.5 g/L).',
            'treatment_kn': 'ಮ್ಯಾಂಕೋಜೆಬ್ (2.5 ಗ್ರಾಂ/ಲೀ) ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'मैनकोजेब या इप्रोडिओन का छिड़काव करें।'
        },
        {
            'id': 'head_rot',
            'disease_name_en': 'Rhizopus Head Rot',
            'disease_name_kn': 'ಸೂರ್ಯಕಾಂತಿ ಹೂಗೊಂಚಲು ಕೊಳೆ ರೋಗ',
            'disease_name_hi': 'सूरजमुखी हेड रॉट (सिर सड़न)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/sunflower/head_rot.jpg',
            'symptoms_en': 'Water-soaked soft brown rotting of the capitulum head back.',
            'symptoms_kn': 'ಹೂವಿನ ತಲೆಯ ಹಿಂಭಾಗ ಮೆತ್ತಗಾಗಿ ಕೊಳೆತು ಕಪ್ಪಾಗುತ್ತದೆ.',
            'symptoms_hi': 'फूल के पिछले हिस्से में पानीदार भूरी सड़न।',
            'treatment_en': 'Avoid insect injury to head; spray Carbendazim (1 g/L).',
            'treatment_kn': 'ಕಾರ್ಬೆಂಡಾಜಿಮ್ (1 ಗ್ರಾಂ/ಲೀ) ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'कार्बेन्डाजिम (1 ग्राम/लीटर) का छिड़काव करें।'
        }
    ],
    'arecanut': [
        {
            'id': 'koleroga',
            'disease_name_en': 'Koleroga / Mahali (Fruit Rot)',
            'disease_name_kn': 'ಅಡಿಕೆ ಕೊಳೆರೋಗ (ಮಹಾಲಿ)',
            'disease_name_hi': 'सुपारी कोलेरोगा / महाली (फल सड़न)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/arecanut/koleroga.jpg',
            'symptoms_en': 'Dark green water-soaked lesions at fruit base causing heavy premature nut shedding.',
            'symptoms_kn': 'ಮಳೆಯ ಸಮಯದಲ್ಲಿ ಅಡಿಕೆ ಕಾಯಿಗಳ ಬುಡದಲ್ಲಿ ಕಪ್ಪು ಕಲೆಗಳುಂಟಾಗಿ ಉದುರುತ್ತವೆ.',
            'symptoms_hi': 'बारिश में सुपारी के आधार पर काले धब्बे जिससे कच्चे फल भारी मात्रा में गिरते हैं।',
            'treatment_en': 'Spray 1% Bordeaux mixture before onset of southwest monsoon.',
            'treatment_kn': 'ಮುಂಗಾರು ಆರಂಭಕ್ಕೆ ಮುನ್ನ 1% ಬೋರ್ಡೋ ದ್ರಾವಣ ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'मानसून से पूर्व 1% बोर्डो मिश्रण का छिड़काव करें।'
        },
        {
            'id': 'yellow_leaf',
            'disease_name_en': 'Yellow Leaf Disease (Phytoplasma)',
            'disease_name_kn': 'ಅಡಿಕೆ ಹಳದಿ ಎಲೆ ರೋಗ',
            'disease_name_hi': 'सुपारी पीला पत्ती रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/arecanut/yellow_leaf.jpg',
            'symptoms_en': 'Progressive yellowing of outer whorl leaflets, kernel blackening and crown reduction.',
            'symptoms_kn': 'ಗರಿಗಳು ತುದಿಯಿಂದ ಹಳದಿಯಾಗುವುದು ಮತ್ತು ಅಡಿಕೆ ತಿರುಳು ಕಪ್ಪಾಗುವುದು.',
            'symptoms_hi': 'पत्तियों का पीला पड़ना और सुपारी के अंदर का भाग काला होना।',
            'treatment_en': 'Apply balanced NPK + Micronutrients and root feed with Oxytetracycline.',
            'treatment_kn': 'ಸಮತೋಲಿತ ಪೋಷಕಾಂಶ ಮತ್ತು ಸೂಕ್ಷ್ಮ ಪೋಷಕಾಂಶ ಒದಗಿಸಿ.',
            'treatment_hi': 'संतुलित खाद एवं सूक्ष्म पोषक तत्व दें।'
        }
    ],
    'turmeric': [
        {
            'id': 'rhizome_rot',
            'disease_name_en': 'Rhizome Rot (Pythium / Fusarium)',
            'disease_name_kn': 'ಅರಿಶಿನ ಗಡ್ಡೆ ಕೊಳೆ ರೋಗ',
            'disease_name_hi': 'हल्दी कंद सड़न (राइजोम रॉट)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/turmeric/rhizome_rot.jpg',
            'symptoms_en': 'Water-soaked basal pseudostem collapse and soft decaying rhizomes with foul odor.',
            'symptoms_kn': 'ಕಾಂಡದ ಬುಡ ಮೆತ್ತಗಾಗಿ ಗಡ್ಡೆಗಳು ಕೊಳೆಯುತ್ತವೆ ಮತ್ತು ಸುಲಭವಾಗಿ ಕೀಳಬರುತ್ತವೆ.',
            'symptoms_hi': 'तने का निचला हिस्सा गल जाता है और कंद सड़ने लगते हैं।',
            'treatment_en': 'Drench with Copper Oxychloride (3 g/L) or Metalaxyl (1.25 g/L).',
            'treatment_kn': 'ಕಾಪರ್ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ (3 ಗ್ರಾಂ/ಲೀ) ಬುಡಕ್ಕೆ ಸುರಿಯಿರಿ.',
            'treatment_hi': 'कॉपर ऑक्सीक्लोराइड का जड़ों में छिड़काव करें।'
        },
        {
            'id': 'leaf_blotch',
            'disease_name_en': 'Leaf Blotch (Taphrina maculans)',
            'disease_name_kn': 'ಅರಿಶಿನ ಎಲೆ ಕಲೆ ರೋಗ',
            'disease_name_hi': 'हल्दी पत्ती धब्बा रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/turmeric/leaf_blotch.jpg',
            'symptoms_en': 'Small reddish-brown to dirty yellow spots coalescing into large necrotic patches.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ಕಂದು-ಹಳದಿ ಬಣ್ಣದ ಸಣ್ಣ ಚುಕ್ಕೆಗಳು ಹರಡುತ್ತವೆ.',
            'symptoms_hi': 'पत्तियों पर छोटे लाल-भूरे धब्बे जो बाद में बड़े हो जाते हैं।',
            'treatment_en': 'Spray Mancozeb (2.5 g/L) or Propiconazole (1 ml/L).',
            'treatment_kn': 'ಮ್ಯಾಂಕೋಜೆಬ್ (2.5 ಗ್ರಾಂ/ಲೀ) ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'मैनकोजेब या प्रोपिकोनाजोल का छिड़काव करें।'
        }
    ],
    'cashew': [
        {
            'id': 'tea_mosquito_dieback',
            'disease_name_en': 'Tea Mosquito Bug & Dieback',
            'disease_name_kn': 'ಗೋಡಂಬಿ ಸೊಳ್ಳೆ ಮತ್ತು ತುದಿ ಒಣಗು ರೋಗ',
            'disease_name_hi': 'काजू चाय मच्छर कीट एवं डाईबैक',
            'verified_by_expert': False,
            'image': 'static/disease_samples/cashew/dieback.jpg',
            'symptoms_en': 'Necrotic black lesions on tender shoots and flower panicles with drying tips.',
            'symptoms_kn': 'ಚಿಗುರು ಮತ್ತು ಹೂಗೊಂಚಲುಗಳ ಮೇಲೆ ಕಪ್ಪು ಕಲೆಗಳುಂಟಾಗಿ ತುದಿ ಒಣಗುತ್ತದೆ.',
            'symptoms_hi': 'कोमल टहनियों और फूलों पर काले धब्बे जिससे टहनियां सूखती हैं।',
            'treatment_en': 'Spray Lambda Cyhalothrin (0.6 ml/L) at flushing, flowering, and nut set.',
            'treatment_kn': 'ಲ್ಯಾಮ್ಡಾ ಸೈಹ್ಯಾಲೋಥ್ರಿನ್ (0.6 ಮಿಲಿ/ಲೀ) ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'लैम्ब्डा साइहलोथ्रिन (0.6 मिली/लीटर) का छिड़काव करें।'
        }
    ],
    'mulberry': [
        {
            'id': 'leaf_spot',
            'disease_name_en': 'Mulberry Leaf Spot (Cercospora)',
            'disease_name_kn': 'ಹಿಪ್ಪುನೇರಳೆ ಎಲೆ ಚುಕ್ಕೆ ರೋಗ',
            'disease_name_hi': 'शहतूत पत्ती धब्बा रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/mulberry/leaf_spot.jpg',
            'symptoms_en': 'Brown circular spots with chlorotic margins causing unpalatable silkworm feed.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ಕಂದು ಚುಕ್ಕೆಗಳು ಬರುವುದರಿಂದ ರೇಷ್ಮೆ ಹುಳುಗಳಿಗೆ ಮೇವು ಸೂಕ್ತವಾಗುವುದಿಲ್ಲ.',
            'symptoms_hi': 'पत्तियों पर भूरे गोल धब्बे जिससे पत्तियां रेशम कीटों के लिए अनुपयुक्त हो जाती हैं।',
            'treatment_en': 'Spray Carbendazim (1 g/L); wait 7 days before feeding silkworms.',
            'treatment_kn': 'ಕಾರ್ಬೆಂಡಾಜಿಮ್ (1 ಗ್ರಾಂ/ಲೀ) ಸಿಂಪಡಿಸಿ (7 ದಿನಗಳ ನಂತರ ಹುಳುಗಳಿಗೆ ನೀಡಿ).',
            'treatment_hi': 'कार्बेन्डाजिम का छिड़काव करें और 7 दिन बाद ही रेशम कीटों को खिलाएं।'
        }
    ],
    'green gram': [
        {
            'id': 'yellow_mosaic',
            'disease_name_en': 'Mungbean Yellow Mosaic Virus (MYMV)',
            'disease_name_kn': 'ಹೆಸರುಕಾಳು ಹಳದಿ ಮೊಸಾಯಿಕ್ ರೋಗ',
            'disease_name_hi': 'मूंग पीला मोज़ेक वायरस (MYMV)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/green_gram/yellow_mosaic.jpg',
            'symptoms_en': 'Bright yellow patches alternating with green on trifoliate leaves, severely reducing pod yield.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ಹಳದಿ ಮತ್ತು ಹಸಿರು ಮಿಶ್ರಿತ ಚುಕ್ಕೆಗಳು ಹರಡಿ ಇಳುವರಿ ಕಡಿಮೆಯಾಗುತ್ತದೆ.',
            'symptoms_hi': 'पत्तियों पर चमकदार पीले और हरे धब्बे, जिससे फलियों की पैदावार घटती है।',
            'treatment_en': 'Spray Dimethoate (1.5 ml/L) or Acetamiprid to control whitefly vector.',
            'treatment_kn': 'ಬಿಳಿ ನೊಣ ನಿಯಂತ್ರಣಕ್ಕೆ ಡೈಮೆಥೊಯೇಟ್ (1.5 ಮಿಲಿ/ಲೀ) ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'सफेद मक्खी नियंत्रण हेतु डाइमेथोएट (1.5 मिली/लीटर) का छिड़काव करें।'
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
            'treatment_en': 'Seed treatment with Thiram (2 g/kg); spray Mancozeb (2 g/L).',
            'treatment_kn': 'ಥೈರಾಮ್‌ನಿಂದ ಬೀಜೋಪಚಾರ ಮಾಡಿ; ಮ್ಯಾಂಕೋಜೆಬ್ ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'थीरम से बीजोपचार करें और मैनकोजेब का छिड़काव करें।'
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
            'treatment_en': 'Drench nursery and field with Metalaxyl MZ (2 g/L).',
            'treatment_kn': 'ಮೆಟಾಲಾಕ್ಸಿಲ್ (2 ಗ್ರಾಂ/ಲೀ) ಬುಡಕ್ಕೆ ಸುರಿಯಿರಿ.',
            'treatment_hi': 'मेटालेक्सिल (2 ग्राम/लीटर) से थालों का उपचार करें।'
        }
    ],
    'ginger': [
        {
            'id': 'soft_rot',
            'disease_name_en': 'Soft Rot / Rhizome Rot (Pythium)',
            'disease_name_kn': 'ಶುಂಠಿ ಮೃದು ಕೊಳೆ ರೋಗ (ಗಡ್ಡೆ ಕೊಳೆ)',
            'disease_name_hi': 'अदरक मृदु सड़न (सॉफ्ट रॉट)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/ginger/soft_rot.jpg',
            'symptoms_en': 'Water-soaked collar pseudostem causing yellowing, drooping, and foul-smelling rhizome decay.',
            'symptoms_kn': 'ಕಾಂಡದ ಬುಡ ಕೊಳೆತು ಎಲೆಗಳು ಹಳದಿಯಾಗಿ ಬೀಳುತ್ತವೆ, ಶುಂಠಿ ಗಡ್ಡೆ ದುರ್ವಾಸನೆಯಿಂದ ಕೊಳೆಯುತ್ತದೆ.',
            'symptoms_hi': 'तने के निचले हिस्से में सड़न, पत्तियां पीली पड़कर गिरती हैं और कंद दुर्गंध के साथ सड़ते हैं।',
            'treatment_en': 'Seed rhizome treatment with Metalaxyl (2 g/L); drench field with COC (3 g/L).',
            'treatment_kn': 'ಬೀಜದ ಶುಂಠಿಗೆ ಮೆಟಾಲಾಕ್ಸಿಲ್ ಉಪಚಾರ ಮಾಡಿ; ಕಾಪರ್ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ ಬುಡಕ್ಕೆ ಹಾಕಿ.',
            'treatment_hi': 'कंद उपचार करें और कॉपर ऑक्सीक्लोराइड से थालों की सिंचाई करें।'
        }
    ],
    'onion': [
        {
            'id': 'purple_blotch',
            'disease_name_en': 'Purple Blotch (Alternaria porri)',
            'disease_name_kn': 'ಈರುಳ್ಳಿ ನೇರಳೆ ಚುಕ್ಕೆ ರೋಗ (ಪರ್ಪಲ್ ಬ್ಲಾಚ್)',
            'disease_name_hi': 'प्याज बैंगनी धब्बा रोग (पर्पल ब्लॉच)',
            'verified_by_expert': False,
            'image': 'static/disease_samples/onion/purple_blotch.jpg',
            'symptoms_en': 'Small white sunken lesions with purple centers spreading along flower stalks and leaves.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ನೇರಳೆ ಬಣ್ಣದ ಕೇಂದ್ರವಿರುವ ಬಿಳಿ-ಕಂದು ಕಲೆಗಳು.',
            'symptoms_hi': 'पत्तियों और डंठल पर बैंगनी केंद्र वाले धंसे हुए धब्बे।',
            'treatment_en': 'Spray Mancozeb (2.5 g/L) or Tebuconazole (1 ml/L).',
            'treatment_kn': 'ಮ್ಯಾಂಕೋಜೆಬ್ (2.5 ಗ್ರಾಂ/ಲೀ) ಅಥವಾ ಟೆಬುಕೊನಾಜೋಲ್ ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'मैनकोजेब या टेबुकोनाजोल का छिड़काव करें।'
        }
    ],
    'pomegranate': [
        {
            'id': 'bacterial_blight_telya',
            'disease_name_en': 'Bacterial Blight / Telya (Xanthomonas)',
            'disease_name_kn': 'ದಾಳಿಂಬೆ ತೆಲ್ಯಾ / ಬ್ಯಾಕ್ಟೀರಿಯಲ್ ಬ್ಲೈಟ್ ರೋಗ',
            'disease_name_hi': 'अनार तेल्या / जीवाणु झुलसा रोग',
            'verified_by_expert': False,
            'image': 'static/disease_samples/pomegranate/telya.jpg',
            'symptoms_en': 'Dark oily water-soaked spots on leaves and fruit with characteristic Y-shaped cracking on rinds.',
            'symptoms_kn': 'ಎಲೆ ಮತ್ತು ಹಣ್ಣುಗಳ ಮೇಲೆ ಎಣ್ಣೆಯಂತಹ ಕಪ್ಪು ಕಲೆಗಳು ಮತ್ತು ಹಣ್ಣು ಬಿರಿಯುವುದು.',
            'symptoms_hi': 'पत्तियों और फलों पर तेल जैसे काले धब्बे और फलों का फटना।',
            'treatment_en': 'Spray Streptocycline (0.5 g/L) + Copper Oxychloride (2.5 g/L).',
            'treatment_kn': 'ಸ್ಟ್ರೆಪ್ಟೊಸೈಕ್ಲಿನ್ + ಕಾಪರ್ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'स्ट्रेप्टोसाइक्लिन + कॉपर ऑक्सीक्लोराइड का छिड़काव करें।'
        }
    ],
    'papaya': [
        {
            'id': 'ring_spot',
            'disease_name_en': 'Papaya Ring Spot Virus (PRSV)',
            'disease_name_kn': 'ಪಪ್ಪಾಯಿ ರಿಂಗ್ ಸ್ಪಾಟ್ ವೈರಸ್ ರೋಗ',
            'disease_name_hi': 'पपीता रिंग स्पॉट वायरस',
            'verified_by_expert': False,
            'image': 'static/disease_samples/papaya/ring_spot.jpg',
            'symptoms_en': 'Severe mosaic shoe-stringing of leaves and distinct concentric ring spots on fruit rinds.',
            'symptoms_kn': 'ಎಲೆಗಳು ನೂಲಿನಂತೆ ಮುದುರಿಕೊಳ್ಳುವುದು ಮತ್ತು ಹಣ್ಣಿನ ಮೇಲೆ ವೃತ್ತಾಕಾರದ ಕಲೆಗಳು.',
            'symptoms_hi': 'पत्तियों का धागे जैसा मुड़ना और फलों पर गोल छल्लेदार धब्बे।',
            'treatment_en': 'Control aphid vectors with systemic insecticide; rogue out infected plants.',
            'treatment_kn': 'ಸಸ್ಯ ಹೇನು ನಿಯಂತ್ರಿಸಿ ಮತ್ತು ರೋಗಗ್ರಸ್ತ ಗಿಡಗಳನ್ನು ನಾಶಪಡಿಸಿ.',
            'treatment_hi': 'माहू नियंत्रण करें और गंभीर रूप से प्रभावित पौधे उखाड़ दें।'
        }
    ],
    'watermelon': [
        {
            'id': 'anthracnose',
            'disease_name_en': 'Watermelon Anthracnose',
            'disease_name_kn': 'ಕಲ್ಲಂಗಡಿ ಕಪ್ಪು ಕಲೆ ರೋಗ',
            'disease_name_hi': 'तरबूज एन्थ्रेक्नोज',
            'verified_by_expert': False,
            'image': 'static/disease_samples/watermelon/anthracnose.jpg',
            'symptoms_en': 'Circular black lesions on foliage and sunken dark spots with pink slime on fruit.',
            'symptoms_kn': 'ಎಲೆಗಳ ಮೇಲೆ ಕಪ್ಪು ಕಲೆಗಳು ಮತ್ತು ಹಣ್ಣಿನ ಮೇಲೆ ಗುಳಿಬಿದ್ದ ಕಲೆಗಳು.',
            'symptoms_hi': 'पत्तियों पर काले धब्बे और फलों पर धंसे हुए घाव।',
            'treatment_en': 'Spray Mancozeb (2.5 g/L) or Carbendazim (1 g/L).',
            'treatment_kn': 'ಮ್ಯಾಂಕೋಜೆಬ್ (2.5 ಗ್ರಾಂ/ಲೀ) ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'मैनकोजेब या कार्बेन्डाजिम का छिड़काव करें।'
        }
    ],
    'muskmelon': [
        {
            'id': 'downy_mildew',
            'disease_name_en': 'Muskmelon Downy Mildew',
            'disease_name_kn': 'ಕರಬೂಜ ಡೌನಿ ಮಿಲ್ಡ್ಯೂ ರೋಗ',
            'disease_name_hi': 'खरबूजा डाउनी मिल्ड्यू',
            'verified_by_expert': False,
            'image': 'static/disease_samples/muskmelon/downy_mildew.jpg',
            'symptoms_en': 'Angular yellow lesions restricted by veins turning brown and papery.',
            'symptoms_kn': 'ಎಲೆಯ ನರಗಳಿಂದ ಸೀಮಿತವಾದ ಹಳದಿ-ಕಂದು ಕಲೆಗಳು.',
            'symptoms_hi': 'नसों से बंधे कोणीय पीले-भूरे धब्बे।',
            'treatment_en': 'Spray Metalaxyl + Mancozeb (2 g/L).',
            'treatment_kn': 'ಮೆಟಾಲಾಕ್ಸಿಲ್ + ಮ್ಯಾಂಕೋಜೆಬ್ ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'मेटालेक्सिल + मैनकोजेब का छिड़काव करें।'
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
            'treatment_en': 'Spray Copper Oxychloride (2.5 g/L) before bud break.',
            'treatment_kn': 'ಕಾಪರ್ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'कॉपर ऑक्सीक्लोराइड का छिड़काव करें।'
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
            'treatment_en': 'Spray Wettable Sulphur (2 g/L) or Myclobutanil.',
            'treatment_kn': 'ಕರಗುವ ಗಂಧಕ (2 ಗ್ರಾಂ/ಲೀ) ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'घुलनशील गंधक का छिड़काव करें।'
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
            'treatment_en': 'Spray Captan (2 g/L) or Azoxystrobin (1 ml/L).',
            'treatment_kn': 'ಕ್ಯಾಪ್ಟನ್ ಅಥವಾ ಅಜಾಕ್ಸಿಸ್ಟ್ರೋಬಿನ್ ಸಿಂಪಡಿಸಿ.',
            'treatment_hi': 'कैप्टन या एजोक्सीस्ट्रोबिन का छिड़काव करें।'
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
    ]
"""
