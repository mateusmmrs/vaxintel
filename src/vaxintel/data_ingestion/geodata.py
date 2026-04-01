"""IBGE geodata download and processing helpers."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from zipfile import ZipFile

import geopandas as gpd
import pandas as pd
import requests

from vaxintel.utils.metadata import SourceMetadata

GEODATA_URL = (
    "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/"
    "malhas_municipais/municipio_2024/Brasil/BR_UF_2024.zip"
)


def download_uf_geodata(raw_zip_path: Path, timeout: int = 120) -> Path:
    """Download the official IBGE 2024 UF archive."""
    response = requests.get(GEODATA_URL, timeout=timeout)
    response.raise_for_status()
    raw_zip_path.write_bytes(response.content)
    return raw_zip_path


def _find_shapefile_in_zip(zip_path: Path) -> str:
    """Return the internal shapefile path from a zip archive."""
    with ZipFile(zip_path) as archive:
        for name in archive.namelist():
            if name.lower().endswith(".shp"):
                return name
    raise FileNotFoundError(f"No shapefile found inside {zip_path}")


def read_uf_geodata(zip_path: Path) -> gpd.GeoDataFrame:
    """Read the IBGE UF shapefile from a zip archive."""
    internal_shp = _find_shapefile_in_zip(zip_path)
    return gpd.read_file(f"zip://{zip_path}!{internal_shp}")


def build_uf_area_frame(gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    """Extract UF areas in km2 from the official geometry."""
    columns = {column.upper(): column for column in gdf.columns}
    sigla_col = columns.get("SIGLA_UF")
    area_col = columns.get("AREA_KM2")
    if sigla_col is None:
        raise KeyError(f"SIGLA_UF column not found in geodata columns: {list(gdf.columns)}")
    if area_col is not None:
        area_series = pd.to_numeric(gdf[area_col], errors="coerce")
    else:
        projected = gdf.to_crs(5880)
        area_series = projected.area / 1_000_000
    return pd.DataFrame({"uf": gdf[sigla_col].astype(str), "uf_area_km2": area_series})


def export_geojson(gdf: gpd.GeoDataFrame, output_path: Path) -> Path:
    """Export a simplified UF GeoJSON for dashboard rendering."""
    gdf.to_file(output_path, driver="GeoJSON")
    return output_path


def create_placeholder_geodata_manifest() -> list[SourceMetadata]:
    """Register the official UF geography source used by the dashboard."""
    return [
        SourceMetadata(
            variable="uf_area",
            description="Area territorial por UF para derivacao de densidade bovina",
            source_name="IBGE Geociencias - Malhas 2024",
            source_url=GEODATA_URL,
            reference_year="2024",
            extraction_date=date.today().isoformat(),
            file_path="data/interim/uf_area.csv",
            notes="A area e derivada da geometria oficial BR_UF_2024.zip; prioriza AREA_KM2 quando disponivel.",
        )
    ]
