"""Table helpers."""

from __future__ import annotations

import pandas as pd


def top_n(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return the top N rows ordered by the opportunity index."""
    return df.nlargest(n, "vaccination_opportunity_index")

