import tensorflow as tf
from tf_keras.preprocessing.image import ImageDataGenerator
from tf_keras import layers, models
import os
import pickle
import shutil

try:
    from models.disease_class_utils import discover_combined_disease_classes
except ModuleNotFoundError:
    from disease_class_utils import discover_combined_disease_classes

# ── Dataset Paths ─────────────────────────────────────────────────────────────
plantvillage_color = r"D:\Major Project\Datasets\plantvillage dataset\color"
rice_train_path    = r"D:\Major Project\Datasets\rice_data"
wheat_train_path   = r"D:\Major Project\Datasets\wheat_data"
combined_path      = r"D:\Major Project\Datasets\disease_combined"
IMG_SIZE   = 128
BATCH_SIZE = 16
EPOCHS     = 10

# ── Step 1: Build combined flat dataset ───────────────────────────────────────
print("Building combined dataset...")

if os.path.exists(combined_path):
    shutil.rmtree(combined_path)
os.makedirs(combined_path, exist_ok=True)

# ── Add PlantVillage crops ────────────────────────────────────────────────────
print("\n→ Adding PlantVillage crops...")
for folder in os.listdir(plantvillage_color):
    folder_path = os.path.join(plantvillage_color, folder)
    if not os.path.isdir(folder_path):
        continue

    parts = folder.split('___')
    if len(parts) != 2:
        continue

    crop = parts[0].replace('_', ' ').replace('(', '').replace(')', '').strip()
    disease = parts[1].replace('_', ' ').strip()
    class_name = f"{crop} - {disease}"
    dest_path = os.path.join(combined_path, class_name)

    if not os.path.exists(dest_path):
        shutil.copytree(folder_path, dest_path)
        print(f"  ✓ Added: {class_name}")

# ── Add Rice crops ────────────────────────────────────────────────────────────
print("\n→ Adding Rice crops...")
rice_dataset_root = os.path.join(rice_train_path, "RiceLeafsDisease", "train")
if os.path.isdir(rice_dataset_root):
    for disease_folder in sorted(os.listdir(rice_dataset_root)):
        disease_path = os.path.join(rice_dataset_root, disease_folder)
        if not os.path.isdir(disease_path):
            continue

        class_name = f"Rice - {disease_folder.replace('_', ' ').title()}"
        dest_path = os.path.join(combined_path, class_name)

        if not os.path.exists(dest_path):
            shutil.copytree(disease_path, dest_path)
            print(f"  ✓ Added: {class_name}")

# ── Add Wheat crops ───────────────────────────────────────────────────────────
print("\n→ Adding Wheat crops...")
wheat_dataset_root = os.path.join(wheat_train_path, "Wheat Leaf Disease")
for split_name in ["Train", "Test", "Validation"]:
    split_path = os.path.join(wheat_dataset_root, split_name)
    if not os.path.isdir(split_path):
        continue

    for disease_folder in sorted(os.listdir(split_path)):
        disease_path = os.path.join(split_path, disease_folder)
        if not os.path.isdir(disease_path):
            continue

        class_name = f"Wheat - {disease_folder.replace('_', ' ').title()}"
        dest_path = os.path.join(combined_path, class_name)

        if not os.path.exists(dest_path):
            shutil.copytree(disease_path, dest_path)
            print(f"  ✓ Added: {class_name}")

# ── Summary ───────────────────────────────────────────────────────────────────
all_classes = sorted(os.listdir(combined_path))
print(f"\n✓ Combined dataset ready!")
print(f"Total classes: {len(all_classes)}")
print("\nAll classes:")
for i, cls in enumerate(all_classes):
    print(f"  {i+1}. {cls}")

# ── Step 2: Data Generator ────────────────────────────────────────────────────
datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=15,
    horizontal_flip=True,
    zoom_range=0.1
)

train_data = datagen.flow_from_directory(
    combined_path,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training'
)

val_data = datagen.flow_from_directory(
    combined_path,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation'
)

print(f"\nTotal classes: {train_data.num_classes}")
print(f"Training images: {train_data.samples}")
print(f"Validation images: {val_data.samples}")

# ── Step 3: CNN Model ─────────────────────────────────────────────────────────
model = models.Sequential([
    layers.Input(shape=(IMG_SIZE, IMG_SIZE, 3)),

    layers.Conv2D(32, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),

    layers.Conv2D(64, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),

    layers.Conv2D(128, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),

    layers.Conv2D(256, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),

    layers.Flatten(),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(train_data.num_classes, activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

# ── Step 4: Train ─────────────────────────────────────────────────────────────
model.fit(
    train_data,
    validation_data=val_data,
    epochs=EPOCHS
)

# ── Step 5: Save ──────────────────────────────────────────────────────────────
os.makedirs("models/saved_models", exist_ok=True)

model.save("models/saved_models/disease_model.h5")

class_names = list(train_data.class_indices.keys())

with open("models/saved_models/disease_classes.pkl", "wb") as f:
    pickle.dump(class_names, f)

print("\n✅ Disease Model Trained & Saved!")
print(f"Total classes: {len(class_names)}")
print("\nFinal classes:")
for i, cls in enumerate(class_names):
    print(f"  {i+1}. {cls}")