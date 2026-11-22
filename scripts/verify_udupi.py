import sys
sys.path.insert(0, '.')
from app import app, compute_price_forecast

client = app.test_client()
res = client.post('/predict_crop', data={
    'district': 'Udupi', 'nitrogen': '65', 'phosphorus': '45', 'potassium': '25',
    'ph': '5.8', 'rainfall': '120', 'season': 'auto', 'lang': 'en'
}, headers={'Accept': 'application/json'})

data = res.get_json()
print("Top crops count:", len(data.get('top_crops', [])))
for c in data.get('top_crops', []):
    print("Crop:", c.get('name'))
    print("  Key:", c.get('crop_key'))
    print("  Score:", c.get('score'))
    print("  Reason:", c.get('reason'))
    print("  Sowing:", c.get('sowing_en'))
    print("  Harvest:", c.get('harvest_en'))

p_cowpea = compute_price_forecast('Cowpea', 'Udupi', month=11, year=2026)
print("\nPrice Cowpea:")
print("  price_en:", p_cowpea['price_en'])
print("  forecast_available:", p_cowpea['forecast_available'])
