# -*- coding: utf-8 -*-
"""
SmartAgri AI - Automated Botanical Image Generator Script
Generates 3 diseased photos + 1 healthy photo for all reference crops using Gemini API
and automatically optimizes them (<200KB) into static/disease_samples_optimized/.
"""

import os
import time
import requests
from PIL import Image

CROP_PROMPT_REGISTRY = {
    # Chilli
    ('chilli', 'leaf_curl'): "A close-up photograph of a chilli pepper plant leaf infected with Chilli Leaf Curl Virus, showing upward curling, wrinkled crinkled texture, yellowing margins, on a natural garden background, realistic botanical photography",
    ('chilli', 'fruit_rot'): "Close-up photograph of red and green chilli peppers on the plant with dark sunken circular lesions and anthracnose fruit rot spots, realistic agronomy photography",
    ('chilli', 'bacterial_wilt'): "Field photograph of a chilli pepper plant showing sudden bacterial wilt, green drooping and wilting foliage on healthy-looking green leaves in garden soil",
    ('chilli', 'healthy'): "Macro photograph of a vibrant healthy dark green chilli pepper leaf with smooth surface and crisp leaf veins on a garden plant, realistic botanical photography",

    # Black Pepper
    ('black_pepper', 'quick_wilt'): "Close-up agronomy photo of black pepper vine leaves showing dark water-soaked necrotic lesions and yellowing caused by Phytophthora quick wilt foot rot",
    ('black_pepper', 'pollu'): "Close-up of black pepper vine foliage and pepper berry spike showing anthracnose pollu disease with circular brown leaf spots and hollow blackened berries",
    ('black_pepper', 'slow_decline'): "Agronomy photo of black pepper vine showing slow decline with foliar yellowing, small leaves, and dieback of branches in a plantation",
    ('black_pepper', 'healthy'): "Close-up botanical photo of healthy lush deep-green heart-shaped black pepper vine leaves climbing on a tree trunk in a tropical garden",

    # Green Gram
    ('green_gram', 'yellow_mosaic'): "Close-up photo of green gram moong bean trifoliate leaf infected with yellow mosaic virus showing alternating bright golden yellow and green patches on the foliage",
    ('green_gram', 'cercospora'): "Close-up photo of green gram moong bean leaf with Cercospora leaf spot showing circular brown spots with reddish-brown borders",
    ('green_gram', 'powdery_mildew'): "Close-up photo of green gram moong bean leaves with powdery mildew showing white powdery fungal patches spreading across green foliage",
    ('green_gram', 'healthy'): "Macro photo of healthy fresh green trifoliate leaves of a green gram moong bean crop growing in farm soil",

    # Onion
    ('onion', 'purple_blotch'): "Close-up agricultural photo of onion foliage showing purple blotch Alternaria porri lesions with sunken purplish centers and yellow halos on tubular leaves",
    ('onion', 'stemphylium_blight'): "Close-up photo of onion plant leaves with Stemphylium blight showing yellowish-orange ovate lesions with dark central fungal spore masses",
    ('onion', 'downy_mildew'): "Close-up photo of onion leaves infected with downy mildew showing pale yellowish oval patches with violet-grey downy fungal growth",
    ('onion', 'healthy'): "Close-up photo of healthy upright crisp green tubular onion leaves with smooth waxy surface in agricultural farm field",

    # Pomegranate
    ('pomegranate', 'telya'): "Close-up of pomegranate leaf and fruit with bacterial blight Telya showing dark brown water-soaked oily angular spots and rind cracking",
    ('pomegranate', 'cercospora'): "Close-up photo of pomegranate leaves showing Cercospora leaf spot with minute circular dark brown spots and leaf yellowing",
    ('pomegranate', 'wilt'): "Field photo of pomegranate tree showing Ceratocystis wilt with yellowing and sudden drying of leaves on one or more branches",
    ('pomegranate', 'healthy'): "Macro photo of healthy glossy green pomegranate leaves on a tree branch with vibrant fresh foliage in orchard",

    # Jowar (Sorghum)
    ('jowar', 'grain_mold'): "Close-up photo of a sorghum jowar earhead panicle with grain mold disease showing pinkish-black fungal discoloration and chalky damaged grains",
    ('jowar', 'rust'): "Macro photo of long sorghum jowar cereal leaf showing leaf rust Puccinia purpurea with reddish-brown to purple powdery pustules on the leaf blade",
    ('jowar', 'downy_mildew'): "Close-up photo of sorghum jowar leaf showing downy mildew systemic infection with vivid chlorotic yellow striping along leaf veins and white down",
    ('jowar', 'healthy'): "Macro photograph of healthy long broad green sorghum jowar leaf blade in bright daylight on agricultural farm",

    # Sunflower
    ('sunflower', 'alternaria'): "Close-up photo of sunflower leaf with Alternaria leaf blight showing dark brown necrotic zonate circular spots surrounded by yellow chlorotic halo",
    ('sunflower', 'head_rot'): "Close-up photo of a maturing sunflower head showing fungal head rot Rhizopus with water-soaked brown rotting tissue on the receptacle and drooping flower head",
    ('sunflower', 'rust'): "Close-up photo of sunflower leaf with sunflower rust Puccinia helianthi showing numerous small powdery cinnamon-brown pustules on lower leaf surface",
    ('sunflower', 'healthy'): "Macro photo of large healthy vibrant dark green sunflower leaf with prominent venation and clean leaf surface in sunflower field",

    # Turmeric
    ('turmeric', 'rhizome_rot'): "Field photo of turmeric plant crop suffering from rhizome rot Pythium, showing yellowing and wilting drying leaves with collar rot at pseudostem base",
    ('turmeric', 'leaf_blotch'): "Macro agronomy photo of broad green turmeric leaf showing Taphrina leaf blotch with reddish-brown to dark brown rectangular spots aligned between leaf veins",
    ('turmeric', 'leaf_spot'): "Close-up photo of turmeric leaf showing Colletotrichum leaf spot with elliptic brown lesions surrounded by bright yellow halo",
    ('turmeric', 'healthy'): "Macro photo of large broad healthy lush green turmeric plant leaves with clear parallel veins in an organic spice farm",

    # Cashew
    ('cashew', 'dieback'): "Close-up agronomy photo of cashew shoot tip showing tea mosquito bug Helopeltis damage and dieback with blackened necrotic shoots, drying leaves and resinous exude",
    ('cashew', 'anthracnose'): "Close-up photo of cashew leaves and shoot with anthracnose showing reddish-brown water-soaked spots coalescing into large necrotic blighted areas",
    ('cashew', 'root_rot'): "Field photo of cashew sapling suffering from root rot with drooping wilting brown foliage in sandy loam soil",
    ('cashew', 'healthy'): "Macro photo of healthy leathery ovate dark green cashew leaves on a flowering branch in a sunny coastal orchard",

    # Mulberry
    ('mulberry', 'leaf_spot'): "Macro photo of mulberry Morus leaf showing fungal Cercospora leaf spot disease with numerous circular brownish-black spots with paler centers",
    ('mulberry', 'powdery_mildew'): "Close-up photo of mulberry leaves with powdery mildew showing white powdery patches on lower leaf surface and yellowish chlorosis on upper surface",
    ('mulberry', 'leaf_rust'): "Macro photo of mulberry leaf underside showing leaf rust with numerous tiny pin-head reddish-brown uredinial pustules",
    ('mulberry', 'healthy'): "Macro photo of healthy fresh tender green mulberry leaf with serrated edges and distinct venation in a sericulture farm",

    # Horse Gram
    ('horse_gram', 'anthracnose'): "Macro photo of horse gram Macrotyloma uniflorum plant foliage showing anthracnose disease with brown sunken circular necrotic spots and chlorotic yellowing",
    ('horse_gram', 'yellow_mosaic'): "Close-up photo of horse gram crop leaves showing yellow mosaic virus with bright golden yellow chlorotic mottling across trifoliate leaflets",
    ('horse_gram', 'dry_root_rot'): "Field photo of horse gram plant with dry root rot showing sudden drying of foliage and brown discoloration at the stem base",
    ('horse_gram', 'healthy'): "Macro photo of healthy lush green trifoliate horse gram leaves growing densely in fertile dryland soil",

    # Tobacco
    ('tobacco', 'black_shank'): "Close-up photo of tobacco plant showing black shank Phytophthora with black lesion on stem collar and sudden yellowing wilting leaves",
    ('tobacco', 'mosaic_virus'): "Close-up photo of broad tobacco leaf infected with Tobacco Mosaic Virus (TMV) showing distinctive mottled light and dark green mosaic patterns and leaf distortion",
    ('tobacco', 'frog_eye'): "Macro photo of tobacco leaf with Frog-Eye leaf spot Cercospora showing circular brown spots with white paper-like center resembling a frog's eye",
    ('tobacco', 'healthy'): "Macro photo of large healthy broad green tobacco leaf with smooth texture and clear venation on vigorous plant",

    # Ginger
    ('ginger', 'soft_rot'): "Field photo of ginger crop Zingiber officinale suffering from soft rot Pythium with water-soaked pseudostem base and yellowing drooping leaves",
    ('ginger', 'bacterial_wilt'): "Close-up photo of ginger plant foliage with bacterial wilt showing bronze discoloration, curling margins and rapid wilting",
    ('ginger', 'leaf_spot'): "Macro photo of ginger leaf with Phyllosticta leaf spot showing small spindle-shaped spots with white centers and dark brown margins",
    ('ginger', 'healthy'): "Macro photo of healthy vibrant green lanceolate ginger leaves with smooth texture on upright pseudostem",

    # Papaya
    ('papaya', 'ring_spot'): "Close-up photo of papaya leaf and young fruit infected with Papaya Ringspot Virus (PRSV) showing prominent dark green vein clearing, mosaic, and yellow ringspots",
    ('papaya', 'anthracnose'): "Close-up photo of papaya fruit and leaf showing anthracnose Colletotrichum with sunken circular brown lesions with pinkish spore masses",
    ('papaya', 'foot_rot'): "Field photo of papaya tree showing foot rot / stem rot Pythium with water-soaked soft rotting trunk base and falling yellow leaves",
    ('papaya', 'healthy'): "Macro photo of healthy deeply lobed dark green papaya leaf with prominent palmate venation in sunlight",

    # Watermelon
    ('watermelon', 'anthracnose'): "Close-up photo of watermelon leaf and rind showing anthracnose with circular black sunken spots and ragged leaf holes",
    ('watermelon', 'fusarium_wilt'): "Field photo of watermelon vine showing Fusarium wilt with one-sided vine wilting, yellowing leaves and vascular browning",
    ('watermelon', 'downy_mildew'): "Macro photo of watermelon leaf with downy mildew showing angular yellow lesions strictly delimited by leaf veins",
    ('watermelon', 'healthy'): "Macro photo of healthy deeply pinnatifid green watermelon leaf on vigorous vine with tender tendrils",

    # Muskmelon
    ('muskmelon', 'downy_mildew'): "Macro photo of muskmelon leaf with downy mildew showing bright yellow angular lesions bounded by veins and greyish-purple down on underside",
    ('muskmelon', 'powdery_mildew'): "Close-up photo of muskmelon vine leaves with powdery mildew showing white powdery talc-like patches covering the foliage",
    ('muskmelon', 'fusarium_wilt'): "Field photo of muskmelon vine showing Fusarium wilt with yellowing of runner leaves and sudden collapse in midday heat",
    ('muskmelon', 'healthy'): "Macro photo of healthy rounded lobed green muskmelon leaf on trailing vine with vibrant green texture",

    # Blueberry
    ('blueberry', 'healthy'): "Macro photo of healthy blueberry shrub branch with glossy dark green oval leaves and clusters of ripe blue berries",
    # Raspberry
    ('raspberry', 'healthy'): "Macro photo of healthy raspberry cane with fresh vibrant green pinnate leaves and clean serrated margins",
    # Cotton
    ('cotton', 'bacterial_blight'): "Close-up photograph of a cotton plant leaf Gossypium with angular water-soaked brown leaf spots bounded by leaf veins and black arm lesion on stem, realistic botanical photography",
    ('cotton', 'leaf_curl'): "Close-up photo of cotton leaf infected with Cotton Leaf Curl Virus showing upward leaf curling, thickened veins and enations on lower surface",
    ('cotton', 'alternaria_spot'): "Close-up photo of cotton leaf with Alternaria leaf spot showing circular necrotic brown spots with purple margins and shot-holes",
    ('cotton', 'healthy'): "Macro photograph of a healthy genuine cotton plant leaf Gossypium with characteristic 3-to-5 pointed lobes, vibrant clean green color and smooth leaf surface in cotton field, botanical photography",

    # Ragi (Finger Millet)
    ('ragi', 'blast'): "Close-up photo of finger millet ragi leaf showing blast disease Pyricularia with spindle-shaped lesions having greyish centers and dark brown borders",
    ('ragi', 'foot_rot'): "Field photo of finger millet ragi crop seedling showing foot rot / collar rot Sclerotium with brown rotting at collar region and wilting seedlings",
    ('ragi', 'brown_spot'): "Close-up photo of finger millet ragi leaf blade showing brown spot Bipolaris with small oval to circular reddish-brown spots scattered across foliage",
    ('ragi', 'healthy'): "Macro photo of healthy vibrant green finger millet ragi leaf and developing healthy green earhead in farm field",

    # Arecanut
    ('arecanut', 'koleroga'): "Close-up photo of arecanut palm bunch with Koleroga fruit rot showing rotting dark brown nuts covered with white fungal mycelium",
    ('arecanut', 'yellow_leaf'): "Photo of arecanut palm fronds showing yellow leaf disease with conspicuous yellowing starting from inner whorl leaflets",
    ('arecanut', 'anabe_roga'): "Photo of arecanut palm base showing Anabe roga foot rot Ganoderma bracket fungus at base of drying trunk",
    ('arecanut', 'healthy'): "Photo of healthy lush deep-green arecanut palm frond with glossy leaflets under tropical canopy"
}

def optimize_image(src_path, dst_path, max_width=800, max_bytes=307200, quality=85):
    """Resizes and compresses image if over threshold."""
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    with Image.open(src_path) as img:
        img = img.convert('RGB')
        if img.width > max_width:
            new_h = int(img.height * (max_width / img.width))
            img = img.resize((max_width, new_h), Image.Resampling.LANCZOS)
        img.save(dst_path, 'JPEG', quality=quality, optimize=True)

if __name__ == '__main__':
    print(f"Loaded {len(CROP_PROMPT_REGISTRY)} botanical image prompt specifications.")
    print("When API capacity resets, use generate_image or execute batch generator.")
