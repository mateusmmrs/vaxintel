"""Export presentation images for the VaxIntel README."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib import ticker
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a readable font for the hero image."""
    font_candidates = [
        "/usr/share/fonts/google-noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/google-noto/NotoSans-Bold.ttf",
        "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf",
        "/usr/share/fonts/liberation-sans/LiberationSans-Regular.ttf",
    ]
    for candidate in font_candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def _load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Load processed datasets and geospatial assets."""
    dataset = pd.read_parquet(ROOT / "data/processed/vaxintel_bovinos_uf.parquet")
    quarterly = pd.read_parquet(ROOT / "data/processed/bovines_quarterly_uf.parquet")
    geojson = json.loads((ROOT / "data/processed/brazil_ufs.geojson").read_text())
    return dataset, quarterly, geojson


def _write_hero(df: pd.DataFrame, output_path: Path) -> None:
    """Create a hero banner image for the repository README."""
    top = df.iloc[0]
    image = Image.new("RGB", (1600, 900), color=(247, 242, 234))
    draw = ImageDraw.Draw(image)
    title_font = _load_font(64)
    subtitle_font = _load_font(28)
    body_font = _load_font(34)
    small_font = _load_font(24)

    draw.rounded_rectangle((70, 60, 1530, 840), radius=36, fill=(255, 252, 246), outline=(221, 206, 187), width=3)
    draw.text((120, 120), "VaxIntel Brasil", fill=(58, 44, 30), font=title_font)
    draw.text(
        (120, 215),
        "Inteligencia territorial para priorizacao estrategica\n"
        "de vacinacao animal no Brasil",
        fill=(94, 76, 58),
        font=subtitle_font,
        spacing=10,
    )
    draw.text(
        (120, 360),
        "MVP bovinos | UF | Dados reais do IBGE | Scores configuraveis",
        fill=(171, 93, 21),
        font=body_font,
    )
    draw.rounded_rectangle((120, 460, 520, 720), radius=28, fill=(243, 232, 216))
    draw.rounded_rectangle((560, 460, 960, 720), radius=28, fill=(243, 232, 216))
    draw.rounded_rectangle((1000, 460, 1400, 720), radius=28, fill=(243, 232, 216))
    draw.text((155, 500), "UF lider", fill=(100, 81, 63), font=small_font)
    draw.text((155, 555), str(top["uf"]), fill=(58, 44, 30), font=_load_font(68))
    draw.text((595, 500), "VOI max", fill=(100, 81, 63), font=small_font)
    draw.text((595, 555), f"{top['vaccination_opportunity_index']:.1f}", fill=(58, 44, 30), font=_load_font(68))
    draw.text((1035, 500), "Ano base", fill=(100, 81, 63), font=small_font)
    draw.text((1035, 555), f"{int(df['reference_year'].max())}", fill=(58, 44, 30), font=_load_font(68))
    draw.text(
        (120, 770),
        "Mateus Martins | Medico Veterinario | Data Analyst",
        fill=(111, 95, 79),
        font=small_font,
    )
    image.save(output_path)


def main() -> None:
    """Export dashboard presentation assets into docs/images."""
    images_dir = ROOT / "docs/images"
    images_dir.mkdir(parents=True, exist_ok=True)
    df, quarterly, geojson = _load_inputs()

    _write_hero(df, images_dir / "hero-banner.png")

    geo_df = gpd.GeoDataFrame.from_features(geojson["features"], crs="EPSG:4326")
    map_df = geo_df.merge(df[["uf", "vaccination_opportunity_index"]], left_on="SIGLA_UF", right_on="uf", how="left")
    fig, ax = plt.subplots(figsize=(14, 9))
    fig.patch.set_facecolor("#fffaf3")
    ax.set_facecolor("#fffaf3")
    map_df.plot(
        column="vaccination_opportunity_index",
        cmap="YlOrBr",
        linewidth=0.6,
        edgecolor="#fff7ef",
        legend=True,
        ax=ax,
    )
    ax.set_title("Vaccination Opportunity Index por UF", loc="left", fontsize=20, color="#3a2c1e", pad=20)
    ax.axis("off")
    fig.savefig(images_dir / "dashboard-map.png", dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

    top_df = df.head(12).sort_values("vaccination_opportunity_index")
    fig, ax = plt.subplots(figsize=(14, 9))
    fig.patch.set_facecolor("#fffaf3")
    ax.set_facecolor("#fffaf3")
    ax.barh(top_df["uf"], top_df["vaccination_opportunity_index"], color="#bf7b1a")
    ax.set_title("Top UFs por Vaccination Opportunity Index", loc="left", fontsize=20, color="#3a2c1e", pad=20)
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter("%.0f"))
    ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(images_dir / "dashboard-ranking.png", dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(14, 9))
    fig.patch.set_facecolor("#fffaf3")
    ax.set_facecolor("#fffaf3")
    sizes = df["animal_exposure_score"].clip(lower=5) * 12
    scatter = ax.scatter(
        df["sanitary_pressure_score"],
        df["economic_exposure_score"],
        s=sizes,
        c=df["vaccination_opportunity_index"],
        cmap="YlOrBr",
        alpha=0.85,
        edgecolors="#6d5235",
        linewidths=0.6,
    )
    for _, row in df.iterrows():
        ax.annotate(row["uf"], (row["sanitary_pressure_score"], row["economic_exposure_score"]), xytext=(4, 4), textcoords="offset points", fontsize=9)
    ax.set_title("Drivers do indice por UF", loc="left", fontsize=20, color="#3a2c1e", pad=20)
    ax.set_xlabel("Sanitary Pressure Score")
    ax.set_ylabel("Economic Exposure Score")
    fig.colorbar(scatter, ax=ax, label="VOI")
    fig.savefig(images_dir / "dashboard-drivers.png", dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

    selected = df.iloc[0]["uf"]
    qf = quarterly.loc[quarterly["uf"] == selected].copy()
    qf["period"] = qf["reference_year"].astype(str) + "T" + qf["quarter"].astype(str)
    fig, ax1 = plt.subplots(figsize=(14, 9))
    fig.patch.set_facecolor("#fffaf3")
    ax1.set_facecolor("#fffaf3")
    ax1.plot(qf["period"], qf["bovine_slaughter"], color="#a85b17", marker="o", linewidth=2.5, label="Bovinos abatidos")
    ax1.set_ylabel("Bovinos abatidos", color="#a85b17")
    ax1.tick_params(axis="y", labelcolor="#a85b17")
    ax2 = ax1.twinx()
    ax2.plot(qf["period"], qf["milk_production_liters"], color="#5c7c58", marker="o", linewidth=2.5, label="Leite adquirido")
    ax2.set_ylabel("Leite adquirido (litros)", color="#5c7c58")
    ax2.tick_params(axis="y", labelcolor="#5c7c58")
    ax1.set_title(f"Atividade trimestral em {selected}", loc="left", fontsize=20, color="#3a2c1e", pad=20)
    ax1.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)
    fig.savefig(images_dir / "dashboard-timeseries.png", dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


if __name__ == "__main__":
    main()
