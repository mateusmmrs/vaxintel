"""Build the processed analytic dataset for the VaxIntel Brasil MVP."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vaxintel.config import settings
from vaxintel.data_processing.clean import standardize_uf_frame
from vaxintel.data_processing.validate import validate_required_columns
from vaxintel.features.economic import build_economic_features
from vaxintel.features.exposure import build_exposure_features
from vaxintel.features.opportunity import build_opportunity_dataset
from vaxintel.features.sanitary_pressure import build_sanitary_features
from vaxintel.logging_utils import configure_logging, get_logger


def _load_interim_inputs() -> dict[str, pd.DataFrame]:
    """Load expected interim tables if they exist."""
    inputs = {}
    for name, path in settings.interim_input_paths.items():
        if path.exists():
            if path.suffix == ".parquet":
                inputs[name] = pd.read_parquet(path)
            else:
                inputs[name] = pd.read_csv(path)
    return inputs


def main() -> None:
    """Build the scored UF-level dataset from available real inputs."""
    configure_logging()
    logger = get_logger(__name__)
    settings.ensure_directories()

    inputs = _load_interim_inputs()
    if not inputs:
        logger.warning(
            "Nenhum insumo interim encontrado em %s. Execute primeiro `python scripts/download_data.py`.",
            settings.interim_dir,
        )
        return

    cleaned = {name: standardize_uf_frame(frame) for name, frame in inputs.items()}
    features = {}

    if "bovine_herd" in cleaned:
        features["exposure"] = build_exposure_features(cleaned["bovine_herd"], cleaned.get("uf_area"))
    if {"bovine_slaughter", "milk_production", "bovine_herd"} <= set(cleaned):
        features["sanitary"] = build_sanitary_features(
            herd_df=cleaned["bovine_herd"],
            slaughter_df=cleaned["bovine_slaughter"],
            milk_df=cleaned["milk_production"],
            area_df=cleaned.get("uf_area"),
        )
    if {"production_value", "bovine_slaughter", "milk_production"} <= set(cleaned):
        features["economic"] = build_economic_features(
            production_value_df=cleaned["production_value"],
            slaughter_df=cleaned["bovine_slaughter"],
            milk_df=cleaned["milk_production"],
        )

    dataset = build_opportunity_dataset(
        exposure_df=features.get("exposure"),
        sanitary_df=features.get("sanitary"),
        economic_df=features.get("economic"),
    )
    validate_required_columns(dataset)
    dataset.to_parquet(settings.processed_dataset_path, index=False)
    logger.info("Processed dataset written to %s", settings.processed_dataset_path)


if __name__ == "__main__":
    main()
