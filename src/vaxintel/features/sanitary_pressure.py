"""Sanitary pressure feature engineering."""

from __future__ import annotations

import pandas as pd

from vaxintel.data_processing.harmonize import merge_on_uf
from vaxintel.scoring.normalize import mean_score, min_max_scale


def build_sanitary_features(
    herd_df: pd.DataFrame,
    slaughter_df: pd.DataFrame,
    milk_df: pd.DataFrame,
    area_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Build a conservative sanitary pressure proxy score."""
    merged = merge_on_uf(
        [
            herd_df[[column for column in ["uf", "bovine_herd", "reference_year"] if column in herd_df.columns]],
            slaughter_df[[column for column in ["uf", "bovine_slaughter"] if column in slaughter_df.columns]],
            milk_df[[column for column in ["uf", "milk_production_liters"] if column in milk_df.columns]],
        ]
    )
    merged["slaughter_intensity"] = merged["bovine_slaughter"] / merged["bovine_herd"]
    merged["milk_intensity"] = merged["milk_production_liters"] / merged["bovine_herd"]
    components = [
        min_max_scale(merged["slaughter_intensity"]),
        min_max_scale(merged["milk_intensity"]),
    ]
    if area_df is not None and {"uf", "uf_area_km2"} <= set(area_df.columns):
        merged = merged.merge(area_df[["uf", "uf_area_km2"]], on="uf", how="left")
        merged["bovine_density"] = merged["bovine_herd"] / merged["uf_area_km2"]
        components.append(min_max_scale(merged["bovine_density"]))
    merged["sanitary_pressure_score"] = mean_score(components)
    return merged
