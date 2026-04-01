"""Cleaning functions for raw source tables."""

from __future__ import annotations

import pandas as pd


def standardize_uf_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names and UF codes across tables."""
    cleaned = df.copy()
    cleaned.columns = [column.strip().lower() for column in cleaned.columns]
    if "uf" not in cleaned.columns:
        for candidate in ("sigla_uf", "state", "unidade_federacao"):
            if candidate in cleaned.columns:
                cleaned = cleaned.rename(columns={candidate: "uf"})
                break
    cleaned["uf"] = cleaned["uf"].astype(str).str.upper().str.strip()
    return cleaned

