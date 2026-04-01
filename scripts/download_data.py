"""Download raw source data for the VaxIntel Brasil MVP."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vaxintel.config import settings
from vaxintel.data_ingestion.geodata import (
    build_uf_area_frame,
    create_placeholder_geodata_manifest,
    download_uf_geodata,
    export_geojson,
    read_uf_geodata,
)
from vaxintel.data_ingestion.ibge import (
    aggregate_bovine_slaughter_year,
    aggregate_milk_year,
    create_ibge_source_templates,
    fetch_bovine_herd_uf,
    fetch_bovine_slaughter_quarterly,
    fetch_milk_quarterly,
)
from vaxintel.data_ingestion.mapa import create_mapa_reference
from vaxintel.logging_utils import configure_logging, get_logger
from vaxintel.utils.metadata import merge_manifests


def main() -> None:
    """Download official sources and materialize interim files for the bovine MVP."""
    configure_logging()
    logger = get_logger(__name__)
    settings.ensure_directories()

    bovine_herd = fetch_bovine_herd_uf(reference_year=2024)
    bovine_herd.to_csv(settings.interim_input_paths["bovine_herd"], index=False)
    logger.info("Saved %s", settings.interim_input_paths["bovine_herd"])

    slaughter_quarterly = fetch_bovine_slaughter_quarterly(reference_year=2024)
    slaughter_quarterly.to_csv(settings.interim_input_paths["bovine_slaughter_quarterly"], index=False)
    aggregate_bovine_slaughter_year(slaughter_quarterly).to_csv(
        settings.interim_input_paths["bovine_slaughter"],
        index=False,
    )
    logger.info("Saved slaughter quarterly and annual aggregates")

    milk_quarterly = fetch_milk_quarterly(reference_year=2024)
    milk_quarterly.to_csv(settings.interim_input_paths["milk_quarterly"], index=False)
    milk_annual = aggregate_milk_year(milk_quarterly)
    milk_annual[["uf", "reference_year", "milk_production_liters", "milk_price_brl_per_liter"]].to_csv(
        settings.interim_input_paths["milk_production"],
        index=False,
    )
    milk_annual[["uf", "reference_year", "estimated_milk_value_brl"]].to_csv(
        settings.interim_input_paths["production_value"],
        index=False,
    )
    logger.info("Saved milk quarterly and annual aggregates")

    raw_zip_path = settings.raw_dir / "BR_UF_2024.zip"
    download_uf_geodata(raw_zip_path)
    uf_gdf = read_uf_geodata(raw_zip_path)
    build_uf_area_frame(uf_gdf).to_csv(settings.interim_input_paths["uf_area"], index=False)
    export_geojson(uf_gdf.to_crs(4326), settings.processed_geojson_path)
    logger.info("Saved official UF geodata outputs")

    quarterly = pd.merge(
        slaughter_quarterly,
        milk_quarterly,
        on=["uf", "reference_year", "quarter"],
        how="outer",
    ).sort_values(["reference_year", "quarter", "uf"])
    quarterly.to_parquet(settings.processed_quarterly_path, index=False)
    logger.info("Saved quarterly analytic dataset to %s", settings.processed_quarterly_path)

    manifest_entries = merge_manifests(
        create_ibge_source_templates(),
        create_placeholder_geodata_manifest(),
        [create_mapa_reference()],
    )
    settings.write_manifest(manifest_entries)
    logger.info("Source manifest written to %s", settings.source_manifest_path)


if __name__ == "__main__":
    main()
