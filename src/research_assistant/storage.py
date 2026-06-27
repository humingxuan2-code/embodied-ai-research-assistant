"""Local JSON storage for the reading list."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import READING_LIST_PATH
from .models import Paper


def load_reading_list() -> list[Paper]:
    """Load the local reading list, creating an empty file if needed."""
    data = _read_json_list(READING_LIST_PATH)
    try:
        return [Paper.from_dict(item) for item in data]
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Reading list at {READING_LIST_PATH} contains invalid paper data."
        ) from exc


def add_to_reading_list(paper: Paper) -> bool:
    """Add a paper to the local reading list if it is not already saved."""
    papers = load_reading_list()
    if any(saved.paper_id == paper.paper_id for saved in papers):
        return False

    papers.append(paper)
    _write_papers(READING_LIST_PATH, papers)
    return True


def remove_from_reading_list(paper_id: str) -> bool:
    """Remove a paper by ID from the local reading list."""
    papers = load_reading_list()
    remaining = [paper for paper in papers if paper.paper_id != paper_id]
    if len(remaining) == len(papers):
        return False

    _write_papers(READING_LIST_PATH, remaining)
    return True


def _read_json_list(path: Path) -> list[dict[str, Any]]:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        _write_raw_list(path, [])
        return []

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Reading list file at {path} is not valid JSON. Please fix or back it up."
        ) from exc

    if not isinstance(data, list):
        raise ValueError(f"Reading list file at {path} must contain a JSON array.")
    if not all(isinstance(item, dict) for item in data):
        raise ValueError(f"Reading list file at {path} must contain paper objects.")

    return data


def _write_papers(path: Path, papers: list[Paper]) -> None:
    _write_raw_list(path, [paper.to_dict() for paper in papers])


def _write_raw_list(path: Path, data: list[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")
