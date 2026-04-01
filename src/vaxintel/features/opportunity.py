"""Compose the final opportunity dataset."""

from __future__ import annotations

import pandas as pd

from vaxintel.data_processing.harmonize import merge_on_uf
from vaxintel.scoring.index import compute_vaccination_opportunity_index
from vaxintel.scoring.weights import DEFAULT_WEIGHTS


def _coalesce_duplicate_suffix_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Coalesce pandas merge suffix columns into a single canonical column."""
    result = df.copy()
    x_columns = [column for column in result.columns if column.endswith("_x")]
    for x_column in x_columns:
        base = x_column[:-2]
        y_column = f"{base}_y"
        if y_column in result.columns:
            result[base] = result[x_column].combine_first(result[y_column])
            result = result.drop(columns=[x_column, y_column])
    return result


def build_opportunity_dataset(
    exposure_df: pd.DataFrame | None,
    sanitary_df: pd.DataFrame | None,
    economic_df: pd.DataFrame | None,
) -> pd.DataFrame:
    """Merge feature blocks and compute the final opportunity index."""
    frames = [frame for frame in (exposure_df, sanitary_df, economic_df) if frame is not None]
    if not frames:
        return pd.DataFrame()
    keep_columns = []
    for frame in frames:
        keep_columns.append(frame.loc[:, ~frame.columns.duplicated()])
    dataset = merge_on_uf(keep_columns)
    dataset = _coalesce_duplicate_suffix_columns(dataset)
    dataset = dataset.fillna(0)
    for column in (
        "animal_exposure_score",
        "sanitary_pressure_score",
        "economic_exposure_score",
    ):
        if column not in dataset.columns:
            dataset[column] = 0.0
    dataset["vaccination_opportunity_index"] = compute_vaccination_opportunity_index(
        animal_score=dataset["animal_exposure_score"],
        sanitary_score=dataset["sanitary_pressure_score"],
        economic_score=dataset["economic_exposure_score"],
        weights=DEFAULT_WEIGHTS,
    )
    return dataset.sort_values("vaccination_opportunity_index", ascending=False)
