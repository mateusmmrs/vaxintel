"""Compose the final opportunity dataset."""

from __future__ import annotations

import pandas as pd

from vaxintel.config import settings
from vaxintel.data_processing.harmonize import merge_on_uf
from vaxintel.scoring.index import compute_combined_opportunity_index, compute_opportunity_score


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


def _classify_territory_profile(df: pd.DataFrame) -> pd.Series:
    """Classify whether a UF is more beef-oriented, dairy-oriented or mixed."""
    gap = df["beef_opportunity_score"] - df["dairy_opportunity_score"]
    profile = pd.Series("Território misto", index=df.index, dtype="object")
    profile = profile.mask(gap >= 7.5, "Território de corte")
    profile = profile.mask(gap <= -7.5, "Território de leite")
    return profile


def _classify_combined_band(series: pd.Series) -> pd.Series:
    """Classify combined scores into executive bands."""
    bands = pd.Series("Monitorar", index=series.index, dtype="object")
    bands = bands.mask(series >= 60, "Muito alta")
    bands = bands.mask((series >= 45) & (series < 60), "Alta")
    bands = bands.mask((series >= 30) & (series < 45), "Moderada")
    return bands


def build_opportunity_dataset(
    exposure_df: pd.DataFrame | None,
    sanitary_df: pd.DataFrame | None,
    economic_df: pd.DataFrame | None,
) -> pd.DataFrame:
    """Merge feature blocks and compute beef, dairy and combined opportunity scores."""
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
        "beef_economic_score",
        "dairy_economic_score",
        "economic_exposure_score_combined",
    ):
        if column not in dataset.columns:
            dataset[column] = 0.0
    dataset["beef_opportunity_score"] = compute_opportunity_score(
        animal_score=dataset["animal_exposure_score"],
        sanitary_score=dataset["sanitary_pressure_score"],
        economic_score=dataset["beef_economic_score"],
        weights=settings.score_config.beef_opportunity,
    )
    dataset["dairy_opportunity_score"] = compute_opportunity_score(
        animal_score=dataset["animal_exposure_score"],
        sanitary_score=dataset["sanitary_pressure_score"],
        economic_score=dataset["dairy_economic_score"],
        weights=settings.score_config.dairy_opportunity,
    )
    dataset["combined_vaccination_opportunity_index"] = compute_combined_opportunity_index(
        beef_score=dataset["beef_opportunity_score"],
        dairy_score=dataset["dairy_opportunity_score"],
        weights=settings.score_config.combined_mode,
    )
    dataset["territory_profile"] = _classify_territory_profile(dataset)
    dataset["combined_band"] = _classify_combined_band(dataset["combined_vaccination_opportunity_index"])
    dataset["final_methodological_note"] = (
        "Score territorial de priorização estratégica; não mede cobertura vacinal real nem vigilância epidemiológica causal."
    )
    return dataset.sort_values("combined_vaccination_opportunity_index", ascending=False)
