"""Run the Streamlit application."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    """Launch the Streamlit dashboard."""
    root = Path(__file__).resolve().parents[1]
    pythonpath = str(root / "src")
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", "app/main.py"],
        check=True,
        cwd=root,
        env={"PYTHONPATH": pythonpath, **(__import__("os").environ)},
    )


if __name__ == "__main__":
    main()
