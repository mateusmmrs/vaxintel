"""Animal exposure feature engineering."""

from __future__ import annotations

import pandas as pd

from vaxintel.scoring.normalize import min_max_scale


def build_exposure_features(herd_df: pd.DataFrame, area_df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Build cattle exposure features and the animal exposure score."""
    keep = ["uf", "bovine_herd"]
    if "reference_year" in herd_df.columns:
        keep.append("reference_year")
    df = herd_df[keep].copy()
    if area_df is not None and {"uf", "uf_area_km2"} <= set(area_df.columns):
        df = df.merge(area_df[["uf", "uf_area_km2"]], on="uf", how="left")
        df["bovine_density"] = df["bovine_herd"] / df["uf_area_km2"]
    df["animal_exposure_score"] = min_max_scale(df["bovine_herd"])
    return df
