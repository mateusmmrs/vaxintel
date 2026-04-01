"""Tests for feature engineering steps."""

from __future__ import annotations

import pandas as pd

from vaxintel.features.exposure import build_exposure_features


def test_build_exposure_features_creates_score() -> None:
    herd = pd.DataFrame({"uf": ["SP", "MT"], "bovine_herd": [10, 20]})
    result = build_exposure_features(herd)
    assert "animal_exposure_score" in result.columns
    assert result["animal_exposure_score"].max() == 100.0

