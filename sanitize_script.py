# Script to sanitize all chemical pesticide names across translations.py
import re

with open('translations.py', 'r', encoding='utf-8') as f:
    text = f.read()

chems_list = [
    'carbofuran', 'carbosulfan', 'monocrotophos', 'phorate', 'methyl parathion', 'endosulfan', 'paraquat',
    'tricyclazole', 'buprofezin', 'carbendazim', 'mancozeb', 'chlorpyrifos', 'imidacloprid', 'thiamethoxam',
    'triazophos', 'quinalphos', 'dimethoate', 'hexaconazole', 'propiconazole', 'streptocycline', 'copper oxychloride',
    'captan', 'metalaxyl', 'spinosad', 'spinetoram', 'chlorothalonil', 'tebuconazole', 'azoxystrobin', 'thiram',
    'fipronil', 'profenofos', 'carbaryl', 'cymoxanil', 'oxytetracycline', 'dinocap', 'difenoconazole', 'kasugamycin',
    'iprodione', 'copper hydroxide', 'emamectin benzoate', 'deltamethrin', 'lambdacyhalothrin', 'malathion',
    'indoxacarb', 'fipronil', 'bordeaux mixture'
]

# Clean CROP_TRANSLATIONS pests
# Pattern matches any sentence starting with pest name -> IPM method with chemical
lines = text.split('\n')
new_lines = []

for line in lines:
    l_strip = line.strip()
    
    # Check if this line is in CROP_TRANSLATIONS pests list
    if (l_strip.startswith("'") or l_strip.startswith('"')) and any(arr in l_strip for arr in ['→', '->', 'Scouting:', 'Monitoring:']):
        # If it mentions any chemical, clean it
        for chem in chems_list:
            if chem in line.lower():
                # Replace chemical parts with bio-control / KVK advice
                line = re.sub(r'Use\s+[A-Za-z0-9\s\.\@\%]+(?:spray|granules|fungicide|insecticide|soil treatment|soil drench|seed treatment)?', 'Apply 5% neem oil / bio-agents; consult your local KVK for verified options', line, flags=re.IGNORECASE)
                line = re.sub(r'\([A-Za-z0-9\s\.\@\%\/\-\+\,]+\)', '', line)
                line = re.sub(r';\s*consult your KVK[^\'\"]*', '. Consult your local KVK for label-claim verified treatments.', line, flags=re.IGNORECASE)
                line = re.sub(r'\s{2,}', ' ', line)
                break

    new_lines.append(line)

sanitized_text = '\n'.join(new_lines)

with open('translations.py', 'w', encoding='utf-8') as f:
    f.write(sanitized_text)

print("Finished second pass sanitization!")
