"""Harmonization helpers for temporal and territorial joins."""

from __future__ import annotations

import pandas as pd


def merge_on_uf(frames: list[pd.DataFrame]) -> pd.DataFrame:
    """Merge multiple UF-level frames with an outer join."""
    if not frames:
        return pd.DataFrame()
    merged = frames[0].copy()
    for frame in frames[1:]:
        merged = merged.merge(frame, on="uf", how="outer")
    return merged

