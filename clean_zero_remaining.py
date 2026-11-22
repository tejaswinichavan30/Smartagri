# Final clean script for remaining lines
with open('translations.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("Dry root rot → Seed treatment with Carbendazim", "Dry root rot → Seed treatment with Trichoderma viride (4g/kg)")
text = text.replace("Pod borer → Spray Neem oil 1500 ppm or Spinosad", "Pod borer → Spray Neem oil 1500 ppm and install pheromone traps (5/acre)")
text = text.replace("Pod borer → Spray Chlorpyrifos 20 EC @ 2 ml/L", "Pod borer → Install light traps and apply Trichogramma cards")
text = text.replace("Rhizome rot → Drench with Metalaxyl + Mancozeb @ 2.5 g/L", "Rhizome rot → Drench with Trichoderma viride and 1% Bordeaux mixture")
text = text.replace("Soft rot / Rhizome rot → Drench with Copper Oxychloride 50 WP @ 3 g/L or Trichoderma", "Soft rot / Rhizome rot → Drench with Trichoderma viride and 1% Bordeaux mixture")
text = text.replace("Downy mildew → Metalaxyl seed treatment", "Downy mildew → Seed treatment with Trichoderma harzianum (4g/kg seed)")
text = text.replace("ಕಾಪರ್ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ ದ್ರಾವಣ", "ಟ್ರೈಕೋಡರ್ಮಾ ಮತ್ತು ಶೇ. 1ರ ಬೋರ್ಡೋ ದ್ರಾವಣ")
text = text.replace("ಮೆಟಲಾಕ್ಸಿಲ್ ಬೀಜೋಪಚಾರ", "ಟ್ರೈಕೋಡರ್ಮಾ ಬೀಜೋಪಚಾರ")
text = text.replace("ಮೆಟಲಾಕ್ಸಿಲ್ +", "ಟ್ರೈಕೋಡರ್ಮಾ +")
text = text.replace("ಮಾರ್ಚ್ - ಜೂನ್ (ಕಚ್ಚಾ ಗೋಡಂಬಿ ಕಟಾವು ಸಮಯ)", "ಮಾರ್ಚ್ - ಜೂನ್ (ಕಚ್ಚಾ ಗೋಡಂಬಿ ಕಟಾವು ಸಮಯ)")

with open('translations.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Finished zero-remaining sanitization!")
