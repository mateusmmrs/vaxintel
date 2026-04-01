"""Metadata models and helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from pydantic import BaseModel


class SourceMetadata(BaseModel):
    """Schema for source-level lineage metadata."""

    variable: str
    description: str
    source_name: str
    source_url: str
    reference_year: str
    extraction_date: str
    file_path: str
    notes: str


def merge_manifests(*manifest_lists: list[SourceMetadata]) -> list[SourceMetadata]:
    """Flatten multiple metadata lists preserving input order."""
    merged: list[SourceMetadata] = []
    for manifest in manifest_lists:
        merged.extend(manifest)
    return merged


def load_source_manifest(path: Path) -> pd.DataFrame:
    """Load the source manifest if it exists."""
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)
