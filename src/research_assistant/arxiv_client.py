"""arXiv metadata retrieval helpers."""

from __future__ import annotations

from typing import Any

import arxiv

from .models import Paper


def search_papers(query: str, max_results: int) -> list[Paper]:
    """Search arXiv and return normalized paper metadata."""
    cleaned_query = query.strip()
    if not cleaned_query:
        raise ValueError("Please enter a non-empty search query.")
    if max_results <= 0:
        raise ValueError("max_results must be greater than zero.")

    client = arxiv.Client()
    search = arxiv.Search(
        query=cleaned_query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )

    try:
        return [_result_to_paper(result) for result in client.results(search)]
    except Exception as exc:
        raise RuntimeError(
            "Unable to retrieve papers from arXiv. Please check your network "
            "connection or try again later."
        ) from exc


def _result_to_paper(result: Any) -> Paper:
    """Normalize an arxiv.Result object into the app's Paper model."""
    paper_id = _extract_paper_id(result)
    published = result.published.date().isoformat() if result.published else ""
    authors = [author.name for author in result.authors]
    categories = list(getattr(result, "categories", []) or [])

    return Paper(
        paper_id=paper_id,
        title=_normalize_text(result.title),
        authors=authors,
        summary=_normalize_text(result.summary),
        published=published,
        arxiv_url=result.entry_id,
        pdf_url=result.pdf_url,
        categories=categories,
        relevance_score=0.0,
    )


def _extract_paper_id(result: Any) -> str:
    """Return a stable arXiv identifier without the URL prefix."""
    if getattr(result, "get_short_id", None):
        return str(result.get_short_id())

    entry_id = str(getattr(result, "entry_id", "")).rstrip("/")
    if not entry_id:
        raise ValueError("arXiv returned a result without an entry ID.")
    return entry_id.rsplit("/", maxsplit=1)[-1]


def _normalize_text(value: str) -> str:
    """Collapse repeated whitespace from arXiv metadata fields."""
    return " ".join(value.split())
