"""Aplicação Streamlit do VaxIntel Brasil v2."""
# ruff: noqa: E402

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vaxintel.config import settings
from vaxintel.utils.metadata import load_source_manifest
from vaxintel.visualization.maps import choropleth_by_uf

MODE_LABELS = {
    "beef": "Corte",
    "dairy": "Leite",
    "combined": "Combinado",
}
MODE_SCORE_COLUMN = {
    "beef": "beef_opportunity_score",
    "dairy": "dairy_opportunity_score",
    "combined": "combined_vaccination_opportunity_index",
}
MODE_ECONOMIC_COLUMN = {
    "beef": "beef_economic_score",
    "dairy": "dairy_economic_score",
    "combined": "economic_exposure_score_combined",
}


@st.cache_data
def load_dataset() -> pd.DataFrame:
    """Carrega o dataset processado v2 em nível de UF."""
    return pd.read_parquet(settings.processed_dataset_path)


@st.cache_data
def load_quarterly() -> pd.DataFrame:
    """Carrega a base trimestral v2."""
    if not settings.processed_quarterly_path.exists():
        return pd.DataFrame()
    return pd.read_parquet(settings.processed_quarterly_path)


@st.cache_data
def load_geojson() -> dict | None:
    """Carrega o GeoJSON processado das UFs."""
    if not settings.processed_geojson_path.exists():
        return None
    return json.loads(settings.processed_geojson_path.read_text())


@st.cache_data
def load_methodology_markdown() -> str:
    """Carrega a metodologia em markdown para exibição no app."""
    methodology_path = ROOT / "docs" / "methodology.md"
    return methodology_path.read_text() if methodology_path.exists() else ""


def get_mode_score_column(mode: str) -> str:
    """Retorna a coluna do score correspondente ao modo selecionado."""
    return MODE_SCORE_COLUMN[mode]


def get_mode_economic_column(mode: str) -> str:
    """Retorna a coluna econômica correspondente ao modo selecionado."""
    return MODE_ECONOMIC_COLUMN[mode]


def get_top_uf(df: pd.DataFrame, score_column: str) -> pd.Series:
    """Retorna a UF líder para uma coluna de score."""
    return df.sort_values(score_column, ascending=False).iloc[0]


def get_most_balanced_uf(df: pd.DataFrame) -> pd.Series:
    """Retorna a UF com menor distância entre corte e leite."""
    balanced = df.assign(balance_gap=(df["beef_opportunity_score"] - df["dairy_opportunity_score"]).abs())
    return balanced.sort_values(["balance_gap", "combined_vaccination_opportunity_index"], ascending=[True, False]).iloc[0]


def classify_profile(row: pd.Series) -> str:
    """Explica se a UF é mais orientada a corte, leite ou ambos."""
    gap = row["beef_opportunity_score"] - row["dairy_opportunity_score"]
    if gap >= 7.5:
        return "Território mais orientado a corte"
    if gap <= -7.5:
        return "Território mais orientado a leite"
    return "Território de perfil misto"


def explain_top_driver(row: pd.Series, mode: str) -> str:
    """Explica qual bloco mais puxou a UF para cima."""
    if mode == "beef":
        drivers = {
            "Exposição animal": row["animal_exposure_score"],
            "Pressão sanitária": row["sanitary_pressure_score"],
            "Economia do corte": row["beef_economic_score"],
        }
    elif mode == "dairy":
        drivers = {
            "Exposição animal": row["animal_exposure_score"],
            "Pressão sanitária": row["sanitary_pressure_score"],
            "Economia do leite": row["dairy_economic_score"],
        }
    else:
        drivers = {
            "Corte": row["beef_opportunity_score"],
            "Leite": row["dairy_opportunity_score"],
        }
    return max(drivers, key=drivers.get)


def build_executive_summary(df: pd.DataFrame) -> str:
    """Cria uma leitura executiva curta do ranking combinado."""
    combined = get_top_uf(df, "combined_vaccination_opportunity_index")
    beef = get_top_uf(df, "beef_opportunity_score")
    dairy = get_top_uf(df, "dairy_opportunity_score")
    return (
        f"{combined['uf']} lidera o modo combinado, {beef['uf']} concentra a maior força relativa no corte "
        f"e {dairy['uf']} aparece como principal território do leite no cenário atual."
    )


def build_unified_mode_frame(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Organiza scores de corte, leite e combinado em formato longo."""
    top = df.sort_values("combined_vaccination_opportunity_index", ascending=False).head(top_n).copy()
    long_df = top.melt(
        id_vars=["uf", "territory_profile"],
        value_vars=[
            "beef_opportunity_score",
            "dairy_opportunity_score",
            "combined_vaccination_opportunity_index",
        ],
        var_name="score_type",
        value_name="score",
    )
    label_map = {
        "beef_opportunity_score": "Corte",
        "dairy_opportunity_score": "Leite",
        "combined_vaccination_opportunity_index": "Combinado",
    }
    long_df["modo"] = long_df["score_type"].map(label_map)
    return long_df


def build_component_heatmap_frame(df: pd.DataFrame, top_n: int = 12) -> pd.DataFrame:
    """Prepara a matriz de componentes para leitura unificada."""
    top = df.sort_values("combined_vaccination_opportunity_index", ascending=False).head(top_n).copy()
    return top[
        [
            "uf",
            "animal_exposure_score",
            "sanitary_pressure_score",
            "beef_economic_score",
            "dairy_economic_score",
            "beef_opportunity_score",
            "dairy_opportunity_score",
            "combined_vaccination_opportunity_index",
        ]
    ].set_index("uf")


def render_weight_sidebar() -> None:
    """Exibe a lógica de pesos utilizada na v2."""
    st.sidebar.header("Arquitetura de scores")
    st.sidebar.markdown(
        """
        **Motores analíticos**

        - Corte
        - Leite
        - Combinado

        **Blocos**

        - Exposição animal
        - Pressão sanitária indireta
        - Economia do corte
        - Economia do leite
        """
    )
    st.sidebar.subheader("Pesos padrão")
    st.sidebar.caption(
        f"Corte: {settings.score_config.beef_opportunity.animal:.0%} animal · "
        f"{settings.score_config.beef_opportunity.sanitary:.0%} sanitário · "
        f"{settings.score_config.beef_opportunity.economic:.0%} econômico"
    )
    st.sidebar.caption(
        f"Leite: {settings.score_config.dairy_opportunity.animal:.0%} animal · "
        f"{settings.score_config.dairy_opportunity.sanitary:.0%} sanitário · "
        f"{settings.score_config.dairy_opportunity.economic:.0%} econômico"
    )
    st.sidebar.caption(
        f"Combinado: {settings.score_config.combined_mode.beef:.0%} corte · "
        f"{settings.score_config.combined_mode.dairy:.0%} leite"
    )
    st.sidebar.info(
        "O ano-base padrão é 2024 porque esse é o corte anual mais consistente para harmonizar rebanho, abate e leite em uma base fechada."
    )


def main() -> None:
    """Renderiza a versão v2 do dashboard."""
    st.set_page_config(page_title="VaxIntel Brasil v2", page_icon="🐄", layout="wide")
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(194, 126, 42, 0.14), transparent 24%),
                radial-gradient(circle at 85% 12%, rgba(27, 94, 73, 0.10), transparent 20%),
                linear-gradient(180deg, #f6f1e8 0%, #fcfbf8 52%, #f0ede6 100%);
            color: #1f2a24;
            font-family: "SF Pro Display", "Helvetica Neue", Helvetica, Arial, sans-serif;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1400px;
        }
        .vx-hero {
            background: linear-gradient(135deg, rgba(17, 55, 43, 0.97), rgba(33, 92, 73, 0.92));
            border-radius: 28px;
            padding: 2rem 2.2rem;
            color: #f7f2e9;
            margin-bottom: 1rem;
            box-shadow: 0 18px 42px rgba(22, 41, 33, 0.16);
        }
        .vx-hero h1 {
            color: #f7f2e9;
            margin-bottom: 0.45rem;
        }
        .vx-callout {
            background: rgba(255,255,255,0.72);
            border-left: 5px solid #b97a28;
            border-radius: 18px;
            padding: 1rem 1.1rem;
            margin-bottom: 1rem;
        }
        .vx-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(250,246,239,0.98));
            border: 1px solid rgba(53, 74, 63, 0.08);
            border-radius: 18px;
            padding: 0.95rem 1rem;
            box-shadow: 0 12px 28px rgba(39, 43, 36, 0.05);
        }
        .vx-card-label {
            color: #8d6f4e;
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }
        .vx-card-title {
            color: #1f2a24;
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }
        .vx-card-text {
            color: #5b655f;
            font-size: 0.95rem;
            line-height: 1.45;
        }
        button[role="tab"] {
            border-radius: 999px;
            border: 1px solid rgba(53, 74, 63, 0.08);
            background: rgba(255,255,255,0.62);
            padding: 0.45rem 0.9rem;
            margin-right: 0.35rem;
        }
        button[role="tab"][aria-selected="true"] {
            background: #173d31;
            color: #f7f2e9;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if not settings.processed_dataset_path.exists():
        st.warning("Execute o pipeline antes de abrir o app.")
        st.stop()

    render_weight_sidebar()
    df = load_dataset().copy()
    quarterly = load_quarterly()
    geojson = load_geojson()
    methodology_md = load_methodology_markdown()

    st.markdown(
        f"""
        <div class="vx-hero">
            <div style="font-size:0.82rem;font-weight:700;letter-spacing:0.06em;color:#f4d39a;text-transform:uppercase;">VaxIntel Brasil · v2 bovinos</div>
            <h1>Inteligência territorial para corte, leite e leitura combinada</h1>
            <div style="max-width:960px;font-size:1.05rem;line-height:1.6;color:rgba(247,242,233,0.92);">
                Plataforma analítica para identificar onde estratégias de vacinação bovina combinam melhor escala animal,
                intensidade produtiva e valor econômico exposto. Ano-base atual: <strong>{int(df['reference_year'].max())}</strong>.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="vx-callout"><strong>Leitura executiva:</strong> {build_executive_summary(df)}</div>', unsafe_allow_html=True)

    tab_exec, tab_drivers, tab_time, tab_data, tab_method = st.tabs(
        ["Visão executiva", "Drivers por UF", "Evolução temporal", "Base analítica", "Metodologia"]
    )

    with tab_exec:
        top_beef = get_top_uf(df, "beef_opportunity_score")
        top_dairy = get_top_uf(df, "dairy_opportunity_score")
        top_combined = get_top_uf(df, "combined_vaccination_opportunity_index")
        most_balanced = get_most_balanced_uf(df)
        cards = st.columns(4)
        cards[0].markdown(
            f'<div class="vx-card"><div class="vx-card-label">Top UF no corte</div><div class="vx-card-title">{top_beef["uf"]}</div><div class="vx-card-text">Score {top_beef["beef_opportunity_score"]:.1f}</div></div>',
            unsafe_allow_html=True,
        )
        cards[1].markdown(
            f'<div class="vx-card"><div class="vx-card-label">Top UF no leite</div><div class="vx-card-title">{top_dairy["uf"]}</div><div class="vx-card-text">Score {top_dairy["dairy_opportunity_score"]:.1f}</div></div>',
            unsafe_allow_html=True,
        )
        cards[2].markdown(
            f'<div class="vx-card"><div class="vx-card-label">Top UF combinado</div><div class="vx-card-title">{top_combined["uf"]}</div><div class="vx-card-text">Score {top_combined["combined_vaccination_opportunity_index"]:.1f}</div></div>',
            unsafe_allow_html=True,
        )
        cards[3].markdown(
            f'<div class="vx-card"><div class="vx-card-label">UF mais equilibrada</div><div class="vx-card-title">{most_balanced["uf"]}</div><div class="vx-card-text">{classify_profile(most_balanced)}</div></div>',
            unsafe_allow_html=True,
        )

        mode = st.radio("Modo de leitura", ["beef", "dairy", "combined"], horizontal=True, format_func=lambda x: MODE_LABELS[x])
        score_column = get_mode_score_column(mode)
        economic_column = get_mode_economic_column(mode)
        top_labels = set(df.sort_values(score_column, ascending=False).head(5)["uf"])

        left, right = st.columns([1.15, 0.85])
        with left:
            if geojson is not None:
                map_fig = choropleth_by_uf(
                    df.assign(selected_mode_score=df[score_column]),
                    geojson=geojson,
                    value_column="selected_mode_score",
                    title=f"Mapa de oportunidade - {MODE_LABELS[mode]}",
                )
                map_fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    coloraxis_colorbar_title="Score",
                    margin=dict(l=0, r=0, t=56, b=0),
                )
                st.plotly_chart(map_fig, width="stretch")
        with right:
            ranking_fig = px.bar(
                df.sort_values(score_column, ascending=False).head(10),
                x=score_column,
                y="uf",
                orientation="h",
                color="territory_profile",
                title=f"Top 10 - modo {MODE_LABELS[mode]}",
                labels={score_column: "Score", "uf": "UF"},
                color_discrete_map={
                    "Território de corte": "#a85d1a",
                    "Território de leite": "#2f7d68",
                    "Território misto": "#c59a59",
                },
            )
            ranking_fig.update_layout(
                yaxis={"categoryorder": "total ascending"},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=56, b=0),
            )
            st.plotly_chart(ranking_fig, width="stretch")

        st.caption(
            "O ranking final não é um ranking de tamanho de rebanho. Uma UF pode ter grande massa animal e ainda perder posição se for relativamente mais fraca em intensidade produtiva, valor econômico exposto ou equilíbrio entre corte e leite."
        )

        bubble_fig = px.scatter(
            df,
            x="sanitary_pressure_score",
            y=economic_column,
            size="animal_exposure_score",
            color=score_column,
            text=df["uf"].where(df["uf"].isin(top_labels), ""),
            color_continuous_scale=["#e7d6b8", "#d88b2e", "#8f4d19"],
            title=f"Drivers da oportunidade - modo {MODE_LABELS[mode]}",
            labels={
                "sanitary_pressure_score": "Pressão sanitária indireta",
                economic_column: "Exposição econômica",
                "animal_exposure_score": "Exposição animal",
                score_column: "Índice do modo",
            },
        )
        bubble_fig.update_traces(textposition="middle center", marker=dict(line=dict(width=1, color="rgba(31,42,36,0.18)")))
        bubble_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0.55)",
            margin=dict(l=0, r=0, t=56, b=0),
        )
        st.plotly_chart(bubble_fig, width="stretch")

        st.markdown("### Comparativo unificado entre corte e leite")
        compare_left, compare_right = st.columns([1.05, 0.95])

        with compare_left:
            comparison = build_unified_mode_frame(df, top_n=10)
            unified_fig = px.bar(
                comparison,
                x="score",
                y="uf",
                color="modo",
                barmode="group",
                orientation="h",
                title="Top 10 UFs com leitura paralela de corte, leite e combinado",
                color_discrete_map={
                    "Corte": "#b76f20",
                    "Leite": "#2f7d68",
                    "Combinado": "#173d31",
                },
                labels={"score": "Score", "uf": "UF", "modo": "Modo"},
            )
            unified_fig.update_layout(
                yaxis={"categoryorder": "total ascending"},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(255,255,255,0.55)",
                margin=dict(l=0, r=0, t=56, b=0),
                legend_title_text="Modo",
            )
            st.plotly_chart(unified_fig, width="stretch")

        with compare_right:
            heatmap_df = build_component_heatmap_frame(df, top_n=12)
            heatmap_fig = go.Figure(
                data=go.Heatmap(
                    z=heatmap_df.values,
                    x=[
                        "Animal",
                        "Sanitário",
                        "Econ. corte",
                        "Econ. leite",
                        "Score corte",
                        "Score leite",
                        "Combinado",
                    ],
                    y=heatmap_df.index.tolist(),
                    colorscale=[
                        [0.0, "#f1e6cf"],
                        [0.45, "#d79643"],
                        [1.0, "#1b4c3d"],
                    ],
                    colorbar_title="Score",
                )
            )
            heatmap_fig.update_layout(
                title="Leitura matricial dos componentes por UF",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(255,255,255,0.55)",
                margin=dict(l=0, r=0, t=56, b=0),
            )
            st.plotly_chart(heatmap_fig, width="stretch")
        st.caption(
            "Esses dois gráficos mostram, na mesma leitura, como corte e leite coexistem por UF. O objetivo é evidenciar territórios dominados por uma cadeia, territórios equilibrados e a forma como isso se transforma no índice combinado."
        )

    with tab_drivers:
        selected_uf = st.selectbox("Selecione uma UF", df["uf"].tolist(), index=0)
        row = df.loc[df["uf"] == selected_uf].iloc[0]
        metrics = st.columns(3)
        metrics[0].metric("Score de corte", f"{row['beef_opportunity_score']:.1f}")
        metrics[1].metric("Score de leite", f"{row['dairy_opportunity_score']:.1f}")
        metrics[2].metric("Score combinado", f"{row['combined_vaccination_opportunity_index']:.1f}")
        st.markdown(
            f'<div class="vx-callout"><strong>Perfil territorial:</strong> {classify_profile(row)}. '
            f'<strong>Bloco dominante no combinado:</strong> {explain_top_driver(row, "combined")}.</div>',
            unsafe_allow_html=True,
        )

        decomposition = pd.DataFrame(
            {
                "Bloco": [
                    "Exposição animal",
                    "Pressão sanitária",
                    "Economia do corte",
                    "Economia do leite",
                    "Score de corte",
                    "Score de leite",
                    "Índice combinado",
                ],
                "Valor": [
                    row["animal_exposure_score"],
                    row["sanitary_pressure_score"],
                    row["beef_economic_score"],
                    row["dairy_economic_score"],
                    row["beef_opportunity_score"],
                    row["dairy_opportunity_score"],
                    row["combined_vaccination_opportunity_index"],
                ],
            }
        )
        decomposition_fig = px.bar(
            decomposition,
            x="Valor",
            y="Bloco",
            orientation="h",
            color="Bloco",
            title=f"Decomposição analítica - {selected_uf}",
        )
        decomposition_fig.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(decomposition_fig, width="stretch")

    with tab_time:
        if quarterly.empty:
            st.info("A base trimestral ainda não está disponível.")
        else:
            category = st.radio("Leitura temporal", ["Corte", "Leite"], horizontal=True)
            selected_uf = st.selectbox("UF temporal", df["uf"].tolist(), index=0, key="uf_temporal")
            if category == "Corte":
                metric_options = {
                    "Bovinos abatidos": "bovine_slaughter",
                    "Peso de carcaças (kg)": "carcass_weight_kg",
                }
            else:
                metric_options = {
                    "Leite adquirido (litros)": "milk_production_liters",
                    "Preço do leite (R$/litro)": "milk_price_brl_per_liter",
                    "Valor estimado do leite (R$)": "estimated_milk_value_brl",
                }
            metric_label = st.radio("Métrica", list(metric_options), horizontal=True)
            qf = quarterly.loc[quarterly["uf"] == selected_uf].copy()
            qf["Período"] = qf["reference_year"].astype(str) + " T" + qf["quarter"].astype(str)
            trend_fig = px.line(
                qf,
                x="Período",
                y=metric_options[metric_label],
                markers=True,
                title=f"{metric_label} em {selected_uf}",
                labels={metric_options[metric_label]: metric_label},
            )
            trend_fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(255,255,255,0.58)",
                margin=dict(l=0, r=0, t=56, b=0),
            )
            st.plotly_chart(trend_fig, width="stretch")

    with tab_data:
        dataset_view = df[
            [
                "uf",
                "reference_year",
                "animal_exposure_score",
                "sanitary_pressure_score",
                "beef_economic_score",
                "dairy_economic_score",
                "beef_opportunity_score",
                "dairy_opportunity_score",
                "combined_vaccination_opportunity_index",
                "territory_profile",
                "combined_band",
                "final_methodological_note",
            ]
        ].copy()
        st.dataframe(dataset_view, width="stretch", hide_index=True)
        manifest = load_source_manifest(settings.source_manifest_path)
        if not manifest.empty:
            with st.expander("Manifesto de fontes"):
                st.dataframe(manifest, width="stretch", hide_index=True)

    with tab_method:
        st.markdown(
            """
            ### Como interpretar a v2

            - **Corte**: prioriza o peso relativo da cadeia de abate e carcaças.
            - **Leite**: prioriza volume, preço e valor estimado da cadeia leiteira.
            - **Combinado**: integra os dois motores em uma leitura territorial única.

            ### Como usar comercialmente

            - Priorização territorial da equipe comercial.
            - Planejamento de campanhas técnicas e visitas a campo.
            - Segmentação entre territórios de corte, leite ou perfil misto.
            - Suporte à defesa de budget com racional analítico.

            ### O que o bloco sanitário mede

            Proxy de intensidade territorial, baseada em densidade bovina, intensidade de abate e intensidade leiteira. Não representa vigilância epidemiológica causal.

            ### O que o índice não mede

            - Cobertura vacinal real.
            - Eficácia de produto.
            - Probabilidade causal de surto.
            - Impacto econômico causal de uma intervenção específica.
            """
        )
        st.markdown(methodology_md)


if __name__ == "__main__":
    main()
