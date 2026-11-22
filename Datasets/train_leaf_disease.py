"""
train_leaf_disease.py
----------------------
Generic image-classification training script for leaf disease datasets
(works for both the Rice Leaf Disease dataset and the Wheat Leaf Disease
dataset from Kaggle, since both are just folders of images grouped by class).

USAGE (run separately for each dataset):
    python train_leaf_disease.py --data_dir "path/to/rice_dataset" --out_name rice_model
    python train_leaf_disease.py --data_dir "path/to/wheat_dataset" --out_name wheat_model

REQUIREMENTS:
    pip install tensorflow matplotlib scikit-learn

WHAT THIS SCRIPT EXPECTS:
    A folder structure like:
        data_dir/
            ClassA/
                img1.jpg
                img2.jpg
            ClassB/
                img1.jpg
                ...
    (This is exactly how Kaggle image datasets are usually structured —
     one sub-folder per class. If your download has separate train/ and
     val/ / test/ folders already, point --data_dir at the train folder
     and pass --val_dir for the validation one.)
"""

import argparse
import os
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.applications.efficientnet import preprocess_input


def build_datasets(data_dir, val_dir, img_size, batch_size, val_split=0.2, seed=123):
    if val_dir:
        train_ds = tf.keras.utils.image_dataset_from_directory(
            data_dir, image_size=img_size, batch_size=batch_size, seed=seed
        )
        val_ds = tf.keras.utils.image_dataset_from_directory(
            val_dir, image_size=img_size, batch_size=batch_size, seed=seed
        )
    else:
        train_ds = tf.keras.utils.image_dataset_from_directory(
            data_dir, validation_split=val_split, subset="training",
            image_size=img_size, batch_size=batch_size, seed=seed
        )
        val_ds = tf.keras.utils.image_dataset_from_directory(
            data_dir, validation_split=val_split, subset="validation",
            image_size=img_size, batch_size=batch_size, seed=seed
        )
    return train_ds, val_ds


def build_model(num_classes, img_size):
    base = EfficientNetB0(
        include_top=False, weights="imagenet", input_shape=img_size + (3,)
    )
    base.trainable = False  # freeze for initial training (transfer learning)

    inputs = tf.keras.Input(shape=img_size + (3,))
    x = preprocess_input(inputs)
    x = base(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)
    model = models.Model(inputs, outputs)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model, base


def fine_tune(model, base, learning_rate=1e-5):
    base.trainable = True
    # unfreeze only the last ~30% of layers for fine-tuning
    fine_tune_at = int(len(base.layers) * 0.7)
    for layer in base.layers[:fine_tune_at]:
        layer.trainable = False
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def plot_history(history, out_name):
    acc = history.history["accuracy"] + history.history.get("fine_accuracy", [])
    val_acc = history.history["val_accuracy"] + history.history.get("fine_val_accuracy", [])
    plt.figure(figsize=(8, 5))
    plt.plot(acc, label="train acc")
    plt.plot(val_acc, label="val acc")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.title(f"{out_name} training curve")
    plt.savefig(f"{out_name}_training_curve.png")
    print(f"Saved plot to {out_name}_training_curve.png")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", required=True, help="Path to training image folder (class subfolders)")
    parser.add_argument("--val_dir", default=None, help="Optional separate validation folder")
    parser.add_argument("--out_name", default="model", help="Prefix for saved model/plot files")
    parser.add_argument("--img_size", type=int, default=224)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--fine_tune_epochs", type=int, default=10)
    args = parser.parse_args()

    img_size = (args.img_size, args.img_size)

    train_ds, val_ds = build_datasets(args.data_dir, args.val_dir, img_size, args.batch_size)
    class_names = train_ds.class_names
    print("Classes found:", class_names)

    # Performance: cache + prefetch
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)

    # Light augmentation to reduce overfitting on small datasets
    data_augmentation = tf.keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.1),
        layers.RandomZoom(0.1),
    ])
    train_ds = train_ds.map(lambda x, y: (data_augmentation(x, training=True), y))

    model, base = build_model(num_classes=len(class_names), img_size=img_size)
    model.summary()

    callbacks = [
        tf.keras.callbacks.EarlyStopping(patience=4, restore_best_weights=True),
        tf.keras.callbacks.ModelCheckpoint(f"{args.out_name}_best.keras", save_best_only=True),
    ]

    print("\n--- Stage 1: training classifier head (base frozen) ---")
    history = model.fit(
        train_ds, validation_data=val_ds, epochs=args.epochs, callbacks=callbacks
    )

    print("\n--- Stage 2: fine-tuning top layers of base model ---")
    model = fine_tune(model, base)
    history_fine = model.fit(
        train_ds, validation_data=val_ds, epochs=args.fine_tune_epochs, callbacks=callbacks
    )

    # merge histories for plotting
    history.history["fine_accuracy"] = history_fine.history["accuracy"]
    history.history["fine_val_accuracy"] = history_fine.history["val_accuracy"]
    plot_history(history, args.out_name)

    model.save(f"{args.out_name}_final.keras")
    with open(f"{args.out_name}_classes.txt", "w") as f:
        f.write("\n".join(class_names))

    print(f"\nDone. Saved: {args.out_name}_final.keras, {args.out_name}_best.keras, {args.out_name}_classes.txt")


if __name__ == "__main__":
    main()
