from pathlib import Path

from models.disease_class_utils import discover_combined_disease_classes


def test_discovers_nested_rice_and_wheat_disease_classes(tmp_path):
    plantvillage_root = tmp_path / "plantvillage"
    rice_root = tmp_path / "rice"
    wheat_root = tmp_path / "wheat"

    (plantvillage_root / "Apple___Apple_scab").mkdir(parents=True)
    (plantvillage_root / "Apple___Apple_scab" / "img1.jpg").write_text("x")
    (plantvillage_root / "Apple___Black_rot").mkdir(parents=True)
    (plantvillage_root / "Apple___Black_rot" / "img2.jpg").write_text("x")

    (rice_root / "RiceLeafsDisease" / "train" / "bacterial_leaf_blight").mkdir(parents=True)
    (rice_root / "RiceLeafsDisease" / "train" / "bacterial_leaf_blight" / "img3.jpg").write_text("x")
    (rice_root / "RiceLeafsDisease" / "train" / "healthy").mkdir(parents=True)
    (rice_root / "RiceLeafsDisease" / "train" / "healthy" / "img4.jpg").write_text("x")

    (wheat_root / "Wheat Leaf Disease" / "Train" / "BlackPoint").mkdir(parents=True)
    (wheat_root / "Wheat Leaf Disease" / "Train" / "BlackPoint" / "img5.jpg").write_text("x")
    (wheat_root / "Wheat Leaf Disease" / "Train" / "HealthyLeaf").mkdir(parents=True)
    (wheat_root / "Wheat Leaf Disease" / "Train" / "HealthyLeaf" / "img6.jpg").write_text("x")

    classes = discover_combined_disease_classes(
        plantvillage_root=plantvillage_root,
        rice_root=rice_root,
        wheat_root=wheat_root,
    )

    assert classes == [
        "Apple - Apple scab",
        "Apple - Black rot",
        "Rice - Bacterial Leaf Blight",
        "Rice - Healthy",
        "Wheat - Black Point",
        "Wheat - Healthy Leaf",
    ]
