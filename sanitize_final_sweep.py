# Script to clean remaining chemical lines in translations.py
import re

with open('translations.py', 'r', encoding='utf-8') as f:
    text = f.read()

replacements = [
    (r"Spinosad spray", "Pheromone traps (5/acre) and HaNPV bio-spray"),
    (r"Spray Lambda cyhalothrin", "Apply 5% neem oil / bio-agents"),
    (r"apply chlorpyrifos", "swab trunk with lime and apply neem cake"),
    (r"Spray Mancozeb", "Spray 5% neem oil / bio-fungicide"),
    (r"Spray Spinosad", "Install pheromone traps (5/acre) and spray HaNPV"),
    (r"Control thrips with Imidacloprid", "Install blue sticky traps and spray 5% neem oil"),
    (r"Spray Dichlorvos or release Ladybird beetles", "Release Ladybird beetles (Cryptolaemus) and spray 5% neem oil"),
    (r"Spray Carbendazim", "De-leaf infected leaves and spray 1% Bordeaux mixture"),
    (r"Spray Hexaconazole", "Practice crop rotation and apply Trichoderma"),
    (r"Spray Propiconazole", "Maintain balanced nutrition and apply bio-fungicide"),
    (r"Spray Dimethoate", "Install yellow sticky traps and spray 5% neem oil"),
    (r"Spray Fenazaquin", "Apply wettable sulfur (2g/L) and 5% neem oil"),
    (r"Spray Novaluron", "Apply HaNPV bio-spray and pheromone traps"),
    (r"Spray Ridomil", "Apply 1% Bordeaux mixture / bio-fungicide"),
    (r"Spray Metalaxyl", "Apply Trichoderma viride and 1% Bordeaux mixture"),
    (r"Spray Fipronil", "Install blue sticky traps and spray 5% neem oil"),
    (r"Spray Profenofos", "Install sticky traps and spray 5% neem oil"),
    (r"Spray Azoxystrobin", "Apply Trichoderma viride bio-fungicide"),
    (r"Spray Copper Oxychloride", "Spray 1% Bordeaux mixture"),
    (r"Spray copper oxychloride", "Spray 1% Bordeaux mixture"),
    (r"ಥಯಾಮೆಥೊಕ್ಸಾಮ್", "ಬೇವಿನ ಎಣ್ಣೆ ಮತ್ತು ಜೈವಿಕ ಪರಿಹಾರ"),
    (r"ಥೈರಾಮ್", "ಟ್ರೈಕೋಡರ್ಮಾ ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ"),
    (r"ಲ್ಯಾಂಬ್ಡಾ ಸೈಹ್ಯಾಲೋಥ್ರಿನ್", "5% ಬೇವಿನ ಎಣ್ಣೆ"),
    (r"ಡೈಕ್ಲೋರ್ವಾಸ್", "ಪರಭಕ್ಷಕ ಜೀರುಂಡೆಗಳು"),
    (r"ಸ್ಪಿನೊಸ್ಯಾಡ್", "ಮೋಹಕ ಬಲೆಗಳು ಮತ್ತು ಜೈವಿಕ ನಿಯಂತ್ರಣ"),
    (r"ಸ್ಪಿನೋಸ್ಯಾಡ್", "ಮೋಹಕ ಬಲೆಗಳು ಮತ್ತು ಜೈವಿಕ ನಿಯಂತ್ರಣ"),
    (r"ಮ್ಯಾಂಕೋಜೆಬ್", "ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಅಥವಾ ಬೇವಿನ ಎಣ್ಣೆ"),
    (r"ಕ್ಲೋರ್‌ಪೈರಿಫಾಸ್", "ಬೇವಿನ ಹಿಂಡಿ ಮತ್ತು ಜೈವಿಕ ನಿಯಂತ್ರಣ"),
    (r"ಕಾರ್ಬೆಂಡಾಜಿಮ್", "ಟ್ರೈಕೋಡರ್ಮಾ ಮತ್ತು ಶೇ. 1ರ ಬೋರ್ಡೋ"),
    (r"ಇಮಿಡಾಕ್ಲೋಪ್ರಿಡ್", "ಹಳದಿ ಜಿಗುಟು ಬಲೆಗಳು ಮತ್ತು ಬೇವಿನ ಎಣ್ಣೆ"),
    (r"हेक्साकोनाजोल", "जैविक कवकनाशी और फसल चक्र"),
    (r"प्रोपिकोनाजोल", "संतुलित पोषण एवं जैविक नियंत्रण"),
    (r"डाइमेथोएट", "पीले चिपचिपे ट्रैप और 5% नीम तेल"),
    (r"क्लोरपायरीफॉस", "सड़ी गोबर खाद और नीम खली"),
    (r"फेनाजाक्विन", "सल्फर (2 ग्राम/ली) और नीम तेल"),
    (r"स्पिनोसैड", "फेरोमोन ट्रैप और HaNPV जैविक छिड़काव"),
    (r"कार्बेन्डाजिम", "संक्रमित पत्तियां हटाएं और 1% बोर्डो मिश्रण"),
    (r"फोरेट", "गहरी ग्रीष्मकालीन जुताई और मेटाराइजियम"),
    (r"थायमेथॉक्सम", "ट्राइकोडर्मा बीजोपचार"),
    (r"ट्रायजोफॉस", "खरपतवार नियंत्रण और प्रकाश प्रपंच"),
    (r"ट्राइसाइक्लाजोल", "ट्राइकोडर्मा बीजोपचार और संतुलित खाद"),
    (r"मैंकोजेब", "जैविक कवकनाशी या 5% नीम तेल"),
    (r"इमिडाक्लोप्रिड", "पीले चिपचिपे ट्रैप और 5% नीम तेल"),
    (r"डाइक्लोरवोस", "लेडीबर्ड भृंग और 5% नीम तेल"),
    (r"लैम्ब्डा साइहलोथ्रिन", "5% नीम तेल और जैविक नियंत्रण"),
    (r"थीरम", "ट्राइकोडर्मा जैविक बीजोपचार"),
    (r"कॉपर ऑक्सीक्लोराइड", "1% बोर्डो मिश्रण या जैविक कवकनाशी")
]

for pat, repl in replacements:
    text = re.sub(pat, repl, text, flags=re.IGNORECASE)

with open('translations.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Final translations.py sweep complete!")
