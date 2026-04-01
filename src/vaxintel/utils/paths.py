"""Path utilities."""

from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    """Return the project root based on the current file location."""
    return Path(__file__).resolve().parents[3]

