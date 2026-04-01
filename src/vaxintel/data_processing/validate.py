"""Validation utilities for the processed dataset."""

from __future__ import annotations

import pandas as pd


REQUIRED_COLUMNS = {
    "uf",
    "animal_exposure_score",
    "sanitary_pressure_score",
    "economic_exposure_score",
    "vaccination_opportunity_index",
}


def validate_required_columns(df: pd.DataFrame) -> None:
    """Raise an error if required output columns are missing."""
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Processed dataset missing required columns: {sorted(missing)}")

