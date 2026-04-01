"""Tests for score normalization and weighting."""

from __future__ import annotations

import pandas as pd

from vaxintel.scoring.index import compute_vaccination_opportunity_index
from vaxintel.scoring.normalize import min_max_scale
from vaxintel.scoring.weights import ScoreWeights


def test_min_max_scale_returns_zero_when_constant() -> None:
    series = pd.Series([5, 5, 5])
    result = min_max_scale(series)
    assert result.tolist() == [0.0, 0.0, 0.0]


def test_opportunity_index_normalizes_weights() -> None:
    result = compute_vaccination_opportunity_index(
        animal_score=pd.Series([100.0]),
        sanitary_score=pd.Series([0.0]),
        economic_score=pd.Series([0.0]),
        weights=ScoreWeights(4.0, 3.0, 3.0),
    )
    assert result.iloc[0] == 40.0

