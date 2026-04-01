"""Exporta imagens de apresentação para o README do VaxIntel."""

from __future__ import annotations

import json
import sys
import textwrap
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

plt.rcParams["font.family"] = ["SF Pro Display", "Nimbus Sans", "sans-serif"]
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.titlesize"] = 24
plt.rcParams["axes.labelsize"] = 13


def _load_font(size: int, weight: str = "regular") -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Carrega uma fonte legível para a imagem de capa."""
    font_candidates = [
        f"/home/mateus/.local/share/fonts/SF/SF-Pro-Display-{'Bold' if weight == 'bold' else 'Regular'}.otf",
        "/usr/share/fonts/urw-base35/NimbusSans-Regular.otf",
        "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    ]
    for candidate in font_candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def _load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Carrega os datasets processados e os ativos geográficos."""
    dataset = pd.read_parquet(ROOT / "data/processed/vaxintel_bovinos_uf.parquet")
    quarterly = pd.read_parquet(ROOT / "data/processed/bovines_quarterly_uf.parquet")
    geojson = json.loads((ROOT / "data/processed/brazil_ufs.geojson").read_text())
    return dataset, quarterly, geojson


def _write_hero(df: pd.DataFrame, output_path: Path) -> None:
    """Cria a imagem de capa principal do repositório."""
    top = df.sort_values("combined_vaccination_opportunity_index", ascending=False).iloc[0]
    image = Image.new("RGB", (1600, 900), color=(245, 240, 232))
    draw = ImageDraw.Draw(image)
    title_font = _load_font(70, weight="bold")
    subtitle_font = _load_font(22)
    body_font = _load_font(22)
    small_font = _load_font(22, weight="bold")
    metric_label_font = _load_font(22)
    metric_value_font = _load_font(60, weight="bold")

    draw.rounded_rectangle((54, 54, 1546, 846), radius=42, fill=(252, 249, 243), outline=(219, 201, 173), width=3)
    draw.rounded_rectangle((86, 98, 1002, 812), radius=36, fill=(22, 58, 47))
    draw.rounded_rectangle((1030, 98, 1514, 812), radius=36, fill=(242, 231, 213))
    draw.rounded_rectangle((122, 138, 430, 190), radius=24, fill=(48, 102, 85))
    draw.text((150, 152), "VAXINTEL BRASIL · V2", fill=(244, 220, 177), font=_load_font(19, weight="bold"))
    draw.text((122, 232), "Inteligência territorial\npara vacinação bovina", fill=(247, 242, 232), font=title_font, spacing=4)
    draw.text(
        (126, 462),
        "Plataforma analítica para identificar onde estratégias de vacinação\n"
        "bovina combinam melhor escala animal, intensidade produtiva\n"
        "e valor econômico exposto em corte, leite e modo combinado.",
        fill=(214, 229, 223),
        font=subtitle_font,
        spacing=10,
    )
    draw.rounded_rectangle((122, 684, 760, 758), radius=22, fill=(198, 128, 43))
    draw.text((148, 705), "Bovinos | UFs | Corte, Leite e Combinado | Pesos Configuráveis", fill=(255, 248, 239), font=body_font)

    draw.text((1082, 140), "Resumo Executivo", fill=(92, 68, 43), font=_load_font(26, weight="bold"))
    draw.text(
        (1082, 204),
        "Leitura executiva\npara corte, leite\n e modo combinado.".replace("\n ", "\n"),
        fill=(51, 39, 28),
        font=_load_font(26, weight="bold"),
        spacing=6,
    )
    draw.rounded_rectangle((1080, 346, 1464, 500), radius=26, fill=(250, 244, 234))
    draw.rounded_rectangle((1080, 530, 1464, 684), radius=26, fill=(250, 244, 234))
    draw.rounded_rectangle((1080, 714, 1464, 786), radius=22, fill=(219, 201, 173))

    draw.text((1118, 380), "UF Líder", fill=(116, 97, 78), font=metric_label_font)
    draw.text((1118, 426), str(top["uf"]), fill=(45, 34, 24), font=metric_value_font)
    draw.text((1118, 564), "VOI Combinado", fill=(116, 97, 78), font=metric_label_font)
    draw.text((1118, 610), f"{top['combined_vaccination_opportunity_index']:.1f}", fill=(45, 34, 24), font=metric_value_font)
    draw.text((1118, 734), f"Ano-base {int(df['reference_year'].max())}", fill=(74, 57, 41), font=_load_font(28, weight="bold"))
    draw.text((122, 780), "Mateus Martins | Médico Veterinário | Data Analyst", fill=(213, 225, 220), font=small_font)
    image.save(output_path)


def _style_axes(ax, title: str, xlabel: str | None = None, ylabel: str | None = None) -> None:
    """Aplica estilo editorial consistente aos gráficos."""
    ax.set_title(title, loc="left", fontsize=24, color="#2a231d", pad=18, fontweight="bold")
    if xlabel:
        ax.set_xlabel(xlabel, color="#594a3a")
    if ylabel:
        ax.set_ylabel(ylabel, color="#594a3a")
    ax.tick_params(colors="#4e453b", labelsize=12)
    ax.grid(color="#dccfbf", alpha=0.45, linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#d6c5ad")
    ax.spines["bottom"].set_color("#d6c5ad")


def _measure_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont, spacing: int = 4) -> tuple[int, int]:
    """Return rendered text width and height."""
    left, top, right, bottom = draw.multiline_textbbox((0, 0), text, font=font, spacing=spacing)
    return right - left, bottom - top


def _wrap_text_to_width(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    max_width: int,
    spacing: int = 4,
) -> str:
    """Wrap text to fit a maximum width in pixels."""
    wrapped_lines: list[str] = []
    for raw_line in text.splitlines():
        words = raw_line.split()
        if not words:
            wrapped_lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            trial = f"{current} {word}"
            width, _ = _measure_text(draw, trial, font, spacing=spacing)
            if width <= max_width:
                current = trial
            else:
                wrapped_lines.append(current)
                current = word
        wrapped_lines.append(current)
    return "\n".join(wrapped_lines)


def _fit_wrapped_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_loader,
    initial_size: int,
    min_size: int,
    max_width: int,
    max_height: int,
    weight: str = "regular",
    spacing: int = 6,
) -> tuple[ImageFont.FreeTypeFont | ImageFont.ImageFont, str]:
    """Reduce font size until wrapped text fits the target box."""
    for size in range(initial_size, min_size - 1, -1):
        font = font_loader(size, weight=weight)
        wrapped = _wrap_text_to_width(draw, text, font, max_width=max_width, spacing=spacing)
        _, height = _measure_text(draw, wrapped, font, spacing=spacing)
        if height <= max_height:
            return font, wrapped
    font = font_loader(min_size, weight=weight)
    wrapped = _wrap_text_to_width(draw, text, font, max_width=max_width, spacing=spacing)
    return font, wrapped


def _draw_info_card(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    body: str,
    accent: tuple[int, int, int],
    title_size: int = 26,
    body_size: int = 22,
) -> None:
    """Draw a card with top accent, title and wrapped body."""
    x1, y1, x2, y2 = box
    inner_width = x2 - x1 - 48
    draw.rounded_rectangle(box, radius=28, fill=(248, 243, 234), outline=(224, 213, 194), width=2)
    draw.rounded_rectangle((x1 + 18, y1 + 16, x1 + 120, y1 + 28), radius=6, fill=accent)

    title_font, wrapped_title = _fit_wrapped_text(
        draw,
        title,
        _load_font,
        initial_size=title_size,
        min_size=20,
        max_width=inner_width,
        max_height=70,
        weight="bold",
        spacing=4,
    )
    draw.multiline_text((x1 + 24, y1 + 38), wrapped_title, fill=(45, 62, 53), font=title_font, spacing=4)

    _, title_height = _measure_text(draw, wrapped_title, title_font, spacing=4)
    body_top = y1 + 38 + title_height + 22
    body_max_height = y2 - body_top - 24
    body_font, wrapped_body = _fit_wrapped_text(
        draw,
        body,
        _load_font,
        initial_size=body_size,
        min_size=18,
        max_width=inner_width,
        max_height=body_max_height,
        spacing=8,
    )
    draw.multiline_text((x1 + 24, body_top), wrapped_body, fill=(88, 80, 70), font=body_font, spacing=8)


def _write_project_overview(output_path: Path) -> None:
    """Cria uma imagem-resumo explicando o produto."""
    image = Image.new("RGB", (1600, 920), color=(246, 241, 232))
    draw = ImageDraw.Draw(image)
    title_font = _load_font(48, weight="bold")
    subtitle_font = _load_font(24)
    draw.rounded_rectangle((44, 44, 1556, 876), radius=42, fill=(252, 249, 243), outline=(219, 201, 173), width=3)
    draw.text((90, 90), "Como o VaxIntel Brasil funciona", fill=(29, 41, 35), font=title_font)
    draw.text(
        (90, 160),
        "Plataforma de inteligência territorial para identificar onde vacinação bovina combina melhor escala animal,\n"
        "intensidade produtiva e valor econômico exposto, com leitura separada de corte, leite e modo combinado.",
        fill=(83, 88, 80),
        font=subtitle_font,
        spacing=8,
    )

    cards = [
        ((90, 280, 500, 560), "Entradas reais", "Rebanho bovino\nAbate e carcaças\nLeite e preço do leite\nGeometrias oficiais do IBGE", (214, 166, 88)),
        ((540, 280, 950, 560), "Motores analíticos", "Exposição animal\nPressão sanitária indireta\nEconomia do corte\nEconomia do leite", (64, 112, 96)),
        ((990, 280, 1400, 560), "Saídas do produto", "Score de corte\nScore de leite\nÍndice combinado\nPerfil territorial por UF", (191, 126, 50)),
        ((90, 600, 500, 820), "Pergunta de negócio", "Onde está a melhor combinação entre escala, intensidade produtiva e valor econômico exposto?", (50, 94, 77)),
        ((540, 600, 950, 820), "Uso comercial", "Priorização territorial\nPlanejamento de campo\nGo-to-market regional\nDefesa de budget", (183, 139, 68)),
        ((990, 600, 1400, 820), "Leitura responsável", "Não mede cobertura vacinal\nNão mede eficácia vacinal\nNão substitui vigilância epidemiológica", (103, 116, 96)),
    ]
    for box, title, body, accent in cards:
        _draw_info_card(draw, box, title, body, accent, title_size=25, body_size=21)
    image.save(output_path)


def _write_project_business_use(output_path: Path) -> None:
    """Cria uma imagem com as aplicações comerciais do projeto."""
    image = Image.new("RGB", (1600, 920), color=(243, 239, 229))
    draw = ImageDraw.Draw(image)
    title_font = _load_font(46, weight="bold")
    subtitle_font = _load_font(23)
    draw.rounded_rectangle((44, 44, 1556, 876), radius=42, fill=(251, 248, 242), outline=(209, 196, 174), width=3)
    draw.text((90, 90), "Como usar o VaxIntel em saúde animal", fill=(30, 44, 37), font=title_font)
    draw.text(
        (90, 156),
        "A plataforma foi desenhada para apoiar decisão comercial e técnica, sem vender causalidade onde o dado não permite.",
        fill=(90, 89, 80),
        font=subtitle_font,
    )
    boxes = [
        ((90, 250, 450, 470), "Equipe comercial", "Priorizar UFs\nRoteirizar visitas\nAlocar cobertura regional", (189, 140, 63)),
        ((490, 250, 850, 470), "Marketing técnico", "Selecionar territórios\nPlanejar campanhas\nAdaptar discurso por cadeia", (57, 106, 87)),
        ((890, 250, 1250, 470), "Liderança", "Defender budget\nComparar territórios\nRevisar tese regional", (95, 112, 93)),
        ((1290, 250, 1510, 470), "Produto", "Separar corte e leite\nEntender perfil misto\nAvaliar equilíbrio territorial", (179, 152, 91)),
        ((90, 520, 725, 820), "O que os gráficos unificados mostram", "Quem sobe por força do corte.\nQuem sobe por força do leite.\nQuais UFs são equilibradas.\nComo os componentes convergem no índice combinado.", (40, 86, 69)),
        ((765, 520, 1510, 820), "Por que isso é melhor do que olhar só rebanho", "Uma UF pode ter muito gado e ainda assim não liderar. Se perder em intensidade produtiva, exposição econômica ou equilíbrio entre as cadeias, ela cai no ranking final.", (185, 128, 63)),
    ]
    for box, title, body, accent in boxes:
        _draw_info_card(draw, box, title, body, accent, title_size=24, body_size=20)
    image.save(output_path)


def main() -> None:
    """Exporta os assets visuais do dashboard para docs/images."""
    images_dir = ROOT / "docs/images"
    images_dir.mkdir(parents=True, exist_ok=True)
    df, quarterly, geojson = _load_inputs()

    _write_hero(df, images_dir / "hero-banner.png")

    geo_df = gpd.GeoDataFrame.from_features(geojson["features"], crs="EPSG:4326")
    map_df = geo_df.merge(df[["uf", "combined_vaccination_opportunity_index"]], left_on="SIGLA_UF", right_on="uf", how="left")
    fig, ax = plt.subplots(figsize=(14, 9))
    fig.patch.set_facecolor("#f8f4ec")
    ax.set_facecolor("#f8f4ec")
    map_df.plot(
        column="combined_vaccination_opportunity_index",
        cmap="YlOrBr",
        linewidth=0.8,
        edgecolor="#fcfbf8",
        legend=True,
        ax=ax,
    )
    ax.set_title("Mapa do índice combinado por UF", loc="left", fontsize=24, color="#2a231d", pad=20, fontweight="bold")
    ax.axis("off")
    fig.savefig(images_dir / "dashboard-map.png", dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

    top_df = df.sort_values("combined_vaccination_opportunity_index", ascending=False).head(12).sort_values("combined_vaccination_opportunity_index")
    fig, ax = plt.subplots(figsize=(14, 9))
    fig.patch.set_facecolor("#f8f4ec")
    ax.set_facecolor("#f8f4ec")
    ax.barh(top_df["uf"], top_df["combined_vaccination_opportunity_index"], color="#b76f20", height=0.65)
    _style_axes(ax, "Ranking das UFs por índice combinado")
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter("%.0f"))
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color="#e4d7c3", alpha=0.6, linewidth=0.8)
    for idx, (_, row) in enumerate(top_df.iterrows()):
        ax.text(row["combined_vaccination_opportunity_index"] + 0.8, idx, f"{row['combined_vaccination_opportunity_index']:.1f}", va="center", fontsize=11, color="#6a573f")
    fig.savefig(images_dir / "dashboard-ranking.png", dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(14, 9))
    fig.patch.set_facecolor("#f8f4ec")
    ax.set_facecolor("#f8f4ec")
    sizes = df["animal_exposure_score"].clip(lower=5) * 12
    scatter = ax.scatter(
        df["sanitary_pressure_score"],
        df["economic_exposure_score_combined"],
        s=sizes,
        c=df["combined_vaccination_opportunity_index"],
        cmap="YlOrBr",
        alpha=0.85,
        edgecolors="#6d5235",
        linewidths=0.6,
    )
    for _, row in df.sort_values("combined_vaccination_opportunity_index", ascending=False).head(5).iterrows():
        label_color = "#fffaf1" if row["combined_vaccination_opportunity_index"] >= 45 else "#2b231d"
        ax.text(
            row["sanitary_pressure_score"],
            row["economic_exposure_score_combined"],
            row["uf"],
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color=label_color,
        )
    _style_axes(ax, "Drivers do índice combinado por UF", "Pressão sanitária", "Exposição econômica combinada")
    fig.colorbar(scatter, ax=ax, label="VOI combinado")
    fig.savefig(images_dir / "dashboard-drivers.png", dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

    comparison_df = (
        df.sort_values("combined_vaccination_opportunity_index", ascending=False)
        .head(10)[["uf", "beef_opportunity_score", "dairy_opportunity_score", "combined_vaccination_opportunity_index"]]
        .set_index("uf")
        .rename(
            columns={
                "beef_opportunity_score": "Corte",
                "dairy_opportunity_score": "Leite",
                "combined_vaccination_opportunity_index": "Combinado",
            }
        )
    )
    fig, ax = plt.subplots(figsize=(14, 9))
    fig.patch.set_facecolor("#f8f4ec")
    ax.set_facecolor("#f8f4ec")
    comparison_df.plot(
        kind="barh",
        ax=ax,
        color=["#b76f20", "#2f7d68", "#173d31"],
        width=0.76,
    )
    _style_axes(ax, "Comparativo unificado entre corte, leite e combinado", "Score", "UF")
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="y", visible=False)
    fig.savefig(images_dir / "dashboard-unified-modes.png", dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

    selected = df.iloc[0]["uf"]
    qf = quarterly.loc[quarterly["uf"] == selected].copy()
    qf["period"] = qf["reference_year"].astype(str) + "T" + qf["quarter"].astype(str)
    fig, ax1 = plt.subplots(figsize=(14, 9))
    fig.patch.set_facecolor("#f8f4ec")
    ax1.set_facecolor("#f8f4ec")
    ax1.plot(qf["period"], qf["bovine_slaughter"], color="#a85b17", marker="o", linewidth=2.5, label="Bovinos abatidos")
    ax1.set_ylabel("Bovinos abatidos", color="#a85b17")
    ax1.tick_params(axis="y", labelcolor="#a85b17")
    ax2 = ax1.twinx()
    ax2.plot(qf["period"], qf["milk_production_liters"], color="#5c7c58", marker="o", linewidth=2.5, label="Leite adquirido")
    ax2.set_ylabel("Leite adquirido (litros)", color="#5c7c58")
    ax2.tick_params(axis="y", labelcolor="#5c7c58")
    _style_axes(ax1, f"Evolução Trimestral em {selected}")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_color("#d6c5ad")
    ax2.tick_params(colors="#4e453b", labelsize=12)
    fig.savefig(images_dir / "dashboard-timeseries.png", dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

    _write_project_overview(images_dir / "project-overview.png")
    _write_project_business_use(images_dir / "project-business-use.png")


if __name__ == "__main__":
    main()
