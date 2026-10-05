from ml_infra.artifact import predict
from ml_infra.features import FEATURE_NAMES, FEATURE_VERSION, make_features


def test_feature_vector_uses_only_latest_lookback() -> None:
    bars = [{"close": float(100 + i), "volume": 1000} for i in range(30)]
    result = make_features(bars)
    assert set(result) == set(FEATURE_NAMES)
    assert result["volume_ratio_5"] == 1.0
    assert result["pe_ratio"] == 0.0
    assert make_features(bars[-21:]) == result


def test_zero_weight_artifact_predicts_half() -> None:
    bars = [{"close": float(100 + i), "volume": 1000} for i in range(30)]
    artifact = {"feature_version": FEATURE_VERSION, "feature_names": list(FEATURE_NAMES),
                "mean": [0.0] * len(FEATURE_NAMES), "scale": [1.0] * len(FEATURE_NAMES),
                "weights": [0.0] * len(FEATURE_NAMES), "bias": 0.0}
    assert predict(artifact, make_features(bars)) == 0.5
