# Complete cleaner for translations.py
import re

with open('translations.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace any pesticide lines in translations.py
chems_en_to_bio = [
    (r'Spray Mancozeb / Ridomil', 'Apply 5% neem oil / bio-fungicide preventives'),
    (r'Spray Imidacloprid', 'Install yellow sticky traps and spray 5% neem oil'),
    (r'Spray copper oxychloride', 'Spray 1% Bordeaux mixture / bio-fungicide'),
    (r'Spray Fipronil or Profenofos', 'Install blue sticky traps and spray 5% neem oil'),
    (r'Spray Hexaconazole', 'Practice crop rotation and apply Trichoderma'),
    (r'Spray Propiconazole', 'Maintain balanced N-K nutrition and crop hygiene'),
    (r'Spray Dimethoate', 'Install yellow sticky traps and spray 5% neem oil'),
    (r'Chlorpyrifos soil application', 'Apply decomposed FYM and neem cake into soil'),
    (r'Spray Fenazaquin', 'Apply wettable sulfur (2g/L) and 5% neem oil'),
    (r'Spray Spinosad / Novaluron', 'Install Helicoverpa pheromone traps @ 5/acre and spray HaNPV'),
    (r'Spray Mancozeb / Metalaxyl', 'Apply Trichoderma viride and 1% Bordeaux mixture'),
    (r'Control whiteflies with Imidacloprid', 'Install yellow sticky traps (20/acre) and spray 5% neem oil'),
    (r'Pseudostem weevil → Clean cultivation and chlorpyrifos', 'Pseudostem weevil → Pseudostem traps and field sanitation'),
    (r'Sigatoka leaf spot → Carbendazim spray', 'Sigatoka leaf spot → De-leafing infected leaves and 1% Bordeaux spray'),
    (r'Tikka leaf spot → Mancozeb spray', 'Tikka leaf spot → Seed treatment with Trichoderma (10g/kg) and neem spray'),
    (r'Leaf miner → Chlorpyrifos spray', 'Leaf miner → Light traps and 5% neem seed kernel extract'),
    (r'White grub → Phorate soil application', 'White grub → Deep summer ploughing and Metarhizium anisopliae application'),
    (r'Stem fly → Seed treatment with thiamethoxam', 'Stem fly → Seed treatment with Trichoderma and timely planting'),
    (r'Girdle beetle → Triazophos spray', 'Girdle beetle → Destruction of alternate weeds and light traps'),
    (r'Rust → Hexaconazole spray', 'Rust → Grow resistant varieties and apply bio-fungicides'),
    (r'Blast disease → Tricyclazole spray', 'Blast disease → Seed treatment with Trichoderma and balanced fertilizer'),
    (r'Stem borer → Chlorpyrifos spray', 'Stem borer → Light traps and Trichogramma cards'),
    (r'Aphids → Dimethoate spray', 'Aphids → Yellow sticky traps and 5% neem oil'),
    (r'White stem borer → Bark tracing and chlorpyrifos', 'White stem borer → Bark tracing, stem swabbing with lime, and light traps'),
    (r'Bollworm → Spray Spinosad', 'Bollworm → Pheromone traps (5/acre) and HaNPV spray'),
]

# Kannada replacements
chems_kn_to_bio = [
    (r'ಮ್ಯಾಂಕೋಜೆಬ್ ಸಿಂಪಡಿಸಿ', '5% ಬೇವಿನ ಎಣ್ಣೆ ಅಥವಾ ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಬಳಸಿ'),
    (r'ಇಮಿಡಾಕ್ಲೋಪ್ರಿಡ್ ಸಿಂಪಡಿಸಿ', 'ಹಳದಿ ಜಿಗುಟು ಬಲೆಗಳು ಮತ್ತು 5% ಬೇವಿನ ಎಣ್ಣೆ ಬಳಸಿ'),
    (r'ತಾಮ್ರದ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ ಸಿಂಪಡಿಸಿ', 'ಶೇ. 1ರ ಬೋರ್ಡೋ ಮಿಶ್ರಣ ಸಿಂಪಡಿಸಿ'),
    (r'ಫಿಪ್ರೊನಿಲ್ ಸಿಂಪಡಿಸಿ', 'ನೀಲಿ ಜಿಗುಟು ಬಲೆಗಳು ಮತ್ತು ಬೇವಿನ ಎಣ್ಣೆ ಬಳಸಿ'),
    (r'ಹೆಕ್ಸಾಕೊನಜೋಲ್ ಬಳಸಿ', 'ಬೆಳೆ ಪರಿವರ್ತನೆ ಮಾಡಿ ಮತ್ತು ಟ್ರೈಕೋಡರ್ಮಾ ಬಳಸಿ'),
    (r'ಹೆಕ್ಸಾಕೋನಾಜೋಲ್ ಸಿಂಪಡಿಸಿ', 'ಬೆಳೆ ಪರಿವರ್ತನೆ ಮಾಡಿ ಮತ್ತು ಟ್ರೈಕೋಡರ್ಮಾ ಬಳಸಿ'),
    (r'ಪ್ರೊಪಿಕೊನಜೋಲ್ ಸಿಂಪಡಿಸಿ', 'ಸಮತೋಲಿತ ಪೋಷಕಾಂಶ ಮತ್ತು ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು ಬಳಸಿ'),
    (r'ಪ್ರೊಪಿಕೊನಾಜೋಲ್ ಶಿಲೀಂಧ್ರನಾಶಕ ಬಳಸಿ', 'ಸಮತೋಲಿತ ಪೋಷಕಾಂಶ ಮತ್ತು ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು ಬಳಸಿ'),
    (r'ಡೈಮೆಥೊಯೇಟ್ ಸಿಂಪಡಿಸಿ', 'ಹಳದಿ ಜಿಗುಟು ಬಲೆಗಳು ಮತ್ತು 5% ಬೇವಿನ ಎಣ್ಣೆ ಬಳಸಿ'),
    (r'ಕ್ಲೋರ್‌ಪೈರಿಫಾಸ್ ಮಣ್ಣಿಗೆ ನೀಡಿ', 'ಬೇವಿನ ಹಿಂಡಿ ಮತ್ತು ಕಳಿತ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಬಳಸಿ'),
    (r'ಕ್ಲೋರ್‌ಪೈರಿಫಾಸ್ ಮಣ್ಣಿಗೆ ಹಾಕಿ', 'ಬೇವಿನ ಹಿಂಡಿ ಮತ್ತು ಕಳಿತ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಬಳಸಿ'),
    (r'ಕ್ಲೋರ್‌ಪೈರಿಫಾಸ್ ಸಿಂಪಡಿಸಿ', 'ದೀಪದ ಬಲೆಗಳು ಮತ್ತು ಟ್ರೈಕೋಗ್ರಾಮ ಕಾರ್ಡ್ ಬಳಸಿ'),
    (r'ಕ್ಲೋರ್‌ಪೈರಿಫಾಸ್ ಬಳಸಿ', 'ಕಾಂಡದ ಬಲೆಗಳು ಮತ್ತು ಸ್ವಚ್ಛ ಬೇಸಾಯ ಕ್ರಮಗಳನ್ನು ಬಳಸಿ'),
    (r'ಫೆನಾಜಾಕ್ವಿನ್ ಸಿಂಪಡಿಸಿ', 'ಗಂಧಕದ ಪುಡಿ (2 ಗ್ರಾಂ/ಲೀ) ಮತ್ತು ಬೇವಿನ ಎಣ್ಣೆ ಬಳಸಿ'),
    (r'ಸ್ಪಿನೊಸ್ಯಾಡ್ ಸಿಂಪಡಿಸಿ', 'ಮೋಹಕ ಬಲೆಗಳು (5/ಎಕರೆ) ಮತ್ತು HaNPV ಸಿಂಪಡಿಸಿ'),
    (r'ಕಾರ್ಬೆಂಡಾಜಿಮ್ ಸಿಂಪಡಿಸಿ', 'ಸೋಂಕಿತ ಎಲೆಗಳನ್ನು ತೆಗೆದು ಶೇ. 1ರ ಬೋರ್ಡೋ ಸಿಂಪಡಿಸಿ'),
    (r'ಫೋರೇಟ್ ಮಣ್ಣಿಗೆ ಸೇರಿಸಿ', 'ಆಳ ಉಳುಮೆ ಮತ್ತು ಮೆಟಾರೈಜಿಯಮ್ ಜೈವಿಕ ಶಿಲೀಂಧ್ರ ಬಳಸಿ'),
    (r'ಥಯಾಮೆಥೊಕ್ಸಾಮ್ ಬೀಜೋಪಚಾರ ಮಾಡಿ', 'ಟ್ರೈಕೋಡರ್ಮಾ ಬೀಜೋಪಚಾರ ಮತ್ತು ಸಕಾಲಿಕ ಬಿತ್ತನೆ ಮಾಡಿ'),
    (r'ಥಯಾಮೆಥೊಕ್ಸಾಮ್ ಸಿಂಪಡಿಸಿ', 'ಹಳದಿ ಜಿಗುಟು ಬಲೆ ಮತ್ತು ಬೇವಿನ ಕಷಾಯ ಬಳಸಿ'),
    (r'ಟ್ರಯಾಜೋಫಾಸ್ ಸಿಂಪಡಿಸಿ', 'ಕಳೆ ನಾಶ ಮತ್ತು ದೀಪದ ಬಲೆಗಳನ್ನು ಬಳಸಿ'),
    (r'ಟ್ರೈಸೈಕ್ಲಾಜೋಲ್ ಸಿಂಪಡಿಸಿ', 'ಟ್ರೈಕೋಡರ್ಮಾ ಬೀಜೋಪಚಾರ ಮತ್ತು ಸಮತೋಲಿತ ಗೊಬ್ಬರ ಬಳಸಿ'),
]

# Hindi replacements
chems_hi_to_bio = [
    (r'मैंकोजेब या रिडोमिल का छिड़काव करें', '5% नीम तेल या जैविक कवकनाशी का प्रयोग करें'),
    (r'मैंकोजेब का छिड़काव करें', '5% नीम तेल या जैविक कवकनाशी का प्रयोग करें'),
    (r'मैंकोजेब या मेटालेक्सिल का छिड़काव करें', 'ट्राइकोडर्मा और 1% बोर्डो मिश्रण का प्रयोग करें'),
    (r'इमिडाक्लोप्रिड स्प्रे करें', 'पीले चिपचिपे ट्रैप और 5% नीम तेल का प्रयोग करें'),
    (r'इमिडाक्लोप्रिड का छिड़काव करें', 'पीले चिपचिपे ट्रैप और 5% नीम तेल का छिड़काव करें'),
    (r'इमिडाक्लोप्रिड छिड़कें', 'पीले चिपचिपे ट्रैप और 5% नीम तेल का छिड़काव करें'),
    (r'कॉपर ऑक्सीक्लोराइड का छिड़काव करें', '1% बोर्डो मिश्रण या जैविक कवकनाशी का छिड़काव करें'),
    (r'फिप्रोनिल या प्रोफेनोफॉस स्प्रे करें', 'नीले चिपचिपे ट्रैप और नीम तेल का छिड़काव करें'),
    (r'फिप्रोनिल इंजेक्शन का प्रयोग करें', 'फेरोमोन ट्रैप और ताज की सफाई करें'),
    (r'हेक्साकोनाजोल स्प्रे करें', 'फसल चक्र अपनाएं और ट्राइकोडर्मा का प्रयोग करें'),
    (r'हेक्साकोनाजोल का छिड़काव करें', 'फसल चक्र अपनाएं और ट्राइकोडर्मा का प्रयोग करें'),
    (r'प्रोपिकोनाजोल का छिड़काव करें', 'संतुलित पोषण एवं जैविक नियंत्रण अपनाएं'),
    (r'प्रोपिकोनाजोल कवकनाशी का प्रयोग करें', 'संतुलित पोषण एवं जैविक नियंत्रण अपनाएं'),
    (r'डाइमेथोएट स्प्रे करें', 'पीले चिपचिपे ट्रैप और 5% नीम तेल का छिड़काव करें'),
    (r'डाइमेथोएट का छिड़काव करें', 'पीले चिपचिपे ट्रैप और 5% नीम तेल का छिड़काव करें'),
    (r'क्लोरपायरीफॉस का प्रयोग करें', 'सड़ी गोबर खाद और नीम खली का प्रयोग करें'),
    (r'क्लोरपायरीफॉस से मिट्टी उपचारित करें', 'सड़ी गोबर खाद और नीम खली का प्रयोग करें'),
    (r'क्लोरपायरीफॉस का छिड़काव करें', 'प्रकाश प्रपंच और ट्राइकोग्रामा कार्ड लगाएं'),
    (r'फेनाजाक्विन स्प्रे करें', 'सल्फर (2 ग्राम/ली) और नीम तेल का प्रयोग करें'),
    (r'स्पिनोसैड या नोवाल्यूरॉन का छिड़काव करें', 'प्रति एकड़ 5 फेरोमोन ट्रैप और HaNPV का छिड़काव करें'),
    (r'स्पिनोसैड का छिड़काव करें', 'फेरोमोन ट्रैप (5/एकड़) और HaNPV छिड़काव करें'),
    (r'कार्बेन्डाजिम का छिड़काव करें', 'संक्रमित पत्तियां हटाएं और 1% बोर्डो मिश्रण छिड़कें'),
    (r'फोरेट दाने का प्रयोग करें', 'गहरी ग्रीष्मकालीन जुताई और मेटाराइजियम का प्रयोग करें'),
    (r'थायमेथॉक्सम से बीजोपचार करें', 'ट्राइकोडर्मा बीजोपचार और समय पर बुवाई करें'),
    (r'थायमेथॉक्सम का छिड़काव करें', 'पीले चिपचिपे ट्रैप और नीम अर्क का छिड़काव करें'),
    (r'ट्रायजोफॉस का छिड़काव करें', 'खरपतवार नियंत्रण और प्रकाश प्रपंच का प्रयोग करें'),
    (r'ट्राइसाइक्लाजोल का छिड़काव करें', 'ट्राइकोडर्मा बीजोपचार और संतुलित खाद का प्रयोग करें'),
]

for pat, repl in chems_en_to_bio:
    text = re.sub(pat, repl, text, flags=re.IGNORECASE)

for pat, repl in chems_kn_to_bio:
    text = re.sub(pat, repl, text)

for pat, repl in chems_hi_to_bio:
    text = re.sub(pat, repl, text)

with open('translations.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("translations.py clean pass completed!")
