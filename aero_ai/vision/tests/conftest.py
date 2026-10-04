import json
import pytest
from PIL import Image


@pytest.fixture
def dummy_dataset(tmp_path):
    train_img_dir = tmp_path / "images" / "train"
    val_img_dir = tmp_path / "images" / "val"
    annot_dir = tmp_path / "annotations"
    train_img_dir.mkdir(parents=True)
    val_img_dir.mkdir(parents=True)
    annot_dir.mkdir(parents=True)

    # Make test image
    img = Image.new("RGB", (640, 640), color=(100, 100, 100))
    img.save(train_img_dir / "frame_0001.jpg")
    img.save(val_img_dir / "frame_0001.jpg")

    coco_data = {
        "images": [{"id": 1, "file_name": "frame_0001.jpg", "width": 640, "height": 640}],
        "categories": [
            {"id": 1, "name": "person"},
            {"id": 2, "name": "vehicle"},
            {"id": 3, "name": "animal"},
        ],
        "annotations": [
            {
                "id": 1,
                "image_id": 1,
                "category_id": 1,
                "bbox": [50.0, 50.0, 40.0, 40.0],
                "area": 1600.0,
                "iscrowd": 0,
            }
        ],
    }

    train_json = annot_dir / "train.json"
    val_json = annot_dir / "val.json"
    train_json.write_text(json.dumps(coco_data), encoding="utf-8")
    val_json.write_text(json.dumps(coco_data), encoding="utf-8")

    return {
        "train_images": train_img_dir,
        "train_annotations": train_json,
        "val_images": val_img_dir,
        "val_annotations": val_json,
    }