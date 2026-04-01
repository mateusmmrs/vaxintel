"""Composite score calculation."""

from __future__ import annotations

import pandas as pd

from vaxintel.scoring.weights import ScoreWeights


def compute_vaccination_opportunity_index(
    animal_score: pd.Series,
    sanitary_score: pd.Series,
    economic_score: pd.Series,
    weights: ScoreWeights,
) -> pd.Series:
    """Compute the weighted Vaccination Opportunity Index."""
    normalized = weights.normalized()
    return (
        normalized.animal * animal_score
        + normalized.sanitary * sanitary_score
        + normalized.economic * economic_score
    )

