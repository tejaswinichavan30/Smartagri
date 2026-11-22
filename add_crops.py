import pandas as pd
import numpy as np

df = pd.read_csv(r'C:\Users\Dell\OneDrive\Desktop\Major Project\Datasets\Crop_recommendation.csv')

print("Current crops:", df['label'].unique())
print("Current shape:", df.shape)

# ── Add Tomato (100 rows) ─────────────────────────────────────────────────────
# Real agronomic values for Tomato
np.random.seed(42)
tomato = pd.DataFrame({
    'N':           np.random.uniform(60, 100, 100),
    'P':           np.random.uniform(40, 80, 100),
    'K':           np.random.uniform(150, 200, 100),
    'temperature': np.random.uniform(20, 30, 100),
    'humidity':    np.random.uniform(60, 80, 100),
    'ph':          np.random.uniform(6.0, 7.0, 100),
    'rainfall':    np.random.uniform(400, 600, 100),
    'label':       'tomato'
})

# ── Add Potato (100 rows) ─────────────────────────────────────────────────────
# Real agronomic values for Potato
potato = pd.DataFrame({
    'N':           np.random.uniform(80, 120, 100),
    'P':           np.random.uniform(40, 70, 100),
    'K':           np.random.uniform(150, 200, 100),
    'temperature': np.random.uniform(15, 25, 100),
    'humidity':    np.random.uniform(60, 80, 100),
    'ph':          np.random.uniform(5.0, 6.5, 100),
    'rainfall':    np.random.uniform(400, 600, 100),
    'label':       'potato'
})

# ── Combine ───────────────────────────────────────────────────────────────────
df_new = pd.concat([df, tomato, potato], ignore_index=True)

print("\nNew crops:", df_new['label'].unique())
print("New shape:", df_new.shape)

# ── Save ──────────────────────────────────────────────────────────────────────
df_new.to_csv(
   r'C:\Users\Dell\OneDrive\Desktop\Major Project\Datasets\Crop_recommendation.csv' ,
    index=False
)

print("\n✅ Tomato and Potato added successfully!")