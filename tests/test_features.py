"""Tests for feature engineering steps."""

from __future__ import annotations

import pandas as pd

from vaxintel.features.economic import build_economic_features
from vaxintel.features.exposure import build_exposure_features


def test_build_exposure_features_creates_score() -> None:
    herd = pd.DataFrame({"uf": ["SP", "MT"], "bovine_herd": [10, 20]})
    result = build_exposure_features(herd)
    assert "animal_exposure_score" in result.columns
    assert result["animal_exposure_score"].max() == 100.0


def test_build_economic_features_creates_beef_and_dairy_scores() -> None:
    production_value = pd.DataFrame(
        {
            "uf": ["SP", "MT"],
            "reference_year": [2024, 2024],
            "estimated_milk_value_brl": [100.0, 50.0],
        }
    )
    slaughter = pd.DataFrame(
        {
            "uf": ["SP", "MT"],
            "bovine_slaughter": [10.0, 20.0],
            "carcass_weight_kg": [1000.0, 2500.0],
        }
    )
    milk = pd.DataFrame(
        {
            "uf": ["SP", "MT"],
            "milk_production_liters": [200.0, 50.0],
            "milk_price_brl_per_liter": [2.0, 1.0],
        }
    )
    result = build_economic_features(production_value, slaughter, milk)
    assert "beef_economic_score" in result.columns
    assert "dairy_economic_score" in result.columns
    assert "economic_exposure_score_combined" in result.columns
