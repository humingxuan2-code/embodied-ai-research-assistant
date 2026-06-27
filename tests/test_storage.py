from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from research_assistant import storage
from research_assistant.models import Paper


def make_paper(paper_id: str = "2401.00001") -> Paper:
    return Paper(
        paper_id=paper_id,
        title="Embodied AI Research",
        authors=["Researcher One", "Researcher Two"],
        summary="A test paper for local storage.",
        published="2024-01-01",
        arxiv_url=f"https://arxiv.org/abs/{paper_id}",
        pdf_url=f"https://arxiv.org/pdf/{paper_id}",
        categories=["cs.RO", "cs.AI"],
        relevance_score=7.0,
    )


def test_first_add_succeeds(tmp_path: Path, monkeypatch) -> None:
    reading_list_path = tmp_path / "data" / "reading_list.json"
    monkeypatch.setattr(storage, "READING_LIST_PATH", reading_list_path)

    added = storage.add_to_reading_list(make_paper())

    assert added is True
    assert len(storage.load_reading_list()) == 1


def test_duplicate_add_does_not_save_twice(tmp_path: Path, monkeypatch) -> None:
    reading_list_path = tmp_path / "data" / "reading_list.json"
    monkeypatch.setattr(storage, "READING_LIST_PATH", reading_list_path)
    paper = make_paper()

    first_add = storage.add_to_reading_list(paper)
    second_add = storage.add_to_reading_list(paper)

    papers = storage.load_reading_list()
    assert first_add is True
    assert second_add is False
    assert len(papers) == 1
    assert papers[0].paper_id == paper.paper_id


def test_remove_existing_paper_succeeds(tmp_path: Path, monkeypatch) -> None:
    reading_list_path = tmp_path / "data" / "reading_list.json"
    monkeypatch.setattr(storage, "READING_LIST_PATH", reading_list_path)
    paper = make_paper()
    storage.add_to_reading_list(paper)

    removed = storage.remove_from_reading_list(paper.paper_id)

    assert removed is True
    assert storage.load_reading_list() == []


def test_remove_missing_paper_returns_false(tmp_path: Path, monkeypatch) -> None:
    reading_list_path = tmp_path / "data" / "reading_list.json"
    monkeypatch.setattr(storage, "READING_LIST_PATH", reading_list_path)
    storage.add_to_reading_list(make_paper())

    removed = storage.remove_from_reading_list("9999.99999")

    assert removed is False
    assert len(storage.load_reading_list()) == 1
