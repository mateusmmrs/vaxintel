"""Economic exposure feature engineering."""

from __future__ import annotations

import pandas as pd

from vaxintel.data_processing.harmonize import merge_on_uf
from vaxintel.scoring.normalize import mean_score, min_max_scale


def build_economic_features(
    production_value_df: pd.DataFrame,
    slaughter_df: pd.DataFrame,
    milk_df: pd.DataFrame,
) -> pd.DataFrame:
    """Build an economic exposure score for the cattle chain."""
    merged = merge_on_uf(
        [
            production_value_df[
                [column for column in ["uf", "estimated_milk_value_brl"] if column in production_value_df.columns]
            ],
            slaughter_df[[column for column in ["uf", "carcass_weight_kg"] if column in slaughter_df.columns]],
            milk_df[[column for column in ["uf", "milk_production_liters"] if column in milk_df.columns]],
        ]
    )
    merged["economic_exposure_score"] = mean_score(
        [
            min_max_scale(merged["estimated_milk_value_brl"]),
            min_max_scale(merged["carcass_weight_kg"]),
            min_max_scale(merged["milk_production_liters"]),
        ]
    )
    return merged
