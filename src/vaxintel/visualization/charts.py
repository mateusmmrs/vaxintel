"""Chart helpers."""

from __future__ import annotations

import pandas as pd
import plotly.express as px


def ranking_bar(df: pd.DataFrame, value_column: str, title: str):
    """Build a ranking bar chart by UF."""
    return px.bar(df, x="uf", y=value_column, title=title)

