from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from research_assistant.models import Paper
from research_assistant.ranking import rank_papers


def make_paper(
    paper_id: str,
    title: str,
    summary: str,
    published: str = "2024-01-01",
) -> Paper:
    return Paper(
        paper_id=paper_id,
        title=title,
        authors=["Researcher One"],
        summary=summary,
        published=published,
        arxiv_url=f"https://arxiv.org/abs/{paper_id}",
        pdf_url=f"https://arxiv.org/pdf/{paper_id}",
        categories=["cs.RO"],
        relevance_score=0.0,
    )


def test_title_keyword_match_ranks_before_summary_match() -> None:
    title_match = make_paper(
        paper_id="2401.00001",
        title="Robot Navigation with Vision-Language Models",
        summary="A paper about embodied systems.",
    )
    summary_match = make_paper(
        paper_id="2401.00002",
        title="Planning for Mobile Robots",
        summary="This paper studies robot navigation in indoor scenes.",
    )

    ranked = rank_papers([summary_match, title_match], "robot navigation")

    assert ranked[0].paper_id == title_match.paper_id
    assert ranked[0].relevance_score > ranked[1].relevance_score


def test_newer_paper_ranks_first_when_scores_tie() -> None:
    older = make_paper(
        paper_id="2301.00001",
        title="Embodied AI Benchmark",
        summary="A benchmark for robots.",
        published="2023-01-01",
    )
    newer = make_paper(
        paper_id="2401.00001",
        title="Embodied AI Benchmark",
        summary="A benchmark for robots.",
        published="2024-01-01",
    )

    ranked = rank_papers([older, newer], "embodied ai")

    assert ranked[0].paper_id == newer.paper_id


def test_rank_papers_does_not_modify_input_list() -> None:
    first = make_paper(
        paper_id="2401.00001",
        title="World Model for Robotics",
        summary="Robotics research.",
    )
    second = make_paper(
        paper_id="2401.00002",
        title="Robot Learning",
        summary="World model methods for robots.",
    )
    papers = [second, first]
    original_ids = [paper.paper_id for paper in papers]
    original_scores = [paper.relevance_score for paper in papers]

    ranked = rank_papers(papers, "world model")

    assert [paper.paper_id for paper in papers] == original_ids
    assert [paper.relevance_score for paper in papers] == original_scores
    assert ranked is not papers
    assert all(ranked_paper is not original for ranked_paper, original in zip(ranked, papers))
