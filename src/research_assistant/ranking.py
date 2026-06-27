"""Transparent keyword-based ranking for retrieved papers."""

from __future__ import annotations

import re
from dataclasses import replace
from datetime import date

from .models import Paper


def rank_papers(papers: list[Paper], query: str) -> list[Paper]:
    """Return papers sorted by rule-based relevance score and recency."""
    cleaned_query = query.strip().lower()
    keywords = _extract_keywords(cleaned_query)

    scored_papers = [
        replace(paper, relevance_score=_score_paper(paper, cleaned_query, keywords))
        for paper in papers
    ]

    return sorted(
        scored_papers,
        key=lambda paper: (paper.relevance_score, _parse_date(paper.published)),
        reverse=True,
    )


def _score_paper(paper: Paper, query: str, keywords: list[str]) -> float:
    title = paper.title.lower()
    summary = paper.summary.lower()
    score = 0.0

    if query and query in title:
        score += 6
    score += sum(3 for keyword in keywords if keyword in title)

    if query and query in summary:
        score += 3
    score += sum(1 for keyword in keywords if keyword in summary)

    return score


def _extract_keywords(query: str) -> list[str]:
    """Split a query into simple alphanumeric tokens."""
    return re.findall(r"[a-z0-9]+", query.lower())


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return date.min
