import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# ── Load dataset ──────────────────────────────────────────────────────────────
# UPDATE THIS PATH to where your Crop_recommendation.csv is located
df = pd.read_csv(r"C:\Users\Dell\OneDrive\Desktop\Major Project\Datasets\Crop_recommendation.csv")

# ── Rename columns ────────────────────────────────────────────────────────────
df = df.rename(columns={
    'N':           'Nitrogen',
    'P':           'Phosphorus',
    'K':           'Potassium',
    'temperature': 'Temperature',
    'humidity':    'Humidity',
    'ph':          'pH_Value',
    'rainfall':    'Rainfall',
    'label':       'Crop'
})

print("Columns:", df.columns.tolist())
print("Shape:", df.shape)
print("\nCrop Count:\n", df['Crop'].value_counts())
print("\nMissing values:\n", df.isnull().sum())

# ── Drop duplicates ───────────────────────────────────────────────────────────
df = df.drop_duplicates()
print(f"\nAfter dedup: {df.shape}")

# ── Encode target ─────────────────────────────────────────────────────────────
crop_encoder = LabelEncoder()
df['Crop'] = crop_encoder.fit_transform(df['Crop'])
print("\nCrop classes:", crop_encoder.classes_)

# ── Features & Target ─────────────────────────────────────────────────────────
X = df.drop("Crop", axis=1)
y = df["Crop"]

print("\nClass distribution after encoding:\n", y.value_counts())

# ── Train/Test split ──────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ── Scale ─────────────────────────────────────────────────────────────────────
scaler    = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)

# ── NOTE: SMOTE skipped ───────────────────────────────────────────────────────
# Dataset is already perfectly balanced (100 rows per crop).
# SMOTE has zero effect on balanced data — skipping avoids the extra dependency.

# ── Train model ───────────────────────────────────────────────────────────────
model = RandomForestClassifier(
    n_estimators=300,
    max_depth=15,
    min_samples_leaf=2,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
model.fit(X_train_s, y_train)

# ── Evaluate ──────────────────────────────────────────────────────────────────
y_pred = model.predict(X_test_s)

print("\n" + "="*50)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=crop_encoder.classes_))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# ── Cross-validation ──────────────────────────────────────────────────────────
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(model, X_train_s, y_train, cv=cv, scoring='accuracy')
print(f"\nCross-Val Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# ── Feature importance ────────────────────────────────────────────────────────
feat_imp = pd.DataFrame({
    'feature':    X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
print("\nTop features:\n", feat_imp)

# ── Save models ───────────────────────────────────────────────────────────────
os.makedirs("models/saved_models", exist_ok=True)

joblib.dump(model,        "models/saved_models/crop_model.pkl")
joblib.dump(scaler,       "models/saved_models/scaler.pkl")
joblib.dump(crop_encoder, "models/saved_models/crop_encoder.pkl")

print("\n✓ Model saved successfully!")
print("✓ Files saved to: models/saved_models/")
print("   - crop_model.pkl")
print("   - scaler.pkl")
print("   - crop_encoder.pkl")