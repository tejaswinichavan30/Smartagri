import pandas as pd
import numpy as np

# Load existing price data
df = pd.read_csv("Datasets/Agriculture_price_dataset.csv")

print("Current shape:", df.shape)
print("Current crops:", df['Commodity'].unique())

np.random.seed(42)

# Karnataka states and markets for new crops
states_markets = [
    ('Karnataka', 'Belagavi', 'Belagavi'),
    ('Karnataka', 'Kolar', 'Kolar'),
    ('Karnataka', 'Mysuru', 'Mysuru'),
    ('Karnataka', 'Dharwad', 'Dharwad'),
    ('Karnataka', 'Hassan', 'Hassan'),
    ('Maharashtra', 'pune', 'Pune'),
    ('Maharashtra', 'nashik', 'Nashik'),
    ('Uttar Pradesh', 'lucknow', 'Lucknow'),
    ('Punjab', 'ludhiana', 'Ludhiana'),
    ('Andhra Pradesh', 'kurnool', 'Kurnool'),
]

dates = pd.date_range(start='2020-01-01', end='2024-12-31', freq='W')

def generate_crop_data(commodity, min_price_range, max_price_range, modal_price_range, variety='Common', grade='FAQ'):
    rows = []
    for date in dates:
        for state, district, market in states_markets:
            min_p   = np.random.uniform(*min_price_range)
            max_p   = min_p + np.random.uniform(100, 500)
            modal_p = np.random.uniform(min_p, max_p)
            rows.append({
                'STATE':         state,
                'District Name': district,
                'Market Name':   market,
                'Commodity':     commodity,
                'Variety':       variety,
                'Grade':         grade,
                'Min_Price':     round(min_p, 2),
                'Max_Price':     round(max_p, 2),
                'Modal_Price':   round(modal_p, 2),
                'Price Date':    date.strftime('%d/%m/%Y')
            })
    return pd.DataFrame(rows)

# ── Generate data for missing crops ──────────────────────────────────────────
print("\nGenerating Maize data...")
maize = generate_crop_data(
    commodity='Maize',
    min_price_range=(1200, 2000),
    max_price_range=(1500, 2500),
    modal_price_range=(1300, 2200),
    variety='Yellow'
)

print("Generating Grapes data...")
grapes = generate_crop_data(
    commodity='Grapes',
    min_price_range=(2000, 4000),
    max_price_range=(2500, 5000),
    modal_price_range=(2200, 4500),
    variety='Black'
)

print("Generating Apple data...")
apple = generate_crop_data(
    commodity='Apple',
    min_price_range=(3000, 6000),
    max_price_range=(3500, 7000),
    modal_price_range=(3200, 6500),
    variety='Red Delicious'
)

print("Generating Tomato extra data...")
tomato_extra = generate_crop_data(
    commodity='Tomato',
    min_price_range=(500, 2000),
    max_price_range=(800, 2500),
    modal_price_range=(600, 2200),
    variety='Hybrid'
)

print("Generating Potato extra data...")
potato_extra = generate_crop_data(
    commodity='Potato',
    min_price_range=(600, 1500),
    max_price_range=(800, 2000),
    modal_price_range=(700, 1800),
    variety='Jyoti'
)

print("Generating Rice extra data...")
rice_extra = generate_crop_data(
    commodity='Rice',
    min_price_range=(1800, 3000),
    max_price_range=(2000, 3500),
    modal_price_range=(1900, 3200),
    variety='Basmati'
)

print("Generating Mango data...")
mango = generate_crop_data(
    commodity='Mango',
    min_price_range=(2000, 5000),
    max_price_range=(2500, 6000),
    modal_price_range=(2200, 5500),
    variety='Alphonso'
)

print("Generating Banana data...")
banana = generate_crop_data(
    commodity='Banana',
    min_price_range=(800, 2000),
    max_price_range=(1000, 2500),
    modal_price_range=(900, 2200),
    variety='Robusta'
)

print("Generating Cotton data...")
cotton = generate_crop_data(
    commodity='Cotton',
    min_price_range=(4000, 7000),
    max_price_range=(4500, 8000),
    modal_price_range=(4200, 7500),
    variety='Medium Staple'
)

print("Generating Coconut data...")
coconut = generate_crop_data(
    commodity='Coconut',
    min_price_range=(1500, 3000),
    max_price_range=(1800, 3500),
    modal_price_range=(1600, 3200),
    variety='Tall'
)

# ── Combine all data ──────────────────────────────────────────────────────────
df_new = pd.concat([
    df,
    maize, grapes, apple,
    tomato_extra, potato_extra, rice_extra,
    mango, banana, cotton, coconut
], ignore_index=True)

print(f"\nNew shape: {df_new.shape}")
print("New crops:", df_new['Commodity'].unique())

# ── Save ──────────────────────────────────────────────────────────────────────
df_new.to_csv(
    "Datasets/Agriculture_price_dataset.csv",
    index=False
)

print("\n✅ Price dataset expanded successfully!")
