"""Economic feature engineering for beef, dairy and combined modes."""

from __future__ import annotations

import pandas as pd

from vaxintel.data_processing.harmonize import merge_on_uf
from vaxintel.scoring.normalize import mean_score, min_max_scale


def build_economic_features(
    production_value_df: pd.DataFrame,
    slaughter_df: pd.DataFrame,
    milk_df: pd.DataFrame,
) -> pd.DataFrame:
    """Build separate beef, dairy and combined economic scores."""
    merged = merge_on_uf(
        [
            production_value_df[
                [column for column in ["uf", "reference_year", "estimated_milk_value_brl"] if column in production_value_df.columns]
            ],
            slaughter_df[
                [column for column in ["uf", "bovine_slaughter", "carcass_weight_kg"] if column in slaughter_df.columns]
            ],
            milk_df[
                [
                    column
                    for column in ["uf", "milk_production_liters", "milk_price_brl_per_liter"]
                    if column in milk_df.columns
                ]
            ],
        ]
    ).fillna(0)

    merged["beef_economic_score"] = mean_score(
        [
            min_max_scale(merged["bovine_slaughter"]),
            min_max_scale(merged["carcass_weight_kg"]),
        ]
    )
    merged["dairy_economic_score"] = mean_score(
        [
            min_max_scale(merged["milk_production_liters"]),
            min_max_scale(merged["milk_price_brl_per_liter"]),
            min_max_scale(merged["estimated_milk_value_brl"]),
        ]
    )
    merged["economic_exposure_score_combined"] = mean_score(
        [
            merged["beef_economic_score"],
            merged["dairy_economic_score"],
        ]
    )
    return merged
