import re

banned = [
    'sun', 'sunny', 'sunshine', 'sunlight', 'humidity', 'humid', 'moisture', 
    'dry', 'cool', 'cooler', 'cooling', 'warm', 'warmer', 'warmth', 
    'rain', 'rains', 'rainfall', 'rainfed', 'shower', 'showers', 
    'heat', 'hot', 'breeze', 'wind', 'temperature', 'temperatures', 
    'weather', 'climate', 'climatic', 'monsoon', 'ambient', 'chilling'
]
pattern = re.compile(r'\b(' + '|'.join(banned) + r')\b', re.IGNORECASE)

facts = {
    'soybean': {
        'en': 'Protein-rich oilseed legume that enriches soil through biological nitrogen fixation.',
        'kn': 'ಸಾರಜನಕ ಸ್ಥಿರೀಕರಿಸಿ ಮಣ್ಣಿನ ಫಲವತ್ತತೆ ಹೆಚ್ಚಿಸುವ ಪ್ರಮುಖ ಎಣ್ಣೆಕಾಳು ಬೆಳೆ.',
        'hi': 'प्रोटीन युक्त तिलहनी दलहन जो जैविक नाइट्रोजन स्थिरीकरण द्वारा मिट्टी को समृद्ध बनाती है।'
    },
    'groundnut': {
        'en': 'Major oilseed legume that fixes nitrogen and develops pods underground.',
        'kn': 'ಮಣ್ಣಿನಡಿ ಕಾಯಿ ಕಟ್ಟುವ ಹಾಗೂ ಸಾರಜನಕ ಸ್ಥಿರೀಕರಿಸುವ ಪ್ರಮುಖ ವಾಣಿಜ್ಯ ಎಣ್ಣೆಕಾಳು ಬೆಳೆ.',
        'hi': 'प्रमुख तिलहनी फसल जो नाइट्रोजन स्थिरीकरण करती है और भूमिगत फलियां बनाती है।'
    },
    'ragi': {
        'en': 'Hardy millet crop with high dietary calcium content and deep rooting capacity.',
        'kn': 'ಅಧಿಕ ಕ್ಯಾಲ್ಸಿಯಂ ಮತ್ತು ನಾರಿನಂಶ ಹೊಂದಿರುವ ಸಾಂಪ್ರದಾಯಿಕ ಪೌಷ್ಟಿಕ ಸಿರಿಧಾನ್ಯ.',
        'hi': 'प्रचुर कैल्शियम और आहार फाइबर से भरपूर पारंपरिक पौष्टिक मोटा अनाज।'
    },
    'rice': {
        'en': 'Primary cereal food grain cultivated in puddled wetlands and irrigated systems.',
        'kn': 'ನೀರಾವರಿ ಮತ್ತು ಗದ್ದೆಗಳಲ್ಲಿ ಬೆಳೆಯಲಾಗುವ ಪ್ರಮುಖ ಆಹಾರ ಧಾನ್ಯ ಬೆಳೆ.',
        'hi': 'सिंचित खेतों और दलदली भूमि में उगाई जाने वाली प्रमुख खाद्यान्न फसल।'
    },
    'maize': {
        'en': 'High-yielding versatile cereal crop requiring well-drained fertile soils.',
        'kn': 'ಉತ್ತಮ ನೀರು ಬಸಿದು ಹೋಗುವ ಗೋಡು ಮಣ್ಣಿನಲ್ಲಿ ಬೆಳೆಯುವ ಅಧಿಕ ಇಳುವರಿಯ ಪ್ರಮುಖ ಧಾನ್ಯ.',
        'hi': 'उचित जल निकासी वाली उपजाऊ मिट्टी में उच्च उपज देने वाली बहुमुखी खाद्यान्न फसल।'
    },
    'arecanut': {
        'en': 'Perennial commercial plantation palm cultivated across dedicated agrarian belts.',
        'kn': 'ವಿಶೇಷ ಕೃಷಿ ವಲಯಗಳಲ್ಲಿ ಬೆಳೆಯಲಾಗುವ ದೀರ್ಘಾವಧಿಯ ಪ್ರಮುಖ ವಾಣಿಜ್ಯ ತೋಟಗಾರಿಕಾ ಬೆಳೆ.',
        'hi': 'विशिष्ट कृषि क्षेत्रों में उगाई जाने वाली प्रमुख दीर्घकालिक व्यावसायिक बागवानी फसल।'
    },
    'cashew': {
        'en': 'Commercial plantation crop with extensive taproots, well adapted to lateritic soils.',
        'kn': 'ಕೆಂಪು ಜಂಬಿಟ್ಟಿಗೆ ಮಣ್ಣಿಗೆ ಹೊಂದಿಕೊಳ್ಳುವ ಹಾಗೂ ಆಳವಾದ ಬೇರು ವ್ಯವಸ್ಥೆ ಹೊಂದಿರುವ ತೋಟಗಾರಿಕಾ ಬೆಳೆ.',
        'hi': 'गहरी जड़ प्रणाली वाली और लेटराइट मिट्टी के अनुकूल प्रमुख व्यावसायिक बागवानी फसल।'
    },
    'sunflower': {
        'en': 'Commercial oilseed crop cultivated for edible oil with high polyunsaturated fatty acids.',
        'kn': 'ಉತ್ತಮ ಗುಣಮಟ್ಟದ ಅಡುಗೆ ಎಣ್ಣೆ ನೀಡುವ ಪ್ರಮುಖ ವಾಣಿಜ್ಯ ಎಣ್ಣೆಕಾಳು ಬೆಳೆ.',
        'hi': 'उच्च पॉलीअनसैचुरेटेड फैटी एसिड युक्त खाद्य तेल के लिए उगाई जाने वाली तिलहनी फसल।'
    },
    'mulberry': {
        'en': 'Perennial foliage shrub cultivated to rear silkworm larvae for sericulture silk production.',
        'kn': 'ರೇಷ್ಮೆ ಹುಳು ಸಾಕಾಣಿಕೆಗೆ ಪೌಷ್ಟಿಕ ಎಲೆಗಳನ್ನು ಒದಗಿಸುವ ಪ್ರಮುಖ ತೋಟಗಾರಿಕಾ ಬೆಳೆ.',
        'hi': 'रेशम कीट पालन और उच्च गुणवत्ता वाले रेशम उत्पादन के लिए उगाई जाने वाली बहुवर्षीय झाड़ी।'
    },
    'jowar': {
        'en': 'Hardy staple cereal with extensive fibrous roots and high water-use efficiency.',
        'kn': 'ಆಳವಾದ ಬೇರು ಮತ್ತು ಕಡಿಮೆ ನೀರಿನಲ್ಲೂ ಉತ್ತಮ ಇಳುವರಿ ನೀಡುವ ಪ್ರಮುಖ ಧಾನ್ಯ.',
        'hi': 'गहरी जड़ प्रणाली और उच्च जल उपयोग दक्षता वाली प्रमुख पारंपरिक खाद्यान्न फसल।'
    },
    'bengalgram': {
        'en': 'Major protein-rich pulse crop that enriches soil through atmospheric nitrogen fixation.',
        'kn': 'ಸಾರಜನಕ ಸ್ಥಿರೀಕರಣದ ಮೂಲಕ ಮಣ್ಣಿನ ಫಲವತ್ತತೆ ಹೆಚ್ಚಿಸುವ ಪ್ರಮುಖ ಪ್ರೋಟೀನ್ ಯುಕ್ತ ಕಾಳು ಬೆಳೆ.',
        'hi': 'जैविक नाइट्रोजन स्थिरीकरण द्वारा मिट्टी की उर्वरता बढ़ाने वाली प्रमुख दलहनी फसल।'
    },
    'chickpea': {
        'en': 'Major protein-rich pulse crop that enriches soil through atmospheric nitrogen fixation.',
        'kn': 'ಸಾರಜನಕ ಸ್ಥಿರೀಕರಣದ ಮೂಲಕ ಮಣ್ಣಿನ ಫಲವತ್ತತೆ ಹೆಚ್ಚಿಸುವ ಪ್ರಮುಖ ಪ್ರೋಟೀನ್ ಯುಕ್ತ ಕಾಳು ಬೆಳೆ.',
        'hi': 'जैविक नाइट्रोजन स्थिरीकरण द्वारा मिट्टी की उर्वरता बढ़ाने वाली प्रमुख दलहनी फसल।'
    },
    'cotton': {
        'en': 'Primary fiber cash crop with indeterminate growth pattern and deep taproot system.',
        'kn': 'ಆಳವಾದ ಬೇರು ಮತ್ತು ನಿರಂತರ ಕವಲೊಡೆಯುವ ಪ್ರಮುಖ ನಾರಿನ ವಾಣಿಜ್ಯ ಬೆಳೆ.',
        'hi': 'गहरी मूसला जड़ और निरंतर शाखाएं विकसित करने वाली प्रमुख प्राकृतिक रेशा नकदी फसल।'
    },
    'sugarcane': {
        'en': 'Long-duration sucrose cash crop demanding intensive soil nutrients and systematic irrigation.',
        'kn': 'ಹೆಚ್ಚಿನ ಪೋಷಕಾಂಶ ಮತ್ತು ನೀರಾವರಿ ನಿರ್ವಹಣೆಗೆ ಸ್ಪಂದಿಸುವ ಪ್ರಮುಖ ವಾಣಿಜ್ಯ ಬೆಳೆ.',
        'hi': 'गहन मृदा पोषण और सुनियोजित सिंचाई प्रबंधन की आवश्यकता वाली प्रमुख नकदी फसल।'
    },
    'tomato': {
        'en': 'High-value commercial solanaceous vegetable cultivated through nursery seedling transplanting.',
        'kn': 'ಸಸಿ ಮಡಿ ನಾಟಿ ಪದ್ಧತಿಯ ಮೂಲಕ ಬೆಳೆಯಲಾಗುವ ಪ್ರಮುಖ ವಾಣಿಜ್ಯ ತರಕಾರಿ ಬೆಳೆ.',
        'hi': 'नर्सरी पौध रोपाई द्वारा उगाई जाने वाली प्रमुख उच्च मूल्य सोलेनेसी सब्जी फसल।'
    },
    'potato': {
        'en': 'Starch-dense tuber crop requiring balanced soil nutrition and systematic ridge formation.',
        'kn': 'ಉತ್ತಮ ಗೆಡ್ಡೆ ಕಟ್ಟಲು ಸಮತೋಲಿತ ಮಣ್ಣಿನ ಪೋಷಕಾಂಶ ಮತ್ತು ಏರಿ ಪದ್ಧತಿ ಅಗತ್ಯವಿರುವ ಪ್ರಮುಖ ಆಹಾರ ಬೆಳೆ.',
        'hi': 'कंदों के उचित विकास के लिए संतुलित मृदा पोषण और मेड़ चढ़ाने की आवश्यकता वाली प्रमुख स्टार्च फसल।'
    },
    'onion': {
        'en': 'High-value bulb vegetable requiring fertile, well-aerated sandy loam soils for uniform bulbs.',
        'kn': 'ಏಕರೂಪದ ಗಾತ್ರದ ಈರುಳ್ಳಿ ಪಡೆಯಲು ಫಲವತ್ತಾದ ಹಾಗೂ ನೀರು ಸರಾಗವಾಗಿ ಹರಿಯುವ ಮರಳು ಮಿಶ್ರಿತ ಗೋಡು ಮಣ್ಣು ಪ್ರಶಸ್ತ.',
        'hi': 'एकसमान कंद आकार के लिए उपजाऊ और उचित जल निकासी वाली बलुई दोमट मिट्टी वाली उच्च मूल्य फसल।'
    },
    'pomegranate': {
        'en': 'Commercial fruit crop cultivated for nutrient-dense arils, responsive to systematic canopy training.',
        'kn': 'ವ್ಯವಸ್ಥಿತ ರೆಂಬೆ ಕತ್ತರಿಸುವಿಕೆಗೆ ಸ್ಪಂದಿಸುವ ಮತ್ತು ಅಧಿಕ ಮಾರುಕಟ್ಟೆ ಮೌಲ್ಯ ಹೊಂದಿರುವ ಪ್ರಮುಖ ಹಣ್ಣಿನ ಬೆಳೆ.',
        'hi': 'उचित कटाई-छंटाई प्रबंधन और समृद्ध दानों के लिए उगाई जाने वाली उच्च व्यावसायिक फल फसल।'
    },
    'grapes': {
        'en': 'Commercial berry crop trained on trellis systems, responsive to vine pruning and balanced nutrition.',
        'kn': 'ಪಂದಲ್ ಅಥವಾ ಟ್ರೆಲ್ಲಿಸ್ ಪದ್ಧತಿಯಲ್ಲಿ ಬೆಳೆಯಲಾಗುವ ಮತ್ತು ಸೂಕ್ತ ಕವಲು ಕತ್ತರಿಸುವಿಕೆಗೆ ಸ್ಪಂದಿಸುವ ಪ್ರಮುಖ ವಾಣಿಜ್ಯ ಬೆಳೆ.',
        'hi': 'पंडाल प्रणाली पर उगाई जाने वाली और नियमित छंटाई तथा संतुलित पोषण के प्रति संवेदनशील व्यावसायिक फसल।'
    },
    'banana': {
        'en': 'Heavy-feeding fruit crop requiring substantial potassium nutrition and organic mulching.',
        'kn': 'ಭಾರವಾದ ಗೊನೆ ಕಟ್ಟಲು ಅಧಿಕ ಪೊಟ್ಯಾಷ್ ಪೋಷಕಾಂಶ ಮತ್ತು ಸಾವಯವ ಹೊದಿಕೆ ಅಗತ್ಯವಿರುವ ಪ್ರಮುಖ ಹಣ್ಣಿನ ಬೆಳೆ.',
        'hi': 'भारी गुच्छे प्राप्त करने के लिए उच्च पोटाश पोषण और जैविक मल्चिंग की आवश्यकता वाली प्रमुख फल फसल।'
    },
    'mango': {
        'en': 'Perennial orchard fruit crop responsive to balanced nutrition and post-bloom canopy management.',
        'kn': 'ಸಮತೋಲಿತ ಪೋಷಕಾಂಶ ಮತ್ತು ಹೂವಿನ ನಂತರದ ರೆಂಬೆ ನಿರ್ವಹಣೆಗೆ ಸ್ಪಂದಿಸುವ ಪ್ರಮುಖ ಸಾಂಪ್ರದಾಯಿಕ ಹಣ್ಣಿನ ಬೆಳೆ.',
        'hi': 'संतुलित पोषण और पुष्पन के बाद उचित छत्र प्रबंधन के अनुकूल प्रमुख फल फसल।'
    },
    'coffee': {
        'en': 'Shade-grown plantation crop with dual Arabica and Robusta cultivars under multi-tier forest canopies.',
        'kn': 'ಬಹುಹಂತದ ನೆರಳಿನ ಮರಗಳ ಅಡಿಯಲ್ಲಿ ಅರೇಬಿಕಾ ಮತ್ತು ರೋಬಸ್ಟಾ ತಳಿಗಳೊಂದಿಗೆ ಬೆಳೆಯಲಾಗುವ ತೋಟಗಾರಿಕಾ ಬೆಳೆ.',
        'hi': 'बहु-स्तरीय छायादार वृक्षों के नीचे अरेबिका और रोबस्टा किस्मों के रूप में उगाई जाने वाली प्रमुख बागवानी फसल।'
    },
    'coconut': {
        'en': 'Perennial palm yielding timber, coir fiber, and nutrient-rich copra under systematic basin management.',
        'kn': 'ಕಟ್ಟೆ ನಿರ್ವಹಣೆ ಮತ್ತು ಸಮತೋಲಿತ ಪೋಷಕಾಂಶಗಳೊಂದಿಗೆ ಗರಿಷ್ಠ ಇಳುವರಿ ನೀಡುವ ಸದಾಹಸಿರು ಕಲ್ಪವೃಕ್ಷ ಬೆಳೆ.',
        'hi': 'नियमित थाला प्रबंधन और संतुलित पोषक तत्वों के साथ वर्षभर उपज देने वाला कल्पवृक्ष वृक्ष फसल।'
    },
    'pigeonpeas': {
        'en': 'Deep-rooting grain legume fixing nitrogen and producing protein-rich seeds for pulses.',
        'kn': 'ಆಳವಾದ ಬೇರು ವ್ಯವಸ್ಥೆ ಮತ್ತು ಸಾರಜನಕ ಸ್ಥಿರೀಕರಣದೊಂದಿಗೆ ಪ್ರೋಟೀನ್ ಯುಕ್ತ ಬೇಳೆ ನೀಡುವ ಪ್ರಮುಖ ಬೆಳೆ.',
        'hi': 'गहरी जड़ प्रणाली और नाइट्रोजन स्थिरीकरण के साथ प्रोटीन युक्त दाल प्रदान करने वाली प्रमुख दलहन फसल।'
    },
    'blackgram': {
        'en': 'Short-duration pulse crop that enriches soil through biological nitrogen fixation and leaf residue.',
        'kn': 'ಅಲ್ಪಾವಧಿಯಲ್ಲಿ ಕೊಯ್ಲಿಗೆ ಬರುವ ಹಾಗೂ ಸಾರಜನಕ ಸ್ಥಿರೀಕರಣದ ಮೂಲಕ ಭೂಮಿಯ ಫಲವತ್ತತೆ ಹೆಚ್ಚಿಸುವ ಪ್ರಮುಖ ಕಾಳು ಬೆಳೆ.',
        'hi': 'कम अवधि में पकने वाली दलहन जो जैविक नाइट्रोजन स्थिरीकरण द्वारा खेत की उर्वरा शक्ति को बढ़ाती है।'
    },
    'mungbean': {
        'en': 'Fast-maturing pulse legume that restores soil fertility through symbiotic nitrogen fixation.',
        'kn': 'ಶೀಘ್ರ ಕಟಾವಿಗೆ ಬರುವ ಮತ್ತು ಸಾರಜನಕ ಸ್ಥಿರೀಕರಿಸಿ ಭೂಮಿಯ ಸತ್ವವನ್ನು ಹೆಚ್ಚಿಸುವ ಪ್ರಮುಖ ಕಾಳು ಬೆಳೆ.',
        'hi': 'शीघ्र परिपक्व होने वाली दलहन जो सहजीवी नाइट्रोजन स्थिरीकरण द्वारा मृदा स्वास्थ्य में सुधार करती है।'
    },
    'watermelon': {
        'en': 'Trailing cucurbit vine cultivated for sweet fruit, responsive to raised beds and plastic mulching.',
        'kn': 'ಏರು ಮಡಿ ಮತ್ತು ಮಲ್ಚಿಂಗ್ ಪದ್ಧತಿಯಲ್ಲಿ ಅತ್ಯಧಿಕ ಇಳುವರಿ ನೀಡುವ ಜನಪ್ರಿಯ ಹಣ್ಣಿನ ಬೆಳೆ.',
        'hi': 'उठी हुई क्यारियों और मल्चिंग तकनीक पर बेहतर उपज देने वाली प्रमुख तरबूज फल बेल।'
    },
    'muskmelon': {
        'en': 'High-value cucurbit cultivated on raised beds with drip fertigation for uniform netting and flavor.',
        'kn': 'ಏಕರೂಪದ ಹಣ್ಣಿನ ಗಾತ್ರ ಮತ್ತು ಸುವಾಸನೆಗಾಗಿ ಹನಿ ನೀರಾವರಿ ಪದ್ಧತಿಯಲ್ಲಿ ಬೆಳೆಯಲಾಗುವ ವಾಣಿಜ್ಯ ಬೆಳೆ.',
        'hi': 'आकर्षक जालीदार छिलके और सुगंधित गूदे के लिए ड्रिप फर्टिगेशन विधि से उगाई जाने वाली उच्च मूल्य नकदी फसल।'
    },
    'papaya': {
        'en': 'Rapid-growing herbaceous fruit crop producing heavy fruit clusters along its central trunk axis.',
        'kn': 'ಕಾಂಡದ ಉದ್ದಕ್ಕೂ ಒತ್ತಾಗಿ ಹಣ್ಣಿನ ಗೊಂಚಲುಗಳನ್ನು ನೀಡುವ ಅಲ್ಪಾವಧಿಯ ಜನಪ್ರಿಯ ಹಣ್ಣಿನ ಬೆಳೆ.',
        'hi': 'मुख्य तने पर सघन फल गुच्छे प्रदान करने वाली तेजी से बढ़ने वाली प्रमुख फल फसल।'
    },
    'orange': {
        'en': 'Citrus fruit tree responsive to micro-nutrient foliar sprays and systematic pruning.',
        'kn': 'ಸೂಕ್ಷ್ಮ ಪೋಷಕಾಂಶಗಳ ಸಿಂಪಡಣೆ ಮತ್ತು ನಿಯಮಿತ ಕವಲು ಕತ್ತರಿಸುವಿಕೆಗೆ ಸ್ಪಂದಿಸುವ ಸಿಟ್ರಸ್ ಹಣ್ಣಿನ ಬೆಳೆ.',
        'hi': 'सूक्ष्म पोषक तत्वों के छिड़काव और नियमित छंटाई के प्रति संवेदनशील प्रमुख खट्टे फल की फसल।'
    },
    'apple': {
        'en': 'Deciduous pome fruit requiring dedicated rootstock management and spur-bearing canopy training.',
        'kn': 'ವ್ಯವಸ್ಥಿತ ಕವಲು ನಿರ್ವಹಣೆ ಮತ್ತು ಮೂಲಕಾಂಡದ ತಳಿಗಳಿಂದ ಉತ್ಕೃಷ್ಟ ಇಳುವರಿ ನೀಡುವ ಪೌಷ್ಟಿಕ ಹಣ್ಣಿನ ಬೆಳೆ.',
        'hi': 'उचित रूटस्टॉक प्रबंधन और सुनियोजित छत्र विकास के साथ उगाई जाने वाली प्रमुख शीतोष्ण फल फसल।'
    },
    'lentil': {
        'en': 'Protein-dense pulse crop suitable for sustainable crop rotations and balanced soil enhancement.',
        'kn': 'ಬೆಳೆ ಪರಿವರ್ತನೆಗೆ ಅತ್ಯಂತ ಸೂಕ್ತವಾದ ಮತ್ತು ಪ್ರೋಟೀನ್ ಭರಿತ ಸಾಂಪ್ರದಾಯಿಕ ಕಾಳು ಬೆಳೆ.',
        'hi': 'फसल चक्र के लिए अत्यंत उपयुक्त और प्रोटीन से भरपूर प्रमुख दलहनी फसल।'
    },
    'kidneybeans': {
        'en': 'Nutrient-demanding legume grown for high-protein culinary beans with upright bushy canopy.',
        'kn': 'ಅಧಿಕ ಪ್ರೋಟೀನ್ ಹೊಂದಿರುವ ಮತ್ತು ನೇರ ಪೊದೆಯಾಗಿ ಬೆಳೆಯುವ ಪ್ರಮುಖ ಪೌಷ್ಟಿಕ ಕಾಳು ಬೆಳೆ.',
        'hi': 'झाड़ीनुमा पौधों पर उच्च प्रोटीन युक्त फलियां प्रदान करने वाली पोषक दलहनी फसल।'
    },
    'mothbeans': {
        'en': 'Hardy sprawling legume crop cultivated for high-protein pulses and green livestock forage.',
        'kn': 'ಹೆಚ್ಚಿನ ಪ್ರೋಟೀನ್ ಭರಿತ ಕಾಳು ಮತ್ತು ಜಾನುವಾರುಗಳಿಗೆ ಪೌಷ್ಟಿಕ ಮೇವು ನೀಡುವ ಹರಡುವ ಜಾತಿಯ ಕಾಳು ಬೆಳೆ.',
        'hi': 'जमीन पर फैलने वाली दलहन जो उच्च प्रोटीन युक्त दाने और पशुओं के लिए हरा चारा प्रदान करती है।'
    },
    'wheat': {
        'en': 'Major cereal staple grown for high-energy carbohydrates, protein gluten content, and livestock fodder.',
        'kn': 'ಹೆಚ್ಚಿನ ಶಕ್ತಿ ಮತ್ತು ಪ್ರೋಟೀನ್ ಒದಗಿಸುವ ಹಾಗೂ ಪ್ರಮುಖ ಆಹಾರ ಭದ್ರತೆ ನೀಡುವ ಪ್ರಮುಖ ಧಾನ್ಯ ಬೆಳೆ.',
        'hi': 'ऊर्जा, ग्लूटेन प्रोटीन और पोषण सुरक्षा प्रदान करने वाली प्रमुख खाद्यान्न फसल।'
    },
    'fieldbeans': {
        'en': 'Traditional pulse with high biological nitrogen fixation and aromatic pod development.',
        'kn': 'ಸಾರಜನಕ ಸ್ಥಿರೀಕರಣ ಮತ್ತು ಉತ್ತಮ ಸುವಾಸನೆಯ ಕಾಯಿಗಳನ್ನು ಹೊಂದಿರುವ ಸಾಂಪ್ರದಾಯಿಕ ಬೇಳೆಕಾಳು ಬೆಳೆ.',
        'hi': 'उच्च जैविक नाइट्रोजन स्थिरीकरण और सुगंधित फलियों वाली पारंपरिक दलहनी फसल।'
    },
    'horsegram': {
        'en': 'Hardy, protein-dense traditional pulse widely cultivated across regional agricultural tracts.',
        'kn': 'ಕಡಿಮೆ ನೀರಿನ ಪ್ರದೇಶಗಳಲ್ಲಿ ಬೆಳೆಯಲಾಗುವ ಅತ್ಯಂತ ಪೌಷ್ಟಿಕ ಹಾಗೂ ಸಾಂಪ್ರದಾಯಿಕ ಕಾಳು ಬೆಳೆ.',
        'hi': 'कम पानी वाले क्षेत्रों में उगाई जाने वाली उच्च प्रोटीन युक्त पारंपरिक दलहन फसल।'
    },
    'vegetables': {
        'en': 'Intensive horticultural crops cultivated for essential minerals, dietary vitamins, and daily market harvest.',
        'kn': 'ದೈನಂದಿನ ಮಾರುಕಟ್ಟೆ ಮಾರಾಟ ಮತ್ತು ಪೌಷ್ಟಿಕಾಂಶಗಳಿಗಾಗಿ ಬೆಳೆಯಲಾಗುವ ತರಕಾರಿ ಬೆಳೆಗಳು.',
        'hi': 'नियमित दैनिक मंडी आपूर्ति और आवश्यक पोषक तत्वों के लिए उगाई जाने वाली सघन सब्जी फसलें।'
    },
    'flowers': {
        'en': 'Commercial floricultural crops cultivated for decorative loose blooms, garland making, and perfumery oils.',
        'kn': 'ಹೂಮಾಲೆ, ಅಲಂಕಾರಿಕ ಬಳಕೆ ಮತ್ತು ಸುವಾಸನಾ ತೈಲ ತಯಾರಿಕೆಗೆ ಬೆಳೆಯಲಾಗುವ ವಾಣಿಜ್ಯ ಪುಷ್ಪ ಕೃಷಿ ಬೆಳೆಗಳು.',
        'hi': 'सजावट, माला निर्माण और सुगंधित इत्र निष्कर्षण के लिए उगाई जाने वाली व्यावसायिक फूल फसलें।'
    },
    'fodder': {
        'en': 'Fast-growing biomass crops cultivated to provide nutrient-balanced green forage for dairy livestock.',
        'kn': 'ಹೈನುಗಾರಿಕೆ ಜಾನುವಾರುಗಳಿಗೆ ಸಮತೋಲಿತ ಪೌಷ್ಟಿಕ ಹಸಿರು ಮೇವು ಒದಗಿಸುವ ಅಧಿಕ ಇಳುವರಿಯ ಮೇವಿನ ಬೆಳೆಗಳು.',
        'hi': 'दुधारू पशुओं के लिए संतुलित हरा चारा उपलब्ध कराने वाली तेजी से बढ़ने वाली बायोमास चारा फसलें।'
    },
    'turmeric': {
        'en': 'Valuable spice crop yielding high-curcumin rhizomes, responsive to rich organic matter and ridge planting.',
        'kn': 'ಹೆಚ್ಚಿನ ಕುರ್ಕುಮಿನ್ ಅಂಶ ಹೊಂದಿರುವ ಮತ್ತು ಮಣ್ಣಿನಲ್ಲಿ ಸಾವಯವ ಗೊಬ್ಬರ ನಿರ್ವಹಣೆಗೆ ಸ್ಪಂದಿಸುವ ಪ್ರಮುಖ ಸಾಂಬಾರ ಬೆಳೆ.',
        'hi': 'उच्च करक्यूमिन युक्त प्रकंद देने वाली और समृद्ध जैविक खाद प्रबंधन के अनुकूल प्रमुख मसाला फसल।'
    },
    'cowpea': {
        'en': 'Versatile pulse grown for fresh green vegetable pods as well as harvested grain pulses.',
        'kn': 'ಹಸಿರು ಕಾಯಿ ತರಕಾರಿ ಹಾಗೂ ಒಣ ಕಾಳು ಎರಡಕ್ಕೂ ಬೆಳೆಯಲಾಗುವ ಬಹುಪಯೋಗಿ ಸಾಂಪ್ರದಾಯಿಕ ಕಾಳು ಬೆಳೆ.',
        'hi': 'हरी फलियों की सब्जी और सूखे प्रोटीन युक्त दानों के लिए उगाई जाने वाली बहुमुखी दलहनी फसल।'
    },
    'chilli': {
        'en': 'Commercial spice and vegetable crop cultivated for pungent capsaicin and vibrant oleoresin pigments.',
        'kn': 'ಖಾರ ಮತ್ತು ನೈಸರ್ಗಿಕ ಕೆಂಪು ಬಣ್ಣದ ಸಾರಕ್ಕಾಗಿ ಬೆಳೆಯಲಾಗುವ ಪ್ರಮುಖ ವಾಣಿಜ್ಯ ಸಾಂಬಾರ ಬೆಳೆ.',
        'hi': 'तीखे कैप्साइसिन और आकर्षक प्राकृतिक लाल रंग के लिए उगाई जाने वाली प्रमुख व्यावसायिक मसाला फसल।'
    },
    'ginger': {
        'en': 'Aromatic spice crop producing essential oil-rich rhizomes, requiring well-drained, organically rich loams.',
        'kn': 'ಉತ್ತಮ ಸುವಾಸನೆ ಮತ್ತು ಔಷಧೀಯ ಗುಣವುಳ್ಳ ಶುಂಠಿ ಬೆಳೆಯಲು ನೀರು ಬಸಿದು ಹೋಗುವ ಗೋಡು ಮಣ್ಣು ಸೂಕ್ತ.',
        'hi': 'सुगंधित आवश्यक तेलों से भरपूर कंद देने वाली मसाला फसल, जिसे जल-निकासी वाली उपजाऊ दोमट मिट्टी चाहिए।'
    },
    'tobacco': {
        'en': 'Commercial cash crop grown for cured leaf production, responsive to balanced potash fertilization.',
        'kn': 'ಉತ್ತಮ ಎಲೆಗಳ ಇಳುವರಿಗಾಗಿ ಪೊಟ್ಯಾಷ್ ಪೋಷಕಾಂಶಗಳ ಸಮತೋಲಿತ ನಿರ್ವಹಣೆಗೆ ಸ್ಪಂದಿಸುವ ವಾಣಿಜ್ಯ ಬೆಳೆ.',
        'hi': 'गुणवत्तापूर्ण पत्तियों के उत्पादन के लिए संतुलित पोटाश प्रबंधन के अनुकूल प्रमुख नकदी फसल।'
    },
    'bajra': {
        'en': 'Nutrient-rich coarse cereal producing iron-rich grain heads and green forage for livestock.',
        'kn': 'ಹೆಚ್ಚಿನ ಕಬ್ಬಿಣದ ಅಂಶ ಮತ್ತು ಜಾನುವಾರುಗಳಿಗೆ ಗುಣಮಟ್ಟದ ಮೇವು ನೀಡುವ ಪ್ರಮುಖ ಪೌಷ್ಟಿಕ ಸಿರಿಧಾನ್ಯ ಬೆಳೆ.',
        'hi': 'लौह तत्व से भरपूर दाने और पशुओं के लिए पौष्टिक हरा चारा प्रदान करने वाला प्रमुख पोषक मोटा अनाज।'
    },
    'pulses': {
        'en': 'Essential grain legumes enriching soils through atmospheric nitrogen fixation and crop rotations.',
        'kn': 'ಸಾರಜನಕ ಸ್ಥಿರೀಕರಣದ ಮೂಲಕ ಮಣ್ಣನ್ನು ಸಮೃದ್ಧಗೊಳಿಸುವ ಮತ್ತು ಸಮತೋಲಿತ ಆಹಾರ ಒದಗಿಸುವ ಪ್ರಮುಖ ಕಾಳು ಬೆಳೆಗಳು.',
        'hi': 'वायुमंडलीय नाइट्रोजन स्थिरीकरण और फसल चक्र द्वारा मिट्टी को समृद्ध बनाने वाली प्रमुख दलहनी फसलें।'
    }
}

matched = 0
for k, v in facts.items():
    m = pattern.findall(v['en'])
    if m:
        print(f"MATCH in {k}: {m} -> {v['en']}")
        matched += 1

print(f"Total crops checked: {len(facts)}, Banned matches: {matched}")
