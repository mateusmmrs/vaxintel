"""Map helpers."""

from __future__ import annotations

import pandas as pd
import plotly.express as px


def choropleth_by_uf(df: pd.DataFrame, geojson: dict, value_column: str, title: str):
    """Build a Brazil UF choropleth using IBGE GeoJSON."""
    figure = px.choropleth(
        df,
        geojson=geojson,
        locations="uf",
        featureidkey="properties.SIGLA_UF",
        color=value_column,
        color_continuous_scale="YlOrRd",
        title=title,
    )
    figure.update_geos(fitbounds="locations", visible=False)
    return figure
