import numpy as np
from aero_autonomy_ai.data.dataset import TelemetryDataset
from aero_autonomy_ai.data.normalizer import TelemetryNormalizer


def test_normalizer_fit_transform():
    features = ("roll", "pitch", "vbat")
    data = np.array(
        [
            [10.0, -5.0, 14.8],
            [20.0, 5.0, 14.2],
            [30.0, 15.0, 13.6],
        ],
        dtype=np.float32,
    )

    norm = TelemetryNormalizer(features)
    norm.fit(data)
    transformed = norm.transform(data)

    # Transformed data should have mean ~0 and std ~1 along axis 0
    assert np.allclose(np.mean(transformed, axis=0), [0.0, 0.0, 0.0], atol=1e-5)
    assert np.allclose(np.std(transformed, axis=0), [1.0, 1.0, 1.0], atol=1e-5)


def test_normalizer_zero_std_handling():
    # Feature with zero variance should not divide by zero
    features = ("static_sensor",)
    data = np.array([[5.0], [5.0], [5.0]], dtype=np.float32)

    norm = TelemetryNormalizer(features)
    norm.fit(data)
    transformed = norm.transform(data)
    assert not np.isnan(transformed).any()
    assert np.allclose(transformed, 0.0)


def test_normalizer_save_load(tmp_path):
    features = ("f1", "f2")
    norm = TelemetryNormalizer(features)
    norm.mean = np.array([1.5, 2.5], dtype=np.float32)
    norm.std = np.array([0.5, 1.2], dtype=np.float32)

    out_file = tmp_path / "stats.json"
    norm.save(out_file)

    loaded_norm = TelemetryNormalizer.load(out_file)
    assert loaded_norm.features == features
    assert np.allclose(loaded_norm.mean, norm.mean)
    assert np.allclose(loaded_norm.std, norm.std)


def test_telemetry_dataset_slicing():
    x = np.random.randn(20, 6).astype(np.float32)
    y = np.random.randint(0, 3, size=(20,)).astype(np.int64)

    dataset = TelemetryDataset(x, y)
    assert len(dataset) == 20

    sample_x, sample_y = dataset[0]
    assert sample_x.shape == (6,)
    assert sample_y.item() == y[0]