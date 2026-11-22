import os
from pathlib import Path


def _normalize_class_name(raw_name: str) -> str:
    return raw_name.replace('_', ' ').replace('  ', ' ').strip()


def _iter_dataset_class_dirs(root: Path):
    if not root.exists():
        return []
    return sorted(
        [p for p in root.iterdir() if p.is_dir() and any(p.iterdir())],
        key=lambda p: p.name,
    )


def discover_combined_disease_classes(plantvillage_root, rice_root, wheat_root):
    classes = []

    for folder in _iter_dataset_class_dirs(Path(plantvillage_root)):
        parts = folder.name.split('___')
        if len(parts) != 2:
            continue
        crop = parts[0].replace('_', ' ').replace('(', '').replace(')', '').strip()
        disease = parts[1].replace('_', ' ').strip()
        classes.append(f"{crop} - {disease}")

    rice_root = Path(rice_root)
    rice_dataset_root = rice_root / "RiceLeafsDisease"
    if rice_dataset_root.exists():
        for disease_dir in sorted([p for p in (rice_dataset_root / "train").iterdir() if p.is_dir()]):
            class_name = f"Rice - {_normalize_class_name(disease_dir.name)}"
            classes.append(class_name)

    wheat_root = Path(wheat_root)
    wheat_dataset_root = wheat_root / "Wheat Leaf Disease"
    if wheat_dataset_root.exists():
        for split_dir in ["Train", "Test", "Validation"]:
            split_path = wheat_dataset_root / split_dir
            if not split_path.exists():
                continue
            for disease_dir in sorted([p for p in split_path.iterdir() if p.is_dir()]):
                class_name = f"Wheat - {_normalize_class_name(disease_dir.name)}"
                classes.append(class_name)

    return sorted(set(classes))
