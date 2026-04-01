"""Tests for cleaning and validation logic."""

from __future__ import annotations

import pandas as pd
import pytest

from vaxintel.data_processing.clean import standardize_uf_frame
from vaxintel.data_processing.validate import validate_required_columns


def test_standardize_uf_frame_renames_state_column() -> None:
    frame = pd.DataFrame({"state": ["sp"], "bovine_herd": [10]})
    cleaned = standardize_uf_frame(frame)
    assert cleaned.loc[0, "uf"] == "SP"


def test_validate_required_columns_raises_on_missing_output() -> None:
    with pytest.raises(ValueError):
        validate_required_columns(pd.DataFrame({"uf": ["SP"]}))

