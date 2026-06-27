"""Application configuration defaults."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
READING_LIST_PATH = DATA_DIR / "reading_list.json"

DEFAULT_MAX_RESULTS = 10
MAX_RESULTS_OPTIONS = [10, 20, 50]
