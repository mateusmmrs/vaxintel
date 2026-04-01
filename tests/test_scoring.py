"""Tests for score normalization and weighting."""

from __future__ import annotations

import pandas as pd

from vaxintel.scoring.index import compute_combined_opportunity_index, compute_opportunity_score
from vaxintel.scoring.normalize import min_max_scale
from vaxintel.scoring.weights import CombinedModeWeights, OpportunityWeights


def test_min_max_scale_returns_zero_when_constant() -> None:
    series = pd.Series([5, 5, 5])
    result = min_max_scale(series)
    assert result.tolist() == [0.0, 0.0, 0.0]


def test_opportunity_score_normalizes_weights() -> None:
    result = compute_opportunity_score(
        animal_score=pd.Series([100.0]),
        sanitary_score=pd.Series([0.0]),
        economic_score=pd.Series([0.0]),
        weights=OpportunityWeights(4.0, 3.0, 3.0),
    )
    assert result.iloc[0] == 40.0


def test_combined_opportunity_index_normalizes_weights() -> None:
    result = compute_combined_opportunity_index(
        beef_score=pd.Series([100.0]),
        dairy_score=pd.Series([0.0]),
        weights=CombinedModeWeights(5.0, 5.0),
    )
    assert result.iloc[0] == 50.0
