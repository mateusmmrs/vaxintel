"""Normalization utilities for score construction."""

from __future__ import annotations

import pandas as pd


def min_max_scale(series: pd.Series) -> pd.Series:
    """Scale a numeric series to a 0-100 range."""
    minimum = series.min()
    maximum = series.max()
    if pd.isna(minimum) or pd.isna(maximum) or minimum == maximum:
        return pd.Series([0.0] * len(series), index=series.index, dtype=float)
    return 100.0 * (series - minimum) / (maximum - minimum)


def mean_score(components: list[pd.Series]) -> pd.Series:
    """Average multiple score components aligned by index."""
    return pd.concat(components, axis=1).mean(axis=1)

