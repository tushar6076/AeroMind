from aero_vision_ai.data.coco import CocoDetectionDataset
from aero_vision_ai.data.validate import validate_coco_dataset


def test_coco_dataset_loading(dummy_dataset):
    dataset = CocoDetectionDataset(
        image_dir=dummy_dataset["train_images"],
        annotation_file=dummy_dataset["train_annotations"],
        class_names=("person", "vehicle", "animal"),
    )
    assert len(dataset) == 1
    image, target = dataset[0]
    assert image.shape == (3, 640, 640)
    assert len(target["boxes"]) == 1
    assert target["labels"][0] == 1


def test_coco_validation(dummy_dataset):
    report = validate_coco_dataset(
        dummy_dataset["train_images"],
        dummy_dataset["train_annotations"],
        ("person", "vehicle", "animal"),
    )
    assert report["images"] == 1
    assert report["annotations"] == 1