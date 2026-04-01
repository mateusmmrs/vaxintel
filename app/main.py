"""Streamlit application for VaxIntel Brasil."""

from __future__ import annotations

import sys
from pathlib import Path
import json

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vaxintel.config import settings
from vaxintel.scoring.weights import ScoreWeights
from vaxintel.utils.metadata import load_source_manifest
from vaxintel.visualization.maps import choropleth_by_uf


@st.cache_data
def load_dataset() -> pd.DataFrame:
    """Load the processed UF-level cattle opportunity dataset."""
    if not settings.processed_dataset_path.exists():
        raise FileNotFoundError(settings.processed_dataset_path)
    return pd.read_parquet(settings.processed_dataset_path)


@st.cache_data
def load_quarterly() -> pd.DataFrame:
    """Load the processed quarterly dataset for trend analysis."""
    if not settings.processed_quarterly_path.exists():
        return pd.DataFrame()
    return pd.read_parquet(settings.processed_quarterly_path)


@st.cache_data
def load_geojson() -> dict | None:
    """Load the processed UF GeoJSON if available."""
    if not settings.processed_geojson_path.exists():
        return None
    return json.loads(settings.processed_geojson_path.read_text())


def main() -> None:
    """Render the VaxIntel dashboard."""
    st.set_page_config(page_title="VaxIntel Brasil", layout="wide")
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(213, 148, 74, 0.18), transparent 28%),
                linear-gradient(180deg, #f7f2ea 0%, #fcfbf8 48%, #f0eee9 100%);
        }
        div[data-testid="stMetric"] {
            background: rgba(255,255,255,0.78);
            border: 1px solid rgba(64,49,34,0.08);
            padding: 1rem;
            border-radius: 16px;
            box-shadow: 0 8px 24px rgba(55, 42, 24, 0.06);
        }
        h1, h2, h3 {
            letter-spacing: -0.02em;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title("VaxIntel Brasil")
    st.caption(
        "Priorizacao territorial para programas estrategicos de vacinacao animal. "
        "MVP inicial focado em bovinos por UF."
    )

    st.sidebar.header("Escopo")
    species = st.sidebar.selectbox("Especie", ["Bovinos"], index=0)
    st.sidebar.caption("Arquitetura pronta para futuras extensoes em aves, suinos e aquacultura.")

    st.sidebar.header("Pesos do indice")
    weights = ScoreWeights(
        animal=st.sidebar.slider("Animal Exposure", 0.0, 1.0, 0.40, 0.05),
        sanitary=st.sidebar.slider("Sanitary Pressure", 0.0, 1.0, 0.30, 0.05),
        economic=st.sidebar.slider("Economic Exposure", 0.0, 1.0, 0.30, 0.05),
    ).normalized()

    if not settings.processed_dataset_path.exists():
        st.warning(
            "Dataset processado ainda nao encontrado. Execute `python scripts/download_data.py` "
            "e `python scripts/build_dataset.py` para carregar dados reais."
        )
        st.stop()

    df = load_dataset().copy()
    quarterly = load_quarterly()
    geojson = load_geojson()
    df["vaccination_opportunity_index"] = (
        weights.animal * df["animal_exposure_score"]
        + weights.sanitary * df["sanitary_pressure_score"]
        + weights.economic * df["economic_exposure_score"]
    )
    df = df.sort_values("vaccination_opportunity_index", ascending=False)

    top = df.iloc[0]
    col1, col2, col3 = st.columns(3)
    col1.metric("Especie", species)
    col2.metric("UF lider", top["uf"])
    col3.metric("VOI max", f"{top['vaccination_opportunity_index']:.1f}")
    col4, col5 = st.columns(2)
    col4.metric("N UFs", len(df))
    col5.metric("Ano base", str(int(df["reference_year"].max())) if "reference_year" in df.columns else "2024")

    left, right = st.columns([1.15, 0.85])
    with left:
        if geojson is not None:
            map_fig = choropleth_by_uf(
                df,
                geojson=geojson,
                value_column="vaccination_opportunity_index",
                title="Mapa de oportunidade vacinal por UF",
            )
            st.plotly_chart(map_fig, width="stretch")
    with right:
        ranking_fig = px.bar(
            df.head(10),
            x="vaccination_opportunity_index",
            y="uf",
            color="vaccination_opportunity_index",
            orientation="h",
            title="Top 10 UFs por VOI",
            labels={"uf": "UF", "vaccination_opportunity_index": "VOI"},
            color_continuous_scale="YlOrBr",
        )
        ranking_fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(ranking_fig, width="stretch")

    driver_fig = px.scatter(
        df,
        x="sanitary_pressure_score",
        y="economic_exposure_score",
        size="animal_exposure_score",
        text="uf",
        title="Drivers do indice por UF",
        labels={
            "sanitary_pressure_score": "Sanitary Pressure Score",
            "economic_exposure_score": "Economic Exposure Score",
            "animal_exposure_score": "Animal Exposure Score",
        },
    )
    driver_fig.update_traces(textposition="top center")
    st.plotly_chart(driver_fig, width="stretch")

    if not quarterly.empty:
        st.subheader("Comparacao temporal")
        selected_uf = st.selectbox("UF para serie trimestral", df["uf"].tolist(), index=0)
        qf = quarterly.loc[quarterly["uf"] == selected_uf].copy()
        qf["period"] = qf["reference_year"].astype(str) + "T" + qf["quarter"].astype(str)
        trend_fig = px.line(
            qf,
            x="period",
            y=["bovine_slaughter", "milk_production_liters"],
            markers=True,
            title=f"Atividade trimestral em {selected_uf}",
        )
        st.plotly_chart(trend_fig, width="stretch")

    st.subheader("Tabela analitica")
    st.dataframe(
        df[
            [
                "uf",
                "reference_year",
                "animal_exposure_score",
                "sanitary_pressure_score",
                "economic_exposure_score",
                "vaccination_opportunity_index",
            ]
        ],
        width="stretch",
    )

    manifest = load_source_manifest(settings.source_manifest_path)
    if not manifest.empty:
        st.subheader("Manifesto de fontes")
        st.dataframe(manifest, width="stretch")


if __name__ == "__main__":
    main()
