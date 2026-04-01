"""Composite score calculations for the VaxIntel v2 architecture."""

from __future__ import annotations

import pandas as pd

from vaxintel.scoring.weights import CombinedModeWeights, OpportunityWeights


def compute_opportunity_score(
    animal_score: pd.Series,
    sanitary_score: pd.Series,
    economic_score: pd.Series,
    weights: OpportunityWeights,
) -> pd.Series:
    """Compute a weighted opportunity score for one production mode."""
    normalized = weights.normalized()
    return (
        normalized.animal * animal_score
        + normalized.sanitary * sanitary_score
        + normalized.economic * economic_score
    )


def compute_combined_opportunity_index(
    beef_score: pd.Series,
    dairy_score: pd.Series,
    weights: CombinedModeWeights,
) -> pd.Series:
    """Compute the blended combined opportunity index."""
    normalized = weights.normalized()
    return normalized.beef * beef_score + normalized.dairy * dairy_score
