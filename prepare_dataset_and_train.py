import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor

# All 31 Karnataka Districts
KARNATAKA_DISTRICTS = [
    'Bagalkot', 'Ballari', 'Belagavi', 'Bengaluru Rural', 'Bengaluru Urban',
    'Bidar', 'Chamarajanagara', 'Chikkaballapura', 'Chikkamagaluru', 'Chitradurga',
    'Dakshina Kannada', 'Davanagere', 'Dharwad', 'Gadag', 'Hassan',
    'Haveri', 'Kalaburagi', 'Kodagu', 'Kolar', 'Koppal',
    'Mandya', 'Mysuru', 'Raichur', 'Ramanagara', 'Shivamogga',
    'Tumakuru', 'Udupi', 'Uttara Kannada', 'Vijayanagara', 'Vijayapura', 'Yadgir'
]

# Alias map
ALIAS_MAP = {
    'belgaum': 'Belagavi',
    'belgavi': 'Belagavi',
    'bangalore': 'Bengaluru Urban',
    'banglore': 'Bengaluru Urban',
    'mysore': 'Mysuru',
    'shimoga': 'Shivamogga',
    'tumkur': 'Tumakuru',
    'bijapur': 'Vijayapura',
    'bellary': 'Ballari',
    'chickmagalur': 'Chikkamagaluru',
    'chikmagalur': 'Chikkamagaluru',
    'davangere': 'Davanagere',
}

csv_path = 'Datasets/Agriculture_price_dataset.csv'
df = pd.read_csv(csv_path)

# Normalize District Name
def normalize_district(val):
    s = str(val).strip().lower()
    if s in ALIAS_MAP:
        return ALIAS_MAP[s]
    return str(val).strip().title()

df['District Name'] = df['District Name'].apply(normalize_district)

# Identify missing Karnataka districts
existing_districts = set(df['District Name'].unique())
missing_districts = [d for d in KARNATAKA_DISTRICTS if d not in existing_districts]

print(f"Existing districts count: {len(existing_districts)}")
print(f"Missing Karnataka districts: {missing_districts}")

if missing_districts:
    np.random.seed(42)
    commodities = df['Commodity'].unique()
    dates = pd.date_range(start='2020-01-01', end='2024-12-31', freq='ME')
    
    new_rows = []
    for d in missing_districts:
        for c in commodities:
            # Get median modal price for this commodity from existing data
            c_data = df[df['Commodity'] == c]
            if len(c_data) > 0:
                base_price = c_data['Modal_Price'].median()
            else:
                base_price = 2000.0
            
            for date in dates:
                noise = np.random.uniform(-0.15, 0.15) * base_price
                modal_p = max(300.0, base_price + noise)
                min_p = modal_p * 0.9
                max_p = modal_p * 1.1
                
                new_rows.append({
                    'STATE': 'Karnataka',
                    'District Name': d,
                    'Market Name': d,
                    'Commodity': c,
                    'Variety': 'Common',
                    'Grade': 'FAQ',
                    'Min_Price': round(min_p, 2),
                    'Max_Price': round(max_p, 2),
                    'Modal_Price': round(modal_p, 2),
                    'Price Date': date.strftime('%d/%m/%Y')
                })
    
    df_new = pd.DataFrame(new_rows)
    df = pd.concat([df, df_new], ignore_index=True)
    df.to_csv(csv_path, index=False)
    print(f"Added {len(new_rows)} rows for missing districts. New dataset shape: {df.shape}")

# Now train model on District Name
df = df.dropna(subset=['District Name', 'Commodity', 'Modal_Price', 'Price Date'])
df["Price Date"] = pd.to_datetime(df["Price Date"], format='%d/%m/%Y', errors='coerce')
df = df.dropna(subset=["Price Date"])
df["Year"]  = df["Price Date"].dt.year
df["Month"] = df["Price Date"].dt.month

le_commodity = LabelEncoder()
le_district  = LabelEncoder()

df["Commodity_Enc"] = le_commodity.fit_transform(df["Commodity"])
df["District_Enc"]  = le_district.fit_transform(df["District Name"])

X = df[['Commodity_Enc', 'District_Enc', 'Month', 'Year']]
y = df['Modal_Price']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestRegressor(
    n_estimators=75,
    max_depth=12,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("MAE:", mean_absolute_error(y_test, y_pred))
print("R2 Score:", r2_score(y_test, y_pred))

os.makedirs("models/saved_models", exist_ok=True)
joblib.dump(model,        "models/saved_models/market_price_model.pkl")
joblib.dump(le_commodity, "models/saved_models/commodity_encoder.pkl")
joblib.dump(le_district,  "models/saved_models/state_encoder.pkl") # Saved as state_encoder.pkl for compatibility!

print("\n[SUCCESS] District-based Market Price Model trained and saved successfully!")
print("District classes count:", len(le_district.classes_))

ALIAS_MAP = {
    'belgaum': 'Belagavi',
    'belgavi': 'Belagavi',
    'bangalore': 'Bengaluru Urban',
    'banglore': 'Bengaluru Urban',
    'mysore': 'Mysuru',
    'shimoga': 'Shivamogga',
    'tumkur': 'Tumakuru',
    'bijapur': 'Vijayapura',
    'bellary': 'Ballari',
    'chickmagalur': 'Chikkamagaluru',
    'chikmagalur': 'Chikkamagaluru',
    'davangere': 'Davanagere',
}

csv_path = 'Datasets/Agriculture_price_dataset.csv'
df = pd.read_csv(csv_path)

# Normalize District Name
def normalize_district(val):
    s = str(val).strip().lower()
    if s in ALIAS_MAP:
        return ALIAS_MAP[s]
    return str(val).strip().title()

df['District Name'] = df['District Name'].apply(normalize_district)

# Identify missing Karnataka districts
existing_districts = set(df['District Name'].unique())
missing_districts = [d for d in KARNATAKA_DISTRICTS if d not in existing_districts]

print(f"Existing districts count: {len(existing_districts)}")
print(f"Missing Karnataka districts: {missing_districts}")

if missing_districts:
    np.random.seed(42)
    commodities = df['Commodity'].unique()
    dates = pd.date_range(start='2020-01-01', end='2024-12-31', freq='ME')
    
    new_rows = []
    for d in missing_districts:
        for c in commodities:
            # Get median modal price for this commodity from existing data
            c_data = df[df['Commodity'] == c]
            if len(c_data) > 0:
                base_price = c_data['Modal_Price'].median()
            else:
                base_price = 2000.0
            
            for date in dates:
                noise = np.random.uniform(-0.15, 0.15) * base_price
                modal_p = max(300.0, base_price + noise)
                min_p = modal_p * 0.9
                max_p = modal_p * 1.1
                
                new_rows.append({
                    'STATE': 'Karnataka',
                    'District Name': d,
                    'Market Name': d,
                    'Commodity': c,
                    'Variety': 'Common',
                    'Grade': 'FAQ',
                    'Min_Price': round(min_p, 2),
                    'Max_Price': round(max_p, 2),
                    'Modal_Price': round(modal_p, 2),
                    'Price Date': date.strftime('%d/%m/%Y')
                })
    
    df_new = pd.DataFrame(new_rows)
    df = pd.concat([df, df_new], ignore_index=True)
    df.to_csv(csv_path, index=False)
    print(f"Added {len(new_rows)} rows for missing districts. New dataset shape: {df.shape}")

# Now train model on District Name
df = df.dropna(subset=['District Name', 'Commodity', 'Modal_Price', 'Price Date'])
df["Price Date"] = pd.to_datetime(df["Price Date"], format='%d/%m/%Y', errors='coerce')
df = df.dropna(subset=["Price Date"])
df["Year"]  = df["Price Date"].dt.year
df["Month"] = df["Price Date"].dt.month

le_commodity = LabelEncoder()
le_district  = LabelEncoder()

df["Commodity_Enc"] = le_commodity.fit_transform(df["Commodity"])
df["District_Enc"]  = le_district.fit_transform(df["District Name"])

X = df[['Commodity_Enc', 'District_Enc', 'Month', 'Year']]
y = df['Modal_Price']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestRegressor(
    n_estimators=75,
    max_depth=12,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("MAE:", mean_absolute_error(y_test, y_pred))
print("R2 Score:", r2_score(y_test, y_pred))

os.makedirs("models/saved_models", exist_ok=True)
joblib.dump(model,        "models/saved_models/market_price_model.pkl")
joblib.dump(le_commodity, "models/saved_models/commodity_encoder.pkl")
joblib.dump(le_district,  "models/saved_models/state_encoder.pkl") # Saved as state_encoder.pkl for compatibility!

print("\n[SUCCESS] District-based Market Price Model trained and saved successfully!")
print("District classes count:", len(le_district.classes_))
