import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
import joblib

data_path = r"Datasets\Agriculture_price_dataset.csv"

print("Loading dataset...")

data_path = "Datasets/Agriculture_price_dataset.csv"
data = pd.read_csv(data_path)
print("Dataset loaded successfully!")
print("Columns:", data.columns)
print("Crops:", data['Commodity'].unique())
print("Shape:", data.shape)

# ── Data Cleaning ─────────────────────────────────────────────────────────────
data = data.dropna()
data["Price Date"] = pd.to_datetime(data["Price Date"], errors='coerce')
data = data.dropna(subset=["Price Date"])
data["Year"]  = data["Price Date"].dt.year
data["Month"] = data["Price Date"].dt.month

# ── Encode ────────────────────────────────────────────────────────────────────
le_commodity = LabelEncoder()
le_state     = LabelEncoder()

data["Commodity"] = le_commodity.fit_transform(data["Commodity"])
data["STATE"]     = le_state.fit_transform(data["STATE"])

# ── Features ──────────────────────────────────────────────────────────────────
X = data[['Commodity', 'STATE', 'Month', 'Year']]
y = data['Modal_Price']

# ── Split ─────────────────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ── Train ─────────────────────────────────────────────────────────────────────
model = RandomForestRegressor(
    n_estimators=75,
    max_depth=12,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)
print("Model trained successfully!")

# ── Evaluate ──────────────────────────────────────────────────────────────────
y_pred = model.predict(X_test)
print("MAE:", mean_absolute_error(y_test, y_pred))
print("R2 Score:", r2_score(y_test, y_pred))

# ── Save ──────────────────────────────────────────────────────────────────────
os.makedirs("models/saved_models", exist_ok=True)

joblib.dump(model,        "models/saved_models/market_price_model.pkl")
joblib.dump(le_commodity, "models/saved_models/commodity_encoder.pkl")
joblib.dump(le_state,     "models/saved_models/state_encoder.pkl")

print("\n✅ Model and Encoders saved successfully!")
print("Crops in model:", le_commodity.classes_)