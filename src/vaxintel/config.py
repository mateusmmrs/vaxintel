"""Central configuration for VaxIntel Brasil."""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path

import pandas as pd

from vaxintel.scoring.weights import CombinedModeWeights, OpportunityWeights, ScoreConfig
from vaxintel.utils.metadata import SourceMetadata
from vaxintel.utils.paths import project_root


@dataclass(slots=True)
class Settings:
    """Store commonly used project paths and runtime parameters."""

    root_dir: Path = field(default_factory=project_root)
    data_dir: Path = field(init=False)
    raw_dir: Path = field(init=False)
    interim_dir: Path = field(init=False)
    processed_dir: Path = field(init=False)
    processed_dataset_path: Path = field(init=False)
    processed_geojson_path: Path = field(init=False)
    processed_quarterly_path: Path = field(init=False)
    source_manifest_path: Path = field(init=False)
    interim_input_paths: dict[str, Path] = field(init=False)
    reference_year: int = field(init=False)
    score_config: ScoreConfig = field(init=False)

    def __post_init__(self) -> None:
        self.reference_year = int(os.getenv("VAXINTEL_REFERENCE_YEAR", "2024"))
        self.score_config = ScoreConfig(
            beef_opportunity=OpportunityWeights(
                animal=float(os.getenv("VAXINTEL_BEEF_WEIGHT_ANIMAL", "0.40")),
                sanitary=float(os.getenv("VAXINTEL_BEEF_WEIGHT_SANITARY", "0.30")),
                economic=float(os.getenv("VAXINTEL_BEEF_WEIGHT_ECONOMIC", "0.30")),
            ),
            dairy_opportunity=OpportunityWeights(
                animal=float(os.getenv("VAXINTEL_DAIRY_WEIGHT_ANIMAL", "0.35")),
                sanitary=float(os.getenv("VAXINTEL_DAIRY_WEIGHT_SANITARY", "0.25")),
                economic=float(os.getenv("VAXINTEL_DAIRY_WEIGHT_ECONOMIC", "0.40")),
            ),
            combined_mode=CombinedModeWeights(
                beef=float(os.getenv("VAXINTEL_COMBINED_WEIGHT_BEEF", "0.50")),
                dairy=float(os.getenv("VAXINTEL_COMBINED_WEIGHT_DAIRY", "0.50")),
            ),
        )
        self.data_dir = self.root_dir / "data"
        self.raw_dir = self.data_dir / "raw"
        self.interim_dir = self.data_dir / "interim"
        self.processed_dir = self.data_dir / "processed"
        self.processed_dataset_path = self.processed_dir / "vaxintel_bovinos_uf.parquet"
        self.processed_geojson_path = self.processed_dir / "brazil_ufs.geojson"
        self.processed_quarterly_path = self.processed_dir / "bovines_quarterly_uf.parquet"
        self.source_manifest_path = self.processed_dir / "source_manifest.csv"
        self.interim_input_paths = {
            "bovine_herd": self.interim_dir / "bovine_herd.csv",
            "bovine_slaughter": self.interim_dir / "bovine_slaughter.csv",
            "bovine_slaughter_quarterly": self.interim_dir / "bovine_slaughter_quarterly.csv",
            "milk_production": self.interim_dir / "milk_production.csv",
            "milk_quarterly": self.interim_dir / "milk_quarterly.csv",
            "production_value": self.interim_dir / "production_value.csv",
            "uf_area": self.interim_dir / "uf_area.csv",
        }

    def ensure_directories(self) -> None:
        """Create the expected data directories if missing."""
        for path in (self.raw_dir, self.interim_dir, self.processed_dir):
            path.mkdir(parents=True, exist_ok=True)

    def write_manifest(self, entries: list[SourceMetadata]) -> None:
        """Persist source metadata to the processed folder."""
        frame = pd.DataFrame([entry.model_dump() for entry in entries])
        frame.to_csv(self.source_manifest_path, index=False)


settings = Settings()
