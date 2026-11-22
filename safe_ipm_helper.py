# Comprehensive script to clean all pests in CROP_TRANSLATIONS in translations.py
import re
import translations

# Standard safe IPM mapping for each crop
SAFE_IPM_PESTS = {
    'rice': {
        'en': [
            'Brown planthopper → Alternate wetting & drying, light traps, avoid excess nitrogen.',
            'Stem borer → Install pheromone traps @ 5/acre and release Trichogramma egg parasitoids.',
            'Blast disease → Seed treatment with Trichoderma viride (10g/kg) and balanced N-K nutrition.'
        ],
        'kn': [
            'ಕಂದು ಜಿಗಿಹುಳು → ನೀರು ಬಸಿದು ಒಣಗಿಸುವುದು, ದೀಪದ ಬಲೆಗಳು, ಹಿತಮಿತ ಸಾರಜನಕ ಬಳಕೆ.',
            'ಕಾಂಡ ಕೊರೆಯುವ ಹುಳು → ಎಕರೆಗೆ 5 ಮೋಹಕ ಬಲೆಗಳು ಮತ್ತು ಟ್ರೈಕೋಗ್ರಾಮ ಪರಾವಲಂಬಿ ಕಾರ್ಡ್‌ಗಳು.',
            'ಬೆಂಕಿ ರೋಗ (ಬ್ಲಾಸ್ಟ್) → ಟ್ರೈಕೋಡರ್ಮಾ ಬೀಜೋಪಚಾರ (10ಗ್ರಾಂ/ಕೆಜಿ) ಮತ್ತು ಸಮತೋಲಿತ ಗೊಬ್ಬರ.'
        ],
        'hi': [
            'भूरा फुदका (BPH) → बारी-बारी से जल निकासी, प्रकाश प्रपंच, संतुलित नाइट्रोजन प्रयोग।',
            'तना छेदक → प्रति एकड़ 5 फेरोमोन ट्रैप लगाएं एवं ट्राइकोग्रामा अंड परजीवी छोड़ें।',
            'ब्लास्ट रोग → ट्राइकोडर्मा विरिडी (10 ग्राम/किग्रा) से बीजोपचार एवं संतुलित खाद।'
        ]
    },
    'maize': {
        'en': [
            'Fall Armyworm (FAW) Scouting: Install pheromone traps @ 5/acre; apply NSKE 5% / Bt bio-spray at early instar.',
            'Stem borer → Monitoring with light traps and Trichogramma cards; apply push-pull trap cropping.',
            'Aphids → Sticky traps & 5% neem oil spray; conserve ladybird beetles.'
        ],
        'kn': [
            'ಲದ್ದಿ ಹುಳು (FAW) ಕಣ್ಗಾವಲು: ಎಕರೆಗೆ 5 ಮೋಹಕ ಬಲೆಗಳು; ಬೇವಿನ ಕಷಾಯ (NSKE 5%) ಅಥವಾ ಜೈವಿಕ Bt ಬಳಕೆ.',
            'ಕಾಂಡ ಕೊರೆಯುವ ಹುಳು → ದೀಪದ ಬಲೆ ಮತ್ತು ಟ್ರೈಕೋಗ್ರಾಮ ಕಾರ್ಡ್‌ಗಳು; ಆಕರ್ಷಕ ಬೆಳೆಗಳ ಬಳಕೆ.',
            'ಸಸ್ಯ ಹೇನು (Aphids) → ಹಳದಿ ಜಿಗುಟು ಬಲೆ ಮತ್ತು 5% ಬೇವಿನ ಎಣ್ಣೆ ಸಿಂಪರಣೆ.'
        ],
        'hi': [
            'फॉल आर्मीवर्म (FAW) निगरानी: प्रति एकड़ 5 फेरोमोन ट्रैप; नीम काढ़ा (NSKE 5%) या जैविक Bt का प्रयोग।',
            'तना छेदक → प्रकाश प्रपंच और ट्राइकोग्रामा कार्ड का उपयोग; ट्रैप क्रॉपिंग।',
            'माहू (एफिड्स) → पीले चिपचिपे ट्रैप और 5% नीम तेल छिड़काव; लेडीबर्ड भृंग संरक्षण।'
        ]
    },
    'chickpea': {
        'en': [
            'Pod borer (Helicoverpa) → Pheromone traps @ 5/acre, bird perches, and HaNPV spray (250 LE/ha).',
            'Wilt disease → Crop rotation, Trichoderma viride seed treatment @ 4 g/kg, avoid waterlogging.',
            'Aphids → Yellow sticky traps and 5% neem seed kernel extract spray.'
        ],
        'kn': [
            'ಕಾಯಿ ಕೊರೆಯುವ ಹುಳು → ಮೋಹಕ ಬಲೆ (5/ಎಕರೆ), ಪಕ್ಷಿ ಆಸರೆಗಳು ಮತ್ತು HaNPV ಸಿಂಪರಣೆ.',
            'ಸೊರಗು ರೋಗ → ಬೆಳೆ ಪರಿವರ್ತನೆ, ಟ್ರೈಕೋಡರ್ಮಾ ಬೀಜೋಪಚಾರ (4 ಗ್ರಾಂ/ಕೆಜಿ), ನೀರು ನಿಲ್ಲದಂತೆ ನಿರ್ವಹಣೆ.',
            'ಸಸ್ಯ ಹೇನು → ಹಳದಿ ಜಿಗುಟು ಬಲೆ ಮತ್ತು 5% ಬೇವಿನ ಕಷಾಯ ಸಿಂಪರಣೆ.'
        ],
        'hi': [
            'फली छेदक → फेरोमोन ट्रैप @ 5/एकड़, पक्षी बसेरे और HaNPV जैविक छिड़काव।',
            'उकठा (विल्ट) रोग → फसल चक्र, ट्राइकोडर्मा विरिडी बीजोपचार (4 ग्राम/किग्रा), जल निकासी।',
            'माहू → पीले चिपचिपे ट्रैप और 5% नीम बीज अर्क छिड़काव।'
        ]
    },
    'kidneybeans': {
        'en': [
            'Bean fly → Soil solarization and seed treatment with bio-agents.',
            'Aphids → 5% neem oil spray and yellow sticky traps.',
            'Rust → Crop hygiene, wider spacing, and bio-fungicide preventive spray.'
        ],
        'kn': [
            'ಬೀನ್ ನೊಣ → ಮಣ್ಣು ಸೌರೀಕರಣ ಮತ್ತು ಜೈವಿಕ ಬೀಜೋಪಚಾರ.',
            'ಸಸ್ಯ ಹೇನು → 5% ಬೇವಿನ ಎಣ್ಣೆ ಮತ್ತು ಹಳದಿ ಜಿಗುಟು ಬಲೆಗಳು.',
            'ತುಕ್ಕು ರೋಗ → ಸ್ವಚ್ಛ ಬೇಸಾಯ ಮತ್ತು ಮುನ್ನೆಚ್ಚರಿಕೆ ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ.'
        ],
        'hi': [
            'बीन मक्खी → मृदा सौरीकरण एवं जैविक बीजोपचार।',
            'माहू → 5% नीम तेल छिड़काव और पीले चिपचिपे ट्रैप।',
            'रस्ट रोग → खेत की सफाई और जैविक फफूंदनाशक का प्रयोग।'
        ]
    },
    'pigeonpeas': {
        'en': [
            'Pod borer → Install pheromone traps, erect bird perches (50/ha), apply HaNPV spray.',
            'Pod fly → Early sowing, intercropping with sorghum/bajra, light traps.',
            'Sterility mosaic → Rogue out vector-infested diseased plants early.'
        ],
        'kn': [
            'ಕಾಯಿ ಕೊರೆಯುವ ಹುಳು → ಮೋಹಕ ಬಲೆ, ಪಕ್ಷಿ ಆಸರೆಗಳು (50/ಹೆಕ್ಟೇರ್) ಮತ್ತು HaNPV ಸಿಂಪರಣೆ.',
            'ಕಾಯಿ ನೊಣ → ಮುಂಚಿತ ಬಿತ್ತನೆ, ಜೋಳ/ಸಜ್ಜೆ ಮಿಶ್ರಬೆಳೆ ಮತ್ತು ದೀಪದ ಬಲೆಗಳು.',
            'ಬಂಜೆ ರೋಗ → ರೋಗಗ್ರಸ್ತ ಸಸಿಗಳನ್ನು ಕಿತ್ತು ನಾಶಪಡಿಸುವುದು.'
        ],
        'hi': [
            'फली छेदक → फेरोमोन ट्रैप, पक्षी बसेरे (50/हेक्टेयर) और HaNPV छिड़काव।',
            'फली मक्खी → समय पर बुवाई, ज्वार/बाजरा अंतरफसल और प्रकाश प्रपंच।',
            'बांझपन मोज़ेक → रोगग्रस्त पौधों को उखाड़कर नष्ट करना।'
        ]
    },
    'cotton': {
        'en': [
            'Bollworm → Pheromone traps @ 5/acre, light traps, and intercropping with cowpea/maize.',
            'Whitefly → Yellow sticky traps (15-20/acre) and 5% neem oil spray.',
            'Aphids → Conserve predatory ladybird beetles and spray 5% NSKE.'
        ],
        'kn': [
            'ಕಾಯಿ ಕೊರೆಯುವ ಹುಳು → ಎಕರೆಗೆ 5 ಮೋಹಕ ಬಲೆಗಳು, ದೀಪದ ಬಲೆಗಳು ಮತ್ತು ಅಲಸಂದೆ ಮಿಶ್ರಬೆಳೆ.',
            'ಬಿಳಿ ನೊಣ → ಹಳದಿ ಜಿಗುಟು ಬಲೆಗಳು (15-20/ಎಕರೆ) ಮತ್ತು 5% ಬೇವಿನ ಎಣ್ಣೆ.',
            'ಸಸ್ಯ ಹೇನು → ಪರಭಕ್ಷಕ ಜೀವಿಗಳ ಸಂರಕ್ಷಣೆ ಮತ್ತು 5% ಬೇವಿನ ಕಷಾಯ.'
        ],
        'hi': [
            'बॉलवर्म/सुंडी → प्रति एकड़ 5 फेरोमोन ट्रैप, प्रकाश प्रपंच और लोबिया/मक्का अंतरफसल।',
            'सफेद मक्खी → पीले चिपचिपे ट्रैप (15-20/एकड़) और 5% नीम तेल छिड़काव।',
            'माहू → लेडीबर्ड भृंग संरक्षण और 5% नीम काढ़ा छिड़काव।'
        ]
    },
    'coffee': {
        'en': [
            'White stem borer → Bark tracing, stem swabbing with lime, and light traps.',
            'Coffee berry borer → Beauveria bassiana bio-spray and broca traps.',
            'Leaf rust → Overhead shade regulation and 0.5% Bordeaux mixture.'
        ],
        'kn': [
            'ಬಿಳಿ ಕಾಂಡ ಕೊರೆಯುವ ಹುಳು → ಕಾಂಡಕ್ಕೆ ಸುಣ್ಣ ಹಚ್ಚುವುದು ಮತ್ತು ದೀಪದ ಬಲೆಗಳು.',
            'ಬೆರ್ರಿ ಬೋರರ್ → ಬವೇರಿಯಾ ಬಸ್ಸಿಯಾನ ಜೈವಿಕ ಸಿಂಪರಣೆ ಮತ್ತು ಬ್ರೋಕಾ ಬಲೆಗಳು.',
            'ಎಲೆ ತುಕ್ಕು ರೋಗ → ನೆರಳು ನಿರ್ವಹಣೆ ಮತ್ತು 0.5% ಬೋರ್ಡೋ ದ್ರಾವಣ.'
        ],
        'hi': [
            'सफेद तना छेदक → छाल सफाई, तने पर चूना लेपन और प्रकाश प्रपंच।',
            'बेरी बोरर → ब्यूवेरिया बेसियाना जैव छिड़काव और ब्रोका ट्रैप।',
            'पत्ती रस्ट → छाया प्रबंधन और 0.5% बोर्डो मिश्रण।'
        ]
    },
    'grapes': {
        'en': [
            'Downy mildew → Canopy management for air flow and preventive Bordeaux mixture.',
            'Thrips → Blue sticky traps and 5% neem formulation.',
            'Mealybug → Release Cryptolaemus montrouzieri predatory beetles.'
        ],
        'kn': [
            'ಬೂದಿ ರೋಗ/ಡೌನಿ ಮಿಲ್ಡ್ಯೂ → ಗಾಳಿಯಾಡುವಂತೆ ಕತ್ತರಿಸುವುದು ಮತ್ತು ಬೋರ್ಡೋ ದ್ರಾವಣ.',
            'ನುಸಿ (ಥ್ರಿಪ್ಸ್) → ನೀಲಿ ಜಿಗುಟು ಬಲೆಗಳು ಮತ್ತು 5% ಬೇವಿನ ಸೂತ್ರೀಕರಣ.',
            'ಹಿಟ್ಟು ತಿಗಣೆ (Mealybug) → ಕ್ರಿಪ್ಟೋಲಿಮಸ್ ಪರಭಕ್ಷಕ ಜೀವಿಗಳ ಬಿಡುಗಡೆ.'
        ],
        'hi': [
            'डाउनी मिल्ड्यू → छंटाई द्वारा वायु संचार और निवारक बोर्डो मिश्रण।',
            'थ्रिप्स → नीले चिपचिपे ट्रैप और 5% नीम उत्पाद।',
            'मिलीबग → क्रिप्टोलीमस परभक्षी भृंगों का उपयोग।'
        ]
    },
    'banana': {
        'en': [
            'Banana weevil → Pseudostem trap management and clean planting suckers.',
            'Sigatoka leaf spot → De-leafing infected foliage and spraying 1% Bordeaux mixture.',
            'Aphids → Yellow sticky traps and bio-pesticide spray.'
        ],
        'kn': [
            'ಬಾಳೆ ಸೊಂಡಿಲು ಹುಳು → ಕಾಂಡದ ಬಲೆ ನಿರ್ವಹಣೆ ಮತ್ತು ಶುದ್ಧ ಕಂದುಗಳ ಬಳಕೆ.',
            'ಸಿಗಾಟೋಕ ಎಲೆ ಚುಕ್ಕೆ ರೋಗ → ಸೋಂಕಿತ ಎಲೆಗಳನ್ನು ತೆಗೆಯುವುದು ಮತ್ತು 1% ಬೋರ್ಡೋ ದ್ರಾವಣ.',
            'ಸಸ್ಯ ಹೇನು → ಹಳದಿ ಜಿಗುಟು ಬಲೆ ಮತ್ತು ಜೈವಿಕ ಕೀಟನಾಶಕ.'
        ],
        'hi': [
            'केला घुन कीट → छद्म तना ट्रैप प्रबंधन और स्वस्थ कंदों का चयन।',
            'सिगाटोका पत्ती धब्बा → संक्रमित पत्तियों को हटाना और 1% बोर्डो मिश्रण।',
            'माहू → पीले चिपचिपे ट्रैप और जैविक छिड़काव।'
        ]
    },
    'mango': {
        'en': [
            'Mango hopper → Pruning dense canopy for sunlight and 5% neem oil spray (3000 ppm).',
            'Fruit fly → Methyl eugenol pheromone traps @ 10/ha and orchard sanitation.',
            'Powdery mildew → Wettable sulfur spray (2g/L) at panicle emergence.'
        ],
        'kn': [
            'ಮಾವಿನ ಜಿಗಿಹುಳು → ಸೂರ್ಯನ ಬೆಳಕಿಗಾಗಿ ರೆಂಬೆ ಕತ್ತರಿಸುವುದು ಮತ್ತು 5% ಬೇವಿನ ಎಣ್ಣೆ.',
            'ಹಣ್ಣಿನ ನೊಣ → ಮಿಥೈಲ್ ಯುಜೆನಾಲ್ ಮೋಹಕ ಬಲೆಗಳು (10/ಹೆಕ್ಟೇರ್) ಮತ್ತು ಸ್ವಚ್ಛತೆ.',
            'ಬೂದಿ ರೋಗ → ಹೂಗೊಂಚಲು ಬಿಡುವಾಗ ಗಂಧಕದ ಪುಡಿ (2 ಗ್ರಾಂ/ಲೀ) ಸಿಂಪರಣೆ.'
        ],
        'hi': [
            'आम का फुदका → धूप के लिए छंटाई और 5% नीम तेल का छिड़काव।',
            'फल मक्खी → मिथाइल यूजेनॉल फेरोमोन ट्रैप (10/हेक्टेयर) और स्वच्छता।',
            'चूर्णिल फफूंद → बौर निकलने के समय सल्फर (2 ग्राम/लीटर) का छिड़काव।'
        ]
    },
    'soybean': {
        'en': [
            'Stem fly → Seed treatment with Trichoderma and timely early planting.',
            'Girdle beetle → Destruction of alternate host weeds and light traps.',
            'Rust → Grow resistant varieties and apply bio-fungicide preventives.'
        ],
        'kn': [
            'ಕಾಂಡದ ನೊಣ → ಟ್ರೈಕೋಡರ್ಮಾ ಬೀಜೋಪಚಾರ ಮತ್ತು ಸಕಾಲಿಕ ಬಿತ್ತನೆ.',
            'ಕಂಕಣ ದುಂಬಿ (Girdle beetle) → ಕಳೆ ನಾಶ ಮತ್ತು ದೀಪದ ಬಲೆಗಳು.',
            'ತುಕ್ಕು ರೋಗ → ನಿರೋಧಕ ತಳಿಗಳ ಆಯ್ಕೆ ಮತ್ತು ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ.'
        ],
        'hi': [
            'तना मक्खी → ट्राइकोडर्मा बीजोपचार और समय पर बुवाई।',
            'गर्डल बीटल → खरपतवार नियंत्रण और प्रकाश प्रपंच।',
            'रस्ट रोग → प्रतिरोधी किस्में और जैविक कवकनाशी का प्रयोग।'
        ]
    },
    'groundnut': {
        'en': [
            'Tikka leaf spot → Seed treatment with Trichoderma viride (10g/kg) and neem oil spray.',
            'Leaf miner → Light traps and 5% neem seed kernel extract.',
            'White grub → Deep summer ploughing and application of Metarhizium anisopliae.'
        ],
        'kn': [
            'ತಿಕ್ಕಾ ಎಲೆ ಚುಕ್ಕೆ ರೋಗ → ಟ್ರೈಕೋಡರ್ಮಾ ಬೀಜೋಪಚಾರ (10ಗ್ರಾಂ/ಕೆಜಿ) ಮತ್ತು ಬೇವಿನ ಎಣ್ಣೆ.',
            'ಎಲೆ ಸುರಂಗ ಹುಳು → ದೀಪದ ಬಲೆ ಮತ್ತು 5% ಬೇವಿನ ಕಷಾಯ.',
            'ಬಿಳಿ ಹುಳು (White grub) → ಬೇಸಿಗೆ ಆಳ ಉಳುಮೆ ಮತ್ತು ಮೆಟಾರೈಜಿಯಮ್ ಜೈವಿಕ ಬಳಕೆ.'
        ],
        'hi': [
            'टिक्का पत्ती धब्बा → ट्राइकोडर्मा विरिडी (10 ग्राम/किग्रा) बीजोपचार और नीम तेल छिड़काव।',
            'पत्ती सुरंग कीट → प्रकाश प्रपंच और 5% नीम काढ़ा।',
            'सफेद लट (White grub) → गहरी ग्रीष्मकालीन जुताई और मेटाराइजियम का प्रयोग।'
        ]
    },
    'ragi': {
        'en': [
            'Blast disease → Seed treatment with Trichoderma harzianum (4g/kg seed) and balanced fertilizer use.',
            'Stem borer → Release Trichogramma parasitoids and use light traps.',
            'Aphids → 5% neem oil spray.'
        ],
        'kn': [
            'ಬೆಂಕಿ ರೋಗ (ಬ್ಲಾಸ್ಟ್) → ಟ್ರೈಕೋಡರ್ಮಾ ಬೀಜೋಪಚಾರ (4 ಗ್ರಾಂ/ಕೆಜಿ) ಮತ್ತು ಸಮತೋಲಿತ ಗೊಬ್ಬರ.',
            'ಕಾಂಡ ಕೊರೆಯುವ ಹುಳು → ಟ್ರೈಕೋಗ್ರಾಮ ಕಾರ್ಡ್ ಮತ್ತು ದೀಪದ ಬಲೆಗಳು.',
            'ಸಸ್ಯ ಹೇನು → 5% ಬೇವಿನ ಎಣ್ಣೆ ಸಿಂಪರಣೆ.'
        ],
        'hi': [
            'ब्लास्ट रोग → ट्राइकोडर्मा (4 ग्राम/किग्रा) बीजोपचार और संतुलित खाद।',
            'तना छेदक → ट्राइकोग्रामा परजीवी और प्रकाश प्रपंच।',
            'माहू → 5% नीम तेल का छिड़काव।'
        ]
    }
}

# Read translations.py
with open('translations.py', 'r', encoding='utf-8') as f:
    code = f.read()

# For any crop in SAFE_IPM_PESTS, let's update CROP_TRANSLATIONS
# We can also do a general cleanup in CROP_TRANSLATIONS
for crop_key, pest_dict in SAFE_IPM_PESTS.items():
    if crop_key in translations.CROP_TRANSLATIONS:
        translations.CROP_TRANSLATIONS[crop_key]['pests'] = pest_dict

print("Safe IPM mapping ready for verification!")
